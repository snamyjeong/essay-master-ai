# backend/app/api/v2/__init__.py
# v2 API 라우터들을 통합합니다.
from fastapi import APIRouter
from backend.app.api.v2.endpoints import learning, content_generation, auth, documents, users

api_router = APIRouter()
api_router.include_router(learning.router, prefix="/learning", tags=["v2-learning"])
api_router.include_router(content_generation.router, prefix="/content", tags=["v2-content"])
api_router.include_router(auth.router, prefix="/auth", tags=["v2-auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["v2-documents"])
api_router.include_router(users.router, prefix="/users", tags=["v2-users"])
