from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import List, Optional
from app.models.models import Session as TrainingSession, SleepLog, Athlete
from app.schemas.insights import (
    ReadinessInsight, ImpactReason, AnalyticsTrends, LoadTrend,
    TrainingPrescription, RosterEntry, CoachRoster,
)
from app.services.weather import get_current_weather

# Sports Science Metrics & References:
# [1] Gabbett, T.J. (2016) ACWR thresholds for injury prevention.
# [2] Hulin, B.T., et al. (2016) Acute:chronic workload ratios.
# [3] Foster, C., et al. (2001) Session RPE method for training load.
# [4] Mah, C.D., et al. (2011) Sleep extension and athletic performance.


def calculate_daily_load(db: Session, athlete_id: int, target_date: date) -> float:
    """Calculates total training load (sRPE) for a specific day."""
    sessions = db.query(TrainingSession).filter(
        TrainingSession.athlete_id == athlete_id,
        func.date(TrainingSession.date) == target_date
    ).all()
    # Load = duration (min) × intensity (1-10 RPE)
    return sum((s.duration or 0) * (s.intensity or 0) for s in sessions)


def get_training_load_history(db: Session, athlete_id: int, days: int, target_date: date) -> List[float]:
    """Retrieves training load history for calculation of moving averages."""
    history = []
    for i in range(days):
        d = target_date - timedelta(days=i)
        history.append(calculate_daily_load(db, athlete_id, d))
    return history


async def compute_readiness(
    db: Session, 
    athlete_id: int, 
    target_date: date,
    mock_sleep: Optional[float] = None,
    mock_quality: Optional[int] = None,
    mock_session_load: float = 0
) -> ReadinessInsight:
    """Computes an athlete's readiness score based on ACWR and wellness signals."""
    # 1. Acute/Chronic Workload (7d vs 28d)
    loads = get_training_load_history(db, athlete_id, 28, target_date)
    
    acute_load = (sum(loads[:7]) + mock_session_load) / 7
    chronic_load = sum(loads) / 28
    
    acwr = 1.0
    if chronic_load > 0:
        acwr = round(acute_load / chronic_load, 2)

    # 2. Recovery Factors (Sleep)
    sleep_entry = db.query(SleepLog).filter(
        SleepLog.athlete_id == athlete_id,
        SleepLog.date == target_date
    ).first()
    
    sleep_hrs = mock_sleep if mock_sleep is not None else (sleep_entry.sleep_hours if sleep_entry else 8.0)
    sleep_qual = mock_quality if mock_quality is not None else (sleep_entry.sleep_quality if sleep_entry else 4)

    # 3. Readiness Scoring Logic
    score = 70.0  # Baseline
    reasons = []

    # ACWR threshold adjustments
    if 0.8 <= acwr <= 1.3:
        score += 15
        reasons.append(ImpactReason(reason="Optimal training load balance (ACWR 0.8-1.3)", impact=15))
    elif acwr > 1.5:
        score -= 20
        reasons.append(ImpactReason(reason="Elevated injury risk (high ACWR > 1.5)", impact=-20))
    elif acwr < 0.5:
        score -= 10
        reasons.append(ImpactReason(reason="Under-training / deconditioning risk", impact=-10))

    # Sleep adjustments
    if sleep_hrs >= 8.0:
        score += 10
        reasons.append(ImpactReason(reason="Excellent sleep duration (>=8h)", impact=10))
    elif sleep_hrs < 6.5:
        score -= 15
        reasons.append(ImpactReason(reason="Inadequate recovery sleep (<6.5h)", impact=-15))

    if sleep_qual >= 4:
        score += 5
        reasons.append(ImpactReason(reason="High sleep quality", impact=5))

    # 4. Weather Factors (External API Integration)
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    weather_info = None
    if athlete and athlete.city:
        weather_info = await get_current_weather(athlete.city)
        if weather_info:
            if weather_info["temp"] > 30.0:
                score -= 20
                reasons.append(ImpactReason(
                    reason=f"Extreme Heat Stress ({weather_info['temp']}°C in {athlete.city})", 
                    impact=-20
                ))
            if weather_info["humidity"] > 80.0:
                score -= 10
                reasons.append(ImpactReason(
                    reason=f"High Humidity Stress ({weather_info['humidity']}% in {athlete.city})", 
                    impact=-10
                ))

    # Final normalization
    final_score = max(0, min(100, int(score)))
    band = "High" if final_score >= 80 else ("Medium" if final_score >= 50 else "Low")

    return ReadinessInsight(
        athlete_id=athlete_id,
        date=target_date,
        readiness_score=final_score,
        readiness_band=band,
        signals={
            "acute_load_7d": round(acute_load * 7, 1),
            "chronic_load_28d": round(chronic_load * 7, 1), # scaled to weekly avg
            "acwr": acwr,
            "sleep_hours": sleep_hrs,
            "sleep_quality": sleep_qual,
            "weather": weather_info
        },
        top_reasons=reasons,
        links={
            "self": f"/api/v1/athletes/{athlete_id}/insights/readiness",
            "sessions": f"/api/v1/sessions/?athlete_id={athlete_id}"
        }
    )


