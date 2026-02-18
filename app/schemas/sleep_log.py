from pydantic import BaseModel, ConfigDict, Field
import datetime
from typing import Optional


class SleepLogBase(BaseModel):
    """Base sleep log schema"""
    sleep_hours: float = Field(..., ge=0, le=24, description="Hours of sleep (0-24)")
    sleep_quality: Optional[int] = Field(None, ge=1, le=5, description="Sleep quality (1-5)")
    date: Optional[datetime.date] = Field(default_factory=datetime.date.today)


class SleepLogCreate(SleepLogBase):
    """Schema for creating a sleep log"""
    athlete_id: int


class SleepLogUpdate(BaseModel):
    """Schema for updating a sleep log"""
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    date: Optional[datetime.date] = None


class SleepLog(SleepLogBase):
    """Schema for sleep log response"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    athlete_id: int
