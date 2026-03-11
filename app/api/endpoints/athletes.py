from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.athlete import Athlete, AthleteCreate, AthleteUpdate
from app.schemas.sleep_log import SleepLog, SleepLogCreate
from app.schemas.checkin import CheckIn, CheckInCreate
from app.crud import crud_athlete, crud_sleep, crud_checkin
from app.core.auth import get_current_user
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.post(
    "/",
    response_model=Athlete,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new athlete",
    description="Registers a new athlete in the system.",
    responses={
        400: {"description": "Email already registered."},
    },
)
def create_athlete(athlete: AthleteCreate, db: Session = Depends(get_db)):
    db_athlete = crud_athlete.get_by_email(db, email=athlete.email)
    if db_athlete:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_athlete.create_athlete(db=db, athlete=athlete)


@router.get(
    "/",
    response_model=List[Athlete],
    summary="List all athletes",
    description="Returns a paginated list of all registered athletes.",
)
def list_athletes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_athlete.get_athletes(db, skip=skip, limit=limit)


@router.get(
    "/{athlete_id}",
    response_model=Athlete,
    summary="Get an athlete by ID",
    description="Retrieves a single athlete by their unique identifier.",
)
def get_athlete(athlete_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not db_athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return db_athlete


@router.put(
    "/{athlete_id}",
    response_model=Athlete,
    summary="Update an athlete",
    description="Updates an existing athlete profile.",
)
def update_athlete(athlete_id: int, athlete: AthleteUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_athlete = crud_athlete.update_athlete(db, athlete_id=athlete_id, athlete_update=athlete)
    if not db_athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return db_athlete


@router.delete(
    "/{athlete_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an athlete",
    description="Deletes an athlete and all associated data.",
)
def delete_athlete(athlete_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    success = crud_athlete.delete_athlete(db, athlete_id=athlete_id)
    if not success:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return None


@router.post(
    "/{athlete_id}/sleep",
    response_model=SleepLog,
    status_code=status.HTTP_201_CREATED,
    summary="Log sleep for an athlete",
    description="Records a night of sleep for a specific athlete.",
    responses={
        404: {"description": "Athlete not found."},
        409: {"description": "Sleep log already exists for this date."},
    },
)
def create_athlete_sleep(athlete_id: int, sleep_in: SleepLogCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    existing = crud_sleep.get_sleep_log_by_date(db, athlete_id=athlete_id, log_date=sleep_in.date)
    if existing:
        raise HTTPException(status_code=409, detail="Sleep log already exists for this date")
    
    sleep_in.athlete_id = athlete_id
    return crud_sleep.create_sleep_log(db=db, sleep_log=sleep_in)


@router.post(
    "/{athlete_id}/checkins",
    response_model=CheckIn,
    status_code=status.HTTP_201_CREATED,
    summary="Log wellness for an athlete",
    description="Records a wellness check-in for a specific athlete.",
    responses={
        404: {"description": "Athlete not found."},
        409: {"description": "Check-in already exists for this date."},
    },
)
def create_athlete_checkin(athlete_id: int, checkin_in: CheckInCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    existing = crud_checkin.get_checkin_by_date(db, athlete_id=athlete_id, checkin_date=checkin_in.date)
    if existing:
        raise HTTPException(status_code=409, detail="Check-in already exists for this date")
    
    checkin_in.athlete_id = athlete_id
    return crud_checkin.create_checkin(db=db, checkin=checkin_in)


@router.get(
    "/{athlete_id}/export",
    summary="Export athlete data to CSV",
    description="Generates a downloadable CSV file of all training sessions for an athlete.",
)
def export_athlete_data(athlete_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Date", "Sport", "Duration (min)", "Intensity (RPE)", "Distance (km)"])
    
    # Data
    for session in athlete.sessions:
        writer.writerow([
            session.date.strftime('%Y-%m-%d') if session.date else "",
            session.sport,
            session.duration,
            session.intensity,
            session.distance
        ])
    
    output.seek(0)
    
    filename = f"athlete_{athlete_id}_export.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
