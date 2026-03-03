from __future__ import annotations

from typing import Optional, TypeVar
from sqlalchemy.orm import Session
from pydantic import BaseModel

T = TypeVar("T")


def apply_update(db: Session, obj: Optional[T], schema: BaseModel) -> Optional[T]:
    """Applies a Pydantic partial update to an ORM object."""
    if obj is None:
        return None
    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_record(db: Session, obj: Optional[T]) -> bool:
    """Deletes an ORM object from the database."""
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True


def save_new(db: Session, obj: T) -> T:
    """Saves a new ORM object to the database."""
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
