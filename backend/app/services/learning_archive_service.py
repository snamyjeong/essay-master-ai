from sqlalchemy.ext.asyncio import AsyncSession # 비동기 SQLAlchemy 세션 임포트
from sqlalchemy import select, desc # 비동기 쿼리 구성을 위한 select, 정렬을 위한 desc 임포트
from sqlalchemy.orm import joinedload # 관계형 로딩을 위한 joinedload 임포트
from app.db.models import Document, QuizResult, TypingRecord # 학습 이력 모델 임포트
from app.core.cache import cache_service # Redis 캐싱 서비스를 임포트합니다.
import json # 객체를 JSON 문자열로 직렬화/역직렬화하기 위한 임포트

class LearningArchiveService:
    """
    사용자의 학습 이력(문서 업로드, 퀴즈 결과, 타자 연습 기록 등)을 관리하는 서비스입니다。
    """
    def __init__(self, db: AsyncSession): # DB 세션 타입을 AsyncSession으로 변경
        self.db = db # 데이터베이스 세션 초기화
    
    async def add_document(self, user_id: int, title: str, content: str, chroma_collection_name: str) -> Document:
        """
        새로운 학습 문서를 데이터베이스에 추가합니다.
        '지식의 보고'를 채우는 첫 걸음입니다.
        """
        new_document = Document(
            user_id=user_id, # 문서를 업로드한 사용자 ID
            title=title, # 문서 제목
            content=content, # 파싱된 문서 내용
            chroma_collection_name=chroma_collection_name # ChromaDB 컬렉션 이름 저장
        )
        self.db.add(new_document) # 새 문서 객체를 세션에 추가
        await self.db.commit() # 비동기 트랜잭션 커밋
        await self.db.refresh(new_document) # 객체 새로고침 (DB로부터 최신 상태 반영)
        await cache_service.delete(f"user_history:{user_id}") # 문서 추가 시 캐시 무효화
        return new_document # 새로 생성된 문서 반환

    async def add_quiz_result(self, user_id: int, document_id: int, quiz_type: str, 
                        question_text: str, user_answer: str, correct_answer: str, 
                        score: int | None = None) -> QuizResult:
        """
        사용자의 퀴즈 풀이 결과를 데이터베이스에 저장합니다。
        '오답 노트는 성공의 지름길'이라는 원칙에 따라, 모든 시도와 결과를 기록합니다。
        """
        if score is not None and (score < 0 or score > 100): # 점수 유효성 검사
            raise ValueError("점수는 0에서 100 사이여야 합니다.")
        
        new_quiz_result = QuizResult(
            user_id=user_id, # 퀴즈를 푼 사용자 ID
            document_id=document_id, # 관련 문서 ID
            quiz_type=quiz_type, # 퀴즈 유형
            question_text=question_text, # 제시된 퀴즈 질문 내용
            user_answer=user_answer, # 사용자가 제출한 답변
            correct_answer=correct_answer, # 퀴즈의 정답 또는 모범 답안
            score=score # 해당 퀴즈 질문에 대한 점수
        )
        self.db.add(new_quiz_result) # 새 퀴즈 결과 객체를 세션에 추가
        await self.db.commit() # 비동기 트랜잭션 커밋
        await self.db.refresh(new_quiz_result) # 객체 새로고침 (DB로부터 최신 상태 반영)
        await cache_service.delete(f"user_history:{user_id}") # 퀴즈 결과 추가 시 캐시 무효화
        return new_quiz_result # 새로 생성된 퀴즈 결과 반환

    async def add_typing_record(self, user_id: int, document_id: int, sentence_content: str, 
                          user_input: str, wpm: float, accuracy: float, 
                          difficulty: str | None = None) -> TypingRecord:
        """
        사용자의 타자 연습 기록을 데이터베이스에 저장합니다。
        '꾸준함이 실력을 만든다'는 일타 강사의 가르침처럼, 모든 연습 과정을 기록으로 남깁니다。
        """
        if wpm <= 0 or accuracy <= 0: # WPM 및 정확도 유효성 검사
            raise ValueError("WPM과 정확도는 0보다 커야 합니다.")
        
        new_record = TypingRecord(
            user_id=user_id, # 타자 연습을 한 사용자 ID
            document_id=document_id, # 관련 문서 ID
            sentence_content=sentence_content, # 타자 연습에 사용된 문장 내용
            user_input=user_input, # 사용자가 실제로 입력한 내용
            wpm=wpm, # 분당 단어 수
            accuracy=accuracy, # 타자 정확도
            difficulty=difficulty # 문장 난이도
        )
        self.db.add(new_record) # 새 타자 기록 객체를 세션에 추가
        await self.db.commit() # 비동기 트랜잭션 커밋
        await self.db.refresh(new_record) # 객체 새로고침 (DB로부터 최신 상태 반영)
        await cache_service.delete(f"user_history:{user_id}") # 타자 기록 추가 시 캐시 무효화
        return new_record # 새로 생성된 타자 기록 반환

    async def get_user_history(self, user_id: int):
        """
        특정 사용자의 모든 학습 이력(문서, 퀴즈 결과, 타자 기록)을 조회합니다.
        '성적표는 거짓말을 하지 않는다. 모든 기록은 너의 노력을 증명한다.'는 일타 강사의 좌우명처럼, 
        사용자의 모든 학습 발자취를 상세히 보여줍니다.
        """
        cache_key = f"user_history:{user_id}" # 사용자 ID 기반의 캐시 키 생성
        cached_data = await cache_service.get(cache_key) # 캐시에서 데이터 조회

        if cached_data: # 캐시된 데이터가 있다면
            # 캐시에서 가져온 데이터를 반환합니다.
            print(f"✅ Cache Hit for user_history:{user_id}") # 캐시 히트 로그
            # ORM 객체가 아닌 dict 형태로 저장되었으므로, 필요한 경우 Pydantic 모델로 변환하여 반환해야 할 수 있습니다.
            # 여기서는 JSON 직렬화/역직렬화 가능한 형태로 반환한다고 가정합니다.
            return cached_data

        print(f"❌ Cache Miss for user_history:{user_id}. Fetching from DB...") # 캐시 미스 로그
        # 사용자가 업로드한 문서들을 최신순으로 조회합니다. (비동기 쿼리)
        documents_result = await self.db.execute(select(Document).filter(Document.user_id == user_id).order_by(desc(Document.uploaded_at)))
        documents = documents_result.scalars().all()

        # 사용자의 퀴즈 결과들을 최신순으로 조회합니다. Document 정보와 함께 로드합니다. (비동기 쿼리)
        quiz_results_result = await self.db.execute(
            select(QuizResult)
            .filter(QuizResult.user_id == user_id)
            .options(joinedload(QuizResult.owner))
            .options(joinedload(QuizResult.document))
            .order_by(desc(QuizResult.attempted_at))
        )
        quiz_results = quiz_results_result.scalars().all()

        # 사용자의 타자 기록들을 최신순으로 조회합니다. Document 정보와 함께 로드합니다. (비동기 쿼리)
        typing_records_result = await self.db.execute(
            select(TypingRecord)
            .filter(TypingRecord.user_id == user_id)
            .options(joinedload(TypingRecord.owner))
            .options(joinedload(TypingRecord.document))
            .order_by(desc(TypingRecord.attempted_at))
        )
        typing_records = typing_records_result.scalars().all()
        
        history_data = {
            "documents": [doc.__dict__ for doc in documents], # ORM 객체를 딕셔너리로 변환하여 저장
            "quiz_results": [qr.__dict__ for qr in quiz_results], # ORM 객체를 딕셔너리로 변환하여 저장
            "typing_records": [tr.__dict__ for tr in typing_records] # ORM 객체를 딕셔너리로 변환하여 저장
        }

        await cache_service.set(cache_key, history_data, ex=60) # 60초(1분) 동안 캐시 저장
        
        return {
            "documents": documents, # 업로드된 문서 리스트
            "quiz_results": quiz_results, # 퀴즈 결과 리스트
            "typing_records": typing_records # 타자 기록 리스트
        }

    async def get_document_content_for_rag(self, document_id: int) -> str:
        """
        특정 document_id에 해당하는 문서의 내용을 반환합니다。
        이는 RAG 검색을 위해 ChromaDB에서 해당 문서 컬렉션 이름을 찾거나, 
        직접 문서 내용을 검색할 때 사용될 수 있습니다.
        '지식은 연결될 때 비로소 빛을 발한다'는 일타 강사의 지론처럼, 
        검색의 기초가 되는 원본 지문을 제공합니다。
        """
        document_result = await self.db.execute(select(Document).filter(Document.id == document_id))
        document = document_result.scalars().first()
        if not document: # 문서가 존재하지 않으면
            raise ValueError(f"Document with ID {document_id} not found.") # 에러 발생
        return document.content # 문서의 내용 반환

    async def get_document_by_collection_name(self, collection_name: str) -> Document:
        """
        ChromaDB 컬렉션 이름을 통해 해당 문서를 조회합니다。
        RAGManager가 특정 컬렉션에 대한 검색을 수행할 때, 원본 문서 정보를 다시 가져오기 위함입니다。
        """
        document_result = await self.db.execute(select(Document).filter(Document.chroma_collection_name == collection_name))
        document = document_result.scalars().first()
        if not document:
            raise ValueError(f"Document with collection name {collection_name} not found.")
        return document

    async def get_document_by_id(self, document_id: int) -> Document:
        """
        문서 ID를 통해 해당 문서를 조회합니다。
        """
        document_result = await self.db.execute(select(Document).filter(Document.id == document_id))
        document = document_result.scalars().first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        return document

    async def update_document_collection_name(self, document_id: int, collection_name: str) -> Document:
        """
        문서의 ChromaDB 컬렉션 이름을 업데이트합니다.
        문서 업로드 후 RAGManager에서 컬렉션 이름을 생성하면 이 함수를 통해 DB에 반영합니다.
        """
        document = await self.get_document_by_id(document_id) # 문서 ID로 문서 조회 (비동기 호출)
        document.chroma_collection_name = collection_name # 컬렉션 이름 업데이트
        await self.db.commit() # 비동기 트랜잭션 커밋
        await self.db.refresh(document) # 객체 새로고침 (DB로부터 최신 상태 반영)
        await cache_service.delete(f"user_history:{document.user_id}") # 관련 유저의 캐시 무효화
        return document # 업데이트된 문서 객체 반환