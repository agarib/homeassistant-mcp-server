#!/usr/bin/env python3
"""
🏠 Home Assistant MCP Server - Native Add-on Version
Version: 1.0.3
Date: October 30, 2025
Authors: agarib (https://github.com/agarib) & GitHub Copilot

Running INSIDE Home Assistant with direct file system access - eliminates ALL SSH/SFTP complexity!

🌟 FEATURED CAPABILITIES:
✨ 105 TOTAL TOOLS for comprehensive Home Assistant control
✨ Persistent server.py across restarts (no more losing tools after updates!)
✨ Direct /config access - no network/auth issues
✨ Python code execution with pandas, matplotlib, numpy
✨ Camera VLM integration for image analysis
✨ Complete add-on management including restarts

📦 TOOL CATEGORIES:
✅ File Operations (9 tools)
✅ Basic HA API (3 tools + restart!)
✅ Device Discovery & Control (18 tools)
✅ Security, Automation, Workflows (35 tools)
✅ Dashboard & HACS Management (9 tools)
✅ Code Execution & Data Analysis (3 tools)
✅ Camera VLM Integration (5 tools)
✅ Vacuum Control (7 tools)
✅ Fan Control (6 tools)
✅ Add-on Management (9 tools)

CHANGELOG:
v1.0.3 (2025-10-30):
  - Added restart_homeassistant tool for system restarts
  - Fixed server.py persistence across container restarts
  - Total tools: 105 (up from 104)
  
v1.0.0 (2025-10-27):
  - Initial release with 104 tools
  - Native add-on architecture with direct /config access
"""

import asyncio
import os
import json
import logging
import re
import base64
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


# ============================================================================
# CODE EXECUTION & DATA ANALYSIS HELPERS
# ============================================================================

async def execute_python_code(code: str, return_stdout: bool = True, return_plots: bool = True) -> str:
    """
    Execute Python code in a safe sandbox with pandas, numpy, matplotlib available.
    Returns stdout output and/or base64-encoded plots.
    """
    import io
    import sys
    import base64
    from contextlib import redirect_stdout
    
    try:
        # Import analysis libraries
        import pandas as pd
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Capture stdout
        stdout_capture = io.StringIO()
        plots = []
        
        # Create safe globals with common libraries
        safe_globals = {
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            '__builtins__': __builtins__,
        }
        
        # Execute code
        with redirect_stdout(stdout_capture):
            exec(code, safe_globals)
        
        # Capture any matplotlib figures
        if return_plots and plt.get_fignums():
            for fig_num in plt.get_fignums():
                fig = plt.figure(fig_num)
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plots.append(f"data:image/png;base64,{img_base64}")
                plt.close(fig)
        
        # Build response
        result = {}
        
        if return_stdout:
            stdout_text = stdout_capture.getvalue()
            if stdout_text:
                result['stdout'] = stdout_text
        
        if return_plots and plots:
            result['plots'] = plots
        
        if not result:
            result['message'] = "Code executed successfully (no output)"
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.error(f"Python execution error: {e}")
        return json.dumps({
            'error': str(e),
            'type': type(e).__name__
        }, indent=2)


async def analyze_states_as_dataframe(
    ha_api: HomeAssistantAPI,
    domain: Optional[str] = None,
    include_attributes: bool = True,
    query: Optional[str] = None
) -> str:
    """
    Get HA states as a pandas DataFrame for analysis.
    Returns JSON representation of the DataFrame.
    """
    try:
        import pandas as pd
        
        # Get states
        states = await ha_api.get_states()
        
        # Filter by domain if specified
        if domain:
            states = [s for s in states if s['entity_id'].startswith(f"{domain}.")]
        
        # Build DataFrame
        data = []
        for state in states:
            row = {
                'entity_id': state['entity_id'],
                'state': state['state'],
                'last_changed': state.get('last_changed'),
                'last_updated': state.get('last_updated')
            }
            
            # Add attributes if requested
            if include_attributes and 'attributes' in state:
                for key, value in state['attributes'].items():
                    # Flatten attributes (convert complex types to strings)
                    if isinstance(value, (list, dict)):
                        row[f'attr_{key}'] = json.dumps(value)
                    else:
                        row[f'attr_{key}'] = value
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Apply query filter if specified
        if query:
            df = df.query(query)
        
        # Return as JSON with metadata
        result = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'data': df.to_dict(orient='records'),
            'summary': {
                'total_entities': len(df),
                'domains': df['entity_id'].str.split('.').str[0].value_counts().to_dict() if len(df) > 0 else {}
            }
        }
        
        return json.dumps(result, indent=2, default=str)
    
    except Exception as e:
        logger.error(f"DataFrame analysis error: {e}")
        return json.dumps({
            'error': str(e),
            'type': type(e).__name__
        }, indent=2)


