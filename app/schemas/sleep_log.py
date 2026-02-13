from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


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
