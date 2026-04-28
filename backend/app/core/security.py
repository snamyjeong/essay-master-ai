# -*- coding: utf-8 -*-
# 보안 관련 유틸리티 함수들을 정의하는 파일입니다.
# 비밀번호 해싱, JWT 토큰 생성 및 검증 등의 기능을 포함합니다.

from datetime import datetime, timedelta, timezone # 날짜 및 시간 계산을 위한 모듈 임포트
from typing import Optional, Any # 타입 힌팅을 위한 도구 임포트
import bcrypt # 비밀번호 해싱 라이브러리 직접 임포트

from jose import jwt # JWT 생성 및 디코딩을 위한 라이브러리
from passlib.context import CryptContext

# [주의] 임포트 경로는 수석님의 프로젝트 루트 설정에 따라 'backend.app...'으로 통일하는 것이 안전합니다.
from backend.app.core.config import settings 

# [몽키 패치] passlib와 최신 bcrypt(4.0.0+) 간의 버전 참조 오류 해결 로직
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (object,), {"__version__": bcrypt.__version__})

# 비밀번호 해싱을 위한 컨텍스트 생성
# [정도(正道) 3] bcrypt와 pbkdf2_sha256를 모두 수용하는 멀티 알고리즘 컨텍스트 구축
# init_db.py에서 생성된 관리자 암호와 일반 유저 암호를 모두 검증할 수 있습니다.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"], 
    deprecated="auto"
)

# JWT 서명 생성 시 사용할 암호화 알고리즘
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """DB의 해시 접두어를 보고 알고리즘을 자동 선택하여 검증합니다."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def hash_password(password: str) -> str:
    """안전하게 암호를 해싱합니다."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """장기 유효 토큰(Refresh Token) 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """JWT 토큰의 유효성 검증 및 데이터 추출"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.JWTError):
        return None