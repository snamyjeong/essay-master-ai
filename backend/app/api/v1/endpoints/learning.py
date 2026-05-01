# backend/app/api/v1/endpoints/learning.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # FastAPI 코어 기능
from sqlalchemy.ext.asyncio import AsyncSession # 비동기 DB 처리를 위한 세션 타입 (deps.py와 일치시킴)
from backend.app.api.deps import get_db, get_current_user # 공용 의존성 임포트
from backend.app.services.rag_learning_service import rag_learning_service # RAG 처리 레이어
from backend.app.db.models import User # 사용자 모델
from backend.app.services.quiz_service import QuizGenerationService # 퀴즈 생성 로직 레이어
from pydantic import BaseModel # 데이터 스키마 정의
import traceback # 시스템 오류 발생 시 추적 로그 출력을 위한 모듈

router = APIRouter() # 학습/분석 관련 경로를 관리하는 라우터

class LearningRequest(BaseModel): 
    # 클라이언트로부터 받을 요청 데이터 구조 정의
    text: str # 분석할 원본 학습 텍스트

@router.post("/generate-content") 
async def generate_learning_content(
    request: LearningRequest, 
    db: AsyncSession = Depends(get_db), # [중요] deps.py의 AsyncSession과 데이터 타입을 맞춤
    current_user: User = Depends(get_current_user) # 인증된 마스터 계정 확인
):
    """입력된 텍스트를 분석하여 퀴즈, 논술, 타자 연습 콘텐츠를 생성합니다."""
    try:
        user_id = current_user.id # 현재 세션 유저의 고유 ID 추출
        
        # 1. RAG 지식 베이스(벡터 DB)에 원본 텍스트를 보관 (임시 처리)
        await rag_learning_service.save_content(str(user_id), request.text) 
        
        # 2. 퀴즈 생성 서비스 인스턴스 생성 (비동기 세션 주입)
        quiz_service = QuizGenerationService(db)
        
        # 3. AI 엔진 가동: 실제 퀴즈 및 학습 데이터 생성 요청
        quiz_data = await quiz_service.generate_learning_content(request.text)
        
        return quiz_data # 생성된 결과물을 프론트엔드로 즉시 반환
        
    except Exception as e:
        # [디버깅] 서버 터미널에 에러의 정확한 위치와 원인을 출력합니다.
        traceback.print_exc() 
        # [피드백] 500 에러 발생 시 수석님이 원인을 바로 알 수 있도록 에러 메시지를 detail에 노출합니다.
        raise HTTPException(status_code=500, detail=f"Jarvis 엔진 분석 에러: {str(e)}")

# (이하 evaluate_essay 엔드포인트도 동일한 방식으로 AsyncSession 및 에러 로깅 적용 권장)