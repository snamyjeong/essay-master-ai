# tests/test_api_learning.py
# 이 파일은 backend/app/api/v1/endpoints/learning.py에 정의된 API 엔드포인트를 테스트합니다.
# '모든 길은 로마로 통한다!'는 일타 강사의 철학처럼, API의 모든 흐름을 검증합니다.

from fastapi.testclient import TestClient # FastAPI 테스트 클라이언트 임포트
from unittest.mock import AsyncMock, patch # 비동기 함수 모킹을 위한 AsyncMock과 patch 임포트
import pytest # pytest 프레임워크 임포트
from app.schemas.essay_generation import EssayEvaluationResponse # 논술 평가 응답 스키마 임포트
from app.db.models import User # 사용자 모델 임포트 (mock_user에서 사용)

# 1. /learning/generate-content 엔드포인트 테스트
def test_generate_learning_content(client: TestClient, mock_rag_service: AsyncMock, mock_llm: AsyncMock, mock_user: User):
    """
    학습 내용 생성 API 엔드포인트의 정상 동작을 테스트합니다.
    - RAG 서비스의 save_content가 호출되는지 확인합니다.
    - QuizGenerationService의 generate_learning_content가 호출되는지 확인합니다.
    - 올바른 응답 형식을 반환하는지 확인합니다.
    """
    # Mock 객체의 비동기 메서드 리턴 값을 설정합니다.
    # QuizGenerationService.generate_learning_content의 반환 값 Mock
    mock_llm.ainvoke.return_value = "Mocked LLM Response" # 일반 LLM 응답 Mock
    
    # QuizGenerationService.full_generation_chain.ainvoke의 반환 값을 명시적으로 Mock
    with patch("app.services.quiz_service.QuizGenerationService.full_generation_chain.ainvoke", new_callable=AsyncMock) as mock_full_chain_ainvoke:
        mock_full_chain_ainvoke.return_value = {
            "keyword_quizzes": "Mocked Keyword Quizzes",
            "essay_quizzes": "Mocked Essay Quizzes",
            "typing_text": "Mocked Typing Text",
            "mentoring": "Mocked Mentoring"
        }

        content = "Test learning content for generation." # 테스트용 학습 내용
        response = client.post(
            "/api/v1/learning/generate-content",
            json={"content": content}
        )

        assert response.status_code == 200 # HTTP 상태 코드 200 (OK) 확인
        data = response.json()
        assert data["keyword_quizzes"] == "Mocked Keyword Quizzes" # Mock된 퀴즈 내용 확인
        assert data["mentoring"] == "Mocked Mentoring" # Mock된 멘토링 내용 확인
        
        # RAG 서비스의 save_content 메서드가 올바른 인자로 호출되었는지 확인
        mock_rag_service.save_content.assert_called_once_with(str(mock_user.id), content)

# 2. /learning/upload-pdf 엔드포인트 테스트
@patch('app.services.rag_learning_service.rag_learning_service.process_pdf', new_callable=AsyncMock)
@patch('app.services.quiz_service.QuizGenerationService.generate_learning_content', new_callable=AsyncMock)
def test_upload_pdf(mock_generate_learning_content: AsyncMock, mock_process_pdf: AsyncMock, client: TestClient, mock_user: User):
    """
    PDF 업로드 API 엔드포인트의 정상 동작을 테스트합니다.
    - RAG 서비스의 process_pdf가 호출되는지 확인합니다.
    - QuizGenerationService의 generate_learning_content가 호출되는지 확인합니다.
    - 올바른 응답 형식을 반환하는지 확인합니다.
    """
    # Mock 객체의 반환 값 설정
    mock_process_pdf.return_value = "Extracted text from PDF."
    mock_generate_learning_content.return_value = {
        "keyword_quizzes": "PDF Keyword Quizzes",
        "essay_quizzes": "PDF Essay Quizzes",
        "typing_text": "PDF Typing Text",
        "mentoring": "PDF Mentoring"
    }

    # 테스트용 더미 PDF 파일 생성
    test_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj"
    files = {"file": ("test.pdf", test_pdf_content, "application/pdf")}

    response = client.post(
        "/api/v1/learning/upload-pdf",
        files=files
    )

    assert response.status_code == 200 # HTTP 상태 코드 200 (OK) 확인
    data = response.json()
    assert data["keyword_quizzes"] == "PDF Keyword Quizzes"
    assert data["mentoring"] == "PDF Mentoring"
    
    # process_pdf와 generate_learning_content가 올바른 인자로 호출되었는지 확인
    mock_process_pdf.assert_called_once()
    mock_generate_learning_content.assert_called_once_with("Extracted text from PDF.")

# 3. /learning/evaluate-essay 엔드포인트 테스트
@patch('app.services.quiz_service.QuizGenerationService.evaluate_essay_answer_with_rag', new_callable=AsyncMock)
def test_evaluate_essay(mock_evaluate_essay_answer_with_rag: AsyncMock, client: TestClient, mock_user: User):
    """
    심화 논술 평가 API 엔드포인트의 정상 동작을 테스트합니다.
    - QuizGenerationService의 evaluate_essay_answer_with_rag가 호출되는지 확인합니다.
    - 올바른 응답 형식을 반환하는지 확인합니다.
    """
    # Mock 객체의 반환 값 설정 (EssayEvaluationResponse 스키마에 맞는 JSON)
    mock_evaluate_essay_answer_with_rag.return_value = {
        "overall_feedback": "전반적으로 훌륭한 답변입니다.",
        "factual_accuracy": {"score": 90, "feedback": "참고 자료의 핵심 내용을 잘 반영했습니다."}, 
        "logical_coherence": {"score": 85, "feedback": "논리 전개가 비교적 일관됩니다."}, 
        "expression_readability": {"score": 95, "feedback": "문장 구성과 가독성이 매우 뛰어납니다."}, 
        "overall_score": 90
    }

    question = "인공지능의 미래 사회 영향에 대해 논술하시오."
    answer = "인공지능은 사회 전반에 걸쳐 긍정적 및 부정적 영향을 미칠 것입니다..."

    response = client.post(
        "/api/v1/learning/evaluate-essay",
        json={"question": question, "answer": answer}
    )

    assert response.status_code == 200 # HTTP 상태 코드 200 (OK) 확인
    data = response.json()
    # 응답 데이터가 EssayEvaluationResponse 스키마와 일치하는지 Pydantic을 통해 검증 (선택 사항)
    EssayEvaluationResponse(**data)
    assert data["overall_feedback"] == "전반적으로 훌륭한 답변입니다."
    assert data["overall_score"] == 90
    
    # evaluate_essay_answer_with_rag 메서드가 올바른 인자로 호출되었는지 확인
    mock_evaluate_essay_answer_with_rag.assert_called_once_with(
        user_id=str(mock_user.id),
        question=question,
        user_answer=answer
    )
