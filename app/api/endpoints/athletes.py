from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.Athlete, status_code=201)
def create_athlete(athlete: schemas.AthleteCreate, db: Session = Depends(get_db)):
    """Create a new athlete"""
    db_athlete = db.query(models.Athlete).filter(models.Athlete.email == athlete.email).first()
    if db_athlete:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_athlete = models.Athlete(**athlete.model_dump())
    db.add(db_athlete)
    db.commit()
    db.refresh(db_athlete)
    return db_athlete


@router.get("/", response_model=List[schemas.Athlete])
def list_athletes(db: Session = Depends(get_db)):
    """List all athletes"""
    athletes = db.query(models.Athlete).all()
    return athletes


@router.get("/{athlete_id}", response_model=schemas.Athlete)
def get_athlete(athlete_id: int, db: Session = Depends(get_db)):
    """Get a specific athlete by ID"""
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete
