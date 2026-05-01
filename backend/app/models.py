from pydantic import BaseModel
from typing import Optional

# 사용자 인증 요청 모델: 로그인 시 사용자 이름과 비밀번호를 받습니다.
class UserLogin(BaseModel):
    username: str  # 사용자 아이디
    password: str  # 비밀번호

# JWT 토큰 응답 모델: Access Token과 Refresh Token을 반환합니다.
class Token(BaseModel):
    access_token: str   # 접근 토큰
    token_type: str     # 토큰 타입 (예: Bearer)
    refresh_token: str  # 갱신 토큰

# 토큰 데이터 모델: JWT 내부에 저장될 데이터를 정의합니다.
class TokenData(BaseModel):
    username: Optional[str] = None # 토큰에 포함된 사용자 이름

# 사용자 모델 (현재는 가상): 실제 DB 모델 대신 사용될 가상 사용자 정보입니다.
class User(BaseModel):
    username: str   # 사용자 아이디
    email: Optional[str] = None # 이메일 (선택 사항)
    full_name: Optional[str] = None # 전체 이름 (선택 사항)
    disabled: Optional[bool] = None # 계정 비활성화 여부 (선택 사항)

# 분석 요청 모델: InputScreen에서 텍스트와 파일 데이터를 받습니다.
class AnalyzeRequest(BaseModel):
    text_content: Optional[str] = None # 분석할 텍스트 내용
    file_content: Optional[str] = None # 파일 내용 (Base64 인코딩 등)
    file_name: Optional[str] = None    # 파일 이름

# 분석 응답 모델: 분석 결과를 반환합니다.
class AnalyzeResponse(BaseModel):
    analysis_result: str # 분석 결과 텍스트