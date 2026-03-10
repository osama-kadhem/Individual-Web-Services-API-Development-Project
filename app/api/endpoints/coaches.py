from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.insights import CoachRoster
from app.services import insights as insight_service

router = APIRouter()


@router.get(
    "/roster",
    response_model=CoachRoster,
    summary="Get coaching roster",
    description=(
        "Returns every registered athlete with their live readiness score, ACWR, "
        "readiness band, and training prescription tier — sorted by readiness score "
        "ascending so the athletes needing most attention appear at the top. "
        "Also returns band-level counts (High / Medium / Low) for a quick squad overview."
    ),
)
def get_roster(db: Session = Depends(get_db)):
    return insight_service.get_coach_roster(db)
