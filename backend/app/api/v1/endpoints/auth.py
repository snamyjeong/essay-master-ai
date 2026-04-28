# backend/app/api/v1/auth.py
from datetime import timedelta, datetime, timezone # 토큰 만료 시간 계산을 위한 모듈 및 datetime, timezone 임포트
from fastapi import APIRouter, Depends, HTTPException, status # FastAPI 관련 기능 임포트
from fastapi.security import OAuth2PasswordRequestForm # 로그인 폼 처리를 위한 임포트
from sqlalchemy.ext.asyncio import AsyncSession # 비동기식 데이터베이스 세션 타입 임포트
from sqlalchemy import select # 비동기 쿼리를 위한 select 임포트

from app.api import deps # DB 세션 및 인증 의존성 임포트
from app.core import security # 비밀번호 해싱 및 토큰 생성 유틸리티 임포트
from app.core.config import settings # 시스템 설정(비밀번호 만료 등) 임포트
from app.db.models import User # 사용자 DB 모델 임포트
from app.schemas.auth import UserCreate, UserResponse, Token, RefreshTokenRequest, TokenData # 데이터 규격 스키마 임포트

router = APIRouter() # 인증 관련 API 경로를 관리할 라우터 객체 생성

# 1. 회원가입 엔드포인트
@router.post("/signup", response_model=UserResponse)
async def register_user(
    user_in: UserCreate, # 클라이언트로부터 받은 회원가입 정보
    db: AsyncSession = Depends(deps.get_db) # DB 세션 주입 (비동기 방식)
):
    """
    새로운 사용자를 등록하는 API입니다.
    """
    # 비동기 쿼리로 사용자 조회 (username 및 email 중복 확인)
    result_by_username = await db.execute(select(User).filter(User.username == user_in.username))
    existing_user_by_username = result_by_username.scalars().first()

    result_by_email = await db.execute(select(User).filter(User.email == user_in.email))
    existing_user_by_email = result_by_email.scalars().first()

    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자 이름입니다."
        )
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )

    # 비밀번호 해싱 후 새 사용자 객체 생성
    hashed_password = security.hash_password(user_in.password)
    new_user = User(
        username=user_in.username, # username 필드 사용
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True # 기본적으로 활성 상태로 생성
    )

    db.add(new_user) # DB에 사용자 추가
    await db.commit() # 비동기 커밋
    await db.refresh(new_user) # 생성된 ID 등 최신 정보를 DB로부터 다시 읽어옴

    return new_user # 생성된 사용자 정보 반환

# 2. 로그인 엔드포인트 (액세스 토큰 및 갱신 토큰 발급)
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # OAuth2 표준 폼 데이터 수신
    db: AsyncSession = Depends(deps.get_db) # AsyncSession으로 변경
):
    """
    로그인을 처리하고 JWT 액세스 토큰 및 갱신 토큰을 발급하는 API입니다.
    """
    # 비동기 방식으로 사용자 조회 (username으로 조회)
    result = await db.execute(select(User).filter(User.username == form_data.username))
    user = result.scalars().first()

    # 사용자 확인 및 비밀번호 검증
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 이름 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 액세스 토큰 만료 시간 설정 및 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 갱신 토큰 만료 시간 설정 및 생성
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    # 갱신 토큰을 해싱하여 DB에 저장
    hashed_refresh_token = security.hash_password(refresh_token)
    user.refresh_token = hashed_refresh_token
    user.refresh_token_expires_at = datetime.now(timezone.utc) + refresh_token_expires
    
    db.add(user) # 변경된 사용자 정보 DB에 추가 (업데이트)
    await db.commit() # 비동기 커밋
    await db.refresh(user) # 최신 정보를 DB로부터 다시 읽어옴

    # 액세스 토큰 및 갱신 토큰 정보 반환
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# 3. 토큰 갱신 엔드포인트
@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest, # 클라이언트로부터 받은 갱신 토큰 요청
    db: AsyncSession = Depends(deps.get_db) # AsyncSession 주입
):
    """
    갱신 토큰을 사용하여 새로운 액세스 토큰과 갱신 토큰을 발급하는 API입니다.
    """
    # 갱신 토큰 디코딩 및 유효성 검사
    payload = security.decode_token(refresh_request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 갱신 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub") # 갱신 토큰에서 사용자 이름 추출
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="갱신 토큰에 사용자 정보가 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # DB에서 사용자 조회
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 저장된 갱신 토큰과 현재 갱신 토큰 일치 여부 확인
    if not user.refresh_token or not security.verify_password(refresh_request.refresh_token, user.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 갱신 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 갱신 토큰 만료 여부 확인
    if user.refresh_token_expires_at and user.refresh_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="갱신 토큰이 만료되었습니다. 다시 로그인하십시오.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 새로운 액세스 토큰 및 갱신 토큰 생성
    new_access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=new_access_token_expires
    )

    new_refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_refresh_token = security.create_refresh_token(
        data={"sub": user.username}, expires_delta=new_refresh_token_expires
    )

    # 새로운 갱신 토큰을 해싱하여 DB에 저장
    user.refresh_token = security.hash_password(new_refresh_token)
    user.refresh_token_expires_at = datetime.now(timezone.utc) + new_refresh_token_expires
    
    db.add(user) # 변경된 사용자 정보 DB에 추가 (업데이트)
    await db.commit() # 비동기 커밋
    await db.refresh(user) # 최신 정보를 DB로부터 다시 읽어옴

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}