# 데이터베이스 초기화를 위한 스크립트입니다.
import logging

from sqlalchemy.orm import Session

# SQLAlchemy 모델과 베이스를 임포트합니다.
from backend.app.db.base import Base  # Base 임포트
from backend.app.db.models import User # User 모델 임포트

# CRUD 유틸리티와 설정을 임포트합니다.
from backend.app import crud
from backend.app.core.config import settings
from backend.app.schemas import UserCreate # User 생성 스키마 임포트

logger = logging.getLogger(__name__)

# 데이터베이스 초기 데이터를 생성하는 함수입니다.
def init_db(db: Session) -> None:
    # 모든 테이블을 생성합니다. (이미 존재하면 건너뜁니다)
    # 일반적으로 Alembic과 같은 마이그레이션 도구를 사용하지만, 여기서는 간단한 초기화를 위해 사용합니다.
    Base.metadata.create_all(bind=db.get_bind())

    # 초기 슈퍼유저를 생성합니다.
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="Superuser", # 기본 전체 이름 설정
        )
        user = crud.user.create(db, obj_in=user_in)
        logger.info("✅ 초기 슈퍼유저 생성 완료")
    else:
        logger.info("❕ 슈퍼유저가 이미 존재합니다.")