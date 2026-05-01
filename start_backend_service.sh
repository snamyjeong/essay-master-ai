#!/usr/bin/env zsh
# start_backend_service.sh - Jarvis 백엔드 및 워커 통합 기동 스크립트 (V3 안정화 버전)

# 1. 환경 및 경로 설정
export PYTHONPATH="$(pwd):$PYTHONPATH" # 프로젝트 루트를 Python 경로에 등록

# [핵심] .env 파일에서 API 키 등 환경 변수를 읽어 현재 프로세스에 로드합니다.
if [ -f .env ]; then
    echo "📄 .env 파일을 로드하여 환경 변수를 설정합니다..."
    set -a
    source .env
    set +a
else
    echo "⚠️  .env 파일을 찾을 수 없습니다. API 키 설정 확인이 필요합니다."
fi

DB_ABS_DIR="$(pwd)/app_data" # DB 저장 폴더 경로
# SQLite 비동기 처리를 위한 URL 설정
export DATABASE_URL="sqlite+aiosqlite:///${DB_ABS_DIR}/jarvis_neo.db" 

# 2. 기존 세션 정리
echo "🛑 기존 백엔드/워커 세션 정리 중..."
tmux kill-session -t backend 2>/dev/null
tmux kill-session -t celery 2>/dev/null
sleep 1

# 3. DB 초기화 (스키마 생성)
echo "🔑 데이터베이스 스키마 동기화 중..."
python3 backend/init_db.py

# 4. 백엔드(FastAPI) 시작 시퀀스
echo "🚀 [1/2] 백엔드 서비스를 시작합니다 (Session: backend)..."
tmux new-session -d -s backend
tmux send-keys -t backend "eval \"\$(conda shell.zsh hook)\"" C-m
tmux send-keys -t backend "conda activate essay-master" C-m
# [중요] tmux 세션 내부로 필수 환경 변수를 명시적으로 전달합니다.
if [ -f .env ]; then
    grep -v '^#' .env | xargs -I {} tmux send-keys -t backend "export {}" C-m
fi
tmux send-keys -t backend "export DATABASE_URL='${DATABASE_URL}'" C-m
tmux send-keys -t backend "export GEMINI_API_KEY='${GEMINI_API_KEY}'" C-m
tmux send-keys -t backend "export GOOGLE_API_KEY='${GOOGLE_API_KEY}'" C-m
tmux send-keys -t backend "export PYTHONPATH='$(pwd)'" C-m
tmux send-keys -t backend "python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000" C-m

# 5. 워커(Celery) 시작 시퀀스
echo "🚀 [2/2] Celery 비동기 워커를 시작합니다 (Session: celery)..."
tmux new-session -d -s celery
tmux send-keys -t celery "eval \"\$(conda shell.zsh hook)\"" C-m
tmux send-keys -t celery "conda activate essay-master" C-m
# 워커도 RAG 분석을 수행해야 하므로 동일한 환경 변수가 필요합니다.
tmux send-keys -t celery "export DATABASE_URL='${DATABASE_URL}'" C-m
tmux send-keys -t celery "export GEMINI_API_KEY='${GEMINI_API_KEY}'" C-m
tmux send-keys -t celery "export GOOGLE_API_KEY='${GOOGLE_API_KEY}'" C-m
tmux send-keys -t celery "export PYTHONPATH='$(pwd)'" C-m
tmux send-keys -t celery "celery -A backend.app.worker.celery_worker worker --loglevel=info" C-m

# 6. 최종 상태 확인 및 결과 출력
echo "----------------------------------------------------------------"
echo "🔍 현재 실행 중인 tmux 세션 리스트:"
tmux ls

echo "----------------------------------------------------------------"
echo "✨ 모든 서비스가 정상 궤도에 진입했습니다."
echo "📝 백엔드 로그 확인: tmux attach -t backend"
echo "⚙️  워커 로그 확인: tmux attach -t celery"
echo "📱 접속 주소(Local): http://$(hostname -I | awk '{print $1}'):8000"
echo "----------------------------------------------------------------"