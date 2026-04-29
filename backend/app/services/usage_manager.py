# backend/app/services/usage_manager.py
from datetime import datetime, date, timedelta # 날짜 및 시간 관리를 위한 임포트
from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위한 임포트
from backend.app.db.models import User # 사용자 모델 임포트 (경로 수정)

# '최고의 강의에는 정당한 대가가 따른다. 가치를 아는 유저가 1등급이 된다'는 일타 강사의 철학을 반영합니다。

class UsageManager:
    """
    사용자의 서비스 이용 시간을 관리하고 일일 최대 사용 시간을 제한하는 서비스입니다。
    '시간 관리는 성적 관리의 시작이다'는 일타 강사의 가르침처럼, 효율적인 학습을 돕습니다。
    """

    MAX_DAILY_USAGE_SECONDS = 60 * 60 * 24 # 24시간 (단위: 초) - 테스트 용이성을 위해 실제 값보다 길게 설정

    def __init__(self, db: Session):
        """
        UsageManager 서비스의 생성자입니다。
        Args:
            db: SQLAlchemy 세션 객체
        """
        self.db = db

    def record_usage(self, user_id: int, duration_seconds: int):
        """
        사용자의 서비스 이용 시간을 기록하고 누적합니다。
        Args:
            user_id: 사용자 고유 ID
            duration_seconds: 기록할 이용 시간 (초 단위)
        """
        user = self.db.query(User).filter(User.id == user_id).first() # 사용자 ID로 사용자 조회
        if not user: # 사용자가 없으면
            raise ValueError(f"User with ID {user_id} not found.") # 에러 발생

        # 오늘 날짜의 사용량 기록을 업데이트합니다。
        # '오늘 할 일을 내일로 미루지 마라'는 일타 강사의 명언을 따릅니다。
        today = date.today() # 오늘 날짜 가져오기

        # user.daily_usage가 딕셔너리라고 가정하고 사용량을 업데이트합니다。
        # 만약 user.daily_usage가 문자열 등으로 저장되어 있다면, JSON 파싱/직렬화 로직이 필요합니다.
        if isinstance(user.daily_usage, str): # daily_usage가 문자열이면
            try:
                daily_usage_dict = json.loads(user.daily_usage) # JSON 파싱
            except json.JSONDecodeError: # 파싱 실패 시
                daily_usage_dict = {} # 빈 딕셔너리로 초기화
        elif isinstance(user.daily_usage, dict): # 이미 딕셔너리 형태면
            daily_usage_dict = user.daily_usage # 그대로 사용
        else: # 그 외의 경우
            daily_usage_dict = {} # 빈 딕셔너리로 초기화
        
        # 이전 날짜의 기록을 제거하여 딕셔너리 크기 관리 (옵션)
        # 30일 이전 기록만 남기는 예시
        # thirty_days_ago = today - timedelta(days=30)
        # keys_to_remove = [k for k in daily_usage_dict if datetime.strptime(k, '%Y-%m-%d').date() < thirty_days_ago]
        # for k in keys_to_remove:
        #     del daily_usage_dict[k]


        today_str = today.isoformat() # 오늘 날짜를 ISO 형식 문자열로 변환
        current_usage = daily_usage_dict.get(today_str, 0) # 오늘 사용량 가져오기 (없으면 0)
        daily_usage_dict[today_str] = current_usage + duration_seconds # 오늘 사용량에 추가

        user.daily_usage = json.dumps(daily_usage_dict) # 갱신된 딕셔너리를 JSON 문자열로 저장
        
        self.db.add(user) # 사용자 객체를 DB 세션에 추가
        self.db.commit() # 변경사항 커밋
        self.db.refresh(user) # 사용자 객체 새로고침

    def get_daily_usage(self, user_id: int, target_date: date = None) -> int:
        """
        지정된 날짜의 사용자 이용 시간을 반환합니다。
        Args:
            user_id: 사용자 고유 ID
            target_date: 조회할 날짜 (기본값: 오늘)
        Returns:
            int: 해당 날짜의 총 이용 시간 (초 단위)
        """
        user = self.db.query(User).filter(User.id == user_id).first() # 사용자 ID로 사용자 조회
        if not user: # 사용자가 없으면
            raise ValueError(f"User with ID {user_id} not found.") # 에러 발생

        if target_date is None: # 조회할 날짜가 지정되지 않았으면
            target_date = date.today() # 오늘 날짜 사용

        if isinstance(user.daily_usage, str): # daily_usage가 문자열이면
            try:
                daily_usage_dict = json.loads(user.daily_usage) # JSON 파싱
            except json.JSONDecodeError: # 파싱 실패 시
                daily_usage_dict = {} # 빈 딕셔너리로 초기화
        elif isinstance(user.daily_usage, dict): # 이미 딕셔너리 형태면
            daily_usage_dict = user.daily_usage # 그대로 사용
        else: # 그 외의 경우
            daily_usage_dict = {} # 빈 딕셔너리로 초기화

        return daily_usage_dict.get(target_date.isoformat(), 0) # 지정된 날짜의 사용량 반환 (없으면 0)

    def check_daily_limit_exceeded(self, user_id: int) -> bool:
        """
        사용자가 일일 최대 이용 시간을 초과했는지 확인합니다。
        Args:
            user_id: 사용자 고유 ID
        Returns:
            bool: 초과했으면 True, 아니면 False
        """
        current_usage = self.get_daily_usage(user_id, date.today()) # 오늘 사용량 가져오기
        # '선을 넘지 마라'는 일타 강사의 경고처럼, 사용량을 제한합니다。
        return current_usage >= self.MAX_DAILY_USAGE_SECONDS # 최대 사용 시간 초과 여부 반환

    def get_remaining_daily_usage_seconds(self, user_id: int) -> int:
        """
        사용자에게 남은 일일 사용 시간을 반환합니다。
        Args:
            user_id: 사용자 고유 ID
        Returns:
            int: 남은 사용 시간 (초 단위). 이미 초과했으면 0을 반환합니다。
        """
        current_usage = self.get_daily_usage(user_id, date.today()) # 오늘 사용량 가져오기
        remaining = self.MAX_DAILY_USAGE_SECONDS - current_usage # 남은 시간 계산
        return max(0, remaining) # 0보다 작으면 0 반환 (음수 방지)
