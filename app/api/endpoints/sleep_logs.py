from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.schemas.sleep_log import SleepLog, SleepLogCreate, SleepLogUpdate
from app.crud import crud_sleep, crud_athlete

router = APIRouter()


@router.post("/", response_model=SleepLog, status_code=status.HTTP_201_CREATED)
def create_sleep_log(sleep_log: SleepLogCreate, db: Session = Depends(get_db)):
    """Create a new sleep log"""
    # 1. Check if athlete exists
    athlete = crud_athlete.get_athlete(db, athlete_id=sleep_log.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    # 2. Check for existing log on this date (Uniqueness Constraint)
    log_date = sleep_log.date or date.today()
    existing_log = crud_sleep.get_sleep_log_by_date(db, athlete_id=sleep_log.athlete_id, log_date=log_date)
    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Sleep log already exists for athlete {sleep_log.athlete_id} on {log_date}"
        )
        
    return crud_sleep.create_sleep_log(db=db, sleep_log=sleep_log)


@router.get("/", response_model=List[SleepLog])
def list_sleep_logs(
    athlete_id: Optional[int] = None, 
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List sleep logs with filtering and pagination"""
    return crud_sleep.get_sleep_logs(
        db, 
        athlete_id=athlete_id, 
        start_date=from_date, 
        end_date=to_date, 
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


@router.delete("/{sleep_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sleep_log(sleep_log_id: int, db: Session = Depends(get_db)):
    """Delete a sleep log"""
    success = crud_sleep.delete_sleep_log(db=db, sleep_log_id=sleep_log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return None
