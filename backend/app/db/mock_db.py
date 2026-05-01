# backend/app/db/mock_db.py
import uuid # 고유 사용자 식별자 생성을 위해 uuid 임포트
from backend.app.core import security # 비밀번호 해싱 처리를 위한 보안 유틸리티 임포트

# [Global Shared Storage] 모든 모듈이 공유할 전역 메모리 데이터베이스
# { "username/email": { "id": "...", "username": "...", ... } } 구조로 저장됩니다.
mock_users_db = {}

def seed_mock_users_db():
    """서버 기동 시 테스트를 위한 마스터 계정을 자동으로 주입하는 함수입니다."""
    test_username = "snamy78" # 테스트용 아이디 설정
    test_email = "snamy78@gmail.com" # 테스트용 이메일 설정
    test_password = "jarvis1234" # 테스트용 초기 비밀번호

    # 이미 데이터가 존재하는 경우 중복 주입을 방지하기 위한 조건문
    if test_username not in mock_users_db:
        hashed_pw = security.hash_password(test_password) # 평문 비밀번호를 안전하게 해싱 처리
        user_id = str(uuid.uuid4()) # 고유한 UUID 문자열 생성
        
        # 실제 DB 레코드와 동일한 구조로 데이터 구성
        mock_users_db[test_username] = {
            "id": user_id,
            "username": test_username,
            "email": test_email,
            "hashed_password": hashed_pw,
            "is_active": True,
            "refresh_token": None,
            "refresh_token_expires_at": None
        }
        print(f"✅ [MockDB] 마스터 계정 '{test_email}' 시드 완료 (공용 저장소 활성화)")