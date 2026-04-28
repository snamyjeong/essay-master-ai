# API 버전 관리 전략

Jarvis Neo-Genesis V3의 API는 지속적으로 발전하고 확장될 것입니다. 새로운 기능 추가, 기존 기능 변경, 또는 데이터 모델 수정이 발생할 경우, 하위 호환성을 유지하면서 점진적인 API 업데이트를 제공하기 위한 명확한 버전 관리 전략이 필요합니다.

## 1. 현재 API 버전

현재 API는 `/api/v1` 프리픽스를 사용하여 버전이 명시되어 있습니다.

*   **예시:** `GET /api/v1/users/me`

## 2. 권장하는 버전 관리 방식: URI 버전 관리 (Path Versioning)

FastAPI는 `APIRouter`를 사용하여 URI 기반의 버전 관리를 매우 효과적으로 지원합니다. 이는 클라이언트가 요청하는 API 엔드포인트 자체에 버전 정보를 포함시키는 방식입니다.

### 2.1 URI 버전 관리의 장점

*   **명확성:** API 엔드포인트만 봐도 어떤 버전의 API를 사용하고 있는지 명확하게 알 수 있습니다.
*   **간단함:** HTTP 헤더 조작 없이 표준 URI 스키마를 따르므로 클라이언트 구현이 간단합니다.
*   **프록시/캐시 친화적:** 각 버전이 고유한 URI를 가지므로 프록시 서버나 CDN 캐싱에 유리합니다.
*   **FastAPI 통합 용이:** FastAPI의 `APIRouter`를 통해 각 버전별 라우터를 쉽게 분리하고 관리할 수 있습니다.

### 2.2 버전 업그레이드 전략

새로운 API 버전 (`v2`, `v3` 등)을 도입해야 할 경우 다음과 같은 절차를 따릅니다.

1.  **새로운 라우터 모듈 생성:** `backend/app/api/v2/`와 같은 새로운 디렉토리를 생성하고, 해당 버전의 엔드포인트와 비즈니스 로직을 구현합니다.
2.  **`main.py`에 새로운 라우터 등록:** `backend/app/main.py` 파일에서 `app.include_router(api_router_v2, prefix="/api/v2")`와 같이 새로운 버전의 라우터를 등록합니다.
3.  **점진적 마이그레이션:**
    *   `v1` API는 즉시 제거하지 않고, `v2`가 안정화될 때까지 함께 운영합니다.
    *   클라이언트에게 `v2` API로의 마이그레이션을 안내하고 충분한 전환 기간을 제공합니다.
    *   `v1` API의 사용률이 현저히 낮아지면, Deprecated 메시지를 추가하고 최종적으로 제거를 고려합니다.
4.  **문서화:** 새로운 API 버전의 변경 사항, 추가된 기능, 제거된 기능 등을 상세히 문서화합니다.

### 2.3 버전 관리 예시 (FastAPI)

```python
# backend/app/api/v1/endpoints/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/me")
async def read_current_user_v1():
    return {"message": "Current user info (v1)"}

# backend/app/api/v2/endpoints/users.py (새로 생성)
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/me")
async def read_current_user_v2():
    # v2에서는 응답 데이터 형식이 변경될 수 있습니다.
    return {"id": 1, "username": "testuser", "version": "v2"}

# backend/app/main.py
from fastapi import FastAPI
from app.api.v1.endpoints import users as users_v1
from app.api.v2.endpoints import users as users_v2 # v2 라우터 임포트

app = FastAPI()

app.include_router(users_v1.router, prefix="/api/v1", tags=["v1-users"])
app.include_router(users_v2.router, prefix="/api/v2", tags=["v2-users"]) # v2 라우터 등록
```

이 전략은 API의 진화를 투명하게 관리하고, 클라이언트의 유연한 전환을 지원하는 데 도움이 됩니다.

---