from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.schemas.checkin import CheckIn, CheckInCreate, CheckInUpdate
from app.crud import crud_checkin, crud_athlete

router = APIRouter()


@router.post(
    "/",
    response_model=CheckIn,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a wellness check-in",
    description="Records an athlete's daily subjective wellness metrics.",
    responses={
        404: {"description": "Athlete not found."},
        409: {"description": "Check-in already exists for this date."},
    },
)
def create_checkin(checkin: CheckInCreate, db: Session = Depends(get_db)):
    athlete = crud_athlete.get_athlete(db, athlete_id=checkin.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    existing = crud_checkin.get_checkin_by_date(db, athlete_id=checkin.athlete_id, checkin_date=checkin.date)
    if existing:
        raise HTTPException(status_code=409, detail="Check-in already exists for this date")
        
    return crud_checkin.create_checkin(db=db, checkin=checkin)


@router.get(
    "/",
    response_model=List[CheckIn],
    summary="List check-ins",
    description="Returns a list of wellness entries, filtered by athlete or date range.",
)
def list_checkins(
    athlete_id: Optional[int] = None,
    from_date: Optional[date] = Query(None, alias="start_date"),
    to_date: Optional[date] = Query(None, alias="end_date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud_checkin.get_checkins(
        db,
        athlete_id=athlete_id,
        start_date=from_date,
        end_date=to_date,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{checkin_id}",
    response_model=CheckIn,
    summary="Get a check-in by ID",
    description="Retrieves a single wellness entry by its unique identifier.",
)
def get_checkin(checkin_id: int, db: Session = Depends(get_db)):
    db_checkin = crud_checkin.get_checkin(db, checkin_id=checkin_id)
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return db_checkin


@router.put(
    "/{checkin_id}",
    response_model=CheckIn,
    summary="Update a check-in",
    description="Updates existing wellness metrics.",
)
def update_checkin(checkin_id: int, checkin: CheckInUpdate, db: Session = Depends(get_db)):
    db_checkin = crud_checkin.update_checkin(db, checkin_id=checkin_id, checkin_update=checkin)
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return db_checkin


@router.delete(
    "/{checkin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a check-in",
    description="Deletes a wellness entry from the system.",
)
def delete_checkin(checkin_id: int, db: Session = Depends(get_db)):
    success = crud_checkin.delete_checkin(db, checkin_id=checkin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return None
