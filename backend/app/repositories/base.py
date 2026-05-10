from typing import override

from sqlalchemy.orm import Session

from app.database import Base
from app.interfaces import IRepository


class BaseRepository[T: Base](IRepository[T]):
    """Base repository class that implements IRepository[T] and provides CRUD operations for SQLAlchemy models"""

    model: type[T]

    def __init__(self, db: Session):
        self._db = db

    @override
    def get(self, entity_id: int) -> T | None:
        return self._db.query(self.model).filter(self.model.id == entity_id).first()

    @override
    def get_all(self) -> list[T]:
        return self._db.query(self.model).all()

    @override
    def add(self, entity: T) -> T:
        self._db.add(entity)
        self._db.commit()
        self._db.refresh(entity)
        return entity

    @override
    def update(self, entity: T) -> T:
        self._db.commit()
        self._db.refresh(entity)
        return entity

    @override
    def delete(self, entity: T) -> None:
        self._db.delete(entity)
        self._db.commit()