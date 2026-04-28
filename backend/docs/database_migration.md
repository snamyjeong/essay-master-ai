# 데이터베이스 마이그레이션 (Alembic)

데이터베이스 스키마 변경 이력을 관리하고, 개발/운영 환경 간에 스키마를 동기화하기 위해 Alembic을 사용합니다.

## 1. Alembic 설치

```bash
pip install alembic
```

## 2. Alembic 초기화 (최초 1회만 실행)

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 Alembic 환경을 초기화합니다. 이 명령은 `alembic/` 디렉토리와 `alembic.ini` 파일을 생성합니다.

```bash
alembic init alembic
```

**참고:** 이 프로젝트에서는 이미 `alembic/` 디렉토리와 `alembic.ini`, `alembic/env.py` 파일이 미리 생성되어 있습니다.

## 3. 설정 파일 (`alembic.ini`) 수정

`alembic.ini` 파일에서 데이터베이스 연결 URL과 스크립트 위치 등을 설정합니다.

*   **`sqlalchemy.url`**: Alembic이 데이터베이스에 연결할 URL을 지정합니다. 이 프로젝트에서는 `alembic/env.py`에서 `app.core.config.settings.SQLALCHEMY_DATABASE_URL`을 사용하여 동적으로 설정됩니다.
*   **`script_location`**: Alembic 스크립트가 위치할 디렉토리입니다. `alembic`으로 설정되어 있습니다.

## 4. 환경 스크립트 (`alembic/env.py`) 수정

`alembic/env.py` 파일은 Alembic이 마이그레이션을 실행할 때 데이터베이스 연결 방법, 메타데이터 로드 등을 정의하는 핵심 스크립트입니다.

*   **`target_metadata`**: `backend.app.db.base.Base.metadata`로 설정되어 SQLAlchemy 모델의 메타데이터를 Alembic이 인식하도록 합니다.
*   **`run_migrations_online()`**: `app.core.config.settings.SQLALCHEMY_DATABASE_URL`을 사용하여 동적으로 데이터베이스에 연결하도록 수정되어 있습니다.

## 5. 마이그레이션 스크립트 생성

데이터베이스 모델(`backend/app/db/models.py`)에 변경 사항이 생겼을 때, 다음 명령어를 실행하여 변경 사항을 감지하고 마이그레이션 스크립트를 자동으로 생성합니다.

```bash
alembic revision --autogenerate -m "Add user table"
```

*   `-m "Add user table"`: 생성될 마이그레이션 파일에 대한 설명 메시지입니다.

이 명령어를 실행하면 `alembic/versions/` 디렉토리에 새로운 `.py` 파일이 생성됩니다. 이 파일에는 데이터베이스 스키마 변경 내용(예: 테이블 생성, 컬럼 추가/수정)이 Python 코드로 작성됩니다. **생성된 스크립트를 항상 검토하여 의도한 변경 사항만 포함되어 있는지 확인해야 합니다.**

## 6. 마이그레이션 적용

생성된 마이그레이션 스크립트를 데이터베이스에 적용하려면 다음 명령어를 실행합니다.

```bash
alembic upgrade head
```

*   `head`: 가장 최신 버전의 마이그레이션까지 적용하라는 의미입니다.

## 7. 현재 데이터베이스 버전 확인

```bash
alembic current
```

## 8. 특정 버전으로 롤백 (주의해서 사용)

```bash
alembic downgrade -1 # 이전 버전으로 롤백
alembic downgrade <revision_id> # 특정 revision_id로 롤백
```

---