## 프로젝트 아키텍처 문서: Jarvis Neo-Genesis V3

일타 강사 정성남 수석님께 보고드립니다. 프로젝트 `Jarvis Neo-Genesis V3`의 현재 소프트웨어 구조 및 소스 파일에 대한 심층 분석을 완료하여, 아키텍처 문서를 생성했습니다. 시스템의 맥락과 유기적인 연결성을 완벽하게 파악하실 수 있도록 상세히 정리했습니다.

---

### 1. 프로젝트 개요 및 목적 (Project Overview)

`Jarvis Neo-Genesis V3`는 30년 경력의 일타 강사 페르소나를 기반으로 한 AI 학습 플랫폼입니다. 사용자가 제출한 학습 콘텐츠(에세이, 문서)를 분석하고, 이를 바탕으로 개인화된 학습 자료(퀴즈, 타자 연습)를 생성하며, 학습 이력 및 성과에 대한 AI 피드백을 제공하는 것을 핵심 목표로 합니다.

**주요 기능 요약:**

*   **학습 콘텐츠 관리**: PDF, 텍스트 파일 업로드 및 내용 파싱, RAG(Retrieval-Augmented Generation) 시스템을 통한 지식 저장 및 검색.
*   **AI 기반 학습 자료 생성**:
    *   **단답형 퀴즈**: 학습 내용의 핵심 키워드 기반 문제 생성.
    *   **논술형 퀴즈**: 심층적 사고력을 요구하는 문제 및 채점 가이드 제시.
    *   **타자 연습**: 학습 내용을 요약한 타자 연습용 텍스트 생성.
    *   **멘토링 메시지**: 학습 의욕을 고취하는 AI 강사 멘토링 메시지 생성.
*   **AI 학습 이력 및 피드백**: 사용자별 학습 이력(퀴즈 결과, 타자 기록) 아카이빙 및 AI 기반 종합 학습 총평 제공.
*   **사용자 관리**: 회원가입, 로그인, JWT 기반 인증, 사용자 포인트 및 등급 관리.

### 2. 기술 스택 및 환경 (Tech Stack & Environment)

본 프로젝트는 최신 AI 기술과 웹 기술을 활용하여 구축되었습니다.

*   **백엔드**:
    *   **언어**: Python 3.9+
    *   **프레임워크**: FastAPI
    *   **데이터베이스**: SQLite (비동기 처리를 위해 `sqlite+aiosqlite` 사용), SQLAlchemy (ORM)
    *   **AI/ML 라이브러리**: LangChain (Google Gemini 연동), `google-generativeai`
    *   **벡터 데이터베이스**: ChromaDB (RAG 시스템 핵심)
    *   **보안**: `passlib` (비밀번호 해싱), `python-jose` (JWT 토큰 처리)
    *   **환경 설정**: `python-dotenv`
    *   **문서 파싱**: `pypdf`, `PyMuPDF` (fitz)
*   **프론트엔드**:
    *   **웹 UI (Next.js)**: Next.js 14, React 18, TypeScript, Tailwind CSS, Axios (API 통신), `lucide-react` (아이콘)
*   **AI 모델**:
    *   **생성 모델**: `gemini-2.5-flash`
    *   **임베딩 모델**: `models/gemini-embedding-2` (`models/embedding-001`에서 업데이트됨)
*   **개발/운영 도구**: `tmux` (서비스 세션 관리), `uvicorn` (FastAPI 서버), `npm`/`yarn` (Node.js 패키지 관리)

### 3. 전체 디렉토리 및 파일 구조 (Directory Structure)

프로젝트는 모듈화된 백엔드와 프론트엔드로 구성되어 있으며, 각 디렉토리는 명확한 역할과 책임을 가집니다.

