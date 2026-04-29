# -*- coding: utf-8 -*-
# SQLAlchemy 모델 정의 파일입니다.
# '데이터는 영원하다'는 일타 강사의 철학에 따라, 중요한 정보가 이 곳에 정의됩니다.

from sqlalchemy import Column, Integer, String, DateTime, func, Text, ForeignKey, Float, Boolean # SQLAlchemy 컬럼 및 타입
from sqlalchemy.orm import relationship, backref # 관계형 모델 설정을 위한 도구
from backend.app.db.base import Base # [수정] base.py에서 정의된 통합 Base 클래스를 임포트합니다.

# 에세이(Essay) 모델 정의
class Essay(Base):
    """사용자가 작성한 에세이 정보를 저장하는 모델입니다."""
    __tablename__ = "essays" 

    id = Column(Integer, primary_key=True, index=True) 
    title = Column(String, index=True, nullable=False) 
    content = Column(Text, nullable=False) 
    created_at = Column(DateTime, default=func.now()) 

    generations = relationship("GenerationResult", back_populates="essay", cascade="all, delete-orphan")

# 생성 결과(GenerationResult) 모델 정의
class GenerationResult(Base):
    """AI가 에세이에 대해 생성한 분석 데이터를 저장하는 모델입니다."""
    __tablename__ = "generation_results"

    id = Column(Integer, primary_key=True, index=True) 
    essay_id = Column(Integer, ForeignKey("essays.id"), nullable=False) 
    result_type = Column(String, nullable=False) 
    feedback = Column(Text, nullable=True) 
    score = Column(Float, nullable=True) 
    created_at = Column(DateTime, default=func.now()) 

    essay = relationship("Essay", back_populates="generations")

# 사용자(User) 모델 정의
class User(Base):
    """사용자 계정 및 멤버십 정보를 저장하는 모델입니다."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) 
    username = Column(String, unique=True, index=True, nullable=False) 
    email = Column(String, unique=True, index=True, nullable=False) 
    hashed_password = Column(String, nullable=False) 
    is_active = Column(Boolean, default=True) 
    is_superuser = Column(Boolean, default=False) # [중요] 관리자 권한 여부 필드명
    membership_type = Column(String, default="FREE", nullable=False) 
    membership_start_date = Column(DateTime, default=func.now(), nullable=False) 
    membership_end_date = Column(DateTime, nullable=True) 
    point_balance = Column(Integer, default=0) 
    created_at = Column(DateTime, default=func.now()) 
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 
    refresh_token = Column(String, nullable=True) 
    refresh_token_expires_at = Column(DateTime, nullable=True) 

    documents = relationship("Document", back_populates="owner", lazy="joined", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="owner", lazy="joined", cascade="all, delete-orphan")
    typing_records = relationship("TypingRecord", back_populates="owner", lazy="joined", cascade="all, delete-orphan")

# 문서(Document) 모델 정의
class Document(Base):
    """사용자가 업로드한 문서(PDF/Text 등) 정보를 저장하는 모델입니다."""
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    chroma_collection_name = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())
    
    owner = relationship("User", back_populates="documents")

# 퀴즈 결과(QuizResult) 모델 정의
class QuizResult(Base):
    """사용자의 퀴즈 풀이 결과를 저장하는 모델입니다."""
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    quiz_type = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=False)
    score = Column(Integer, nullable=True)
    attempted_at = Column(DateTime, default=func.now())
    
    owner = relationship("User", back_populates="quiz_results")
    document = relationship("Document", backref=backref("quiz_results", cascade="all, delete-orphan"))

# 타자 기록(TypingRecord) 모델 정의
class TypingRecord(Base):
    """사용자의 타자 연습 속도 및 정확도를 기록하는 모델입니다."""
    __tablename__ = "typing_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    sentence_content = Column(Text, nullable=False)
    user_input = Column(Text, nullable=False)
    wpm = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    difficulty = Column(String, nullable=True)
    attempted_at = Column(DateTime, default=func.now())
    
    owner = relationship("User", back_populates="typing_records")
    document = relationship("Document", backref=backref("typing_records", cascade="all, delete-orphan"))