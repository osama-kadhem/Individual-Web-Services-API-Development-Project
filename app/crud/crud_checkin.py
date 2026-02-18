from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.models.models import CheckIn
from app.schemas.checkin import CheckInCreate, CheckInUpdate


def get_checkin(db: Session, checkin_id: int) -> Optional[CheckIn]:
    return db.query(CheckIn).filter(CheckIn.id == checkin_id).first()


def get_checkin_by_date(db: Session, athlete_id: int, checkin_date: date) -> Optional[CheckIn]:
    """Check if a check-in already exists for an athlete on a specific date"""
    return db.query(CheckIn).filter(
        CheckIn.athlete_id == athlete_id, 
        CheckIn.date == checkin_date
    ).first()


def get_checkins(
    db: Session, 
    athlete_id: Optional[int] = None, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[CheckIn]:
    query = db.query(CheckIn)
    if athlete_id:
        query = query.filter(CheckIn.athlete_id == athlete_id)
    if start_date:
        query = query.filter(CheckIn.date >= start_date)
    if end_date:
        query = query.filter(CheckIn.date <= end_date)
    return query.offset(skip).limit(limit).all()


def create_checkin(db: Session, checkin: CheckInCreate) -> CheckIn:
    db_checkin = CheckIn(**checkin.model_dump())
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin


def update_checkin(db: Session, checkin_id: int, checkin_update: CheckInUpdate) -> Optional[CheckIn]:
    db_checkin = get_checkin(db, checkin_id)
    if not db_checkin:
        return None
    
    update_data = checkin_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_checkin, key, value)
    
    db.commit()
    db.refresh(db_checkin)
    return db_checkin


def delete_checkin(db: Session, checkin_id: int) -> bool:
    db_checkin = get_checkin(db, checkin_id)
    if not db_checkin:
        return False
    
    db.delete(db_checkin)
    db.commit()
    return True
