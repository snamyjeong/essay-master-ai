## Jarvis Neo-Genesis V3 (Essay Master AI) 시스템 아키텍처 및 핵심 로직 요약 리포트

### 1. 디렉토리 구조

`essay-master-ai` 프로젝트는 프론트엔드와 백엔드가 명확히 분리된 마이크로서비스 지향 아키텍처를 따르며, 핵심 비즈니스 로직은 `backend/app` 디렉토리 하위에 모듈화되어 있습니다.

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   └── v2/
│   │   ├── core/
│   │   ├── db/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── worker/
│   ├── data/
│   └── docs/
├── frontend_nextjs/
│   ├── app/
│   ├── components/
│   └── lib/
└── frontend-mobile/
    ├── src/
    └── assets/
```

| 디렉토리           | 주요 역할                                                                          |
| :----------------- | :--------------------------------------------------------------------------------- |
| `backend/app/api`  | FastAPI 애플리케이션의 RESTful API 엔드포인트 정의 (버전별 분리: v1, v2)             |
| `backend/app/core` | 공통 설정 (config), 보안 (security), 로깅, 캐싱 등 핵심 유틸리티 및 설정             |
| `backend/app/db`   | 데이터베이스 연결 (database, session), SQLAlchemy 모델 (models), 초기화 스크립트 |
| `backend/app/schemas`| Pydantic 기반 데이터 유효성 검사 및 직렬화/역직렬화 스키마 정의 (DTO)              |
| `backend/app/services`| 비즈니스 로직 구현 (RAG, 퀴즈 생성, 포인트 관리 등)                              |
| `backend/app/worker`| Celery 워커 애플리케이션 및 비동기 작업 정의                                       |
| `backend/data`     | 정적 데이터 파일 (예: corpus.json)                                                |
| `backend/docs`     | 시스템 문서 (모니터링, Celery 관리, API 버전 관리 등)                             |
| `frontend_nextjs`  | Next.js 기반 웹 프론트엔드 애플리케이션                                            |
| `frontend-mobile`  | Expo/React Native 기반 모바일 프론트엔드 애플리케이션                              |

### 2. 데이터베이스 모델링 (`backend/app/db/models.py`)

SQLAlchemy ORM을 사용하여 정의된 핵심 데이터 모델은 다음과 같습니다. 데이터베이스는 SQLite 기반이며, 비동기 처리를 위해 `sqlite+aiosqlite` 드라이버를 사용합니다.

| 모델명           | 역할                                                                            | 주요 필드 및 관계                                                                                              |
| :--------------- | :------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------- |
| `User`           | 사용자 계정 및 멤버십 정보, 포인트 잔액 관리                                    | `id`, `username`, `email` (Unique), `hashed_password`, `is_superuser`, `membership_type`, `point_balance` <br> `documents`, `quiz_results`, `typing_records` (One-to-Many) |
| `Document`       | 사용자가 업로드한 원본 문서 (PDF, 텍스트) 정보 및 ChromaDB 연동                 | `id`, `user_id` (FK to User), `title`, `content`, `chroma_collection_name` (Unique) <br> `owner` (Many-to-One)                                  |
| `Essay`          | AI가 생성한 에세이 (또는 학습 자료) 정보                                          | `id`, `title`, `content`, `created_at` <br> `generations` (One-to-Many)                                        |
| `GenerationResult`| AI가 생성한 퀴즈, 멘토링, 평가 결과 등                                          | `id`, `essay_id` (FK to Essay), `result_type`, `feedback`, `score` <br> `essay` (Many-to-One)                  |
| `QuizResult`     | 사용자의 퀴즈 풀이 결과 기록                                                    | `id`, `user_id` (FK to User), `document_id` (FK to Document), `quiz_type`, `question_text`, `user_answer`, `correct_answer`, `score` <br> `owner`, `document` (Many-to-One) |
| `TypingRecord`   | 사용자의 타자 연습 기록 (WPM, 정확도 등)                                        | `id`, `user_id` (FK to User), `document_id` (FK to Document), `sentence_content`, `user_input`, `wpm`, `accuracy`, `difficulty` <br> `owner`, `document` (Many-to-One) |

### 3. 코어 및 보안 설정 (`backend/app/core/config.py`, `security.py`)

시스템의 핵심 동작 방식과 보안 메커니즘은 `core` 모듈에 정의됩니다.

*   **`config.py`**:
    *   `API_V1_STR`: `/api/v1`과 같은 API 버전 접두사 정의.
    *   `DATABASE_URL`: 데이터베이스 연결 URL (환경 변수 또는 기본값 사용, `sqlite+aiosqlite`로 자동 보정).
    *   `REDIS_URL`: Celery 브로커 및 캐싱을 위한 Redis URL.
    *   `GEMINI_API_KEY`: Google Gemini API 키 (환경 변수에서 로드).
    *   `SECRET_KEY`: JWT 토큰 서명에 사용되는 비밀 키.
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_MINUTES`: JWT 토큰의 만료 시간 설정.
    *   `CORS_ORIGINS`: 허용된 CORS 도메인 목록 (`*` 또는 콤마로 구분된 리스트).
