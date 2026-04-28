from celery import Celery # Celery 앱을 생성하기 위해 Celery 클래스를 임포트합니다.
from backend.app.core.config import settings # 프로젝트 설정을 로드하기 위해 settings 객체를 임포트합니다.
import logging # 로깅을 위한 logging 모듈을 임포트합니다.

# 로거 설정
logger = logging.getLogger(__name__) # 현재 모듈의 이름을 가진 로거 인스턴스를 생성합니다.
logger.setLevel(logging.INFO) # 로깅 레벨을 INFO로 설정합니다.
handler = logging.StreamHandler() # 콘솔에 로그를 출력하는 핸들러를 생성합니다.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # 로그 메시지 포맷을 정의합니다.
handler.setFormatter(formatter) # 핸들러에 포매터를 설정합니다.
logger.addHandler(handler) # 로거에 핸들러를 추가합니다.

# Celery 앱 인스턴스 생성
# 'backend.app.worker.celery_worker'는 Celery가 태스크를 찾을 모듈 이름입니다.
# broker는 메시지 브로커(Redis)의 URL을 사용합니다.
# backend는 태스크 결과 저장소(Redis)의 URL을 사용합니다.
celery_app = Celery(
    "celery_worker", # Celery 앱의 이름입니다.
    broker=settings.REDIS_URL, # Redis를 브로커로 사용합니다.
    backend=settings.REDIS_URL, # Redis를 백엔드로 사용합니다.
    include=['backend.app.worker.celery_worker'] # Celery가 태스크를 찾아야 할 모듈 목록을 지정합니다.
)

# Celery 설정 업데이트
celery_app.conf.update(
    task_track_started=True, # 태스크가 시작되었을 때 상태를 'STARTED'로 추적합니다.
    task_serializer='json', # 태스크를 직렬화할 때 JSON 형식을 사용합니다.
    result_serializer='json', # 태스크 결과를 직렬화할 때 JSON 형식을 사용합니다.
    accept_content=['json'], # 허용할 콘텐츠 타입을 JSON으로 설정합니다.
    timezone='Asia/Seoul', # 시간대를 서울로 설정합니다.
    enable_utc=False, # UTC 사용을 비활성화합니다.
    worker_prefetch_multiplier=1, # 워커가 한 번에 가져올 태스크의 수를 설정합니다.
    worker_max_tasks_per_child=10, # 각 워커 자식 프로세스가 처리할 최대 태스크 수를 설정합니다.
)

@celery_app.task(acks_late=True, name="example_task") # Celery 태스크로 정의하며, 태스크 이름을 "example_task"로 설정합니다.
def example_task(arg1: int, arg2: int) -> int:
    """
    두 개의 정수를 받아 합을 반환하는 예제 Celery 태스크입니다.
    """
    logger.info(f"Executing example_task with arg1: {arg1}, arg2: {arg2}") # 태스크 실행 정보를 로그로 남깁니다.
    # 여기에 비동기적으로 실행될 실제 로직을 추가합니다.
    import time
    time.sleep(5) # 5초 동안 작업을 시뮬레이션합니다.
    result = arg1 + arg2 # 두 인자를 더하여 결과를 생성합니다.
    logger.info(f"example_task finished. Result: {result}") # 태스크 완료 정보를 로그로 남깁니다.
    return result # 결과를 반환합니다.
