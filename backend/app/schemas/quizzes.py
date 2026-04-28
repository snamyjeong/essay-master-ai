# backend/app/schemas/quizzes.py
from pydantic import BaseModel, Field # 데이터 모델 정의를 위한 임포트
from typing import List, Optional # 타입 힌트용 임포트
from enum import Enum # Enum 클래스 사용을 위한 임포트

# 퀴즈 유형을 Enum으로 정의합니다. (Literal 대신 Enum을 써야 .속성 접근이 가능합니다)
class QuizType(str, Enum):
    SHORT_ANSWER = "short_answer" # 단답형 문제
    ESSAY = "essay"               # 논술/서술형 문제

# 단일 퀴즈 질문 모델 정의
class QuizQuestion(BaseModel):
    # [수정] 서비스의 AI 프롬프트 및 프론트엔드와 필드명을 'question'으로 통일합니다.
    question: str = Field(..., description="퀴즈 질문 내용") 
    answer: str = Field(..., description="퀴즈 정답 또는 모범 답안") 
    question_type: QuizType = Field(..., description="퀴즈 유형 (short_answer 또는 essay)") 

# 퀴즈 생성을 위한 요청 모델 정의
class QuizGenerationRequest(BaseModel):
    # 유저가 입력한 학습 내용 (에세이 본문 등)
    document_content: str = Field(..., description="퀴즈를 생성할 학습 내용 텍스트") 
    num_questions: int = Field(default=5, ge=1, le=20, description="생성할 퀴즈 질문 개수") 
    # 기본값을 Enum 멤버로 설정하여 안전성을 확보합니다.
    quiz_type: QuizType = Field(default=QuizType.SHORT_ANSWER, description="생성할 퀴즈의 유형")

    class Config:
        # JSON 요청에서 문자열로 들어와도 Enum으로 잘 변환되도록 설정
        use_enum_values = True