*   **`security.py`**:
    *   **비밀번호 해싱**: `passlib.context.CryptContext`를 사용하여 `pbkdf2_sha256` 및 `bcrypt` 스키마로 비밀번호를 안전하게 해싱하고 검증합니다. (72바이트 제한 우회 로직 포함)
    *   **JWT 토큰**: `jose` 라이브러리를 사용하여 `HS256` 알고리즘으로 액세스 토큰 및 리프레시 토큰을 생성하고 디코딩합니다. 토큰 페이로드에는 `sub` (사용자 이름)이 포함됩니다.
    *   `create_access_token`, `create_refresh_token`, `decode_token`, `hash_password`, `verify_password`와 같은 유틸리티 함수를 제공합니다.

### 4. API 엔드포인트 (`backend/app/api/v1/endpoints`)

FastAPI의 `APIRouter`를 사용하여 모듈화된 API 엔드포인트는 다음과 같습니다. 현재 V1 API가 활성화되어 있습니다.

| 엔드포인트 모듈             | 주요 API 라우팅                     | 담당 기능 요약                                                                      |
| :-------------------------- | :---------------------------------- | :---------------------------------------------------------------------------------- |
| `auth.py`                   | `POST /signup`                      | 새 사용자 계정 생성 (이메일, 사용자명, 비밀번호)                                    |
|                             | `POST /login`                       | 사용자 로그인 및 JWT 액세스/리프레시 토큰 발급                                  |
|                             | `POST /refresh`                     | 유효한 리프레시 토큰으로 새 액세스/리프레시 토큰 갱신                               |
| `users.py`                  | `GET /me`                           | 현재 로그인된 사용자 정보 조회                                                  |
| `documents.py`              | `POST /upload`                      | PDF/텍스트 파일 업로드, 파싱, SQL DB 및 ChromaDB에 문서 저장 (RAG 연동)            |
| `learning.py`               | `POST /generate-content`            | 학습 텍스트를 기반으로 퀴즈, 타자 연습 문구, 멘토링 메시지 생성 및 RAG 저장           |
|                             | `POST /upload-pdf`                  | PDF 파일을 업로드하여 텍스트 추출 후 학습 콘텐츠 생성                               |
|                             | `POST /evaluate-essay`              | 사용자의 논술 답안을 RAG 컨텍스트 기반으로 AI가 심층 평가 (JSON 피드백 반환)          |
| `content_generation.py`     | `POST /generate-quiz`               | (레거시) 특정 문서에서 퀴즈를 생성 (QuizGenerationService 내부 로직과 유사)           |
| `tasks.py`                  | `POST /example-task`                | Celery 비동기 워커를 통해 백그라운드 작업 실행 (예시)                               |

### 5. 핵심 비즈니스 로직 (RAG & Celery)

Jarvis Neo-Genesis V3의 핵심은 RAG(Retrieval-Augmented Generation) 시스템과 Celery를 활용한 비동기 작업 처리입니다.

#### 5.1 RAG (Retrieval-Augmented Generation) 시스템

`backend/app/services/rag_system.py`와 `backend/app/services/rag_learning_service.py`가 RAG 시스템을 구성합니다.

*   **`rag_system.py` (`RAGSystem` 싱글톤 클래스)**:
    *   **벡터 DB 관리**: `chromadb.PersistentClient`를 사용하여 로컬 파일 시스템(`chroma_data/`)에 벡터 데이터베이스를 구축하고 관리합니다.
    *   **임베딩**: `GoogleGenerativeAIEmbeddings` (`models/gemini-embedding-2` 모델)를 사용하여 텍스트 데이터를 벡터로 변환합니다.
    *   **LLM 연동**: `ChatGoogleGenerativeAI` (`gemini-2.5-flash` 모델)를 사용하여 콘텐츠 생성 및 평가를 수행합니다.
    *   **문서 적재 (`add_documents`)**: 텍스트 문서와 메타데이터를 받아 ChromaDB 컬렉션에 벡터화하여 저장합니다. 사용자별로 고유한 컬렉션(`user_{user_id}_doc_{document_id}`)을 생성하여 문서 분리를 강화합니다.
    *   **문서 검색 (`query_documents`)**: 주어진 질의 텍스트와 유사한 문서를 벡터 DB에서 검색하여 반환합니다.
    *   **에세이 평가 (`evaluate_essay_async`)**: 사용자의 에세이를 심층 분석하며, 관련 문서를 검색하여 `context`로 활용해 LLM에 전달합니다.

