import logging
from logging.handlers import RotatingFileHandler
import os
from pythonjsonlogger import jsonlogger # JSON 로깅을 위한 라이브러리 임포트

# 로그 파일이 저장될 디렉토리 정의. 프로젝트 루트에 'logs' 폴더를 생성합니다.
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True) # 디렉토리가 없으면 생성합니다.

# 기본 로그 파일 경로
LOG_FILE = os.path.join(LOG_DIR, "app.log")
# 에러 로그 파일 경로 (구조화된 로깅 예시를 위해 분리)
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")

def setup_logging():
    """
    애플리케이션의 로깅 설정을 초기화합니다.
    모든 로그는 콘솔과 파일로 출력되며, 파일 로그는 크기 기반으로 로테이션됩니다.
    에러 로그는 JSON 형식으로 구조화되어 별도 파일에 저장됩니다.
    """
    # 루트 로거 설정 (기본 모든 로그를 처리)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # INFO 레벨 이상의 로그를 처리

    # 기존 핸들러 제거 (중복 로깅 방지)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 1. 콘솔 핸들러 설정 (개발 환경에서 실시간 로그 확인용)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(levelname)s:     %(asctime)s - %(name)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 2. 파일 핸들러 설정 (모든 로그를 JSON 형식으로 파일에 저장, 1MB 도달 시 5개 파일까지 로테이션)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
    )
    # [수정] 일반 파일 로그도 JSON 포매터를 사용하도록 변경합니다.
    json_formatter_for_file = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)d %(pathname)s' # 추가 정보 포함 (라인 번호, 파일 경로)
    )
    file_handler.setFormatter(json_formatter_for_file)
    root_logger.addHandler(file_handler)

    # 3. JSON 형식의 에러 로그 핸들러 설정 (에러 및 심각한 로그를 구조화된 JSON 형태로 저장)
    # 이 부분은 이미 JSON 형식으로 잘 되어 있으므로 유지합니다.
    error_file_handler = RotatingFileHandler(
        ERROR_LOG_FILE, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
    )
    json_formatter_for_error = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)d %(pathname)s %(exc_info)s' # 예외 정보 추가
    )
    error_file_handler.setFormatter(json_formatter_for_error)
    error_file_handler.setLevel(logging.ERROR) # ERROR 레벨 이상의 로그만 JSON 파일에 기록
    root_logger.addHandler(error_file_handler)

    # Uvicorn 및 SQLAlchemy 로거 설정 (선택 사항, 상세도 조절 가능)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING) # SQLAlchemy 쿼리 로깅
    logging.getLogger("alembic").setLevel(logging.INFO) # Alembic 로깅

# 초기 로깅 설정 적용
setup_logging()
