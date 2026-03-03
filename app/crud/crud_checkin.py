from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.models.models import CheckIn
from app.schemas.checkin import CheckInCreate, CheckInUpdate
from app.crud.base import apply_update, delete_record, save_new


def get_checkin(db: Session, checkin_id: int) -> Optional[CheckIn]:
    return db.query(CheckIn).filter(CheckIn.id == checkin_id).first()


def get_checkin_by_date(db: Session, athlete_id: int, checkin_date: date) -> Optional[CheckIn]:
    """Return the check-in for an athlete on a specific date, or None."""
    return db.query(CheckIn).filter(
        CheckIn.athlete_id == athlete_id,
        CheckIn.date == checkin_date,
    ).first()


def get_checkins(
    db: Session,
    athlete_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
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
    return save_new(db, CheckIn(**checkin.model_dump()))


def update_checkin(db: Session, checkin_id: int, checkin_update: CheckInUpdate) -> Optional[CheckIn]:
    return apply_update(db, get_checkin(db, checkin_id), checkin_update)


def delete_checkin(db: Session, checkin_id: int) -> bool:
    return delete_record(db, get_checkin(db, checkin_id))
