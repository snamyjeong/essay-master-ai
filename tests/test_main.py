# tests/test_main.py
# 이 파일은 FastAPI 애플리케이션의 메인 엔트리 포인트(app.main)를 테스트합니다.
# 서버의 기본적인 동작 및 헬스 체크 엔드포인트의 무결성을 검증합니다.

from fastapi.testclient import TestClient # FastAPI 테스트 클라이언트 임포트
from app.main import app # 테스트할 FastAPI 애플리케이션 인스턴스 임포트

# TestClient 인스턴스 생성
# 이 클라이언트를 통해 FastAPI 애플리케이션에 HTTP 요청을 보낼 수 있습니다.
client = TestClient(app)

def test_health_check():
    """
    루트 경로("/")의 헬스 체크 엔드포인트가 정상적으로 작동하는지 테스트합니다.
    - HTTP 상태 코드가 200 OK인지 확인합니다.
    - 응답 JSON에 예상되는 메시지와 페르소나 정보가 포함되어 있는지 확인합니다.
    """
    response = client.get("/") # GET 요청을 루트 경로로 보냅니다.
    assert response.status_code == 200 # 응답 상태 코드가 200인지 확인 (성공)

    data = response.json() # 응답 본문을 JSON으로 파싱합니다.
    assert data["status"] == "online" # "status" 필드가 "online"인지 확인
    assert "Jarvis Neo-Genesis V3가 정상 작동 중입니다." in data["message"] # "message" 필드에 특정 문자열 포함 확인
    assert "30년 경력 일타 강사 정성남 모드 활성화" in data["persona"] # "persona" 필드에 특정 문자열 포함 확인
