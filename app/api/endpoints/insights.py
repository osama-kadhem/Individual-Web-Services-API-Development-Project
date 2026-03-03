from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.db.session import get_db
from app.schemas.insights import ReadinessInsight, AnalyticsTrends, WhatIfRequest, WhatIfResponse
from app.services import insights as insight_service
from app.crud import crud_athlete

router = APIRouter()


@router.get(
    "/{athlete_id}/insights/readiness",
    response_model=ReadinessInsight,
    summary="Get athlete readiness",
    description="Calculates training readiness using Acute:Chronic Workload Ratio (ACWR) and recovery metrics.",
)
def get_readiness_insight(
    athlete_id: int,
    target_date: Optional[date] = Query(None, description="Reference date for analysis (defaults to today)."),
    db: Session = Depends(get_db)
):
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    analysis_date = target_date or date.today()
    return insight_service.compute_readiness(db, athlete_id=athlete_id, target_date=analysis_date)


@router.get(
    "/{athlete_id}/analytics/trends",
    response_model=AnalyticsTrends,
    summary="Get training trends",
    description="Retrieves training load distribution and averages over the last 14 days.",
)
def get_training_trends(athlete_id: int, db: Session = Depends(get_db)):
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
        
    return insight_service.get_analytics(db, athlete_id=athlete_id)


@router.post(
    "/{athlete_id}/whatif/readiness",
    response_model=WhatIfResponse,
    summary="Simulate future readiness",
    description="Projects health scores based on planned training sessions and expected sleep.",
)
def simulate_readiness(athlete_id: int, whatif: WhatIfRequest, db: Session = Depends(get_db)):
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    today = date.today()
    
    # Original baseline
    original = insight_service.compute_readiness(db, athlete_id=athlete_id, target_date=today)
    
    # Projected
    projected = insight_service.compute_readiness(
        db, 
        athlete_id=athlete_id, 
        target_date=today,
        mock_sleep=whatif.expected_sleep_hours,
        mock_quality=whatif.expected_sleep_quality,
        mock_session_load=whatif.planned_session_duration * whatif.planned_session_intensity
    )
    
    diff = projected.readiness_score - original.readiness_score
    tone = "improve" if diff >= 0 else "reduce"
    desc = f"This plan is projected to {tone} your readiness score by {abs(diff)} points compared to your current baseline."
    
    return WhatIfResponse(
        athlete_id=athlete_id,
        original_readiness=original,
        projected_readiness=projected,
        change_description=desc
    )
