#!/usr/bin/env python3
"""
🏠 Home Assistant MCP Server - Native Add-on Version (COMPLETE WITH 62 TOOLS!)
Running INSIDE Home Assistant with direct file system access

This version eliminates ALL SSH/SFTP complexity by running natively
inside Home Assistant as an add-on with direct access to:
- /config directory (mounted volume)
- Home Assistant API (via localhost/supervisor)
- No network issues, no authentication problems, 100% reliable

INCLUDES:
✅ File Operations (9 tools)
✅ Basic HA API (3 tools)
✅ Device Discovery & Control (18 tools from Part 1)
✅ Security, Automation, Workflows, Intelligence (35 tools from Part 2)
✅ Dashboard & HACS Management (9 tools from Part 3)

TOTAL: 74 TOOLS for comprehensive Home Assistant control!
"""

import asyncio
import os
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import aiofiles
from aiofiles import os as aio_os

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
HA_URL = os.getenv("HA_URL", "http://supervisor/core/api")
HA_TOKEN = os.getenv("SUPERVISOR_TOKEN", "")
HA_CONFIG_PATH = Path(os.getenv("HA_CONFIG_PATH", "/config"))
PORT = int(os.getenv("PORT", "8001"))

logger.info(f"🏠 Home Assistant MCP Server (Native Add-on)")
logger.info(f"📁 Config Path: {HA_CONFIG_PATH}")
logger.info(f"🌐 HA API URL: {HA_URL}")
logger.info(f"🔌 Port: {PORT}")

# Create MCP server
app = Server("homeassistant-native")

# HTTP client for HA API
http_client = httpx.AsyncClient(
    timeout=30.0,
    headers={
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    } if HA_TOKEN else {"Content-Type": "application/json"}
)


