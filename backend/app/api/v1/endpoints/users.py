# backend/app/api/v1/users.py
from fastapi import APIRouter, Depends # FastAPI 라우터 및 의존성 주입 도구 임포트
from sqlalchemy.ext.asyncio import AsyncSession # [교정] 비동기 세션 타입을 사용하도록 변경합니다.

from backend.app.api import deps # [교정] 인증 의존성 함수를 절대 경로를 통해 안전하게 가져옵니다.
from backend.app.db.models import User # [교정] User 모델을 절대 경로를 통해 정확하게 매핑합니다.
from backend.app.schemas.auth import UserResponse # [교정] 응답용 데이터 스키마를 절대 경로로 불러옵니다.

# APIRouter 인스턴스를 생성하여 사용자 관련 경로를 관리합니다.
router = APIRouter()

# 현재 로그인된 사용자의 정보를 가져오는 엔드포인트
# response_model: 응답 데이터의 형식을 UserResponse 스키마에 맞춥니다.
@router.get("/me", response_model=UserResponse)
def read_current_user(
    # [교정] deps.get_current_user를 통해 토큰을 검증하고 현재 인증된 사용자 정보를 주입받습니다.
    # 이 과정에서 내부적으로 DB 세션과 JWT 토큰 검증이 모두 이루어집니다.
    current_user: User = Depends(deps.get_current_user) 
):
    """
    현재 로그인된 사용자의 정보를 안전하게 반환합니다.
    이미 'deps.get_current_user'에서 검증이 끝났으므로 객체를 그대로 반환하면 됩니다.
    """
    # 20년 차 베테랑의 설계답게 불필요한 DB 조회를 줄이고 검증된 객체만 반환합니다.
    return current_user