from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class Athlete(Base):
    """Athlete model with relationships to other entities"""
    __tablename__ = "athletes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
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
    """Sleep log entity"""
    __tablename__ = "sleep_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    hours = Column(Float, nullable=False)
    quality = Column(Integer)  # 1-10
    
    athlete = relationship("Athlete", back_populates="sleep_logs")


class CheckIn(Base):
    """Daily check-in entity"""
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    readiness_score = Column(Integer)  # 1-100
    fatigue = Column(Integer)  # 1-10
    stress = Column(Integer)  # 1-10
    soreness = Column(Integer)  # 1-10
    
    athlete = relationship("Athlete", back_populates="checkins")
