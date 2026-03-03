from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class AthleteBase(BaseModel):
    """Base athlete schema"""
    name: str
    email: EmailStr
    age: Optional[int] = None


class AthleteCreate(AthleteBase):
    """Schema for creating an athlete – inherits all fields from AthleteBase."""


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
