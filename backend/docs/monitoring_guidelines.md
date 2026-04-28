# 모니터링 및 로깅 가이드라인

Jarvis Neo-Genesis V3의 운영 환경에서 시스템의 상태와 성능을 효과적으로 모니터링하고, 발생 가능한 문제를 신속하게 파악하기 위한 가이드라인입니다.

## 1. 로깅 전략

현재 시스템은 `backend/app/core/logging_config.py`를 통해 로깅을 설정하고 있습니다. 주요 특징은 다음과 같습니다:

*   **콘솔 출력:** 개발 중 실시간 확인을 위해 모든 INFO 레벨 이상의 로그가 콘솔에 출력됩니다.
*   **일반 파일 로그:** `logs/app.log` 파일에 모든 INFO 레벨 이상의 로그가 기록됩니다. 파일 크기는 1MB로 제한되며, 최대 5개의 백업 파일이 생성됩니다.
*   **구조화된 에러 로그:** `logs/error.log` 파일에 ERROR 레벨 이상의 로그가 **JSON 형식**으로 기록됩니다. 이는 중앙 집중식 로그 관리 시스템(예: ELK Stack)에서 파싱 및 분석하기 용이합니다.

### 1.1 구조화된 로깅 활용 예시

서비스 코드 내에서 중요한 에러나 특정 이벤트 발생 시 JSON 로거를 직접 활용할 수 있습니다.

```python
import logging

logger = logging.getLogger(__name__)

async def process_data(data_id: str):
    try:
        # ... 데이터 처리 로직 ...
        logger.info("Data processed successfully", extra={"data_id": data_id, "status": "success"})
    except Exception as e:
        logger.error("Failed to process data", extra={"data_id": data_id, "error_message": str(e)})
```

`extra` 인자를 사용하여 추가적인 컨텍스트 정보를 JSON 로그에 포함시킬 수 있습니다.

## 2. 모니터링 시스템 구축 (권장)

장기적인 운영 및 성능 최적화를 위해 다음과 같은 모니터링 시스템 도입을 권장합니다.

### 2.1 메트릭 수집 및 시각화 (Prometheus & Grafana)

*   **Prometheus:** FastAPI 애플리케이션에 Prometheus 클라이언트 라이브러리(`prometheus_client`)를 연동하여 API 응답 시간, 요청 수, 에러율, CPU/메모리 사용량 등의 메트릭을 노출시킵니다.
*   **Grafana:** Prometheus에서 수집된 메트릭을 시각화하여 대시보드를 구축합니다. 이를 통해 시스템의 전반적인 상태를 한눈에 파악하고, 성능 병목 현상을 식별할 수 있습니다.

### 2.2 분산 트레이싱 (OpenTelemetry)

*   **OpenTelemetry:** 마이크로서비스 아키텍처나 복잡한 시스템에서 요청이 여러 컴포넌트(FastAPI, Celery, DB, 외부 API)를 거쳐가는 과정을 추적하고, 각 단계에서의 지연 시간을 측정하는 데 사용됩니다. 이를 통해 분산 시스템의 병목 현상을 정확하게 파악할 수 있습니다.

### 2.3 중앙 집중식 로그 관리 (ELK Stack / Grafana Loki)

*   **ELK Stack (Elasticsearch, Logstash, Kibana):** 구조화된 JSON 로그를 Elasticsearch에 저장하고, Logstash로 로그를 수집/파싱하며, Kibana로 로그를 검색, 분석, 시각화합니다. 대규모 로그를 효율적으로 관리하고 문제를 디버깅하는 데 필수적입니다.
*   **Grafana Loki:** Prometheus와 유사한 방식으로 로그를 수집하고 Grafana에서 시각화할 수 있는 경량 로그 수집 시스템입니다. 작은 규모의 시스템에 더 적합할 수 있습니다.

## 3. 알림 시스템

모니터링 시스템과 연동하여 특정 임계값 초과 또는 에러 발생 시 개발팀에 자동으로 알림을 전송하는 시스템을 구축합니다 (예: Slack, PagerDuty 연동).

---