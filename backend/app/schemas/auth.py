# backend/app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field # 데이터 모델 및 이메일 유효성 검사 도구, Field 임포트
from typing import Optional, Literal # 선택적 필드 처리를 위한 Optional 임포트, Literal 타입 임포트
from datetime import datetime # 날짜/시간 타입 임포트

# 모든 사용자 데이터 모델의 기반이 되는 클래스
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="이메일 주소") # 이메일 주소 (email-validator를 통해 형식을 검증합니다)

# 회원가입 시 요청 데이터 규격
class UserCreate(UserBase):
    username: str = Field(..., description="사용자 이름") # 사용자 이름 필드 추가
    password: str = Field(..., description="사용자가 입력한 평문 비밀번호") # 사용자가 입력한 평문 비밀번호

# [추가] 멤버십 유형을 위한 Literal 타입 정의
MembershipType = Literal["FREE", "PREMIUM", "VIP"]

# API 응답 시 사용자 정보 데이터 규격
class UserResponse(UserBase):
    id: int = Field(..., description="시스템이 부여한 사용자 고유 ID") # 시스템이 부여한 사용자 고유 ID
    username: str = Field(..., description="사용자 이름") # 사용자 이름
    is_active: bool = Field(..., description="계정 활성화 상태") # 계정 활성화 상태
    is_superuser: bool = Field(False, description="관리자 여부") # 관리자 여부 (기본값 False)
    membership_type: MembershipType = Field("FREE", description="멤버십 유형 (FREE, PREMIUM 등)") # 멤버십 유형 (기본값 FREE)
    membership_start_date: datetime = Field(..., description="멤버십 시작일") # 멤버십 시작일
    membership_end_date: Optional[datetime] = Field(None, description="멤버십 종료일") # 멤버십 종료일
    point_balance: int = Field(0, description="사용자 포인트 잔액") # 사용자 포인트 잔액 (기본값 0)

    class Config:
        # SQLAlchemy 모델(객체)을 Pydantic 모델로 자동 변환할 수 있도록 설정합니다.
        from_attributes = True 

# 로그인 성공 시 발급되는 토큰 정보 규격 (액세스 토큰 및 갱신 토큰 포함)
class Token(BaseModel):
    access_token: str = Field(..., description="실제 JWT 액세스 토큰 문자열") # 실제 JWT 액세스 토큰 문자열
    refresh_token: str = Field(..., description="갱신 토큰 문자열") # 갱신 토큰 문자열
    token_type: str = Field("bearer", description="토큰의 인증 타입") # 토큰의 인증 타입 (기본값 bearer)

# 갱신 토큰 요청을 위한 데이터 규격
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="클라이언트가 제출하는 갱신 토큰") # 클라이언트가 제출하는 갱신 토큰

# 토큰 내부에 저장될 데이터 규격
class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="토큰 데이터에 포함된 사용자 이름") # email 대신 username을 토큰 데이터로 사용
