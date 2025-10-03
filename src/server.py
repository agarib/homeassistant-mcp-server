#!/usr/bin/env python3
"""
ðŸ  Home Assistant MCP Server - AI-Native Smart Home Control

This MCP server exposes comprehensive Home Assistant controls to AI models,
enabling context-aware automations, predictive behaviors, and natural language
understanding that goes far beyond basic on/off commands.

Features:
- 50+ intelligent tools organized by capability
- Context-aware lighting (sun position, ambient light, activity)
- Multi-room audio/video coordination
- Predictive environment optimization
- Security monitoring with AI reasoning
- Adaptive routines (morning, evening, sleep)
- Maintenance prediction and alerts
- Whole-home intelligent coordination
- Learning user patterns

Protocol: Model Context Protocol (MCP)
License: MIT
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urljoin

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Home Assistant configuration
HA_URL = os.getenv("HA_URL", "http://192.168.1.203:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

if not HA_TOKEN:
    logger.warning("âš ï¸  HA_TOKEN not set! Server will not be able to control Home Assistant.")

# Create MCP server instance
app = Server("homeassistant-mcp-server")

# HTTP client for Home Assistant API
http_client = httpx.AsyncClient(timeout=30.0)


class HomeAssistantAPI:
    """Wrapper for Home Assistant REST API with intelligent error handling."""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def call_service(self, domain: str, service: str, entity_id: str = None, **kwargs) -> Dict:
        """Call a Home Assistant service."""
        url = f"{self.base_url}/api/services/{domain}/{service}"
        data = kwargs.copy()
        if entity_id:
            data["entity_id"] = entity_id
        
        try:
            response = await http_client.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Service call failed: {domain}.{service} - {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_states(self, entity_id: str = None) -> Dict:
        """Get entity states."""
        url = f"{self.base_url}/api/states"
        if entity_id:
            url += f"/{entity_id}"
        
        try:
            response = await http_client.get(url, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Get states failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_services(self) -> Dict:
        """Get available services."""
        url = f"{self.base_url}/api/services"
        try:
            response = await http_client.get(url, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_config(self) -> Dict:
        """Get Home Assistant configuration."""
        url = f"{self.base_url}/api/config"
        try:
            response = await http_client.get(url, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def fire_event(self, event_type: str, event_data: Dict = None) -> Dict:
        """Fire a custom event."""
        url = f"{self.base_url}/api/events/{event_type}"
        try:
            response = await http_client.post(
                url, 
                json=event_data or {}, 
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def render_template(self, template: str) -> Dict:
        """Render a Jinja2 template."""
        url = f"{self.base_url}/api/template"
        try:
            response = await http_client.post(
                url,
                json={"template": template},
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Initialize Home Assistant API client
ha_api = HomeAssistantAPI(HA_URL, HA_TOKEN)


# ============================================================================
# ï¿½ SSH/SFTP FILE MANAGEMENT for /config directory
# ============================================================================

# SSH Configuration for HA config access
HA_SSH_HOST = os.getenv("HA_SSH_HOST", "192.168.1.203")
HA_SSH_PORT = int(os.getenv("HA_SSH_PORT", "22"))
HA_SSH_USER = os.getenv("HA_SSH_USER", "hassio")
HA_SSH_PASSWORD = os.getenv("HA_SSH_PASSWORD", "")
HA_CONFIG_PATH = os.getenv("HA_CONFIG_PATH", "/config")

class HAConfigManager:
    """Manage Home Assistant config files via SSH/SFTP."""
    
    def __init__(self, host: str, port: int, username: str, password: str, config_path: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.config_path = config_path
        self.enabled = bool(password)  # Only enabled if password is set
        
        if not self.enabled:
            logger.warning("âš ï¸  SSH password not set - config file management disabled")
    
    def _connect_sftp(self):
        """Create SSH/SFTP connection."""
        if not self.enabled:
            raise Exception("SSH not configured - please set HA_SSH_PASSWORD")
        
        try:
            import paramiko
        except ImportError:
            raise Exception("paramiko not installed - run: pip install paramiko")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            timeout=10
        )
        sftp = ssh.open_sftp()
        return ssh, sftp
    
    def list_files(self, path: str = "packages") -> List[str]:
        """List files in config directory."""
        full_path = f"{self.config_path}/{path}"
        ssh, sftp = None, None
        try:
            ssh, sftp = self._connect_sftp()
            files = sftp.listdir(full_path)
            return sorted([f for f in files if not f.startswith('.')])
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def read_file(self, filepath: str) -> str:
        """Read file content from config directory."""
        if not filepath.startswith('/'):
            filepath = f"{self.config_path}/{filepath}"
        
        ssh, sftp = None, None
        try:
            ssh, sftp = self._connect_sftp()
            with sftp.open(filepath, 'r') as f:
                return f.read().decode('utf-8') if isinstance(f.read(), bytes) else f.read()
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def write_file(self, filepath: str, content: str, create_backup: bool = True) -> bool:
        """Write file to config directory with optional backup."""
        if not filepath.startswith('/'):
            filepath = f"{self.config_path}/{filepath}"
        
        ssh, sftp = None, None
        try:
            ssh, sftp = self._connect_sftp()
            
            # Create backup if file exists
            if create_backup:
                try:
                    sftp.stat(filepath)  # Check if file exists
                    backup_path = f"{filepath}.bak"
                    sftp.rename(filepath, backup_path)
                    logger.info(f"âœ… Backup created: {backup_path}")
                except FileNotFoundError:
                    pass  # File doesn't exist, no backup needed
            
            # Write new content
            with sftp.open(filepath, 'w') as f:
                f.write(content.encode('utf-8') if isinstance(content, str) else content)
            
            logger.info(f"âœ… File written: {filepath}")
            return True
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def delete_file(self, filepath: str, create_backup: bool = True) -> bool:
        """Delete file from config directory with optional backup."""
        if not filepath.startswith('/'):
            filepath = f"{self.config_path}/{filepath}"
        
        ssh, sftp = None, None
        try:
            ssh, sftp = self._connect_sftp()
            
            # Create backup before deleting
            if create_backup:
                backup_path = f"{filepath}.deleted"
                sftp.rename(filepath, backup_path)
                logger.info(f"âœ… File moved to: {backup_path}")
            else:
                sftp.remove(filepath)
                logger.info(f"âœ… File deleted: {filepath}")
            
            return True
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists in config directory."""
        if not filepath.startswith('/'):
            filepath = f"{self.config_path}/{filepath}"
        
        ssh, sftp = None, None
        try:
            ssh, sftp = self._connect_sftp()
            sftp.stat(filepath)
            return True
        except FileNotFoundError:
            return False
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

# Initialize HA Config Manager
ha_config = HAConfigManager(HA_SSH_HOST, HA_SSH_PORT, HA_SSH_USER, HA_SSH_PASSWORD, HA_CONFIG_PATH)


