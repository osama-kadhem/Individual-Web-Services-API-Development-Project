from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.models import Athlete
from app.schemas.athlete import AthleteCreate, AthleteUpdate


def get_athlete(db: Session, athlete_id: int) -> Optional[Athlete]:
    return db.query(Athlete).filter(Athlete.id == athlete_id).first()


def get_athlete_by_email(db: Session, email: str) -> Optional[Athlete]:
    return db.query(Athlete).filter(Athlete.email == email).first()


def get_athletes(db: Session, skip: int = 0, limit: int = 100) -> List[Athlete]:
    return db.query(Athlete).offset(skip).limit(limit).all()


def create_athlete(db: Session, athlete: AthleteCreate) -> Athlete:
    db_athlete = Athlete(**athlete.model_dump())
    db.add(db_athlete)
    db.commit()
    db.refresh(db_athlete)
    return db_athlete


def update_athlete(db: Session, athlete_id: int, athlete_update: AthleteUpdate) -> Optional[Athlete]:
    db_athlete = get_athlete(db, athlete_id)
    if not db_athlete:
        return None
    
    update_data = athlete_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_athlete, key, value)
    
    db.commit()
    db.refresh(db_athlete)
    return db_athlete


def delete_athlete(db: Session, athlete_id: int) -> bool:
    db_athlete = get_athlete(db, athlete_id)
    if not db_athlete:
        return False
    
    db.delete(db_athlete)
    db.commit()
    return True
