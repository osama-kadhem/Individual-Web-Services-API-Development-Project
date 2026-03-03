import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.errors import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.db.session import engine, Base
from app.api.v1.api import api_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Athletes",
        "description": "Manage athlete profiles, registration, and basic information.",
    },
    {
        "name": "Insights",
        "description": "Evidence-based readiness scoring, ACWR analysis, and performance simulation.",
    },
    {
        "name": "Sessions",
        "description": "Log and track training workouts across different sports.",
    },
    {
        "name": "Sleep Logs",
        "description": "Monitor recovery through sleep duration and quality metrics.",
    },
    {
        "name": "Check-ins",
        "description": "Daily subjective wellness tracking including fatigue, stress, and mood.",
    },
    {
        "name": "System",
        "description": "Core API health and versioning information.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_tags=tags_metadata,
    description=(
        "A specialized REST API for high-performance triathlon training and recovery analytics. "
        "Built on evidence-based sports science metrics like Acute:Chronic Workload Ratio (ACWR)."
    ),
    docs_url=None,
    redoc_url=None, # Disabled to serve custom-styled ReDoc
)

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    """Custom-themed Swagger UI."""
    theme_url = "/static/css/swagger-theme.css"
    extra_head = (
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700'
        f'&family=Outfit:wght@600;800&display=swap" rel="stylesheet">'
        f'<link rel="stylesheet" href="{theme_url}">'
    )
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} | Developer Console",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )
    content = html.body.decode().replace("</head>", f"{extra_head}</head>")
    return HTMLResponse(content=content)


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_ui():
    """Custom-themed ReDoc interface."""
    return FileResponse(os.path.join(static_dir, "redoc.html"))


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get(
    "/health",
    tags=["System"],
    summary="API Health Status",
)
def health_check():
    return {"status": "healthy", "version": settings.VERSION}
