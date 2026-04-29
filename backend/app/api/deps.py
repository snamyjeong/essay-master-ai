# backend/app/api/deps.py
from typing import Generator, Optional # 타입 힌트를 위한 임포트
from fastapi import Depends, HTTPException, status # FastAPI 의존성 및 예외 처리
from fastapi.security import OAuth2PasswordBearer # OAuth2 토큰 인증 방식 사용
from jose import jwt, JWTError # JWT 토큰 해독을 위한 라이브러리
from sqlalchemy.ext.asyncio import AsyncSession # [수정] 비동기식 DB 세션 타입
from sqlalchemy import select # [추가] 비동기 쿼리를 위한 select 임포트

from backend.app.core.config import settings # [교정] 프로젝트 루트 기준 절대 경로로 수정하여 경로 이탈 방지
from backend.app.core import security # [교정] 보안 유틸리티 절대 경로로 수정
from backend.app.db.database import AsyncSessionLocal # [교정] 비동기 세션 팩토리 절대 경로로 수정
from backend.app.db.models import User # [교정] 유저 모델 절대 경로로 수정
from backend.app.schemas.auth import TokenData # [교정] 토큰 규격 절대 경로로 수정

# 토큰을 추출할 API 경로를 지정합니다. (Swagger UI에서 인증 버튼 활성화용)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_db() -> Generator[AsyncSession, None, None]: # [수정] 비동기 제너레이터 및 AsyncSession 타입 힌트
    """
    데이터베이스 세션을 생성하고 사용 후 자동으로 닫아주는 의존성 함수입니다.
    """
    async with AsyncSessionLocal() as session: # [수정] 비동기 컨텍스트 매니저 사용
        try:
            yield session
        finally:
            await session.close() # [수정] 비동기 세션 닫기

async def get_current_user(
    db: AsyncSession = Depends(get_db), # [수정] DB 세션 타입 AsyncSession으로 변경
    token: str = Depends(reusable_oauth2) # 토큰 주입
) -> User:
    """
    JWT 토큰을 검증하고 토큰에 담긴 유저 정보가 실제 DB에 있는지 확인하여 반환합니다.
    이 함수는 모든 '로그인 필수' API에서 가드 역할을 수행합니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. 토큰 해독 시도
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        username: str = payload.get("sub") # 토큰의 'sub' 필드에서 유저 식별자(username) 추출
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username) # [수정] email 대신 username 사용
    except JWTError:
        raise credentials_exception

    # 2. DB에서 실제 유저 조회 (비동기 쿼리 사용)
    result = await db.execute(select(User).filter(User.username == token_data.username)) # [수정] 비동기 쿼리로 변경
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
        
    return user # 검증된 유저 객체 반환