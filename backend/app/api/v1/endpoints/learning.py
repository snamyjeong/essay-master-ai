from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # FastAPI 구성 요소 및 파일 업로드 처리를 위한 임포트
from sqlalchemy.orm import Session # 데이터베이스 세션 처리를 위한 SQLAlchemy 임포트
from backend.app.api.deps import get_db, get_current_user # DB 세션 및 현재 사용자 획득을 위한 의존성 주입 함수 임포트
from backend.app.services.rag_learning_service import rag_learning_service # RAG 지식 저장 및 PDF 처리를 위한 서비스 임포트
from backend.app.db.models import User # 사용자 모델 임포트
from backend.app.services.quiz_service import QuizGenerationService # AI 강사 페르소나의 퀴즈 생성 서비스 임포트
from pydantic import BaseModel # 데이터 요청 규격을 정의하기 위한 Pydantic BaseModel 임포트
from backend.app.schemas.essay_generation import EssayEvaluationResponse # 심화 논술 평가 응답 스키마 임포트

router = APIRouter() # '/api/v1/learning' 하위 경로의 모든 API를 관리할 라우터 인스턴스 생성

class LearningRequest(BaseModel): 
    """
    프론트엔드에서 학습 텍스트를 보낼 때 사용하는 데이터 규격입니다.
    """
    content: str # 유저가 분석을 요청한 학습 내용 본문

@router.post("/generate-content") 
async def generate_learning_content(
    request: LearningRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 현재 로그인된 사용자 정보 주입
):
    """
    제출된 학습 내용을 RAG 벡터 DB에 영구 저장하고, AI 강사 모드로 퀴즈를 생성합니다.
    """
    try:
        user_id = current_user.id # 인증된 사용자 ID 사용
        
        # 1. 사용자의 지식을 RAG(검색 증강 생성) 시스템의 벡터 DB에 안전하게 저장합니다.
        await rag_learning_service.save_content(str(user_id), request.content) # user_id는 str 타입으로 전달
        
        # 2. 퀴즈 생성 서비스를 DB 세션과 함께 초기화합니다.
        quiz_service = QuizGenerationService(db)
        
        # 이 과정에서 단답형, 논술형, 타자 연습 문구, 멘토링이 병렬로 생성됩니다.
        quiz_data = await quiz_service.generate_learning_content(request.content)
        
        # 분석이 완료된 퀴즈 및 학습 데이터를 프론트엔드로 반환합니다.
        return quiz_data 
        
    except Exception as e:
        # 엔진 가동 중 오류 발생 시 터미널에 상세 로그를 출력하고 클라이언트에 에러를 던집니다.
        print(f"학습 콘텐츠 생성 실패 상세 로그: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Jarvis 분석 엔진 오류: {str(e)}")

@router.post("/upload-pdf") 
async def upload_pdf(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 현재 로그인된 사용자 정보 주입
):
    """
    PDF 파일을 업로드받아 텍스트를 추출하고, 해당 지식을 기반으로 학습 콘텐츠를 생성합니다.
    """
    try:
        user_id = current_user.id # 인증된 사용자 ID 사용
        
        # 1. 업로드된 PDF 파일에서 텍스트를 추출하고 RAG 지식 베이스에 적재합니다.
        extracted_text = await rag_learning_service.process_pdf(str(user_id), file) # user_id는 str 타입으로 전달
        
        # 2. 추출된 대량의 텍스트를 분석 엔진에 주입하여 퀴즈 세트를 구성합니다.
        quiz_service = QuizGenerationService(db)
        
        # PDF 추출 텍스트에 대해서도 올바른 메서드명을 호출하도록 수정했습니다.
        quiz_data = await quiz_service.generate_learning_content(extracted_text)
        
        return quiz_data
    except Exception as e:
        # PDF 파싱이나 AI 호출 중 발생한 예외를 처리합니다.
        print(f"PDF 분석 및 퀴즈 연계 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 분석 엔진 오류: {str(e)}")

# --- 심화 논술 평가 API ---

class EssayEvaluationRequest(BaseModel):
    """
    프론트엔드에서 논술 평가를 요청할 때 사용하는 데이터 규격입니다.
    """
    question: str # 출제된 심화 논술 주제
    answer: str   # 유저가 작성한 논술 답안

@router.post("/evaluate-essay", response_model=EssayEvaluationResponse) # 응답 모델 지정
async def evaluate_essay(
    request: EssayEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 현재 로그인된 사용자 정보 주입
):
    """
    유저가 작성한 심화 논술 답안을 AI가 평가하여 피드백을 반환합니다.
    """
    try:
        # 퀴즈 생성 서비스를 DB 세션과 함께 초기화합니다.
        quiz_service = QuizGenerationService(db)
        
        # 유저가 입력한 답안의 앞뒤 공백을 제거합니다.
        user_answer = request.answer.strip()
        
        user_id = str(current_user.id) # 사용자 ID를 문자열로 변환하여 전달
        
        # RAG 시스템과 Gemini 2.5 Flash를 연동한 심층 평가 로직 호출
        evaluation_result = await quiz_service.evaluate_essay_answer_with_rag(
            user_id=user_id,
            question=request.question,
            user_answer=user_answer
        )
            
        # 평가 결과를 EssayEvaluationResponse Pydantic 모델에 맞춰 반환
        return EssayEvaluationResponse(**evaluation_result)
        
    except HTTPException as e:
        # quiz_service에서 발생한 HTTPException을 그대로 전달합니다.
        raise e
    except Exception as e:
        # 평가 중 오류 발생 시 터미널에 상세 로그를 출력하고 클라이언트에 500 에러를 던집니다.
        print(f"논술 평가 실패 상세 로그: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 평가 엔진 오류: {str(e)}")
