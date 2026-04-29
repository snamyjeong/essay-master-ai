from fastapi.testclient import TestClient
from backend.app.main import app
import datetime # datetime 모듈을 추가합니다. (timestamp 비교에 필요)

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

    response_data = response.json()

    # 'timestamp' 필드의 존재 여부를 확인합니다.
    assert "timestamp" in response_data

    # 'timestamp' 필드를 제외한 나머지 필드를 비교합니다.
    expected_data = {
        "status": "online",
        "message": "Jarvis Neo-Genesis V3가 정상 작동 중입니다.",
        "persona": "30년 경력 일타 강사 정성남 모드 활성화", # 이 라인을 추가합니다.
    }

    # 동적으로 변하는 timestamp 필드를 삭제하고 나머지 필드를 비교합니다.
    del response_data["timestamp"]
    assert response_data == expected_data
