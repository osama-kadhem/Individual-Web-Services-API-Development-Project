from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import athletes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Phase 1: Basic REST API for athlete management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Phase 1: Include only athletes router
app.include_router(
    athletes.router,
    prefix=f"{settings.API_V1_STR}/athletes",
    tags=["Athletes"]
)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "IronMind Coach API - Phase 1",
        "version": settings.VERSION,
        "phase": "Phase 1: Basic Setup",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "phase": "1"}
