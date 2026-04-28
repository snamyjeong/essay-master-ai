import pytest
from httpx import AsyncClient
from typing import Dict, Any

# 테스트용 유틸리티 함수 (필요시 백엔드 유틸리티 함수를 모방)
def get_user_headers(token: str) -> Dict[str, str]:
    """사용자 인증 토큰을 포함한 헤더를 반환합니다."""
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_read_users_not_authenticated(client: AsyncClient) -> None:
    """인증되지 않은 사용자가 사용자 목록을 조회할 수 없는지 테스트합니다."""
    response = await client.get("/api/v1/users/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

@pytest.mark.asyncio
async def test_read_users_as_normal_user_forbidden(client: AsyncClient, normal_user_token: str) -> None:
    """일반 사용자가 사용자 목록을 조회할 수 없는지 테스트합니다 (어드민 권한 필요)."""
    headers = get_user_headers(normal_user_token)
    response = await client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "The user doesn't have enough privileges"}

@pytest.mark.asyncio
async def test_read_users_as_superuser(client: AsyncClient, superuser_token: str) -> None:
    """슈퍼유저가 사용자 목록을 조회할 수 있는지 테스트합니다."""
    headers = get_user_headers(superuser_token)
    response = await client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    # 최소한 슈퍼유저 자신은 리스트에 있어야 합니다.
    users = response.json()
    assert any(user["email"] == "admin@example.com" for user in users)

@pytest.mark.asyncio
async def test_create_user_as_superuser(client: AsyncClient, superuser_token: str) -> None:
    """슈퍼유저가 새 사용자를 생성할 수 있는지 테스트합니다."""
    headers = get_user_headers(superuser_token)
    new_user_data = {
        "email": "newuser@example.com",
        "password": "securepassword",
        "full_name": "New Test User",
        "is_active": True,
        "is_superuser": False
    }
    response = await client.post("/api/v1/users/", json=new_user_data, headers=headers)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["email"] == new_user_data["email"]
    assert "password" not in created_user # 비밀번호는 반환되지 않아야 합니다.

@pytest.mark.asyncio
async def test_create_existing_user_as_superuser(client: AsyncClient, superuser_token: str) -> None:
    """슈퍼유저가 이미 존재하는 이메일로 사용자를 생성할 수 없는지 테스트합니다."""
    headers = get_user_headers(superuser_token)
    existing_user_data = {
        "email": "admin@example.com", # 이미 존재하는 이메일
        "password": "anotherpassword",
        "full_name": "Existing User",
        "is_active": True,
        "is_superuser": False
    }
    response = await client.post("/api/v1/users/", json=existing_user_data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "The user with this username already exists in the system."}

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, normal_user_token: str) -> None:
    """일반 사용자가 자신의 정보를 성공적으로 조회하는지 테스트합니다."""
    headers = get_user_headers(normal_user_token)
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "test@example.com" # normal_user_token에 해당하는 이메일 가정

@pytest.mark.asyncio
async def test_update_user_me(client: AsyncClient, normal_user_token: str) -> None:
    """일반 사용자가 자신의 정보를 성공적으로 업데이트하는지 테스트합니다."""
    headers = get_user_headers(normal_user_token)
    update_data = {
        "full_name": "Updated Test Name",
        "email": "test@example.com" # 이메일은 변경하지 않는 것으로 가정
    }
    response = await client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["full_name"] == update_data["full_name"]
    assert updated_user["email"] == update_data["email"]

@pytest.mark.asyncio
async def test_update_user_me_with_password_change(client: AsyncClient, normal_user_token: str) -> None:
    """일반 사용자가 자신의 비밀번호를 업데이트하는지 테스트합니다."""
    headers = get_user_headers(normal_user_token)
    update_data = {
        "password": "newsecurepassword",
        "email": "test@example.com" # 이메일은 변경하지 않는 것으로 가정
    }
    response = await client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == update_data["email"]
    # 비밀번호 변경 후 로그인 테스트 (여기서는 구현 생략, 실제 통합 테스트에서 확인)

@pytest.mark.asyncio
async def test_update_user_me_invalid_email(client: AsyncClient, normal_user_token: str) -> None:
    """일반 사용자가 자신의 정보를 유효하지 않은 이메일로 업데이트할 수 없는지 테스트합니다."""
    headers = get_user_headers(normal_user_token)
    update_data = {
        "email": "invalid-email",
        "full_name": "Invalid Email User"
    }
    response = await client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == 422 # FastAPI의 Pydantic 유효성 검사 실패 코드
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_update_user_me_existing_email(client: AsyncClient, normal_user_token: str, superuser_token: str) -> None:
    """일반 사용자가 자신의 이메일을 이미 존재하는 다른 사용자의 이메일로 업데이트할 수 없는지 테스트합니다."""
    # 먼저 테스트용 다른 일반 유저를 생성합니다.
    headers_superuser = get_user_headers(superuser_token)
    other_user_data = {
        "email": "other@example.com",
        "password": "otherpassword",
        "full_name": "Other User",
        "is_active": True,
        "is_superuser": False
    }
    await client.post("/api/v1/users/", json=other_user_data, headers=headers_superuser)

    headers_normal_user = get_user_headers(normal_user_token)
    update_data = {
        "email": "other@example.com", # 이미 존재하는 이메일
        "full_name": "Attempting to change email"
    }
    response = await client.put("/api/v1/users/me", json=update_data, headers=headers_normal_user)
    assert response.status_code == 400
    assert response.json() == {"detail": "The user with this username already exists in the system."}

# 추가적으로, 특정 사용자를 ID로 조회, 업데이트, 삭제하는 어드민 기능 테스트도 필요합니다.
# (현재 users.py에 직접적인 ID 기반 엔드포인트는 없는 것으로 보이나,
# 만약 있다면 해당 부분에 대한 테스트도 추가해야 합니다.)
