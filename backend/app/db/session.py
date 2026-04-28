# 데이터베이스 세션 및 엔진을 설정하는 파일입니다.

from sqlalchemy import create_engine # 데이터베이스 엔진을 생성하는 함수를 가져옵니다.
from sqlalchemy.orm import sessionmaker # 세션 팩토리를 생성하는 함수를 가져옵니다.

from backend.app.core.config import settings # 설정값을 임포트합니다.


# SQLAlchemy 엔진을 생성합니다.
# settings.SQLALCHEMY_DATABASE_URL은 config.py에서 정의된 PostgreSQL 연결 문자열입니다.
# connect_args는 SQLite를 사용할 때만 필요한 인자이므로, PostgreSQL에서는 빈 딕셔너리를 전달하거나 생략할 수 있습니다.
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True) # 데이터베이스 엔진을 생성합니다.

# SessionLocal 클래스를 생성합니다.
# autocommit=False: 트랜잭션이 자동으로 커밋되지 않도록 설정합니다.
# autoflush=False: 쿼리 실행 전에 변경사항이 자동으로 플러시되지 않도록 설정합니다.
# bind=engine: 생성된 엔진에 세션을 바인딩합니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # 데이터베이스 세션 팩토리를 생성합니다.
