import os # 파일 경로 및 환경 변수 관리를 위한 os 모듈 임포트
import fitz # PDF 파일 처리를 위한 PyMuPDF(fitz) 라이브러리 임포트
from typing import List, Dict, Optional # 타입 힌트를 위한 리스트, 딕셔너리, 옵셔널 임포트
from pydantic import BaseModel # 데이터 유효성 검사를 위한 Pydantic BaseModel 임포트
from fastapi import UploadFile # 파일 업로드 처리를 위한 FastAPI 클래스 임포트

# 기존 RAGSystem 임포트 (ChromaDB 클라이언트 및 벡터 저장소 관리)
# 수석님, 이 경로는 현재 프로젝트 구조에 맞게 설정되어 있습니다.
from app.services.rag_system import rag_system as core_rag_system 

# Pydantic 모델 정의: 학습 콘텐츠 인제스트 요청 바디
class LearningContentIngestRequest(BaseModel):
    user_id: str # 콘텐츠를 업로드하는 사용자 ID
    content: str # 학습 콘텐츠 텍스트
    source_type: str = "text_input" # 콘텐츠 원본 타입 (text_input, pdf 등)
    metadata: Optional[Dict] = None # 추가 메타데이터

class RAGLearningService:
    """
    RAG(Retrieval-Augmented Generation) 시스템을 활용하여
    학습 콘텐츠를 관리하고 검색하는 서비스입니다.
    """
    def __init__(self):
        # 기존 RAGSystem 인스턴스를 참조하여 벡터 저장소를 사용합니다.
        self.rag_system = core_rag_system 
        # 사용자별 컬렉션 구분을 위한 접두사 설정
        self.learning_collection_prefix = "user_learning_data_" 

    def _get_user_collection_name(self, user_id: str) -> str:
        """ 사용자 ID에 기반한 전용 ChromaDB 컬렉션 이름을 생성합니다. """
        return f"{self.learning_collection_prefix}{user_id}"

    async def save_content(self, user_id: str, content: str, source_type: str = "text_input") -> Dict[str, str]:
        """ 학습 콘텐츠를 벡터 DB에 저장합니다. """
        collection_name = self._get_user_collection_name(user_id)
        metadata = {"user_id": user_id, "source_type": source_type}
        
        # RAGSystem의 add_documents 메서드를 호출하여 문서 인덱싱 진행
        await self.rag_system.add_documents(
            collection_name=collection_name,
            documents=[content],
            metadatas=[metadata]
        )
        return {"status": "success", "message": "학습 콘텐츠가 벡터 DB에 저장되었습니다."}

    async def process_pdf(self, user_id: str, file: UploadFile) -> str:
        """
        [수석님 전용 핵심 로직] 
        업로드된 PDF 파일의 바이너리 데이터를 읽어 텍스트를 추출하고 RAG에 저장합니다.
        """
        try:
            # 업로드된 파일의 내용을 메모리로 읽어옵니다.
            pdf_bytes = await file.read()
            # PyMuPDF(fitz)를 사용하여 PDF 스트림을 엽니다.
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            full_text = "" # 추출된 전체 텍스트를 담을 변수
            for page in doc: # PDF의 모든 페이지를 순회합니다.
                full_text += page.get_text() # 페이지 내의 텍스트를 추출하여 결합합니다.
            
            # 추출된 텍스트를 RAG 시스템에 자동으로 저장합니다.
            await self.save_content(user_id, full_text, source_type="pdf")
            return full_text # 추출된 텍스트를 반환하여 퀴즈 생성에 활용합니다.
            
        except Exception as e:
            # 시스템 엔지니어링 관점에서 예외 상황을 로그로 남기고 상위로 던집니다.
            print(f"PDF 처리 중 오류 발생: {str(e)}")
            raise Exception(f"PDF 파싱 실패: {str(e)}")

# 서비스 인스턴스를 생성하여 라우터에서 쉽게 호출할 수 있게 합니다.
rag_learning_service = RAGLearningService()