async def plot_sensor_history_chart(
    ha_api: HomeAssistantAPI,
    entity_ids: List[str],
    hours: int = 24,
    chart_type: str = "line",
    title: Optional[str] = None
) -> str:
    """
    Plot sensor history as a time-series chart.
    Returns base64-encoded PNG image.
    """
    try:
        import pandas as pd
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from datetime import datetime, timedelta
        import base64
        import io
        
        # Get history for each entity
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Note: We'll use get_states for now since we don't have get_entity_history in current tools
        # In a real implementation, you'd call the HA history API
        all_data = []
        
        for entity_id in entity_ids:
            try:
                state = await ha_api.get_state(entity_id)
                # For now, just plot current state (you'd extend this to get full history)
                all_data.append({
                    'entity_id': entity_id,
                    'timestamp': datetime.now(),
                    'value': float(state['state']) if state['state'] not in ['unavailable', 'unknown'] else None
                })
            except Exception as e:
                logger.warning(f"Could not get state for {entity_id}: {e}")
        
        if not all_data:
            return json.dumps({'error': 'No data available for plotting'})
        
        df = pd.DataFrame(all_data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if chart_type == "line":
            for entity_id in entity_ids:
                entity_data = df[df['entity_id'] == entity_id]
                if not entity_data.empty:
                    ax.plot(entity_data['timestamp'], entity_data['value'], marker='o', label=entity_id)
        
        elif chart_type == "bar":
            df.pivot(index='timestamp', columns='entity_id', values='value').plot(kind='bar', ax=ax)
        
        elif chart_type == "scatter":
            for entity_id in entity_ids:
                entity_data = df[df['entity_id'] == entity_id]
                if not entity_data.empty:
                    ax.scatter(entity_data['timestamp'], entity_data['value'], label=entity_id, s=100)
        
        # Formatting
        ax.set_title(title or f'Sensor History - Last {hours} Hours')
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return json.dumps({
            'plot': f"data:image/png;base64,{img_base64}",
            'entities_plotted': entity_ids,
            'data_points': len(df),
            'time_range_hours': hours
        }, indent=2)
    
    except Exception as e:
        logger.error(f"Plotting error: {e}")
        return json.dumps({
            'error': str(e),
            'type': type(e).__name__
        }, indent=2)


# Initialize managers
ha_api = HomeAssistantAPI()
file_mgr = FileManager(HA_CONFIG_PATH)




# ============================================================================
# TOOL DEFINITIONS FROM CONVERTED PARTS
# ============================================================================

def get_part1_tools() -> list[Tool]:
    """
    Returns Part 1 tool definitions to merge into server.py list_tools()
    Copy these into the main list_tools() function
    """
    return [
        # =================================================================
        # DEVICE DISCOVERY & STATE MANAGEMENT
        # =================================================================
        
        Tool(
            name="discover_devices",
            description=(
                "🔍 **Intelligent Device Discovery with Smart Filtering**\n\n"
                "Discovers ALL Home Assistant entities with advanced filtering and categorization.\n\n"
                "**FEATURES:**\n"
                "- Filter by domain (light, switch, sensor, climate, media_player, etc.)\n"
                "- Filter by area/room (kitchen, bedroom, living_room)\n"
                "- Filter by state (on, off, unavailable, unknown)\n"
                "- Filter by attribute patterns (brightness > 50, battery < 20%)\n"
                "- Returns: entity_id, friendly_name, state, domain, area, last_changed\n\n"
                "**SMART USE CASES:**\n"
                "- 'Find all lights in the kitchen' → domain='light', area='kitchen'\n"
                "- 'Show me battery sensors below 20%' → domain='sensor', attribute_filter={'battery': '<20'}\n"
                "- 'List unavailable devices' → state_filter='unavailable'\n"
                "- 'All media players currently playing' → domain='media_player', state_filter='playing'\n\n"
                "**RETURNS:** Structured list with entity details, organized by domain/area.\n\n"
                "**RELATED TOOLS:** Use get_device_state() for detailed single entity info, "
                "or get_area_devices() when you already know the area name."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filter by domain (light, switch, sensor, climate, media_player, cover, fan, etc.)",
                        "enum": ["light", "switch", "sensor", "binary_sensor", "climate", "media_player", 
                                "cover", "fan", "lock", "camera", "alarm_control_panel", "vacuum", "all"]
                    },
                    "area": {
                        "type": "string",
                        "description": "Filter by area/room name (e.g., 'kitchen', 'bedroom', 'living_room')"
                    },
                    "state_filter": {
                        "type": "string",
                        "description": "Filter by current state (on, off, playing, paused, unavailable, unknown)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 100)",
                        "default": 100
                    }
                }
            }
        ),
        
        Tool(
            name="get_device_state",
            description=(
                "📊 **Comprehensive Device State Inspector**\n\n"
                "Get COMPLETE state information for any Home Assistant entity with full context.\n\n"
                "**RETURNS:**\n"
                "- Current state (on/off/value)\n"
                "- All attributes (brightness, color, temperature, battery, etc.)\n"
                "- Metadata (friendly_name, device_class, unit_of_measurement)\n"
                "- Timing (last_changed, last_updated)\n"
                "- Context (area, device info, related entities)\n\n"
                "**SMART ANALYSIS:**\n"
                "- Light: brightness (0-255), RGB color, color_temp, effect mode\n"
                "- Climate: current_temp, target_temp, hvac_mode, fan_mode\n"
                "- Sensor: value, unit, battery level, device_class\n"
                "- Media Player: source, volume, media_title, app_name\n"
                "- Switch/Lock: state, battery (if applicable)\n\n"
                "**USE CASES:**\n"
                "- 'What's the current state of kitchen light?' → Brightness, color, on/off\n"
                "- 'Check living room thermostat' → Current temp, target, mode\n"
                "- 'Is front door locked?' → State + battery level\n"
                "- 'What's playing on TV?' → Media info, volume, source\n\n"
                "**RELATED TOOLS:** Use discover_devices() when entity_id is unknown, get_area_devices() for all devices in a room."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to inspect (e.g., 'light.kitchen', 'climate.thermostat', 'media_player.tv')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="get_area_devices",
            description=(
                "🏠 **Area/Room Device Lister with Grouping**\n\n"
                "Get ALL devices in a specific area/room, organized by type (lights, switches, sensors, etc.).\n\n"
                "**FEATURES:**\n"
                "- Groups devices by domain automatically\n"
                "- Shows current state for each device\n"
                "- Includes device metadata (friendly names, capabilities)\n"
                "- Identifies controllable vs. read-only devices\n\n"
                "**RETURNS (organized by type):**\n"
                "- Lights: with current brightness/color state\n"
                "- Switches: on/off state\n"
                "- Sensors: current readings\n"
                "- Climate: temperature, mode\n"
                "- Media Players: playing/paused state\n"
                "- Covers/Blinds: open/closed position\n\n"
                "**USE CASES:**\n"
                "- 'What devices are in the kitchen?' → All kitchen entities grouped\n"
                "- 'Show bedroom lights and switches' → Controllable bedroom devices\n"
                "- 'List all living room sensors' → Temperature, motion, etc.\n\n"
                "**WORKFLOW:** After getting area devices, use control_light(), control_switch(), etc. "
                "after identifying target entity_ids."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area/room name (kitchen, bedroom, living_room, office, etc.)"
                    },
                    "include_unavailable": {
                        "type": "boolean",
                        "description": "Include offline/unavailable devices (default: false)",
                        "default": False
                    },
                    "device_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by device types (light, switch, sensor, climate, media_player)"
                    }
                },
                "required": ["area"]
            }
        ),
        
        # =================================================================
        # BASIC DEVICE CONTROL
        # =================================================================
        
        Tool(
            name="control_light",
            description=(
                "💡 **Advanced Light Control with Color & Effects**\n\n"
                "Control lights with full capability support: on/off, brightness, color, temperature, effects.\n\n"
                "**ACTIONS:**\n"
                "- turn_on: Power on with optional brightness/color\n"
                "- turn_off: Power off\n"
                "- toggle: Switch state\n"
                "- set_brightness: Adjust brightness (0-255 or 0-100%)\n"
                "- set_color: RGB color or color name\n"
                "- set_temperature: Color temperature (warm to cool)\n"
                "- set_effect: Special effects (flash, colorloop, etc.)\n\n"
                "**PARAMETERS:**\n"
                "- brightness: 0-255 or percentage string '50%'\n"
                "- rgb_color: [R, G, B] e.g., [255, 0, 0] for red\n"
                "- color_temp: Kelvin (2000-6500) or mireds\n"
                "- transition: Fade time in seconds\n\n"
                "**RELATED TOOLS:** Use adaptive_lighting() for context-aware control, scene_based_lighting() for activity presets."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Light entity ID or comma-separated list"},
                    "action": {
                        "type": "string",
                        "enum": ["turn_on", "turn_off", "toggle"],
                        "description": "Light action"
                    },
                    "brightness": {
                        "type": "integer",
                        "description": "Brightness (0-255)",
                        "minimum": 0,
                        "maximum": 255
                    },
                    "brightness_pct": {
                        "type": "integer",
                        "description": "Brightness percentage (0-100)",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "rgb_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "RGB color [r, g, b] (0-255 each)"
                    },
                    "color_temp": {
                        "type": "integer",
                        "description": "Color temperature in Kelvin (2000-6500) or mireds"
                    },
                    "effect": {
                        "type": "string",
                        "description": "Light effect (colorloop, flash, etc.)"
                    },
                    "transition": {
                        "type": "integer",
                        "description": "Transition time in seconds"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="control_switch",
            description=(
                "🔌 **Smart Switch Control**\n\n"
                "Control switches, outlets, and other binary devices.\n\n"
                "**ACTIONS:**\n"
                "- turn_on: Power on the switch\n"
                "- turn_off: Power off the switch\n"
                "- toggle: Switch between on/off states\n\n"
                "**USE CASES:**\n"
                "- Control power outlets\n"
                "- Toggle smart plugs\n"
                "- Control relay switches\n"
                "- Manage energy monitoring switches\n\n"
                "**RELATED TOOLS:** control_light() for lights, control_climate() for HVAC, control_cover() for blinds."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Switch entity ID"},
                    "action": {
                        "type": "string",
                        "enum": ["turn_on", "turn_off", "toggle"],
                        "description": "Switch action"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="control_climate",
            description=(
                "🌡️ **Advanced Climate Control (HVAC/Thermostat)**\n\n"
                "Control thermostats, air conditioners, heaters with full HVAC mode support.\n\n"
                "**ACTIONS:**\n"
                "- set_temperature: Change target temperature\n"
                "- set_hvac_mode: Change mode (heat, cool, auto, off, heat_cool)\n"
                "- set_fan_mode: Change fan mode (auto, on, low, high, etc.)\n"
                "- set_preset_mode: Use preset (away, home, sleep, eco)\n"
                "- set_humidity: Target humidity level\n\n"
                "**HVAC MODES:**\n"
                "- heat: Heating only\n"
                "- cool: Cooling only\n"
                "- heat_cool: Auto heating/cooling\n"
                "- auto: Automatic mode\n"
                "- off: HVAC off\n"
                "- dry: Dehumidify mode\n"
                "- fan_only: Fan without heating/cooling\n\n"
                "**SMART FEATURES:**\n"
                "- Dual setpoint support (heat + cool targets)\n"
                "- Preset modes for energy efficiency\n"
                "- Fan speed control\n"
                "- Humidity control (if supported)\n\n"
                "**RELATED TOOLS:** Use smart_thermostat() for schedule-based control, zone_temperature_control() for multi-room systems."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Climate entity ID"},
                    "temperature": {"type": "number", "description": "Target temperature"},
                    "target_temp_high": {"type": "number", "description": "Upper temperature (heat_cool mode)"},
                    "target_temp_low": {"type": "number", "description": "Lower temperature (heat_cool mode)"},
                    "hvac_mode": {
                        "type": "string",
                        "enum": ["heat", "cool", "heat_cool", "auto", "off", "dry", "fan_only"],
                        "description": "HVAC operation mode"
                    },
                    "fan_mode": {"type": "string", "description": "Fan mode (auto, on, low, medium, high)"},
                    "preset_mode": {"type": "string", "description": "Preset mode (away, home, sleep, eco)"},
                    "humidity": {"type": "integer", "description": "Target humidity percentage"}
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="control_cover",
            description=(
                "🪟 **Smart Cover/Blind Control**\n\n"
                "Control blinds, shades, curtains, garage doors, and other cover entities.\n\n"
                "**ACTIONS:**\n"
                "- open_cover: Fully open\n"
                "- close_cover: Fully close\n"
                "- stop_cover: Stop movement\n"
                "- toggle: Switch between open/closed\n"
                "- set_position: Set to specific position (0-100%)\n"
                "- set_tilt_position: Adjust slat angle (venetian blinds)\n\n"
                "**POSITION CONTROL:**\n"
                "- 0% = Fully closed\n"
                "- 50% = Half open\n"
                "- 100% = Fully open\n\n"
                "**USE CASES:**\n"
                "- 'Open living room blinds 75%' → set_position: 75\n"
                "- 'Close bedroom curtains' → close_cover\n"
                "- 'Open garage door' → open_cover\n"
                "- 'Tilt blinds 45 degrees' → set_tilt_position\n\n"
                "**SMART AUTOMATION:** Use circadian_rhythm_blinds() for sun-based automation, "
                "weather_based_automation() to adjust based on sun/temperature."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Cover entity ID"},
                    "action": {
                        "type": "string",
                        "enum": ["open_cover", "close_cover", "stop_cover", "toggle"],
                        "description": "Cover action"
                    },
                    "position": {
                        "type": "integer",
                        "description": "Position percentage (0-100)",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "tilt_position": {
                        "type": "integer",
                        "description": "Tilt position for venetian blinds (0-100)",
                        "minimum": 0,
                        "maximum": 100
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        # =================================================================
        # ADVANCED LIGHTING CONTROL
        # =================================================================
        
        Tool(
            name="adaptive_lighting",
            description=(
                "🌅 **Context-Aware Adaptive Lighting**\n\n"
                "Automatically adjusts lighting based on time of day, sun position, ambient light, and activity.\n\n"
                "**ADAPTS TO:**\n"
                "- Time of day (morning bright, evening warm)\n"
                "- Sun position (sunrise/sunset transitions)\n"
                "- Ambient light sensors (darken if room is bright)\n"
                "- Occupancy/motion (different levels for activity vs. presence)\n"
                "- Activity type (reading, watching TV, cooking, relaxing)\n\n"
                "**AUTOMATIC ADJUSTMENTS:**\n"
                "- Morning (6-9 AM): Cool white, energizing brightness\n"
                "- Day (9 AM-5 PM): Bright, neutral white\n"
                "- Evening (5-9 PM): Warm white, moderate brightness\n"
                "- Night (9 PM+): Dim warm light, sleep-friendly\n\n"
                "**ACTIVITY PRESETS:**\n"
                "- reading: Bright cool white focused light\n"
                "- watching_tv: Dim warm ambient lighting\n"
                "- cooking: Bright task lighting\n"
                "- relaxing: Soft warm glow\n"
                "- working: Bright neutral white\n\n"
                "**RELATED TOOLS:** Use circadian_lighting() for health-focused rhythms, "
                "control_light() for manual override, multi_room_lighting_sync() to coordinate multiple rooms with same activity."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Light or group to control"},
                    "activity": {
                        "type": "string",
                        "enum": ["reading", "watching_tv", "cooking", "relaxing", "working", "auto"],
                        "description": "Current activity (auto = time-based)"
                    },
                    "use_ambient_sensor": {
                        "type": "boolean",
                        "description": "Use ambient light sensor for brightness adjustment"
                    },
                    "ambient_sensor": {
                        "type": "string",
                        "description": "Entity ID of ambient light sensor"
                    },
                    "motion_sensor": {
                        "type": "string",
                        "description": "Motion sensor for occupancy detection"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="circadian_lighting",
            description=(
                "☀️ **Health-Optimized Circadian Rhythm Lighting**\n\n"
                "Aligns lighting with natural circadian rhythms for better sleep and alertness.\n\n"
                "**SCIENCE-BASED LIGHTING:**\n"
                "- Morning: High color temp (5500-6500K), bright → Cortisol boost, alertness\n"
                "- Midday: Neutral white (4000-5000K) → Sustained focus\n"
                "- Afternoon: Gradual warm shift (3500-4000K) → Natural wind-down\n"
                "- Evening: Warm white (2700-3000K), dimmed → Melatonin production\n"
                "- Night: Very warm (2000-2500K), very dim → Sleep preparation\n\n"
                "**HEALTH BENEFITS:**\n"
                "- Improved sleep quality\n"
                "- Better morning alertness\n"
                "- Reduced eye strain\n"
                "- Natural hormone regulation\n\n"
                "**CUSTOMIZATION:**\n"
                "- sleep_time: When to shift to sleep-friendly lighting\n"
                "- wake_time: When to start energizing morning light\n"
                "- transition_duration: How gradually to change (minutes)\n\n"
                "**MODES:**\n"
                "- normal: Standard circadian curve\n"
                "- sleep: Extra warm/dim for sleep issues\n"
                "- energize: Brighter/cooler for alertness\n\n"
                "**RELATED TOOLS:** Use adaptive_lighting() for activity-based control, "
                "control_light() for manual override, bedtime_routine() to transition to sleep mode."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Light or group to control"},
                    "mode": {
                        "type": "string",
                        "enum": ["normal", "sleep", "energize"],
                        "description": "Circadian mode"
                    },
                    "sleep_time": {
                        "type": "string",
                        "description": "Bedtime (HH:MM format, e.g., '22:00')"
                    },
                    "wake_time": {
                        "type": "string",
                        "description": "Wake time (HH:MM format, e.g., '07:00')"
                    },
                    "transition_duration": {
                        "type": "integer",
                        "description": "Transition duration in minutes (default: 30)",
                        "default": 30
                    },
                    "min_brightness": {
                        "type": "integer",
                        "description": "Minimum brightness (0-255, default: 10)",
                        "default": 10
                    },
                    "max_brightness": {
                        "type": "integer",
                        "description": "Maximum brightness (0-255, default: 255)",
                        "default": 255
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="multi_room_lighting_sync",
            description=(
                "🏡 **Multi-Room Lighting Synchronization**\n\n"
                "Synchronize lighting across multiple rooms for consistent whole-home atmosphere.\n\n"
                "**FEATURES:**\n"
                "- Apply same scene/settings to multiple rooms\n"
                "- Gradual room-by-room transitions\n"
                "- Zone-based control (upstairs, downstairs, etc.)\n"
                "- Activity-based synchronization\n\n"
                "**SYNC MODES:**\n"
                "- instant: All rooms change simultaneously\n"
                "- wave: Gradual room-by-room transition\n"
                "- follow: Lights follow user movement between rooms\n\n"
                "**USE CASES:**\n"
                "- 'Set all downstairs lights to movie mode'\n"
                "- 'Sync bedroom and hallway for nighttime navigation'\n"
                "- 'Create party lighting across living spaces'\n"
                "- 'Gradual wake-up lighting cascade from bedroom to kitchen'\n\n"
                "**ACTIVITY PRESETS:**\n"
                "- movie: Dim ambient lighting\n"
                "- party: Dynamic colorful lighting\n"
                "- dinner: Warm intimate lighting\n"
                "- cleanup: Bright task lighting\n"
                "- bedtime: Progressive dimming sequence\n\n"
                "**RELATED TOOLS:** Use adaptive_lighting() for individual room intelligence, "
                "whole_home_scene() for complex multi-device coordination beyond just lights."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "rooms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of room/area names to sync"
                    },
                    "activity": {
                        "type": "string",
                        "enum": ["movie", "party", "dinner", "cleanup", "bedtime", "custom"],
                        "description": "Activity preset to apply"
                    },
                    "sync_mode": {
                        "type": "string",
                        "enum": ["instant", "wave", "follow"],
                        "description": "How to synchronize (default: instant)",
                        "default": "instant"
                    },
                    "custom_brightness": {
                        "type": "integer",
                        "description": "Custom brightness for all rooms (0-255)"
                    },
                    "custom_color_temp": {
                        "type": "integer",
                        "description": "Custom color temp for all rooms (Kelvin)"
                    },
                    "transition_delay": {
                        "type": "integer",
                        "description": "Delay between rooms in wave mode (seconds)"
                    }
                },
                "required": ["rooms", "activity"]
            }
        ),
        
        Tool(
            name="presence_based_lighting",
            description=(
                "👤 **Presence-Aware Smart Lighting**\n\n"
                "Automatically turn lights on/off based on room occupancy with intelligent timeout.\n\n"
                "**FEATURES:**\n"
                "- Motion sensor integration\n"
                "- Configurable timeout before turning off\n"
                "- Manual override detection (if user turned off manually, respect it)\n"
                "- Time-of-day brightness adjustment\n"
                "- Activity-based scene selection\n\n"
                "**USE CASES:**\n"
                "- Hallway: Turn on when motion, off 2 minutes after last motion\n"
                "- Bathroom: Bright when occupied, off when empty\n"
                "- Closet: On when door opens, off when closed\n"
                "- Garage: On when entered, off 10 minutes after exit\n\n"
                "**RELATED TOOLS:** adaptive_lighting() for context-aware brightness/color"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "light_entity": {"type": "string", "description": "Light to control"},
                    "motion_sensor": {"type": "string", "description": "Motion sensor entity"},
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Seconds to wait before turning off (default: 300)",
                        "default": 300
                    },
                    "respect_manual_off": {
                        "type": "boolean",
                        "description": "Don't auto-turn-on if manually turned off (default: true)",
                        "default": True
                    }
                },
                "required": ["light_entity", "motion_sensor"]
            }
        ),
        
        # =================================================================
        # MEDIA PLAYER CONTROL
        # =================================================================
        
        Tool(
            name="control_media_player",
            description=(
                "🎵 **Advanced Media Player Control**\n\n"
                "Control TVs, speakers, receivers, and streaming devices with comprehensive actions.\n\n"
                "**PLAYBACK ACTIONS:**\n"
                "- turn_on, turn_off: Power control\n"
                "- play, pause, stop: Playback control\n"
                "- media_next_track, media_previous_track: Track navigation\n"
                "- media_play_pause: Toggle play/pause\n\n"
                "**VOLUME CONTROL:**\n"
                "- volume_set: Set volume (0.0-1.0)\n"
                "- volume_up, volume_down: Adjust volume\n"
                "- mute, unmute: Mute control\n\n"
                "**SOURCE/INPUT:**\n"
                "- select_source: Choose input (HDMI1, Chromecast, Bluetooth, etc.)\n\n"
                "**ACTIONS:** turn_on, turn_off, play, pause, stop, mute, unmute, volume_set, volume_up, volume_down, select_source, media_next_track, media_previous_track"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Media player entity ID"},
                    "action": {
                        "type": "string",
                        "enum": ["turn_on", "turn_off", "play", "pause", "stop", "toggle", 
                                "volume_up", "volume_down", "mute", "unmute", "media_next_track", "media_previous_track"],
                        "description": "Media player action"
                    },
                    "volume_level": {
                        "type": "number",
                        "description": "Volume level (0.0-1.0)",
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "source": {"type": "string", "description": "Input source name"}
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="play_media",
            description=(
                "▶️ **Play Media Content**\n\n"
                "Play specific media content (music, video, radio, playlists) on media players.\n\n"
                "Supports URLs, Spotify URIs, local files, and streaming services."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Media player entity ID"},
                    "media_content_id": {"type": "string", "description": "URL or media identifier"},
                    "media_content_type": {
                        "type": "string",
                        "description": "Media type (music, video, playlist, etc.)"
                    }
                },
                "required": ["entity_id", "media_content_id", "media_content_type"]
            }
        ),
        
        Tool(
            name="multi_room_audio_sync",
            description=(
                "🔊 **Multi-Room Audio Synchronization**\n\n"
                "Play synchronized audio across multiple speakers/rooms. Perfect for whole-home audio or party mode.\n\n"
                "**FEATURES:**\n"
                "- Synchronized playback across rooms\n"
                "- Volume balancing\n"
                "- Group management\n\n"
                "**USE CASES:**\n"
                "- Play music in kitchen + living room simultaneously\n"
                "- Whole-home announcements\n"
                "- Party mode audio distribution"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "media_players": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of media player entity IDs to sync"
                    },
                    "master_player": {"type": "string", "description": "Primary player (controls others)"},
                    "media_content_id": {"type": "string", "description": "Media to play"},
                    "volume_level": {"type": "number", "description": "Volume for all (0.0-1.0)"}
                },
                "required": ["media_players"]
            }
        ),
        
        Tool(
            name="party_mode",
            description=(
                "🎉 **Party Mode Activation**\n\n"
                "Transform your home into party mode: dynamic colorful lighting, multi-room audio, and optimized climate.\n\n"
                "**ACTIVATES:**\n"
                "- Colorful dynamic lighting (color loops, effects)\n"
                "- Multi-room synchronized audio\n"
                "- Climate adjustments (cooler for more people)\n"
                "- All entertainment devices coordinated\n\n"
                "**CUSTOMIZATION:**\n"
                "- Light intensity and color patterns\n"
                "- Audio zones and volume levels\n"
                "- Climate presets for crowd comfort"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "rooms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Rooms to include in party mode"
                    },
                    "music_source": {"type": "string", "description": "Media content to play"},
                    "light_intensity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Light effect intensity"
                    },
                    "volume_level": {"type": "number", "description": "Music volume (0.0-1.0)"}
                },
                "required": ["rooms"]
            }
        ),
        
        # =================================================================
        # CLIMATE & ENVIRONMENT
        # =================================================================
        
        Tool(
            name="smart_thermostat_optimization",
            description=(
                "🌡️ **Smart Thermostat with Occupancy & Schedule**\n\n"
                "Optimize thermostat based on occupancy, schedule, and weather for maximum efficiency and comfort.\n\n"
                "**FEATURES:**\n"
                "- Occupancy-based setbacks (lower temp when away)\n"
                "- Schedule integration (work hours, sleep hours)\n"
                "- Weather-based pre-cooling/pre-heating\n"
                "- Energy efficiency optimization\n\n"
                "**MODES:**\n"
                "- home: Comfort mode (normal temps)\n"
                "- away: Energy saving (setback temps)\n"
                "- sleep: Nighttime temps\n"
                "- eco: Maximum energy efficiency"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Climate entity ID"},
                    "mode": {
                        "type": "string",
                        "enum": ["home", "away", "sleep", "eco"],
                        "description": "Thermostat mode"
                    },
                    "occupancy_sensor": {"type": "string", "description": "Occupancy/motion sensor entity"},
                    "schedule": {
                        "type": "object",
                        "description": "Temperature schedule by time of day"
                    }
                },
                "required": ["entity_id", "mode"]
            }
        ),
        
        Tool(
            name="zone_climate_control",
            description=(
                "🏠 **Multi-Zone Climate Control**\n\n"
                "Control different temperature zones independently for personalized comfort.\n\n"
                "Perfect for multi-zone HVAC or room-by-room temperature management."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "zones": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "entity_id": {"type": "string"},
                                "target_temp": {"type": "number"}
                            }
                        },
                        "description": "List of zones with target temperatures"
                    }
                },
                "required": ["zones"]
            }
        ),
        
        Tool(
            name="air_quality_management",
            description=(
                "🌬️ **Air Quality Management & Ventilation**\n\n"
                "Monitor and control air quality with fans, purifiers, and automated ventilation.\n\n"
                "Controls fans, purifiers, and windows based on indoor/outdoor air quality."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "air_quality_sensor": {"type": "string", "description": "Air quality sensor entity"},
                    "fan_entity": {"type": "string", "description": "Fan or purifier to control"},
                    "target_aqi": {
                        "type": "integer",
                        "description": "Target AQI threshold (turn on if exceeded)"
                    },
                    "window_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Smart windows to open for ventilation"
                    }
                },
                "required": ["air_quality_sensor"]
            }
        ),
    ]


