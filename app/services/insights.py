from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import List, Optional
from app.models.models import Session as TrainingSession, SleepLog
from app.schemas.insights import ReadinessInsight, ImpactReason, AnalyticsTrends, LoadTrend

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


def compute_readiness(
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
            "sleep_quality": sleep_qual
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
