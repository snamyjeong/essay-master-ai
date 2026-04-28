import os # 운영체제 리소스 및 경로 접근을 위한 모듈 임포트
import json # AI 응답 문자열을 파이썬 객체로 변환하기 위한 JSON 처리 모듈 임포트
from typing import List, Optional # 정적 타입 검사 및 가독성을 위한 타입 힌트 임포트
from langchain_google_genai import ChatGoogleGenerativeAI # [교정] 구형 SDK 대신 랭체인 기반 제미나이 엔진 임포트
from app.core.config import settings # 시스템 전역 설정(API 키 등)을 참조하기 위한 임포트
from app.schemas.quizzes import QuizQuestion, QuizType # 퀴즈 데이터 구조 및 타입을 정의한 스키마 임포트

class QuizGenerator:
    """
    30년 경력의 노련한 일타 강사 페르소나를 장착한 퀴즈 생성 엔진입니다.
    기존의 구형 호출 방식을 제거하고 최신 랭체인 인터페이스로 업그레이드되었습니다.
    """
    def __init__(self):
        """
        서비스 초기화 시점에 최신형 Gemini 엔진을 세팅합니다.
        '수업 준비가 완벽해야 일타 강사'라는 정성남 수석님의 철학을 반영합니다.
        """
        # [교정] FutureWarning을 유발하는 genai.configure 대신 랭체인 객체를 사용하여 2.5-flash 모델을 할당합니다.
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # 수석님 환경에서 확인된 최신 정규 모델명입니다.
            api_key=settings.GEMINI_API_KEY, # .env에서 로드된 안전한 API 키를 사용합니다.
            temperature=0.7 # 문제 출제의 창의성과 정답의 일관성을 맞춘 최적의 온도값입니다.
        )

    async def generate_quiz(self, document_content: str, quiz_type: QuizType = QuizType.SHORT_ANSWER, num_questions: int = 5) -> List[QuizQuestion]:
        """
        제공된 텍스트를 분석하여 지정된 유형의 퀴즈 세트를 비동기로 생성합니다.
        """
        # 일타 강사의 카리스마를 담은 정밀 출제 지시서(프롬프트)를 작성합니다.
        prompt = self._build_prompt(document_content, quiz_type, num_questions)
        
        try:
            # [교정] ainvoke를 사용하여 비동기 방식으로 AI 모델을 호출합니다. (서버 블로킹 방지)
            response = await self.llm.ainvoke(prompt)
            
            # AI의 답변 텍스트(response.content)에서 순수 JSON 배열만 추출합니다.
            quiz_json = self._extract_json_from_response(response.content)
            
            # 추출된 JSON 리스트를 돌며 Pydantic 스키마인 QuizQuestion 객체로 조립합니다.
            quizzes = []
            for item in quiz_json:
                # 필드명 불일치를 대비하여 'question'과 'question_text'를 모두 체크합니다.
                quizzes.append(QuizQuestion(
                    question_text=item.get("question", item.get("question_text", "질문을 생성하지 못했습니다.")),
                    answer=item.get("answer", "정답을 확인 중입니다."),
                    question_type=quiz_type # 요청한 퀴즈 타입을 주입합니다.
                ))
            return quizzes # 조립 완료된 퀴즈 리스트를 반환합니다.

        except Exception as e:
            # 20년 차 엔지니어의 로깅: 에러 발생 시 명확한 원인을 로그로 남기고 예외를 던집니다.
            print(f"Quiz Generation Modern Engine Error: {e}")
            raise ValueError(f"최신 엔진 가동 중 퀴즈 생성에 실패했습니다: {str(e)}")

    def _build_prompt(self, document_content: str, quiz_type: QuizType, num_questions: int) -> str:
        """ 
        AI가 완벽한 문제를 출제할 수 있도록 가이드라인을 제시하는 프롬프트 빌더 메서드입니다. 
        """
        # 퀴즈 타입에 따른 수석님 맞춤 지시사항을 설정합니다.
        if quiz_type == QuizType.ESSAY:
            type_desc = "심도 있는 사고와 논리적 기술을 요구하는 논술형(essay)"
        else:
            type_desc = "핵심 키워드를 정확히 파악해야 하는 단답형(short_answer)"

        # 30년 경력 강사 '정성남' 페르소나를 주입하여 문제의 퀄리티를 높입니다.
        return f"""
        당신은 30년 경력의 노련한 일타 강사 정성남입니다. 
        다음 학습 내용을 분석하여 학생의 암기를 돕는 {num_questions}개의 {type_desc} 문제를 출제하세요.
        
        [학습 내용]
        {document_content}
        
        [출력 규격 - 엄격 준수]
        반드시 JSON 리스트 형식으로만 응답하며, 각 객체는 다음 필드를 포함해야 합니다:
        - question: 문제 내용
        - answer: 정답(단답형) 또는 모범 답안(논술형)
        
        불필요한 설명 없이 오직 JSON 데이터만 출력하세요.
        """

    def _extract_json_from_response(self, text: str) -> List[dict]:
        """ AI의 답변 텍스트 중 백틱(```) 사이에 낀 JSON 데이터만 깨끗하게 발라내는 방어적 로직입니다. """
        try:
            # 문자열에서 JSON 배열의 시작([)과 끝(]) 위치를 찾습니다.
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end > 0:
                # 잘라낸 문자열을 파이썬 리스트/딕셔너리로 변환합니다.
                return json.loads(text[start:end])
            return json.loads(text) # 구조가 단순할 경우 전체를 파싱 시도합니다.
        except Exception:
            return [] # 파싱 실패 시 빈 리스트를 반환하여 시스템 중단을 방지합니다.