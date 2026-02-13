from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.schemas.sleep_log import SleepLog, SleepLogCreate, SleepLogUpdate
from app.crud import crud_sleep, crud_athlete

router = APIRouter()


@router.post("/", response_model=SleepLog, status_code=201)
def create_sleep_log(sleep_log: SleepLogCreate, db: Session = Depends(get_db)):
    """Create a new sleep log"""
    athlete = crud_athlete.get_athlete(db, athlete_id=sleep_log.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return crud_sleep.create_sleep_log(db=db, sleep_log=sleep_log)


@router.get("/", response_model=List[SleepLog])
def list_sleep_logs(
    athlete_id: int = None, 
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List sleep logs with filtering and pagination"""
    return crud_sleep.get_sleep_logs(
        db, 
        athlete_id=athlete_id, 
        start_date=start_date, 
        end_date=end_date, 
        skip=skip, 
        limit=limit
    )


@router.get("/{sleep_log_id}", response_model=SleepLog)
def get_sleep_log(sleep_log_id: int, db: Session = Depends(get_db)):
    """Get a specific sleep log by ID"""
    db_sleep_log = crud_sleep.get_sleep_log(db, sleep_log_id=sleep_log_id)
    if not db_sleep_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return db_sleep_log


@router.put("/{sleep_log_id}", response_model=SleepLog)
def update_sleep_log(sleep_log_id: int, sleep_log_update: SleepLogUpdate, db: Session = Depends(get_db)):
    """Update a sleep log"""
    db_sleep_log = crud_sleep.update_sleep_log(db=db, sleep_log_id=sleep_log_id, sleep_log_update=sleep_log_update)
    if not db_sleep_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return db_sleep_log


@router.delete("/{sleep_log_id}", status_code=204)
def delete_sleep_log(sleep_log_id: int, db: Session = Depends(get_db)):
    """Delete a sleep log"""
    success = crud_sleep.delete_sleep_log(db=db, sleep_log_id=sleep_log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return None
