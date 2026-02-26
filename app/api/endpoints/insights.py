from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.db.session import get_db
from app.schemas.insights import ReadinessInsight, AnalyticsTrends, WhatIfRequest, WhatIfResponse
from app.services import insights as insight_service
from app.crud import crud_athlete

router = APIRouter()

@router.get("/{athlete_id}/insights/readiness", response_model=ReadinessInsight)
def get_readiness_insight(
    athlete_id: int, 
    target_date: Optional[date] = Query(None), 
    db: Session = Depends(get_db)
):
    """
    Phase 5: Get readiness insight for an athlete.
    Includes readiness score, ACWR, and top impact factors.
    """
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    computation_date = target_date or date.today()
    return insight_service.compute_readiness(db, athlete_id, computation_date)

@router.get("/{athlete_id}/analytics/trends", response_model=AnalyticsTrends)
def get_athlete_trends(athlete_id: int, db: Session = Depends(get_db)):
    """
    Phase 5: Get training load trends and summaries for the last 14 days.
    """
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    return insight_service.get_analytics(db, athlete_id)

@router.post("/{athlete_id}/whatif/readiness", response_model=WhatIfResponse)
def what_if_readiness(
    athlete_id: int, 
    request: WhatIfRequest, 
    db: Session = Depends(get_db)
):
    """
    Phase 5: What-If Simulator.
    Project how a planned session and expected sleep will impact today's readiness.
    """
    athlete = crud_athlete.get_athlete(db, athlete_id=athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    today = date.today()
    
    # 1. Current state
    original = insight_service.compute_readiness(db, athlete_id, today)
    
    # 2. Projected state
    projected = insight_service.compute_readiness(
        db, 
        athlete_id, 
        today,
        mock_sleep=request.expected_sleep_hours,
        mock_quality=request.expected_sleep_quality,
        mock_session_load=request.planned_session_duration * request.planned_session_intensity
    )
    
    # Simple change description
    diff = projected.readiness_score - original.readiness_score
    if diff > 5:
        desc = f"Your readiness is projected to improve by {diff} points with this sleep/training plan."
    elif diff < -5:
        desc = f"This plan may reduce your readiness by {abs(diff)} points. Consider more recovery."
    else:
        desc = "Your readiness will remain stable under this plan."
        
    return WhatIfResponse(
        original_readiness=original,
        projected_readiness=projected,
        change_description=desc
    )
