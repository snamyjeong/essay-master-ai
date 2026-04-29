# backend/app/tests/test_api_auth.py
# 이 파일은 사용자 인증(회원가입, 로그인, 토큰 갱신) 관련 API 엔드포인트를 테스트합니다.
# '기본이 튼튼해야 고득점이다!'는 일타 강사의 철학처럼, 인증 시스템의 무결성을 검증합니다.

import pytest # pytest 프레임워크 임포트
from fastapi.testclient import TestClient # FastAPI 테스트 클라이언트 임포트
from sqlalchemy.ext.asyncio import AsyncSession # 비동기 DB 세션 타입 임포트
from backend.app.db.models import User # 사용자 DB 모델 임포트
from backend.app.core import security # 보안 유틸리티 (비밀번호 해싱 등) 임포트

# TestClient 인스턴스는 conftest.py에서 fixture로 제공됩니다.
# db_session fixture는 각 테스트 함수가 호출될 때마다 독립적인 DB 세션을 제공합니다.

@pytest.mark.asyncio # 비동기 테스트 함수를 위한 마크
async def test_register_user_success(client: TestClient, db_session: AsyncSession):
    """
    성공적인 사용자 회원가입을 테스트합니다.
    """
    # 1. 회원가입 요청 데이터 준비
    user_data = {
        "username": "testuser_signup_success",
        "email": "success@example.com",
        "password": "strongpassword123"
    }
    
    # 2. 회원가입 API 호출
    response = client.post("/api/v1/auth/signup", json=user_data)

    # 3. 응답 검증
    assert response.status_code == 200 # HTTP 상태 코드 200 (OK) 확인
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data # 사용자 ID가 생성되었는지 확인
    assert data["is_active"] is True # 기본적으로 활성 상태인지 확인
    assert data["is_superuser"] is False # 기본적으로 관리자가 아닌지 확인
    assert "hashed_password" not in data # 비밀번호가 응답에 포함되지 않는지 확인 (보안)

    # 4. 데이터베이스에서 사용자 존재 여부 및 비밀번호 해싱 확인
    # 직접 쿼리하여 DB에 정확히 저장되었는지 확인합니다.
    user_in_db = await db_session.execute(User.__table__.select().where(User.email == user_data["email"])) # [수정] select 구문 AsyncSession에 맞게 변경
    user_in_db = user_in_db.scalars().first()
    assert user_in_db is not None
    assert security.verify_password(user_data["password"], user_in_db.hashed_password) # 해싱된 비밀번호 검증

@pytest.mark.asyncio
async def test_register_user_duplicate_username_and_email(client: TestClient, db_session: AsyncSession):
    """
    중복된 사용자 이름과 이메일로 회원가입 시도 시 에러를 테스트합니다.
    """
    # 1. 첫 번째 사용자 회원가입 (성공)
    user_data = {
        "username": "duplicateuser",
        "email": "duplicate@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 200

    # 2. 중복된 사용자 이름으로 회원가입 시도
    duplicate_username_data = {
        "username": "duplicateuser",
        "email": "another@example.com",
        "password": "password456"
    }
    response_duplicate_username = client.post("/api/v1/auth/signup", json=duplicate_username_data)
    assert response_duplicate_username.status_code == 400 # HTTP 400 Bad Request
    assert "이미 사용 중인 사용자 이름입니다." in response_duplicate_username.json()["detail"]

    # 3. 중복된 이메일로 회원가입 시도
    duplicate_email_data = {
        "username": "anotheruser",
        "email": "duplicate@example.com",
        "password": "password789"
    }
    response_duplicate_email = client.post("/api/v1/auth/signup", json=duplicate_email_data)
    assert response_duplicate_email.status_code == 400 # HTTP 400 Bad Request
    assert "이미 등록된 이메일입니다." in response_duplicate_email.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client: TestClient, db_session: AsyncSession):
    """
    성공적인 사용자 로그인을 테스트하고 토큰이 발급되는지 확인합니다.
    """
    # 1. 테스트 사용자 생성 (미리 회원가입)
    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "testpassword"
    }
    client.post("/api/v1/auth/signup", json=user_data)

    # 2. 로그인 요청 데이터 준비 (OAuth2PasswordRequestForm 형식)
    form_data = {
        "username": "loginuser",
        "password": "testpassword"
    }
    
    # 3. 로그인 API 호출
    response = client.post("/api/v1/auth/login", data=form_data)

    # 4. 응답 검증
    assert response.status_code == 200 # HTTP 상태 코드 200 (OK) 확인
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # 5. DB에 refresh_token이 저장되었는지 확인
    user_in_db = await db_session.execute(User.__table__.select().where(User.username == form_data["username"])) # [수정] select 구문 AsyncSession에 맞게 변경
    user_in_db = user_in_db.scalars().first()
    assert user_in_db.refresh_token is not None
    # 저장된 refresh_token이 해싱되어 있는지 확인 (원문과 직접 비교 불가)
    assert security.verify_password(data["refresh_token"], user_in_db.refresh_token)

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: TestClient, db_session: AsyncSession):
    """
    잘못된 사용자 이름 또는 비밀번호로 로그인 시도 시 에러를 테스트합니다.
    """
    # 1. 테스트 사용자 생성 (미리 회원가입)
    user_data = {
        "username": "invalidcreduser",
        "email": "invalid@example.com",
        "password": "correctpassword"
    }
    client.post("/api/v1/auth/signup", json=user_data)

    # 2. 잘못된 비밀번호로 로그인 시도
    form_data_wrong_password = {
        "username": "invalidcreduser",
        "password": "wrongpassword"
    }
    response_wrong_password = client.post("/api/v1/auth/login", data=form_data_wrong_password)
    assert response_wrong_password.status_code == 401 # HTTP 401 Unauthorized
    assert "사용자 이름 또는 비밀번호가 올바르지 않습니다." in response_wrong_password.json()["detail"]

    # 3. 존재하지 않는 사용자로 로그인 시도
    form_data_non_existent_user = {
        "username": "nonexistentuser",
        "password": "anypassword"
    }
    response_non_existent_user = client.post("/api/v1/auth/login", data=form_data_non_existent_user)
    assert response_non_existent_user.status_code == 401 # HTTP 401 Unauthorized
    assert "사용자 이름 또는 비밀번호가 올바르지 않습니다." in response_non_existent_user.json()["detail"]

