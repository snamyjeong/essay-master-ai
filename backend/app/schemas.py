# Pydantic 스키마를 정의하여 데이터 유효성 검사 및 직렬화를 수행합니다.
from typing import Optional

from pydantic import BaseModel, EmailStr

# 모든 스키마의 기본이 되는 Base 클래스입니다.
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # Pydantic V2에서 `orm_mode` 대신 사용

# UserBase: 사용자 생성 및 업데이트 시 공통 필드 정의
class UserBase(BaseSchema):
    full_name: Optional[str] = None  # 사용자 전체 이름 (선택 사항)
    email: Optional[EmailStr] = None # 사용자 이메일 (선택 사항, 이메일 형식 검증)

# UserCreate: 사용자 생성 시 필요한 필드 (비밀번호 포함)
class UserCreate(UserBase):
    email: EmailStr              # 이메일 (필수)
    password: str                # 비밀번호 (필수)
    is_superuser: bool = False   # 최고 관리자 여부 (기본값: False)

# UserUpdate: 사용자 정보 업데이트 시 필요한 필드
class UserUpdate(UserBase):
    password: Optional[str] = None # 비밀번호 (선택 사항)

# UserInDBBase: 데이터베이스에서 읽어올 사용자 정보의 기본 필드 (ID 포함)
class UserInDBBase(UserBase):
    id: Optional[int] = None     # 사용자 ID (선택 사항)

    class Config:
        from_attributes = True   # Pydantic V2에서 `orm_mode` 대신 사용

# User: 클라이언트에 반환될 사용자 정보 (보안상 비밀번호 제외)
class User(UserInDBBase):
    pass

# UserInDB: 데이터베이스에 저장된 사용자 정보 (해시된 비밀번호 포함)
class UserInDB(UserInDBBase):
    hashed_password: str         # 해시된 비밀번호

# Token: OAuth2 토큰 응답 스키마
class Token(BaseSchema):
    access_token: str            # 액세스 토큰
    token_type: str = "bearer"   # 토큰 타입 (기본값: "bearer")

# TokenPayload: JWT 토큰 페이로드 스키마
class TokenPayload(BaseSchema):
    sub: Optional[int] = None    # 토큰 주체 (사용자 ID)

# UserLogin: 사용자 로그인 요청 스키마
class UserLogin(BaseSchema):
    email: EmailStr              # 로그인 이메일
    password: str                # 로그인 비밀번호