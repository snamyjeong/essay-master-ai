from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.essay_generation import EssayGenerationRequest, EssayResponse, GenerationResultResponse, EssayEvaluationRequest, EssayEvaluationResponse
from app.schemas.history import TypingRecordCreate, TypingRecordResponse, QuizResultCreate, QuizResultResponse
from app.db.mongodb import AsyncIOMotorClient, get_database
from app.crud.essay import generate_essay_data, evaluate_essay_data, save_typing_record_data, save_quiz_result_data
from app.core.logging import get_logger # get_logger 함수를 임포트합니다.

router = APIRouter()
logger = get_logger(__name__) # 로거 인스턴스 가져오기

# 논술 생성 API
@router.post("/generate", response_model=EssayResponse, status_code=status.HTTP_201_CREATED)
async def generate_essay(
    request: EssayGenerationRequest, db: AsyncIOMotorClient = Depends(get_database)
):
    logger.info(f"논술 생성 API 호출됨: prompt_id={request.prompt_id}, user_id={request.user_id}") # API 호출 로그
    try:
        essay_data = await generate_essay_data(db, request)
        logger.info(f"논술 생성 성공: essay_id={essay_data.id}") # 논술 생성 성공 로그
        return essay_data
    except Exception as e:
        logger.error(f"논술 생성 실패: {e}", exc_info=True) # 논술 생성 실패 로그 (예외 정보 포함)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"논술 생성 중 오류 발생: {e}",
        )

# 논술 평가 API
@router.post("/evaluate", response_model=EssayEvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_essay(
    request: EssayEvaluationRequest, db: AsyncIOMotorClient = Depends(get_database)
):
    logger.info(f"논술 평가 API 호출됨: essay_id={request.essay_id}, user_id={request.user_id}") # API 호출 로그
    try:
        evaluation_result = await evaluate_essay_data(db, request)
        logger.info(f"논술 평가 성공: essay_id={request.essay_id}") # 논술 평가 성공 로그
        return evaluation_result
    except Exception as e:
        logger.error(f"논술 평가 실패: {e}", exc_info=True) # 논술 평가 실패 로그 (예외 정보 포함)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"논술 평가 중 오류 발생: {e}",
        )

# 타이핑 기록 저장 API
@router.post("/typing-record", response_model=TypingRecordResponse, status_code=status.HTTP_201_CREATED)
async def save_typing_record(
    record: TypingRecordCreate, db: AsyncIOMotorClient = Depends(get_database)
):
    logger.info(f"타이핑 기록 저장 API 호출됨: user_id={record.user_id}, essay_id={record.essay_id}") # API 호출 로그
    try:
        saved_record = await save_typing_record_data(db, record)
        logger.info(f"타이핑 기록 저장 성공: record_id={saved_record.id}") # 저장 성공 로그
        return saved_record
    except Exception as e:
        logger.error(f"타이핑 기록 저장 실패: {e}", exc_info=True) # 저장 실패 로그
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"타이핑 기록 저장 중 오류 발생: {e}",
        )

# 퀴즈 결과 저장 API
@router.post("/quiz-result", response_model=QuizResultResponse, status_code=status.HTTP_201_CREATED)
async def save_quiz_result(
    result: QuizResultCreate, db: AsyncIOMotorClient = Depends(get_database)
):
    logger.info(f"퀴즈 결과 저장 API 호출됨: user_id={result.user_id}, quiz_id={result.quiz_id}") # API 호출 로그
    try:
        saved_result = await save_quiz_result_data(db, result)
        logger.info(f"퀴즈 결과 저장 성공: result_id={saved_result.id}") # 저장 성공 로그
        return saved_result
    except Exception as e:
        logger.error(f"퀴즈 결과 저장 실패: {e}", exc_info=True) # 저장 실패 로그
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"퀴즈 결과 저장 중 오류 발생: {e}",
        )