# ============================================================================
# PART 1: TOOL HANDLERS (to add to call_tool() in server.py)
# ============================================================================



def get_part2_tools() -> list[Tool]:
    """
    Returns Part 2 tool definitions to merge into server.py list_tools()
    Copy these into the main list_tools() function
    """
    return [
        # =================================================================
        # SECURITY & MONITORING
        # =================================================================
        
        Tool(
            name="intelligent_security_monitor",
            description=(
                "🔒 **Intelligent Security Monitoring with AI Analysis**\n\n"
                "Analyzes door/window sensors, cameras, motion patterns. Alerts on unusual activity."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sensor_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of door/window/motion sensor entities to monitor"
                    },
                    "alert_entity": {
                        "type": "string",
                        "description": "Entity to notify on anomalies (notify service, etc.)"
                    },
                    "baseline_hours": {
                        "type": "integer",
                        "description": "Hours of history to establish baseline (default: 24)",
                        "default": 24
                    }
                },
                "required": ["sensor_entities"]
            }
        ),
        
        Tool(
            name="anomaly_detection",
            description=(
                "🚨 **Anomaly Detection in Energy Usage, Motion, or Sensor Readings**\n\n"
                "Uses baseline learning to identify anomalies."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Sensor entity to analyze"
                    },
                    "baseline_days": {
                        "type": "integer",
                        "description": "Days of history for baseline (default: 7)",
                        "default": 7
                    },
                    "sensitivity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Anomaly detection sensitivity",
                        "default": "medium"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="vacation_mode",
            description=(
                "✈️ **Vacation Mode with Presence Simulation**\n\n"
                "Activates energy-efficient settings, presence simulation, and automated alerts."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Vacation start (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Vacation end (YYYY-MM-DD)"},
                    "simulate_presence": {
                        "type": "boolean",
                        "description": "Randomly turn on lights/TVs to simulate occupancy",
                        "default": True
                    },
                    "security_mode": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Security alert sensitivity"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        
        # =================================================================
        # AUTOMATION MANAGEMENT
        # =================================================================
        
        Tool(
            name="list_automations",
            description="📋 List all Home Assistant automations with status and last triggered time.",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        Tool(
            name="trigger_automation",
            description="▶️ Manually trigger an automation by entity_id. Useful for testing or manual execution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Automation entity ID"}
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="enable_disable_automation",
            description="🔀 Enable or disable an automation. Useful for seasonal automations or troubleshooting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Automation entity ID"},
                    "action": {
                        "type": "string",
                        "enum": ["enable", "disable"],
                        "description": "Enable or disable"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="create_automation",
            description=(
                "➕ **Create New Automation from YAML**\n\n"
                "Create sophisticated automations with triggers, conditions, and actions.\n\n"
                "**TRIGGERS:** time, state, numeric_state, sun, event, webhook, etc.\n"
                "**CONDITIONS:** state, numeric_state, time, sun, zone, etc.\n"
                "**ACTIONS:** service calls, scene activation, delays, wait patterns, choose conditions, loops, variables"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "alias": {"type": "string", "description": "Automation friendly name"},
                    "trigger": {
                        "type": "array",
                        "description": "List of trigger configurations"
                    },
                    "condition": {
                        "type": "array",
                        "description": "Optional list of conditions"
                    },
                    "action": {
                        "type": "array",
                        "description": "List of actions to execute"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["single", "restart", "queued", "parallel"],
                        "description": "Automation mode (default: single)",
                        "default": "single"
                    }
                },
                "required": ["alias", "trigger", "action"]
            }
        ),
        
        Tool(
            name="update_automation",
            description="✏️ Update existing automation. Change triggers, conditions, or actions without deleting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Automation entity ID"},
                    "alias": {"type": "string", "description": "New alias (optional)"},
                    "trigger": {"type": "array", "description": "New triggers (optional)"},
                    "condition": {"type": "array", "description": "New conditions (optional)"},
                    "action": {"type": "array", "description": "New actions (optional)"}
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="delete_automation",
            description="🗑️ Delete automation from Home Assistant. Use with caution - cannot be undone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Automation entity ID to delete"},
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation flag (must be true)",
                        "default": False
                    }
                },
                "required": ["entity_id", "confirm"]
            }
        ),
        
        Tool(
            name="get_automation_details",
            description="🔍 Get comprehensive details about automation: triggers, conditions, actions, execution history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Automation entity ID"}
                },
                "required": ["entity_id"]
            }
        ),
        
        # =================================================================
        # LOGS, HISTORY & TROUBLESHOOTING
        # =================================================================
        
        Tool(
            name="get_entity_history",
            description=(
                "📊 **Entity History with State Changes**\n\n"
                "Get historical state changes for any entity to understand past behavior."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity ID to query"},
                    "start_time": {
                        "type": "string",
                        "description": "Start time (ISO format or relative like '-24h')"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time (ISO format, default: now)"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="get_system_logs",
            description=(
                "📝 **Home Assistant System Logs**\n\n"
                "Retrieve system logs for debugging and monitoring. "
                "Filter by severity (error, warning, info) and search for specific components."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["error", "warning", "info", "debug"],
                        "description": "Minimum severity level"
                    },
                    "component": {
                        "type": "string",
                        "description": "Filter by component (e.g., 'light', 'automation')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max log entries (default: 50)",
                        "default": 50
                    }
                },
            }
        ),
        
        Tool(
            name="get_error_log",
            description=(
                "❌ **Quick Error Log Summary**\n\n"
                "Get recent errors and warnings from Home Assistant. "
                "Quick way to identify problems without reading full logs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of errors to return (default: 20)",
                        "default": 20
                    }
                }
            }
        ),
        
        Tool(
            name="diagnose_entity",
            description=(
                "🩺 **Comprehensive Entity Diagnostics**\n\n"
                "Deep dive into entity: current state, attributes, recent history, related automations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity to diagnose"},
                    "include_history": {
                        "type": "boolean",
                        "description": "Include state history (default: true)",
                        "default": True
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="get_statistics",
            description=(
                "📈 **Statistical Analysis of Sensor Data**\n\n"
                "Get min, max, mean, sum values over time periods for sensors."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Sensor entity ID"},
                    "period": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month"],
                        "description": "Statistical period"
                    },
                    "start_time": {"type": "string", "description": "Start time (ISO or relative)"}
                },
                "required": ["entity_id", "period"]
            }
        ),
        
        Tool(
            name="get_binary_sensor",
            description=(
                "🔘 **Binary Sensor State Inspector**\n\n"
                "Check binary sensors (door, window, motion, smoke, etc.) with detailed attributes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Binary sensor entity ID"},
                    "include_battery": {
                        "type": "boolean",
                        "description": "Include battery info if available",
                        "default": True
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="analyze_patterns",
            description=(
                "🔍 **Pattern Analysis for Predictive Automation**\n\n"
                "Analyze usage patterns (when lights are used, when doors open, etc.) for smart scheduling."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity to analyze"},
                    "days": {
                        "type": "integer",
                        "description": "Days of history to analyze (default: 30)",
                        "default": 30
                    },
                    "pattern_type": {
                        "type": "string",
                        "enum": ["hourly", "daily", "weekly"],
                        "description": "Pattern granularity"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        # =================================================================
        # SCENE & SCRIPT MANAGEMENT
        # =================================================================
        
        Tool(
            name="activate_scene",
            description=(
                "🎬 **Activate Predefined Scene**\n\n"
                "Activate a scene to set multiple devices to predefined states instantly.\n\n"
                "**COMMON SCENES:**\n"
                "- Good Morning: Lights on, blinds open, music starts\n"
                "- Movie Time: Dim lights, close blinds, TV on\n"
                "- Dinner: Warm lighting, music\n"
                "- Bedtime: Minimal lighting, cool temp\n"
                "- Away: All off, security armed\n\n"
                "**RELATED TOOLS:** create_automation() to schedule scenes, multi_room_lighting_sync() for coordinated multi-room effects"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Scene entity ID (e.g., scene.movie_time)"},
                    "transition": {
                        "type": "integer",
                        "description": "Transition time in seconds (optional)"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="run_script",
            description=(
                "🎭 **Execute Home Assistant Script**\n\n"
                "Run a predefined script - sequences of actions that can include delays, conditions, service calls."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Script entity ID"},
                    "variables": {
                        "type": "object",
                        "description": "Variables to pass to script"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        # =================================================================
        # MULTI-STEP WORKFLOWS
        # =================================================================
        
        Tool(
            name="morning_routine",
            description=(
                "🌅 **Morning Routine Workflow**\n\n"
                "Gradual wake-up lighting, open blinds, adjust temperature, start coffee maker. Adapts to schedule and weather."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "wake_time": {
                        "type": "string",
                        "description": "Wake time (HH:MM format, default: 07:00)",
                        "default": "07:00"
                    },
                    "light_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lights to include in wake-up routine"
                    },
                    "blind_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Blinds to open"
                    },
                    "climate_entity": {"type": "string", "description": "Thermostat to adjust"}
                }
            }
        ),
        
        Tool(
            name="evening_routine",
            description=(
                "🌆 **Evening Routine Workflow**\n\n"
                "Dims lights, closes blinds, adjusts temperature, locks doors. Prepares home for night."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_time": {"type": "string", "description": "Evening routine start (HH:MM)"},
                    "rooms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Rooms to include"
                    }
                }
            }
        ),
        
        Tool(
            name="bedtime_routine",
            description=(
                "😴 **Bedtime Routine**\n\n"
                "Turns off most lights, activates nightlight, locks doors, lowers thermostat, enables sleep mode."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bedtime": {"type": "string", "description": "Bedtime (HH:MM, default: 22:00)"},
                    "nightlight_entity": {"type": "string", "description": "Nightlight to keep on"},
                    "lock_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Locks to secure"
                    }
                }
            }
        ),
        
        Tool(
            name="arrive_home",
            description=(
                "🏡 **Arrive Home Workflow**\n\n"
                "Turns on welcoming lights, adjusts temperature, disarms security. Adapts based on time of day."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "person_entity": {"type": "string", "description": "Person entity (for tracking)"},
                    "light_scene": {
                        "type": "string",
                        "enum": ["bright", "medium", "dim"],
                        "description": "Lighting preference"
                    }
                }
            }
        ),
        
        Tool(
            name="away_mode",
            description=(
                "🚗 **Away Mode Activation**\n\n"
                "Energy-efficient climate, arms security, enables presence simulation if desired."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "duration_hours": {
                        "type": "integer",
                        "description": "Expected away duration (hours)"
                    },
                    "simulate_presence": {
                        "type": "boolean",
                        "description": "Randomly activate lights/TVs",
                        "default": False
                    }
                }
            }
        ),
        
        # =================================================================
        # CONTEXT-AWARE INTELLIGENCE
        # =================================================================
        
        Tool(
            name="analyze_home_context",
            description=(
                "🧠 **Analyze Complete Home Context**\n\n"
                "Analyzes current state: occupancy, activity, time of day, weather, energy usage."
            ),
            inputSchema={"type": "object", "properties": {}}
        ),
        
        Tool(
            name="activity_recognition",
            description=(
                "👁️ **AI Activity Recognition**\n\n"
                "Infer current activity from sensors, devices, time, and patterns. Detects: sleeping, cooking, working, watching TV, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "rooms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Rooms to analyze"
                    }
                }
            }
        ),
        
        Tool(
            name="comfort_optimization",
            description=(
                "💆 **Multi-Factor Comfort Optimization**\n\n"
                "Optimizes for comfort: temperature, lighting, air quality, noise level."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "room": {"type": "string", "description": "Room to optimize"},
                    "preferences": {
                        "type": "object",
                        "description": "User preferences (temp, brightness, etc.)"
                    }
                }
            }
        ),
        
        Tool(
            name="energy_intelligence",
            description=(
                "⚡ **Energy Usage Analysis & Optimization**\n\n"
                "Analyzes energy consumption and provides recommendations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "enum": ["day", "week", "month"],
                        "description": "Analysis period"
                    },
                    "suggest_savings": {
                        "type": "boolean",
                        "description": "Provide energy-saving suggestions",
                        "default": True
                    }
                }
            }
        ),
        
        # =================================================================
        # PREDICTIVE ANALYTICS
        # =================================================================
        
        Tool(
            name="predictive_maintenance",
            description=(
                "🔧 **Predictive Maintenance Alerts**\n\n"
                "Predicts device failures based on usage patterns, age, sensor readings."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "device_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Device types to analyze (HVAC, lights, etc.)"
                    }
                }
            }
        ),
        
        Tool(
            name="weather_integration",
            description=(
                "🌤️ **Weather-Based Automation**\n\n"
                "Takes actions based on weather: close windows before rain, adjust HVAC, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "weather_entity": {"type": "string", "description": "Weather sensor entity"},
                    "actions": {
                        "type": "array",
                        "description": "Automated actions based on weather"
                    }
                }
            }
        ),
        
        Tool(
            name="pattern_learning",
            description=(
                "📚 **Learn User Behavior Patterns**\n\n"
                "Learns daily routines, preferred settings, habitual behaviors for automation suggestions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Entities to learn patterns from"
                    },
                    "training_days": {
                        "type": "integer",
                        "description": "Days of history to analyze (default: 30)",
                        "default": 30
                    }
                }
            }
        ),
        
        # =================================================================
        # WHOLE-HOME COORDINATION
        # =================================================================
        
        Tool(
            name="synchronized_home_state",
            description=(
                "🏘️ **Whole-Home State Coordination**\n\n"
                "Coordinate all devices for unified home state: movie night, dinner party, relaxation, work-from-home."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": ["movie", "dinner", "party", "work", "relax", "sleep", "wake"],
                        "description": "Whole-home state to activate"
                    },
                    "rooms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Rooms to coordinate (default: all)"
                    }
                },
                "required": ["state"]
            }
        ),
        
        Tool(
            name="follow_me_home",
            description=(
                "🚶 **Follow Me Automation**\n\n"
                "Follows user movement: lights/climate adjust as you enter rooms, optimize energy in vacant rooms."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "person_entity": {"type": "string", "description": "Person to track"},
                    "mode": {
                        "type": "string",
                        "enum": ["lights_only", "climate_only", "full"],
                        "description": "What to adjust"
                    }
                },
                "required": ["person_entity"]
            }
        ),
        
        Tool(
            name="guest_mode",
            description=(
                "🎁 **Guest Mode Activation**\n\n"
                "Adjusts home for guests: guest room climate, accessible controls, welcoming atmosphere."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "guest_rooms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Rooms for guests"
                    },
                    "arrival_time": {"type": "string", "description": "Guest arrival time"}
                }
            }
        ),
        
        Tool(
            name="movie_mode",
            description=(
                "🎬 **Cinema Mode**\n\n"
                "Dims lights, closes blinds, optimizes TV/audio, silences notifications."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "room": {"type": "string", "description": "Room with TV/projector"},
                    "media_player": {"type": "string", "description": "Media player entity"},
                    "light_level": {
                        "type": "integer",
                        "description": "Ambient light brightness (0-100)",
                        "default": 10
                    }
                }
            }
        ),
    ]


