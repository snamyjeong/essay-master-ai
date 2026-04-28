from celery import Celery

# Celery 애플리케이션 인스턴스 생성
# broker: Celery가 메시지를 주고받는 데 사용할 메시지 브로커 URL (Redis 사용)
# backend: Celery가 작업 결과를 저장할 백엔드 URL (Redis 사용)
celery_app = Celery(
    "essay-master-ai", # Celery 애플리케이션의 이름
    broker="redis://localhost:6379/0", # Redis 브로커 URL
    backend="redis://localhost:6379/0" # Redis 백엔드 URL
)

# 작업 모듈을 자동으로 찾기 위한 설정 (예: tasks.py 파일 내의 작업)
# 'backend.app.tasks'는 Celery가 작업을 찾을 모듈의 경로를 지정합니다.
celery_app.autodiscover_tasks(['backend.app.tasks'])
