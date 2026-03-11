from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.db.session import Base


class Athlete(Base):
    """Athlete model with relationships to other entities"""
    __tablename__ = "athletes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Allow null temporarily for old data
    role = Column(String, default="athlete") # "athlete" or "coach"
    city = Column(String, default="Leeds")
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="athlete", cascade="all, delete-orphan")
    sleep_logs = relationship("SleepLog", back_populates="athlete", cascade="all, delete-orphan")
    checkins = relationship("CheckIn", back_populates="athlete", cascade="all, delete-orphan")


class Session(Base):
    """Training session entity"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    sport = Column(String, nullable=False)  # e.g., "Swimming", "Cycling", "Running"
    duration = Column(Float, nullable=False)  # in minutes
    distance = Column(Float)  # in km
    intensity = Column(Integer)  # 1-10 RPE
    date = Column(DateTime, default=datetime.utcnow)
    
    athlete = relationship("Athlete", back_populates="sessions")


class SleepLog(Base):
    """Sleep log entity with unique constraint per athlete per day"""
    __tablename__ = "sleep_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    date = Column(Date, default=date.today)
    sleep_hours = Column(Float, nullable=False)
    sleep_quality = Column(Integer)  # 1-5
    
    # Relationships
    athlete = relationship("Athlete", back_populates="sleep_logs")
    
    __table_args__ = (UniqueConstraint("athlete_id", "date", name="uq_athlete_sleep_date"),)


class CheckIn(Base):
    """Daily check-in entity with unique constraint per athlete per day"""
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    date = Column(Date, default=date.today)
    readiness_score = Column(Integer)  # Optional helper score
    fatigue = Column(Integer)  # 1-10
    stress = Column(Integer)  # 1-10
    mood = Column(Integer)  # 1-10
    soreness = Column(Integer)  # 1-10
    
    # Relationships
    athlete = relationship("Athlete", back_populates="checkins")

    __table_args__ = (UniqueConstraint("athlete_id", "date", name="uq_athlete_checkin_date"),)
