# 타자 연습 관련 API 요청 및 응답 데이터를 정의하는 Pydantic 스키마 파일입니다.

from pydantic import BaseModel, Field # Pydantic BaseModel과 Field 임포트
from typing import List, Literal # 리스트와 특정 문자열 리터럴 타입 힌트를 위한 임포트
import uuid # 고유 ID 생성을 위한 uuid 모듈 임포트

# 타자 연습 문장의 난이도 정의
TypingDifficulty = Literal["easy", "medium", "hard"]

# 단일 타자 연습 문장 모델 정의
class TypingSentence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="타자 연습 문장의 고유 ID") # 고유 ID (UUID)
    content: str = Field(..., description="타자 연습에 사용될 문장 내용") # 문장 내용
    difficulty: TypingDifficulty = Field(default="medium", description="문장의 난이도 (easy, medium, hard)") # 난이도
    length: int = Field(..., ge=1, description="문장의 길이 (공백 포함)") # 문장 길이

# 타자 연습 콘텐츠 생성 요청 모델 정의 (선택적)
# 현재는 요청 시 추가 파라미터가 없으므로 간단히 정의합니다.
class TypingContentGenerationRequest(BaseModel):
    source_content: str = Field(..., description="타자 연습 콘텐츠를 생성할 원본 텍스트") # 원본 텍스트
    min_length: int = Field(default=10, ge=1, description="타자 연습 문장의 최소 길이") # 최소 길이
    max_length: int = Field(default=100, ge=1, description="타자 연습 문장의 최대 길이") # 최대 길이
