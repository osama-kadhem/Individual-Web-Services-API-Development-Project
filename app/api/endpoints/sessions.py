from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.Session, status_code=201)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    """Create a new training session"""
    # Verify athlete exists
    athlete = db.query(models.Athlete).filter(models.Athlete.id == session.athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    db_session = models.Session(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/", response_model=List[schemas.Session])
def list_sessions(athlete_id: int = None, db: Session = Depends(get_db)):
    """List training sessions, optionally filtered by athlete_id"""
    query = db.query(models.Session)
    if athlete_id:
        query = query.filter(models.Session.athlete_id == athlete_id)
    return query.all()


@router.get("/{session_id}", response_model=schemas.Session)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific session by ID"""
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.put("/{session_id}", response_model=schemas.Session)
def update_session(session_id: int, session_update: schemas.SessionUpdate, db: Session = Depends(get_db)):
    """Update a training session"""
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_data = session_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a training session"""
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    return None
