from backend.app.celery import celery_app # Celery 앱 임포트

@celery_app.task(acks_late=True) # Celery 태스크로 등록, 작업 완료 후 승인
def example_task(word: str) -> str: # 문자열을 받아 동일한 문자열을 반환하는 예시 태스크
    return f"Hello {word}"
