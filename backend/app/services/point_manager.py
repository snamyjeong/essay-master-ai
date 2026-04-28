# backend/app/services/point_manager.py
from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위한 임포트
from app.db.models import User # 사용자 모델 임포트 (경로 수정)
from app.models.history import QuizResult, TypingRecord # 퀴즈 결과 및 타자 기록 모델 임포트 (경로 수정)

class PointManager:
    """
    사용자의 학습 활동에 따라 포인트를 관리하는 서비스입니다。
    '성적은 계단식으로 오른다. 지금의 포인트가 내일의 실력이다'는 일타 강사의 모토처럼,
    학습 성과를 포인트로 보상하여 학습 동기를 부여합니다。
    """

    def __init__(self, db: Session):
        """
        PointManager 서비스의 생성자입니다。
        Args:
            db: SQLAlchemy 세션 객체
        """
        self.db = db

    def _get_user(self, user_id: int) -> User:
        """
        지정된 ID의 사용자 객체를 데이터베이스에서 조회합니다。
        Args:
            user_id: 사용자 고유 ID
        Returns:
            User: 사용자 객체
        Raises:
            ValueError: 사용자를 찾을 수 없을 때 발생
        """
        user = self.db.query(User).filter(User.id == user_id).first() # 사용자 ID로 사용자 조회
        if not user: # 사용자가 없으면
            raise ValueError(f"User with ID {user_id} not found.") # 에러 발생
        return user

    def calculate_quiz_points(self, quiz_result: QuizResult) -> int:
        """
        퀴즈 결과에 따라 포인트를 계산합니다。
        Args:
            quiz_result: 퀴즈 결과 객체
        Returns:
            int: 지급될 포인트
        """
        # 퀴즈 점수(score) 10점당 1포인트를 지급합니다。
        # '점수는 노력의 흔적'이라는 일타 강사의 철학을 반영합니다.
        points = quiz_result.score // 10 if quiz_result.score is not None else 0 # 점수를 10으로 나눈 몫을 포인트로 지급 (None 처리 추가)
        return points

    def calculate_typing_points(self, typing_record: TypingRecord) -> int:
        """
        타자 기록에 따라 포인트를 계산합니다。
        Args:
            typing_record: 타자 기록 객체
        Returns:
            int: 지급될 포인트
        """
        # WPM(분당 단어 수) 10점당 1포인트, 정확도 10%당 1포인트를 지급합니다。
        # '정확하고 빠르게'는 실력 향상의 기본이라는 일타 강사의 가르침을 따릅니다。
        wpm_points = int(typing_record.wpm // 10) # WPM 10점당 1포인트
        accuracy_points = int(typing_record.accuracy * 10) # 정확도 0.1당 1포인트 (예: 0.9 -> 9포인트)
        total_points = wpm_points + accuracy_points # 총 포인트 합산
        return total_points

    def add_points_to_user(self, user_id: int, points: int):
        """
        지정된 사용자에게 포인트를 추가합니다。
        Args:
            user_id: 사용자 고유 ID
            points: 추가할 포인트 양
        """
        user = self._get_user(user_id) # 사용자 객체 조회
        user.point_balance += points # 사용자의 포인트 잔액에 포인트 추가
        self.db.add(user) # 사용자 객체를 DB 세션에 추가 (변경사항 추적)
        self.db.commit() # 변경사항 커밋
        self.db.refresh(user) # 사용자 객체 새로고침 (최신 상태 반영)

    def get_user_total_points(self, user_id: int) -> int:
        """
        사용자의 현재 누적 포인트를 반환합니다。
        Args:
            user_id: 사용자 고유 ID
        Returns:
            int: 사용자의 현재 포인트 잔액
        """
        user = self._get_user(user_id) # 사용자 객체 조회
        return user.point_balance # 포인트 잔액 반환