@pytest.mark.asyncio
async def test_refresh_token_success(client: TestClient, db_session: AsyncSession):
    """
    유효한 갱신 토큰으로 새 액세스 토큰과 갱신 토큰을 발급받는 것을 테스트합니다.
    """
    # 1. 테스트 사용자 생성 및 로그인하여 초기 토큰 발급
    user_data = {
        "username": "refreshuser",
        "email": "refresh@example.com",
        "password": "refreshpassword"
    }
    client.post("/api/v1/auth/signup", json=user_data)
    login_response = client.post("/api/v1/auth/login", data={"username": "refreshuser", "password": "refreshpassword"})
    assert login_response.status_code == 200
    initial_refresh_token = login_response.json()["refresh_token"]

    # 2. 갱신 토큰 요청
    refresh_request_data = {"refresh_token": initial_refresh_token}
    response = client.post("/api/v1/auth/refresh", json=refresh_request_data)

    # 3. 응답 검증
    assert response.status_code == 200 # HTTP 상태 코드 200 (OK) 확인
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] != initial_refresh_token # 새로운 갱신 토큰이 발급되었는지 확인

    # 4. DB에 새로운 refresh_token이 저장되었는지 확인
    user_in_db = await db_session.execute(User.__table__.select().where(User.username == user_data["username"])) # [수정] select 구문 AsyncSession에 맞게 변경
    user_in_db = user_in_db.scalars().first()
    assert user_in_db.refresh_token is not None
    assert security.verify_password(data["refresh_token"], user_in_db.refresh_token)

@pytest.mark.asyncio
async def test_refresh_token_invalid_or_expired(client: TestClient, db_session: AsyncSession):
    """
    유효하지 않거나 만료된 갱신 토큰으로 갱신 시도 시 에러를 테스트합니다.
    (만료는 시뮬레이션하기 어려우므로 유효하지 않은 토큰 위주로 테스트)
    """
    # 1. 유효하지 않은 갱신 토큰으로 요청
    invalid_refresh_token_data = {"refresh_token": "invalid.token.here"}
    response_invalid = client.post("/api/v1/auth/refresh", json=invalid_refresh_token_data)
    assert response_invalid.status_code == 401 # HTTP 401 Unauthorized
    assert "유효하지 않거나 만료된 갱신 토큰입니다." in response_invalid.json()["detail"]

    # 2. 빈 갱신 토큰으로 요청
    empty_refresh_token_data = {"refresh_token": ""}
    response_empty = client.post("/api/v1/auth/refresh", json=empty_refresh_token_data)
    assert response_empty.status_code == 422 # HTTP 422 Unprocessable Entity (Pydantic 유효성 검사 실패)

@pytest.mark.asyncio
async def test_get_current_user_success(client: TestClient, db_session: AsyncSession):
    """
    유효한 액세스 토큰으로 현재 사용자 정보를 조회하는 것을 테스트합니다.
    """
    # 1. 테스트 사용자 생성 및 로그인하여 토큰 발급
    user_data = {
        "username": "currentuser",
        "email": "current@example.com",
        "password": "currentpassword"
    }
    client.post("/api/v1/auth/signup", json=user_data)
    login_response = client.post("/api/v1/auth/login", data={"username": "currentuser", "password": "currentpassword"})
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # 2. 사용자 정보 조회 API 호출 (Authorization 헤더 포함)
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    # 3. 응답 검증
    assert response.status_code == 200 # HTTP 상태 코드 200 (OK) 확인
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: TestClient):
    """
    토큰 없이 또는 유효하지 않은 토큰으로 사용자 정보 조회 시도 시 에러를 테스트합니다.
    """
    # 1. 토큰 없이 조회 시도
    response_no_token = client.get("/api/v1/users/me")
    assert response_no_token.status_code == 401 # HTTP 401 Unauthorized
    assert "인증 정보가 유효하지 않습니다." in response_no_token.json()["detail"]

    # 2. 유효하지 않은 토큰으로 조회 시도
    response_invalid_token = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid.fake.token"
        }
    )
    assert response_invalid_token.status_code == 401 # HTTP 401 Unauthorized
    assert "인증 정보가 유효하지 않습니다." in response_invalid_token.json()["detail"]
