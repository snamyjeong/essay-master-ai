from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.models import Token, UserLogin, User # Token과 UserLogin 모델 임포트
from backend.app.utils import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES # Access Token 만료 시간 임포트
)

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/auth", # /auth 경로 접두사 사용
    tags=["Auth"],  # API 문서에 표시될 태그
)

# --- 로그인 엔드포인트 ---
@router.post("/login", response_model=Token)
async def login_for_access_tokens(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    사용자 이름과 비밀번호를 받아 Access Token과 Refresh Token을 발급합니다.
    """
    # 사용자 인증 시도
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        # 인증 실패 시 401 Unauthorized 에러 발생
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Access Token 만료 시간 설정
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Access Token 생성
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Refresh Token 생성 (Access Token보다 긴 만료 시간)
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    
    # 생성된 토큰 반환
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

# --- 토큰 유효성 검사 엔드포인트 ---
@router.get("/verify", response_model=User)
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """
    현재 활성 사용자의 토큰 유효성을 검사하고 사용자 정보를 반환합니다.
    """
    # get_current_active_user 의존성 주입을 통해 토큰이 이미 검증되었으므로,
    # 단순히 현재 사용자 정보를 반환합니다.
    return current_user

# --- 리프레시 토큰으로 새로운 Access Token 발급 엔드포인트 (선택 사항) ---
# 여기서는 복잡성을 위해 생략하지만, 실제 프로덕션에서는 Refresh Token을 이용한
# Access Token 갱신 로직을 구현하는 것이 일반적입니다.
# 예: @router.post("/refresh", response_model=Token)
# async def refresh_access_token(refresh_token: str = Depends(oauth2_scheme)):
#     ...
