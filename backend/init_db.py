# -*- coding: utf-8 -*-
# Jarvis DB 초기화 및 관리자 생성 최종 안정화 버전 (v3.5)

import sys
import os

# 1. 프로젝트 루트 경로 강제 인식 (절대 경로)
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rich.console import Console
from rich.table import Table

# [교정] 비동기 엔진(AsyncEngine)은 동기 스크립트와 충돌하므로, 스크립트 전용 동기 엔진을 생성할 도구를 가져옵니다.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.base import Base

# [핵심] 동기식 엔진과 통합 Base 임포트
import backend.app.db.models as models

console = Console()

def get_safe_hash(password: str):
    """Bcrypt의 72바이트 제한을 우회하여 안전하게 해싱합니다."""
    from passlib.context import CryptContext
    # 72바이트 제한이 없는 pbkdf2_sha256를 우선적으로 사용합니다.
    pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def init_database():
    console.print("[bold cyan]🚀 [Jarvis] 인프라 최종 안정화 및 데이터 주입을 시작합니다...[/bold cyan]")

    # [완벽한 분리] .env 파일에 비동기 드라이버(+aiosqlite 등)가 포함되어 있으면 greenlet_spawn 에러가 발생합니다.
    # 따라서 동기 엔진에서 안전하게 사용할 수 있도록 URL 문자열에서 비동기 키워드를 강제로 제거합니다.
    sync_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
    if sync_url.startswith("postgres://"): # 혹시 모를 구형 postgres 접두어도 최신 표준으로 보정합니다.
        sync_url = sync_url.replace("postgres://", "postgresql://")

    # [추가] 현재 어떤 경로로 DB를 생성하려는지 디버깅 로그를 출력합니다.
    console.print(f"[dim]🔍 (디버그) DB 타겟 경로: {sync_url}[/dim]")
    
    # [교정] SQLite 파일이 위치할 상위 폴더가 존재하지 않으면 생성 에러(e3q8)가 발생하므로 강제 생성합니다.
    if "sqlite" in sync_url:
        db_path = sync_url.split("sqlite:///")[-1] # URL에서 실제 파일 경로만 추출합니다.
        target_dir = os.path.dirname(os.path.abspath(db_path)) # 절대 경로 기준 상위 폴더를 찾습니다.
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True) # 폴더가 없다면 안전하게 생성합니다.
            console.print(f"[yellow]💡 누락된 DB 저장 폴더 자동 생성 완료: {target_dir}[/yellow]")

    sync_engine = create_engine(sync_url) # 완전히 정제된 순수 동기식 URL로 엔진을 생성합니다.
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    try:
        # Step 1: 테이블 생성 확인 (동기 방식)
        tables = list(Base.metadata.tables.keys())
        console.print(f"[yellow]1. 인식된 테이블 목록: {tables}[/yellow]")
        
        Base.metadata.create_all(bind=sync_engine)
        console.print("[bold green]✅ 물리적 테이블 생성 및 정합성 확인 완료.[/bold green]")

        # Step 2: 관리자 계정 강제 주입
        with SyncSessionLocal() as db:
            admin_email = "snamy78@gmail.com"
            # 기존 계정 존재 여부 확인
            admin_user = db.query(models.User).filter(models.User.email == admin_email).first()

            if not admin_user:
                console.print(f"[yellow]2. 관리자 계정 생성 시도: {admin_email}[/yellow]")
                
                # [보정] 기존 보안 함수가 에러 나면 안전한 해싱으로 대체
                try:
                    from backend.app.core.security import hash_password
                    hashed_pw = hash_password("jarvis1234")
                except Exception:
                    console.print("[bold red]⚠️ 기존 보안 함수 72바이트 제한 감지. 안전 알고리즘으로 전환합니다.[/bold red]")
                    hashed_pw = get_safe_hash("jarvis1234")

                new_admin = models.User(
                    email=admin_email,
                    username=admin_email, # [교정] 서버 검색 조건에 맞춰 이메일을 username으로 설정
                    hashed_password=hashed_pw,
                    is_active=True,
                    is_superuser=True 
                )
                db.add(new_admin)
                db.commit()
                console.print(f"[bold green]✅ 관리자 주입 최종 성공: {admin_email}[/bold green]")
            else:
                console.print(f"[blue]ℹ️ 관리자 계정이 이미 활성화되어 있습니다.[/blue]")

        # 최종 리포트
        summary = Table(title="Jarvis 인프라 최종 가동 리포트")
        summary.add_column("항목", style="cyan")
        summary.add_column("상태", style="magenta")
        summary.add_row("DB 파일", "/home/snamy78/essay-master-ai/essay_master.db")
        summary.add_row("생성 테이블", str(len(tables)) + " 개")
        summary.add_row("관리자 ID", admin_email)
        console.print(summary)

    except Exception as e:
        console.print(f"[bold red]💥 초기화 중단:[/bold red] {str(e)}")

if __name__ == "__main__":
    init_database()