from app.api.endpoints import auth, athletes, sessions, sleep_logs, checkins, insights, mcp, coaches
from app.core.auth import get_current_user, RoleChecker

api_router = APIRouter()

# Authentication (public)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Protected Endpoints
api_router.include_router(athletes.router, prefix="/athletes", tags=["Athletes"])
api_router.include_router(insights.router, prefix="/athletes", tags=["Insights"], dependencies=[Depends(get_current_user)])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"], dependencies=[Depends(get_current_user)])
api_router.include_router(sleep_logs.router, prefix="/sleep-logs", tags=["Sleep Logs"], dependencies=[Depends(get_current_user)])
api_router.include_router(checkins.router, prefix="/checkins", tags=["Check-ins"], dependencies=[Depends(get_current_user)])
api_router.include_router(mcp.router, prefix="/mcp", tags=["System"], dependencies=[Depends(get_current_user)])

# Role-Protected (Coach Only)
api_router.include_router(
    coaches.router, 
    prefix="/coaches", 
    tags=["Coaches"], 
    dependencies=[Depends(RoleChecker(allowed_roles=["coach"]))]
)
