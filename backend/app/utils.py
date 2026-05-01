from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.app.models import User, TokenData # 모델 임포트

# JWT 관련 설정
SECRET_KEY = "your-secret-key"  # 실제 운영 환경에서는 환경 변수 등으로 관리해야 합니다.
ALGORITHM = "HS256"              # JWT 서명 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Access Token 만료 시간 (분)
REFRESH_TOKEN_EXPIRE_DAYS = 7    # Refresh Token 만료 시간 (일)

# 비밀번호 해싱을 위한 컨텍스트 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer: 토큰을 추출하는 데 사용됩니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- 가상 사용자 데이터베이스 (데이터베이스 연동 전 임시 사용) ---
FAKE_USERS_DB = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("testpassword"), # 비밀번호는 해싱하여 저장
        "disabled": False,
    },
    "jarvis": {
        "username": "jarvis",
        "full_name": "Jarvis AI",
        "email": "jarvis@example.com",
        "hashed_password": pwd_context.hash("jarvispassword"),
        "disabled": False,
    }
}

# --- 비밀번호 검증 함수 ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해싱된 비밀번호를 비교하여 일치 여부를 반환합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)

# --- 사용자 조회 함수 (가상 DB에서) ---
def get_user(username: str) -> Optional[User]:
    """
    주어진 사용자 이름으로 가상 데이터베이스에서 사용자를 조회합니다.
    """
    if username in FAKE_USERS_DB:
        user_dict = FAKE_USERS_DB[username]
        return User(**user_dict)
    return None

# --- JWT 토큰 생성 함수 ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token을 생성합니다.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # 만료 시간 추가
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Refresh Token을 생성합니다.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"}) # 만료 시간 및 토큰 타입 추가
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 현재 활성 사용자 가져오기 함수 (인증 의존성) ---
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    현재 요청의 JWT 토큰을 검증하고, 유효한 경우 해당 사용자를 반환합니다.
    토큰이 유효하지 않으면 HTTPException을 발생시킵니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰 디코딩 시도
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # 'sub' 클레임에서 사용자 이름 추출
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username) # TokenData 모델로 변환
    except JWTError:
        raise credentials_exception
    
    # 사용자 조회
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    현재 활성 상태인 사용자를 반환합니다. 비활성 사용자라면 HTTPException을 발생시킵니다.
    """
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