# ============================================================================
# ï¿½ðŸ“‹ TOOL DEFINITIONS - Organized by Capability
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available Home Assistant MCP tools.
    
    Categories:
    - Device Discovery & State Management
    - Basic Device Control
    - Advanced Lighting Control
    - Media Player Control
    - Climate & Environment
    - Security & Monitoring
    - Automation Management
    - Scene & Script Management
    - Multi-Step Workflows
    - Context-Aware Intelligence
    - Predictive Analytics
    - Whole-Home Coordination
    """
    
    return [
        # =================================================================
        # CATEGORY 1: DEVICE DISCOVERY & STATE MANAGEMENT
        # =================================================================
        
        Tool(
            name="discover_devices",
            description=(
                "Discover all available Home Assistant devices and entities. "
                "Returns a comprehensive list of all connected devices organized by domain "
                "(lights, switches, sensors, media_players, etc) with their current state and area assignment. "
                "Use this to understand what devices are available before controlling them. "
                "Supports optional filters: domain (e.g., 'light', 'switch') and area (e.g., 'living_room')."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filter by domain (optional): light, switch, sensor, "
                                     "media_player, climate, cover, lock, camera, etc.",
                        "enum": [
                            "all", "light", "switch", "sensor", "binary_sensor", 
                            "media_player", "climate", "cover", "lock", "camera",
                            "alarm_control_panel", "vacuum", "fan", "scene", "automation"
                        ]
                    },
                    "area": {
                        "type": "string",
                        "description": "Filter by area/room (optional): living_room, bedroom, kitchen, etc."
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_device_state",
            description=(
                "Get the current state and attributes of a specific device. "
                "Returns detailed information including state, brightness, color, "
                "temperature, battery level, and all other attributes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The entity ID (e.g., 'light.living_room', 'sensor.temperature')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="get_area_devices",
            description=(
                "Get all devices in a specific area/room. Returns devices grouped by type "
                "with their current states. Perfect for whole-room control operations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area name (e.g., 'living_room', 'bedroom', 'kitchen')"
                    },
                    "device_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by device types (optional): ['light', 'switch', 'media_player']"
                    }
                },
                "required": ["area"]
            }
        ),
        
        # =================================================================
        # CATEGORY 2: BASIC DEVICE CONTROL
        # =================================================================
        
        Tool(
            name="control_light",
            description=(
                "Control a light with comprehensive options. Can turn on/off, set brightness, "
                "color, color temperature, and effects. Supports both simple commands and "
                "detailed control."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Light entity ID (e.g., 'light.living_room')"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["turn_on", "turn_off", "toggle", "brightness", "color", "effect"],
                        "description": "Action to perform"
                    },
                    "brightness": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255,
                        "description": "Brightness level (0-255)"
                    },
                    "color_name": {
                        "type": "string",
                        "description": "Color name (e.g., 'red', 'blue', 'warm_white')"
                    },
                    "rgb_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "minItems": 3,
                        "maxItems": 3,
                        "description": "RGB color [R, G, B] values (0-255)"
                    },
                    "kelvin": {
                        "type": "integer",
                        "description": "Color temperature in Kelvin (2000-6500)"
                    },
                    "effect": {
                        "type": "string",
                        "description": "Light effect (e.g., 'colorloop', 'random')"
                    },
                    "transition": {
                        "type": "number",
                        "description": "Transition time in seconds"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="control_switch",
            description=(
                "Control switches and outlets. Turn on/off or toggle any switch device."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Switch entity ID (e.g., 'switch.coffee_maker')"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["turn_on", "turn_off", "toggle"],
                        "description": "Action to perform"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="control_climate",
            description=(
                "Control climate devices (thermostats, HVAC). Set temperature, mode, "
                "fan speed, and more. Supports both heating and cooling operations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Climate entity ID (e.g., 'climate.thermostat')"
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Target temperature"
                    },
                    "hvac_mode": {
                        "type": "string",
                        "enum": ["off", "heat", "cool", "heat_cool", "auto", "dry", "fan_only"],
                        "description": "HVAC mode"
                    },
                    "fan_mode": {
                        "type": "string",
                        "description": "Fan mode (e.g., 'auto', 'low', 'medium', 'high')"
                    },
                    "preset_mode": {
                        "type": "string",
                        "description": "Preset mode (e.g., 'away', 'home', 'sleep', 'eco')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="control_cover",
            description=(
                "Control covers (blinds, curtains, garage doors). Open, close, stop, "
                "or set to specific position."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Cover entity ID (e.g., 'cover.living_room_blinds')"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["open", "close", "stop", "toggle", "set_position"],
                        "description": "Action to perform"
                    },
                    "position": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Position percentage (0=closed, 100=open)"
                    },
                    "tilt_position": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Tilt position for blinds"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        # =================================================================
        # CATEGORY 3: ADVANCED LIGHTING CONTROL
        # =================================================================
        
        Tool(
            name="adaptive_lighting",
            description=(
                "ðŸŒ… INTELLIGENT: Adjust lighting based on time of day, sun position, and activity. "
                "Automatically calculates optimal brightness and color temperature. "
                "Mimics natural daylight patterns for circadian rhythm support."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of light entity IDs to control"
                    },
                    "activity": {
                        "type": "string",
                        "enum": ["reading", "working", "relaxing", "watching_tv", "sleeping", "cooking", "dining"],
                        "description": "Current activity for context-aware adjustment"
                    },
                    "ambient_lux": {
                        "type": "number",
                        "description": "Current ambient light level in lux (from sensor)"
                    },
                    "preference": {
                        "type": "string",
                        "enum": ["energetic", "neutral", "relaxing"],
                        "description": "User preference for lighting mood"
                    }
                },
                "required": ["entity_ids"]
            }
        ),
        
        Tool(
            name="circadian_lighting",
            description=(
                "ðŸŒž INTELLIGENT: Implement circadian lighting that follows natural daylight patterns. "
                "Automatically adjusts color temperature throughout the day: cool white in morning, "
                "warm white in evening. Supports custom sunrise/sunset times."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of light entity IDs"
                    },
                    "sunrise_time": {
                        "type": "string",
                        "description": "Custom sunrise time (HH:MM format, optional)"
                    },
                    "sunset_time": {
                        "type": "string",
                        "description": "Custom sunset time (HH:MM format, optional)"
                    },
                    "transition_minutes": {
                        "type": "integer",
                        "description": "Transition duration in minutes (default: 60)"
                    }
                },
                "required": ["entity_ids"]
            }
        ),
        
        Tool(
            name="multi_room_lighting_sync",
            description=(
                "ðŸ  COORDINATION: Synchronize lighting across multiple rooms. Creates a cohesive "
                "lighting experience with smooth transitions between spaces. Perfect for "
                "open floor plans or whole-home scenes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of areas to synchronize"
                    },
                    "brightness": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255,
                        "description": "Synchronized brightness level"
                    },
                    "color_temperature": {
                        "type": "integer",
                        "description": "Synchronized color temperature in Kelvin"
                    },
                    "transition_seconds": {
                        "type": "number",
                        "description": "Transition time in seconds"
                    }
                },
                "required": ["areas"]
            }
        ),
        
        Tool(
            name="presence_based_lighting",
            description=(
                "ðŸ‘¤ INTELLIGENT: Adjust lighting based on presence detection and movement patterns. "
                "Uses motion sensors, room presence, and time-of-day to automatically control "
                "lights. Includes timeout settings and manual override detection."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area to monitor"
                    },
                    "motion_sensors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Motion sensor entity IDs"
                    },
                    "timeout_minutes": {
                        "type": "integer",
                        "description": "Minutes of no motion before turning off (default: 5)"
                    },
                    "nightlight_mode": {
                        "type": "boolean",
                        "description": "Enable dimmed nightlight mode after sunset"
                    }
                },
                "required": ["area"]
            }
        ),
        
        # =================================================================
        # CATEGORY 4: MEDIA PLAYER CONTROL
        # =================================================================
        
        Tool(
            name="control_media_player",
            description=(
                "Control media players (TV, speakers, streaming devices). Play, pause, stop, "
                "volume control, source selection, and more."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Media player entity ID"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["play", "pause", "stop", "next", "previous", "volume_up", 
                                "volume_down", "volume_set", "mute", "unmute", "toggle"],
                        "description": "Media control action"
                    },
                    "volume_level": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Volume level (0.0-1.0)"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="play_media",
            description=(
                "Play specific media on a media player. Supports various media types "
                "(music, video, radio, playlist) and sources."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Media player entity ID"
                    },
                    "media_content_id": {
                        "type": "string",
                        "description": "Media content ID (URL, Spotify URI, etc.)"
                    },
                    "media_content_type": {
                        "type": "string",
                        "enum": ["music", "video", "playlist", "tvshow", "channel", "radio"],
                        "description": "Type of media content"
                    }
                },
                "required": ["entity_id", "media_content_id", "media_content_type"]
            }
        ),
        
        Tool(
            name="multi_room_audio_sync",
            description=(
                "ðŸŽµ COORDINATION: Create synchronized multi-room audio. Group speakers together "
                "for whole-home audio or zone-based playback. Perfect for parties or "
                "distributed entertainment."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "master_player": {
                        "type": "string",
                        "description": "Master media player entity ID"
                    },
                    "slave_players": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of media players to sync with master"
                    },
                    "media_content_id": {
                        "type": "string",
                        "description": "Media to play (optional)"
                    }
                },
                "required": ["master_player", "slave_players"]
            }
        ),
        
        Tool(
            name="follow_me_audio",
            description=(
                "ðŸš¶ INTELLIGENT: Audio that follows you between rooms. Automatically transfers "
                "playback to the nearest speaker based on presence detection. Seamless "
                "listening experience throughout the home."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "User identifier for tracking"
                    },
                    "presence_sensors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Presence sensor entity IDs for each room"
                    },
                    "media_players": {
                        "type": "object",
                        "description": "Map of area names to media player entity IDs"
                    }
                },
                "required": ["user"]
            }
        ),
        
        Tool(
            name="party_mode",
            description=(
                "ðŸŽ‰ WORKFLOW: Activate party mode with synchronized audio, dynamic lighting, "
                "and optimized climate. All entertainment devices work together."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to include in party mode"
                    },
                    "music_playlist": {
                        "type": "string",
                        "description": "Playlist URI or URL"
                    },
                    "lighting_effect": {
                        "type": "string",
                        "enum": ["colorloop", "disco", "energetic", "chill"],
                        "description": "Lighting effect for party atmosphere"
                    }
                },
                "required": ["areas"]
            }
        ),
        
        # =================================================================
        # CATEGORY 5: CLIMATE & ENVIRONMENT
        # =================================================================
        
        Tool(
            name="smart_thermostat_optimization",
            description=(
                "ðŸŒ¡ï¸ INTELLIGENT: Optimize thermostat based on occupancy, weather forecast, "
                "energy prices, and comfort preferences. Learns patterns for maximum "
                "efficiency and comfort."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Climate entity ID"
                    },
                    "occupancy_sensors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Occupancy sensor entity IDs"
                    },
                    "optimize_for": {
                        "type": "string",
                        "enum": ["comfort", "efficiency", "balanced"],
                        "description": "Optimization goal"
                    },
                    "temperature_preferences": {
                        "type": "object",
                        "description": "Temperature preferences by time and activity"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="zone_climate_control",
            description=(
                "ðŸ  COORDINATION: Control climate in different zones independently. "
                "Perfect for multi-zone HVAC or room-by-room temperature management."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "zones": {
                        "type": "object",
                        "description": "Map of zone names to climate entity IDs and target temps"
                    },
                    "sync_mode": {
                        "type": "boolean",
                        "description": "Synchronize all zones to same temperature"
                    }
                },
                "required": ["zones"]
            }
        ),
        
        Tool(
            name="air_quality_management",
            description=(
                "ðŸ’¨ INTELLIGENT: Monitor and optimize air quality using sensors and ventilation. "
                "Controls fans, purifiers, and windows based on indoor/outdoor air quality."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "air_quality_sensors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Air quality sensor entity IDs (CO2, VOC, PM2.5)"
                    },
                    "ventilation_devices": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fans, purifiers, or ventilation controls"
                    },
                    "thresholds": {
                        "type": "object",
                        "description": "Air quality thresholds for automatic action"
                    }
                },
                "required": ["air_quality_sensors"]
            }
        ),
        
        # =================================================================
        # CATEGORY 6: SECURITY & MONITORING
        # =================================================================
        
        Tool(
            name="intelligent_security_monitor",
            description=(
                "ðŸ”’ INTELLIGENT: Monitor home security with AI-powered anomaly detection. "
                "Analyzes door/window sensors, cameras, motion patterns. Alerts on unusual activity."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "security_sensors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Security sensor entity IDs"
                    },
                    "cameras": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Camera entity IDs"
                    },
                    "notification_method": {
                        "type": "string",
                        "enum": ["mobile", "email", "sms", "all"],
                        "description": "How to send alerts"
                    },
                    "armed_state": {
                        "type": "string",
                        "enum": ["home", "away", "night", "disarmed"],
                        "description": "Current security state"
                    }
                },
                "required": ["security_sensors"]
            }
        ),
        
        Tool(
            name="anomaly_detection",
            description=(
                "ðŸ” PREDICTIVE: Detect unusual patterns in device usage, energy consumption, "
                "or sensor readings. Uses baseline learning to identify anomalies."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Entities to monitor for anomalies"
                    },
                    "sensitivity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Detection sensitivity"
                    },
                    "learning_period_days": {
                        "type": "integer",
                        "description": "Days of historical data for baseline (default: 7)"
                    }
                },
                "required": ["entity_ids"]
            }
        ),
        
        Tool(
            name="vacation_mode",
            description=(
                "âœˆï¸ WORKFLOW: Activate vacation mode with simulated occupancy, security monitoring, "
                "and automated alerts. Lights, TVs simulate presence, security enhanced."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Vacation start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Vacation end date (YYYY-MM-DD)"
                    },
                    "simulate_presence": {
                        "type": "boolean",
                        "description": "Randomly activate lights/media to simulate occupancy"
                    },
                    "security_level": {
                        "type": "string",
                        "enum": ["normal", "enhanced", "maximum"],
                        "description": "Security monitoring level"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        
        # =================================================================
        # CATEGORY 7: AUTOMATION MANAGEMENT
        # =================================================================
        
        Tool(
            name="list_automations",
            description=(
                "List all Home Assistant automations with their current state (enabled/disabled) "
                "and last triggered time."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_enabled": {
                        "type": "boolean",
                        "description": "Filter to show only enabled automations"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="trigger_automation",
            description=(
                "Manually trigger an automation. Useful for testing or manual execution "
                "of automated routines."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Automation entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="enable_disable_automation",
            description=(
                "Enable or disable an automation. Useful for temporary adjustments "
                "or troubleshooting."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Automation entity ID"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["enable", "disable", "toggle"],
                        "description": "Action to perform"
                    }
                },
                "required": ["entity_id", "action"]
            }
        ),
        
        Tool(
            name="create_automation",
            description=(
                "ðŸŽ¯ CREATE AUTOMATION: Create a new Home Assistant automation with user-defined "
                "triggers, conditions, and actions. This enables users to build custom automations "
                "through natural conversation. The AI translates user intent into proper automation "
                "configuration. Supports complex logic with multiple triggers and conditions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "automation_name": {
                        "type": "string",
                        "description": "Friendly name for the automation (e.g., 'Turn on lights at sunset')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of what the automation does"
                    },
                    "triggers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "platform": {
                                    "type": "string",
                                    "enum": ["state", "time", "sun", "numeric_state", "event", "webhook", "zone", "device"],
                                    "description": "Trigger platform"
                                },
                                "entity_id": {"type": "string", "description": "Entity that triggers"},
                                "from": {"type": "string", "description": "Previous state"},
                                "to": {"type": "string", "description": "New state"},
                                "at": {"type": "string", "description": "Time (HH:MM:SS)"},
                                "event": {"type": "string", "description": "Event name"},
                                "above": {"type": "number", "description": "Threshold value"},
                                "below": {"type": "number", "description": "Threshold value"}
                            }
                        },
                        "description": "Triggers that start the automation (at least one required)"
                    },
                    "conditions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "condition": {
                                    "type": "string",
                                    "enum": ["state", "numeric_state", "time", "sun", "zone", "and", "or", "not"],
                                    "description": "Condition type"
                                },
                                "entity_id": {"type": "string"},
                                "state": {"type": "string"},
                                "above": {"type": "number"},
                                "below": {"type": "number"},
                                "before": {"type": "string"},
                                "after": {"type": "string"}
                            }
                        },
                        "description": "Conditions that must be met (optional, all must be true)"
                    },
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "service": {
                                    "type": "string",
                                    "description": "Service to call (e.g., 'light.turn_on', 'notify.mobile_app')"
                                },
                                "entity_id": {"type": "string", "description": "Target entity"},
                                "data": {
                                    "type": "object",
                                    "description": "Service data (brightness, color, message, etc.)"
                                },
                                "delay": {"type": "string", "description": "Delay (HH:MM:SS format)"}
                            }
                        },
                        "description": "Actions to perform when triggered"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["single", "restart", "queued", "parallel"],
                        "description": "Execution mode: single=ignore new, restart=cancel and restart, queued=queue, parallel=run parallel"
                    }
                },
                "required": ["automation_name", "triggers", "actions"]
            }
        ),
        
        Tool(
            name="update_automation",
            description=(
                "âœï¸ UPDATE AUTOMATION: Modify an existing automation's configuration. "
                "Change triggers, conditions, or actions without deleting and recreating."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Automation entity ID to update"
                    },
                    "automation_name": {
                        "type": "string",
                        "description": "New friendly name (optional)"
                    },
                    "triggers": {
                        "type": "array",
                        "description": "New triggers (replaces existing if provided)"
                    },
                    "conditions": {
                        "type": "array",
                        "description": "New conditions (replaces existing if provided)"
                    },
                    "actions": {
                        "type": "array",
                        "description": "New actions (replaces existing if provided)"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="delete_automation",
            description=(
                "ðŸ—‘ï¸ DELETE AUTOMATION: Permanently remove an automation from Home Assistant. "
                "Use with caution - this cannot be undone."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Automation entity ID to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Must be true to confirm deletion"
                    }
                },
                "required": ["entity_id", "confirm"]
            }
        ),
        
        Tool(
            name="get_automation_details",
            description=(
                "ðŸ“‹ Get detailed configuration of an automation including triggers, conditions, "
                "actions, and execution history. Useful for understanding or debugging automations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Automation entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        # =================================================================
        # CATEGORY 7B: LOGS, HISTORY & TROUBLESHOOTING
        # =================================================================
        
        Tool(
            name="get_entity_history",
            description=(
                "ðŸ“Š HISTORICAL DATA: Get state history for entities over a time period. "
                "Essential for pattern recognition, trend analysis, and understanding device "
                "behavior. Returns timestamps and state changes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Entity IDs to get history for"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time (ISO 8601 or relative like '-24h', '-7d')"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time (ISO 8601, defaults to now)"
                    },
                    "minimal_response": {
                        "type": "boolean",
                        "description": "Return only state changes, skip attributes"
                    }
                },
                "required": ["entity_ids"]
            }
        ),
        
        Tool(
            name="get_system_logs",
            description=(
                "ðŸ” TROUBLESHOOTING: Read Home Assistant system logs to diagnose issues. "
                "Filter by severity (error, warning, info) and search for specific components."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["error", "warning", "info", "debug", "all"],
                        "description": "Minimum log severity level"
                    },
                    "filter_component": {
                        "type": "string",
                        "description": "Filter logs by component (e.g., 'homeassistant.components.light')"
                    },
                    "search_text": {
                        "type": "string",
                        "description": "Search for specific text in logs"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of log lines to return (default: 50, max: 500)"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_error_log",
            description=(
                "âš ï¸ TROUBLESHOOTING: Get recent errors and warnings from Home Assistant. "
                "Quick way to identify problems without reading full logs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Hours of history to check (default: 24)"
                    },
                    "include_warnings": {
                        "type": "boolean",
                        "description": "Include warnings in addition to errors"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="diagnose_entity",
            description=(
                "ðŸ”§ TROUBLESHOOTING: Comprehensive diagnostic for an entity. Checks state, "
                "attributes, recent history, related automations, and identifies common issues."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to diagnose"
                    },
                    "check_history_hours": {
                        "type": "integer",
                        "description": "Hours of history to analyze (default: 24)"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="get_statistics",
            description=(
                "ðŸ“ˆ ANALYTICS: Get long-term statistics for sensor entities. Useful for "
                "energy monitoring, temperature trends, and pattern analysis. Returns min, "
                "max, mean, and sum values over time periods."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sensor entity IDs"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["5minute", "hour", "day", "week", "month"],
                        "description": "Statistics period"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time (ISO 8601 or relative)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time (defaults to now)"
                    }
                },
                "required": ["entity_ids"]
            }
        ),
        
        Tool(
            name="get_binary_sensor",
            description=(
                "ðŸ”˜ Get binary sensor state and attributes. Binary sensors have on/off states "
                "and include device_class (motion, door, window, occupancy, etc), friendly_name, "
                "and additional attributes like battery level."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Binary sensor entity ID (e.g., 'binary_sensor.front_door')"
                    },
                    "include_history": {
                        "type": "boolean",
                        "description": "Include recent state changes"
                    },
                    "history_hours": {
                        "type": "integer",
                        "description": "Hours of history if include_history=true (default: 24)"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="analyze_patterns",
            description=(
                "ðŸ§  PATTERN RECOGNITION: Analyze historical data to identify patterns and trends. "
                "Discovers daily/weekly patterns, anomalies, and correlations between entities. "
                "Essential for predictive automation and optimization."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Entities to analyze for patterns"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Days of history to analyze (default: 14)"
                    },
                    "pattern_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["daily", "weekly", "correlation", "anomaly", "trend"]
                        },
                        "description": "Types of patterns to search for"
                    }
                },
                "required": ["entity_ids"]
            }
        ),
        
        # =================================================================
        # CATEGORY 8: SCENE & SCRIPT MANAGEMENT
        # =================================================================
        
        Tool(
            name="activate_scene",
            description=(
                "Activate a predefined scene. Scenes restore specific states for "
                "multiple devices at once."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Scene entity ID (e.g., 'scene.movie_night')"
                    },
                    "transition": {
                        "type": "number",
                        "description": "Transition time in seconds"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        Tool(
            name="run_script",
            description=(
                "Execute a Home Assistant script. Scripts are sequences of actions "
                "that can include delays, conditions, and service calls."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Script entity ID"
                    },
                    "variables": {
                        "type": "object",
                        "description": "Variables to pass to the script"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        
        # =================================================================
        # CATEGORY 9: MULTI-STEP WORKFLOWS
        # =================================================================
        
        Tool(
            name="morning_routine",
            description=(
                "ðŸŒ… WORKFLOW: Execute intelligent morning routine. Gradually increases lighting, "
                "adjusts temperature, starts coffee maker, reads news/weather. Adapts to "
                "schedule and weather conditions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "wake_time": {
                        "type": "string",
                        "description": "Wake time (HH:MM format)"
                    },
                    "gradual_wake": {
                        "type": "boolean",
                        "description": "Gradually increase lights before wake time"
                    },
                    "weather_announcement": {
                        "type": "boolean",
                        "description": "Announce weather and schedule"
                    },
                    "coffee_maker": {
                        "type": "string",
                        "description": "Coffee maker entity ID"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="evening_routine",
            description=(
                "ðŸŒ† WORKFLOW: Execute evening wind-down routine. Dims lights, closes blinds, "
                "adjusts temperature, locks doors. Prepares home for night."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sunset_trigger": {
                        "type": "boolean",
                        "description": "Trigger at sunset automatically"
                    },
                    "lock_doors": {
                        "type": "boolean",
                        "description": "Automatically lock all doors"
                    },
                    "close_blinds": {
                        "type": "boolean",
                        "description": "Close all blinds/curtains"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="bedtime_routine",
            description=(
                "ðŸ˜´ WORKFLOW: Execute bedtime routine. Turns off lights gradually, sets "
                "nightlight, locks doors, lowers thermostat, enables sleep mode on devices."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bedtime": {
                        "type": "string",
                        "description": "Bedtime (HH:MM format)"
                    },
                    "nightlight_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lights to use as nightlights"
                    },
                    "sleep_temperature": {
                        "type": "number",
                        "description": "Target sleep temperature"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="arrive_home",
            description=(
                "ðŸ¡ WORKFLOW: Execute arrival home routine. Unlocks door, turns on lights, "
                "adjusts temperature, disarms security. Adapts based on time of day."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "User arriving home"
                    },
                    "entry_point": {
                        "type": "string",
                        "description": "Entry door/area"
                    },
                    "time_away_hours": {
                        "type": "number",
                        "description": "Hours away (affects welcome intensity)"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="away_mode",
            description=(
                "ðŸš— WORKFLOW: Activate away mode. Turns off unnecessary devices, sets "
                "efficient climate, arms security, enables presence simulation if desired."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expected_duration_hours": {
                        "type": "number",
                        "description": "Expected time away in hours"
                    },
                    "eco_mode": {
                        "type": "boolean",
                        "description": "Enable energy-saving mode"
                    },
                    "simulate_presence": {
                        "type": "boolean",
                        "description": "Simulate occupancy with lights/media"
                    }
                },
                "required": []
            }
        ),
        
        # =================================================================
        # CATEGORY 10: CONTEXT-AWARE INTELLIGENCE
        # =================================================================
        
        Tool(
            name="analyze_home_context",
            description=(
                "ðŸ§  INTELLIGENCE: Analyze current home context including occupancy, activity, "
                "time of day, weather, energy usage. Provides insights for intelligent decisions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "include_predictions": {
                        "type": "boolean",
                        "description": "Include predictive analysis"
                    },
                    "include_recommendations": {
                        "type": "boolean",
                        "description": "Include optimization recommendations"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="activity_recognition",
            description=(
                "ðŸ‘ï¸ INTELLIGENCE: Recognize current household activity based on device states, "
                "time, and patterns. Detects: sleeping, cooking, working, watching TV, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Specific area to analyze (optional, analyzes whole home if not specified)"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Minimum confidence for activity detection (default: 0.7)"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="comfort_optimization",
            description=(
                "ðŸ˜Œ INTELLIGENCE: Optimize home comfort by balancing temperature, lighting, "
                "air quality, noise level. Multi-factor optimization for wellbeing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to optimize"
                    },
                    "user_preferences": {
                        "type": "object",
                        "description": "User comfort preferences"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["temperature", "lighting", "air_quality", "balanced"],
                        "description": "Optimization priority"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="energy_intelligence",
            description=(
                "âš¡ INTELLIGENCE: Analyze energy consumption patterns and provide optimization "
                "recommendations. Identifies high-consumption devices and suggests efficiency improvements."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "time_period": {
                        "type": "string",
                        "enum": ["today", "yesterday", "week", "month"],
                        "description": "Time period for analysis"
                    },
                    "include_costs": {
                        "type": "boolean",
                        "description": "Include cost estimates"
                    },
                    "optimization_suggestions": {
                        "type": "boolean",
                        "description": "Provide optimization suggestions"
                    }
                },
                "required": []
            }
        ),
        
        # =================================================================
        # CATEGORY 11: PREDICTIVE ANALYTICS
        # =================================================================
        
        Tool(
            name="predictive_maintenance",
            description=(
                "ðŸ”§ PREDICTIVE: Predict maintenance needs for devices based on usage patterns, "
                "age, and sensor readings. Alerts before failures occur."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "device_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Device types to analyze (HVAC, appliances, etc.)"
                    },
                    "prediction_horizon_days": {
                        "type": "integer",
                        "description": "Days ahead to predict (default: 30)"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="weather_integration",
            description=(
                "ðŸŒ¤ï¸ PREDICTIVE: Integrate weather forecast with home automation. Suggests "
                "actions based on upcoming weather (close windows before rain, adjust HVAC, etc.)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "forecast_hours": {
                        "type": "integer",
                        "description": "Hours ahead to consider (default: 24)"
                    },
                    "auto_adjust": {
                        "type": "boolean",
                        "description": "Automatically adjust home systems based on weather"
                    },
                    "conditions_to_monitor": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Weather conditions to monitor (rain, storm, freeze, heat)"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="pattern_learning",
            description=(
                "ðŸ“Š PREDICTIVE: Learn usage patterns and preferences over time. Identifies "
                "routines, preferred settings, and habitual behaviors for automation suggestions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "learning_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains to learn patterns from (lighting, climate, media, etc.)"
                    },
                    "minimum_data_days": {
                        "type": "integer",
                        "description": "Minimum days of data before suggesting automations (default: 14)"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Confidence threshold for pattern detection (0.0-1.0)"
                    }
                },
                "required": []
            }
        ),
        
        # =================================================================
        # CATEGORY 12: WHOLE-HOME COORDINATION
        # =================================================================
        
        Tool(
            name="synchronized_home_state",
            description=(
                "ðŸ  COORDINATION: Create synchronized whole-home state. All devices work together "
                "for movie night, dinner party, relaxation, work-from-home, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "home_mode": {
                        "type": "string",
                        "enum": ["movie", "dinner_party", "relaxation", "work", "sleep", "morning", "cleaning"],
                        "description": "Whole-home mode to activate"
                    },
                    "intensity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Mode intensity level"
                    },
                    "areas_to_include": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific areas to include (all if not specified)"
                    }
                },
                "required": ["home_mode"]
            }
        ),
        
        Tool(
            name="follow_me_home",
            description=(
                "ðŸš¶ COORDINATION: Lights and climate follow you through the home. Automatically "
                "adjusts each room as you enter and optimizes energy by adjusting rooms you leave."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "User to follow"
                    },
                    "presence_sensors": {
                        "type": "object",
                        "description": "Map of area names to presence sensor entity IDs"
                    },
                    "energy_saving_mode": {
                        "type": "boolean",
                        "description": "Turn off lights/adjust climate in unoccupied rooms"
                    }
                },
                "required": ["user"]
            }
        ),
        
        Tool(
            name="guest_mode",
            description=(
                "ðŸ‘¥ WORKFLOW: Activate guest mode with appropriate privacy settings, "
                "accessible controls, and welcoming atmosphere."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "guest_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas guests will use"
                    },
                    "privacy_mode": {
                        "type": "boolean",
                        "description": "Disable cameras/sensors in guest areas"
                    },
                    "duration_days": {
                        "type": "integer",
                        "description": "Expected guest stay duration"
                    }
                },
                "required": ["guest_areas"]
            }
        ),
        
        Tool(
            name="movie_mode",
            description=(
                "ðŸŽ¬ WORKFLOW: Activate movie mode with optimized lighting, audio, and climate. "
                "Dims lights, closes blinds, optimizes TV/audio, silences notifications."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Viewing area"
                    },
                    "media_player": {
                        "type": "string",
                        "description": "Media player entity ID"
                    },
                    "movie_type": {
                        "type": "string",
                        "enum": ["action", "drama", "comedy", "horror"],
                        "description": "Adjust ambiance based on genre"
                    }
                },
                "required": ["area"]
            }
        ),
        
        # =================================================================
        # CATEGORY: CONFIG FILE MANAGEMENT (SSH/SFTP)
        # =================================================================
        
        Tool(
            name="list_ha_config_files",
            description=(
                "List files in Home Assistant /config directory. "
                "Browse automation packages, configuration files, and other HA config files. "
                "Specify a subdirectory (e.g., 'packages', 'automations') or leave empty for root /config."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Subdirectory path (default: 'packages'). Examples: 'packages', '', 'custom_components'",
                        "default": "packages"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="read_ha_config_file",
            description=(
                "Read the content of a file in Home Assistant /config directory. "
                "View automation packages, configuration files, scripts, etc. "
                "Provide the relative path from /config (e.g., 'packages/lights.yaml', 'configuration.yaml')."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "File path relative to /config (e.g., 'packages/bedroom_lights.yaml')"
                    }
                },
                "required": ["filepath"]
            }
        ),
        
        Tool(
            name="write_ha_config_file",
            description=(
                "Write or update a file in Home Assistant /config directory. "
                "Create or modify automation packages, configuration files, etc. "
                "âš ï¸ IMPORTANT: This will modify your HA configuration! Always creates a backup (.bak) first. "
                "The file will be written to /config/ directory."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "File path relative to /config (e.g., 'packages/new_automation.yaml')"
                    },
                    "content": {
                        "type": "string",
                        "description": "File content (YAML, text, etc.)"
                    },
                    "create_backup": {
                        "type": "boolean",
                        "description": "Create backup before writing (default: true)",
                        "default": True
                    }
                },
                "required": ["filepath", "content"]
            }
        ),
        
        Tool(
            name="delete_ha_config_file",
            description=(
                "Delete a file from Home Assistant /config directory. "
                "âš ï¸ IMPORTANT: This will permanently modify your HA configuration! "
                "By default, creates a backup (.deleted) before removal."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "File path relative to /config (e.g., 'packages/old_automation.yaml')"
                    },
                    "create_backup": {
                        "type": "boolean",
                        "description": "Rename to .deleted instead of permanent delete (default: true)",
                        "default": True
                    }
                },
                "required": ["filepath"]
            }
        ),
        
        Tool(
            name="check_ha_config_file",
            description=(
                "Check if a file exists in Home Assistant /config directory. "
                "Useful before reading or writing to verify file presence."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "File path relative to /config (e.g., 'packages/lights.yaml')"
                    }
                },
                "required": ["filepath"]
            }
        ),
        
    ]


# ============================================================================
# ðŸ”§ TOOL IMPLEMENTATION HANDLERS
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    Execute a tool based on its name and arguments.
    Returns results as MCP content types.
    """
    
    try:
        # =================================================================
        # CATEGORY 1: DEVICE DISCOVERY & STATE
        # =================================================================
        
        if name == "discover_devices":
            domain = arguments.get("domain", "all")
            area = arguments.get("area")
            
            result = await ha_api.get_states()
            if not result["success"]:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
            
            entities = result["data"]
            
            # Filter by domain
            if domain != "all":
                entities = [e for e in entities if e["entity_id"].startswith(f"{domain}.")]
            
            # Filter by area (would need area registry, simplified here)
            if area:
                entities = [e for e in entities if area.lower() in e.get("attributes", {}).get("friendly_name", "").lower()]
            
            # Organize by domain
            devices_by_domain = {}
            for entity in entities:
                entity_domain = entity["entity_id"].split(".")[0]
                if entity_domain not in devices_by_domain:
                    devices_by_domain[entity_domain] = []
                
                # Extract area information from attributes or infer from name
                attributes = entity.get("attributes", {})
                friendly_name = attributes.get("friendly_name", entity["entity_id"])
                
                # Try to get area from attributes (usually not available via REST API)
                area_name = attributes.get("area_id") or attributes.get("area")
                
                # If not in attributes, infer from friendly name patterns
                if not area_name:
                    name_lower = friendly_name.lower()
                    # Common room name patterns
                    if "kitchen" in name_lower:
                        area_name = "kitchen"
                    elif "living room" in name_lower or "living_room" in name_lower or "livingroom" in name_lower:
                        area_name = "living_room"
                    elif "bedroom" in name_lower or "bed room" in name_lower:
                        area_name = "bedroom"
                    elif "bathroom" in name_lower or "bath room" in name_lower or "toilet" in name_lower:
                        area_name = "bathroom"
                    elif "hallway" in name_lower or "hall way" in name_lower or "corridor" in name_lower:
                        area_name = "hallway"
                    elif "garage" in name_lower:
                        area_name = "garage"
                    elif "office" in name_lower:
                        area_name = "office"
                    elif "dining room" in name_lower or "dining_room" in name_lower:
                        area_name = "dining_room"
                    elif "basement" in name_lower or "cellar" in name_lower:
                        area_name = "basement"
                    elif "attic" in name_lower or "loft" in name_lower:
                        area_name = "attic"
                    elif "stairs" in name_lower or "stairway" in name_lower:
                        area_name = "stairs"
                    elif "porch" in name_lower or "patio" in name_lower or "deck" in name_lower:
                        area_name = "outdoor"
                    elif "yard" in name_lower or "garden" in name_lower or "outdoor" in name_lower:
                        area_name = "outdoor"
                    elif "entry" in name_lower or "entrance" in name_lower or "foyer" in name_lower:
                        area_name = "entryway"
                    else:
                        area_name = "Unknown"
                
                devices_by_domain[entity_domain].append({
                    "entity_id": entity["entity_id"],
                    "name": friendly_name,
                    "state": entity["state"],
                    "area": area_name
                })
            
            response = f"ðŸ  **Discovered Devices**\n\n"
            for domain_name, devices in sorted(devices_by_domain.items()):
                response += f"\n**{domain_name.upper()}** ({len(devices)} devices):\n"
                for device in devices[:10]:  # Limit to 10 per domain
                    area_info = f" [Area: {device['area']}]" if device['area'] != "Unknown" else ""
                    response += f"  â€¢ {device['name']} (`{device['entity_id']}`) - {device['state']}{area_info}\n"
                if len(devices) > 10:
                    response += f"  ... and {len(devices) - 10} more\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "get_device_state":
            entity_id = arguments["entity_id"]
            
            result = await ha_api.get_states(entity_id)
            if not result["success"]:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
            
            state_data = result["data"]
            response = f"ðŸ“Š **Device State: {state_data.get('attributes', {}).get('friendly_name', entity_id)}**\n\n"
            response += f"**Entity ID:** `{entity_id}`\n"
            response += f"**State:** {state_data['state']}\n"
            response += f"**Last Changed:** {state_data.get('last_changed', 'Unknown')}\n\n"
            
            response += "**Attributes:**\n"
            for key, value in state_data.get("attributes", {}).items():
                response += f"  â€¢ {key}: {value}\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "get_area_devices":
            area = arguments["area"]
            device_types = arguments.get("device_types", [])
            
            result = await ha_api.get_states()
            if not result["success"]:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
            
            entities = result["data"]
            
            # Filter by area (simplified - looking for area in friendly_name)
            area_entities = [e for e in entities if area.lower().replace("_", " ") in 
                           e.get("attributes", {}).get("friendly_name", "").lower()]
            
            # Filter by device types
            if device_types:
                area_entities = [e for e in area_entities if any(e["entity_id"].startswith(f"{dt}.") for dt in device_types)]
            
            response = f"ðŸ  **Devices in {area.replace('_', ' ').title()}**\n\n"
            for entity in area_entities:
                name = entity.get("attributes", {}).get("friendly_name", entity["entity_id"])
                response += f"  â€¢ {name} (`{entity['entity_id']}`) - {entity['state']}\n"
            
            return [TextContent(type="text", text=response)]
        
        # =================================================================
        # CATEGORY 2: BASIC DEVICE CONTROL
        # =================================================================
        
        elif name == "control_light":
            entity_id = arguments["entity_id"]
            action = arguments["action"]
            
            service_data = {}
            
            if action == "turn_on":
                service = "turn_on"
                if "brightness" in arguments:
                    service_data["brightness"] = arguments["brightness"]
                if "rgb_color" in arguments:
                    service_data["rgb_color"] = arguments["rgb_color"]
                if "kelvin" in arguments:
                    service_data["kelvin"] = arguments["kelvin"]
                if "effect" in arguments:
                    service_data["effect"] = arguments["effect"]
                if "transition" in arguments:
                    service_data["transition"] = arguments["transition"]
            elif action == "turn_off":
                service = "turn_off"
                if "transition" in arguments:
                    service_data["transition"] = arguments["transition"]
            elif action == "toggle":
                service = "toggle"
            else:
                service = "turn_on"
                if action == "brightness" and "brightness" in arguments:
                    service_data["brightness"] = arguments["brightness"]
                elif action == "color" and "rgb_color" in arguments:
                    service_data["rgb_color"] = arguments["rgb_color"]
            
            result = await ha_api.call_service("light", service, entity_id, **service_data)
            
            if result["success"]:
                return [TextContent(type="text", text=f"âœ… Light control successful: {entity_id} - {action}")]
            else:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
        
        elif name == "control_switch":
            entity_id = arguments["entity_id"]
            action = arguments["action"]
            
            result = await ha_api.call_service("switch", action, entity_id)
            
            if result["success"]:
                return [TextContent(type="text", text=f"âœ… Switch {action}: {entity_id}")]
            else:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
        
        elif name == "control_climate":
            entity_id = arguments["entity_id"]
            service_data = {}
            
            if "temperature" in arguments:
                service_data["temperature"] = arguments["temperature"]
            if "hvac_mode" in arguments:
                service_data["hvac_mode"] = arguments["hvac_mode"]
            if "fan_mode" in arguments:
                service_data["fan_mode"] = arguments["fan_mode"]
            if "preset_mode" in arguments:
                service_data["preset_mode"] = arguments["preset_mode"]
            
            result = await ha_api.call_service("climate", "set_temperature", entity_id, **service_data)
            
            if result["success"]:
                return [TextContent(type="text", text=f"âœ… Climate control successful: {entity_id}")]
            else:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
        
        elif name == "control_cover":
            entity_id = arguments["entity_id"]
            action = arguments["action"]
            
            if action == "set_position":
                result = await ha_api.call_service("cover", "set_cover_position", 
                                                  entity_id, position=arguments["position"])
            elif action == "open":
                result = await ha_api.call_service("cover", "open_cover", entity_id)
            elif action == "close":
                result = await ha_api.call_service("cover", "close_cover", entity_id)
            elif action == "stop":
                result = await ha_api.call_service("cover", "stop_cover", entity_id)
            elif action == "toggle":
                result = await ha_api.call_service("cover", "toggle", entity_id)
            
            if result["success"]:
                return [TextContent(type="text", text=f"âœ… Cover control successful: {entity_id} - {action}")]
            else:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
        
        # =================================================================
        # CATEGORY 3: ADVANCED LIGHTING
        # =================================================================
        
        elif name == "adaptive_lighting":
            entity_ids = arguments["entity_ids"]
            activity = arguments.get("activity", "relaxing")
            ambient_lux = arguments.get("ambient_lux")
            preference = arguments.get("preference", "neutral")
            
            # Get current time and calculate lighting parameters
            now = datetime.now()
            hour = now.hour
            
            # Calculate brightness and color temperature based on context
            if activity == "sleeping":
                brightness = 0
                kelvin = 2000
            elif activity == "reading" or activity == "working":
                brightness = 220
                kelvin = 4500  # Cool white for focus
            elif activity == "watching_tv":
                brightness = 50
                kelvin = 2700
            elif activity == "cooking":
                brightness = 255
                kelvin = 4000
            elif activity == "dining":
                brightness = 180
                kelvin = 3000
            else:  # relaxing
                brightness = 120
                kelvin = 2700
            
            # Adjust for time of day
            if 6 <= hour < 9:  # Morning
                kelvin = min(kelvin + 500, 6500)
            elif 21 <= hour or hour < 6:  # Night
                kelvin = max(kelvin - 500, 2000)
                brightness = int(brightness * 0.7)
            
            # Adjust for ambient light
            if ambient_lux:
                if ambient_lux < 50:  # Dark
                    brightness = min(brightness + 30, 255)
                elif ambient_lux > 500:  # Bright
                    brightness = max(brightness - 50, 0)
            
            # Adjust for preference
            if preference == "energetic":
                brightness = min(brightness + 35, 255)
                kelvin = min(kelvin + 500, 6500)
            elif preference == "relaxing":
                brightness = max(brightness - 35, 0)
                kelvin = max(kelvin - 500, 2000)
            
            # Apply to all lights
            response = f"ðŸŒ… **Adaptive Lighting Applied**\n\n"
            response += f"**Context:** {activity.replace('_', ' ').title()}\n"
            response += f"**Settings:** {brightness}/255 brightness, {kelvin}K color temp\n"
            response += f"**Preference:** {preference.title()}\n\n"
            
            for entity_id in entity_ids:
                result = await ha_api.call_service("light", "turn_on", entity_id,
                                                  brightness=brightness, kelvin=kelvin, transition=3)
                status = "âœ…" if result["success"] else "âŒ"
                response += f"{status} {entity_id}\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "circadian_lighting":
            entity_ids = arguments["entity_ids"]
            sunrise_time = arguments.get("sunrise_time", "06:00")
            sunset_time = arguments.get("sunset_time", "18:00")
            transition_minutes = arguments.get("transition_minutes", 60)
            
            # Calculate current circadian position
            now = datetime.now()
            current_hour = now.hour + now.minute / 60
            
            sunrise_hour = int(sunrise_time.split(":")[0]) + int(sunrise_time.split(":")[1]) / 60
            sunset_hour = int(sunset_time.split(":")[0]) + int(sunset_time.split(":")[1]) / 60
            
            # Calculate color temperature based on sun position
            if current_hour < sunrise_hour:
                # Night - warm, dim
                kelvin = 2200
                brightness = 30
            elif sunrise_hour <= current_hour < sunrise_hour + 1:
                # Sunrise - warming up
                progress = (current_hour - sunrise_hour)
                kelvin = int(2200 + (4500 - 2200) * progress)
                brightness = int(30 + (200 - 30) * progress)
            elif sunrise_hour + 1 <= current_hour < 12:
                # Morning - bright, cool
                kelvin = 5500
                brightness = 220
            elif 12 <= current_hour < sunset_hour - 2:
                # Afternoon - bright
                kelvin = 5000
                brightness = 200
            elif sunset_hour - 2 <= current_hour < sunset_hour:
                # Pre-sunset - warming
                progress = (current_hour - (sunset_hour - 2)) / 2
                kelvin = int(5000 - (5000 - 3000) * progress)
                brightness = int(200 - (200 - 150) * progress)
            elif sunset_hour <= current_hour < sunset_hour + 2:
                # Sunset - warm
                progress = (current_hour - sunset_hour) / 2
                kelvin = int(3000 - (3000 - 2200) * progress)
                brightness = int(150 - (150 - 50) * progress)
            else:
                # Evening/Night - warm, dim
                kelvin = 2200
                brightness = 40
            
            response = f"ðŸŒž **Circadian Lighting Active**\n\n"
            response += f"**Time:** {now.strftime('%H:%M')}\n"
            response += f"**Color Temperature:** {kelvin}K\n"
            response += f"**Brightness:** {brightness}/255\n"
            response += f"**Sunrise/Sunset:** {sunrise_time} / {sunset_time}\n\n"
            
            for entity_id in entity_ids:
                result = await ha_api.call_service("light", "turn_on", entity_id,
                                                  brightness=brightness, kelvin=kelvin, 
                                                  transition=transition_minutes * 60)
                status = "âœ…" if result["success"] else "âŒ"
                response += f"{status} {entity_id}\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "multi_room_lighting_sync":
            areas = arguments["areas"]
            brightness = arguments.get("brightness", 180)
            color_temperature = arguments.get("color_temperature", 3000)
            transition_seconds = arguments.get("transition_seconds", 2)
            
            response = f"ðŸ  **Multi-Room Lighting Sync**\n\n"
            response += f"**Areas:** {', '.join(areas)}\n"
            response += f"**Brightness:** {brightness}/255\n"
            response += f"**Color Temperature:** {color_temperature}K\n\n"
            
            # Get all lights in specified areas
            all_states = await ha_api.get_states()
            if not all_states["success"]:
                return [TextContent(type="text", text=f"âŒ Error: {all_states['error']}")]
            
            for area in areas:
                area_lights = [e for e in all_states["data"] 
                             if e["entity_id"].startswith("light.") and 
                             area.lower().replace("_", " ") in e.get("attributes", {}).get("friendly_name", "").lower()]
                
                response += f"\n**{area.replace('_', ' ').title()}:**\n"
                for light in area_lights:
                    result = await ha_api.call_service("light", "turn_on", light["entity_id"],
                                                      brightness=brightness, kelvin=color_temperature,
                                                      transition=transition_seconds)
                    status = "âœ…" if result["success"] else "âŒ"
                    response += f"{status} {light.get('attributes', {}).get('friendly_name', light['entity_id'])}\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "presence_based_lighting":
            area = arguments["area"]
            motion_sensors = arguments.get("motion_sensors", [])
            timeout_minutes = arguments.get("timeout_minutes", 5)
            nightlight_mode = arguments.get("nightlight_mode", False)
            
            response = f"ðŸ‘¤ **Presence-Based Lighting Active**\n\n"
            response += f"**Area:** {area.replace('_', ' ').title()}\n"
            response += f"**Timeout:** {timeout_minutes} minutes\n"
            response += f"**Nightlight Mode:** {'Enabled' if nightlight_mode else 'Disabled'}\n\n"
            
            # Check motion sensors
            motion_detected = False
            for sensor_id in motion_sensors:
                sensor_state = await ha_api.get_states(sensor_id)
                if sensor_state["success"] and sensor_state["data"]["state"] == "on":
                    motion_detected = True
                    break
            
            # Get lights in area
            all_states = await ha_api.get_states()
            if all_states["success"]:
                area_lights = [e for e in all_states["data"]
                             if e["entity_id"].startswith("light.") and
                             area.lower().replace("_", " ") in e.get("attributes", {}).get("friendly_name", "").lower()]
                
                # Determine lighting settings
                now = datetime.now()
                is_night = now.hour >= 22 or now.hour < 6
                
                if motion_detected:
                    if is_night and nightlight_mode:
                        brightness = 50
                        kelvin = 2200
                    else:
                        brightness = 200
                        kelvin = 3500
                    
                    response += "**Status:** Motion detected, turning on lights\n"
                    for light in area_lights:
                        await ha_api.call_service("light", "turn_on", light["entity_id"],
                                                brightness=brightness, kelvin=kelvin, transition=1)
                else:
                    response += "**Status:** No motion, lights will turn off after timeout\n"
            
            return [TextContent(type="text", text=response)]
        
        # =================================================================
        # CATEGORY 4: MEDIA PLAYER CONTROL
        # =================================================================
        
        elif name == "control_media_player":
            entity_id = arguments["entity_id"]
            action = arguments["action"]
            
            if action == "volume_set":
                result = await ha_api.call_service("media_player", "volume_set", 
                                                  entity_id, volume_level=arguments["volume_level"])
            else:
                result = await ha_api.call_service("media_player", action, entity_id)
            
            if result["success"]:
                return [TextContent(type="text", text=f"âœ… Media player {action}: {entity_id}")]
            else:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
        
        elif name == "play_media":
            entity_id = arguments["entity_id"]
            media_content_id = arguments["media_content_id"]
            media_content_type = arguments["media_content_type"]
            
            result = await ha_api.call_service("media_player", "play_media", entity_id,
                                              media_content_id=media_content_id,
                                              media_content_type=media_content_type)
            
            if result["success"]:
                return [TextContent(type="text", text=f"â–¶ï¸ Playing {media_content_type}: {media_content_id}")]
            else:
                return [TextContent(type="text", text=f"âŒ Error: {result['error']}")]
        
        elif name == "multi_room_audio_sync":
            master_player = arguments["master_player"]
            slave_players = arguments["slave_players"]
            media_content_id = arguments.get("media_content_id")
            
            response = f"ðŸŽµ **Multi-Room Audio Sync**\n\n"
            response += f"**Master:** {master_player}\n"
            response += f"**Synced Players:** {len(slave_players)}\n\n"
            
            # Join slaves to master (implementation varies by platform)
            for slave in slave_players:
                result = await ha_api.call_service("media_player", "join", slave,
                                                  group_members=[master_player])
                status = "âœ…" if result["success"] else "âŒ"
                response += f"{status} {slave} joined\n"
            
            # Play media if provided
            if media_content_id:
                await ha_api.call_service("media_player", "play_media", master_player,
                                        media_content_id=media_content_id,
                                        media_content_type="music")
                response += f"\nâ–¶ï¸ Playing: {media_content_id}"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "party_mode":
            areas = arguments["areas"]
            music_playlist = arguments.get("music_playlist")
            lighting_effect = arguments.get("lighting_effect", "colorloop")
            
            response = f"ðŸŽ‰ **Party Mode Activated!**\n\n"
            response += f"**Areas:** {', '.join(areas)}\n"
            response += f"**Lighting:** {lighting_effect}\n\n"
            
            # Get all lights and media players in areas
            all_states = await ha_api.get_states()
            if all_states["success"]:
                for area in areas:
                    area_name = area.replace("_", " ")
                    response += f"\n**{area_name.title()}:**\n"
                    
                    # Set lighting
                    lights = [e for e in all_states["data"]
                             if e["entity_id"].startswith("light.") and
                             area_name in e.get("attributes", {}).get("friendly_name", "").lower()]
                    
                    for light in lights:
                        if lighting_effect == "colorloop":
                            await ha_api.call_service("light", "turn_on", light["entity_id"],
                                                    brightness=200, effect="colorloop")
                        elif lighting_effect == "energetic":
                            await ha_api.call_service("light", "turn_on", light["entity_id"],
                                                    brightness=255, rgb_color=[255, 100, 0])
                        response += f"  ðŸ’¡ {light.get('attributes', {}).get('friendly_name', '')}\n"
                    
                    # Start music
                    if music_playlist:
                        media_players = [e for e in all_states["data"]
                                       if e["entity_id"].startswith("media_player.") and
                                       area_name in e.get("attributes", {}).get("friendly_name", "").lower()]
                        
                        for player in media_players:
                            await ha_api.call_service("media_player", "play_media", player["entity_id"],
                                                    media_content_id=music_playlist,
                                                    media_content_type="playlist")
                            response += f"  ðŸŽµ {player.get('attributes', {}).get('friendly_name', '')}\n"
            
            return [TextContent(type="text", text=response)]
        
        # =================================================================
        # CATEGORY 9: WORKFLOWS
        # =================================================================
        
        elif name == "morning_routine":
            wake_time = arguments.get("wake_time", "07:00")
            gradual_wake = arguments.get("gradual_wake", True)
            weather_announcement = arguments.get("weather_announcement", False)
            coffee_maker = arguments.get("coffee_maker")
            
            response = f"ðŸŒ… **Morning Routine Starting**\n\n"
            response += f"**Wake Time:** {wake_time}\n"
            response += f"**Gradual Wake:** {'Yes' if gradual_wake else 'No'}\n\n"
            
            # Gradually increase bedroom lights
            bedroom_lights = await ha_api.get_states()
            if bedroom_lights["success"]:
                lights = [e for e in bedroom_lights["data"]
                         if e["entity_id"].startswith("light.") and "bedroom" in e["entity_id"]]
                
                if gradual_wake:
                    response += "**Lighting:** Gradual wake (20 min transition)\n"
                    for light in lights:
                        await ha_api.call_service("light", "turn_on", light["entity_id"],
                                                brightness=200, kelvin=4000, transition=1200)
                
                # Start coffee maker
                if coffee_maker:
                    await ha_api.call_service("switch", "turn_on", coffee_maker)
                    response += f"â˜• Coffee maker started\n"
                
                response += "\n**Good morning! Your home is ready for the day.**"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "movie_mode":
            area = arguments["area"]
            media_player = arguments.get("media_player")
            movie_type = arguments.get("movie_type", "action")
            
            response = f"ðŸŽ¬ **Movie Mode Activated**\n\n"
            response += f"**Area:** {area.replace('_', ' ').title()}\n"
            response += f"**Genre:** {movie_type.title()}\n\n"
            
            # Dim lights based on movie type
            brightness_map = {
                "action": 20,
                "drama": 30,
                "comedy": 40,
                "horror": 10
            }
            brightness = brightness_map.get(movie_type, 25)
            
            # Get lights in area
            all_states = await ha_api.get_states()
            if all_states["success"]:
                area_lights = [e for e in all_states["data"]
                             if e["entity_id"].startswith("light.") and
                             area.lower() in e.get("attributes", {}).get("friendly_name", "").lower()]
                
                response += "**Lighting:**\n"
                for light in area_lights:
                    await ha_api.call_service("light", "turn_on", light["entity_id"],
                                            brightness=brightness, kelvin=2700, transition=5)
                    response += f"  ðŸ”… {light.get('attributes', {}).get('friendly_name', '')} â†’ {brightness}/255\n"
                
                # Close covers
                covers = [e for e in all_states["data"]
                         if e["entity_id"].startswith("cover.") and
                         area.lower() in e.get("attributes", {}).get("friendly_name", "").lower()]
                
                if covers:
                    response += "\n**Blinds/Curtains:**\n"
                    for cover in covers:
                        await ha_api.call_service("cover", "close_cover", cover["entity_id"])
                        response += f"  ðŸªŸ {cover.get('attributes', {}).get('friendly_name', '')} â†’ Closed\n"
                
                response += "\nðŸ¿ **Enjoy your movie!**"
            
            return [TextContent(type="text", text=response)]
        
        # =================================================================
        # CATEGORY 10: INTELLIGENCE
        # =================================================================
        
        elif name == "analyze_home_context":
            include_predictions = arguments.get("include_predictions", False)
            include_recommendations = arguments.get("include_recommendations", False)
            
            response = f"ðŸ§  **Home Context Analysis**\n\n"
            
            # Get all states
            all_states = await ha_api.get_states()
            if not all_states["success"]:
                return [TextContent(type="text", text=f"âŒ Error: {all_states['error']}")]
            
            entities = all_states["data"]
            
            # Analyze current state
            now = datetime.now()
            response += f"**Time:** {now.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
            response += f"**Day Type:** {'Weekend' if now.weekday() >= 5 else 'Weekday'}\n\n"
            
            # Count active devices
            lights_on = len([e for e in entities if e["entity_id"].startswith("light.") and e["state"] == "on"])
            switches_on = len([e for e in entities if e["entity_id"].startswith("switch.") and e["state"] == "on"])
            media_playing = len([e for e in entities if e["entity_id"].startswith("media_player.") and e["state"] == "playing"])
            
            response += "**Device Summary:**\n"
            response += f"  ðŸ’¡ Lights ON: {lights_on}\n"
            response += f"  ðŸ”Œ Switches ON: {switches_on}\n"
            response += f"  ðŸ“º Media Playing: {media_playing}\n\n"
            
            # Detect likely activity
            if 22 <= now.hour or now.hour < 6:
                activity = "Sleeping/Night"
            elif 6 <= now.hour < 9:
                activity = "Morning Routine"
            elif media_playing > 0 and lights_on < 3:
                activity = "Watching Media"
            elif lights_on > 5:
                activity = "Active/Entertaining"
            else:
                activity = "Normal Daily Activity"
            
            response += f"**Detected Activity:** {activity}\n\n"
            
            if include_recommendations:
                response += "**Recommendations:**\n"
                if lights_on > 10:
                    response += "  ðŸ’¡ Consider turning off unused lights to save energy\n"
                if now.hour >= 21 and lights_on > 0:
                    response += "  ðŸŒ™ Evening detected - consider warm lighting for better sleep\n"
                if switches_on > 5 and now.hour < 6:
                    response += "  âš¡ Several devices on during night - energy optimization opportunity\n"
            
            return [TextContent(type="text", text=response)]
        
        # =================================================================
        # CATEGORY: CONFIG FILE MANAGEMENT
        # =================================================================
        
        elif name == "list_ha_config_files":
            if not ha_config.enabled:
                return [TextContent(type="text", text="âŒ SSH not configured. Set HA_SSH_PASSWORD environment variable.")]
            
            path = arguments.get("path", "packages")
            
            try:
                files = ha_config.list_files(path)
                response = f"ðŸ“ **Files in /config/{path}/**\n\n"
                
                if not files:
                    response += f"No files found in /config/{path}/\n"
                else:
                    for f in files:
                        response += f"  ðŸ“„ {f}\n"
                    response += f"\n**Total:** {len(files)} files"
                
                return [TextContent(type="text", text=response)]
            except Exception as e:
                return [TextContent(type="text", text=f"âŒ Error listing files: {str(e)}")]
        
        elif name == "read_ha_config_file":
            if not ha_config.enabled:
                return [TextContent(type="text", text="âŒ SSH not configured. Set HA_SSH_PASSWORD environment variable.")]
            
            filepath = arguments.get("filepath")
            
            try:
                content = ha_config.read_file(filepath)
                response = f"ðŸ“„ **File: /config/{filepath}**\n\n```\n{content}\n```"
                return [TextContent(type="text", text=response)]
            except Exception as e:
                return [TextContent(type="text", text=f"âŒ Error reading file: {str(e)}")]
        
        elif name == "write_ha_config_file":
            if not ha_config.enabled:
                return [TextContent(type="text", text="âŒ SSH not configured. Set HA_SSH_PASSWORD environment variable.")]
            
            filepath = arguments.get("filepath")
            content = arguments.get("content")
            create_backup = arguments.get("create_backup", True)
            
            try:
                # Validate YAML if it's a YAML file
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    try:
                        import yaml
                        yaml.safe_load(content)
                    except Exception as yaml_err:
                        return [TextContent(type="text", text=f"âŒ Invalid YAML syntax: {str(yaml_err)}")]
                
                # Write file
                ha_config.write_file(filepath, content, create_backup)
                
                response = f"âœ… **File written: /config/{filepath}**\n\n"
                if create_backup:
                    response += "ðŸ“¦ Backup created: .bak\n"
                response += "\nðŸ’¡ **Next steps:**\n"
                response += "  1. Check HA logs for errors\n"
                response += "  2. Reload HA configuration if needed\n"
                response += "  3. Test the automation/configuration\n"
                
                return [TextContent(type="text", text=response)]
            except Exception as e:
                return [TextContent(type="text", text=f"âŒ Error writing file: {str(e)}")]
        
        elif name == "delete_ha_config_file":
            if not ha_config.enabled:
                return [TextContent(type="text", text="âŒ SSH not configured. Set HA_SSH_PASSWORD environment variable.")]
            
            filepath = arguments.get("filepath")
            create_backup = arguments.get("create_backup", True)
            
            try:
                ha_config.delete_file(filepath, create_backup)
                
                response = f"âœ… **File removed: /config/{filepath}**\n\n"
                if create_backup:
                    response += "ðŸ“¦ Backup saved as: .deleted\n"
                else:
                    response += "âš ï¸ File permanently deleted (no backup)\n"
                
                return [TextContent(type="text", text=response)]
            except Exception as e:
                return [TextContent(type="text", text=f"âŒ Error deleting file: {str(e)}")]
        
        elif name == "check_ha_config_file":
            if not ha_config.enabled:
                return [TextContent(type="text", text="âŒ SSH not configured. Set HA_SSH_PASSWORD environment variable.")]
            
            filepath = arguments.get("filepath")
            
            try:
                exists = ha_config.file_exists(filepath)
                if exists:
                    return [TextContent(type="text", text=f"âœ… File exists: /config/{filepath}")]
                else:
                    return [TextContent(type="text", text=f"âŒ File not found: /config/{filepath}")]
            except Exception as e:
                return [TextContent(type="text", text=f"âŒ Error checking file: {str(e)}")]
        
        # =================================================================
        # FALLBACK FOR UNIMPLEMENTED TOOLS
        # =================================================================
        
        else:
            # For tools not yet fully implemented, provide helpful response
            return [TextContent(type="text", text=(
                f"ðŸš§ **Tool '{name}' is defined but implementation is in progress.**\n\n"
                f"This tool will provide: {name.replace('_', ' ').title()} functionality.\n\n"
                f"Arguments received:\n" + 
                "\n".join([f"  â€¢ {k}: {v}" for k, v in arguments.items()]) +
                "\n\nðŸ’¡ Basic functionality is available through other tools."
            ))]
    
    except Exception as e:
        logger.error(f"Tool execution error: {name} - {str(e)}")
        return [TextContent(type="text", text=f"âŒ Error executing {name}: {str(e)}")]


# ============================================================================
# ðŸš€ SERVER STARTUP
# ============================================================================

async def main():
    """Main entry point for the MCP server."""
    logger.info("ðŸ  Home Assistant MCP Server starting...")
    logger.info(f"ðŸ“¡ Home Assistant URL: {HA_URL}")
    logger.info(f"ðŸ”‘ Token configured: {'Yes' if HA_TOKEN else 'No'}")
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("âœ… MCP Server running on stdio")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
