import csv
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.models import Athlete, Session as TrainingSession, SleepLog, CheckIn
from app.core.auth import get_password_hash

def import_kaggle_dataset(file_path: str):
    print(f"🚀 Integrating REAL Kaggle Dataset: {file_path}")
    db = SessionLocal()
    
    # Default password for all imported athletes
    default_hashed_password = get_password_hash("ironmind2026")
    
    try:
        # Clear existing data to avoid confusion with the real dataset
        db.query(CheckIn).delete()
        db.query(SleepLog).delete()
        db.query(TrainingSession).delete()
        db.query(Athlete).delete()
        db.commit()
        print("🗑️ Cleared existing database records for a fresh import.")

        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            stats = {"athletes": 0, "sessions": 0, "sleep": 0, "checkins": 0}
            
            for row in reader:
                # 1. Athlete Mapping (Standardizing string IDs A0001 -> Email)
                athlete_email = f"athlete_{row['Athlete_ID'].lower()}@ironmind.com"
                athlete = db.query(Athlete).filter(Athlete.email == athlete_email).first()
                if not athlete:
                    athlete = Athlete(
                        name=f"Athlete {row['Athlete_ID']}",
                        email=athlete_email,
                        hashed_password=default_hashed_password,
                        role="athlete",
                        age=25
                    )
                    db.add(athlete)
                    db.flush()
                    stats["athletes"] += 1
                
                # 2. Map Date
                log_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()

                # 3. ETL: Training Sessions
                if float(row['Training_Hours']) > 0:
                    new_session = TrainingSession(
                        athlete_id=athlete.id,
                        sport=row['Sport_Type'],
                        duration=float(row['Training_Hours']) * 60, # Hours to Minutes
                        intensity=int(row['Training_Intensity']),
                        date=datetime.combine(log_date, datetime.min.time())
                    )
                    db.add(new_session)
                    stats["sessions"] += 1

                # 4. ETL: Sleep Logs
                existing_sleep = db.query(SleepLog).filter(
                    SleepLog.athlete_id == athlete.id, 
                    SleepLog.date == log_date
                ).first()
                if not existing_sleep:
                    new_sleep = SleepLog(
                        athlete_id=athlete.id,
                        date=log_date,
                        sleep_hours=float(row['Sleep_Hours']),
                        sleep_quality=4 # Derived default
                    )
                    db.add(new_sleep)
                    stats["sleep"] += 1

                # 5. ETL: Wellness Check-ins
                existing_checkin = db.query(CheckIn).filter(
                    CheckIn.athlete_id == athlete.id, 
                    CheckIn.date == log_date
                ).first()
                if not existing_checkin:
                    # Map 0-100 Recovery_Index to 1-10 Soreness (inverse)
                    soreness = max(1, 10 - int(float(row['Recovery_Index']) / 10))
                    new_checkin = CheckIn(
                        athlete_id=athlete.id,
                        date=log_date,
                        fatigue=int(row['Fatigue_Level']),
                        stress=5,
                        mood=7,
                        soreness=soreness
                    )
                    db.add(new_checkin)
                    stats["checkins"] += 1

            db.commit()
            print("✅ REAL Dataset Integration Finished!")
            print(f"   - Athletes: {stats['athletes']}")
            print(f"   - Training Sessions: {stats['sessions']}")
            print(f"   - Sleep Logs: {stats['sleep']}")
            print(f"   - Wellness Checkins: {stats['checkins']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    target_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/raw/athlete_tracking.csv'))
    import_kaggle_dataset(target_csv)
