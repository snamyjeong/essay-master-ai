#!/usr/bin/env zsh
# check_ai_engine.sh - AI 엔진 가용성 정밀 점검 스크립트

# 1. 환경 변수 로드 (backend/.env 우선)
if [ -f backend/.env ]; then
    source backend/.env
    echo "✅ [System] 백엔드 환경 변수(backend/.env) 로드 완료."
elif [ -f .env ]; then
    source ./.env
    echo "✅ [System] 루트 환경 변수(.env) 로드 완료."
fi

# 2. [강화] Conda 가상환경 활성화
# zsh 쉘에서 conda 명령어를 인식시키기 위한 훅 로드
eval "$(conda shell.zsh hook)" 2> /dev/null
# 수석님의 essay-master 가상환경을 명시적으로 활성화
conda activate essay-master 2> /dev/null

# 가상환경 활성화 여부 확인
if [[ "$CONDA_DEFAULT_ENV" != "essay-master" ]]; then
    echo "❌ [Error] 'essay-master' 가상환경을 활성화할 수 없습니다."
    exit 1
fi

# 3. PYTHONPATH 설정
export PYTHONPATH="$(pwd):$(pwd)/backend:$PYTHONPATH"

echo "================================================================"
echo " 🧠 [Jarvis Core] AI 엔진 점검 시퀀스 (Conda: $CONDA_DEFAULT_ENV)"
echo "================================================================"

# 4. API 키 검증
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ [Error] API 키가 없습니다. .env를 확인하세요."
    exit 1
fi

# 5. 모델 가용성 체크 실행 (backend 폴더 내 유틸리티 활용)
python3 backend/check_gen_models.py
python3 backend/check_models.py

echo "================================================================"
echo " ✨ [Jarvis Core] 점검 완료. 서비스 구동 준비가 되었습니다."
echo "================================================================"