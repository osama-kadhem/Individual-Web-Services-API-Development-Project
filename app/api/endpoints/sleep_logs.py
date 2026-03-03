from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.schemas.sleep_log import SleepLog, SleepLogCreate, SleepLogUpdate
from app.crud import crud_sleep, crud_athlete

router = APIRouter()


@router.post(
    "/",
    response_model=SleepLog,
    status_code=status.HTTP_201_CREATED,
    summary="Log a sleep entry",
    description="Records a night of sleep for an athlete.",
    responses={
        404: {"description": "Athlete not found."},
        409: {"description": "Sleep log already exists for this date."},
    },
)
def create_sleep_log(sleep_log: SleepLogCreate, db: Session = Depends(get_db)):
    athlete = crud_athlete.get_athlete(db, athlete_id=sleep_log.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    existing = crud_sleep.get_sleep_log_by_date(db, athlete_id=sleep_log.athlete_id, log_date=sleep_log.date)
    if existing:
        raise HTTPException(status_code=409, detail="Sleep log already exists for this date")
        
    return crud_sleep.create_sleep_log(db=db, sleep_log=sleep_log)


@router.get(
    "/",
    response_model=List[SleepLog],
    summary="List sleep logs",
    description="Returns a list of sleep entries, filtered by athlete or date range.",
)
def list_sleep_logs(
    athlete_id: Optional[int] = None,
    from_date: Optional[date] = Query(None, alias="start_date"),
    to_date: Optional[date] = Query(None, alias="end_date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud_sleep.get_sleep_logs(
        db,
        athlete_id=athlete_id,
        start_date=from_date,
        end_date=to_date,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{sleep_log_id}",
    response_model=SleepLog,
    summary="Get a sleep log by ID",
    description="Retrieves a single sleep entry by its unique identifier.",
)
def get_sleep_log(sleep_log_id: int, db: Session = Depends(get_db)):
    db_log = crud_sleep.get_sleep_log(db, sleep_log_id=sleep_log_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return db_log


@router.put(
    "/{sleep_log_id}",
    response_model=SleepLog,
    summary="Update a sleep log",
    description="Updates an existing sleep entry.",
)
def update_sleep_log(sleep_log_id: int, sleep_log: SleepLogUpdate, db: Session = Depends(get_db)):
    db_log = crud_sleep.update_sleep_log(db, sleep_log_id=sleep_log_id, sleep_log_update=sleep_log)
    if not db_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return db_log


@router.delete(
    "/{sleep_log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sleep log",
    description="Deletes a sleep entry from the system.",
)
def delete_sleep_log(sleep_log_id: int, db: Session = Depends(get_db)):
    success = crud_sleep.delete_sleep_log(db, sleep_log_id=sleep_log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return None
