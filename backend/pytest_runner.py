# backend/pytest_runner.py
import pytest
import os
import sys

# 현재 스크립트 파일의 디렉토리를 Python 경로에 추가합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
# 프로젝트의 루트 디렉토리를 sys.path에 추가하여 모듈 임포트 문제를 해결합니다.
# essay-master-ai/backend 가 current_dir 이므로, 상위 디렉토리 (essay-master-ai)를 추가해야 합니다.
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

# pytest.main() 함수에 직접 인자를 전달하여 테스트를 실행합니다.
# -s: print문 출력을 허용합니다.
# --rootdir: pytest가 프로젝트의 루트 디렉토리를 인식하도록 합니다.
# 테스트를 실행할 디렉토리 또는 파일을 지정합니다.
pytest_args = [
    '-s',
    f'--rootdir={project_root}',
    'backend/app/tests'
]

# pytest 실행 결과를 캡처하기 위해 파일로 리다이렉션합니다.
with open('pytest_output.log', 'w') as f:
    # stdout과 stderr를 파일로 임시 리다이렉션합니다.
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = f
    sys.stderr = f
    try:
        # pytest.main()을 호출하여 테스트를 실행합니다.
        # 이전에 pytest.ExitCode.NO_TESTS_COLLECTED (5)가 발생했으므로,
        # 다시 한번 실행하여 이번에는 테스트가 수집되는지 확인합니다.
        exit_code = pytest.main(pytest_args)
    finally:
        # 원래의 stdout과 stderr로 복원합니다.
        sys.stdout = old_stdout
        sys.stderr = old_stderr

# pytest 실행 결과를 출력합니다.
if exit_code == 0:
    print("✅ 모든 테스트 통과")
elif exit_code == pytest.ExitCode.NO_TESTS_COLLECTED:
    print("⚠️ 테스트가 수집되지 않았습니다. (0개 수집됨)")
else:
    print(f"❌ 테스트 실패: {exit_code}")

# 로그 파일 내용 요약 출력 (선택 사항)
print('\\n--- pytest_output.log 요약 ---') # <<<<<< 이 부분을 수정합니다.
with open('pytest_output.log', 'r') as f:
    log_content = f.read()
    # 첫 20줄과 마지막 20줄만 출력하여 요약
    lines = log_content.splitlines()
    if len(lines) > 40:
        for line in lines[:20]:
            print(line)
        print("...")
        for line in lines[-20:]:
            print(line)
    else:
        print(log_content)
print("------------------------------")
