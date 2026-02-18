from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.db.session import engine, Base
from app.api.v1.api import api_router
import os

from fastapi.openapi.docs import get_swagger_ui_html

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="IronMind Coach API - Data-driven Triathlon Training Insights",
    docs_url=None, # Disable default docs
    redoc_url="/redoc"
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    ironman_css = """
    <style>
        body { background-color: #0A0F14 !important; margin: 0; padding: 0; }
        .swagger-ui { background-color: #0A0F14 !important; color: #FFFFFF !important; padding-bottom: 50px; }
        .swagger-ui .topbar { display: none; }
        
        /* Typography */
        .swagger-ui .info .title, .swagger-ui .info p, .swagger-ui .info li, .swagger-ui .info td { 
            color: #FFFFFF !important; 
            font-family: 'Inter', sans-serif !important; 
        }
        
        /* Section Tags */
        .swagger-ui .opblock-tag { 
            color: #E31837 !important; 
            border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important; 
            font-family: 'Outfit', sans-serif !important; 
            font-weight: 700 !important;
            padding: 20px 0 !important; 
        }
        
        /* Operation Blocks */
        .swagger-ui .opblock { 
            border-radius: 16px !important; 
            border: 1px solid rgba(255, 255, 255, 0.08) !important; 
            background: rgba(255, 255, 255, 0.03) !important; 
            margin-bottom: 20px !important; 
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3) !important;
            backdrop-filter: blur(10px) !important;
            overflow: hidden !important;
        }
        
        .swagger-ui .opblock .opblock-summary { padding: 15px 24px !important; }
        .swagger-ui .opblock-summary-path { color: #FFFFFF !important; font-weight: 600 !important; }
        .swagger-ui .opblock-summary-description { color: #8E9AAF !important; }
        
        /* Headers in expanded blocks (fixing the white bars) */
        .swagger-ui .opblock-section-header {
            background: rgba(255, 255, 255, 0.05) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding: 12px 24px !important;
        }
        .swagger-ui .opblock-section-header h4 { color: #FFFFFF !important; }
        
        .swagger-ui .opblock-body { background: transparent !important; }
        
        /* Parameters & Tables */
        .swagger-ui table thead tr th { color: #8E9AAF !important; border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important; }
        .swagger-ui .parameter__name, .swagger-ui .parameter__type { color: #FFFFFF !important; }
        .swagger-ui .opblock-description-wrapper p { color: #8E9AAF !important; }
        
        /* Buttons */
        .swagger-ui .btn.execute { 
            background-color: #E31837 !important; 
            border-color: #E31837 !important; 
            color: #FFFFFF !important;
            border-radius: 12px !important; 
            font-weight: 700 !important;
            padding: 10px 30px !important;
            box-shadow: 0 4px 15px rgba(227, 24, 55, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        .swagger-ui .btn.execute:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(227, 24, 55, 0.4) !important; }
        
        .swagger-ui .btn.try-out__btn { 
            background-color: #FFB800 !important; 
            border-color: #FFB800 !important; 
            color: #000000 !important; 
            font-weight: 700 !important; 
            border-radius: 8px !important; 
        }
        
        .swagger-ui .btn.authorize { color: #FFB800 !important; border-color: #FFB800 !important; border-radius: 8px !important; }
        .swagger-ui .btn.authorize svg { fill: #FFB800 !important; }
        
        /* Input & Select */
        .swagger-ui select, .swagger-ui input, .swagger-ui textarea { 
            background: rgba(255, 255, 255, 0.05) !important; 
            color: #FFFFFF !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important; 
            border-radius: 8px !important; 
            padding: 8px 12px !important;
        }
        
        /* Models */
        .swagger-ui section.models { 
            border: 1px solid rgba(255, 255, 255, 0.08) !important; 
            background: rgba(255, 255, 255, 0.02) !important; 
            border-radius: 16px !important; 
        }
        .swagger-ui section.models h4 { color: #8E9AAF !important; border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important; }
        .swagger-ui .model-box { background: rgba(0, 0, 0, 0.2) !important; border-radius: 8px !important; }
        
        /* Code Blocks */
        .swagger-ui .microlight { background: #0F172A !important; border-radius: 12px !important; color: #CBD5E1 !important; }
        
        /* Status Codes */
        .swagger-ui .response-col_status { color: #FFFFFF !important; font-weight: 700 !important; }
        .swagger-ui .tabli button.active { color: #E31837 !important; border-bottom: 2px solid #E31837 !important; }
    </style>
    """
    from fastapi.responses import HTMLResponse
    
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Console",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )
    
    new_content = html.body.decode().replace("</head>", f"{ironman_css}</head>")
    return HTMLResponse(content=new_content)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    """Serve the dashboard"""
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "phase": "4"}
