#!/usr/bin/env python3

from fastapi import APIRouter, HTTPException # FastAPI의 APIRouter와 HTTPException을 임포트합니다.
from starlette.responses import JSONResponse # JSON 형식의 응답을 반환하기 위한 JSONResponse를 임포트합니다.
from app.worker.celery_worker import example_task # 정의된 비동기 작업 (example_task)을 절대 경로로 임포트합니다.
import logging # 로깅을 위한 모듈을 임포트합니다.

router = APIRouter() # APIRouter 인스턴스를 생성합니다.

logger = logging.getLogger(__name__) # 현재 모듈의 로거를 가져옵니다.

@router.post("/example-task/", summary="비동기 예제 작업 실행", description="Celery를 사용하여 백그라운드에서 실행되는 간단한 예제 작업을 시작합니다.") # POST 요청을 처리하는 라우터 데코레이터. API 요약 및 설명을 포함합니다.
async def run_example_task(payload: dict): # 비동기 함수로, 요청 본문에서 페이로드를 받습니다.
    logger.info(f"Received request to run example task with payload: {payload}") # 요청 수신 로그를 기록합니다.
    try:
        task = example_task.delay(payload) # Celery의 delay() 메서드를 사용하여 비동기 작업을 시작하고, 작업 객체를 반환합니다.
        logger.info(f"Celery task {task.id} dispatched.") # Celery 작업 ID를 로그에 기록합니다.
        return JSONResponse({"task_id": task.id, "status": "Task dispatched"}) # 작업 ID와 상태를 JSON 응답으로 반환합니다.
    except Exception as e: # 작업 디스패치 중 예외 발생 시 처리합니다.
        logger.error(f"Error dispatching Celery task: {e}", exc_info=True) # 에러 로그를 기록합니다.
        raise HTTPException(status_code=500, detail=f"Failed to dispatch task: {e}") # 500 상태 코드와 함께 HTTPException을 발생시킵니다.