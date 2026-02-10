from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.SleepLog, status_code=201)
def create_sleep_log(sleep_log: schemas.SleepLogCreate, db: Session = Depends(get_db)):
    """Create a new sleep log"""
    # Verify athlete exists
    athlete = db.query(models.Athlete).filter(models.Athlete.id == sleep_log.athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    db_sleep_log = models.SleepLog(**sleep_log.model_dump())
    db.add(db_sleep_log)
    db.commit()
    db.refresh(db_sleep_log)
    return db_sleep_log


@router.get("/", response_model=List[schemas.SleepLog])
def list_sleep_logs(athlete_id: int = None, db: Session = Depends(get_db)):
    """List sleep logs, optionally filtered by athlete_id"""
    query = db.query(models.SleepLog)
    if athlete_id:
        query = query.filter(models.SleepLog.athlete_id == athlete_id)
    return query.all()


@router.get("/{sleep_log_id}", response_model=schemas.SleepLog)
def get_sleep_log(sleep_log_id: int, db: Session = Depends(get_db)):
    """Get a specific sleep log by ID"""
    db_sleep_log = db.query(models.SleepLog).filter(models.SleepLog.id == sleep_log_id).first()
    if not db_sleep_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return db_sleep_log


@router.put("/{sleep_log_id}", response_model=schemas.SleepLog)
def update_sleep_log(sleep_log_id: int, sleep_log_update: schemas.SleepLogUpdate, db: Session = Depends(get_db)):
    """Update a sleep log"""
    db_sleep_log = db.query(models.SleepLog).filter(models.SleepLog.id == sleep_log_id).first()
    if not db_sleep_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    update_data = sleep_log_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sleep_log, key, value)
    
    db.commit()
    db.refresh(db_sleep_log)
    return db_sleep_log


@router.delete("/{sleep_log_id}", status_code=204)
def delete_sleep_log(sleep_log_id: int, db: Session = Depends(get_db)):
    """Delete a sleep log"""
    db_sleep_log = db.query(models.SleepLog).filter(models.SleepLog.id == sleep_log_id).first()
    if not db_sleep_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    db.delete(db_sleep_log)
    db.commit()
    return None