def get_analytics(db: Session, athlete_id: int) -> AnalyticsTrends:
    """Calculates 14-day training load distribution."""
    today = date.today()
    trends = []
    total_load = 0
    
    for i in range(15): # 0 to 14 days ago
        d = today - timedelta(days=i)
        load = calculate_daily_load(db, athlete_id, d)
        trends.append(LoadTrend(date=d, load=load))
        total_load += load
        
    trends.reverse()
    
    return AnalyticsTrends(
        athlete_id=athlete_id,
        load_summary={
            "total_14d_load": total_load,
            "avg_daily_load": round(total_load / 14, 1)
        },
        trends=trends,
        links={
            "self": f"/api/v1/athletes/{athlete_id}/analytics/trends",
            "readiness": f"/api/v1/athletes/{athlete_id}/insights/readiness"
        }
    )


async def get_training_prescription(db: Session, athlete_id: int) -> TrainingPrescription:
    """
    Derives a structured weekly training prescription from the athlete's current
    ACWR and readiness score.

    Prescription tiers (based on Gabbett 2016 & Mujika et al. 2018):
    - Rest:     readiness < 40  → complete rest, no training
    - Recover:  ACWR > 1.5     → reduce load by 20%, cap RPE at 5
    - Maintain: ACWR 0.8–1.3   → keep current load, cap RPE at 8
    - Build:    ACWR < 0.8     → increase load by 10%, cap RPE at 9
    """
    today = date.today()
    readiness = await compute_readiness(db, athlete_id=athlete_id, target_date=today)
    acwr = readiness.signals["acwr"]
    score = readiness.readiness_score

    if score < 40:
        prescription = "Rest"
        target_sessions = 0
        intensity_cap = 0
        load_change = -100.0
        rationale = (
            "Readiness score is critically low. Full rest is prescribed to prevent "
            "overtraining injury. Resume light activity when score exceeds 50."
        )
    elif acwr > 1.5:
        prescription = "Recover"
        target_sessions = 2
        intensity_cap = 5
        load_change = -20.0
        rationale = (
            f"ACWR of {acwr} exceeds the 1.5 danger threshold (Gabbett, 2016). "
            "Reduce weekly volume by 20% and cap session RPE at 5 to allow adaptation."
        )
    elif 0.8 <= acwr <= 1.3:
        prescription = "Maintain"
        target_sessions = 4
        intensity_cap = 8
        load_change = 0.0
        rationale = (
            f"ACWR of {acwr} sits in the optimal 0.8–1.3 window. Maintain current "
            "training volume. High-intensity sessions permitted up to RPE 8."
        )
    else:
        # acwr < 0.8 — under-trained
        prescription = "Build"
        target_sessions = 5
        intensity_cap = 9
        load_change = +10.0
        rationale = (
            f"ACWR of {acwr} is below 0.8, indicating under-loading. Increase "
            "weekly load by ~10% with progressive intensity up to RPE 9."
        )

    return TrainingPrescription(
        athlete_id=athlete_id,
        date=today,
        acwr=acwr,
        readiness_score=score,
        prescription=prescription,
        target_weekly_sessions=target_sessions,
        max_session_intensity=intensity_cap,
        target_load_change_pct=load_change,
        rationale=rationale,
        links={
            "self": f"/api/v1/athletes/{athlete_id}/training-prescription",
            "readiness": f"/api/v1/athletes/{athlete_id}/insights/readiness",
            "trends": f"/api/v1/athletes/{athlete_id}/analytics/trends",
        }
    )


async def get_coach_roster(db: Session) -> CoachRoster:
    """
    Returns a full coaching overview: every athlete with their live readiness
    score, band, ACWR, and training prescription — sorted by readiness score
    ascending so the athletes needing most attention appear first.
    """
    athletes = db.query(Athlete).all()
    today = date.today()
    roster_entries = []

    for athlete in athletes:
        readiness = await compute_readiness(db, athlete_id=athlete.id, target_date=today)
        prescription_obj = await get_training_prescription(db, athlete_id=athlete.id)
        roster_entries.append(RosterEntry(
            athlete_id=athlete.id,
            name=athlete.name,
            email=athlete.email,
            readiness_score=readiness.readiness_score,
            readiness_band=readiness.readiness_band,
            acwr=readiness.signals["acwr"],
            prescription=prescription_obj.prescription,
        ))

    # Sort: athletes needing most attention (lowest score) first
    roster_entries.sort(key=lambda e: e.readiness_score)

    return CoachRoster(
        total_athletes=len(roster_entries),
        high_readiness=sum(1 for e in roster_entries if e.readiness_band == "High"),
        medium_readiness=sum(1 for e in roster_entries if e.readiness_band == "Medium"),
        low_readiness=sum(1 for e in roster_entries if e.readiness_band == "Low"),
        roster=roster_entries,
        links={
            "self": "/api/v1/coaches/roster",
        }
    )
