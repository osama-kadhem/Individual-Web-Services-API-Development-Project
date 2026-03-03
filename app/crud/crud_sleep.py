from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.models.models import SleepLog
from app.schemas.sleep_log import SleepLogCreate, SleepLogUpdate
from app.crud.base import apply_update, delete_record, save_new


def get_sleep_log(db: Session, sleep_log_id: int) -> Optional[SleepLog]:
    return db.query(SleepLog).filter(SleepLog.id == sleep_log_id).first()


def get_sleep_log_by_date(db: Session, athlete_id: int, log_date: date) -> Optional[SleepLog]:
    """Return the sleep log for an athlete on a specific date, or None."""
    return db.query(SleepLog).filter(
        SleepLog.athlete_id == athlete_id,
        SleepLog.date == log_date,
    ).first()


def get_sleep_logs(
    db: Session,
    athlete_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[SleepLog]:
    query = db.query(SleepLog)
    if athlete_id:
        query = query.filter(SleepLog.athlete_id == athlete_id)
    if start_date:
        query = query.filter(SleepLog.date >= start_date)
    if end_date:
        query = query.filter(SleepLog.date <= end_date)
    return query.offset(skip).limit(limit).all()


def create_sleep_log(db: Session, sleep_log: SleepLogCreate) -> SleepLog:
    return save_new(db, SleepLog(**sleep_log.model_dump()))


def update_sleep_log(db: Session, sleep_log_id: int, sleep_log_update: SleepLogUpdate) -> Optional[SleepLog]:
    return apply_update(db, get_sleep_log(db, sleep_log_id), sleep_log_update)


def delete_sleep_log(db: Session, sleep_log_id: int) -> bool:
    return delete_record(db, get_sleep_log(db, sleep_log_id))
