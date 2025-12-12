import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger
from app.routers import (
    device_control, discovery, automations, 
    file_management, system, dashboards, diagnostics
)

# Configure logger
logger = get_logger("app")

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(device_control.router)
app.include_router(discovery.router)
app.include_router(automations.router)
app.include_router(file_management.router)
app.include_router(system.router)
app.include_router(dashboards.router)
app.include_router(diagnostics.router)

@app.get("/", tags=["info"])
async def root():
    """Root endpoint info."""
    return {
        "name": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["info"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}

if __name__ == "__main__":
    logger.info(f"🚀 Starting {settings.APP_TITLE} v{settings.APP_VERSION}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=True
    )
