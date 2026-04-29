# 데이터베이스 세션을 설정하고 관리합니다.
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # 비동기 엔진 및 세션 관리를 위한 클래스를 임포트합니다.
from sqlalchemy.orm import sessionmaker # 세션 생성을 위한 팩토리 함수를 임포트합니다.

# 프로젝트 설정을 임포트합니다.
from backend.app.core.config import settings

# 데이터베이스 URL을 기반으로 SQLAlchemy 엔진을 생성합니다.
# connect_args는 SQLite 사용 시 필요합니다 (다중 스레드에서 동일 연결 시도 방지).
engine = create_async_engine( # [교정] SQLite 비동기 대응을 위해 create_async_engine을 사용합니다.
    settings.SQLALCHEMY_DATABASE_URL, # config.py에서 생성된 sqlite+aiosqlite:// 경로를 사용합니다.
    pool_pre_ping=True # 연결 유효성 체크 기능을 활성화합니다.
)

SessionLocal = sessionmaker( # [교정] 비동기 세션을 생성하도록 설정을 변경합니다.
    autocommit=False, # 자동 커밋을 끕니다.
    autoflush=False, # 자동 플러시를 끕니다.
    bind=engine, # 생성한 비동기 엔진을 바인딩합니다.
    class_=AsyncSession # 세션 인스턴스를 AsyncSession으로 강제하여 비동기 처리를 보장합니다.
)