from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


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
