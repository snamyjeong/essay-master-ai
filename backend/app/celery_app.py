from celery import Celery # Celery 라이브러리 임포트
from app.core.config import settings # 프로젝트 설정값 임포트

# Celery 애플리케이션 인스턴스를 생성합니다.
# 'main'은 Celery 앱의 이름이며, 일반적으로 모듈 이름과 동일하게 설정합니다.
# 'broker'는 메시지 브로커(Redis)의 URL을 지정합니다. 작업 큐의 통신 채널입니다.
# 'backend'는 작업 결과(성공/실패, 반환 값)를 저장할 백엔드(Redis)의 URL을 지정합니다.
celery_app = Celery(
    "essay_master_ai_celery",
    broker=settings.REDIS_URL, # Redis URL을 브로커로 사용
    backend=settings.REDIS_URL, # Redis URL을 백엔드로 사용
    include=["app.tasks.rag_tasks", "app.tasks.quiz_tasks"] # Celery 작업(task)이 정의된 모듈들을 지정
)

# Celery의 시간대 설정을 UTC로 지정합니다. 이는 분산 시스템에서 시간 일관성을 유지하는 데 중요합니다.
celery_app.conf.timezone = "UTC"

# [추가] Celery 작업 큐 설정 예시
# 작업의 종류나 중요도에 따라 여러 개의 큐를 정의하고, 각 큐에 특정 작업을 라우팅할 수 있습니다.
# 이는 자원 활용의 효율성을 높이고, 중요한 작업이 덜 중요한 작업에 의해 지연되는 것을 방지합니다.
celery_app.conf.task_queues = {
    "default": {
        "exchange": "default",
        "binding_key": "default"
    },
    "rag_processing": {
        "exchange": "rag_processing",
        "binding_key": "rag_processing"
    }, # RAG 문서 처리와 같이 시간이 오래 걸리는 작업을 위한 큐
    "notification": {
        "exchange": "notification",
        "binding_key": "notification"
    } # 사용자 알림과 같이 즉각적인 응답이 필요한 작업을 위한 큐
}

# [추가] 작업 라우팅 설정 예시
# 특정 작업(task)을 특정 큐로 보내도록 라우팅 규칙을 정의합니다.
celery_app.conf.task_routes = {
    'app.tasks.rag_tasks.*': {
        'queue': 'rag_processing'
    }, # rag_tasks 모듈의 모든 작업은 'rag_processing' 큐로 라우팅
    'app.tasks.quiz_tasks.*': {
        'queue': 'default'
    }, # quiz_tasks 모듈의 모든 작업은 'default' 큐로 라우팅 (예시)
    # 'app.tasks.notification_tasks.send_email': {'queue': 'notification'}, # 알림 작업 예시
}


# 작업 직렬화(serialization) 방식을 JSON으로 설정합니다.
# 이는 다양한 언어로 작성된 클라이언트나 워커 간의 데이터 교환을 용이하게 합니다.
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.enable_utc = True

# 작업 결과가 만료되는 시간을 1시간(3600초)으로 설정합니다.
# 너무 오래된 작업 결과는 백엔드에서 자동으로 정리됩니다.
celery_app.conf.result_expires = 3600
