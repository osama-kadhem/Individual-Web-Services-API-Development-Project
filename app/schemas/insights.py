from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Dict

class ImpactReason(BaseModel):
    reason: str
    impact: float  # e.g., -10, +5

class ReadinessInsight(BaseModel):
    athlete_id: int
    date: date
    readiness_score: int = Field(..., ge=0, le=100)
    readiness_band: str  # "Low", "Medium", "High"
    signals: Dict[str, float]  # 7-day load, 28-day avg, last sleep, etc.
    top_reasons: List[ImpactReason]
    links: Dict[str, str]  # HATEOAS

class LoadTrend(BaseModel):
    date: date
    load: float

class AnalyticsTrends(BaseModel):
    athlete_id: int
    load_summary: Dict[str, float]
    trends: List[LoadTrend]
    links: Dict[str, str]

class WhatIfRequest(BaseModel):
    planned_session_duration: float
    planned_session_intensity: int
    expected_sleep_hours: float
    expected_sleep_quality: int

class WhatIfResponse(BaseModel):
    original_readiness: ReadinessInsight
    projected_readiness: ReadinessInsight
    change_description: str
