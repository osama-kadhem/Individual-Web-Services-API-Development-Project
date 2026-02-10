from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.CheckIn, status_code=201)
def create_checkin(checkin: schemas.CheckInCreate, db: Session = Depends(get_db)):
    """Create a new daily check-in"""
    # Verify athlete exists
    athlete = db.query(models.Athlete).filter(models.Athlete.id == checkin.athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    db_checkin = models.CheckIn(**checkin.model_dump())
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin


@router.get("/", response_model=List[schemas.CheckIn])
def list_checkins(athlete_id: int = None, db: Session = Depends(get_db)):
    """List check-ins, optionally filtered by athlete_id"""
    query = db.query(models.CheckIn)
    if athlete_id:
        query = query.filter(models.CheckIn.athlete_id == athlete_id)
    return query.all()


@router.get("/{checkin_id}", response_model=schemas.CheckIn)
def get_checkin(checkin_id: int, db: Session = Depends(get_db)):
    """Get a specific check-in by ID"""
    db_checkin = db.query(models.CheckIn).filter(models.CheckIn.id == checkin_id).first()
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return db_checkin


@router.put("/{checkin_id}", response_model=schemas.CheckIn)
def update_checkin(checkin_id: int, checkin_update: schemas.CheckInUpdate, db: Session = Depends(get_db)):
    """Update a check-in"""
    db_checkin = db.query(models.CheckIn).filter(models.CheckIn.id == checkin_id).first()
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    update_data = checkin_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_checkin, key, value)
    
    db.commit()
    db.refresh(db_checkin)
    return db_checkin


@router.delete("/{checkin_id}", status_code=204)
def delete_checkin(checkin_id: int, db: Session = Depends(get_db)):
    """Delete a check-in"""
    db_checkin = db.query(models.CheckIn).filter(models.CheckIn.id == checkin_id).first()
    if not db_checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    db.delete(db_checkin)
    db.commit()
    return None
