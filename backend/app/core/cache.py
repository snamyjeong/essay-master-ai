import redis # Redis 클라이언트 라이브러리 임포트
import json # Python 객체를 JSON 문자열로 변환하고 다시 파싱하기 위한 임포트
from typing import Optional, Any # 타입 힌트 (선택적 값, 모든 타입)
from app.core.config import settings # 프로젝트 설정값을 가져오기 위한 임포트

# Redis 클라이언트 인스턴스를 전역으로 생성합니다.
# `decode_responses=True`는 Redis에서 받아오는 바이트 데이터를 자동으로 UTF-8 문자열로 디코딩합니다.
# 설정 파일(settings)에서 REDIS_URL을 가져와 연결합니다.
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Redis 연결 테스트를 위해 ping을 시도합니다.
    redis_client.ping()
    print("✅ Redis 캐시 서버에 성공적으로 연결되었습니다.")
except redis.exceptions.ConnectionError as e:
    # 연결 실패 시 경고 메시지를 출력하고 redis_client를 None으로 설정하여 캐시 기능을 비활성화합니다.
    print(f"❌ Redis 캐시 서버 연결 실패: {e}. 캐싱 기능이 비활성화됩니다.")
    redis_client = None

class CacheService:
    """
    Redis를 사용하여 데이터를 캐시하고 관리하는 서비스 클래스입니다.
    """
    def __init__(self, client: Optional[redis.Redis]):
        """
        CacheService를 초기화합니다.
        Args:
            client: Redis 클라이언트 인스턴스 (연결 실패 시 None일 수 있음)
        """
        self.client = client

    async def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 데이터를 조회합니다.
        Args:
            key: 조회할 데이터의 키
        Returns:
            Any: 캐시된 데이터 (JSON 파싱 후), 없으면 None
        """
        if not self.client: # Redis 클라이언트가 없으면 캐시 기능을 사용하지 않습니다.
            return None
        
        cached_data = self.client.get(key) # Redis에서 키에 해당하는 값을 가져옵니다.
        if cached_data: # 캐시된 데이터가 있다면
            try:
                # JSON 문자열로 저장된 데이터를 Python 객체로 파싱하여 반환합니다.
                return json.loads(cached_data) 
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 원본 문자열을 반환하거나 None을 반환하여 오류 처리합니다.
                print(f"⚠️ 캐시 데이터 JSON 파싱 실패: {key}")
                return cached_data # 혹은 None을 반환하여 잘못된 캐시 데이터를 사용하지 않도록 할 수 있습니다.
        return None # 캐시된 데이터가 없으면 None 반환

    async def set(self, key: str, value: Any, ex: Optional[int] = None):
        """
        데이터를 캐시에 저장합니다.
        Args:
            key: 저장할 데이터의 키
            value: 저장할 데이터 (Python 객체, JSON 직렬화됨)
            ex: 만료 시간 (초 단위), None이면 무기한
        """
        if not self.client: # Redis 클라이언트가 없으면 캐시 기능을 사용하지 않습니다.
            return
        
        # Python 객체를 JSON 문자열로 직렬화하여 Redis에 저장합니다.
        # Redis는 주로 문자열 데이터를 저장하므로, 복잡한 객체는 JSON으로 변환합니다.
        self.client.set(key, json.dumps(value), ex=ex) 

    async def delete(self, key: str):
        """
        캐시에서 데이터를 삭제합니다.
        Args:
            key: 삭제할 데이터의 키
        """
        if not self.client: # Redis 클라이언트가 없으면 캐시 기능을 사용하지 않습니다.
            return
        self.client.delete(key) # Redis에서 키에 해당하는 데이터를 삭제합니다.

# 전역 CacheService 인스턴스 생성
cache_service = CacheService(redis_client)