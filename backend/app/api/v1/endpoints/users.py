# backend/app/api/v1/users.py
from fastapi import APIRouter, Depends # FastAPI 라우터 및 의존성 주입 도구 임포트
from sqlalchemy.orm import Session # 동기식 데이터베이스 세션 타입을 위한 임포트

from app.api import deps # [핵심] 우리가 방금 수정한 get_current_user가 들어있는 곳입니다.
from app.db.models import User # 데이터베이스의 User 모델 임포트
from app.schemas.auth import UserResponse # 클라이언트 응답용 데이터 규격 임포트

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