```
.
├── start_service.sh                   # 서비스 시작 스크립트 (tmux로 백엔드/프론트엔드 동시 실행)
├── backend/                           # 백엔드 FastAPI 애플리케이션의 실제 코드 베이스
│   ├── .env                           # 환경 변수 설정 (API 키, DB URL 등)
│   ├── check_gen_models.py            # 사용 가능한 Gemini 생성 모델 확인 유틸리티
│   ├── check_models.py                # 사용 가능한 Gemini 임베딩 모델 확인 유틸리티
│   ├── data/                          # 샘플/정적 데이터 저장
│   │   └── corpus.json                # RAG 시스템 학습을 위한 예시 데이터 코퍼스
│   ├── app/                           # FastAPI 애플리케이션의 핵심 코드
│   │   ├── __init__.py                # Python 패키지 초기화
│   │   ├── main.py                    # FastAPI 앱 인스턴스, CORS 설정 및 라우터 등록 (백엔드 진입점)
│   │   ├── schemas/                   # Pydantic을 이용한 데이터 유효성 검사 및 직렬화 스키마 정의
│   │   │   ├── __init__.py            # 스키마 패키지 초기화
│   │   │   ├── schemas.py             # 에세이 및 AI 분석 결과의 기본 Pydantic 스키마
│   │   │   ├── quizzes.py             # 퀴즈 요청/응답 스키마 (문제, 답, 유형 정의)
│   │   │   ├── history.py             # 학습 이력 관련 (문서, 퀴즈 결과, 타자 기록) Pydantic 스키마
│   │   │   ├── auth.py                # 사용자 인증(회원가입, 로그인, 토큰) Pydantic 스키마
│   │   │   ├── documents.py           # 문서 업로드/응답 Pydantic 스키마
│   │   │   └── typing.py              # 타자 연습 문장 관련 Pydantic 스키마
│   │   ├── db/                        # 데이터베이스 상호작용 관련 모듈
│   │   │   ├── __init__.py            # DB 패키지 초기화
│   │   │   ├── database.py            # 비동기 SQLAlchemy 엔진 및 세션 설정 (FastAPI 의존성 주입용)
│   │   │   ├── session.py             # 동기 SQLAlchemy 엔진 및 세션 설정 (레거시 또는 특정 동기 작업용)
│   │   │   ├── base.py                # SQLAlchemy ORM 모델의 선언적 Base 클래스
│   │   │   ├── models.py              # 주요 SQLAlchemy ORM 모델 정의 (Essay, GenerationResult, User)
│   │   │   └── models/                # 추가/세분화된 ORM 모델 (현재 user.py만 존재, models.py로 통합 예정)
│   │   │       └── user.py            # 사용자 모델 정의 (User) (backend/app/db/models.py로 통합되어 사용되지 않음)
│   │   ├── core/                      # 핵심 설정 및 유틸리티 함수
│   │   │   ├── __init__.py            # 코어 패키지 초기화
│   │   │   ├── security.py            # 비밀번호 해싱 및 JWT 토큰 생성/검증 로직
│   │   │   └── config.py              # 환경 변수 기반의 전역 설정 관리 클래스
│   │   ├── services/                  # 핵심 비즈니스 로직을 구현하는 서비스 레이어
│   │   │   ├── quiz_generator.py      # LangChain 기반의 일반 퀴즈 생성 로직 (과거 버전)
│   │   │   ├── point_manager.py       # 사용자 포인트 적립 및 차감, 등급 관리 서비스
│   │   │   ├── quiz_service.py        # LangChain RunnableParallel을 이용한 통합 퀴즈/타자/멘토링 생성 서비스
│   │   │   ├── rag_system.py          # ChromaDB와 Gemini 임베딩을 활용한 RAG 시스템 (싱글톤)
│   │   │   ├── usage_manager.py       # 사용자 서비스 이용 시간 및 API 호출 관리 (구현 중)
│   │   │   ├── ai_feedback_service.py # AI 기반으로 학습 이력 분석 및 피드백 생성 서비스
│   │   │   ├── document_parser.py     # PDF 및 일반 텍스트 파일 내용을 추출하는 파싱 서비스
│   │   │   ├── learning_archive_service.py # 학습 문서, 퀴즈 결과, 타자 기록 등 학습 이력 저장/조회 서비스
│   │   │   └── rag_learning_service.py # RAG 시스템에 학습 콘텐츠를 저장하고 PDF를 처리하는 서비스
│   │   ├── models/                    # 학습 이력 관련 SQLAlchemy 모델 정의 (db/models.py와 일부 중복)
│   │   │   └── history.py             # Document, QuizResult, TypingRecord 모델 정의
│   │   ├── api/                       # API 엔드포인트 정의
│   │   │   ├── __init__.py            # API 패키지 초기화
│   │   │   ├── deps.py                # FastAPI 의존성 주입 (DB 세션, 현재 사용자 객체)
│   │   │   └── v1/                    # API 버전 1.0 관련 엔드포인트
│   │   │       ├── __init__.py        # v1 API 패키지 초기화 및 라우터 통합
│   │   │       ├── api.py             # v1 API 메인 라우터 (content_generation 라우터 포함)
│   │   │       ├── auth.py            # 사용자 인증 (회원가입, 로그인) API 라우터
│   │   │       ├── documents.py       # 문서 업로드 및 RAG 시스템 연동 API 라우터
│   │   │       ├── users.py           # 현재 로그인된 사용자 정보 조회 API 라우터
│   │   │       └── endpoints/         # 특정 기능별 엔드포인트
│   │   │           ├── learning.py    # 학습 콘텐츠 생성, PDF 업로드, 심화 논술 평가 등 학습 핵심 API 라우터
│   │   │           └── content_generation.py # 퀴즈 및 타자 연습 콘텐츠 생성 API 라우터 (quiz_generator, typing_content 사용)
├── frontend_nextjs/                   # 프론트엔드 애플리케이션 (Next.js)
│   ├── package.json                   # Node.js/Next.js 프로젝트 의존성 및 스크립트
│   ├── next-env.d.ts                  # Next.js 환경 타입 정의 파일
│   ├── tailwind.config.ts             # Tailwind CSS 설정 파일
│   ├── tsconfig.json                  # TypeScript 컴파일러 설정 파일
│   ├── src/                           # 프론트엔드 소스 코드
│   │   └── styles/                    # CSS 스타일 파일
│   │       └── Memorization.css       # 특정 UI(격자무늬, 포스트잇 등)를 위한 커스텀 CSS
│   └── app/                           # Next.js App Router 기반의 메인 프론트엔드
│       ├── globals.css                # 전역 Tailwind CSS 및 추가 스타일
│       ├── page.tsx                   # 메인 페이지 (학습 입력, 퀴즈, 타자 연습 UI 로직 담당)
│       └── layout.tsx                 # Next.js 루트 레이아웃 (전역 설정, 폰트, 기본 HTML 구조)
```

