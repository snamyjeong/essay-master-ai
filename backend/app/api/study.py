from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from backend.app.utils import get_current_active_user

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/study", # /study 경로 접두사 사용
    tags=["Study"],  # API 문서에 표시될 태그
)

# 퀴즈 제출 요청 모델
class QuizSubmission(BaseModel):
    quiz_id: str        # 퀴즈 ID
    user_answer: str    # 사용자 제출 답안

# 퀴즈 평가 응답 모델
class QuizEvaluation(BaseModel):
    quiz_id: str        # 퀴즈 ID
    is_correct: bool    # 정답 여부
    feedback: str       # 피드백 내용
    correct_answer: Optional[str] = None # 정답 (오답일 경우 제공)

# 심화 학습 평가 요청 모델
class EvaluationRequest(BaseModel):
    learning_content: str   # 학습 내용
    user_response: str      # 사용자 응답 (예: 서술형 답변)
    evaluation_type: str    # 평가 유형 (예: "서술형", "논술")

# 심화 학습 평가 응답 모델
class EvaluationResponse(BaseModel):
    evaluation_result: str  # 평가 결과 텍스트
    score: Optional[int] = None # 점수 (선택 사항)
    feedback_details: Optional[dict] = None # 상세 피드백 (선택 사항)

# --- 퀴즈 제출 및 평가 엔드포인트 ---
@router.post("/evaluate/quiz", response_model=QuizEvaluation)
async def evaluate_quiz(submission: QuizSubmission, current_user: str = Depends(get_current_active_user)):
    """
    사용자가 제출한 퀴즈 답안을 평가합니다.
    """
    # 실제 퀴즈 평가 로직 구현 (예: DB에서 정답 조회, AI 모델을 통한 채점)
    if submission.user_answer.lower() == "정답": # 임시 로직
        return QuizEvaluation(quiz_id=submission.quiz_id, is_correct=True, feedback="정답입니다!")
    else:
        return QuizEvaluation(quiz_id=submission.quiz_id, is_correct=False, feedback="오답입니다. 다시 시도해보세요.", correct_answer="정답")

# --- 심화 학습 평가 엔드포인트 ---
@router.post("/evaluate/deep_learning", response_model=EvaluationResponse)
async def evaluate_deep_learning(request: EvaluationRequest, current_user: str = Depends(get_current_active_user)):
    """
    심화 학습 내용에 대한 사용자 응답을 평가합니다.
    """
    # 실제 심화 학습 평가 로직 (예: AI 모델을 통한 서술형 평가)
    feedback_text = f"'{request.evaluation_type}' 평가 결과: 사용자의 '{request.user_response[:30]}'... 응답에 대해 AI가 심층 분석했습니다."
    return EvaluationResponse(evaluation_result=feedback_text, score=85, feedback_details={"comprehension": "Good", "logic": "Needs Improvement"})
