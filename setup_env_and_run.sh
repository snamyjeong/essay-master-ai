#!/bin/bash
# setup_env_and_run.sh

echo "Checking and setting up 'essay-master' conda environment..." # 환경 설정 시작 메시지 출력

# Conda 환경 활성화 (base 환경으로 가서 essay-master 활성화)
source "$(conda info --base)/etc/profile.d/conda.sh" # conda 초기화 스크립트를 소스하여 conda 명령어를 사용 가능하게 합니다.
conda activate essay-master # 'essay-master' conda 환경을 활성화합니다.

# 필요한 패키지 설치
echo "Installing/updating packages from requirements.txt..." # 패키지 설치 시작 메시지 출력
pip install -r requirements.txt # requirements.txt 파일에 명시된 모든 패키지를 현재 활성화된 conda 환경에 설치합니다.

echo "Conda environment setup complete. Now running services..." # 환경 설정 완료 메시지 출력

# start_service.sh 실행
bash start_service.sh # 실제 서비스 시작 스크립트 (start_service.sh)를 실행합니다.
