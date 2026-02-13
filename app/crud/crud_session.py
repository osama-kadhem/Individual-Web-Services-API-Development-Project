from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.models import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate


def get_session(db: Session, session_id: int) -> Optional[SessionModel]:
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()


def get_sessions(
    db: Session, 
    athlete_id: Optional[int] = None, 
    sport: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0, 
    limit: int = 100
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
    db_session = SessionModel(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session(db: Session, session_id: int, session_update: SessionUpdate) -> Optional[SessionModel]:
    db_session = get_session(db, session_id)
    if not db_session:
        return None
    
    update_data = session_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: int) -> bool:
    db_session = get_session(db, session_id)
    if not db_session:
        return False
    
    db.delete(db_session)
    db.commit()
    return True