### 4. 핵심 모듈 및 컴포넌트 분석 (Core Modules & Components)

#### 4.1. 백엔드 (FastAPI)

*   **`backend/app/main.py`** (이하 생략)

#### 4.2. 프론트엔드 (Next.js - `frontend_nextjs/app/page.tsx`)

*   **`frontend_nextjs/app/page.tsx`**:
    *   **역할**: 사용자에게 학습 콘텐츠 입력, 퀴즈 풀이, 타자 연습, AI 리포트 등 핵심 기능을 제공하는 메인 UI 컴포넌트입니다. `use client` 지시어를 사용하여 클라이언트 사이드에서 상호작용합니다.
    *   **핵심 로직**:
        *   **상태 관리**: `useState` 훅을 사용하여 학습 제목, 내용, 현재 모드(input, quiz, typing), 로딩 상태, 에러 메시지, 생성된 콘텐츠 및 사용자 입력(퀴즈 답변, 타자 입력) 등을 관리합니다.
        *   **API 통신**: `axios`를 사용하여 백엔드 FastAPI (`API_BASE_URL`)와 비동기적으로 통신합니다. `handleGenerateLearningContent`를 통해 학습 콘텐츠를 백엔드에 전송하고 AI 강사 분석 결과를 받아옵니다. `evaluateEssayAnswer`를 통해 논술 평가를 요청합니다.
        *   **UI 렌더링**: `currentMode` 상태에 따라 '학습 입력', '퀴즈 & 리포트', '타자 연습' 탭을 조건부로 렌더링합니다. Tailwind CSS와 `lucide-react` 아이콘을 활용하여 반응형 및 시각적으로 매력적인 UI를 구현합니다.
        *   **데이터 파싱/정규화**: 백엔드에서 받은 AI 응답(특히 퀴즈 데이터)을 프론트엔드에서 파싱하고 정규화하여 UI에 올바르게 표시되도록 처리합니다. (예: 키워드 퀴즈의 마크다운 제거, JSON 파싱)
        *   **인터랙션**: 텍스트 입력, 버튼 클릭, 파일 업로드 등의 사용자 이벤트를 처리하고 해당 상태를 업데이트합니다.