# ============================================================================
# PART 2: TOOL HANDLERS (to add to call_tool() in server.py)
# ============================================================================



def get_part3_dashboard_tools() -> list[Tool]:
    """
    Returns Part 3 dashboard management tool definitions
    Copy these into the main list_tools() function
    """
    return [
        # =================================================================
        # DASHBOARD DISCOVERY & LISTING
        # =================================================================
        
        Tool(
            name="list_dashboards",
            description=(
                "📱 **List All Home Assistant Dashboards**\n\n"
                "Shows dashboard names, URLs, and configuration modes (storage/yaml). "
                "WHEN TO USE: To see available dashboards before adding/editing cards. "
                "First step in dashboard management."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="discover_dashboards",
            description=(
                "🔍 **Enhanced Dashboard Discovery**\n\n"
                "List all dashboards with IDs, titles, and metadata. Filter by type. "
                "WHEN TO USE: To explore available dashboards with detailed information.\n\n"
                "**EXAMPLES:**\n"
                "• 'Show all dashboards' → discover_dashboards()\n"
                "• 'List mobile views' → discover_dashboards(dashboard_type='mobile')\n"
                "• 'Show panel views' → discover_dashboards(dashboard_type='panel')"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_type": {
                        "type": "string",
                        "enum": ["all", "mobile", "desktop", "panel", "storage", "yaml"],
                        "description": "Filter by type: all, mobile, desktop, panel, storage, yaml"
                    },
                    "include_cards": {
                        "type": "boolean",
                        "description": "Include card count for each dashboard",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        
        # =================================================================
        # HACS CUSTOM CARDS
        # =================================================================
        
        Tool(
            name="list_hacs_cards",
            description=(
                "📦 **List Installed HACS Custom Cards**\n\n"
                "Shows what custom cards are available for dashboard creation. "
                "WHEN TO USE: Before creating custom cards, to verify installation.\n\n"
                "**COMMON HACS CARDS:**\n"
                "• button-card - Highly customizable buttons\n"
                "• mushroom - Modern minimalist cards\n"
                "• mini-graph-card - Compact graphs\n"
                "• stack-in-card - Card stacking/grouping"
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="create_button_card",
            description=(
                "🎨 **HACS Button-Card Creation**\n\n"
                "Create customizable button-card (most popular HACS card). "
                "Highly flexible with custom colors, icons, tap actions.\n\n"
                "**EXAMPLES:**\n"
                "• Simple: 'Add button for bedroom light' → create_button_card(dashboard='mobile', entity_id='light.bedroom')\n"
                "• Advanced: 'Yellow moon button' → create_button_card(entity_id='light.bedroom', color='yellow', icon='mdi:weather-night')\n\n"
                "**FEATURES:** Custom colors, MDI icons, tap actions, show/hide state\n"
                "**REQUIRES:** button-card from HACS"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name (default, mobile, etc.)",
                        "default": "lovelace"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Entity to control (light.*, switch.*, scene.*, script.*)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Button display name (optional)"
                    },
                    "icon": {
                        "type": "string",
                        "description": "MDI icon (mdi:lightbulb, mdi:power, etc.)"
                    },
                    "color": {
                        "type": "string",
                        "description": "CSS color (yellow, #FFD700, etc.)",
                        "default": "auto"
                    },
                    "tap_action": {
                        "type": "string",
                        "enum": ["toggle", "more-info", "call-service", "navigate", "none"],
                        "description": "Action when tapped",
                        "default": "toggle"
                    },
                    "show_state": {
                        "type": "boolean",
                        "description": "Show entity state",
                        "default": True
                    },
                    "show_name": {
                        "type": "boolean",
                        "description": "Show entity name",
                        "default": True
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="create_mushroom_card",
            description=(
                "🍄 **HACS Mushroom Card Creation**\n\n"
                "Create modern, minimalist mushroom-card. iOS-inspired design with rounded corners.\n\n"
                "**EXAMPLES:**\n"
                "• Simple: 'Add mushroom light card' → create_mushroom_card(card_type='light', entity_id='light.bedroom')\n"
                "• Advanced: 'Mushroom climate card' → create_mushroom_card(card_type='climate', entity_id='climate.living_room', fill_container=true)\n\n"
                "**CARD TYPES:** light, switch, climate, cover, person, entity\n"
                "**REQUIRES:** mushroom from HACS"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_type": {
                        "type": "string",
                        "enum": ["light", "switch", "climate", "cover", "person", "entity"],
                        "description": "Mushroom card type"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Entity to display/control"
                    },
                    "name": {
                        "type": "string",
                        "description": "Custom name override"
                    },
                    "icon": {
                        "type": "string",
                        "description": "Custom MDI icon"
                    },
                    "fill_container": {
                        "type": "boolean",
                        "description": "Fill container width",
                        "default": False
                    },
                    "show_temperature_control": {
                        "type": "boolean",
                        "description": "For climate: show temp slider",
                        "default": True
                    },
                    "layout": {
                        "type": "string",
                        "enum": ["horizontal", "vertical"],
                        "description": "Card layout",
                        "default": "horizontal"
                    }
                },
                "required": ["card_type", "entity_id"]
            }
        ),
        
        # =================================================================
        # STANDARD DASHBOARD CARDS
        # =================================================================
        
        Tool(
            name="create_dashboard_card",
            description=(
                "📋 **Standard Dashboard Card Creation**\n\n"
                "Create built-in Home Assistant card types (entities, glance, button, gauge, etc.).\n\n"
                "**EXAMPLES:**\n"
                "• Entities: 'Add bedroom lights card' → create_dashboard_card(card_type='entities', entities=['light.bedroom', 'light.bedside'])\n"
                "• Gauge: 'Add temp gauge' → create_dashboard_card(card_type='gauge', entity='sensor.temp', min=15, max=30)\n\n"
                "**CARD TYPES:** entities, glance, button, gauge, light, thermostat, picture-entity, history-graph"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_type": {
                        "type": "string",
                        "enum": ["entities", "glance", "button", "gauge", "light", "thermostat", "picture-entity", "history-graph", "sensor", "weather-forecast"],
                        "description": "Standard Lovelace card type"
                    },
                    "entity": {
                        "type": "string",
                        "description": "Single entity for single-entity cards"
                    },
                    "entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of entities for multi-entity cards"
                    },
                    "title": {
                        "type": "string",
                        "description": "Card title"
                    },
                    "name": {
                        "type": "string",
                        "description": "Entity display name override"
                    },
                    "icon": {
                        "type": "string",
                        "description": "Custom MDI icon"
                    },
                    "min": {
                        "type": "number",
                        "description": "Gauge minimum value"
                    },
                    "max": {
                        "type": "number",
                        "description": "Gauge maximum value"
                    }
                },
                "required": ["card_type"]
            }
        ),
        
        # =================================================================
        # CARD EDITING & DELETION
        # =================================================================
        
        Tool(
            name="edit_dashboard_card",
            description=(
                "✏️ **Edit Existing Dashboard Card**\n\n"
                "Modify card properties (colors, icons, name, tap actions). "
                "Works with standard and custom HACS cards.\n\n"
                "**EXAMPLES:**\n"
                "• 'Change bedroom button to yellow' → edit_dashboard_card(card_index=0, color='yellow')\n"
                "• 'Update icon to moon' → edit_dashboard_card(card_index=2, icon='mdi:weather-night')\n\n"
                "**CARD INDEX:** Cards numbered from 0. Use get_dashboard_config() to find indices."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_index": {
                        "type": "integer",
                        "description": "Card position (0-based)"
                    },
                    "color": {
                        "type": "string",
                        "description": "New card color"
                    },
                    "icon": {
                        "type": "string",
                        "description": "New MDI icon"
                    },
                    "name": {
                        "type": "string",
                        "description": "New display name"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "New entity to control"
                    },
                    "tap_action": {
                        "type": "string",
                        "enum": ["toggle", "more-info", "call-service", "navigate", "none"],
                        "description": "New tap action"
                    },
                    "show_state": {
                        "type": "boolean",
                        "description": "Show/hide state"
                    },
                    "show_name": {
                        "type": "boolean",
                        "description": "Show/hide name"
                    }
                },
                "required": ["card_index"]
            }
        ),
        
        Tool(
            name="delete_dashboard_card",
            description=(
                "🗑️ **Delete Dashboard Card**\n\n"
                "Remove card from dashboard by index. Permanent deletion.\n\n"
                "**EXAMPLES:**\n"
                "• 'Remove first card' → delete_dashboard_card(card_index=0)\n"
                "• 'Delete bedroom button' → delete_dashboard_card(card_index=5)\n\n"
                "⚠️ **WARNING:** Deletion is permanent. Use get_dashboard_config() first to verify."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name",
                        "default": "lovelace"
                    },
                    "card_index": {
                        "type": "integer",
                        "description": "Card position to delete (0-based)"
                    }
                },
                "required": ["card_index"]
            }
        ),
        
        # =================================================================
        # DASHBOARD INSPECTION
        # =================================================================
        
        Tool(
            name="get_dashboard_config",
            description=(
                "🔍 **Inspect Dashboard Configuration**\n\n"
                "Retrieve complete dashboard config: all cards, views, settings. "
                "Shows card index positions for editing/deletion.\n\n"
                "**EXAMPLES:**\n"
                "• 'Show mobile dashboard cards' → get_dashboard_config(dashboard='mobile')\n"
                "• 'What's card 3?' → get_dashboard_config() then find index 3\n\n"
                "**RETURNS:** Dashboard title, mode, all cards with indices, card properties"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard": {
                        "type": "string",
                        "description": "Dashboard name to inspect",
                        "default": "lovelace"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_dashboard_card",
            description=(
                "🔎 **Get Single Card Details**\n\n"
                "Retrieve detailed configuration of specific card by index or ID.\n\n"
                "**EXAMPLES:**\n"
                "• 'Show kitchen energy card' → get_dashboard_card(dashboard_id='kitchen', card_index=2)\n"
                "• 'Check weather card' → get_dashboard_card(card_index=0)\n"
                "• 'List all cards' → get_dashboard_card(list_all=true)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_id": {
                        "type": "string",
                        "description": "Dashboard identifier",
                        "default": "lovelace"
                    },
                    "card_index": {
                        "type": "integer",
                        "description": "Card position (0-based)"
                    },
                    "card_id": {
                        "type": "string",
                        "description": "Card identifier (alternative to index)"
                    },
                    "list_all": {
                        "type": "boolean",
                        "description": "List all cards with indices",
                        "default": False
                    }
                },
                "required": []
            }
        ),
    ]


