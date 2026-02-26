from app.db.session import SessionLocal, engine
from app.models.models import Base, Athlete, SleepLog
from app.schemas.sleep_log import SleepLogCreate
from app.crud import crud_athlete, crud_sleep
import datetime

# Reset DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # 1. Create Athlete
    ath = Athlete(name="Test", email="test@test.com")
    db.add(ath)
    db.commit()
    db.refresh(ath)
    print(f"Created Athlete ID: {ath.id}")

    # 2. Create Sleep Log
    s_create = SleepLogCreate(athlete_id=ath.id, sleep_hours=8.0, sleep_quality=5)
    print(f"Schema Data: {s_create.model_dump()}")
    
    # Manually check uniqueness search
    existing = crud_sleep.get_sleep_log_by_date(db, ath.id, datetime.date.today())
    print(f"Existing check: {existing}")

    res = crud_sleep.create_sleep_log(db, s_create)
    print(f"Success: {res.id}")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    db.close()
