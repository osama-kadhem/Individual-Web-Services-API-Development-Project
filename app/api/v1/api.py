from fastapi import APIRouter, Depends
from app.api.endpoints import athletes, sessions, sleep_logs, checkins, insights, mcp
from app.core.auth import get_api_key

api_router = APIRouter(dependencies=[Depends(get_api_key)])

api_router.include_router(athletes.router, prefix="/athletes", tags=["Athletes"])
api_router.include_router(insights.router, prefix="/athletes", tags=["Insights"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(sleep_logs.router, prefix="/sleep-logs", tags=["Sleep Logs"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["Check-ins"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["System"])
