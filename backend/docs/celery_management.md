# Celery 작업 관리 및 확장 가이드라인

Celery는 비동기 작업을 처리하고 백그라운드에서 긴 시간 실행되는 작업을 관리하는 데 사용됩니다. 시스템의 확장성과 안정성을 높이기 위한 Celery 관리 및 확장 전략을 설명합니다.

## 1. Celery 기본 설정

`backend/app/celery_app.py` 파일에서 Celery 애플리케이션이 설정됩니다.

*   **Broker & Backend:** Redis를 메시지 브로커와 결과 백엔드로 사용합니다. (`settings.REDIS_URL`)
*   **Included Tasks:** `app.tasks.rag_tasks`와 `app.tasks.quiz_tasks` 모듈에 정의된 작업들을 포함합니다.

## 2. 다중 작업 큐 (Multiple Queues)

작업의 중요도, 실행 시간, 자원 요구량에 따라 여러 개의 큐를 정의하여 작업을 분리하고 워커를 할당할 수 있습니다. 이는 중요한 작업이 덜 중요한 작업에 의해 블록되는 것을 방지하고, 자원을 효율적으로 사용하게 합니다.

### 2.1 큐 정의 (backend/app/celery_app.py)

`celery_app.conf.task_queues` 설정을 통해 큐를 정의합니다. 예시:

```python
celery_app.conf.task_queues = {
    "default": {"exchange": "default", "binding_key": "default"},
    "rag_processing": {"exchange": "rag_processing", "binding_key": "rag_processing"}, # RAG 문서 처리 큐
    "notification": {"exchange": "notification", "binding_key": "notification"} # 알림 큐
}
```

### 2.2 작업 라우팅 (backend/app/celery_app.py)

`celery_app.conf.task_routes` 설정을 통해 특정 작업을 특정 큐로 라우팅합니다. 예시:

```python
celery_app.conf.task_routes = {
    'app.tasks.rag_tasks.*': {'queue': 'rag_processing'}, # RAG 관련 작업은 rag_processing 큐로
    'app.tasks.quiz_tasks.*': {'queue': 'default'}, # 퀴즈 관련 작업은 default 큐로
}
```

### 2.3 특정 큐의 워커 실행

워커를 실행할 때 `celery -A app.celery_app worker -Q <queue_name>` 옵션을 사용하여 특정 큐의 작업만 처리하도록 지정할 수 있습니다.

```bash
# 모든 큐의 작업을 처리하는 워커 (기본)
celery -A app.celery_app worker --loglevel=info

# 'rag_processing' 큐의 작업만 처리하는 워커
celery -A app.celery_app worker -Q rag_processing --loglevel=info

# 여러 큐의 작업을 처리하는 워커
celery -A app.celery_app worker -Q default,notification --loglevel=info
```

## 3. Celery Beat (주기적인 작업 스케줄링)

Celery Beat는 특정 시간에 주기적으로 실행되어야 하는 작업을 스케줄링하는 데 사용됩니다. 예를 들어, 매일 자정에 통계를 생성하거나, 1시간마다 캐시를 갱신하는 등의 작업을 정의할 수 있습니다.

### 3.1 Beat 설정 (backend/app/celery_app.py)

```python
# celery_app.py 에 다음 설정 추가
celery_app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'app.tasks.some_periodic_task', # 실행할 작업 지정
        'schedule': 30.0, # 30초마다 실행
        'args': (16, 16) # 작업에 전달할 인자
    },
    'cleanup-cache-every-hour': {
        'task': 'app.tasks.cache_tasks.cleanup_expired_cache',
        'schedule': crontab(minute=0, hour='*/1'), # 매시 정각에 실행
    },
}
celery_app.conf.timezone = "UTC"
```

### 3.2 Celery Beat 실행

Celery 워커와 별도로 Beat 스케줄러를 실행해야 합니다.

```bash
celery -A app.celery_app beat --loglevel=info
```

## 4. Celery Flower (모니터링 대시보드)

Celery Flower는 Celery 워커와 작업을 실시간으로 모니터링하고 관리할 수 있는 웹 기반 도구입니다.

### 4.1 Flower 설치

```bash
pip install flower
```

### 4.2 Flower 실행

```bash
celery -A app.celery_app flower --port=5555
```

웹 브라우저에서 `http://localhost:5555`에 접속하여 대시보드를 확인할 수 있습니다.

---