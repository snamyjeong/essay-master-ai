from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# for autogenerate
import sys
import os
sys.path.append(os.getcwd()) # 현재 작업 디렉토리를 Python 경로에 추가
from backend.app.db.base import Base # 베이스 모델 임포트
from backend.app.core.config import settings # 설정 값 임포트

# this is the Alembic Config object, which provides
# access to values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # SQLAlchemy Base 클래스의 MetaData를 타겟으로 설정

# other values from the config, defined by the needs of env.py, 
# can be acquired: 
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is optionally passed in.
    By skipping the Engine creation we don't even need a DBAPI to be
    available.  Calls to context.execute() here emit the given string to a file
    output or stdout.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=settings.SQLALCHEMY_DATABASE_URL, # 설정 파일에서 DB URL 사용
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # compare_type=True, # 컬럼 타입 비교 활성화
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
