# backend/app/schemas/documents.py
# 문서 관련 API 요청 및 응답 데이터를 정의하는 Pydantic 스키마 파일입니다.
# '정확한 기록만이 정확한 분석을 낳는다'는 일타 강사의 철학에 따라, 데이터의 무결성을 보장합니다.

from pydantic import BaseModel, Field # Pydantic의 기본 모델과 필드 유효성 검사를 위한 Field를 임포트합니다.
from datetime import datetime # 날짜/시간 타입 임포트
from typing import Optional # 선택적 필드를 위한 Optional 임포트

# 1. DocumentBase: 문서의 기본 속성을 정의하는 Pydantic 모델입니다.
class DocumentBase(BaseModel):
    """문서의 기본 속성을 정의하는 Pydantic 모델입니다."""
    user_id: int = Field(..., description="문서를 업로드한 사용자 ID") # 문서를 업로드한 사용자 ID
    title: str = Field(..., description="문서 제목") # 문서 제목
    content: str = Field(..., description="문서의 전체 내용") # 문서의 전체 내용

# 2. DocumentCreate: 새 문서를 생성할 때 사용되는 모델입니다.
class DocumentCreate(DocumentBase):
    """새 문서를 생성할 때 사용되는 모델입니다."""
    pass # DocumentBase의 필드를 그대로 사용하며 추가적인 필드는 없습니다.

# 3. DocumentResponse: ORM 모델로부터 조회된 문서 정보를 클라이언트에 응답할 때 사용되는 모델입니다.
class DocumentResponse(DocumentBase):
    """
    문서 정보를 클라이언트에 응답할 때 사용되는 모델입니다. (ORM 호환)
    """
    id: int = Field(..., description="문서 고유 ID") # 문서 고유 ID
    uploaded_at: datetime = Field(..., description="업로드 시각") # 업로드 시각
    chroma_collection_name: str = Field(..., description="ChromaDB 컬렉션 이름") # ChromaDB 컬렉션 이름 (내부 사용을 위해 노출)

    class Config:
        from_attributes = True # SQLAlchemy ORM 모델과의 호환성을 위한 설정

# 4. DocumentUploadResponse: 파일 업로드 API의 응답 데이터를 정의하는 모델입니다.
class DocumentUploadResponse(BaseModel):
    """
    문서 업로드 API의 응답 데이터를 정의하는 모델입니다. (API 응답 전용)
    """
    id: str = Field(..., example="doc_123", description="처리된 문서의 고유 ID (UUID)") # 문서의 고유 ID
    filename: str = Field(..., example="my_document.pdf", description="업로드된 파일명") # 원본 파일명
    status: str = Field(..., example="success", description="문서 처리 상태 (예: success, failed)") # 처리 상태
    message: str = Field(..., example="문서가 성공적으로 업로드 및 처리되었습니다.", description="처리 결과 메시지") # 상세 메시지