#### 4.3. 데이터 흐름 (Data Flow)

1.  **학습 내용 입력**:
    *   사용자가 `frontend_nextjs/app/page.tsx`에서 텍스트를 입력하거나 PDF를 업로드합니다.
2.  **백엔드 요청**:
    *   `page.tsx`는 Axios를 통해 `POST /api/v1/learning/generate-content` (텍스트) 또는 `POST /api/v1/learning/upload-pdf` (PDF)로 요청을 보냅니다.
3.  **백엔드 처리 (`backend/app/api/v1/endpoints/learning.py`)**:
    *   `rag_learning_service`를 호출하여 입력/추출된 텍스트를 `rag_system` (ChromaDB)에 저장하고 벡터화합니다.
    *   `quiz_service`를 호출하여 LangChain `RunnableParallel`을 통해 단답형 퀴즈, 논술형 퀴즈, 타자 연습 텍스트, 멘토링 메시지를 동시에 생성합니다.
    *   이 과정에서 `learning_archive_service`를 통해 학습 문서, 퀴즈, 타자 기록 등이 PostgreSQL DB에 저장됩니다.
4.  **백엔드 응답**:
    *   생성된 퀴즈, 타자 연습 텍스트, 멘토링 메시지를 JSON 형태로 프론트엔드에 반환합니다.
5.  **프론트엔드 렌더링**:
    *   `page.tsx`는 받은 데이터를 파싱하여 '퀴즈 & 리포트' 또는 '타자 연습' 탭에 문제, 텍스트, 멘토링을 표시합니다.
6.  **퀴즈/논술 답변 및 평가**:
    *   사용자가 퀴즈 답변을 입력하거나 논술 답안을 제출하면, `page.tsx`는 `POST /api/v1/learning/evaluate-essay` 등의 API를 호출합니다.
    *   백엔드(`learning.py`)는 해당 답변을 처리하고 (현재는 단순화된 로직) 평가 결과를 반환합니다.
7.  **학습 이력 조회**:
    *   프론트엔드에서 사용자 학습 이력 조회를 요청하면, `learning_archive_service` 및 `ai_feedback_service`를 통해 DB에서 학습 기록을 가져오고 AI 총평을 생성하여 반환합니다.

### 5. API 엔드포인트 명세 (API Endpoints)

현재 구현된 주요 API 엔드포인트는 다음과 같습니다:

