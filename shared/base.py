from __future__ import annotations

from typing import Generic, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")
ID = TypeVar("ID")


class BaseRepository(Generic[T, ID]):
    def __init__(self, db: Session, model: type[T]) -> None:
        self._db = db
        self._model = model

    def create(self, obj: T) -> T:
        self._db.add(obj)
        self._db.commit()
        self._db.refresh(obj)
        return obj

    def get(self, obj_id: ID) -> Optional[T]:
        return self._db.get(self._model, obj_id)

    def exists(self, obj_id: ID) -> bool:
        return (
            self._db.execute(select(self._model.id).where(self._model.id == obj_id)).first()
            is not None
        )

    def save(self, obj: T) -> T:
        self._db.commit()
        self._db.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self._db.delete(obj)
        self._db.commit()
