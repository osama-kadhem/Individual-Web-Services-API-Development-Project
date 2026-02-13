from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.models import SleepLog
from app.schemas.sleep_log import SleepLogCreate, SleepLogUpdate


def get_sleep_log(db: Session, sleep_log_id: int) -> Optional[SleepLog]:
    return db.query(SleepLog).filter(SleepLog.id == sleep_log_id).first()


def get_sleep_logs(
    db: Session, 
    athlete_id: Optional[int] = None, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0, 
    limit: int = 100
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
    db_sleep_log = SleepLog(**sleep_log.model_dump())
    db.add(db_sleep_log)
    db.commit()
    db.refresh(db_sleep_log)
    return db_sleep_log


def update_sleep_log(db: Session, sleep_log_id: int, sleep_log_update: SleepLogUpdate) -> Optional[SleepLog]:
    db_sleep_log = get_sleep_log(db, sleep_log_id)
    if not db_sleep_log:
        return None
    
    update_data = sleep_log_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sleep_log, key, value)
    
    db.commit()
    db.refresh(db_sleep_log)
    return db_sleep_log


def delete_sleep_log(db: Session, sleep_log_id: int) -> bool:
    db_sleep_log = get_sleep_log(db, sleep_log_id)
    if not db_sleep_log:
        return False
    
    db.delete(db_sleep_log)
    db.commit()
    return True
