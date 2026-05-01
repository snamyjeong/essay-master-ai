from fastapi import APIRouter, HTTPException, Depends # FastAPI의 핵심 통제 모듈 임포트
from typing import List # 리스트 타입 힌트를 위한 모듈
from backend.app.schemas.quizzes import QuizGenerationRequest, QuizQuestion # 퀴즈 데이터 규격 임포트

router = APIRouter() # '/api/v1/content' 하위 경로를 관리할 라우터 객체 생성

@router.post("/generate-quiz", response_model=List[QuizQuestion])
async def generate_quiz_content(request: QuizGenerationRequest):
    """
    유저가 제공한 문서를 분석하여 일타 강사 모드로 퀴즈를 생성하는 엔드포인트입니다.
    """
    try:
        # [Mock Data] 실제 퀴즈 생성 로직 대신 Mock 데이터를 반환합니다.
        # QuizQuestion 스키마에 맞춰 Mock 데이터를 생성합니다.
        mock_quiz_questions = [
            QuizQuestion(
                id="q1",
                question_text="GPT 모델은 어떤 종류의 인공지능 모델인가요?",
                question_type="multiple_choice",
                options=["생성형 AI", "판별형 AI", "강화 학습 AI", "지도 학습 AI"],
                correct_answer="생성형 AI",
                explanation="GPT는 Generative Pre-trained Transformer의 약자로, 텍스트를 생성하는 데 특화된 생성형 AI 모델입니다."
            ),
            QuizQuestion(
                id="q2",
                question_text="인공지능 학습에서 '과적합(Overfitting)'이란 무엇이며, 이를 방지하는 방법 한 가지를 설명하세요.",
                question_type="short_answer",
                options=[],
                correct_answer="과적합은 모델이 훈련 데이터에 너무 맞춰져 새로운 데이터에 대한 예측 성능이 떨어지는 현상입니다. 드롭아웃(Dropout)이나 데이터 증강(Data Augmentation) 등의 방법으로 방지할 수 있습니다.",
                explanation="과적합은 모델이 훈련 데이터를 너무 '외워서' 일반화 능력이 떨어지는 현상을 의미합니다. 드롭아웃은 학습 시 일부 뉴런을 무작위로 비활성화하여 모델이 특정 특징에 과도하게 의존하는 것을 방지합니다."
            ),
            QuizQuestion(
                id="q3",
                question_text="머신러닝에서 지도 학습(Supervised Learning)과 비지도 학습(Unsupervised Learning)의 주요 차이점은 무엇인가요?",
                question_type="multiple_choice",
                options=["정답 라벨의 유무", "학습 속도", "알고리즘 복잡성", "데이터 크기"],
                correct_answer="정답 라벨의 유무",
                explanation="지도 학습은 정답 라벨(레이블)이 있는 데이터를 사용하여 학습하는 반면, 비지도 학습은 정답 라벨 없이 데이터의 패턴이나 구조를 학습합니다."
            ),
            QuizQuestion(
                id="q4",
                question_text="딥러닝에서 컨볼루션 신경망(CNN)이 주로 사용되는 분야는 무엇인가요?",
                question_type="short_answer",
                options=[],
                correct_answer="이미지 인식 및 처리, 컴퓨터 비전 분야",
                explanation="CNN은 특히 이미지 데이터에서 특징을 효과적으로 추출하는 데 탁월하여, 이미지 분류, 객체 탐지 등 컴퓨터 비전 분야에서 널리 활용됩니다."
            ),
            QuizQuestion(
                id="q5",
                question_text="인공지능의 윤리적 문제 중 '편향(Bias)'이 발생하는 주된 원인은 무엇인가요?",
                question_type="multiple_choice",
                options=["모델의 복잡성", "데이터의 편향", "알고리즘의 오류", "컴퓨터 성능 부족"],
                correct_answer="데이터의 편향",
                explanation="AI 모델의 편향은 주로 훈련 데이터 자체가 특정 그룹에 편향되어 있거나 특정 정보를 과도하게 반영할 때 발생합니다. 모델은 데이터의 패턴을 학습하므로, 편향된 데이터는 편향된 결과로 이어집니다."
            ),
        ]

        # 요청받은 num_questions 수에 맞춰 Mock 퀴즈를 반환합니다.
        # 실제 구현에서는 quiz_type 등을 고려하여 필터링할 수 있습니다.
        num_to_return = min(request.num_questions, len(mock_quiz_questions))
        return mock_quiz_questions[:num_to_return] # 생성된 퀴즈 리스트를 클라이언트에 반환합니다.

    except ValueError as e:
        # 비즈니스 로직 상의 에러는 400(Bad Request)으로 처리합니다.
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 시스템 레벨의 예기치 못한 에러는 500(Server Error)으로 처리하여 안전성을 확보합니다.
        print(f"API Endpoint Error: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 문제로 퀴즈를 생성할 수 없습니다.")