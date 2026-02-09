from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


# Phase 1: Athlete Schemas Only
class AthleteBase(BaseModel):
    """Base athlete schema"""
    name: str
    email: EmailStr
    age: Optional[int] = None


class AthleteCreate(AthleteBase):
    """Schema for creating an athlete"""
    pass


class Athlete(AthleteBase):
    """Schema for athlete response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
