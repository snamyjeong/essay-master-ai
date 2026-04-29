# backend/app/db/database.py
# 데이터베이스 연결 및 세션 관리를 담당하는 모듈입니다.

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.app.core.config import settings # 설정값을 가져오기 위해 settings 임포트

# SQLAlchemy 비동기 엔진을 생성합니다.
# settings.SQLALCHEMY_DATABASE_URL을 사용하여 데이터베이스 URL을 가져옵니다.
# echo=True: SQLAlchemy가 실행하는 모든 SQL 쿼리를 콘솔에 출력하여 디버깅에 유용합니다.
# connect_args: SQLite의 경우에만 {"check_same_thread": False}를 적용하고, 그 외에는 빈 딕셔너리 사용
connect_args = {}
if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=True,
    connect_args=connect_args # 조건부 connect_args 적용
)

# 비동기 세션 생성을 위한 팩토리를 정의합니다.
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# FastAPI 의존성 주입(Dependency Injection)을 위한 비동기 데이터베이스 세션 제너레이터 함수입니다.
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()