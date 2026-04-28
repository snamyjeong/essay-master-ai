# SQLAlchemy의 선언적(declarative) 베이스를 정의하는 파일입니다.
from typing import Any # Any 타입 힌트를 가져옵니다.

from sqlalchemy.ext.declarative import as_declarative, declared_attr # 선언적 베이스와 선언된 속성을 가져옵니다.
from sqlalchemy import Column, Integer # Column과 Integer 타입을 가져옵니다.


@as_declarative() # 이 클래스를 선언적 베이스로 사용하도록 지정합니다.
class Base:
    """SQLAlchemy 모델의 베이스 클래스입니다."""
    @declared_attr # 이 메서드를 클래스 속성으로 선언합니다.
    def __tablename__(cls) -> str:
        # 클래스 이름을 소문자로 변환하여 테이블 이름으로 사용합니다. (예: User -> user)
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True) # 모든 모델이 가질 기본 키 'id'를 정의합니다.
    __name__: str # 클래스 이름을 저장할 속성입니다.
    __abstract__ = True # 이 클래스는 직접 테이블로 매핑되지 않는 추상 클래스임을 나타냅니다.

    def __init__(self, **kwargs: Any) -> None:
        # 모델 인스턴스 초기화 시 키워드 인자를 사용하여 속성을 설정합니다.
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        # 모델 객체를 문자열로 표현할 때 사용합니다.
        # 예: <User(id=1, email='test@example.com')>
        attrs = ', '.join(f"{key}={getattr(self, key)!r}" for key in self.__table__.columns.keys())
        return f"<{self.__class__.__name__}({attrs})>"
