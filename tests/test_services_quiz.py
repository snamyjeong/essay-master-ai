# tests/test_services_quiz.py
# 이 파일은 backend/app/services/quiz_service.py의 서비스 로직을 테스트합니다.
# '핵심을 꿰뚫는 분석만이 진짜 실력이다!'는 일타 강사의 철학처럼, 서비스의 본질적인 기능을 검증합니다.

import pytest # pytest 프레임워크 임포트
from unittest.mock import AsyncMock, patch # 비동기 함수 모킹을 위한 AsyncMock과 patch 임포트
from app.services.quiz_service import QuizGenerationService # 테스트할 QuizGenerationService 임포트
from app.db.models import User # 사용자 모델 임포트 (RAG 서비스 Mock에서 사용)
from app.services.rag_learning_service import RAGLearningService # RAG 서비스 임포트
from fastapi import HTTPException # HTTPException 임포트 (예외 테스트용)
import json # JSON 파싱 및 생성을 위한 임포트

# 1. QuizGenerationService.generate_learning_content 메서드 테스트
@pytest.mark.asyncio # 비동기 테스트 함수를 위한 마크
async def test_generate_learning_content_service(mock_llm: AsyncMock, db_session):
    """
    generate_learning_content 메서드가 올바른 형식의 응답을 생성하는지 테스트합니다.
    - LLM 호출이 Mocking되었는지 확인합니다.
    - 반환된 데이터 구조가 예상과 일치하는지 확인합니다.
    """
    # LLM의 ainvoke 메서드가 반환할 Mock 값 설정 (RunnableParallel의 각 체인 응답)
    mock_llm.ainvoke.side_effect = [
        "Mocked Keyword Quizzes",
        "Mocked Essay Quizzes",
        "Mocked Typing Text",
        "Mocked Mentoring"
    ]

    quiz_service = QuizGenerationService(db_session) # QuizGenerationService 인스턴스 생성
    content = "Test content for quiz generation." # 테스트용 학습 내용
    
    # generate_learning_content 메서드 호출
    result = await quiz_service.generate_learning_content(content)

    # 결과 확인
    assert isinstance(result, dict) # 결과가 딕셔너리 타입인지 확인
    assert "keyword_quizzes" in result
    assert "essay_quizzes" in result
    assert "typing_text" in result
    assert "mentoring" in result
    assert result["keyword_quizzes"] == "Mocked Keyword Quizzes"
    assert result["mentoring"] == "Mocked Mentoring"
    
    # LLM의 ainvoke 메서드가 각 프롬프트에 대해 호출되었는지 확인
    assert mock_llm.ainvoke.call_count == 4

# 2. QuizGenerationService.evaluate_essay_answer_with_rag 메서드 테스트
@pytest.mark.asyncio
async def test_evaluate_essay_answer_with_rag_service_success(mock_llm: AsyncMock, mock_rag_service: AsyncMock, db_session, mock_user: User):
    """
    evaluate_essay_answer_with_rag 메서드가 성공적으로 논술 평가를 수행하는지 테스트합니다.
    - RAG 서비스의 문서 검색이 Mocking되었는지 확인합니다.
    - LLM의 JSON 응답이 올바르게 파싱되는지 확인합니다.
    """
    user_id = str(mock_user.id)
    question = "Test Essay Question?"
    user_answer = "Test Essay Answer."
    
    # RAG 서비스의 retrieve_related_documents 메서드 Mock
    mock_rag_service.retrieve_related_documents.return_value = [
        AsyncMock(page_content="Mocked RAG Context 1"),
        AsyncMock(page_content="Mocked RAG Context 2")
    ]

    # LLM의 ainvoke 메서드가 반환할 JSON 응답 Mock
    mock_llm.ainvoke.return_value = json.dumps({
        "overall_feedback": "Excellent work!",
        "factual_accuracy": {"score": 90, "feedback": "Accurate."}, 
        "logical_coherence": {"score": 85, "feedback": "Coherent."}, 
        "expression_readability": {"score": 95, "feedback": "Readable."}, 
        "overall_score": 90
    })

    quiz_service = QuizGenerationService(db_session)
    result = await quiz_service.evaluate_essay_answer_with_rag(user_id, question, user_answer)

    assert isinstance(result, dict) # 결과가 딕셔너리 타입인지 확인
    assert result["overall_score"] == 90
    assert "factual_accuracy" in result
    assert mock_rag_service.retrieve_related_documents.called_once_with(user_id, question) # RAG 서비스 호출 확인
    # LLM 호출 시 올바른 context, question, answer가 전달되었는지 확인 (부분 문자열 매칭)
    mock_llm.ainvoke.assert_called_once()
    call_args = mock_llm.ainvoke.call_args[0][0]
    assert "Mocked RAG Context 1\n\nMocked RAG Context 2" in call_args["context"]
    assert question in call_args["question"]
    assert user_answer in call_args["answer"]

@pytest.mark.asyncio
async def test_evaluate_essay_answer_with_rag_service_json_error(mock_llm: AsyncMock, mock_rag_service: AsyncMock, db_session, mock_user: User):
    """
    evaluate_essay_answer_with_rag 메서드에서 LLM의 JSON 응답 파싱 실패 시 예외를 올바르게 처리하는지 테스트합니다.
    """
    user_id = str(mock_user.id)
    question = "Test Question"
    user_answer = "Test Answer"
    
    mock_rag_service.retrieve_related_documents.return_value = [] # 빈 문서 반환
    mock_llm.ainvoke.return_value = "This is not valid JSON." # 유효하지 않은 JSON 응답 Mock

    quiz_service = QuizGenerationService(db_session)
    
    # HTTPException이 발생하고 상세 메시지가 일치하는지 확인
    with pytest.raises(HTTPException) as exc_info:
        await quiz_service.evaluate_essay_answer_with_rag(user_id, question, user_answer)
    assert exc_info.value.status_code == 500
    assert "AI 평가 결과 파싱 오류" in exc_info.value.detail
