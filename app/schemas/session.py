from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


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
