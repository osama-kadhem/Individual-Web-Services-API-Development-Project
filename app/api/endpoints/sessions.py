from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.schemas.session import Session, SessionCreate, SessionUpdate
from app.crud import crud_session, crud_athlete

router = APIRouter()


@router.post(
    "/",
    response_model=Session,
    status_code=status.HTTP_201_CREATED,
    summary="Log a training session",
    description="Records a completed training session for an athlete.",
    responses={
        404: {"description": "Athlete not found."},
    },
)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    athlete = crud_athlete.get_athlete(db, athlete_id=session.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return crud_session.create_session(db=db, session=session)


@router.get(
    "/",
    response_model=List[Session],
    summary="List training sessions",
    description="Returns a list of sessions, filtered by athlete, sport, or date range.",
)
def list_sessions(
    athlete_id: Optional[int] = None,
    sport: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud_session.get_sessions(
        db,
        athlete_id=athlete_id,
        sport=sport,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{session_id}",
    response_model=Session,
    summary="Get a session by ID",
    description="Retrieves a single training session by its unique identifier.",
)
def get_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud_session.get_session(db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.put(
    "/{session_id}",
    response_model=Session,
    summary="Update a session",
    description="Updates an existing training session.",
)
def update_session(session_id: int, session: SessionUpdate, db: Session = Depends(get_db)):
    db_session = crud_session.update_session(db, session_id=session_id, session_update=session)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session",
    description="Deletes a training session from the system.",
)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    success = crud_session.delete_session(db, session_id=session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None
