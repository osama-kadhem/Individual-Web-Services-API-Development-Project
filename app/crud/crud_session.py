from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.models import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate
from app.crud.base import apply_update, delete_record, save_new


def get_session(db: Session, session_id: int) -> Optional[SessionModel]:
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()


def get_sessions(
    db: Session,
    athlete_id: Optional[int] = None,
    sport: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[SessionModel]:
    query = db.query(SessionModel)
    if athlete_id:
        query = query.filter(SessionModel.athlete_id == athlete_id)
    if sport:
        query = query.filter(SessionModel.sport == sport)
    if start_date:
        query = query.filter(SessionModel.date >= start_date)
    if end_date:
        query = query.filter(SessionModel.date <= end_date)
    return query.offset(skip).limit(limit).all()


def create_session(db: Session, session: SessionCreate) -> SessionModel:
    return save_new(db, SessionModel(**session.model_dump()))


def update_session(db: Session, session_id: int, session_update: SessionUpdate) -> Optional[SessionModel]:
    return apply_update(db, get_session(db, session_id), session_update)


def delete_session(db: Session, session_id: int) -> bool:
    return delete_record(db, get_session(db, session_id))
