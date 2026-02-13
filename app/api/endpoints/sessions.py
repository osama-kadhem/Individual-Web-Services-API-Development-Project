from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.schemas.session import Session, SessionCreate, SessionUpdate
from app.crud import crud_session, crud_athlete

router = APIRouter()


@router.post("/", response_model=Session, status_code=201)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new training session"""
    athlete = crud_athlete.get_athlete(db, athlete_id=session.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return crud_session.create_session(db=db, session=session)


@router.get("/", response_model=List[Session])
def list_sessions(
    athlete_id: int = None, 
    sport: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List training sessions with advanced filtering and pagination"""
    return crud_session.get_sessions(
        db, 
        athlete_id=athlete_id, 
        sport=sport, 
        start_date=start_date, 
        end_date=end_date, 
        skip=skip, 
        limit=limit
    )


@router.get("/{session_id}", response_model=Session)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific session by ID"""
    db_session = crud_session.get_session(db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.put("/{session_id}", response_model=Session)
def update_session(session_id: int, session_update: SessionUpdate, db: Session = Depends(get_db)):
    """Update a training session"""
    db_session = crud_session.update_session(db=db, session_id=session_id, session_update=session_update)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a training session"""
    success = crud_session.delete_session(db=db, session_id=session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None
