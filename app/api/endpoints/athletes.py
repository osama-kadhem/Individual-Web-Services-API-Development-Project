from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.db.session import get_db
from app.schemas.athlete import Athlete, AthleteCreate, AthleteUpdate
from app.schemas.sleep_log import SleepLog, SleepLogCreate
from app.schemas.checkin import CheckIn, CheckInCreate
from app.crud import crud_athlete, crud_sleep, crud_checkin

router = APIRouter()


@router.post("/", response_model=Athlete, status_code=status.HTTP_201_CREATED)
def create_athlete(athlete: AthleteCreate, db: Session = Depends(get_db)):
    """Create a new athlete"""
    db_athlete = crud_athlete.get_athlete_by_email(db, email=athlete.email)
    if db_athlete:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_athlete.create_athlete(db=db, athlete=athlete)


@router.get("/", response_model=List[Athlete])
def list_athletes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all athletes with pagination"""
    return crud_athlete.get_athletes(db, skip=skip, limit=limit)


@router.get("/{athlete_id}", response_model=Athlete)
def get_athlete(athlete_id: int, db: Session = Depends(get_db)):
    """Get a specific athlete by ID"""
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.put("/{athlete_id}", response_model=Athlete)
def update_athlete(athlete_id: int, athlete_update: AthleteUpdate, db: Session = Depends(get_db)):
    """Update an athlete"""
    athlete = crud_athlete.update_athlete(db=db, athlete_id=athlete_id, athlete_update=athlete_update)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.delete("/{athlete_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_athlete(athlete_id: int, db: Session = Depends(get_db)):
    """Delete an athlete"""
    success = crud_athlete.delete_athlete(db=db, athlete_id=athlete_id)
    if not success:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return None


@router.post("/{athlete_id}/sleep", response_model=SleepLog, status_code=status.HTTP_201_CREATED)
def create_athlete_sleep_log(athlete_id: int, sleep_log: SleepLogCreate, db: Session = Depends(get_db)):
    """Phase 4: Create a sleep log for a specific athlete"""
    if athlete_id != sleep_log.athlete_id:
        raise HTTPException(status_code=400, detail="Athlete ID mismatch")
    
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    log_date = sleep_log.date or date.today()
    existing = crud_sleep.get_sleep_log_by_date(db, athlete_id=athlete_id, log_date=log_date)
    if existing:
        raise HTTPException(status_code=409, detail=f"Sleep log already exists for {log_date}")
        
    return crud_sleep.create_sleep_log(db=db, sleep_log=sleep_log)


@router.post("/{athlete_id}/checkins", response_model=CheckIn, status_code=status.HTTP_201_CREATED)
def create_athlete_checkin(athlete_id: int, checkin: CheckInCreate, db: Session = Depends(get_db)):
    """Phase 4: Create a check-in for a specific athlete"""
    if athlete_id != checkin.athlete_id:
        raise HTTPException(status_code=400, detail="Athlete ID mismatch")
        
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
        
    checkin_date = checkin.date or date.today()
    existing = crud_checkin.get_checkin_by_date(db, athlete_id=athlete_id, checkin_date=checkin_date)
    if existing:
        raise HTTPException(status_code=409, detail=f"Check-in already exists for {checkin_date}")
        
    return crud_checkin.create_checkin(db=db, checkin=checkin)
