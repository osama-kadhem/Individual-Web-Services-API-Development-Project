from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


# --- Athlete Schemas ---

class AthleteBase(BaseModel):
    """Base athlete schema"""
    name: str
    email: EmailStr
    age: Optional[int] = None


class AthleteCreate(AthleteBase):
    """Schema for creating an athlete"""
    pass


class AthleteUpdate(BaseModel):
    """Schema for updating an athlete"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class Athlete(AthleteBase):
    """Schema for athlete response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# --- Session Schemas ---

class SessionBase(BaseModel):
    """Base session schema"""
    sport: str
    duration: float = Field(..., gt=0, description="Duration in minutes")
    distance: Optional[float] = Field(None, ge=0, description="Distance in km")
    intensity: Optional[int] = Field(None, ge=1, le=10, description="RPE intensity (1-10)")
    date: Optional[datetime] = None


class SessionCreate(SessionBase):
    """Schema for creating a session"""
    athlete_id: int


class SessionUpdate(BaseModel):
    """Schema for updating a session"""
    sport: Optional[str] = None
    duration: Optional[float] = Field(None, gt=0)
    distance: Optional[float] = Field(None, ge=0)
    intensity: Optional[int] = Field(None, ge=1, le=10)
    date: Optional[datetime] = None


class Session(SessionBase):
    """Schema for session response"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    athlete_id: int


# --- Sleep Log Schemas ---

class SleepLogBase(BaseModel):
    """Base sleep log schema"""
    hours: float = Field(..., gt=0, description="Hours of sleep")
    quality: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality (1-10)")
    date: Optional[datetime] = None


class SleepLogCreate(SleepLogBase):
    """Schema for creating a sleep log"""
    athlete_id: int


class SleepLogUpdate(BaseModel):
    """Schema for updating a sleep log"""
    hours: Optional[float] = Field(None, gt=0)
    quality: Optional[int] = Field(None, ge=1, le=10)
    date: Optional[datetime] = None


class SleepLog(SleepLogBase):
    """Schema for sleep log response"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    athlete_id: int


# --- Check-In Schemas ---

class CheckInBase(BaseModel):
    """Base check-in schema"""
    readiness_score: Optional[int] = Field(None, ge=1, le=100)
    fatigue: Optional[int] = Field(None, ge=1, le=10)
    stress: Optional[int] = Field(None, ge=1, le=10)
    soreness: Optional[int] = Field(None, ge=1, le=10)
    date: Optional[datetime] = None


class CheckInCreate(CheckInBase):
    """Schema for creating a check-in"""
    athlete_id: int


class CheckInUpdate(BaseModel):
    """Schema for updating a check-in"""
    readiness_score: Optional[int] = Field(None, ge=1, le=100)
    fatigue: Optional[int] = Field(None, ge=1, le=10)
    stress: Optional[int] = Field(None, ge=1, le=10)
    soreness: Optional[int] = Field(None, ge=1, le=10)
    date: Optional[datetime] = None


class CheckIn(CheckInBase):
    """Schema for check-in response"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    athlete_id: int
