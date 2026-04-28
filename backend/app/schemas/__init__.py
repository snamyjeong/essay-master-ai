# backend/app/schemas/__init__.py
# 이 파일은 FastAPI 애플리케이션의 Pydantic 스키마를 정의합니다.
# '규격은 곧 질서다!'라는 일타 강사의 철학처럼, 데이터의 입출력 형식을 엄격하게 관리합니다.

# auth.py 파일에서 정의된 모든 Pydantic 모델들을 외부로 노출(export)합니다.
from .auth import (
    UserBase, 
    UserCreate, 
    UserResponse, 
    Token, 
    TokenData
)

# documents.py 파일에서 정의된 모든 Pydantic 모델들을 외부로 노출(export)합니다.
from .documents import (
    DocumentBase,
    DocumentCreate,
    DocumentResponse, # ORM 호환 응답
    DocumentUploadResponse # 파일 업로드 API 응답
)

# essay_generation.py 파일에서 정의된 모든 Pydantic 모델들을 외부로 노출(export)합니다.
from .essay_generation import (
    EssayBase,
    EssayCreate,
    EssayUpdateRequest,
    EssayResponse,
    GenerationResultResponse,
    EssayEvaluationResponse # 추가: 심화 논술 평가 응답 스키마
)

# history.py 파일에서 정의된 모든 Pydantic 모델들을 외부로 노출(export)합니다.
from .history import (
    QuizResultBase,
    QuizResultCreate,
    QuizResultResponse,
    TypingRecordBase,
    TypingRecordCreate,
    TypingRecordResponse
)

# quizzes.py 파일에서 정의된 모든 Pydantic 모델들을 외부로 노출(export)합니다.
from .quizzes import (
    QuizType,
    QuizQuestion,
    QuizGenerationRequest
)

# typing.py 파일에서 정의된 모든 Pydantic 모델들을 외부로 노출(export)합니다.
from .typing import (
    TypingDifficulty,
    TypingSentence,
    TypingContentGenerationRequest
)
