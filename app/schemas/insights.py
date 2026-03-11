from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Dict, Any

class ImpactReason(BaseModel):
    reason: str
    impact: float  # e.g., -10, +5

class ReadinessInsight(BaseModel):
    athlete_id: int
    date: date
    readiness_score: int = Field(..., ge=0, le=100)
    readiness_band: str  # "Low", "Medium", "High"
    signals: Dict[str, Any]  # 7-day load, 28-day avg, weather info, etc.
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


class TrainingPrescription(BaseModel):
    """Evidence-based weekly training recommendation derived from ACWR and readiness."""
    athlete_id: int
    date: date
    acwr: float
    readiness_score: int
    prescription: str           # e.g. "Build", "Maintain", "Recover", "Rest"
    target_weekly_sessions: int
    max_session_intensity: int  # RPE cap (1-10)
    target_load_change_pct: float  # e.g. +10.0 or -20.0
    rationale: str
    links: Dict[str, str]


class RosterEntry(BaseModel):
    """Compact athlete + live readiness summary for the coach's roster view."""
    athlete_id: int
    name: str
    email: str
    readiness_score: int
    readiness_band: str
    acwr: float
    prescription: str


class CoachRoster(BaseModel):
    total_athletes: int
    high_readiness: int
    medium_readiness: int
    low_readiness: int
    roster: List[RosterEntry]
    links: Dict[str, str]
