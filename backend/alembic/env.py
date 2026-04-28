import os
import sys
import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 프로젝트 루트 디렉토리를 Python 경로에 추가합니다.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# backend 디렉토리를 Python 경로에 추가하여 'app' 모듈을 찾을 수 있도록 합니다.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Alembic Config 객체, .ini 파일의 값에 접근할 수 있습니다.
config = context.config

# Python 로깅을 위한 설정 파일을 해석합니다.
# 이 라인은 기본적으로 로거를 설정합니다.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 'autogenerate' 지원을 위해 여기에 모델의 MetaData 객체를 추가합니다.
from app.core.config import settings
from app.db.base import Base

# app.db.models의 모든 모델들을 임포트
from app.db.models import User, Document, QuizResult, TypingRecord

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """'오프라인' 모드에서 마이그레이션을 실행합니다.

    URL만으로 컨텍스트를 구성하며 Engine은 사용하지 않습니다.
    Engine 생성을 건너뛰므로 DBAPI가 필요하지 않습니다.

    여기서 context.execute() 호출은 주어진 문자열을 스크립트 출력으로 내보냅니다.
    """
    url = settings.SQLALCHEMY_DATABASE_URL.replace("sqlite+aiosqlite", "sqlite") # Alembic 오프라인 모드에서는 동기 SQLite 사용
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """'온라인' 모드에서 마이그레이션을 실행합니다.

    이 시나리오에서는 Engine을 생성하고 연결을 컨텍스트와 연결해야 합니다.
    """
    configuration = config.get_section(config.config_ini_section)
    # Alembic 내부에서 사용할 DB URL은 동기 SQLite 드라이버로 변경합니다.
    # 애플리케이션은 계속 aiosqlite를 사용합니다.
    configuration["sqlalchemy.url"] = settings.SQLALCHEMY_DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

    # 동기 Engine을 생성합니다.
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection: # 동기 연결 사용
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
