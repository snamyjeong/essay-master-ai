# backend/app/api/v1/endpoints/auth.py
import uuid # 고유 사용자 식별자 생성을 위한 uuid 라이브러리 임포트
from datetime import timedelta, datetime, timezone # 토큰 만료 시간 계산 및 타임존 처리를 위한 모듈 임포트
from fastapi import APIRouter, Depends, HTTPException, status # FastAPI 라우팅, 의존성 주입, 예외 처리 모듈 임포트
from fastapi.security import OAuth2PasswordRequestForm # OAuth2 표준 로그인 폼 데이터 처리를 위한 클래스 임포트

# [정석] 별도로 분리된 mock_db 모듈에서 공용 메모리 저장소와 시드 함수를 가져옵니다.
# 이를 통해 deps.py와 auth.py가 동일한 유저 명부를 공유하게 됩니다.
from backend.app.db.mock_db import mock_users_db, seed_mock_users_db

# [Mock Data] 딕셔너리 형태의 유저 데이터를 객체처럼 다루기 위한 내부 클래스 정의
class MockUser:
    def __init__(self, id: str, username: str, email: str, hashed_password: str, is_active: bool = True, refresh_token: str = None, refresh_token_expires_at: datetime = None):
        self.id = id # 유저 고유 ID (UUID)
        self.username = username # 유저 아이디
        self.email = email # 유저 이메일
        self.hashed_password = hashed_password # 암호화된 비밀번호
        self.is_active = is_active # 계정 활성 상태 여부
        self.refresh_token = refresh_token # 갱신 토큰 값
        self.refresh_token_expires_at = refresh_token_expires_at # 갱신 토큰 만료 일시

from backend.app.core import security # 해싱 및 JWT 토큰 생성 관련 보안 유틸리티 임포트
from backend.app.core.config import settings # 시스템 전역 설정 정보 임포트
from backend.app.schemas.auth import UserCreate, UserResponse, Token, RefreshTokenRequest, TokenData # 통신 규격 스키마 임포트

router = APIRouter() # 인증 관련 API 엔드포인트를 관리할 라우터 인스턴스 생성

# [실행] 모듈 로드 시 공용 저장소에 마스터 계정(snamy78)을 즉시 등록합니다.
seed_mock_users_db()


# 1. 회원가입 엔드포인트
@router.post("/signup", response_model=UserResponse)
async def register_user(
    user_in: UserCreate, # 클라이언트가 보낸 회원가입 요청 데이터
):
    """새로운 사용자를 공용 Mock DB에 등록하는 API입니다."""
    # 공용 mock_users_db에서 아이디 중복 여부를 확인합니다.
    if user_in.username in mock_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자 이름입니다."
        )
    # 공용 mock_users_db의 모든 값을 순회하며 이메일 중복 여부를 확인합니다.
    if any(u['email'] == user_in.email for u in mock_users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )

    # 보안을 위해 비밀번호를 해싱 처리합니다.
    hashed_password = security.hash_password(user_in.password)
    # 유저 식별을 위한 고유 UUID를 생성합니다.
    user_id = str(uuid.uuid4())

    # 공용 저장소 규격에 맞춰 새 유저 데이터를 구성합니다.
    new_user_data = {
        "id": user_id, # 고유 식별자
        "username": user_in.username, # 사용자 이름
        "email": user_in.email, # 사용자 이메일
        "hashed_password": hashed_password, # 해싱된 암호
        "is_active": True, # 기본 활성화 상태
        "refresh_token": None, # 초기 갱신 토큰 없음
        "refresh_token_expires_at": None # 초기 만료 시간 없음
    }

    # [핵심] 공용 mock_users_db에 데이터를 저장합니다.
    mock_users_db[user_in.username] = new_user_data

    # 응답 규격(UserResponse)에 맞춰 데이터를 반환합니다.
    return UserResponse(
        id=new_user_data["id"],
        username=new_user_data["username"],
        email=new_user_data["email"],
        is_active=new_user_data["is_active"]
    )

# 2. 로그인 엔드포인트 (액세스 및 갱신 토큰 발급)
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # OAuth2 표준 로그인 폼 수신
):
    """아이디 또는 이메일을 통해 사용자를 인증하고 JWT 토큰을 발급합니다."""
    # [보정] 공용 저장소의 모든 값을 탐색하여 username 또는 email이 일치하는 유저를 찾습니다.
    user_data = next((u for u in mock_users_db.values() 
                      if u["username"] == form_data.username or u["email"] == form_data.username), None)
    
    # 찾은 데이터가 있으면 MockUser 객체로 변환하여 내부 로직에서 사용합니다.
    user = MockUser(**user_data) if user_data else None

    # 유저가 존재하지 않거나 비밀번호 검증이 실패한 경우 401 에러를 반환합니다.
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 이름 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 액세스 토큰의 유효 기간을 설정하고 토큰을 생성합니다.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 갱신 토큰의 유효 기간을 설정하고 토큰을 생성합니다.
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    # [보안] 갱신 토큰을 해싱하여 공용 저장소에 저장하고 만료 시간을 기록합니다.
    mock_users_db[user.username]['refresh_token'] = security.hash_password(refresh_token)
    mock_users_db[user.username]['refresh_token_expires_at'] = datetime.now(timezone.utc) + refresh_token_expires

    # 생성된 토큰 정보들을 클라이언트에 반환합니다.
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# 3. 토큰 갱신 엔드포인트
@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest, # 클라이언트가 보낸 갱신 토큰 정보
):
    """만료된 액세스 토큰을 갱신 토큰을 통해 재발급합니다."""
    # 전달된 갱신 토큰을 디코딩하여 유효성을 검사합니다.
    payload = security.decode_token(refresh_request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 갱신 토큰입니다.")
    
    username: str = payload.get("sub") # 토큰에서 유저 아이디를 추출합니다.
    
    # 공용 저장소에서 유저 데이터를 다시 조회합니다.
    user_data = mock_users_db.get(username)
    user = MockUser(**user_data) if user_data else None

    # 유저가 없거나 저장된 갱신 토큰과 일치하지 않으면 에러를 처리합니다.
    if not user or not user.refresh_token or not security.verify_password(refresh_request.refresh_token, user.refresh_token):
        raise HTTPException(status_code=401, detail="인증에 실패했습니다.")

    # 갱신 토큰이 만료되었는지 확인합니다.
    if user.refresh_token_expires_at and user.refresh_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="갱신 토큰이 만료되었습니다.")

    # 새로운 액세스 및 갱신 토큰을 생성하여 반환합니다.
    new_access_token = security.create_access_token(data={"sub": user.username})
    new_refresh_token = security.create_refresh_token(data={"sub": user.username})

    # 공용 저장소의 갱신 토큰 정보를 업데이트합니다.
    mock_users_db[user.username]['refresh_token'] = security.hash_password(new_refresh_token)
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}