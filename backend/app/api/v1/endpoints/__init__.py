# -*- coding: utf-8 -*-
# V1 API 라우터 통합 파일 - 배선 복구 버전

from fastapi import APIRouter # 라우터 통합용 도구입니다.
# 수석님의 프로젝트 구조(endpoints 하위)에서 users를 가져옵니다.
from backend.app.api.v1.endpoints import users

api_router = APIRouter() # 통합 라우터 객체 생성

# [복구] users 라우터를 /users 경로 아래에 등록합니다.
# 이렇게 해야 main.py에서 설정한 /api/v1과 합쳐져 /api/v1/users/me가 정상 작동합니다.
api_router.include_router(users.router, prefix="/users", tags=["users"])