# backend/app/api/v1/endpoints/documents.py
import uuid # 고유 ID 생성을 위한 uuid 모듈 임포트
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status # FastAPI 관련 모듈 임포트
from sqlalchemy.ext.asyncio import AsyncSession # 비동기 SQLAlchemy 세션을 위한 임포트
from backend.app.api import deps # 의존성 주입 관련 모듈 (데이터베이스 세션 등)
from backend.app.schemas.documents import DocumentResponse, DocumentUploadResponse # 문서 관련 Pydantic 스키마 임포트 (DocumentUploadResponse 추가 임포트)
from backend.app.services.document_parser import document_parser # 문서 파싱 서비스 임포트
from backend.app.services.rag_system import rag_system # RAG 시스템 서비스 임포트
from backend.app.services.learning_archive_service import LearningArchiveService # 학습 아카이브 서비스 임포트
from backend.app.db.models import User # 사용자 모델 임포트 (현재 사용자 정보 주입용)

# APIRouter 인스턴스를 생성하여 문서 관련 경로를 관리합니다.
router = APIRouter()

# 문서 업로드 엔드포인트
# `response_model`: 응답 데이터의 형식을 DocumentUploadResponse 스키마에 맞춥니다.
# `status_code`: 성공 시 HTTP 201 Created 응답 코드를 반환합니다.
@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...), # 업로드된 파일을 받습니다.
    db: AsyncSession = Depends(deps.get_db), # 의존성 주입을 통해 비동기 데이터베이스 세션을 가져옵니다.
    current_user: User = Depends(deps.get_current_user) # 현재 로그인된 사용자 정보 주입
):
    # 파일 확장자를 소문자로 변환하여 가져옵니다.
    file_extension = file.filename.split(".")[-1].lower() if file.filename else "txt"
    parsed_content = ""
    learning_archive_service = LearningArchiveService(db) # LearningArchiveService 인스턴스 생성

    try:
        # 업로드된 파일의 내용을 비동기로 읽어옵니다.
        file_content = await file.read()

        # 파일 확장자에 따라 적절한 파싱 메서드를 호출합니다.
        if file_extension == "pdf":
            parsed_content = await document_parser.parse_pdf(file_content)
        elif file_extension in ["txt", "md", "csv"]: # 일반 텍스트 파일 형식
            parsed_content = await document_parser.parse_text(file_content)
        else:
            # 지원하지 않는 파일 형식인 경우 400 에러 발생
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 형식입니다: {file_extension}"
            )

        # 파싱된 내용이 없으면 오류 발생
        if not parsed_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파싱된 내용이 없습니다. 파일이 비어 있거나 손상되었을 수 있습니다."
            )

        # 1. SQL DB에 Document 기록 생성 (chroma_collection_name은 RAG 시스템에서 생성 후 업데이트)
        new_db_document = learning_archive_service.add_document(
            user_id=current_user.id, # 현재 사용자의 ID를 문서 소유자로 지정
            title=file.filename or "Untitled Document", # 파일 이름이 없으면 "Untitled Document"로 기본값 설정
            content=parsed_content, # 파싱된 문서 내용
            # chroma_collection_name은 LearningArchiveService.add_document에서 직접 설정되지 않으므로, 이 단계에서는 생략
        )
        
        # 2. ChromaDB 컬렉션 이름 생성 및 SQL DB에 업데이트
        # RAG 시스템이 사용할 고유 컬렉션 이름. user_id와 SQL DB의 document.id를 조합합니다.
        chroma_collection_name = f"user_{current_user.id}_doc_{new_db_document.id}"
        learning_archive_service.update_document_collection_name(
            document_id=new_db_document.id, # 새로 생성된 SQL DB 문서의 ID
            collection_name=chroma_collection_name # 생성된 ChromaDB 컬렉션 이름
        )

        # 3. 파싱된 내용을 RAG 시스템에 추가
        await rag_system.add_documents(
            collection_name=chroma_collection_name, # 새로운 ChromaDB 컬렉션 이름 사용
            documents=[parsed_content], # 파싱된 문서 내용
            metadatas=[{"user_id": str(current_user.id), "document_id": new_db_document.id, "source_type": file_extension}] # 메타데이터에 SQL DB ID 포함
        )

        # 성공 응답 반환 (DocumentUploadResponse 사용)
        return DocumentUploadResponse(
            id=str(new_db_document.id), # SQL DB ID를 문자열로 변환하여 반환
            filename=file.filename, # 업로드된 파일명
            status="success", # 처리 상태
            message="문서가 성공적으로 업로드 및 처리되었습니다." # 결과 메시지
        )

    except HTTPException as e:
        raise e # 이미 HTTP 예외인 경우 그대로 다시 발생시킵니다.
    except ValueError as e:
        # 파싱 서비스에서 발생한 ValueError를 HTTP 400 예외로 변환합니다.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # 그 외 예상치 못한 오류 발생 시 HTTP 500 예외를 발생시킵니다.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"문서 처리 중 서버 오류 발생: {e}")
