from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class Athlete(Base):
    """Phase 1: Basic Athlete model"""
    __tablename__ = "athletes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
