#!/usr/bin/env python3
"""
🏠 Home Assistant MCP Server - Native Add-on (Part 1: Basic Controls)
CONVERTED TOOLS from external REST/SSH server to native HA addon

This file contains:
- Device Discovery & State Management (3 tools)
- Basic Device Control (4 tools)  
- Advanced Lighting Control (4 tools)
- Media Player Control (4 tools)
- Climate & Environment (3 tools)

Total: ~18 tools in Part 1
"""

from datetime import datetime, timedelta
import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent


# ============================================================================
# PART 1: TOOL DEFINITIONS (to add to list_tools() in server.py)
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

async def handle_part1_tools(name: str, arguments: dict, ha_api, file_mgr) -> list[TextContent]:
    """
    Handler functions for Part 1 tools
    Copy these elif blocks into the main call_tool() function
    """
    
    # =================================================================
    # DEVICE DISCOVERY & STATE
    # =================================================================
    
    if name == "discover_devices":
        # Get all states
        all_states = await ha_api.get_states()
        
        # Apply filters
        filtered = all_states
        
        # Filter by domain
        if "domain" in arguments and arguments["domain"] != "all":
            domain = arguments["domain"]
            filtered = [s for s in filtered if s.get("entity_id", "").startswith(f"{domain}.")]
        
        # Filter by state
        if "state_filter" in arguments:
            state = arguments["state_filter"]
            filtered = [s for s in filtered if s.get("state") == state]
        
        # Apply limit
        limit = arguments.get("limit", 100)
        filtered = filtered[:limit]
        
        # Format response
        devices = []
        for state in filtered:
            devices.append({
                "entity_id": state.get("entity_id"),
                "friendly_name": state.get("attributes", {}).get("friendly_name", state.get("entity_id")),
                "state": state.get("state"),
                "domain": state.get("entity_id", "").split(".")[0],
                "last_changed": state.get("last_changed")
            })
        
        result = {
            "total_found": len(devices),
            "devices": devices
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    elif name == "get_device_state":
        entity_id = arguments["entity_id"]
        state = await ha_api.get_state(entity_id)
        
        # Enhanced formatting with all details
        result = {
            "entity_id": state.get("entity_id"),
            "state": state.get("state"),
            "attributes": state.get("attributes", {}),
            "last_changed": state.get("last_changed"),
            "last_updated": state.get("last_updated"),
            "context": state.get("context", {})
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    elif name == "get_area_devices":
        area = arguments["area"]
        all_states = await ha_api.get_states()
        
        # Filter by area (check attributes)
        area_devices = []
        for state in all_states:
            device_area = state.get("attributes", {}).get("area", "")
            if device_area.lower() == area.lower():
                area_devices.append(state)
        
        # Group by domain
        grouped = {}
        for device in area_devices:
            domain = device.get("entity_id", "").split(".")[0]
            if domain not in grouped:
                grouped[domain] = []
            grouped[domain].append({
                "entity_id": device.get("entity_id"),
                "friendly_name": device.get("attributes", {}).get("friendly_name"),
                "state": device.get("state")
            })
        
        result = {
            "area": area,
            "device_count": len(area_devices),
            "devices_by_type": grouped
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # =================================================================
    # BASIC DEVICE CONTROL
    # =================================================================
    
    elif name == "control_light":
        entity_id = arguments["entity_id"]
        action = arguments["action"]
        
        service_data = {"entity_id": entity_id}
        
        # Add optional parameters
        if "brightness" in arguments:
            service_data["brightness"] = arguments["brightness"]
        if "brightness_pct" in arguments:
            service_data["brightness_pct"] = arguments["brightness_pct"]
        if "rgb_color" in arguments:
            service_data["rgb_color"] = arguments["rgb_color"]
        if "color_temp" in arguments:
            service_data["color_temp"] = arguments["color_temp"]
        if "effect" in arguments:
            service_data["effect"] = arguments["effect"]
        if "transition" in arguments:
            service_data["transition"] = arguments["transition"]
        
        result = await ha_api.call_service("light", action, service_data)
        return [TextContent(type="text", text=f"✅ Light {action} successful: {entity_id}")]
    
    elif name == "control_switch":
        entity_id = arguments["entity_id"]
        action = arguments["action"]
        
        result = await ha_api.call_service("switch", action, {"entity_id": entity_id})
        return [TextContent(type="text", text=f"✅ Switch {action} successful: {entity_id}")]
    
    elif name == "control_climate":
        entity_id = arguments["entity_id"]
        service_data = {"entity_id": entity_id}
        
        # Determine service based on what's being changed
        if "temperature" in arguments:
            service_data["temperature"] = arguments["temperature"]
            service = "set_temperature"
        elif "hvac_mode" in arguments:
            service_data["hvac_mode"] = arguments["hvac_mode"]
            service = "set_hvac_mode"
        elif "fan_mode" in arguments:
            service_data["fan_mode"] = arguments["fan_mode"]
            service = "set_fan_mode"
        elif "preset_mode" in arguments:
            service_data["preset_mode"] = arguments["preset_mode"]
            service = "set_preset_mode"
        else:
            service = "set_temperature"
        
        # Add dual setpoint if provided
        if "target_temp_high" in arguments:
            service_data["target_temp_high"] = arguments["target_temp_high"]
        if "target_temp_low" in arguments:
            service_data["target_temp_low"] = arguments["target_temp_low"]
        
        result = await ha_api.call_service("climate", service, service_data)
        return [TextContent(type="text", text=f"✅ Climate control successful: {entity_id}")]
    
    elif name == "control_cover":
        entity_id = arguments["entity_id"]
        action = arguments["action"]
        
        service_data = {"entity_id": entity_id}
        
        # Handle position/tilt
        if "position" in arguments:
            service_data["position"] = arguments["position"]
            service = "set_cover_position"
        elif "tilt_position" in arguments:
            service_data["tilt_position"] = arguments["tilt_position"]
            service = "set_cover_tilt_position"
        else:
            service = action
        
        result = await ha_api.call_service("cover", service, service_data)
        return [TextContent(type="text", text=f"✅ Cover {action} successful: {entity_id}")]
    
    # =================================================================
    # ADVANCED LIGHTING (Simplified implementations)
    # =================================================================
    
    elif name == "adaptive_lighting":
        entity_id = arguments["entity_id"]
        activity = arguments.get("activity", "auto")
        
        # Activity-based presets
        presets = {
            "reading": {"brightness": 255, "color_temp": 400},  # Cool white
            "watching_tv": {"brightness": 50, "color_temp": 500},  # Dim warm
            "cooking": {"brightness": 255, "color_temp": 370},  # Bright neutral
            "relaxing": {"brightness": 100, "color_temp": 454},  # Soft warm
            "working": {"brightness": 200, "color_temp": 380}  # Bright neutral
        }
        
        # If auto, base on time of day
        if activity == "auto":
            hour = datetime.now().hour
            if 6 <= hour < 9:
                preset = {"brightness": 200, "color_temp": 370}  # Morning
            elif 9 <= hour < 17:
                preset = {"brightness": 255, "color_temp": 400}  # Day
            elif 17 <= hour < 21:
                preset = {"brightness": 150, "color_temp": 450}  # Evening
            else:
                preset = {"brightness": 50, "color_temp": 500}  # Night
        else:
            preset = presets.get(activity, presets["relaxing"])
        
        service_data = {"entity_id": entity_id, **preset}
        await ha_api.call_service("light", "turn_on", service_data)
        
        return [TextContent(type="text", text=f"✅ Adaptive lighting applied: {activity} mode")]
    
    elif name == "circadian_lighting":
        entity_id = arguments["entity_id"]
        
        # Calculate color temp and brightness based on time
        hour = datetime.now().hour
        
        # Circadian curve
        if 6 <= hour < 12:  # Morning: energizing
            color_temp = 350 + (hour - 6) * 10  # 350-410 mireds
            brightness = 150 + (hour - 6) * 15  # 150-240
        elif 12 <= hour < 18:  # Afternoon: sustained
            color_temp = 380  # Neutral
            brightness = 255
        elif 18 <= hour < 22:  # Evening: wind down
            color_temp = 380 + (hour - 18) * 30  # 380-500 mireds
            brightness = 255 - (hour - 18) * 40  # 255-95
        else:  # Night: sleep prep
            color_temp = 500
            brightness = arguments.get("min_brightness", 10)
        
        service_data = {
            "entity_id": entity_id,
            "brightness": int(brightness),
            "color_temp": int(color_temp),
            "transition": arguments.get("transition_duration", 30)
        }
        
        await ha_api.call_service("light", "turn_on", service_data)
        return [TextContent(type="text", text=f"✅ Circadian lighting applied (CT: {int(color_temp)}K, Brightness: {int(brightness)})")]
    
    elif name == "multi_room_lighting_sync":
        rooms = arguments["rooms"]
        activity = arguments["activity"]
        
        # Activity presets
        activity_settings = {
            "movie": {"brightness": 10, "color_temp": 500},
            "party": {"effect": "colorloop", "brightness": 200},
            "dinner": {"brightness": 120, "color_temp": 454},
            "cleanup": {"brightness": 255, "color_temp": 370},
            "bedtime": {"brightness": 30, "color_temp": 500}
        }
        
        settings = activity_settings.get(activity, {})
        if "custom_brightness" in arguments:
            settings["brightness"] = arguments["custom_brightness"]
        if "custom_color_temp" in arguments:
            settings["color_temp"] = arguments["custom_color_temp"]
        
        # Apply to all rooms (assuming room = area, lights are light.{room}_*)
        results = []
        for room in rooms:
            # Get all lights in this room
            all_states = await ha_api.get_states()
            room_lights = [
                s.get("entity_id") for s in all_states
                if s.get("entity_id", "").startswith("light.") and
                room.lower() in s.get("entity_id", "").lower()
            ]
            
            for light in room_lights:
                service_data = {"entity_id": light, **settings}
                await ha_api.call_service("light", "turn_on", service_data)
                results.append(light)
        
        return [TextContent(type="text", text=f"✅ Synchronized {len(results)} lights across {len(rooms)} rooms in {activity} mode")]
    
    elif name == "presence_based_lighting":
        # This would require automation setup in HA
        # For now, return configuration guidance
        light = arguments["light_entity"]
        sensor = arguments["motion_sensor"]
        timeout = arguments.get("timeout_seconds", 300)
        
        automation_yaml = f"""
# Presence-based lighting automation
automation:
  - alias: "Presence Light - {light}"
    trigger:
      - platform: state
        entity_id: {sensor}
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: {light}
    
  - alias: "Presence Light Off - {light}"
    trigger:
      - platform: state
        entity_id: {sensor}
        to: "off"
        for:
          seconds: {timeout}
    action:
      - service: light.turn_off
        target:
          entity_id: {light}
"""
        
        return [TextContent(type="text", text=f"✅ Presence-based lighting configuration:\n\n{automation_yaml}")]
    
    # =================================================================
    # MEDIA PLAYER CONTROL
    # =================================================================
    
    elif name == "control_media_player":
        entity_id = arguments["entity_id"]
        action = arguments["action"]
        
        service_data = {"entity_id": entity_id}
        
        # Add optional parameters
        if "volume_level" in arguments:
            service_data["volume_level"] = arguments["volume_level"]
        if "source" in arguments:
            service_data["source"] = arguments["source"]
        
        # Map action to service
        if action in ["turn_on", "turn_off", "toggle", "volume_up", "volume_down", 
                      "media_play_pause", "media_next_track", "media_previous_track"]:
            service = action
        elif action == "mute":
            service = "volume_mute"
            service_data["is_volume_muted"] = True
        elif action == "unmute":
            service = "volume_mute"
            service_data["is_volume_muted"] = False
        else:
            service = action
        
        result = await ha_api.call_service("media_player", service, service_data)
        return [TextContent(type="text", text=f"✅ Media player {action} successful: {entity_id}")]
    
    elif name == "play_media":
        entity_id = arguments["entity_id"]
        media_content_id = arguments["media_content_id"]
        media_content_type = arguments["media_content_type"]
        
        service_data = {
            "entity_id": entity_id,
            "media_content_id": media_content_id,
            "media_content_type": media_content_type
        }
        
        result = await ha_api.call_service("media_player", "play_media", service_data)
        return [TextContent(type="text", text=f"✅ Playing media on {entity_id}")]
    
    elif name == "multi_room_audio_sync":
        players = arguments["media_players"]
        master = arguments.get("master_player", players[0])
        
        # Join all players to master
        service_data = {
            "entity_id": master,
            "group_members": players
        }
        
        result = await ha_api.call_service("media_player", "join", service_data)
        
        # Set volume if specified
        if "volume_level" in arguments:
            for player in players:
                await ha_api.call_service("media_player", "volume_set", {
                    "entity_id": player,
                    "volume_level": arguments["volume_level"]
                })
        
        # Play media if specified
        if "media_content_id" in arguments:
            await ha_api.call_service("media_player", "play_media", {
                "entity_id": master,
                "media_content_id": arguments["media_content_id"],
                "media_content_type": "music"
            })
        
        return [TextContent(type="text", text=f"✅ Synchronized {len(players)} media players")]
    
    elif name == "party_mode":
        rooms = arguments["rooms"]
        
        results = []
        
        # Set colorful lighting
        all_states = await ha_api.get_states()
        for room in rooms:
            room_lights = [
                s.get("entity_id") for s in all_states
                if s.get("entity_id", "").startswith("light.") and
                room.lower() in s.get("entity_id", "").lower()
            ]
            
            for light in room_lights:
                await ha_api.call_service("light", "turn_on", {
                    "entity_id": light,
                    "effect": "colorloop",
                    "brightness": 200
                })
                results.append(f"Light: {light}")
        
        # Set multi-room audio if media provided
        if "music_source" in arguments:
            media_players = [
                s.get("entity_id") for s in all_states
                if s.get("entity_id", "").startswith("media_player.") and
                any(room.lower() in s.get("entity_id", "").lower() for room in rooms)
            ]
            
            if media_players:
                master = media_players[0]
                await ha_api.call_service("media_player", "join", {
                    "entity_id": master,
                    "group_members": media_players
                })
                await ha_api.call_service("media_player", "play_media", {
                    "entity_id": master,
                    "media_content_id": arguments["music_source"],
                    "media_content_type": "music"
                })
                results.append(f"Audio: {len(media_players)} players")
        
        return [TextContent(type="text", text=f"🎉 Party mode activated!\n" + "\n".join(results))]
    
    # =================================================================
    # CLIMATE & ENVIRONMENT
    # =================================================================
    
    elif name == "smart_thermostat_optimization":
        entity_id = arguments["entity_id"]
        mode = arguments["mode"]
        
        # Mode-based temperature presets
        temp_presets = {
            "home": 22,  # Comfort
            "away": 18,  # Energy saving
            "sleep": 19,  # Nighttime
            "eco": 17    # Maximum efficiency
        }
        
        target_temp = temp_presets.get(mode, 22)
        
        await ha_api.call_service("climate", "set_temperature", {
            "entity_id": entity_id,
            "temperature": target_temp
        })
        
        return [TextContent(type="text", text=f"✅ Thermostat optimized for {mode} mode ({target_temp}°C)")]
    
    elif name == "zone_climate_control":
        zones = arguments["zones"]
        
        results = []
        for zone in zones:
            await ha_api.call_service("climate", "set_temperature", {
                "entity_id": zone["entity_id"],
                "temperature": zone["target_temp"]
            })
            results.append(f"{zone['name']}: {zone['target_temp']}°C")
        
        return [TextContent(type="text", text=f"✅ Zone climate control:\n" + "\n".join(results))]
    
    elif name == "air_quality_management":
        sensor = arguments["air_quality_sensor"]
        
        # Get current AQI
        state = await ha_api.get_state(sensor)
        current_aqi = float(state.get("state", 0))
        target_aqi = arguments.get("target_aqi", 50)
        
        actions = []
        
        # Turn on fan/purifier if AQI too high
        if current_aqi > target_aqi and "fan_entity" in arguments:
            await ha_api.call_service("fan", "turn_on", {
                "entity_id": arguments["fan_entity"]
            })
            actions.append(f"Activated air purifier (AQI: {current_aqi})")
        
        # Open windows if specified
        if "window_entities" in arguments and current_aqi > target_aqi:
            for window in arguments["window_entities"]:
                await ha_api.call_service("cover", "open_cover", {
                    "entity_id": window
                })
                actions.append(f"Opened window: {window}")
        
        result = f"🌬️ Air quality management:\nCurrent AQI: {current_aqi}\nTarget: {target_aqi}\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    else:
        return None  # Tool not in Part 1
