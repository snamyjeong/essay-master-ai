# -*- coding: utf-8 -*-
from typing import Generator, Optional # 타입 힌트용 임포트
from fastapi import Header, Depends, HTTPException, status # FastAPI 핵심 기능 임포트
from fastapi.security import OAuth2PasswordBearer # 토큰 추출용 보안 클래스
from jose import jwt, JWTError # JWT 토큰 처리용 라이브러리
from sqlalchemy.ext.asyncio import AsyncSession # 비동기 세션 타입 힌트

from backend.app.core.config import settings # 전역 설정 정보
from backend.app.core import security # 보안 유틸리티
from backend.app.db.database import AsyncSessionLocal # DB 세션 팩토리
from backend.app.db.models import User # SQLAlchemy 유저 모델
from backend.app.schemas.auth import TokenData # 토큰 데이터 규격
# [핵심] auth.py와 동일한 메모리 공간을 공유하기 위해 임포트
from backend.app.db.mock_db import mock_users_db

# OAuth2 토큰 추출 설정 (로그인 경로 지정)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_db() -> Generator[AsyncSession, None, None]:
    """데이터베이스 비동기 세션 생성 및 자동 반납 의존성 함수입니다."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() # 세션 명시적 종료

async def get_current_user(
    db: AsyncSession = Depends(get_db), # 실제 DB 세션 의존성
    token: str = Depends(reusable_oauth2) # 헤더에서 추출된 JWT 토큰
) -> User:
    """
    JWT 토큰의 유효성을 검증하고, 공유 Mock DB에서 해당 유저를 찾아 반환합니다.
    이 함수가 성공해야만 401 에러를 통과할 수 있습니다.
    """
    # [개발용] 마스터 토큰 프리패스 로직
    if settings.DEBUG and token == settings.MASTER_TOKEN:
        return User(id="-1", username="dev_admin", email="dev@example.com", is_active=True)

    # 인증 실패 시 반환할 공통 예외 객체 정의
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다. 다시 로그인해 주세요.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. 수신된 토큰 해독 및 페이로드 추출
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        username: str = payload.get("sub") # 토큰 발행 시 담았던 사용자 식별자(username) 추출
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. [핵심 보정] 실제 DB 대신 공유된 mock_users_db 딕셔너리에서 유저 탐색
    # 아이디(username) 또는 이메일(email) 필드 중 하나라도 일치하는 데이터를 찾습니다.
    user_data = next((u for u in mock_users_db.values() 
                      if u["username"] == username or u["email"] == username), None)

    # 유저 정보가 명부에 없는 경우 인증 실패 처리
    if user_data is None:
        raise credentials_exception
    
    # 3. 획득한 딕셔너리 데이터를 SQLAlchemy User 모델 객체로 변환 (호환성 유지)
    # 필요한 필드(id, username, email 등)만 추출하여 객체화합니다.
    user = User(
        id=user_data.get("id"),
        username=user_data.get("username"),
        email=user_data.get("email"),
        is_active=user_data.get("is_active", True)
    )
        
    return user # 최종 검증된 유저 객체 반환