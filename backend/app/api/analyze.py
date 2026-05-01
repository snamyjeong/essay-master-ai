from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from typing import Optional
from backend.app.models import AnalyzeRequest, AnalyzeResponse # 모델 임포트
from backend.app.utils import get_current_active_user # 인증 의존성 임포트

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/analyze", # /analyze 경로 접두사 사용
    tags=["Analysis"], # API 문서에 표시될 태그
)

# --- 텍스트 및 파일 분석 엔드포인트 ---
@router.post("/", response_model=AnalyzeResponse)
async def analyze_content(
    # 텍스트 내용은 폼 데이터로 받거나 JSON 본문으로 받을 수 있습니다.
    # 여기서는 간단히 JSON 본문을 사용하도록 모델을 정의했습니다.
    request: AnalyzeRequest,
    # 파일 업로드는 선택 사항입니다.
    file: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_active_user) # JWT 인증 필요
):
    """
    사용자가 제출한 텍스트 또는 파일을 분석하고 결과를 반환합니다.
    """
    analysis_results = []

    if request.text_content:
        analysis_results.append(f"텍스트 분석 결과: {request.text_content[:50]}...")

    if file:
        file_content = await file.read()
        # 실제 파일 처리 로직 (예: 파일 내용 파싱, AI 모델에 전달)
        analysis_results.append(f"파일 '{file.filename}' 분석 결과: {len(file_content)} 바이트 처리됨.")

    if not analysis_results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No content provided for analysis")

    return AnalyzeResponse(analysis_result="\n".join(analysis_results))
