from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime
import time # [추가] 요청 처리 시간 측정을 위해 time 모듈을 임포트합니다.
from starlette.middleware.base import BaseHTTPMiddleware # [추가] 커스텀 미들웨어를 위해 BaseHTTPMiddleware를 임포트합니다.
from starlette.requests import Request # [추가] Request 객체에 접근하기 위해 Request를 임포트합니다.
from starlette.responses import Response # [추가] Response 객체에 접근하기 위해 Response를 임포트합니다.
from backend.app.api.v1 import api_router as api_v1_router # V1 API 라우터를 임포트합니다.
from backend.app.api.v2 import api_router as api_v2_router # V2 API 라우터를 임포트합니다.
from backend.app.core.logging import get_logger # get_logger 함수를 임포트합니다.
from backend.app.core.config import settings # 설정값을 가져오기 위해 settings 임포트
from jose import jwt # [추가] JWT 토큰을 디코딩하기 위해 jose 라이브러리를 임포트합니다.
from backend.app.core.security import ALGORITHM # [추가] JWT 알고리즘을 임포트합니다.


# 로거 인스턴스 가져오기
logger = get_logger(__name__)

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="Jarvis Neo-Genesis V3",
    description="30년 경력 일타 강사 페르소나 기반 AI 학습 플랫폼",
    version="3.0.0"
)

# [중요] CORS(Cross-Origin Resource Sharing) 설정
# 수석님의 태블릿(8000번 포트)에서 백엔드(8001번 포트)로 신호를 보낼 때
# 브라우저가 보안상 막지 않도록 허용 범위를 설정합니다.
app.add_middleware(
    CORSMiddleware,
    # [수정] config.py에서 정의된 CORS_ORIGINS 설정을 사용합니다.
    allow_origins=settings.CORS_ORIGINS, # 모든 도메인에서의 접근을 허용 (개발 및 테스트 단계)
    allow_credentials=True, # 쿠키 및 인증 정보 포함 허용
    allow_methods=["*"], # GET, POST, PUT, DELETE 등 모든 HTTP 메서드 허용
    allow_headers=["*"], # 모든 HTTP 헤더 요청 허용
)

# [추가] 요청 로깅 미들웨어 정의
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time() # 요청 처리 시작 시간 기록

        user_id = "anonymous" # 기본 사용자 ID를 "anonymous"로 설정
        # Authorization 헤더에서 JWT 토큰을 추출하여 사용자 ID를 가져옵니다.
        if "authorization" in request.headers:
            token_string = request.headers["authorization"].replace("Bearer ", "") # "Bearer " 접두사 제거
            try:
                # JWT 토큰을 디코딩하여 페이로드에서 사용자 ID (sub)를 추출합니다.
                payload = jwt.decode(token_string, settings.SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub", "anonymous") # JWT 페이로드에서 "sub" 필드를 사용자 ID로 사용
            except Exception:
                user_id = "invalid_token" # 토큰 디코딩 실패 시 "invalid_token"으로 설정

        # 요청 시작 로그 (디버그 레벨)
        logger.debug(f"[User ID: {user_id}] Request: {request.method} {request.url.path} starting.")

        response = await call_next(request) # 다음 미들웨어 또는 실제 라우트 핸들러 호출

        process_time = time.time() - start_time # 요청 처리 시간 계산
        # 요청 완료 로그 (정보 레벨)
        logger.info(f"[User ID: {user_id}] Request: {request.method} {request.url.path} finished in {process_time:.4f}s. Status: {response.status_code}")

        return response # 응답 반환

# [추가] RequestLoggingMiddleware를 FastAPI 애플리케이션에 등록합니다.
# 미들웨어는 등록된 순서의 역순으로 실행됩니다.
app.add_middleware(RequestLoggingMiddleware)


# 각 버전별 통합 라우터를 등록합니다.
# 이렇게 하면 main.py는 버전 관리의 진입점 역할만 하고, 각 버전의 세부 라우팅은 해당 버전의 __init__.py에서 관리됩니다.

# V1 API 라우터 등록
app.include_router(api_v1_router, prefix=settings.API_V1_STR) # V1 라우터에 대한 접두사 설정

# V2 API 라우터 등록 (현재는 플레이스홀더, 추후 개발 예정)
app.include_router(api_v2_router, prefix="/api/v2") # V2 라우터에 대한 접두사 설정


@app.on_event("startup") # 애플리케이션 시작 시 실행되는 이벤트 핸들러
async def startup_event():
    logger.info("Jarvis Neo-Genesis V3 애플리케이션 시작.") # 애플리케이션 시작 로그 기록

@app.on_event("shutdown") # 애플리케이션 종료 시 실행되는 이벤트 핸들러
async def shutdown_event():
    logger.info("Jarvis Neo-Genesis V3 애플리케이션 종료.") # 애플리케이션 종료 로그 기록

@app.get("/") # 서버의 생존 여부를 확인하기 위한 루트 경로 설정
async def health_check():
    """
    서버가 정상적으로 가동 중인지 확인하는 헬스 체크 API입니다.
    일타 강사 정성남 모드가 활성화되었음을 알립니다.
    """
    logger.debug("Health check API 호출됨.") # 헬스 체크 API 호출 로그 기록 (디버그 레벨)
    return {
        "status": "online", # 서버 상태 정보
        "message": "Jarvis Neo-Genesis V3가 정상 작동 중입니다.", # 환영 메시지
        "persona": "30년 경력 일타 강사 정성남 모드 활성화", # 활성화된 페르소나 정보
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat() # 현재 UTC 시간 타임스탬프 추가
    }