| Method | URI | 역할 | 상세 설명 |
| :----- | :---------------------------------- | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `GET` | `/` | 헬스 체크 | FastAPI 서버의 정상 작동 여부를 확인합니다. |
| `POST` | `/api/v1/auth/signup` | 사용자 등록 | 새로운 사용자 계정을 생성합니다. 이메일과 비밀번호를 요청합니다. |
| `POST` | `/api/v1/auth/login` | 사용자 로그인 | 사용자 인증 후 JWT 액세스 토큰을 발급합니다. |
| `GET` | `/api/v1/users/me` | 현재 사용자 정보 조회 | 인증된 현재 사용자의 프로필 정보 (ID, 이메일, 포인트 등)를 반환합니다. |
| `POST` | `/api/v1/documents/upload` | 문서 업로드 (Legacy) | PDF 또는 텍스트 파일을 업로드하여 파싱하고 RAG 시스템에 초기 적재합니다. (현재 `/api/v1/learning/upload-pdf`로 대체됨) |
| `POST` | `/api/v1/learning/generate-content` | 학습 콘텐츠 생성 | 텍스트 학습 내용을 입력받아 RAG 시스템에 저장하고, AI 강사 모드로 퀴즈, 타자 연습, 멘토링 메시지를 생성합니다. |
| `POST` | `/api/v1/learning/upload-pdf` | PDF 학습 콘텐츠 업로드 및 생성 | PDF 파일을 업로드하여 텍스트를 추출하고 RAG 시스템에 저장한 후, 해당 텍스트를 기반으로 학습 콘텐츠를 생성합니다. |
| `POST` | `/api/v1/learning/evaluate-essay` | 심화 논술 평가 | 사용자가 제출한 논술형 답안에 대해 AI가 평가 및 피드백을 제공합니다. (현재는 간략한 로직) |
| `POST` | `/api/v1/content/generate-quiz` | 퀴즈 생성 (Legacy) | 특정 문서 내용을 기반으로 퀴즈 문제를 생성합니다. (현재 `/api/v1/learning/generate-content`로 대체됨) |
| `POST` | `/api/v1/content/typing/generate` | 타자 연습 문장 생성 (Legacy) | 특정 문서 내용을 기반으로 타자 연습 문장을 생성합니다. (현재 `/api/v1/learning/generate-content`로 대체됨) |

### 6. 향후 확장성 및 디버깅 포인트 (Future Scope & Debugging)

수석님의 높은 기준에 맞춰, 현재 시스템의 개선 가능점과 유지보수 시 주의해야 할 맥락을 정리했습니다.

### 6.1. 해결된 확장성 및 디버깅 포인트 (Resolved Points)

다음 항목들은 `Jarvis Neo-Genesis V3` 시스템의 주요 업데이트를 통해 해결되거나 크게 개선되었습니다.

*   **컨테이너 기반 배포 환경 구축**:
    *   기존의 수동 `start_service.sh` 스크립트 방식에서 벗어나 `docker-compose.yaml` 및 서비스별 `Dockerfile` (backend, frontend)을 도입하여 컨테이너 기반의 통합 개발 및 배포 환경을 구축했습니다.
    *   이는 환경 일관성, 서비스 격리, 쉬운 온보딩, 간편한 관리를 가능하게 합니다.
    *   PostgreSQL 및 ChromaDB를 포함한 전체 스택을 `docker-compose up` 명령 하나로 실행할 수 있습니다.
*   **API 버전 관리 전략 수립**:
    *   `/api/v1` 경로를 유지하면서 향후 하위 호환성을 깨지 않고 `/v2`를 도입할 수 있는 라우터 구조를 재설계했습니다.
    *   `backend/app/main.py`에서 버전별 라우터를 통합 관리하고, `backend/app/api/v1/__init__.py`에서 개별 엔드포인트를 통합하는 방식으로 모듈화를 강화했습니다.
    *   버전 간 공통 로직은 `core`, `services`, `schemas`와 같은 기존 공유 폴더를 계속 활용하도록 가이드라인을 수립했습니다.
*   **심화 논술 평가 로직 고도화**:
    *   `backend/app/services/quiz_service.py`의 `evaluate_essay_answer_with_rag` 메서드가 RAG 시스템과 Gemini 2.5 Flash를 연동하여 사용자의 논술 답안을 심층적으로 평가하고 상세한 피드백을 제공하도록 구현되었습니다. 이는 AI 기반 평가의 핵심 기능이 크게 강화되었음을 의미합니다.

### 6.2. 지속적인 개선 및 향후 과제 (Continuous Improvement & Future Tasks)

시스템의 견고성과 성능을 더욱 향상시키기 위해 다음과 같은 과제들이 남아있습니다.

