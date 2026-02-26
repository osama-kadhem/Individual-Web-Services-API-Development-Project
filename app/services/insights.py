"""
IronMind Coach API - Readiness Insights Service
================================================
This module computes athlete readiness scores using evidence-based sports
science metrics. All methods are grounded in peer-reviewed research as cited
below.

REFERENCES
----------
[1] Gabbett, T.J. (2016) 'The training-injury prevention paradox: should athletes
    be training smarter and harder?', British Journal of Sports Medicine,
    50(5), pp. 273-280. https://doi.org/10.1136/bjsports-2015-095788

[2] Hulin, B.T., Gabbett, T.J., Lawson, D.W., Caputi, P. and Sampson, J.A. (2016)
    'The acute:chronic workload ratio predicts injury: high chronic workload may
    decrease injury risk in elite rugby league players', British Journal of Sports
    Medicine, 50(4), pp. 231-236. https://doi.org/10.1136/bjsports-2015-094817

[3] Foster, C., Florhaug, J.A., Franklin, J., Gottschall, L., Hrovatin, L.A.,
    Parker, S., Doleshal, P. and Dodge, C. (2001) 'A new approach to monitoring
    exercise training', Journal of Strength and Conditioning Research,
    15(1), pp. 109-115.

[4] Mah, C.D., Mah, K.E., Kezirian, E.J. and Dement, W.C. (2011) 'The effects
    of sleep extension on the athletic performance of collegiate basketball players',
    Sleep, 34(7), pp. 943-950. https://doi.org/10.5665/SLEEP.1132

[5] Buysse, D.J., Reynolds, C.F., Monk, T.H., Berman, S.R. and Kupfer, D.J. (1989)
    'The Pittsburgh Sleep Quality Index: a new instrument for psychiatric practice
    and research', Psychiatry Research, 28(2), pp. 193-213.
    https://doi.org/10.1016/0165-1781(89)90047-4
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import List, Optional
from app.models.models import Session as TrainingSession, SleepLog, CheckIn
from app.schemas.insights import ReadinessInsight, ImpactReason, AnalyticsTrends, LoadTrend, WhatIfRequest


def calculate_daily_load(db: Session, athlete_id: int, target_date: date) -> float:
    """
    Calculate total training load for a specific day using the Session RPE (sRPE) method.

    Training Load = Session Duration (minutes) × Perceived Intensity (RPE 1–10)

    This is known as the 'Foster Method' or Session RPE (sRPE), a validated
    approach for quantifying internal training load in endurance athletes.

    Reference:
        Foster et al. (2001) [3]
    """
    sessions = db.query(TrainingSession).filter(
        TrainingSession.athlete_id == athlete_id,
        func.date(TrainingSession.date) == target_date
    ).all()
    # sRPE = duration (min) × intensity (1–10 RPE scale) [3]
    return sum((s.duration or 0) * (s.intensity or 0) for s in sessions)


def get_load_history(db: Session, athlete_id: int, end_date: date, days: int) -> List[float]:
    """Get daily sRPE loads for the last N days ending on end_date."""
    loads = []
    for i in range(days):
        d = end_date - timedelta(days=i)
        loads.append(calculate_daily_load(db, athlete_id, d))
    return loads


def compute_readiness(
    db: Session,
    athlete_id: int,
    target_date: date,
    mock_sleep: Optional[float] = None,
    mock_quality: Optional[int] = None,
    mock_session_load: float = 0
) -> ReadinessInsight:
    """
    Compute athlete readiness score using the Acute:Chronic Workload Ratio (ACWR)
    framework combined with subjective sleep and wellness metrics.

    ACWR Framework:
    ---------------
    - Acute Load  = 7-day rolling average of daily sRPE load
    - Chronic Load = 28-day rolling average of daily sRPE load
    - ACWR = Acute Load / Chronic Load

    Evidence-based ACWR thresholds (Gabbett, 2016 [1]; Hulin et al., 2016 [2]):
        0.8 – 1.3  → "Sweet spot": low injury risk, optimal adaptation
        > 1.5      → "Danger zone": significantly elevated injury/fatigue risk
        < 0.5      → Under-training: insufficient stimulus for adaptation

    Sleep Metrics:
    --------------
    Sleep duration thresholds based on Mah et al. (2011) [4], which demonstrated
    measurable performance improvements with ≥8 hours sleep in collegiate athletes.
    Sleep quality scale (1–5) is conceptually aligned with the Pittsburgh Sleep
    Quality Index (PSQI) validated by Buysse et al. (1989) [5].

    Subjective Wellness:
    --------------------
    Soreness and stress scores (1–10) are self-reported subjective wellness markers,
    consistent with athlete monitoring best-practice frameworks.
    """

    # --- 1. Compute ACWR ---
    # Acute load: 7-day average sRPE — represents recent training stimulus [1][3]
    last_7_days = get_load_history(db, athlete_id, target_date - timedelta(days=1), 7)
    # Chronic load: 28-day average sRPE — represents accumulated fitness base [1][3]
    last_28_days = get_load_history(db, athlete_id, target_date - timedelta(days=1), 28)

    acute_load = sum(last_7_days) / 7
    chronic_load = max(sum(last_28_days) / 28, 1.0)  # Floor at 1 to prevent division by zero
    acwr = acute_load / chronic_load

    # --- 2. Sleep Data ---
    # Most recent sleep log for this athlete on or before target_date
    sleep = db.query(SleepLog).filter(
        SleepLog.athlete_id == athlete_id,
        SleepLog.date <= target_date
    ).order_by(SleepLog.date.desc()).first()

    # Default to 7.0h / quality 3 if no sleep data logged
    sleep_h = mock_sleep if mock_sleep is not None else (sleep.sleep_hours if sleep else 7.0)
    sleep_q = mock_quality if mock_quality is not None else (sleep.sleep_quality if sleep else 3)

    # --- 3. Check-in Data ---
    checkin = db.query(CheckIn).filter(
        CheckIn.athlete_id == athlete_id,
        CheckIn.date == target_date
    ).first()

    # --- 4. Score Calculation ---
    # Baseline score of 70 reflects a neutral/average readiness state.
    # Adjustments are applied based on evidence-based thresholds.
    score = 70
    reasons = []

    # ACWR Impact — based on Gabbett (2016) [1] and Hulin et al. (2016) [2]
    if 0.8 <= acwr <= 1.3:
        # Sweet spot: athlete is well-adapted to current load
        score += 10
        reasons.append(ImpactReason(reason="Optimal training load balance (ACWR 0.8–1.3)", impact=10.0))
    elif acwr > 1.5:
        # Danger zone: acute load spike significantly exceeds chronic fitness base
        # Hulin et al. (2016) found ACWR ≥1.5 associated with significantly elevated injury risk [2]
        score -= 20
        reasons.append(ImpactReason(reason="High fatigue risk (Excessive recent load, ACWR > 1.5)", impact=-20.0))
    elif acwr < 0.5:
        # Under-training: insufficient recent load relative to fitness base
        score -= 5
        reasons.append(ImpactReason(reason="Under-training (Low recent load, ACWR < 0.5)", impact=-5.0))

    # Sleep Duration Impact — based on Mah et al. (2011) [4]
    # Athletes sleeping ≥8h showed significant sprint speed and accuracy improvements
    if sleep_h >= 8:
        score += 10
        reasons.append(ImpactReason(reason="Excellent sleep duration (≥8h, optimal per Mah et al., 2011)", impact=10.0))
    elif sleep_h < 6:
        # Chronic sleep restriction <6h associated with >30% performance impairment
        score -= 15
        reasons.append(ImpactReason(reason="Poor sleep duration (<6h, significant impairment risk)", impact=-15.0))

    # Sleep Quality Impact — scale aligned with PSQI conceptual framework [5]
    # PSQI uses a 0–21 score; our 1–5 quality scale maps to its subjective component
    if sleep_q >= 4:
        score += 5
        reasons.append(ImpactReason(reason="High sleep quality (score ≥4/5)", impact=5.0))
    elif sleep_q <= 2:
        score -= 10
        reasons.append(ImpactReason(reason="Low sleep quality (score ≤2/5)", impact=-10.0))

    # Subjective Wellness Impact — soreness & stress (self-reported, 1–10 scale)
    # Consistent with subjective athlete monitoring practices
    if checkin:
        # Soreness: score of 5 = neutral, higher = more sore = negative impact
        soreness_impact = (5 - checkin.soreness) * 2
        if abs(soreness_impact) > 2:
            reasons.append(ImpactReason(reason="Muscle soreness level", impact=float(soreness_impact)))
        score += soreness_impact

        # Stress: score of 5 = neutral, higher = more stressed = negative impact
        stress_impact = (5 - checkin.stress) * 2
        if abs(stress_impact) > 2:
            reasons.append(ImpactReason(reason="Subjective stress level", impact=float(stress_impact)))
        score += stress_impact

    # --- 5. Normalise and Band ---
    final_score = max(0, min(100, int(score)))
    band = "High" if final_score > 80 else "Medium" if final_score > 50 else "Low"

    # Sort by absolute impact, return top 3 drivers
    reasons.sort(key=lambda x: abs(x.impact), reverse=True)

    return ReadinessInsight(
        athlete_id=athlete_id,
        date=target_date,
        readiness_score=final_score,
        readiness_band=band,
        signals={
            "acute_load_7d": round(acute_load, 1),
            "chronic_load_28d": round(chronic_load, 1),
            "acwr": round(acwr, 2),
            "sleep_hours": sleep_h,
            "sleep_quality": sleep_q
        },
        top_reasons=reasons[:3],
        links={
            "self": f"/api/v1/athletes/{athlete_id}/insights/readiness?date={target_date}",
            "sessions": f"/api/v1/sessions/?athlete_id={athlete_id}",
            "sleep": f"/api/v1/sleep-logs/?athlete_id={athlete_id}",
            "checkins": f"/api/v1/checkins/?athlete_id={athlete_id}",
            "whatif": f"/api/v1/athletes/{athlete_id}/whatif/readiness"
        }
    )


def get_analytics(db: Session, athlete_id: int) -> AnalyticsTrends:
    """
    Compute 14-day training load trend using daily sRPE values.

    Each day's load is calculated as Duration × Intensity (sRPE method, Foster et al., 2001 [3]).
    The 14-day window provides a practical view of recent training distribution
    and supports identification of load spikes relevant to ACWR monitoring [1][2].
    """
    today = date.today()
    trends = []
    for i in range(14, -1, -1):
        d = today - timedelta(days=i)
        load = calculate_daily_load(db, athlete_id, d)
        trends.append(LoadTrend(date=d, load=load))

    total_14d = sum(t.load for t in trends)
    avg_14d = total_14d / 14

    return AnalyticsTrends(
        athlete_id=athlete_id,
        load_summary={
            "total_14d_load": round(total_14d, 1),
            "avg_daily_load": round(avg_14d, 1)
        },
        trends=trends,
        links={
            "self": f"/api/v1/athletes/{athlete_id}/analytics/trends",
            "readiness": f"/api/v1/athletes/{athlete_id}/insights/readiness"
        }
    )