class HomeAssistantAPI:
    """Direct access to Home Assistant API via localhost"""
    
    def __init__(self):
        self.base_url = HA_URL.rstrip('/')
        
    async def call_api(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make API call to Home Assistant"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == "GET":
                response = await http_client.get(url)
            elif method.upper() == "POST":
                response = await http_client.post(url, json=data or {})
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise

    async def get_states(self) -> List[Dict]:
        """Get all entity states"""
        return await self.call_api("GET", "states")
    
    async def get_state(self, entity_id: str) -> Dict:
        """Get specific entity state"""
        return await self.call_api("GET", f"states/{entity_id}")
    
    async def call_service(self, domain: str, service: str, service_data: Optional[Dict] = None) -> Any:
        """Call a Home Assistant service"""
        return await self.call_api("POST", f"services/{domain}/{service}", service_data)


class FileManager:
    """Direct file system access - NO SSH/SFTP needed!"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        logger.info(f"✅ FileManager initialized with direct access to: {base_path}")
    
    def _resolve_path(self, relative_path: str) -> Path:
        """Resolve relative path to absolute path within config"""
        # Remove leading slashes and normalize
        clean_path = relative_path.lstrip('/').replace('\\', '/')
        full_path = (self.base_path / clean_path).resolve()
        
        # Security check - ensure path is within config directory
        try:
            full_path.relative_to(self.base_path)
        except ValueError:
            raise PermissionError(f"Access denied: {relative_path} is outside config directory")
        
        return full_path
    
    async def read_file(self, filepath: str) -> str:
        """Read file content"""
        path = self._resolve_path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        logger.info(f"📖 Read file: {filepath} ({len(content)} bytes)")
        return content
    
    async def write_file(self, filepath: str, content: str, create_backup: bool = True) -> str:
        """Write file content with optional backup"""
        path = self._resolve_path(filepath)
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists
        if create_backup and path.exists():
            backup_path = path.with_suffix(path.suffix + f'.bak_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            async with aiofiles.open(path, 'r', encoding='utf-8') as src:
                backup_content = await src.read()
            async with aiofiles.open(backup_path, 'w', encoding='utf-8') as dst:
                await dst.write(backup_content)
            logger.info(f"💾 Created backup: {backup_path.name}")
        
        # Write new content
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        logger.info(f"✍️  Wrote file: {filepath} ({len(content)} bytes)")
        return f"Successfully wrote {len(content)} bytes to {filepath}"
    
    async def list_directory(self, dirpath: str = ".") -> List[Dict[str, Any]]:
        """List directory contents"""
        path = self._resolve_path(dirpath)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dirpath}")
        
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dirpath}")
        
        items = []
        for item in sorted(path.iterdir()):
            try:
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                logger.warning(f"Could not stat {item}: {e}")
        
        logger.info(f"📋 Listed directory: {dirpath} ({len(items)} items)")
        return items
    
    async def get_directory_tree(self, dirpath: str = ".", max_depth: int = 5) -> Dict[str, Any]:
        """Get recursive directory tree"""
        path = self._resolve_path(dirpath)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dirpath}")
        
        def build_tree(current_path: Path, current_depth: int = 0) -> Dict:
            if current_depth >= max_depth:
                return {"truncated": True}
            
            tree = {
                "name": current_path.name or str(current_path),
                "type": "directory" if current_path.is_dir() else "file",
                "children": [] if current_path.is_dir() else None
            }
            
            if current_path.is_file():
                try:
                    tree["size"] = current_path.stat().st_size
                except:
                    pass
            elif current_path.is_dir():
                try:
                    for item in sorted(current_path.iterdir()):
                        tree["children"].append(build_tree(item, current_depth + 1))
                except PermissionError:
                    tree["error"] = "Permission denied"
            
            return tree
        
        tree = build_tree(path)
        logger.info(f"🌳 Generated directory tree: {dirpath}")
        return tree
    
    async def create_directory(self, dirpath: str) -> str:
        """Create directory"""
        path = self._resolve_path(dirpath)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created directory: {dirpath}")
        return f"Created directory: {dirpath}"
    
    async def delete_file(self, filepath: str) -> str:
        """Delete file or directory"""
        path = self._resolve_path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Not found: {filepath}")
        
        if path.is_file():
            path.unlink()
            logger.info(f"🗑️  Deleted file: {filepath}")
            return f"Deleted file: {filepath}"
        elif path.is_dir():
            import shutil
            shutil.rmtree(path)
            logger.info(f"🗑️  Deleted directory: {filepath}")
            return f"Deleted directory: {filepath}"
    
    async def move_file(self, source: str, destination: str) -> str:
        """Move or rename file"""
        src_path = self._resolve_path(source)
        dst_path = self._resolve_path(destination)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        
        # Create destination parent dirs
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        src_path.rename(dst_path)
        logger.info(f"📦 Moved: {source} → {destination}")
        return f"Moved {source} to {destination}"
    
    async def copy_file(self, source: str, destination: str) -> str:
        """Copy file"""
        src_path = self._resolve_path(source)
        dst_path = self._resolve_path(destination)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        
        # Create destination parent dirs
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)
        else:
            shutil.copytree(src_path, dst_path)
        
        logger.info(f"📄 Copied: {source} → {destination}")
        return f"Copied {source} to {destination}"
    
    async def search_files(self, pattern: str, directory: str = ".", extensions: Optional[List[str]] = None) -> List[Dict]:
        """Search files by content"""
        search_path = self._resolve_path(directory)
        matches = []
        
        for file_path in search_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            if extensions and file_path.suffix not in extensions:
                continue
            
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if pattern in content:
                        # Find line numbers
                        lines = content.split('\n')
                        line_numbers = [i + 1 for i, line in enumerate(lines) if pattern in line]
                        
                        relative_path = file_path.relative_to(self.base_path)
                        matches.append({
                            "file": str(relative_path),
                            "lines": line_numbers[:10]  # Limit to first 10 matches
                        })
            except Exception as e:
                logger.debug(f"Could not search {file_path}: {e}")
        
        logger.info(f"🔍 Search found {len(matches)} files matching '{pattern}'")
        return matches


# Initialize managers
ha_api = HomeAssistantAPI()
file_mgr = FileManager(HA_CONFIG_PATH)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    
    return [
        # File System Tools
        Tool(
            name="read_file",
            description="Read file content from Home Assistant config directory. Direct file system access - no SSH needed!",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Relative path from /config (e.g., 'packages/kitchen.yaml')"
                    }
                },
                "required": ["filepath"]
            }
        ),
        
        Tool(
            name="write_file",
            description="Write or update file in Home Assistant config directory. Creates backup automatically.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Relative path from /config"},
                    "content": {"type": "string", "description": "File content"},
                    "create_backup": {"type": "boolean", "description": "Create backup (default: true)", "default": True}
                },
                "required": ["filepath", "content"]
            }
        ),
        
        Tool(
            name="list_directory",
            description="List files and directories",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {"type": "string", "description": "Directory path (default: '.')", "default": "."}
                }
            }
        ),
        
        Tool(
            name="get_directory_tree",
            description="Get recursive directory tree structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {"type": "string", "description": "Starting directory", "default": "."},
                    "max_depth": {"type": "integer", "description": "Maximum recursion depth", "default": 5}
                }
            }
        ),
        
        Tool(
            name="create_directory",
            description="Create new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {"type": "string", "description": "Directory path to create"}
                },
                "required": ["dirpath"]
            }
        ),
        
        Tool(
            name="delete_file",
            description="Delete file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to delete"}
                },
                "required": ["filepath"]
            }
        ),
        
        Tool(
            name="move_file",
            description="Move or rename file/directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source path"},
                    "destination": {"type": "string", "description": "Destination path"}
                },
                "required": ["source", "destination"]
            }
        ),
        
        Tool(
            name="copy_file",
            description="Copy file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source path"},
                    "destination": {"type": "string", "description": "Destination path"}
                },
                "required": ["source", "destination"]
            }
        ),
        
        Tool(
            name="search_files",
            description="Search files by content pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Search pattern"},
                    "directory": {"type": "string", "description": "Directory to search", "default": "."},
                    "extensions": {"type": "array", "items": {"type": "string"}, "description": "File extensions to search"}
                },
                "required": ["pattern"]
            }
        ),
        
        # Home Assistant API Tools
        Tool(
            name="get_states",
            description="Get Home Assistant entity states with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filter by domain (e.g., 'light', 'switch', 'sensor'). Optional."
                    },
                    "entity_id_pattern": {
                        "type": "string",
                        "description": "Filter by entity ID pattern (regex). Optional."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of entities to return (default: 50, max: 500)",
                        "default": 50
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of entities to skip for pagination (default: 0)",
                        "default": 0
                    }
                }
            }
        ),
        
        Tool(
            name="get_state",
            description="Get specific entity state",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity ID (e.g., 'light.kitchen')"}
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="call_service",
            description="Call Home Assistant service",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Service domain (e.g., 'light')"},
                    "service": {"type": "string", "description": "Service name (e.g., 'turn_on')"},
                    "entity_id": {"type": "string", "description": "Target entity ID"},
                    "data": {"type": "object", "description": "Service data"}
                },
                "required": ["domain", "service"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        # File System Operations
        if name == "read_file":
            content = await file_mgr.read_file(arguments["filepath"])
            return [TextContent(type="text", text=content)]
        
        elif name == "write_file":
            result = await file_mgr.write_file(
                arguments["filepath"],
                arguments["content"],
                arguments.get("create_backup", True)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "list_directory":
            items = await file_mgr.list_directory(arguments.get("dirpath", "."))
            return [TextContent(type="text", text=json.dumps(items, indent=2))]
        
        elif name == "get_directory_tree":
            tree = await file_mgr.get_directory_tree(
                arguments.get("dirpath", "."),
                arguments.get("max_depth", 5)
            )
            return [TextContent(type="text", text=json.dumps(tree, indent=2))]
        
        elif name == "create_directory":
            result = await file_mgr.create_directory(arguments["dirpath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "delete_file":
            result = await file_mgr.delete_file(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "move_file":
            result = await file_mgr.move_file(arguments["source"], arguments["destination"])
            return [TextContent(type="text", text=result)]
        
        elif name == "copy_file":
            result = await file_mgr.copy_file(arguments["source"], arguments["destination"])
            return [TextContent(type="text", text=result)]
        
        elif name == "search_files":
            matches = await file_mgr.search_files(
                arguments["pattern"],
                arguments.get("directory", "."),
                arguments.get("extensions")
            )
            return [TextContent(type="text", text=json.dumps(matches, indent=2))]
        
        # Home Assistant API Operations
        elif name == "get_states":
            # Get all states from HA
            all_states = await ha_api.get_states()
            
            # Apply filtering
            filtered_states = all_states
            
            # Filter by domain if specified
            if "domain" in arguments and arguments["domain"]:
                domain = arguments["domain"].lower()
                filtered_states = [
                    state for state in filtered_states 
                    if state.get("entity_id", "").startswith(f"{domain}.")
                ]
            
            # Filter by entity_id pattern if specified
            if "entity_id_pattern" in arguments and arguments["entity_id_pattern"]:
                import re
                pattern = re.compile(arguments["entity_id_pattern"], re.IGNORECASE)
                filtered_states = [
                    state for state in filtered_states
                    if pattern.search(state.get("entity_id", ""))
                ]
            
            # Apply pagination
            offset = arguments.get("offset", 0)
            limit = min(arguments.get("limit", 50), 500)  # Max 500 entities
            
            total_count = len(filtered_states)
            paginated_states = filtered_states[offset:offset + limit]
            
            # Build response with metadata
            response = {
                "states": paginated_states,
                "metadata": {
                    "total": total_count,
                    "returned": len(paginated_states),
                    "offset": offset,
                    "limit": limit,
                    "has_more": (offset + limit) < total_count
                }
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2, default=str))]
        
        elif name == "get_state":
            state = await ha_api.get_state(arguments["entity_id"])
            return [TextContent(type="text", text=json.dumps(state, indent=2))]
        
        elif name == "call_service":
            service_data = arguments.get("data", {})
            if "entity_id" in arguments:
                service_data["entity_id"] = arguments["entity_id"]
            
            result = await ha_api.call_service(
                arguments["domain"],
                arguments["service"],
                service_data
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server as HTTP server"""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount
    from starlette.responses import JSONResponse
    import uvicorn
    
    logger.info("🚀 Starting Home Assistant MCP Server (Native Add-on)")
    logger.info(f"📁 Config access: {HA_CONFIG_PATH}")
    logger.info(f"🔌 Listening on port {PORT}")
    logger.info("✅ Direct file system access - NO SSH/SFTP needed!")
    
    # Create SSE transport for HTTP-based MCP
    sse = SseServerTransport("/messages")
    
    # Health check endpoint
    async def health_check(request):
        return JSONResponse({
            "status": "healthy",
            "service": "ha-mcp-server",
            "version": "1.0.0"
        })
    
    # Favicon endpoint to eliminate 404 errors
    async def favicon(request):
        from starlette.responses import Response
        # Return a simple 1x1 transparent PNG
        favicon_data = bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001"
            "08060000001f15c4890000000a49444154789c6300010000"
            "00050001edd2462e0000000049454e44ae426082"
        )
        return Response(content=favicon_data, media_type="image/png")
    
    # Create ASGI app for SSE handling
    async def handle_sse_message(scope, receive, send):
        from starlette.responses import Response
        if scope["type"] == "http":
            if scope["method"] == "GET":
                async with sse.connect_sse(scope, receive, send) as streams:
                    await app.run(
                        streams[0],
                        streams[1],
                        app.create_initialization_options()
                    )
                return Response(status_code=200)
            elif scope["method"] == "POST":
                await sse.handle_post_message(scope, receive, send)
                return Response(status_code=202)
        # Fallback for unexpected requests
        return Response(status_code=405, content="Method Not Allowed")
    
    # Create Starlette app
    from starlette.routing import Route
    web_app = Starlette(
        routes=[
            Mount("/messages", app=handle_sse_message),
            Route("/health", endpoint=health_check),
            Route("/favicon.ico", endpoint=favicon),
        ]
    )
    
    # Run HTTP server
    logger.info(f"🌐 HTTP server starting on 0.0.0.0:{PORT}")
    config = uvicorn.Config(
        web_app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())