*   **`rag_learning_service.py` (`RAGLearningService` 클래스)**:
    *   `RAGSystem`의 래퍼(Wrapper) 역할을 하며, 사용자 학습 콘텐츠를 RAG 시스템에 통합합니다.
    *   **`save_content`**: 학습 텍스트를 받아 사용자 전용 ChromaDB 컬렉션에 저장합니다.
    *   **`process_pdf`**: 업로드된 PDF 파일을 `PyMuPDF(fitz)`를 사용하여 텍스트로 추출하고, 이 추출된 텍스트를 `save_content`를 통해 RAG 시스템에 저장합니다.
    *   이 서비스는 학습 콘텐츠를 벡터 DB에 저장하여, 이후 AI 퀴즈 생성 및 논술 평가 시 해당 사용자만의 지식 기반으로 답변을 증강할 수 있도록 합니다.

#### 5.2 Celery 워커와 비동기 통신

`backend/app/celery_app.py`, `backend/app/worker/celery_worker.py`, `backend/app/tasks.py`가 Celery 기반 비동기 작업을 담당합니다.

*   **`celery_app.py`**:
    *   Celery 애플리케이션의 메인 설정 파일입니다.
    *   **브로커 및 백엔드**: `settings.REDIS_URL`을 사용하여 Redis를 메시지 브로커(작업 큐)와 결과 백엔드(작업 결과 저장소)로 설정합니다.
    *   **작업 모듈 포함**: `app.tasks.rag_tasks`, `app.tasks.quiz_tasks` 등 Celery 작업이 정의된 모듈들을 명시적으로 포함합니다.
    *   **작업 큐 및 라우팅**: 작업의 중요도와 특성에 따라 `default`, `rag_processing`, `notification`과 같은 다중 큐를 정의하고, 특정 작업을 특정 큐로 라우팅하는 규칙을 설정할 수 있습니다. 예를 들어, RAG 관련 무거운 작업은 `rag_processing` 큐로 보내 백그라운드에서 전담 처리하게 합니다.

*   **`worker/celery_worker.py`**:
    *   Celery 워커 프로세스가 실제로 실행될 때 사용되는 스크립트입니다.
    *   `celery_app` 인스턴스를 생성하고, `example_task`와 같은 실제 비동기 작업 함수를 정의합니다.
    *   워커는 `celery -A backend.app.worker.celery_worker worker --loglevel=info` 명령으로 실행되며, 브로커로부터 작업을 받아 처리합니다.

*   **`tasks.py`**:
    *   Celery 작업을 정의하는 모듈입니다. 현재는 간단한 `example_task`만 포함되어 있습니다.
    *   향후 `rag_tasks`나 `quiz_tasks` 모듈에 RAG 기반 문서 처리, 대규모 퀴즈 생성, 복잡한 논술 평가 등 시간이 오래 걸리는 작업을 정의하고 Celery를 통해 비동기로 실행할 예정입니다.

#### 데이터 흐름 요약 (RAG & Celery)

1.  **프론트엔드 요청**: 사용자가 학습 텍스트를 입력하거나 PDF 파일을 업로드합니다.
2.  **FastAPI 엔드포인트**: `backend/app/api/v1/endpoints/learning.py`의 `generate_learning_content` 또는 `upload_pdf` API가 호출됩니다.
3.  **RAG 지식 저장**: `rag_learning_service.save_content` 또는 `process_pdf`를 통해 원본 학습 내용이 추출되고, `rag_system.add_documents`를 호출하여 사용자 전용 ChromaDB 컬렉션에 벡터화되어 저장됩니다. 이 과정에서 `backend/app/db/models.py`의 `Document` 모델에 메타데이터가 기록됩니다.
4.  **LLM 기반 콘텐츠 생성/평가**:
    *   `QuizGenerationService` (or `QuizGenerator`)가 `rag_learning_service` 또는 직접 RAG 시스템을 활용하여 LLM (`gemini-2.5-flash`)에 프롬프트를 보냅니다.
    *   특히 `evaluate_essay_answer_with_rag`와 같은 심층 평가 로직에서는 사용자의 지식 기반(`ChromaDB`)에서 관련 문서를 검색하여 LLM 프롬프트의 `context`로 증강시킨 후 평가를 수행합니다.
5.  **비동기 처리 (Celery)**:
    *   현재는 동기적으로 처리되는 부분이 많지만, 대규모/장시간 소요 작업(예: 대량 문서 학습, 복잡한 리포트 생성)은 `backend/app/api/v1/endpoints/tasks.py`를 통해 `celery_worker.py`의 Celery 워커로 작업을 위임합니다.
    *   Celery 워커는 Redis 브로커를 통해 작업을 수신하고 백그라운드에서 처리하며, 그 결과는 Redis 백엔드에 저장되거나 콜백을 통해 메인 애플리케이션에 전달될 수 있습니다.
6.  **결과 반환**: 생성된 퀴즈, 멘토링, 논술 평가 결과 등은 프론트엔드로 다시 전송됩니다.

이러한 구조를 통해 Jarvis Neo-Genesis V3는 확장 가능한 비동기 처리와 개인화된 RAG 기반 학습 경험을 제공합니다.
