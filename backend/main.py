"""
Main FastAPI application for Personal Color Analysis.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.core.config import settings
from backend.api.routes import router as api_router


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered personal color analysis using computer vision and color theory",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api prefix
app.include_router(api_router, prefix="/api", tags=["API"])

# Get the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve static files (CSS, JS, assets)
if os.path.exists(FRONTEND_DIR):
    # Mount static directories
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/")
async def serve_frontend():
    """Serve the main frontend HTML page."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {
            "message": "Welcome to Personal Color Analysis API",
            "docs": "/docs",
            "health": "/api/health",
        }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon if it exists."""
    favicon_path = os.path.join(FRONTEND_DIR, "assets", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"message": "No favicon"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

