# tests/conftest.py
# 이 파일은 pytest 테스트를 위한 공통 설정(fixture)을 정의합니다.
# '준비된 자만이 승리한다!'는 일타 강사의 철학처럼, 견고한 테스트 환경을 구축합니다.

import pytest # pytest 프레임워크 임포트
from fastapi.testclient import TestClient # FastAPI 테스트 클라이언트 임포트
from sqlalchemy import create_engine # SQLAlchemy 엔진 생성을 위한 임포트
from sqlalchemy.orm import sessionmaker # SQLAlchemy 세션 생성을 위한 임포트
from app.main import app # 테스트할 FastAPI 애플리케이션 임포트
from app.db.database import Base # SQLAlchemy Base 모델 임포트
from app.api.deps import get_db, get_current_user # 의존성 주입 함수 임포트
from app.db.models import User # 사용자 모델 임포트 (모의 사용자 생성을 위함)
from unittest.mock import AsyncMock, patch # 비동기 함수 모킹을 위한 AsyncMock과 patch 임포트
from app.services.rag_learning_service import RAGLearningService # RAG 서비스 임포트

# 1. 테스트용 데이터베이스 설정 (SQLite 인메모리 DB)
# 실제 데이터베이스에 영향을 주지 않으면서 빠른 테스트를 위해 SQLite 인메모리 데이터베이스를 사용합니다.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # 테스트용 SQLite 파일 DB 경로 (인메모리 사용 시 "sqlite:///:memory:")

# create_engine 함수를 사용하여 SQLAlchemy 엔진을 생성합니다.
# connect_args는 SQLite에만 필요하며, 다중 스레드에서 동시에 접근할 수 있도록 설정합니다.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# sessionmaker를 사용하여 세션 클래스를 생성합니다.
# autocommit=False: 자동으로 커밋하지 않음 (명시적 커밋 필요)
# autoflush=False: 자동으로 플러시하지 않음 (명시적 플러시 필요)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. 테스트용 DB 세션 Fixture
# 각 테스트 함수가 호출될 때마다 독립적인 DB 세션을 제공합니다.
@pytest.fixture(name="db_session")
def db_session_fixture():
    """
    테스트를 위한 데이터베이스 세션을 제공합니다.
    각 테스트 시작 전에 모든 테이블을 생성하고, 테스트 종료 후에 롤백합니다.
    """
    Base.metadata.create_all(bind=engine) # 테스트 시작 전 테이블 생성
    session = TestingSessionLocal() # 새로운 세션 생성
    try:
        yield session # 세션 반환 (테스트 함수가 이 세션을 사용)
    finally:
        session.close() # 테스트 종료 후 세션 닫기
        Base.metadata.drop_all(bind=engine) # 테스트 종료 후 모든 테이블 삭제 (데이터 초기화)

# 3. 의존성 주입 오버라이드 Fixture (DB 세션)
# FastAPI의 get_db 의존성을 테스트용 DB 세션으로 교체합니다。
@pytest.fixture(name="override_get_db")
def override_get_db_fixture(db_session):
    """
    FastAPI의 get_db 의존성을 오버라이드하여 테스트용 DB 세션을 제공합니다.
    """
    def _override_get_db():
        yield db_session # 테스트용 DB 세션 반환
    app.dependency_overrides[get_db] = _override_get_db # 의존성 오버라이드
    yield # 테스트 실행
    app.dependency_overrides.clear() # 오버라이드 해제 (테스트 후 원상 복구)

# 4. 모의(Mock) 사용자 Fixture
# 로그인된 사용자가 필요한 테스트를 위해 가상의 사용자 객체를 제공합니다.
@pytest.fixture(name="mock_user")
def mock_user_fixture():
    """
    테스트를 위한 모의(Mock) 사용자 객체를 생성합니다.
    """
    user = User(id=1, username="testuser", email="test@example.com", hashed_password="hashedpassword", is_active=True)
    return user

# 5. 의존성 주입 오버라이드 Fixture (현재 사용자)
# FastAPI의 get_current_user 의존성을 모의 사용자 객체로 교체합니다.
@pytest.fixture(name="override_get_current_user")
def override_get_current_user_fixture(mock_user):
    """
    FastAPI의 get_current_user 의존성을 오버라이드하여 모의 사용자 객체를 제공합니다.
    """
    def _override_get_current_user():
        return mock_user # 모의 사용자 객체 반환
    app.dependency_overrides[get_current_user] = _override_get_current_user # 의존성 오버라이드
    yield # 테스트 실행
    app.dependency_overrides.clear() # 오버라이드 해제

# 6. FastAPI 테스트 클라이언트 Fixture
# FastAPI 애플리케이션을 테스트할 수 있는 클라이언트를 제공합니다.
@pytest.fixture(name="client")
def client_fixture(override_get_db, override_get_current_user):
    """
    FastAPI TestClient를 생성합니다.
    get_db와 get_current_user 의존성이 오버라이드된 상태로 제공됩니다.
    """
    with TestClient(app) as c: # TestClient 생성 및 컨텍스트 관리
        yield c # 클라이언트 반환

# 7. AI 모델 (ChatGoogleGenerativeAI) Mocking Fixture
# 실제 AI 모델 호출을 피하기 위해 ChatGoogleGenerativeAI 객체를 Mocking합니다.
@pytest.fixture
def mock_llm():
    """
    QuizGenerationService 내부의 ChatGoogleGenerativeAI 인스턴스를 Mocking합니다.
    """
    with patch("langchain_google_genai.ChatGoogleGenerativeAI", autospec=True) as mock_class:
        mock_instance = AsyncMock() # 비동기 메서드를 가질 수 있는 Mock 인스턴스
        mock_class.return_value = mock_instance # ChatGoogleGenerativeAI() 호출 시 Mock 인스턴스 반환
        yield mock_instance # Mock 인스턴스 반환 (테스트에서 Mock 설정 가능)

# 8. RAGLearningService Mocking Fixture
# RAGLearningService 내부의 ChromaDB 클라이언트 및 PDF 처리 로직을 Mocking합니다.
@pytest.fixture
def mock_rag_service():
    """
    RAGLearningService의 인스턴스를 Mocking하여 실제 ChromaDB 호출을 방지합니다.
    """
    with patch("app.services.rag_learning_service.rag_learning_service", autospec=True) as mock_rag_instance:
        yield mock_rag_instance # Mock 인스턴스 반환