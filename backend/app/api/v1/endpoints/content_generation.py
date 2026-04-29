from fastapi import APIRouter, HTTPException, Depends # FastAPI의 핵심 통제 모듈 임포트
from typing import List # 리스트 타입 힌트를 위한 모듈
from backend.app.services.quiz_generator import QuizGenerator # 위에서 수정한 퀴즈 엔진 임포트
from backend.app.schemas.quizzes import QuizGenerationRequest, QuizQuestion # 퀴즈 데이터 규격 임포트

router = APIRouter() # '/api/v1/content' 하위 경로를 관리할 라우터 객체 생성

@router.post("/generate-quiz", response_model=List[QuizQuestion])
async def generate_quiz_content(request: QuizGenerationRequest):
    """
    유저가 제공한 문서를 분석하여 일타 강사 모드로 퀴즈를 생성하는 엔드포인트입니다.
    """
    try:
        # 서비스 인스턴스를 생성하여 비즈니스 로직을 수행합니다.
        generator = QuizGenerator()
        
        # 퀴즈 생성 엔진 가동! (진행시켜!)
        quizzes = generator.generate_quiz(
            document_content=request.document_content,
            quiz_type=request.quiz_type,
            num_questions=request.num_questions
        )
        
        return quizzes # 생성된 퀴즈 리스트를 클라이언트에 반환합니다.

    except ValueError as e:
        # 비즈니스 로직 상의 에러는 400(Bad Request)으로 처리합니다.
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 시스템 레벨의 예기치 못한 에러는 500(Server Error)으로 처리하여 안전성을 확보합니다.
        print(f"API Endpoint Error: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 문제로 퀴즈를 생성할 수 없습니다.")