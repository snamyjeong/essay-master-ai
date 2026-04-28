#!/usr/bin/env zsh
# start_frontend_service.sh - Conda 가상환경 내 npx를 완벽히 찾아내는 고도화 버전

# 1. 경로 설정
MAIN_FRONT_DIR="$(pwd)/frontend-mobile"  # 메인 Expo 폴더
BACKUP_FRONT_DIR="$(pwd)/frontend-nextjs" # 백업 Next.js 폴더

# 2. 기존 세션 정리
echo "🛑 기존 모든 프런트엔드 세션 정리 중..."
tmux kill-session -t frontend 2>/dev/null
tmux kill-session -t frontend-backup 2>/dev/null
sleep 1 # 세션이 완전히 닫힐 때까지 대기

# 3. [핵심 로직] 메인 기동 및 주소 추출
if [ -d "$MAIN_FRONT_DIR" ]; then
    echo "🚀 [Main UI] Expo Mobile 서비스를 백그라운드에서 기동합니다."
    # 새 tmux 세션을 생성합니다.
    tmux new-session -d -s frontend -c "$MAIN_FRONT_DIR"
    
    # 4. [환경 보강] Conda 환경을 tmux 세션 내부로 전이시킵니다.
    # zsh에서 conda를 사용하기 위한 초기화 훅을 먼저 실행합니다.
    tmux send-keys -t frontend "eval \"\$(conda shell.zsh hook)\"" C-m
    # 확인된 npx가 들어있는 가상환경을 강제로 활성화합니다.
    tmux send-keys -t frontend "conda activate essay-master" C-m
    
    # 수석님께서 확인해주신 npx의 절대 경로를 변수로 잡아 실행 안전성을 확보합니다.
    NPX_EXE="/home/snamy78/miniconda3/envs/essay-master/bin/npx"
    echo "🔍 npx 경로 확인: $NPX_EXE"
    
    # Expo 서비스를 터널링 모드로 백그라운드에서 실행합니다.
    tmux send-keys -t frontend "$NPX_EXE expo start --tunnel" C-m
    
    # 5. 접속 URL 추출 시퀀스 (최대 1분 대기)
    echo "⏳ 보안 환경을 위한 접속 주소 추출 중... (잠시만 기다려주세요)"
    for i in {1..60}; do
        sleep 1
        # tmux 히스토리 전체를 긁어 'exp://' 로 시작하는 주소만 추출합니다.
        EXPO_URL=$(tmux capture-pane -pt frontend -S - | grep -o 'exp://[a-zA-Z0-9./?-]*' | tail -n 1)
        if [ ! -z "$EXPO_URL" ]; then
            echo "\n✅ 접속 주소 추출 성공!"
            break
        fi
        echo -n "■" # 진행률 시각화
    done
else
    echo "⚠️  메인 폴더가 없습니다. 백업 서비스를 기동합니다."
    tmux new-session -d -s frontend-backup -c "$BACKUP_FRONT_DIR"
    tmux send-keys -t frontend-backup "npm run dev" C-m
fi

# 6. 최종 가동 결과 보고
echo "----------------------------------------------------------------"
echo "🔍 현재 실행 중인 프런트엔드 tmux 세션 리스트:"
tmux ls | grep frontend

echo "----------------------------------------------------------------"
echo "✨ 모든 서비스가 정상 궤도 진입을 시도 중입니다."

if [ ! -z "$EXPO_URL" ]; then
    echo "🔗 [보안 접속용 URL] 태블릿 주소창에 아래 주소를 입력하세요:"
    echo "👉 $EXPO_URL"
    echo "----------------------------------------------------------------"
    echo "📱 상세 로그 및 QR 코드 확인: tmux attach -t frontend"
else
    echo "❌ 주소 추출 실패. 직접 로그 확인이 필요합니다."
    echo "📝 확인 명령어: tmux attach -t frontend"
fi
echo "💡 팁: 로그 화면 탈출은 [Ctrl + B] 누른 후 [D] 입니다."
echo "----------------------------------------------------------------"