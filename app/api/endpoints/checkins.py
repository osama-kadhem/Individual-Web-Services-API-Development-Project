from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.schemas.checkin import CheckIn, CheckInCreate, CheckInUpdate
from app.crud import crud_checkin, crud_athlete

router = APIRouter()


@router.post("/", response_model=CheckIn, status_code=status.HTTP_201_CREATED)
def create_checkin(checkin: CheckInCreate, db: Session = Depends(get_db)):
    """Create a new daily check-in"""
    # 1. Check if athlete exists
    athlete = crud_athlete.get_athlete(db, athlete_id=checkin.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    # 2. Check for existing check-in on this date (Uniqueness Constraint)
    checkin_date = checkin.date or date.today()
    existing_checkin = crud_checkin.get_checkin_by_date(db, athlete_id=checkin.athlete_id, checkin_date=checkin_date)
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Check-in already exists for athlete {checkin.athlete_id} on {checkin_date}"
        )
        
    return crud_checkin.create_checkin(db=db, checkin=checkin)


@router.get("/", response_model=List[CheckIn])
def list_checkins(
    athlete_id: Optional[int] = None, 
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List check-ins with filtering and pagination"""
    return crud_checkin.get_checkins(
        db, 
        athlete_id=athlete_id, 
        start_date=from_date, 
        end_date=to_date, 
        skip=skip, 
        limit=limit
    )


@router.get("/{checkin_id}", response_model=CheckIn)
def get_checkin(checkin_id: int, db: Session = Depends(get_db)):
    """Get a specific check-in by ID"""
    db_checkin = crud_checkin.get_checkin(db, checkin_id=checkin_id)
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return db_checkin


@router.put("/{checkin_id}", response_model=CheckIn)
def update_checkin(checkin_id: int, checkin_update: CheckInUpdate, db: Session = Depends(get_db)):
    """Update a check-in"""
    db_checkin = crud_checkin.update_checkin(db=db, checkin_id=checkin_id, checkin_update=checkin_update)
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return db_checkin


@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkin(checkin_id: int, db: Session = Depends(get_db)):
    """Delete a check-in"""
    success = crud_checkin.delete_checkin(db=db, checkin_id=checkin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return None
