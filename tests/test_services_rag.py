# tests/test_services_rag.py
# 이 파일은 backend/app/services/rag_learning_service.py의 서비스 로직을 테스트합니다.
# '데이터는 힘이다!'는 일타 강사의 철학처럼, RAG 시스템의 핵심 기능을 검증합니다.

import pytest # pytest 프레임워크 임포트
from unittest.mock import AsyncMock, patch, MagicMock # 비동기 함수 모킹을 위한 AsyncMock, patch, MagicMock 임포트
from app.services.rag_learning_service import RAGLearningService # 테스트할 RAGLearningService 임포트
from app.db.models import Document, User # Document 및 User 모델 임포트 (테스트용)
from app.schemas.documents import DocumentCreate # Document 생성 스키마 임포트
from fastapi import UploadFile # UploadFile 타입 힌트용 임포트
import io # 파일 입출력 처리를 위한 임포트

# 1. save_content 메서드 테스트
@pytest.mark.asyncio # 비동기 테스트 함수를 위한 마크
async def test_save_content(db_session):
    """
    save_content 메서드가 ChromaDB에 올바르게 문서를 저장하고 DB에 기록하는지 테스트합니다.
    - ChromaDB 클라이언트의 get_or_create_collection 및 add 메서드가 호출되는지 확인합니다.
    - Document 모델이 DB에 저장되는지 확인합니다.
    """
    user_id = "1"
    content = "This is a test document content."
    
    # ChromaDB 클라이언트를 Mocking합니다.
    with patch("chromadb.Client", autospec=True) as MockChromaClient:
        mock_collection = MagicMock() # 컬렉션 객체 Mock
        MockChromaClient.return_value.get_or_create_collection.return_value = mock_collection
        
        rag_service = RAGLearningService(db_session) # RAGLearningService 인스턴스 생성
        await rag_service.save_content(user_id, content) # save_content 메서드 호출
        
        # ChromaDB 관련 메서드들이 호출되었는지 확인
        MockChromaClient.return_value.get_or_create_collection.assert_called_once()
        mock_collection.add.assert_called_once()
        
        # DB에 Document가 생성되었는지 확인
        document = db_session.query(Document).filter_by(user_id=int(user_id), content=content).first()
        assert document is not None
        assert document.title == content[:50] # 제목이 content의 앞부분으로 설정되었는지 확인
        assert document.chroma_collection_name is not None

# 2. retrieve_related_documents 메서드 테스트
@pytest.mark.asyncio
async def test_retrieve_related_documents(db_session):
    """
    retrieve_related_documents 메서드가 ChromaDB에서 관련 문서를 올바르게 검색하는지 테스트합니다.
    - ChromaDB 클라이언트의 get_or_create_collection 및 query 메서드가 호출되는지 확인합니다.
    """
    user_id = "1"
    query_text = "test query"
    
    # ChromaDB 클라이언트를 Mocking합니다.
    with patch("chromadb.Client", autospec=True) as MockChromaClient:
        mock_collection = MagicMock()
        # query 메서드의 반환 값 Mock 설정
        mock_collection.query.return_value = {
            'ids': [['doc1']],
            'distances': [[0.1]],
            'metadatas': [[{'document_id': '100'}]],
            'embeddings': None,
            'documents': [['Retrieved document content']]
        }
        MockChromaClient.return_value.get_or_create_collection.return_value = mock_collection
        
        rag_service = RAGLearningService(db_session)
        results = await rag_service.retrieve_related_documents(user_id, query_text)
        
        # ChromaDB 관련 메서드들이 호출되었는지 확인
        MockChromaClient.return_value.get_or_create_collection.assert_called_once()
        mock_collection.query.assert_called_once()
        
        assert len(results) == 1
        assert results[0].page_content == "Retrieved document content"

# 3. process_pdf 메서드 테스트
@pytest.mark.asyncio
async def test_process_pdf(db_session):
    """
    process_pdf 메서드가 PDF 파일에서 텍스트를 추출하고 save_content를 호출하는지 테스트합니다.
    - pdf_to_text 함수가 Mocking되었는지 확인합니다.
    - save_content 메서드가 추출된 텍스트와 함께 호출되는지 확인합니다.
    """
    user_id = "1"
    test_pdf_content = b"This is a dummy PDF content." # 실제 PDF 내용이 아님
    
    # FastAPI의 UploadFile 객체 Mock
    mock_upload_file = MagicMock(spec=UploadFile)
    mock_upload_file.file = io.BytesIO(test_pdf_content) # file 속성에 BytesIO 객체 할당
    mock_upload_file.filename = "test.pdf"
    
    # pdf_to_text 함수를 Mocking합니다.
    with patch("app.services.rag_learning_service.pdf_to_text", new_callable=AsyncMock) as mock_pdf_to_text:
        mock_pdf_to_text.return_value = "Extracted text from PDF."
        
        # save_content 메서드 호출을 Mocking합니다.
        with patch.object(RAGLearningService, 'save_content', new_callable=AsyncMock) as mock_save_content:
            rag_service = RAGLearningService(db_session)
            extracted_text = await rag_service.process_pdf(user_id, mock_upload_file)
            
            assert extracted_text == "Extracted text from PDF."
            
            # pdf_to_text 함수가 호출되었는지 확인
            mock_pdf_to_text.assert_called_once()
            # save_content 메서드가 추출된 텍스트와 함께 호출되었는지 확인
            mock_save_content.assert_called_once_with(user_id, "Extracted text from PDF.")
