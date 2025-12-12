import asyncio
import json
import logging
import httpx
import websockets
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import aiofiles

from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# HTTP Client
# ============================================================================

# Shared HTTP client
http_client = httpx.AsyncClient(
    timeout=30.0,
    headers={
        "Authorization": f"Bearer {settings.HA_TOKEN}",
        "Content-Type": "application/json"
    } if settings.HA_TOKEN else {"Content-Type": "application/json"}
)

# ============================================================================
# WebSocket Client
# ============================================================================

class HomeAssistantWebSocket:
    """WebSocket client for Home Assistant real-time communication.
    
    Handles dashboard/Lovelace operations that require WebSocket API.
    """
    
    def __init__(self, url: str, token: str):
        """Initialize WebSocket client."""
        # Fix WebSocket URL construction for supervisor access
        # REST API: http://supervisor/core/api → WebSocket: ws://supervisor/core/websocket
        base_url = url.replace("http://", "ws://").replace("https://", "wss://")
        if "/core/api" in base_url:
            # Supervisor URL - use /core/websocket
            base_url = base_url.replace("/core/api", "/core")
        self.ws_url = base_url.rstrip('/') + "/websocket"
        self.token = token
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.msg_id = 1
        self._lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """Establish WebSocket connection and authenticate."""
        try:
            self.ws = await websockets.connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10
            )
            
            # Receive auth_required message
            auth_required = json.loads(await self.ws.recv())
            if auth_required.get("type") != "auth_required":
                logger.error(f"Expected auth_required, got: {auth_required}")
                return False
            
            # Send authentication
            await self.ws.send(json.dumps({
                "type": "auth",
                "access_token": self.token
            }))
            
            # Receive auth_ok or auth_invalid
            auth_result = json.loads(await self.ws.recv())
            if auth_result.get("type") == "auth_ok":
                logger.info("✅ WebSocket authenticated successfully")
                return True
            else:
                logger.error(f"WebSocket auth failed: {auth_result}")
                return False
                
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    async def ensure_connected(self):
        """Ensure WebSocket is connected and authenticated."""
        if not self.ws:
            await self.connect()
            return

        try:
            # Check if connection is still open by trying to send ping
            await self.ws.ping()
        except Exception:
            # Connection lost, reconnect
            logger.warning("WebSocket ping failed, reconnecting...")
            await self.connect()
    
    async def call_command(self, command_type: str, **params) -> Dict[str, Any]:
        """Send command and wait for response."""
        async with self._lock:
            await self.ensure_connected()
            
            if not self.ws:
               raise Exception("Failed to connect to WebSocket")

            msg_id = self.msg_id
            self.msg_id += 1
            
            # Send command
            message = {
                "id": msg_id,
                "type": command_type,
                **params
            }
            await self.ws.send(json.dumps(message))
            logger.debug(f"📤 WS Sent: {message}")
            
            # Wait for response with matching ID
            # Verify basic loop protection or timeout could be added here
            while True:
                response_text = await self.ws.recv()
                response = json.loads(response_text)
                logger.debug(f"📥 WS Received: {response}")
                
                # Check if this is our response
                if response.get("id") == msg_id:
                    if response.get("success"):
                        return response.get("result", {})
                    else:
                        error = response.get("error", {})
                        error_message = error.get("message", str(error))
                        raise Exception(f"WebSocket command failed: {error_message}")
    
    async def close(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()

# Global WebSocket client (singleton pattern)
_ws_client: Optional[HomeAssistantWebSocket] = None

async def get_ws_client() -> HomeAssistantWebSocket:
    """Get or create WebSocket client singleton."""
    global _ws_client
    if _ws_client is None:
        _ws_client = HomeAssistantWebSocket(settings.HA_URL, settings.HA_TOKEN or "")
        await _ws_client.connect()
    return _ws_client


# ============================================================================
# Core API Client
# ============================================================================

class HomeAssistantAPI:
    """Direct access to Home Assistant API via localhost"""
    
    def __init__(self):
        self.base_url = settings.HA_URL.rstrip('/')
        
    async def call_api(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make API call to Home Assistant"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == "GET":
                response = await http_client.get(url)
            elif method.upper() == "POST":
                # Ensure data is valid JSON if provided
                response = await http_client.post(url, json=data or {})
            elif method.upper() == "DELETE":
                response = await http_client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP {e.response.status_code} for {url}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"API call failed to {url}: {e}")
            raise
    
    async def get_states(self, entity_id: Optional[str] = None) -> Union[Dict, List[Dict]]:
        """Get entity states"""
        if entity_id:
            return await self.call_api("GET", f"/states/{entity_id}")
        return await self.call_api("GET", "/states")
    
    async def call_service(
        self, 
        domain: str, 
        service: str, 
        entity_id: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Call a Home Assistant service"""
        data = kwargs.copy()
        if entity_id:
            data["entity_id"] = entity_id
        
        return await self.call_api("POST", f"/services/{domain}/{service}", data)
    
    async def get_services(self) -> Dict:
        """Get available services"""
        return await self.call_api("GET", "/services")
    
    async def get_config(self) -> Dict:
        """Get Home Assistant configuration"""
        return await self.call_api("GET", "/config")
    
    async def get_events(self) -> List[Dict]:
        """Get available event types"""
        return await self.call_api("GET", "/events")
    
    async def fire_event(self, event_type: str, event_data: Optional[Dict] = None) -> Dict:
        """Fire a custom event"""
        response = await http_client.post(
            f"{self.base_url}/events/{event_type}",
            json=event_data or {}
        )
        response.raise_for_status()
        return response.json()
    
    async def render_template(self, template: str) -> str:
        """Render a Jinja2 template"""
        # Note: /template endpoint returns text, not JSON usually
        response = await http_client.post(
            f"{self.base_url}/template",
            json={"template": template}
        )
        response.raise_for_status()
        return response.text.strip('"')

# ============================================================================
# File Manager
# ============================================================================

class FileManager:
    """File operations in HA config directory"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        
    def ha_resolve_path(self, filepath: str) -> Path:
        """Resolve and validate file path (prevents directory traversal)"""
        # Handling basic traversal protection
        path = (self.base_path / filepath).resolve()
        if not str(path).startswith(str(self.base_path)):
            raise ValueError(f"Path {filepath} is outside config directory")
        return path
    
    async def ha_read_file(self, filepath: str) -> str:
        """Read file content"""
        path = self.ha_resolve_path(filepath)
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def ha_write_file(self, filepath: str, content: str) -> str:
        """Write file content"""
        path = self.ha_resolve_path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(content)
        return f"Successfully wrote {len(content)} bytes to {filepath}"
    
    async def ha_list_directory(self, dirpath: str = "") -> List[Dict[str, str]]:
        """List directory contents"""
        path = self.ha_resolve_path(dirpath)
        if not path.is_dir():
            raise ValueError(f"{dirpath} is not a directory")
        
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": str(item.relative_to(self.base_path)).replace("\\", "/") # Ensure forward slashes
            })
        return sorted(items, key=lambda x: (x["type"], x["name"]))
    
    async def ha_delete_file(self, filepath: str) -> str:
        """Delete a file"""
        path = self.ha_resolve_path(filepath)
        if path.is_file():
            path.unlink()
            return f"Deleted {filepath}"
        raise ValueError(f"{filepath} is not a file")

# Initialize global instances
ha_api = HomeAssistantAPI()
file_mgr = FileManager(settings.HA_CONFIG_PATH)
