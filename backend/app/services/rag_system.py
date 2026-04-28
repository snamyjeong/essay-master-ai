import chromadb # 벡터 데이터베이스인 ChromaDB 제어용 모듈
import os # 파일 경로 및 환경 변수 접근용 모듈
import json # JSON 데이터 파싱용 모듈
import asyncio # 비동기 처리용 모듈
from typing import List, Dict, Optional, Any # 타입 힌트
from datetime import datetime # 시각 기록용 모듈

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma 

from dotenv import load_dotenv 
load_dotenv() 

# from app.core.config import settings # [제거] 설정값을 가져오기 위해 settings 임포트 (다시 PersistentClient 사용하므로 필요 없음)

GOOGLE_API_KEY = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()

class RAGSystem:
    """
    제미나이 엔진과 벡터 DB를 결합하여 지식 기반 분석을 수행하는 싱글톤 클래스입니다.
    """
    _instance = None 

    def __new__(cls):
        if cls._instance is None: 
            cls._instance = super(RAGSystem, cls).__new__(cls) 
        return cls._instance 

    def __init__(self):
        if hasattr(self, 'initialized'): 
            return 
            
        # [복원] 로컬 ChromaDB 데이터 경로 관련 코드 복원 (PersistentClient 사용)
        self.chroma_data_path = os.path.join(os.getcwd(), "chroma_data") 
        os.makedirs(self.chroma_data_path, exist_ok=True) 
        
        # [복원] ChromaDB 클라이언트를 PersistentClient로 변경하여 로컬 스토리지 사용
        self.client = chromadb.PersistentClient(path=self.chroma_data_path)
        
        self.evaluation_results = {}

        if GOOGLE_API_KEY: 
            # 1. 채팅 모델 설정 (현재 가장 안정적인 1.5-flash 사용)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                api_key=GOOGLE_API_KEY
            )
            
            # 2. [교정] 임베딩 모델 설정을 최신 규격으로 변경합니다.
            # 수석님, 'models/embedding-001'은 구형이라 'models/text-embedding-004'로 교체해야 합니다.
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-2", # 최신 임베딩 모델 부품 번호
                google_api_key=GOOGLE_API_KEY, 
                task_type="retrieval_document" 
            )
        else: 
            self.llm = None
            self.embeddings = None 

        self.default_collection_name = "main_learning_collection" 
        self.vector_store = self._init_store(self.default_collection_name)
        self.initialized = True 

    def _init_store(self, collection_name: str):
        """ 주어진 이름으로 벡터 저장소 객체를 초기화합니다. """
        if self.embeddings: 
            return Chroma(
                client=self.client, 
                collection_name=collection_name, 
                embedding_function=self.embeddings
            )
        return None

    async def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict]):
        """ 지식 데이터를 벡터 DB에 적재합니다. """
        store = self._init_store(collection_name)
        if store:
            store.add_texts(texts=documents, metadatas=metadatas)
            print(f"📊 [{collection_name}] 지식 {len(documents)}건 적재 성공.")

    async def query_documents(self, collection_name: str, query_texts: List[str], n_results: int = 5) -> List[str]:
        """ 가장 유사한 지식을 검색해옵니다. """
        store = self._init_store(collection_name)
        if store:
            results = []
            for query in query_texts:
                search_res = store.similarity_search(query, k=n_results)
                results.extend([doc.page_content for doc in search_res])
            return results
        return []

    async def evaluate_essay_async(self, essay_id: int, content: str):
        """ 에세이 심층 분석 및 평가 로직입니다. """
        if not self.llm or not self.vector_store:
            return

        try:
            relevant_docs = self.vector_store.similarity_search(content, k=2)
            context = "\n".join([doc.page_content for doc in relevant_docs])

            prompt = f"에세이 분석 전문가로서 다음 내용을 평가하세요.\n참고지식: {context}\n분석대상: {content}\n형식: JSON {{\"score\": 점수, \"feedback\": \"한글 피드백\"}}"
            response = await self.llm.ainvoke(prompt)
            
            raw_text = response.content.strip().replace("```json", "").replace("```", "")
            result_data = json.loads(raw_text)

            self.evaluation_results[essay_id] = {
                "id": essay_id,
                "essay_id": essay_id,
                "score": result_data.get("score", 0),
                "feedback": result_data.get("feedback", "분석 완료"),
                "result_type": "evaluation",
                "created_at": datetime.now()
            }
        except Exception as e:
            print(f"RAG Evaluation Error: {e}")

rag_system = RAGSystem()