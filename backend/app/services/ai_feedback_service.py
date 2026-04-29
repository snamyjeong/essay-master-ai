import os # 환경 변수 접근을 위한 임포트
import json # AI의 문자열 응답을 객체로 변환하기 위한 임포트
import re # 마크다운 태그 등을 정제하기 위한 정규표현식 임포트
from typing import List, Dict, Any # 타입 힌트 사용을 위한 임포트
from datetime import datetime, timedelta # 날짜 및 시간 계산을 위한 임포트

from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위한 임포트
from backend.app.models.history import QuizResult, TypingRecord # 모델 임포트

import google.generativeai as genai # Gemini API 사용을 위한 임포트

class AIFeedbackService:
    """
    사용자의 학습 이력을 분석하여 정형화된 JSON 피드백을 제공하는 서비스입니다.
    """

    def __init__(self, db: Session):
        self.db = db
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") 
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=self.gemini_api_key)
        # 2026년 기준 최신 모델인 gemini-2.5-flash를 사용합니다.
        self.model = genai.GenerativeModel('gemini-2.5-flash') 

    def _get_recent_learning_history(self, user_id: int, days: int = 7) -> Dict:
        """ 최근 7일간의 학습 데이터를 쿼리합니다. """
        seven_days_ago = datetime.now() - timedelta(days=days)

        recent_quiz_results = self.db.query(QuizResult).filter(
            QuizResult.user_id == user_id,
            QuizResult.attempted_at >= seven_days_ago
        ).order_by(QuizResult.attempted_at.desc()).all()

        recent_typing_records = self.db.query(TypingRecord).filter(
            TypingRecord.user_id == user_id,
            TypingRecord.attempted_at >= seven_days_ago
        ).order_by(TypingRecord.attempted_at.desc()).all()

        return {
            "quiz_results": [str(r) for r in recent_quiz_results], # 직렬화를 위해 문자열 변환
            "typing_records": [str(r) for r in recent_typing_records]
        }

    def generate_feedback(self, user_id: int) -> Dict[str, Any]:
        """
        AI 모델을 호출하고 결과를 파싱하여 반환합니다.
        """
        history = self._get_recent_learning_history(user_id)
        
        # [프롬프트 최적화] AI에게 JSON 형식을 강요하고, 예외적인 텍스트를 출력하지 못하게 합니다.
        prompt = f"""
        당신은 20년 경력의 일타 강사 정성남입니다. 학생의 학습 이력을 분석하여 JSON 형식으로만 답하세요.
        
        데이터:
        퀴즈: {history['quiz_results']}
        타자: {history['typing_records']}
        
        요구사항:
        1. score: 0~100 사이의 정수
        2. feedback: 격려와 전략을 담은 3~5문장의 해요체 총평
        
        응답 형식 (JSON):
        {{
            "score": 0,
            "feedback": ""
        }}
        """
        
        try:
            # AI 응답 생성
            response = self.model.generate_content(prompt)
            # 생성된 텍스트를 안전하게 파싱합니다.
            return self._safe_json_parse(response.text)
        except Exception as e:
            # 예외 발생 시 베테랑답게 기본값을 반환하여 시스템 가용성을 보장합니다.
            return {
                "score": 0,
                "feedback": f"피드백 생성 중 오류가 발생했습니다: {str(e)}"
            }

    def _safe_json_parse(self, raw_text: str) -> Dict[str, Any]:
        """
        AI가 뱉은 텍스트에서 불필요한 마크다운을 제거하고 JSON으로 변환합니다.
        """
        # 1. ```json 또는 ``` 같은 마크다운 코드 블록 제거
        cleaned = re.sub(r'```json\s?|```', '', raw_text).strip()
        
        try:
            # 2. JSON 파싱 시도
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # 3. 파싱 실패 시 (따옴표 누락 등) 최소한의 구조를 만들어 반환
            # 수석님, 여기서 에러가 났던 것입니다.
            print(f"JSON 파싱 실패: {raw_text}")
            return {
                "score": 50, # 파싱 실패 시 기본 점수
                "feedback": cleaned # 파싱은 실패했지만 텍스트라도 보여줍니다.
            }