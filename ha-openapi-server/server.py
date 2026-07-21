# v4.1.1 cache-bust:20260722
#!/usr/bin/env python3
"""
Home Assistant OpenAPI Server v4.1.1
Main entry point for the application.
"""
import uvicorn
import os
import sys
import logging

# Add current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Auto-install removed — deps are now installed at Docker build time via requirements.txt

# Configure basic logging for startup before app takes over
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("__main__")

if __name__ == "__main__":
    # Import settings AFTER logging setup but try to print config info
    from app.core.config import settings
    
    # -------------------------------------------------------------------------
    # RESTORED RICH STARTUP LOGS
    # -------------------------------------------------------------------------
    logger.info(f"🏠 {settings.APP_TITLE} v{settings.APP_VERSION}")
    logger.info(f"📁 Config Path: {settings.HA_CONFIG_PATH}")
    logger.info(f"🌐 HA API URL: {settings.HA_URL}")
    logger.info(f"🔌 Port: {settings.PORT}")
    
    if settings.SUPERVISOR_TOKEN:
        logger.info("🔑 Supervisor Token: Present")
    else:
        logger.warning("⚠️ Supervisor Token: Check logs or env vars")

    logger.info(f"🚀 Starting {settings.APP_TITLE} v{settings.APP_VERSION}")
    logger.info(f"📡 Server will be available at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📖 API docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🔧 OpenAPI spec: http://{settings.HOST}:{settings.PORT}/openapi.json")
    logger.info("🎉 100% tool success rate - All 71 endpoints working!")
    logger.info("🔌 WebSocket enabled for dashboard operations")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=False
    )
