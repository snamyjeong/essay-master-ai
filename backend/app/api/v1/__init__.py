# backend/app/api/v1/__init__.py
# `backend/app/api/v1` 디렉토리를 Python 패키지로 인식하게 합니다.
# 이 파일에서 v1 API 라우터들을 통합하여 하나의 `api_router`로 묶습니다.

from fastapi import APIRouter # FastAPI의 APIRouter를 임포트합니다.

# v1 버전의 엔드포인트 모듈들을 임포트합니다.
from backend.app.api.v1.endpoints import (
    auth,
    users,
    documents,
    learning,
    content_generation,
    tasks # 비동기 작업(tasks) 라우터 모듈 임포트
)

# 모든 v1 API 라우터들을 포함할 메인 라우터 인스턴스를 생성합니다.
api_router = APIRouter()

# 각 엔드포인트 라우터를 통합 라우터에 포함합니다.
# prefix를 명시하여 /api/v1/learning/... 형태의 계층 구조를 완성합니다.
api_router.include_router(auth.router, prefix="/auth", tags=["v1-auth"]) # /api/v1/auth
api_router.include_router(users.router, prefix="/users", tags=["v1-users"]) # /api/v1/users
api_router.include_router(documents.router, prefix="/documents", tags=["v1-documents"]) # /api/v1/documents
api_router.include_router(learning.router, prefix="/learning", tags=["v1-learning"]) # /api/v1/learning
api_router.include_router(content_generation.router, prefix="/content", tags=["v1-content"]) # /api/v1/content
api_router.include_router(tasks.router, prefix="/tasks", tags=["v1-tasks"]) # /api/v1/tasks