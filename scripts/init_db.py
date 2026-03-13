import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine, Base
from app.models.models import Athlete, Session, SleepLog, CheckIn

print("🔨 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully.")