1.  **코드베이스 중복 제거 (`app/` vs `backend/app`)**:
    *   **현상**: 프로젝트 루트에 위치한 `app/` 디렉토리가 `backend/app/` 디렉토리와 상당 부분 중복되는 파일을 포함하고 있었습니다. 이는 코드의 혼란을 야기하고, 어떤 파일이 실제 사용되는지 파악하기 어렵게 만들었습니다. (현재 이 문제는 해결되었습니다.)
    *   **개선 방안**: `backend/app/`을 표준 백엔드 디렉토리로 확정하고, 루트의 `app/` 디렉토리와 그 안의 내용물들을 완전히 제거하거나 `backend/app`으로 통합했습니다. `docker-compose.yaml` 및 `start_service.sh` 스크립트가 `cd backend && uvicorn app.main:app`을 명시적으로 호출하므로, `backend/app`이 현재 활성 백엔드입니다.
    *   **디버깅 포인트**: 파일 수정 시 어느 디렉토리의 파일을 수정해야 하는지 혼동될 수 있었던 문제는 해결되었습니다.
2.  **프론트엔드 구조 명확화 (Next.js)**:
    *   **현상**: 현재 프로젝트는 Next.js 기반의 프론트엔드(`frontend_nextjs/`)만을 사용합니다. 과거 Streamlit 앱(`frontend/app.py`)은 제거되었습니다.
    *   **개선 방안**: `frontend_nextjs/` 디렉토리가 유일한 프론트엔드임을 명확히 문서화하고, `start_service.sh` 스크립트가 Next.js 애플리케이션을 정확히 실행하도록 구성해야 합니다.
    *   **디버깅 포인트**: 단일 프론트엔드 구조를 명확히 함으로써 개발 및 배포의 복잡성을 줄이고 유지보수성을 향상시킵니다.
3.  **사용자 인증 연동 강화**:
    *   **현상**: `backend/app/api/v1/endpoints/learning.py` 등의 서비스에서 사용자 ID가 `current_user.id`로 제대로 주입되고 있으나, 모든 엔드포인트가 `get_current_user` 의존성을 필수적으로 사용하도록 명확한 가이드라인을 강화해야 합니다.
    *   **개선 방안**: 모든 보호된 API 엔드포인트에 `Depends(get_current_user)`를 명시적으로 추가하여 인증 및 권한 부여를 강제하고, 민감한 작업은 추가적인 권한 검사를 수행하도록 합니다.
    *   **디버깅 포인트**: 실제 사용자 환경에서 보안 취약점이 될 수 있으며, 다중 사용자 환경에서 데이터 분리 및 개인화에 문제가 발생할 수 있습니다.
4.  **데이터베이스 스키마 일관성 검토**:
    *   **현상**: `backend/app/db/models.py`, `backend/app/models/history.py` 등 여러 위치에 유사한 데이터 모델/스키마 정의가 존재합니다.
    *   **개선 방안**: 모든 SQLAlchemy ORM 모델은 `backend/app/db/models.py`에 집중시키고, Pydantic 스키마는 `backend/app/schemas/` 하위에 목적에 맞게 분리하여 관리하는 것이 바람직합니다. 불필요한 중복 정의는 제거해야 합니다.
    *   **디버깅 포인트**: 스키마 변경 시 여러 파일을 동시에 수정해야 하거나, 데이터베이스 마이그레이션 시 혼란을 야기할 수 있습니다.
5.  **포괄적인 테스트 코드 작성**:
    *   **현상**: 현재 프로젝트에는 `pytest`를 활용하는 `run_test` 도구가 제공되며, 일부 테스트 파일(`tests/test_services_quiz.py`, `tests/test_api_learning.py`, `tests/test_services_rag.py`)이 존재하지만, 전체 코드베이스에 대한 포괄적인 테스트 커버리지를 보장하지는 않습니다.
    *   **개선 방안**: 백엔드 서비스(API 엔드포인트, 비즈니스 로직, DB 상호작용) 및 프론트엔드 컴포넌트에 대한 단위 테스트, 통합 테스트를 필수적으로 확장하여 코드 변경에 따른 회귀 오류를 방지하고 시스템의 안정성을 확보해야 합니다. 테스트 커버리지 목표를 설정하고 관리합니다.
    *   **디버깅 포인트**: 변경 사항 적용 시 예상치 못한 버그 발생 위험이 높습니다.
