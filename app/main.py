from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.api_v1.api import api_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="IronMind Coach API - Data-driven Triathlon Training Insights",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "phase": "Phase 2: Complete CRUD & Core Entities",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "phase": "2"}
