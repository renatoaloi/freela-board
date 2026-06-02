from typing import Any, Generic, Optional, TypeVar

from sqlalchemy.orm import Session

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def list_all(self) -> list[ModelType]:
        return self.db.query(self.model).all()

    def update(self, id: str, **kwargs) -> Optional[ModelType]:
        obj = self.get_by_id(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: str) -> bool:
        obj = self.get_by_id(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
