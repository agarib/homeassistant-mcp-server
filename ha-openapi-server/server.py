# v4.1.4 cache-bust:20260826a
#!/usr/bin/env python3
"""
Home Assistant OpenAPI Server v4.1.4
Main entry point for the application.
"""
import uvicorn
import os
import sys
import logging
import subprocess

# Load code from /config/ha-openapi-server (editable, no Docker rebuild needed)
# Falls back to /app (Docker-baked) if /config/ is unavailable
CONFIG_APP_PATH = "/config/ha-openapi-server"
if os.path.isdir(os.path.join(CONFIG_APP_PATH, "app")):
    sys.path.insert(0, CONFIG_APP_PATH)
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------------------------------------------------------
# AUTO-INSTALL DEPENDENCIES (Self-Healing)
# -----------------------------------------------------------------------------
def install_dependencies():
    """Install dependencies if they are missing (fallback for non-rebuilt containers)."""
    missing = []
    try:
        import pydantic_settings
    except ImportError:
        missing.append("pydantic-settings>=2.12.0")
        missing.append("pydantic>=2.0.0")

    for lib in ["pandas", "numpy", "matplotlib", "seaborn"]:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)

    if missing:
        print(f"Missing dependencies: {missing}. Auto-installing...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--break-system-packages"
            ] + missing)
            print("Dependencies installed successfully.")
        except Exception as e:
            print(f"Failed to auto-install dependencies: {e}")

install_dependencies()

# Configure basic logging for startup before app takes over
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("__main__")

if __name__ == "__main__":
    from app.core.config import settings

    logger.info(f"{settings.APP_TITLE} v{settings.APP_VERSION}")
    logger.info(f"Config Path: {settings.HA_CONFIG_PATH}")
    logger.info(f"HA API URL: {settings.HA_URL}")
    logger.info(f"Port: {settings.PORT}")

    if settings.SUPERVISOR_TOKEN:
        logger.info("Supervisor Token: Present")
    else:
        logger.warning("Supervisor Token: Check logs or env vars")

    logger.info(f"Starting {settings.APP_TITLE} v{settings.APP_VERSION}")
    logger.info(f"Server available at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"API docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"OpenAPI spec: http://{settings.HOST}:{settings.PORT}/openapi.json")
    logger.info("All endpoints working!")
    logger.info("WebSocket enabled for dashboard operations")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=False
    )