from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.athlete import Athlete, AthleteCreate, AthleteUpdate
from app.crud import crud_athlete

router = APIRouter()


@router.post("/", response_model=Athlete, status_code=201)
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


@router.delete("/{athlete_id}", status_code=204)
def delete_athlete(athlete_id: int, db: Session = Depends(get_db)):
    """Delete an athlete"""
    success = crud_athlete.delete_athlete(db=db, athlete_id=athlete_id)
    if not success:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return None
