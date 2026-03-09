from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional


class SessionBase(BaseModel):
    """Base session schema"""
    sport: str = Field(..., min_length=1, max_length=60, description="Sport type (e.g. Running, Cycling, Swimming)")
    duration: float = Field(..., gt=0, le=600, description="Duration in minutes (max 600 = 10 hours)")
    distance: Optional[float] = Field(None, ge=0, le=500, description="Distance in km (optional, max 500)")
    intensity: Optional[int] = Field(None, ge=1, le=10, description="RPE intensity (1-10)")
    date: Optional[datetime] = None

    @field_validator("sport")
    @classmethod
    def sport_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("sport must not be blank or whitespace only")
        return v.strip()


class SessionCreate(SessionBase):
    """Schema for creating a session"""
    athlete_id: int = Field(..., gt=0)


class SessionUpdate(BaseModel):
    """Schema for updating a session – all fields optional (partial update)."""
    sport: Optional[str] = Field(None, min_length=1, max_length=60)
    duration: Optional[float] = Field(None, gt=0, le=600)
    distance: Optional[float] = Field(None, ge=0, le=500)
    intensity: Optional[int] = Field(None, ge=1, le=10)
    date: Optional[datetime] = None

    @field_validator("sport")
    @classmethod
    def sport_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("sport must not be blank or whitespace only")
        return v.strip() if v else v


class Session(SessionBase):
    """Schema for session response"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    athlete_id: int
