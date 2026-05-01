import os # 운영체제 환경 변수 접근을 위한 os 모듈 임포트
from typing import List, Dict, Any # 타입 힌트를 위한 리스트, 딕셔너리, Any 임포트
import json # JSON 파싱을 위한 임포트

# Google Gemini(LangChain)를 사용하기 위한 핵심 라이브러리 임포트
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate # 채팅 프롬프트 템플릿 임포트
from langchain_core.output_parsers import StrOutputParser # 문자열 출력 파서 임포트
from langchain_core.runnables import RunnableParallel # 병렬 실행을 위한 런어블 임포트
from langchain_core.exceptions import OutputParserException # 출력 파서 예외 처리를 위한 임포트

from backend.app.core.config import settings # 설정값(API 키 등)을 가져오기 위한 임포트
from backend.app.services.rag_learning_service import rag_learning_service # RAG 서비스 임포트
from fastapi import HTTPException # FastAPI HTTP 예외 처리를 위한 임포트 (evaluate_essay_answer_with_rag에서 사용)

class QuizGenerationService: # [교정] 라우터(learning.py)의 호출 규격에 맞춰 클래스명을 정의합니다.
    """
    학습 콘텐츠를 기반으로 퀴즈 문제(단답형, 논술형), 타자 연습 텍스트, 
    그리고 일타 강사의 멘토링 메시지를 생성하는 서비스입니다.
    """
    def __init__(self, db=None):
        """
        서비스 초기화 시 Gemini 모델을 로드합니다.
        """
        self.db = db

        # [디버깅] 값이 비어있는지 서버 로그에 명확히 찍어봅니다.
        print(f"🔥 [DEBUG] 현재 settings에서 읽은 키: '{settings.GEMINI_API_KEY[:5]}...' (길이: {len(settings.GEMINI_API_KEY)})")     

        # [중요] 최신 라이브러리 규격에 맞춰 'api_key' 매개변수를 사용합니다.
        # settings.GEMINI_API_KEY가 .env에서 로드된 GOOGLE_API_KEY를 정상적으로 물고 있어야 합니다.
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key="AIzaSyCkYlONj3jarZk_RmKptZ8grYX_hy41A5g",
            temperature=0.7
        )

        # 1. 단답형 키워드 퀴즈 생성 프롬프트 템플릿
        # 30년 경력 강사의 페르소나를 시스템 프롬프트에 주입합니다.
        self.keyword_quiz_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 30년 경력의 메타인지 학습 전문가입니다. 
            학습 내용에서 핵심 키워드를 추출하여 학생들이 암기하기 좋은 **단답형 문제** 3개를 생성하세요.
            형식: - 문제: [내용] / 정답: [키워드]"""),
            ("user", "학습 내용:\n{content}")
        ])

        # 2. 서술형 퀴즈 생성 프롬프트 템플릿
        self.essay_quiz_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 30년 경력의 메타인지 학습 전문가입니다. 
            심층적인 사고력을 요구하는 **서술형 심화학습 문제** 1개를 생성하고, 
            학생이 반드시 포함해야 할 '핵심 포인트'를 채점 가이드로 제시하세요."""),
            ("user", "학습 내용:\n{content}")
        ])

        # 3. 타자 연습 텍스트 생성 프롬프트 템플릿
        self.typing_text_prompt = ChatPromptTemplate.from_messages([
            ("system", "학습 내용을 자연스럽게 암기할 수 있도록 문맥이 매끄러운 **타자 연습용 요약문**을 300자 내외로 작성하세요."),
            ("user", "학습 내용:\n{content}")
        ])

        # 4. 멘토링 메시지 생성 프롬프트 템플릿
        self.mentoring_prompt = ChatPromptTemplate.from_messages([
            ("system", "학생의 학습 의욕을 고취시키는 30년 경력 메타인지 학습 전문가의 **따뜻하고 날카로운 한마디**를 작성하세요."),
            ("user", "학습 내용 요약:\n{content}")
        ])
        
        # 5. 서술형 심화 학습 평가 프롬프트 템플릿
        # RAG로 가져온 맥락(context)을 바탕으로 사용자 답변을 심층 평가합니다.
        self.essay_evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 30년 경력의 메타인지 학습 전문가이자, 채점관입니다.
            제공된 '참고 자료'와 '질문'을 바탕으로 학생의 '답변'을 평가해주세요.
            평가는 다음 세 가지 기준에 따라 상세하게 이루어져야 합니다:
            1. 사실 관계 정확성 (factual_accuracy): 답변이 참고 자료의 핵심 내용을 얼마나 정확하게 반영하고 있는가? (0-100점)
            2. 논리적 일관성 (logical_coherence): 답변의 논리 전개가 타당하고 일관성이 있는가? (0-100점)
            3. 표현력 및 가독성 (expression_readability): 문장 구성이 적절하고 가독성이 좋은가? (0-100점)
            
            각 항목별 점수와 함께, 구체적인 피드백 및 개선 가이드를 제공해주세요.
            출력은 반드시 다음 JSON 형식으로 제공해야 합니다:
            {{
                "overall_feedback": "전반적인 평가에 대한 요약",
                "factual_accuracy": {{
                    "score": [0-100],
                    "feedback": "사실 관계 정확성에 대한 구체적인 피드백 및 개선 가이드"
                }},
                "logical_coherence": {{
                    "score": [0-100],
                    "feedback": "논리적 일관성에 대한 구체적인 피드백 및 개선 가이드"
                }},
                "expression_readability": {{
                    "score": [0-100],
                    "feedback": "표현력 및 가독성에 대한 구체적인 피드백 및 개선 가이드"
                }},
                "overall_score": [0-100]
            }}"""),
            ("user", "참고 자료:\n{context}\n\n질문:\n{question}\n\n학생 답변:\n{answer}")
        ])


        # 출력 파서: LLM의 응답 텍스트를 그대로 문자열로 받아옵니다.
        self.output_parser = StrOutputParser()

        # [런어블 체인 구성] LangChain의 RunnableParallel을 사용하여 4가지 작업을 동시에 병렬 처리합니다.
        self.full_generation_chain = RunnableParallel(
            keyword_quizzes=self.keyword_quiz_prompt | self.llm | self.output_parser,
            essay_quizzes=self.essay_quiz_prompt | self.llm | self.output_parser,
            typing_text=self.typing_text_prompt | self.llm | self.output_parser,
            mentoring=self.mentoring_prompt | self.llm | self.output_parser
        )
        
        # 논술 평가를 위한 체인 (단일 LLM 호출)
        self.essay_evaluation_chain = self.essay_evaluation_prompt | self.llm | self.output_parser


    async def generate_learning_content(self, content: str) -> Dict[str, str]:
        """
        주어진 학습 내용을 분석하여 퀴즈 세트와 멘토링 메시지를 비동기로 생성합니다.
        """
        # 디버그용 출력: 분석 시작을 알립니다.
        print(f"Jarvis Neo-Genesis V3 분석 가동: {len(content)}자 분석 중...")
        
        # 병렬 체인 실행 (모든 결과가 나올 때까지 대기 후 딕셔너리로 반환)
        results = await self.full_generation_chain.ainvoke({"content": content})

        # 최종 생성된 콘텐츠를 딕셔너리 구조로 반환합니다. (수석님, 여기가 잘렸던 부분입니다)
        return {
            "keyword_quizzes": results["keyword_quizzes"],
            "essay_quizzes": results["essay_quizzes"],
            "typing_text": results["typing_text"],
            "mentoring": results["mentoring"]
        }

    async def evaluate_essay_answer_with_rag(self, user_id: str, question: str, user_answer: str) -> Dict[str, Any]:
        """
        RAG 시스템을 통해 관련 문서를 가져오고, Gemini 2.5 Flash를 사용하여 
        사용자의 논술 답안을 심층 평가합니다.
        """
        # 1. RAG 시스템을 통해 질문과 관련된 문서를 검색합니다.
        # 이전에 save_content를 통해 저장된 사용자 지식 문서를 활용합니다.
        retrieved_docs = await rag_learning_service.retrieve_related_documents(user_id, question)
        
        # 검색된 문서들의 내용을 하나의 문자열로 결합합니다. (RAG 컨텍스트)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else "제공된 참고 자료 없음."
        
        # 2. Gemini 2.5 Flash를 사용하여 논술 답안을 평가합니다.
        try:
            # 평가 체인을 비동기로 호출하고, 컨텍스트, 질문, 답변을 전달합니다.
            raw_evaluation_result = await self.essay_evaluation_chain.ainvoke({
                "context": context,
                "question": question,
                "answer": user_answer
            })
            
            # LLM의 응답이 JSON 형식이므로 파싱합니다.
            evaluation_data = json.loads(raw_evaluation_result)
            return evaluation_data
            
        except json.JSONDecodeError as e:
            print(f"논술 평가 결과 JSON 파싱 실패: {e}")
            print(f"LLM 원본 응답: {raw_evaluation_result}")
            raise HTTPException(status_code=500, detail="AI 평가 결과 파싱 오류가 발생했습니다.")
        except OutputParserException as e:
            print(f"LangChain 출력 파서 예외 발생: {e}")
            raise HTTPException(status_code=500, detail="AI 응답 처리 중 오류가 발생했습니다.")
        except Exception as e:
            print(f"논술 평가 중 예상치 못한 오류 발생: {e}")
            raise HTTPException(status_code=500, detail="논술 평가 서비스에서 오류가 발생했습니다.")


# 라우터에서 호출할 수 있도록 인스턴스를 생성해 둡니다.
# FastAPI의 Depends를 통해 주입되므로, 여기서는 전역 인스턴스를 직접 사용하지 않습니다.
# quiz_service = QuizGenerationService()
