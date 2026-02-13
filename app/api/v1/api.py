from fastapi import APIRouter
from app.api.endpoints import athletes, sessions, sleep_logs, checkins

api_router = APIRouter()

api_router.include_router(athletes.router, prefix="/athletes", tags=["Athletes"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(sleep_logs.router, prefix="/sleep-logs", tags=["Sleep Logs"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["Check-ins"])
