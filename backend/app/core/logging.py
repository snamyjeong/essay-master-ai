import logging
import logging.config
import os

# logging.conf 파일 경로 설정
# 현재 파일 (logging.py)의 상위 디렉토리 (app)에 logging.conf가 있다고 가정
config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logging.conf')

# logging.conf 파일이 존재하는지 확인하고 로드
if os.path.exists(config_file_path):
    logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
    # root 로거를 가져와서 사용
    logger = logging.getLogger(__name__)
    logger.info(f"로깅 시스템 초기화 완료: '{config_file_path}'에서 설정 로드.")
elif os.path.exists('/backend/app/logging.conf'): # Docker 환경을 위한 절대 경로 탐색 추가
    logging.config.fileConfig('/backend/app/logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info(f"로깅 시스템 초기화 완료: '/backend/app/logging.conf'에서 설정 로드 (Docker 환경).")
else:
    # logging.conf 파일이 없을 경우 기본 로깅 설정 (fallback)
    # [수정] 기본 로깅 레벨을 DEBUG로 설정하여 상세 로그가 출력되도록 합니다.
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    logger.warning(f"로깅 설정 파일 '{config_file_path}'을 찾을 수 없습니다. 기본 로깅 설정을 사용합니다.")

# FastAPI 앱에서 로거를 사용할 수 있도록 내보냅니다.
def get_logger(name: str = __name__):
    """
    지정된 이름의 로거 인스턴스를 반환합니다.
    """
    return logging.getLogger(name)

# Uvicorn 로깅 설정 (FastAPI와 함께 Uvicorn을 사용할 때 Uvicorn의 로그도 통합)
# logging.conf에서 Uvicorn 로거를 설정할 수 있으므로, 여기서는 레벨만 설정하거나
# logging.conf가 로드된 후 추가적인 조정을 합니다.
uvicorn_logger = logging.getLogger("uvicorn")
# uvicorn_logger.handlers = [] # logging.conf에서 핸들러가 설정될 것이므로, 제거하지 않습니다.
# [수정] Uvicorn 로거의 레벨을 DEBUG로 설정하여 상세 로그가 출력되도록 합니다.
uvicorn_logger.setLevel(logging.DEBUG)

# Access 로거도 설정 (선택 사항: Uvicorn의 Access 로그를 커스터마이징)
uvicorn_access_logger = logging.getLogger("uvicorn.access")
# uvicorn_access_logger.handlers = [] # logging.conf에서 핸들러가 설정될 것이므로, 제거하지 않습니다.
# [수정] Uvicorn Access 로거의 레벨을 DEBUG로 설정하여 상세 로그가 출력되도록 합니다.
uvicorn_access_logger.setLevel(logging.DEBUG)