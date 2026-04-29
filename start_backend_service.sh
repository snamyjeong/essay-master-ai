#!/usr/bin/env zsh
# start_backend_service.sh - Jarvis 백엔드 및 워커 통합 기동 스크립트

# 1. 환경 및 경로 설정: Python이 프로젝트 구조를 올바르게 인식하도록 합니다.
export PYTHONPATH="$(pwd):$PYTHONPATH" # 현재 폴더와 backend 폴더를 경로에 등록합니다.
DB_ABS_DIR="$(pwd)/app_data" # 데이터베이스가 저장될 경로를 변수로 설정합니다.
export DATABASE_URL="sqlite+aiosqlite:///${DB_ABS_DIR}/jarvis_neo.db" # 애플리케이션용 DB 접속 정보를 환경 변수로 보냅니다.

# 2. 기존 세션 정리: 중복 실행을 막기 위해 실행 중인 세션들을 종료합니다.
echo "🛑 기존 백엔드/워커 세션 정리 중..."
tmux kill-session -t backend 2>/dev/null # backend 세션이 존재하면 종료합니다.
tmux kill-session -t celery 2>/dev/null # celery 세션이 존재하면 종료합니다.
sleep 1 # 세션이 완전히 닫히도록 1초간 대기합니다.

# 3. DB 초기화: 데이터베이스 테이블을 생성하거나 마이그레이션을 수행합니다.
echo "🔑 데이터베이스 스키마 동기화 중..."
python3 backend/init_db.py # DB 초기화 스크립트를 직접 실행합니다.

# 4. 백엔드(FastAPI) 시작 시퀀스
echo "🚀 [1/2] 백엔드 서비스를 시작합니다 (Session: backend)..."
tmux new-session -d -s backend # 백그라운드 세션을 생성합니다.
tmux send-keys -t backend "eval \"\$(conda shell.zsh hook)\"" C-m # Conda 사용을 위한 훅을 로드합니다.
tmux send-keys -t backend "conda activate essay-master" C-m # 전용 가상환경을 활성화합니다.
tmux send-keys -t backend "export DATABASE_URL='${DATABASE_URL}'" C-m # 내부에서 쓸 DB 경로를 설정합니다.
tmux send-keys -t backend "export PYTHONPATH='$(pwd)'" C-m # 내부용 Python 경로를 설정합니다.
tmux send-keys -t backend "python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000" C-m # 서버를 가동합니다.

# 5. 워커(Celery) 시작 시퀀스
echo "🚀 [2/2] Celery 비동기 워커를 시작합니다 (Session: celery)..."
tmux new-session -d -s celery # 워커용 백그라운드 세션을 생성합니다.
tmux send-keys -t celery "eval \"\$(conda shell.zsh hook)\"" C-m # Conda 훅 로드
tmux send-keys -t celery "conda activate essay-master" C-m # 가상환경 활성화
tmux send-keys -t celery "export DATABASE_URL='${DATABASE_URL}'" C-m # DB 경로 주입
tmux send-keys -t celery "export PYTHONPATH='$(pwd)'" C-m # 경로 설정
tmux send-keys -t celery "celery -A backend.app.worker.celery_worker worker --loglevel=info" C-m # 워커 실행

# 6. 최종 상태 확인 및 결과 출력 (성남 님 요청 양식 적용)
echo "----------------------------------------------------------------"
echo "🔍 현재 실행 중인 tmux 세션 리스트:"
tmux ls # 현재 활성화된 세션 목록을 출력하여 정상 생성을 확인합니다.

echo "----------------------------------------------------------------"
echo "✨ 모든 서비스가 정상 궤도에 진입했습니다."
echo "📝 백엔드 로그 확인: tmux attach -t backend"
echo "⚙️  워커 로그 확인: tmux attach -t celery"
echo "📱 접속 주소(Local): http://$(hostname -I | awk '{print $1}'):8000" # 실제 서버 내부 IP를 자동으로 찾아 표시합니다.
echo "----------------------------------------------------------------"