# backend/Dockerfile
# FastAPI 애플리케이션을 위한 Dockerfile입니다.
# '기본에 충실해야 흔들림 없다!'는 일타 강사의 철학처럼, 안정적인 배포 환경을 구축합니다.

# 1. 빌드 스테이지: 파이썬 기반 이미지 사용 (Python 3.9-slim-buster)
FROM python:3.9-slim-buster as builder

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 클라이언트 라이브러리 등)
# apt-get update: 패키지 목록 업데이트
# apt-get install -y --no-install-recommends: 추천 패키지 없이 필수 패키지만 설치
#   build-essential: 컴파일에 필요한 도구들 (psycopg2-binary 빌드용)
#   libpq-dev: PostgreSQL 클라이언트 라이브러리 개발 파일 (psycopg2-binary 의존성)
#   gcc: C 컴파일러
#   python3-dev: 파이썬 개발 헤더 파일 (psycopg2-binary 의존성)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* # 캐시 삭제로 이미지 크기 최적화

# poetry 설치
# pip install poetry: poetry 패키지 관리자 설치
RUN pip install poetry

# 프로젝트 종속성 파일 복사
COPY poetry.lock pyproject.toml ./ 

# poetry를 사용하여 종속성 설치 (가상 환경 비활성화)
# --no-root: 현재 프로젝트를 패키지로 설치하지 않음
# --no-dev: 개발용 종속성 설치 제외
RUN poetry install --no-root --no-dev

# 2. 최종 실행 스테이지: 더 작은 런타임 이미지 사용
FROM python:3.9-slim-buster as runtime

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 클라이언트 런타임 라이브러리)
# libpq5: PostgreSQL 클라이언트 런타임 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn # uvicorn 실행 파일 복사

# 애플리케이션 코드 복사
COPY . /app

# 환경 변수 설정
ENV PYTHONPATH=/app

# 애플리케이션 실행 명령어
# uvicorn app.main:app --host 0.0.0.0 --port 8000
# docker-compose에서 command로 오버라이드될 수 있음
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]