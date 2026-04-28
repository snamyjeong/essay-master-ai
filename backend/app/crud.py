# CRUD (Create, Read, Update, Delete) 작업을 위한 유틸리티 함수들을 정의합니다.
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

# SQLAlchemy 모델을 임포트합니다.
from backend.app.db.base import Base
from backend.app.db.models import User

# Pydantic 스키마를 임포트합니다.
from backend.app.schemas import UserCreate, UserUpdate

# 보안 유틸리티 함수를 임포트합니다.
from backend.app.core.security import get_password_hash

# SQLAlchemy 모델 타입을 위한 제네릭 타입 변수입니다.
ModelType = TypeVar("ModelType", bound=Base)

# Pydantic 스키마를 위한 제네릭 타입 변수입니다.
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# CRUDBase 클래스: 모든 CRUD 클래스의 기본 기능을 제공합니다.
class CRUDBase(
    ModelType,
    CreateSchemaType,
    UpdateSchemaType
):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD 객체와 SQLAlchemy 모델을 연결합니다.
        :param model: SQLAlchemy 모델 클래스입니다.
        """
        self.model = model

    # ID로 단일 객체를 조회합니다.
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    # 여러 객체를 조회합니다.
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    # 객체를 생성합니다.
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # 객체를 업데이트합니다.
    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) # Pydantic V2
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # 객체를 삭제합니다.
    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

# CRUDUser 클래스: User 모델에 특화된 CRUD 작업을 처리합니다.
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # 새로운 사용자를 생성하고 비밀번호를 해시하여 저장합니다.
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        hashed_password = get_password_hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # 이메일로 사용자를 조회합니다.
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    # 기존 사용자의 정보를 업데이트합니다. 비밀번호가 있을 경우 해시하여 저장합니다.
    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) # Pydantic V2
        if "password" in update_data and update_data["password"] is not None:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    # 활성화된 슈퍼유저인지를 확인합니다.
    def is_superuser(self, user: User) -> bool:
        return user.is_superuser and user.is_active


# user: CRUDUser 클래스의 인스턴스를 생성하여 다른 모듈에서 직접 사용할 수 있도록 합니다.
# 이렇게 하면 `crud.user.create()`, `crud.user.get_by_email()` 등으로 호출할 수 있습니다.
user = CRUDUser(User)