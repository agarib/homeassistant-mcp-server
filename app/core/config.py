import os
import logging
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # App Info
    APP_TITLE: str = "Home Assistant OpenAPI Server"
    APP_VERSION: str = "4.0.29"
    APP_DESCRIPTION: str = "97 unified endpoints with 100% success rate - WebSocket + REST hybrid architecture for comprehensive Home Assistant control."
    
    # Server Config
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    
    # Home Assistant
    HA_URL: str = "http://supervisor/core/api"
    HA_CONFIG_PATH: Path = Path("/config")
    
    # Auth Tokens
    SUPERVISOR_TOKEN: Optional[str] = None
    HA_TOKEN: Optional[str] = None
    
    def model_post_init(self, __context):
        """Post-initialization to handle token fallback logic."""
        if not self.SUPERVISOR_TOKEN:
            self._load_token_from_s6()
            
        if self.SUPERVISOR_TOKEN and not self.HA_TOKEN:
            self.HA_TOKEN = self.SUPERVISOR_TOKEN

    def _load_token_from_s6(self):
        """Try to load SUPERVISOR_TOKEN from s6-overlay container environment files."""
        s6_token_file = "/var/run/s6/container_environment/SUPERVISOR_TOKEN"
        s6_hassio_token_file = "/var/run/s6/container_environment/HASSIO_TOKEN"
        
        try:
            if os.path.exists(s6_token_file):
                with open(s6_token_file, 'r') as f:
                    self.SUPERVISOR_TOKEN = f.read().strip()
            elif os.path.exists(s6_hassio_token_file):
                with open(s6_hassio_token_file, 'r') as f:
                    self.SUPERVISOR_TOKEN = f.read().strip()
        except Exception:
            pass

settings = Settings()