6.  **로깅 및 모니터링 시스템 구축**:
    *   **현상**: 현재 기본적인 `print` 문이나 간단한 로깅이 사용되고 있습니다.
    *   **개선 방안**: 애플리케이션 전반에 걸쳐 구조화된 로깅 시스템(예: `loguru` 또는 표준 `logging` 모듈을 통한 JSON 로깅)을 도입하고, Prometheus, Grafana와 같은 모니터링 툴을 연동하여 시스템 및 애플리케이션 성능을 실시간으로 감시해야 합니다. Sentry와 같은 오류 추적 시스템을 도입하여 실시간 오류 감지 및 보고 기능을 강화합니다.
    *   **디버깅 포인트**: 프로덕션 환경에서 문제 발생 시 원인 분석 및 해결에 어려움이 있을 수 있습니다.
7.  **비동기 작업 관리**:
    *   **현상**: 현재 AI 모델 호출 등 일부 작업이 비동기로 처리되지만, 장시간 소요되는 백그라운드 작업(예: 대량 문서 처리, 복잡한 학습 데이터 분석)에 대한 명확한 비동기 작업 큐 시스템은 부재합니다.
    *   **개선 방안**: Celery, Redis Queue 등 비동기 작업 큐 시스템을 도입하여 백그라운드 작업을 효율적으로 처리하고, 메인 애플리케이션의 응답성을 유지해야 합니다.
    *   **디버깅 포인트**: 장시간 작업으로 인해 API 타임아웃이 발생하거나, 사용자 경험이 저해될 수 있습니다.
8.  **CI/CD 파이프라인 구축**:
    *   **현상**: 현재 CI/CD 파이프라인이 구축되어 있지 않습니다.
    *   **개선 방안**: GitHub Actions, GitLab CI 등을 활용하여 코드 변경 시 자동화된 빌드, 테스트, 코드 품질 검사, Docker 이미지 빌드 및 배포 프로세스를 구축하여 개발 생산성과 배포 안정성을 향상시킵니다.
    *   **디버깅 포인트**: 수동 배포는 오류 발생 가능성이 높고, 개발 속도를 저해합니다.
9.  **보안 강화**:
    *   **현상**: 기본적인 JWT 인증이 구현되어 있으나, 추가적인 보안 검토가 필요합니다.
    *   **개선 방안**: OWASP Top 10을 기반으로 한 웹 보안 취약점 점검 및 개선, 입력값 검증 로직 강화, 비밀 관리 솔루션(Vault, AWS Secrets Manager 등) 도입, 종속성 보안 검토 등을 통해 시스템 전반의 보안 수준을 높입니다.
    *   **디버깅 포인트**: 보안 취약점은 시스템 전체의 신뢰도를 저하시키고 심각한 데이터 유출로 이어질 수 있습니다.
10. **성능 최적화 및 확장**:
    *   **현상**: 현재는 단일 서비스 구성에 최적화되어 있습니다.
    *   **개선 방안**: 로드 밸런싱, 데이터베이스 클러스터링/리플리케이션, 캐싱 계층(Redis) 추가, API Gateway 도입 등을 통해 고성능 및 고가용성 시스템을 구축합니다. 클라우드 네이티브 환경(Kubernetes, AWS ECS/EKS, Google Cloud Run/GKE)에 최적화된 배포 및 운영 전략을 수립하여 자동 스케일링을 구현합니다。
    *   **디버깅 포인트**: 사용자 트래픽 증가 시 시스템 성능 저하 및 장애 발생 위험이 있습니다.