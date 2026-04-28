# backend/app/schemas/history.py
# 학습 이력 관련 Pydantic 스키마 정의 파일입니다.
# '정확한 기록만이 정확한 분석을 낳는다'는 일타 강사의 철학에 따라, 데이터의 무결성을 보장합니다.

from pydantic import BaseModel, Field # Pydantic의 기본 모델과 필드 유효성 검사를 위한 Field를 임포트합니다.
from datetime import datetime # 날짜/시간 타입 임포트
from typing import Optional # 선택적 필드를 위한 Optional 임포트

# 1. 퀴즈 결과(QuizResult) 스키마: 퀴즈 결과 저장 요청 및 응답 데이터 구조 정의
class QuizResultBase(BaseModel):
    """퀴즈 결과의 기본 속성을 정의하는 Pydantic 모델입니다."""
    user_id: int = Field(..., description="퀴즈를 푼 사용자 ID") # 퀴즈를 푼 사용자 ID
    document_id: int = Field(..., description="관련 문서의 ID") # 관련 문서의 ID
    quiz_type: str = Field(..., description="퀴즈 유형 (예: short_answer, essay)") # 퀴즈 유형
    question_text: str = Field(..., description="제시된 퀴즈 질문 내용") # 제시된 퀴즈 질문 내용
    user_answer: Optional[str] = Field(None, description="사용자가 제출한 답변 (선택 사항)") # 사용자가 제출한 답변 (선택 사항)
    correct_answer: str = Field(..., description="퀴즈의 정답 또는 모범 답안") # 퀴즈의 정답 또는 모범 답안
    score: Optional[int] = Field(None, ge=0, le=100, description="해당 퀴즈 질문에 대한 점수 (0~100, 선택 사항)") # 해당 퀴즈 질문에 대한 점수 (선택 사항)

class QuizResultCreate(QuizResultBase):
    """새 퀴즈 결과를 생성할 때 사용되는 모델입니다."""
    pass # QuizResultBase의 필드를 그대로 사용하며 추가적인 필드는 없습니다.

class QuizResultResponse(QuizResultBase):
    """
    퀴즈 결과 정보를 클라이언트에 응답할 때 사용되는 모델입니다.
    """
    id: int = Field(..., description="퀴즈 결과 고유 ID") # 퀴즈 결과 고유 ID
    attempted_at: datetime = Field(..., description="퀴즈 시도 시각") # 퀴즈 시도 시각

    class Config:
        from_attributes = True # SQLAlchemy ORM 모델과의 호환성을 위한 설정

# 2. 타자 기록(TypingRecord) 스키마: 타자 기록 저장 요청 및 응답 데이터 구조 정의
class TypingRecordBase(BaseModel):
    """타자 기록의 기본 속성을 정의하는 Pydantic 모델입니다."""
    user_id: int = Field(..., description="타자 연습을 한 사용자 ID") # 타자 연습을 한 사용자 ID
    document_id: int = Field(..., description="관련 문서의 ID") # 관련 문서의 ID
    sentence_content: str = Field(..., description="타자 연습에 사용된 문장 내용") # 타자 연습에 사용된 문장 내용
    user_input: str = Field(..., description="사용자가 실제로 입력한 내용") # 사용자가 실제로 입력한 내용
    wpm: float = Field(..., gt=0, description="분당 단어 수 (Words Per Minute)") # 분당 단어 수
    accuracy: float = Field(..., gt=0, le=1, description="타자 정확도 (0.0~1.0)") # 타자 정확도 (예: 0.95 = 95%)
    difficulty: Optional[str] = Field(None, description="문장 난이도 (예: easy, medium, hard, 선택 사항)") # 문장 난이도 (선택 사항)

class TypingRecordCreate(TypingRecordBase):
    """새 타자 기록을 생성할 때 사용되는 모델입니다."""
    pass # TypingRecordBase의 필드를 그대로 사용하며 추가적인 필드는 없습니다.

class TypingRecordResponse(TypingRecordBase):
    """
    타자 기록 정보를 클라이언트에 응답할 때 사용되는 모델입니다.
    """
    id: int = Field(..., description="타자 기록 고유 ID") # 타자 기록 고유 ID
    attempted_at: datetime = Field(..., description="타자 연습 시도 시각") # 타자 연습 시도 시각

    class Config:
        from_attributes = True # SQLAlchemy ORM 모델과의 호환성을 위한 설정