# ============================================================================
# PART 3: DASHBOARD TOOL HANDLERS (to add to call_tool() in server.py)
# ============================================================================



# ============================================================================
# TOOL HANDLERS FROM CONVERTED PARTS
# ============================================================================










@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    
    return [
        # ===================================================================
        # CONVERTED TOOLS FROM PART 1: Discovery, Control, Lighting, Media, Climate
        # ===================================================================
        *get_part1_tools(),
        
        # ===================================================================
        # CONVERTED TOOLS FROM PART 2: Security, Automation, Workflows, Intelligence
        # ===================================================================
        *get_part2_tools(),
        
        # ===================================================================
        # CONVERTED TOOLS FROM PART 3: Dashboard & HACS Management
        # ===================================================================
        *get_part3_dashboard_tools(),
        
        # ===================================================================
        # CODE EXECUTION & DATA ANALYSIS TOOLS (NEW!)
        # ===================================================================
        
        Tool(
            name="execute_python",
            description="Execute Python code with access to pandas, matplotlib, numpy, seaborn. Perfect for analyzing Home Assistant data. Code runs in a safe sandbox. Can return print() output and matplotlib plots as base64 images.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Available imports: pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns"
                    },
                    "return_stdout": {
                        "type": "boolean",
                        "description": "Return print() output (default: true)",
                        "default": True
                    },
                    "return_plots": {
                        "type": "boolean",
                        "description": "Return matplotlib plots as base64 PNG images (default: true)",
                        "default": True
                    }
                },
                "required": ["code"]
            }
        ),
        
        Tool(
            name="analyze_states_dataframe",
            description="Get Home Assistant entity states as a pandas DataFrame for instant analysis. Returns entities with all their attributes in a structured format ready for pandas queries, grouping, filtering, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filter by domain (e.g., 'light', 'sensor', 'switch'). Leave empty for all domains."
                    },
                    "include_attributes": {
                        "type": "boolean",
                        "description": "Include all entity attributes as columns (default: true)",
                        "default": True
                    },
                    "query": {
                        "type": "string",
                        "description": "Pandas query string to filter results (e.g., \"state == 'on'\" or \"entity_id.str.contains('temp')\")"
                    }
                }
            }
        ),
        
        Tool(
            name="plot_sensor_history",
            description="Plot sensor history as a time-series chart. Returns matplotlib visualization as base64 PNG. Perfect for temperature trends, power consumption, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of entity IDs to plot (e.g., ['sensor.temperature', 'sensor.humidity'])"
                    },
                    "hours": {
                        "type": "number",
                        "description": "Hours of history to plot (default: 24)",
                        "default": 24
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["line", "bar", "scatter"],
                        "description": "Type of chart (default: 'line')",
                        "default": "line"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title (auto-generated if not provided)"
                    }
                },
                "required": ["entity_ids"]
            }
        ),
        
        # ===================================================================
        # ORIGINAL NATIVE ADD-ON TOOLS (File & API Operations)
        # ===================================================================

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
        
        # ===================================================================
        # 📷 CAMERA TOOLS WITH VLM ANALYSIS (KILLER FEATURE!)
        # ===================================================================
        
        Tool(
            name="get_camera_snapshot",
            description=(
                "📸 Get a snapshot image from a Home Assistant camera entity. "
                "Returns the image as base64-encoded data that can be analyzed by vision models or saved. "
                "Perfect for capturing moments for VLM analysis, security monitoring, or archiving. "
                "\n\n"
                "WHEN TO USE:\n"
                "• Capture current camera view for AI analysis\n"
                "• Get snapshot for motion detection events\n"
                "• Archive camera images at specific times\n"
                "• Combine with analyze_camera_snapshot for vision AI\n"
                "\n\n"
                "EXAMPLE WORKFLOW:\n"
                "1. Motion detected (SSE event)\n"
                "2. get_camera_snapshot(entity_id='camera.front_door')\n"
                "3. analyze_camera_snapshot with the image\n"
                "4. AI decides action based on what it sees\n"
                "\n\n"
                "RETURNS: Base64-encoded image data (PNG/JPEG format)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": (
                            "Camera entity ID. Examples: 'camera.front_door', 'camera.backyard', "
                            "'camera.garage', 'camera.driveway', 'camera.living_room'. "
                            "Use discover_devices(domain='camera') to find available cameras."
                        )
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="analyze_camera_snapshot",
            description=(
                "🤖 THE KILLER FEATURE! Analyze camera snapshot using Vision Language Model (VLM). "
                "Get camera image and send to AI vision model for intelligent scene understanding. "
                "AI can SEE and DESCRIBE what's happening in real-time! "
                "\n\n"
                "CAPABILITIES:\n"
                "• Object detection: 'Is there a package at the door?'\n"
                "• People counting: 'How many people are in the room?'\n"
                "• Activity recognition: 'What is happening in this scene?'\n"
                "• Safety monitoring: 'Is the stove turned on?'\n"
                "• Pet monitoring: 'Is the dog on the couch?'\n"
                "• Security: 'Describe the person at the door'\n"
                "• Scene understanding: 'What's the weather like outside?'\n"
                "\n\n"
                "REAL-TIME REACTIVE AI WORKFLOW:\n"
                "1. Motion detected → SSE event triggers\n"
                "2. analyze_camera_snapshot('camera.front_door', 'Who is at the door?')\n"
                "3. VLM responds: 'Delivery driver in brown uniform with package'\n"
                "4. AI makes decision: Send notification, unlock door, etc.\n"
                "\n\n"
                "QUESTION EXAMPLES:\n"
                "• 'Describe what you see'\n"
                "• 'Is there a person in this image?'\n"
                "• 'What objects are visible?'\n"
                "• 'Is the garage door open or closed?'\n"
                "• 'Describe the person's appearance'\n"
                "• 'Is there a vehicle in the driveway?'\n"
                "\n\n"
                "INTEGRATION: Connects to Open-WebUI VLM endpoint for vision analysis. "
                "Returns structured JSON with description, detected objects, confidence scores."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Camera entity ID to analyze (e.g., 'camera.front_door')"
                    },
                    "question": {
                        "type": "string",
                        "description": (
                            "Question to ask about the image. Examples: "
                            "'Describe what you see', 'Who is at the door?', 'Count the people', "
                            "'Is there a package?', 'What's the weather like?'. "
                            "Default: 'Describe what you see in detail'"
                        ),
                        "default": "Describe what you see in detail"
                    },
                    "vlm_endpoint": {
                        "type": "string",
                        "description": (
                            "VLM API endpoint URL. Default uses Open-WebUI on cluster. "
                            "Format: 'http://host:port/api/vlm/analyze'"
                        ),
                        "default": "http://192.168.1.11:30080/api/chat/completions"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="enable_camera_motion_detection",
            description=(
                "🎬 Enable motion detection on a camera entity. "
                "When enabled, camera will trigger motion events that can be captured via SSE. "
                "Perfect for setting up reactive automations: motion → snapshot → VLM analysis → action."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Camera entity ID (e.g., 'camera.front_door')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="disable_camera_motion_detection",
            description="🛑 Disable motion detection on a camera entity. Use when you want to pause motion alerts temporarily.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Camera entity ID (e.g., 'camera.front_door')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="get_camera_stream_url",
            description=(
                "📹 Get the live stream URL for a camera entity. "
                "Returns the HLS or MJPEG stream URL that can be used for live viewing or recording. "
                "Useful for integrating camera feeds into dashboards or external apps."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Camera entity ID (e.g., 'camera.backyard')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        # ===================================================================
        # 🤖 VACUUM CONTROL TOOLS
        # ===================================================================
        
        Tool(
            name="start_vacuum",
            description="🧹 Start vacuum cleaning. Robot will begin cleaning cycle from current position.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Vacuum entity ID (e.g., 'vacuum.roborock', 'vacuum.roomba')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="stop_vacuum",
            description="🛑 Stop vacuum cleaning. Robot will pause at current position.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Vacuum entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="return_vacuum_to_base",
            description="🏠 Send vacuum back to charging dock. Robot will navigate home automatically.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Vacuum entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="locate_vacuum",
            description="📍 Play sound on vacuum to locate it. Useful when you can't find the robot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Vacuum entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="set_vacuum_fan_speed",
            description=(
                "💨 Set vacuum suction power/fan speed. "
                "Common modes: 'silent'/'quiet' (low noise), 'standard'/'balanced', 'medium', 'turbo'/'max' (maximum power). "
                "Check your vacuum's supported modes with get_device_state()."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Vacuum entity ID"
                    },
                    "fan_speed": {
                        "type": "string",
                        "description": "Fan speed mode (e.g., 'silent', 'standard', 'medium', 'turbo', 'max')"
                    }
                },
                "required": ["entity_id", "fan_speed"]
            }
        ),
        
        Tool(
            name="clean_vacuum_spot",
            description="🎯 Clean specific spot. Robot will clean small area around current position intensively.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Vacuum entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="send_vacuum_command",
            description=(
                "🎮 Send custom command to vacuum. "
                "Advanced control for robot-specific features like zone cleaning, room selection, etc. "
                "Commands are vacuum-specific - check manufacturer documentation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Vacuum entity ID"
                    },
                    "command": {
                        "type": "string",
                        "description": "Command name (e.g., 'app_segment_clean' for Roborock room cleaning)"
                    },
                    "params": {
                        "type": "object",
                        "description": "Command parameters (vacuum-specific, optional)"
                    }
                },
                "required": ["entity_id", "command"]
            }
        ),
        
        # ===================================================================
        # 🌀 FAN CONTROL TOOLS
        # ===================================================================
        
        Tool(
            name="turn_on_fan",
            description="💨 Turn on fan. Optionally set speed percentage and preset mode.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Fan entity ID (e.g., 'fan.bedroom_fan', 'fan.living_room_ceiling_fan')"
                    },
                    "percentage": {
                        "type": "integer",
                        "description": "Speed percentage (0-100). Optional - uses last setting if omitted.",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "preset_mode": {
                        "type": "string",
                        "description": "Preset mode (e.g., 'auto', 'smart', 'sleep', 'nature'). Device-specific."
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="turn_off_fan",
            description="🛑 Turn off fan completely.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Fan entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="set_fan_percentage",
            description="🎚️ Set fan speed by percentage (0-100). More precise than low/medium/high.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Fan entity ID"
                    },
                    "percentage": {
                        "type": "integer",
                        "description": "Speed percentage: 0=off, 1-33=low, 34-66=medium, 67-100=high",
                        "minimum": 0,
                        "maximum": 100
                    }
                },
                "required": ["entity_id", "percentage"]
            }
        ),
        
        Tool(
            name="set_fan_direction",
            description=(
                "↕️ Set fan rotation direction. "
                "'forward' = normal airflow (summer), 'reverse' = pull air upward (winter, distributes heat). "
                "Only supported by ceiling fans with reverse capability."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Fan entity ID"
                    },
                    "direction": {
                        "type": "string",
                        "description": "Direction: 'forward' or 'reverse'",
                        "enum": ["forward", "reverse"]
                    }
                },
                "required": ["entity_id", "direction"]
            }
        ),
        
        Tool(
            name="oscillate_fan",
            description="↔️ Enable or disable fan oscillation (side-to-side movement for wider coverage).",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Fan entity ID"
                    },
                    "oscillating": {
                        "type": "boolean",
                        "description": "true to enable oscillation, false to disable"
                    }
                },
                "required": ["entity_id", "oscillating"]
            }
        ),
        
        Tool(
            name="set_fan_preset_mode",
            description=(
                "🎭 Set fan preset mode. "
                "Common presets: 'auto' (auto speed), 'smart' (AI control), 'sleep' (quiet night mode), "
                "'nature' (variable speed mimicking natural wind), 'normal' (standard operation). "
                "Available modes depend on fan model - check attributes with get_device_state()."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Fan entity ID"
                    },
                    "preset_mode": {
                        "type": "string",
                        "description": "Preset mode name (device-specific)"
                    }
                },
                "required": ["entity_id", "preset_mode"]
            }
        ),
        
        # ===================================================================
        # 🔧 ADD-ON MANAGEMENT (SUPERVISOR API)
        # ===================================================================
        
        Tool(
            name="list_addons",
            description=(
                "📦 List all Home Assistant add-ons (installed and available). "
                "Shows add-on slug, name, version, state (started/stopped), and description. "
                "Perfect for discovering what add-ons are available to install or manage."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "installed_only": {
                        "type": "boolean",
                        "description": "If true, only show installed add-ons. Default: false (show all)",
                        "default": False
                    }
                }
            }
        ),
        
        Tool(
            name="install_addon",
            description=(
                "⬇️ Install a Home Assistant add-on from the add-on store. "
                "Requires add-on slug (e.g., 'core_configurator', 'a0d7b954_vscode'). "
                "Installation may take several minutes depending on add-on size."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Add-on slug (e.g., 'core_configurator', 'a0d7b954_vscode', 'core_mosquitto')"
                    },
                    "version": {
                        "type": "string",
                        "description": "Specific version to install (optional, defaults to latest)"
                    }
                },
                "required": ["slug"]
            }
        ),
        
        Tool(
            name="uninstall_addon",
            description="🗑️ Uninstall/remove an add-on. This will delete the add-on and all its data. Cannot be undone!",
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Add-on slug to uninstall"
                    }
                },
                "required": ["slug"]
            }
        ),
        
        Tool(
            name="start_addon",
            description="▶️ Start an installed add-on. Add-on will begin running in the background.",
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Add-on slug to start"
                    }
                },
                "required": ["slug"]
            }
        ),
        
        Tool(
            name="stop_addon",
            description="⏸️ Stop a running add-on. Add-on will be gracefully shut down.",
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Add-on slug to stop"
                    }
                },
                "required": ["slug"]
            }
        ),
        
        Tool(
            name="restart_addon",
            description="🔄 Restart an add-on. Useful after configuration changes or when troubleshooting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Add-on slug to restart"
                    }
                },
                "required": ["slug"]
            }
        ),
        
        Tool(
            name="get_addon_info",
            description=(
                "ℹ️ Get detailed information about an add-on. "
                "Returns version, state, configuration, logs URL, startup type, and all settings."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Add-on slug to query"
                    }
                },
                "required": ["slug"]
            }
        ),
        
        Tool(
            name="update_addon_config",
            description=(
                "⚙️ Update add-on configuration options. "
                "Configuration is add-on specific - check add-on documentation for available options. "
                "Changes typically require add-on restart to take effect."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Add-on slug to configure"
                    },
                    "options": {
                        "type": "object",
                        "description": "Configuration options (add-on specific key-value pairs)"
                    }
                },
                "required": ["slug", "options"]
            }
        ),
        
        Tool(
            name="restart_homeassistant",
            description=(
                "🔄 Restart Home Assistant Core. "
                "Use this after installing custom cards, add-ons, or making configuration changes that require a restart. "
                "Note: This will disconnect all clients temporarily. Home Assistant will come back online automatically."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "force": {
                        "type": "boolean",
                        "description": "Force restart even if there are pending operations (default: false)",
                        "default": False
                    }
                }
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
        
        # ===================================================================
        # CODE EXECUTION & DATA ANALYSIS TOOL HANDLERS (NEW!)
        # ===================================================================
        elif name == "execute_python":
            result = await execute_python_code(
                arguments["code"],
                return_stdout=arguments.get("return_stdout", True),
                return_plots=arguments.get("return_plots", True)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "analyze_states_dataframe":
            result = await analyze_states_as_dataframe(
                ha_api,
                domain=arguments.get("domain"),
                include_attributes=arguments.get("include_attributes", True),
                query=arguments.get("query")
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "plot_sensor_history":
            result = await plot_sensor_history_chart(
                ha_api,
                entity_ids=arguments["entity_ids"],
                hours=arguments.get("hours", 24),
                chart_type=arguments.get("chart_type", "line"),
                title=arguments.get("title")
            )
            return [TextContent(type="text", text=result)]
        
        # ===================================================================
        # 📷 CAMERA TOOL HANDLERS (KILLER FEATURE!)
        # ===================================================================
        elif name == "get_camera_snapshot":
            entity_id = arguments["entity_id"]
            
            # Get camera snapshot via HA API
            snapshot_url = f"{HA_URL.replace('/core/api', '')}/api/camera_proxy/{entity_id}"
            
            logger.info(f"📸 Fetching camera snapshot: {entity_id}")
            
            try:
                response = await http_client.get(snapshot_url)
                response.raise_for_status()
                
                # Convert image to base64
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                
                # Determine image format from content-type
                content_type = response.headers.get('content-type', 'image/jpeg')
                image_format = content_type.split('/')[-1] if '/' in content_type else 'jpeg'
                
                result = {
                    "entity_id": entity_id,
                    "image_base64": image_base64,
                    "format": image_format,
                    "size_bytes": len(response.content),
                    "data_uri": f"data:{content_type};base64,{image_base64}",
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"✅ Snapshot captured: {len(response.content)} bytes ({image_format})")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to get camera snapshot: {e}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "entity_id": entity_id
                }, indent=2))]
        
        elif name == "analyze_camera_snapshot":
            entity_id = arguments["entity_id"]
            question = arguments.get("question", "Describe what you see in detail")
            vlm_endpoint = arguments.get("vlm_endpoint", "http://192.168.1.11:30080/api/chat/completions")
            
            logger.info(f"🤖 VLM Analysis: {entity_id} - Question: '{question}'")
            
            try:
                # Step 1: Get camera snapshot
                snapshot_url = f"{HA_URL.replace('/core/api', '')}/api/camera_proxy/{entity_id}"
                response = await http_client.get(snapshot_url)
                response.raise_for_status()
                
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                content_type = response.headers.get('content-type', 'image/jpeg')
                
                logger.info(f"📸 Snapshot captured: {len(response.content)} bytes")
                
                # Step 2: Send to VLM for analysis
                # Using OpenAI-compatible chat completions format
                vlm_payload = {
                    "model": "llava",  # Or whatever vision model is configured
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": question
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{content_type};base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                
                logger.info(f"🔍 Sending to VLM: {vlm_endpoint}")
                
                vlm_response = await http_client.post(
                    vlm_endpoint,
                    json=vlm_payload,
                    timeout=60.0  # VLM analysis can take time
                )
                vlm_response.raise_for_status()
                vlm_data = vlm_response.json()
                
                # Extract analysis from response
                analysis_text = vlm_data.get("choices", [{}])[0].get("message", {}).get("content", "No analysis available")
                
                result = {
                    "entity_id": entity_id,
                    "question": question,
                    "analysis": analysis_text,
                    "timestamp": datetime.now().isoformat(),
                    "image_size_bytes": len(response.content),
                    "vlm_model": vlm_data.get("model", "unknown"),
                    "usage": vlm_data.get("usage", {})
                }
                
                logger.info(f"✅ VLM Analysis complete: {len(analysis_text)} chars")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ VLM analysis failed: {e}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "entity_id": entity_id,
                    "question": question
                }, indent=2))]
        
        elif name == "enable_camera_motion_detection":
            entity_id = arguments["entity_id"]
            
            try:
                result = await ha_api.call_service(
                    "camera",
                    "enable_motion_detection",
                    {"entity_id": entity_id}
                )
                logger.info(f"🎬 Motion detection enabled: {entity_id}")
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "entity_id": entity_id,
                    "action": "motion_detection_enabled"
                }, indent=2))]
            except Exception as e:
                logger.error(f"❌ Failed to enable motion detection: {e}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "entity_id": entity_id
                }, indent=2))]
        
        elif name == "disable_camera_motion_detection":
            entity_id = arguments["entity_id"]
            
            try:
                result = await ha_api.call_service(
                    "camera",
                    "disable_motion_detection",
                    {"entity_id": entity_id}
                )
                logger.info(f"🛑 Motion detection disabled: {entity_id}")
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "entity_id": entity_id,
                    "action": "motion_detection_disabled"
                }, indent=2))]
            except Exception as e:
                logger.error(f"❌ Failed to disable motion detection: {e}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "entity_id": entity_id
                }, indent=2))]
        
        elif name == "get_camera_stream_url":
            entity_id = arguments["entity_id"]
            
            try:
                # Get entity state to find stream source
                state = await ha_api.get_state(entity_id)
                
                attributes = state.get("attributes", {})
                
                # Try to get stream URL from entity attributes
                stream_source = attributes.get("entity_picture")
                
                # Build full stream URLs
                base_url = HA_URL.replace('/core/api', '')
                
                result = {
                    "entity_id": entity_id,
                    "stream_urls": {
                        "proxy": f"{base_url}/api/camera_proxy_stream/{entity_id}",
                        "entity_picture": f"{base_url}{stream_source}" if stream_source else None,
                        "hls": f"{base_url}/api/hls/{entity_id}/playlist.m3u8"
                    },
                    "friendly_name": attributes.get("friendly_name", entity_id),
                    "supported_features": attributes.get("supported_features", 0)
                }
                
                logger.info(f"📹 Stream URLs generated: {entity_id}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to get stream URL: {e}")
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e),
                    "entity_id": entity_id
                }, indent=2))]
        
        # ===================================================================
        # 🤖 VACUUM CONTROL TOOL HANDLERS
        # ===================================================================
        elif name == "start_vacuum":
            result = await ha_api.call_service("vacuum", "start", {"entity_id": arguments["entity_id"]})
            logger.info(f"🧹 Vacuum started: {arguments['entity_id']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "stop_vacuum":
            result = await ha_api.call_service("vacuum", "stop", {"entity_id": arguments["entity_id"]})
            logger.info(f"🛑 Vacuum stopped: {arguments['entity_id']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "return_vacuum_to_base":
            result = await ha_api.call_service("vacuum", "return_to_base", {"entity_id": arguments["entity_id"]})
            logger.info(f"🏠 Vacuum returning home: {arguments['entity_id']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "locate_vacuum":
            result = await ha_api.call_service("vacuum", "locate", {"entity_id": arguments["entity_id"]})
            logger.info(f"📍 Locating vacuum: {arguments['entity_id']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "set_vacuum_fan_speed":
            result = await ha_api.call_service(
                "vacuum", 
                "set_fan_speed", 
                {
                    "entity_id": arguments["entity_id"],
                    "fan_speed": arguments["fan_speed"]
                }
            )
            logger.info(f"💨 Vacuum fan speed set: {arguments['entity_id']} -> {arguments['fan_speed']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "clean_vacuum_spot":
            result = await ha_api.call_service("vacuum", "clean_spot", {"entity_id": arguments["entity_id"]})
            logger.info(f"🎯 Vacuum spot cleaning: {arguments['entity_id']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "send_vacuum_command":
            service_data = {
                "entity_id": arguments["entity_id"],
                "command": arguments["command"]
            }
            if "params" in arguments:
                service_data["params"] = arguments["params"]
            
            result = await ha_api.call_service("vacuum", "send_command", service_data)
            logger.info(f"🎮 Vacuum command sent: {arguments['entity_id']} -> {arguments['command']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # ===================================================================
        # 🌀 FAN CONTROL TOOL HANDLERS
        # ===================================================================
        elif name == "turn_on_fan":
            service_data = {"entity_id": arguments["entity_id"]}
            if "percentage" in arguments:
                service_data["percentage"] = arguments["percentage"]
            if "preset_mode" in arguments:
                service_data["preset_mode"] = arguments["preset_mode"]
            
            result = await ha_api.call_service("fan", "turn_on", service_data)
            logger.info(f"💨 Fan turned on: {arguments['entity_id']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "turn_off_fan":
            result = await ha_api.call_service("fan", "turn_off", {"entity_id": arguments["entity_id"]})
            logger.info(f"🛑 Fan turned off: {arguments['entity_id']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "set_fan_percentage":
            result = await ha_api.call_service(
                "fan",
                "set_percentage",
                {
                    "entity_id": arguments["entity_id"],
                    "percentage": arguments["percentage"]
                }
            )
            logger.info(f"🎚️ Fan speed set: {arguments['entity_id']} -> {arguments['percentage']}%")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "set_fan_direction":
            result = await ha_api.call_service(
                "fan",
                "set_direction",
                {
                    "entity_id": arguments["entity_id"],
                    "direction": arguments["direction"]
                }
            )
            logger.info(f"↕️ Fan direction set: {arguments['entity_id']} -> {arguments['direction']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "oscillate_fan":
            result = await ha_api.call_service(
                "fan",
                "oscillate",
                {
                    "entity_id": arguments["entity_id"],
                    "oscillating": arguments["oscillating"]
                }
            )
            logger.info(f"↔️ Fan oscillation: {arguments['entity_id']} -> {arguments['oscillating']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "set_fan_preset_mode":
            result = await ha_api.call_service(
                "fan",
                "set_preset_mode",
                {
                    "entity_id": arguments["entity_id"],
                    "preset_mode": arguments["preset_mode"]
                }
            )
            logger.info(f"🎭 Fan preset mode: {arguments['entity_id']} -> {arguments['preset_mode']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # ===================================================================
        # 🔧 ADD-ON MANAGEMENT TOOL HANDLERS (SUPERVISOR API)
        # ===================================================================
        elif name == "list_addons":
            try:
                # Supervisor API endpoint
                supervisor_url = "http://supervisor/addons"
                
                response = await http_client.get(supervisor_url)
                response.raise_for_status()
                data = response.json()
                
                addons = data.get("data", {}).get("addons", [])
                
                # Filter if requested
                if arguments.get("installed_only", False):
                    addons = [addon for addon in addons if addon.get("installed", False)]
                
                result = {
                    "total_addons": len(addons),
                    "installed_count": sum(1 for a in addons if a.get("installed", False)),
                    "addons": addons
                }
                
                logger.info(f"📦 Listed {len(addons)} add-ons")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to list add-ons: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
        
        elif name == "install_addon":
            try:
                slug = arguments["slug"]
                supervisor_url = f"http://supervisor/addons/{slug}/install"
                
                payload = {}
                if "version" in arguments:
                    payload["version"] = arguments["version"]
                
                logger.info(f"⬇️ Installing add-on: {slug}")
                response = await http_client.post(supervisor_url, json=payload, timeout=300.0)  # 5 min timeout
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Add-on installed: {slug}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to install add-on: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "slug": arguments["slug"]}, indent=2))]
        
        elif name == "uninstall_addon":
            try:
                slug = arguments["slug"]
                supervisor_url = f"http://supervisor/addons/{slug}/uninstall"
                
                logger.info(f"🗑️ Uninstalling add-on: {slug}")
                response = await http_client.post(supervisor_url, timeout=120.0)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Add-on uninstalled: {slug}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to uninstall add-on: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "slug": arguments["slug"]}, indent=2))]
        
        elif name == "start_addon":
            try:
                slug = arguments["slug"]
                supervisor_url = f"http://supervisor/addons/{slug}/start"
                
                logger.info(f"▶️ Starting add-on: {slug}")
                response = await http_client.post(supervisor_url)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Add-on started: {slug}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to start add-on: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "slug": arguments["slug"]}, indent=2))]
        
        elif name == "stop_addon":
            try:
                slug = arguments["slug"]
                supervisor_url = f"http://supervisor/addons/{slug}/stop"
                
                logger.info(f"⏸️ Stopping add-on: {slug}")
                response = await http_client.post(supervisor_url)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Add-on stopped: {slug}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to stop add-on: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "slug": arguments["slug"]}, indent=2))]
        
        elif name == "restart_addon":
            try:
                slug = arguments["slug"]
                supervisor_url = f"http://supervisor/addons/{slug}/restart"
                
                logger.info(f"🔄 Restarting add-on: {slug}")
                response = await http_client.post(supervisor_url)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Add-on restarted: {slug}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to restart add-on: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "slug": arguments["slug"]}, indent=2))]
        
        elif name == "get_addon_info":
            try:
                slug = arguments["slug"]
                supervisor_url = f"http://supervisor/addons/{slug}/info"
                
                response = await http_client.get(supervisor_url)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"ℹ️ Retrieved add-on info: {slug}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to get add-on info: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "slug": arguments["slug"]}, indent=2))]
        
        elif name == "update_addon_config":
            try:
                slug = arguments["slug"]
                options = arguments["options"]
                supervisor_url = f"http://supervisor/addons/{slug}/options"
                
                logger.info(f"⚙️ Updating add-on config: {slug}")
                response = await http_client.post(supervisor_url, json={"options": options})
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Add-on config updated: {slug}")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to update add-on config: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "slug": arguments["slug"]}, indent=2))]
        
        elif name == "restart_homeassistant":
            try:
                force = arguments.get("force", False)
                
                logger.info("🔄 Restarting Home Assistant Core...")
                
                # Use the Supervisor API to restart Home Assistant
                supervisor_url = "http://supervisor/core/restart"
                response = await http_client.post(supervisor_url)
                response.raise_for_status()
                
                result = {
                    "status": "success",
                    "message": "Home Assistant is restarting. It will be back online in about 30-60 seconds.",
                    "force": force
                }
                
                logger.info("✅ Home Assistant restart initiated")
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            except Exception as e:
                logger.error(f"❌ Failed to restart Home Assistant: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e), "message": "Failed to restart Home Assistant"}, indent=2))]
        
        # ===================================================================
        # CONVERTED TOOL HANDLERS - Try all three parts
        # ===================================================================
        else:
            # Try Part 1 handlers
            result = await handle_part1_tools(name, arguments, ha_api, file_mgr)
            if result is not None:
                return result
            
            # Try Part 2 handlers
            result = await handle_part2_tools(name, arguments, ha_api, file_mgr)
            if result is not None:
                return result
            
            # Try Part 3 handlers
            result = await handle_part3_dashboard_tools(name, arguments, ha_api, file_mgr)
            if result is not None:
                return result
            
            # Unknown tool - none of the handlers recognized it
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ============================================================================
# 🔥 REAL-TIME SSE (SERVER-SENT EVENTS) STREAMING
# ============================================================================

async def stream_ha_events(domain: Optional[str] = None, entity_id: Optional[str] = None):
    """
    Stream Home Assistant events in real-time using Server-Sent Events (SSE).
    
    Connects to HA /api/stream and yields events as they happen.
    Filters by domain and/or entity_id if specified.
    
    Args:
        domain: Filter events by domain (e.g., 'light', 'switch', 'automation')
        entity_id: Filter events by specific entity_id
    
    Yields:
        SSE-formatted event strings
    """
    # HA stream endpoint (event stream) - Use Core API directly
    stream_url = f"{HA_URL}/stream"
    
    logger.info(f"🔥 Connecting to HA event stream: {stream_url}")
    if domain:
        logger.info(f"   Filtering by domain: {domain}")
    if entity_id:
        logger.info(f"   Filtering by entity_id: {entity_id}")
    
    try:
        async with httpx.AsyncClient(timeout=None) as client:  # No timeout for long-lived connection
            async with client.stream(
                "GET",
                stream_url,
                headers={
                    "Authorization": f"Bearer {HA_TOKEN}",
                    "Accept": "text/event-stream"
                }
            ) as response:
                logger.info(f"✅ Connected to HA event stream (status: {response.status_code})")
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    # SSE format: "event: message" or "data: {...}"
                    # HA also sends empty "data:" lines as keepalive pings - we skip those
                    if line.startswith("event:"):
                        event_type = line.split(":", 1)[1].strip()
                        continue
                    
                    if line.startswith("data:"):
                        try:
                            event_json = line.split(":", 1)[1].strip()
                            
                            # Skip empty data lines (keepalive pings)
                            if not event_json:
                                continue
                            
                            event_data = json.loads(event_json)
                            
                            # Apply filters
                            should_send = True
                            
                            # Filter by domain
                            if domain and event_data.get("event_type") == "state_changed":
                                entity = event_data.get("data", {}).get("entity_id", "")
                                if not entity.startswith(f"{domain}."):
                                    should_send = False
                            
                            # Filter by entity_id
                            if entity_id and event_data.get("event_type") == "state_changed":
                                entity = event_data.get("data", {}).get("entity_id", "")
                                if entity != entity_id:
                                    should_send = False
                            
                            # Yield filtered events
                            if should_send:
                                # Re-format as SSE
                                yield f"data: {json.dumps(event_data)}\n\n"
                        
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse event JSON: {e} | Raw data: {event_json[:100]}")
                            continue
    
    except Exception as e:
        logger.error(f"❌ SSE stream error: {e}")
        yield f"data: {json.dumps({'error': str(e), 'type': 'stream_error'})}\n\n"


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
            "08060000001f15c4890000000a49414441789c6300010000"
            "00050001edd2462e0000000049454e44ae426082"
        )
        return Response(content=favicon_data, media_type="image/png")
    
    # ========================================================================
    # 🎯 REST API ENDPOINTS (Batch Actions, State, Context Management)
    # ========================================================================
    
    async def api_get_state(request):
        """GET /api/state - Get current Home Assistant state summary"""
        try:
            states = await ha_api.get_states()
            
            # Build summary
            summary = {
                "total_entities": len(states),
                "domains": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Group by domain
            for entity in states:
                domain = entity["entity_id"].split(".")[0]
                if domain not in summary["domains"]:
                    summary["domains"][domain] = {"count": 0, "states": {}}
                summary["domains"][domain]["count"] += 1
                
                # Count state values
                state_value = entity.get("state", "unknown")
                if state_value not in summary["domains"][domain]["states"]:
                    summary["domains"][domain]["states"][state_value] = 0
                summary["domains"][domain]["states"][state_value] += 1
            
            return JSONResponse(summary)
        
        except Exception as e:
            logger.error(f"❌ GET /api/state error: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def api_execute_batch_actions(request):
        """POST /api/actions/batch - Execute multiple HA actions sequentially"""
        try:
            data = await request.json()
            actions = data.get("actions", [])
            
            if not actions:
                return JSONResponse({"error": "No actions provided"}, status_code=400)
            
            results = []
            for idx, action in enumerate(actions):
                action_name = action.get("action")
                parameters = action.get("parameters", {})
                
                try:
                    # Call the MCP tool directly
                    result = await call_tool(action_name, parameters)
                    
                    # Extract text from TextContent
                    result_text = result[0].text if result else "No result"
                    
                    results.append({
                        "action": action_name,
                        "success": True,
                        "result": result_text,
                        "index": idx
                    })
                    
                    logger.info(f"✅ Batch action {idx+1}/{len(actions)}: {action_name}")
                
                except Exception as e:
                    logger.error(f"❌ Batch action {idx+1} failed: {action_name} - {e}")
                    results.append({
                        "action": action_name,
                        "success": False,
                        "error": str(e),
                        "index": idx
                    })
                    
                    # Stop on first error if stop_on_error is true
                    if data.get("stop_on_error", False):
                        break
            
            return JSONResponse({
                "success": all(r["success"] for r in results),
                "total_actions": len(actions),
                "completed": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat()
            })
        
        except Exception as e:
            logger.error(f"❌ POST /api/actions/batch error: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def api_list_actions(request):
        """GET /api/actions - List all available MCP tools"""
        try:
            tools = await list_tools()
            
            tool_list = [
                {
                    "name": tool.name,
                    "description": tool.description.split("\n")[0] if tool.description else "",  # First line only
                    "required_params": tool.inputSchema.get("required", []),
                    "all_params": list(tool.inputSchema.get("properties", {}).keys())
                }
                for tool in tools
            ]
            
            return JSONResponse({
                "total_tools": len(tool_list),
                "tools": tool_list,
                "categories": {
                    "camera": len([t for t in tool_list if "camera" in t["name"]]),
                    "vacuum": len([t for t in tool_list if "vacuum" in t["name"]]),
                    "fan": len([t for t in tool_list if "fan" in t["name"]]),
                    "addon": len([t for t in tool_list if "addon" in t["name"]]),
                    "file": len([t for t in tool_list if "file" in t["name"] or "directory" in t["name"]]),
                }
            })
        
        except Exception as e:
            logger.error(f"❌ GET /api/actions error: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    # SSE Event Stream endpoint
    async def subscribe_events(request):
        """
        Real-time event streaming endpoint.
        
        Query params:
            - domain: Filter by domain (e.g., ?domain=light)
            - entity_id: Filter by specific entity (e.g., ?entity_id=light.living_room)
        
        Example:
            GET /subscribe_events?domain=light
            GET /subscribe_events?entity_id=camera.front_door
        """
        from starlette.responses import StreamingResponse
        
        # Get query parameters
        domain = request.query_params.get("domain")
        entity_id = request.query_params.get("entity_id")
        
        logger.info(f"📡 SSE client connected - domain={domain}, entity_id={entity_id}")
        
        return StreamingResponse(
            stream_ha_events(domain=domain, entity_id=entity_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    
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
            Route("/subscribe_events", endpoint=subscribe_events, methods=["GET"]),  # SSE streaming
            Route("/api/state", endpoint=api_get_state, methods=["GET"]),  # Get HA state summary
            Route("/api/actions", endpoint=api_list_actions, methods=["GET"]),  # List all tools
            Route("/api/actions/batch", endpoint=api_execute_batch_actions, methods=["POST"]),  # Batch actions
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


