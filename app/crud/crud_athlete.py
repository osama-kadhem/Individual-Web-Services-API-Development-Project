from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.models import Athlete
from app.schemas.athlete import AthleteCreate, AthleteUpdate
from app.crud.base import apply_update, delete_record, save_new


def get_athlete(db: Session, athlete_id: int) -> Optional[Athlete]:
    return db.query(Athlete).filter(Athlete.id == athlete_id).first()


def get_athlete_by_email(db: Session, email: str) -> Optional[Athlete]:
    return db.query(Athlete).filter(Athlete.email == email).first()


def get_athletes(db: Session, skip: int = 0, limit: int = 100) -> List[Athlete]:
    return db.query(Athlete).offset(skip).limit(limit).all()


def create_athlete(db: Session, athlete: AthleteCreate) -> Athlete:
    return save_new(db, Athlete(**athlete.model_dump()))


def update_athlete(db: Session, athlete_id: int, athlete_update: AthleteUpdate) -> Optional[Athlete]:
    return apply_update(db, get_athlete(db, athlete_id), athlete_update)


def delete_athlete(db: Session, athlete_id: int) -> bool:
    return delete_record(db, get_athlete(db, athlete_id))
