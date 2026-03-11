from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional


class AthleteBase(BaseModel):
    """Base athlete schema"""
    name: str = Field(..., min_length=1, max_length=120, description="Athlete's full name")
    email: EmailStr
    age: Optional[int] = Field(None, ge=10, le=120, description="Age in years (10–120)")
    role: str = Field("athlete", pattern="^(athlete|coach)$", description="Role: 'athlete' or 'coach'")

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank or whitespace only")
        return v.strip()


class AthleteCreate(AthleteBase):
    """Schema for creating an athlete – requires a password."""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class AthleteUpdate(BaseModel):
    """Schema for updating an athlete – all fields are optional (partial update)."""
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=10, le=120)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("name must not be blank or whitespace only")
        return v.strip() if v else v


class Athlete(AthleteBase):
    """Schema for athlete response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    role: str
