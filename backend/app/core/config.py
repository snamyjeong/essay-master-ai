# -*- coding: utf-8 -*-
# Jarvis 시스템 전역 설정 모듈 - 로그인 성공 당시 안정화 버전

import os # 운영체제 환경 변수 접근을 위해 임포트합니다.
from pathlib import Path # 경로 조작을 위해 Path를 임포트합니다.
from typing import Optional, List # 타입 힌트 지정을 위해 임포트합니다.
from dotenv import load_dotenv # .env 파일 로드를 위해 사용합니다.
from pydantic_settings import BaseSettings # 설정 클래스 정의용입니다.

# [정석] 프로젝트 루트(essay-master-ai)를 절대 경로로 계산합니다.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env") # 루트의 .env 파일을 로드합니다.

class Settings(BaseSettings):
    # 1. API 및 프로젝트 기본 설정
    API_V1_STR: str = "/api/v1" # API 접두어 경로입니다.
    PROJECT_NAME: str = "Jarvis Neo-Genesis V3" # 프로젝트 명칭입니다.
    
    # 2. 데이터베이스 설정 - 절대 경로 고정
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR}/essay_master.db"
    )

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """비동기 처리를 위한 DB 프로토콜 보정"""
        url = self.DATABASE_URL
        if url.startswith("sqlite://") and "+aiosqlite" not in url:
            return url.replace("sqlite://", "sqlite+aiosqlite://")
        return url

    # 3. 필수 서비스 및 보안 설정
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CHROMADB_SERVER_URL: str = os.getenv("CHROMADB_SERVER_URL", "http://localhost:8000")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_jarvis_v3_1978")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1주일
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30일

    # 5. CORS 설정 (에러 13 해결)
    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "*")
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """콤마로 구분된 문자열을 리스트로 변환하여 반환합니다."""
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    class Config:
        case_sensitive = True

settings = Settings() # 전역 설정 객체 생성