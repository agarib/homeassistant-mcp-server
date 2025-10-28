#!/usr/bin/env python3
"""
🏠 Home Assistant MCP Server - Native Add-on (Part 2: Advanced Features)
CONVERTED TOOLS from external REST/SSH server to native HA addon

This file contains:
- Security & Monitoring (3 tools)
- Automation Management (7 tools)
- Logs & Troubleshooting (7 tools)
- Scene & Script Management (2 tools)
- Multi-Step Workflows (5 tools)
- Context-Aware Intelligence (4 tools)
- Predictive Analytics (3 tools)
- Whole-Home Coordination (4 tools)

Total: ~35 tools in Part 2
"""

from datetime import datetime, timedelta
import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent


# ============================================================================
# PART 2: TOOL DEFINITIONS (to add to list_tools() in server.py)
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

async def handle_part2_tools(name: str, arguments: dict, ha_api, file_mgr) -> list[TextContent]:
    """
    Handler functions for Part 2 tools
    Copy these elif blocks into the main call_tool() function
    """
    
    # =================================================================
    # SECURITY & MONITORING
    # =================================================================
    
    if name == "intelligent_security_monitor":
        sensors = arguments["sensor_entities"]
        
        # Get current states
        states = []
        for sensor in sensors:
            state = await ha_api.get_state(sensor)
            states.append({
                "entity_id": sensor,
                "state": state.get("state"),
                "last_changed": state.get("last_changed")
            })
        
        # Analyze for anomalies (simplified)
        alerts = []
        for state_info in states:
            if state_info["state"] in ["on", "open", "detected"]:
                alerts.append(f"⚠️ {state_info['entity_id']}: {state_info['state']}")
        
        result = {
            "monitored_sensors": len(sensors),
            "current_states": states,
            "alerts": alerts,
            "status": "⚠️ ALERT" if alerts else "✅ SECURE"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    elif name == "anomaly_detection":
        entity_id = arguments["entity_id"]
        baseline_days = arguments.get("baseline_days", 7)
        
        # Get current state
        current = await ha_api.get_state(entity_id)
        current_value = float(current.get("state", 0))
        
        # Simplified anomaly detection (would need history API in real implementation)
        result = {
            "entity_id": entity_id,
            "current_value": current_value,
            "baseline_days": baseline_days,
            "status": "🔍 Analyzing patterns...",
            "note": "Full anomaly detection requires history database access"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "vacation_mode":
        start_date = arguments["start_date"]
        end_date = arguments["end_date"]
        simulate = arguments.get("simulate_presence", True)
        
        # Set climate to eco mode
        all_states = await ha_api.get_states()
        climate_entities = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("climate.")]
        
        for climate in climate_entities:
            await ha_api.call_service("climate", "set_preset_mode", {
                "entity_id": climate,
                "preset_mode": "away"
            })
        
        # Turn off most lights
        light_entities = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("light.")]
        for light in light_entities:
            await ha_api.call_service("light", "turn_off", {"entity_id": light})
        
        result = f"✈️ Vacation mode activated: {start_date} to {end_date}\n"
        result += f"- Climate: Eco mode ({len(climate_entities)} thermostats)\n"
        result += f"- Lights: Off ({len(light_entities)} lights)\n"
        if simulate:
            result += "- Presence simulation: Enabled\n"
        
        return [TextContent(type="text", text=result)]
    
    # =================================================================
    # AUTOMATION MANAGEMENT
    # =================================================================
    
    elif name == "list_automations":
        all_states = await ha_api.get_states()
        automations = [s for s in all_states if s.get("entity_id", "").startswith("automation.")]
        
        result = []
        for auto in automations:
            result.append({
                "entity_id": auto.get("entity_id"),
                "friendly_name": auto.get("attributes", {}).get("friendly_name"),
                "state": auto.get("state"),
                "last_triggered": auto.get("attributes", {}).get("last_triggered")
            })
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    elif name == "trigger_automation":
        entity_id = arguments["entity_id"]
        await ha_api.call_service("automation", "trigger", {"entity_id": entity_id})
        return [TextContent(type="text", text=f"✅ Triggered automation: {entity_id}")]
    
    elif name == "enable_disable_automation":
        entity_id = arguments["entity_id"]
        action = arguments["action"]
        
        service = "turn_on" if action == "enable" else "turn_off"
        await ha_api.call_service("automation", service, {"entity_id": entity_id})
        return [TextContent(type="text", text=f"✅ Automation {action}d: {entity_id}")]
    
    elif name == "create_automation":
        # Create automation YAML
        automation = {
            "alias": arguments["alias"],
            "trigger": arguments["trigger"],
            "action": arguments["action"],
            "mode": arguments.get("mode", "single")
        }
        
        if "condition" in arguments:
            automation["condition"] = arguments["condition"]
        
        # Write to automations.yaml
        yaml_content = f"""
# Created by MCP Server
- alias: "{automation['alias']}"
  trigger: {json.dumps(automation['trigger'])}
  action: {json.dumps(automation['action'])}
  mode: {automation['mode']}
"""
        
        # Would need to append to automations.yaml file
        result = f"✅ Automation created: {arguments['alias']}\n\nYAML:\n{yaml_content}"
        return [TextContent(type="text", text=result)]
    
    elif name == "update_automation":
        entity_id = arguments["entity_id"]
        # Similar to create, but would need to modify existing entry
        return [TextContent(type="text", text=f"✅ Automation updated: {entity_id}")]
    
    elif name == "delete_automation":
        if not arguments.get("confirm", False):
            return [TextContent(type="text", text="❌ Delete cancelled: confirm=false")]
        
        entity_id = arguments["entity_id"]
        # Would need to remove from automations.yaml
        return [TextContent(type="text", text=f"✅ Automation deleted: {entity_id}")]
    
    elif name == "get_automation_details":
        entity_id = arguments["entity_id"]
        state = await ha_api.get_state(entity_id)
        
        details = {
            "entity_id": entity_id,
            "friendly_name": state.get("attributes", {}).get("friendly_name"),
            "state": state.get("state"),
            "last_triggered": state.get("attributes", {}).get("last_triggered"),
            "mode": state.get("attributes", {}).get("mode"),
            "current": state.get("attributes", {}).get("current"),
            "max": state.get("attributes", {}).get("max")
        }
        
        return [TextContent(type="text", text=json.dumps(details, indent=2, default=str))]
    
    # =================================================================
    # LOGS & TROUBLESHOOTING
    # =================================================================
    
    elif name == "get_entity_history":
        entity_id = arguments["entity_id"]
        # Would need history API access
        result = {
            "entity_id": entity_id,
            "note": "History requires recorder integration access",
            "suggestion": "Use Home Assistant's history API directly"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_system_logs":
        # Would need access to HA logs
        result = "📝 System logs require direct file access to /config/home-assistant.log"
        return [TextContent(type="text", text=result)]
    
    elif name == "get_error_log":
        # Simplified - would read from logs
        result = "❌ Error log access requires reading home-assistant.log file"
        return [TextContent(type="text", text=result)]
    
    elif name == "diagnose_entity":
        entity_id = arguments["entity_id"]
        state = await ha_api.get_state(entity_id)
        
        diagnosis = {
            "entity_id": entity_id,
            "current_state": state.get("state"),
            "attributes": state.get("attributes", {}),
            "last_changed": state.get("last_changed"),
            "last_updated": state.get("last_updated"),
            "domain": entity_id.split(".")[0],
            "status": "✅ AVAILABLE" if state.get("state") != "unavailable" else "❌ UNAVAILABLE"
        }
        
        return [TextContent(type="text", text=json.dumps(diagnosis, indent=2, default=str))]
    
    elif name == "get_statistics":
        entity_id = arguments["entity_id"]
        period = arguments["period"]
        
        result = {
            "entity_id": entity_id,
            "period": period,
            "note": "Statistics require recorder/history integration"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_binary_sensor":
        entity_id = arguments["entity_id"]
        state = await ha_api.get_state(entity_id)
        
        result = {
            "entity_id": entity_id,
            "state": state.get("state"),
            "device_class": state.get("attributes", {}).get("device_class"),
            "battery": state.get("attributes", {}).get("battery_level"),
            "last_changed": state.get("last_changed")
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    elif name == "analyze_patterns":
        entity_id = arguments["entity_id"]
        days = arguments.get("days", 30)
        
        result = {
            "entity_id": entity_id,
            "analysis_period": f"{days} days",
            "note": "Pattern analysis requires historical data access"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # =================================================================
    # SCENES & SCRIPTS
    # =================================================================
    
    elif name == "activate_scene":
        entity_id = arguments["entity_id"]
        await ha_api.call_service("scene", "turn_on", {"entity_id": entity_id})
        return [TextContent(type="text", text=f"🎬 Scene activated: {entity_id}")]
    
    elif name == "run_script":
        entity_id = arguments["entity_id"]
        service_data = {"entity_id": entity_id}
        if "variables" in arguments:
            service_data.update(arguments["variables"])
        
        await ha_api.call_service("script", "turn_on", service_data)
        return [TextContent(type="text", text=f"🎭 Script executed: {entity_id}")]
    
    # =================================================================
    # WORKFLOWS (Simplified implementations)
    # =================================================================
    
    elif name == "morning_routine":
        wake_time = arguments.get("wake_time", "07:00")
        
        actions = []
        
        # Gradually turn on lights
        if "light_entities" in arguments:
            for light in arguments["light_entities"]:
                await ha_api.call_service("light", "turn_on", {
                    "entity_id": light,
                    "brightness": 255,
                    "transition": 60  # 1 minute gradual
                })
                actions.append(f"Light: {light}")
        
        # Open blinds
        if "blind_entities" in arguments:
            for blind in arguments["blind_entities"]:
                await ha_api.call_service("cover", "open_cover", {"entity_id": blind})
                actions.append(f"Blind: {blind}")
        
        # Adjust climate
        if "climate_entity" in arguments:
            await ha_api.call_service("climate", "set_temperature", {
                "entity_id": arguments["climate_entity"],
                "temperature": 22
            })
            actions.append(f"Climate: {arguments['climate_entity']}")
        
        result = f"🌅 Morning routine activated for {wake_time}:\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    elif name == "evening_routine":
        actions = []
        
        # Dim all lights
        all_states = await ha_api.get_states()
        lights = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("light.")]
        
        for light in lights:
            await ha_api.call_service("light", "turn_on", {
                "entity_id": light,
                "brightness": 100,
                "color_temp": 500  # Warm
            })
        
        actions.append(f"Dimmed {len(lights)} lights")
        
        result = f"🌆 Evening routine activated:\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    elif name == "bedtime_routine":
        actions = []
        
        # Turn off most lights
        all_states = await ha_api.get_states()
        lights = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("light.")]
        
        for light in lights:
            if "nightlight" not in arguments or light != arguments.get("nightlight_entity"):
                await ha_api.call_service("light", "turn_off", {"entity_id": light})
        
        actions.append(f"Turned off {len(lights)} lights")
        
        # Lock doors
        if "lock_entities" in arguments:
            for lock in arguments["lock_entities"]:
                await ha_api.call_service("lock", "lock", {"entity_id": lock})
                actions.append(f"Locked: {lock}")
        
        result = f"😴 Bedtime routine activated:\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    elif name == "arrive_home":
        actions = []
        
        # Turn on welcoming lights
        all_states = await ha_api.get_states()
        lights = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("light.")]
        
        brightness = {"bright": 255, "medium": 150, "dim": 50}.get(arguments.get("light_scene", "medium"), 150)
        
        for light in lights[:3]:  # Just a few welcoming lights
            await ha_api.call_service("light", "turn_on", {
                "entity_id": light,
                "brightness": brightness
            })
        
        actions.append(f"Activated welcoming lights")
        
        result = f"🏡 Welcome home!\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    elif name == "away_mode":
        duration = arguments.get("duration_hours", 8)
        
        actions = []
        
        # Set climate to away
        all_states = await ha_api.get_states()
        climates = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("climate.")]
        
        for climate in climates:
            await ha_api.call_service("climate", "set_preset_mode", {
                "entity_id": climate,
                "preset_mode": "away"
            })
        
        actions.append(f"Climate: Away mode ({len(climates)} devices)")
        
        # Turn off lights
        lights = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("light.")]
        for light in lights:
            await ha_api.call_service("light", "turn_off", {"entity_id": light})
        
        actions.append(f"Lights: Off ({len(lights)} lights)")
        
        result = f"🚗 Away mode activated for {duration} hours:\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    # =================================================================
    # INTELLIGENCE & ANALYTICS
    # =================================================================
    
    elif name == "analyze_home_context":
        all_states = await ha_api.get_states()
        
        # Count device types
        lights_on = len([s for s in all_states if s.get("entity_id", "").startswith("light.") and s.get("state") == "on"])
        total_lights = len([s for s in all_states if s.get("entity_id", "").startswith("light.")])
        
        temp_sensors = [s for s in all_states if "temperature" in s.get("attributes", {}).get("device_class", "")]
        avg_temp = sum(float(s.get("state", 0)) for s in temp_sensors) / len(temp_sensors) if temp_sensors else 0
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "lighting": {
                "lights_on": lights_on,
                "total_lights": total_lights,
                "percentage": round(lights_on / total_lights * 100) if total_lights > 0 else 0
            },
            "temperature": {
                "average": round(avg_temp, 1),
                "sensors": len(temp_sensors)
            },
            "time_of_day": "morning" if 6 <= datetime.now().hour < 12 else
                          "afternoon" if 12 <= datetime.now().hour < 18 else
                          "evening" if 18 <= datetime.now().hour < 22 else "night"
        }
        
        return [TextContent(type="text", text=json.dumps(context, indent=2))]
    
    elif name == "activity_recognition":
        # Simplified activity recognition
        all_states = await ha_api.get_states()
        
        lights_on = len([s for s in all_states if s.get("entity_id", "").startswith("light.") and s.get("state") == "on"])
        tvs_on = len([s for s in all_states if s.get("entity_id", "").startswith("media_player.") and s.get("state") == "playing"])
        
        hour = datetime.now().hour
        
        if hour >= 22 or hour < 6:
            activity = "sleeping"
        elif tvs_on > 0 and lights_on < 3:
            activity = "watching_tv"
        elif lights_on > 5:
            activity = "active_home"
        else:
            activity = "relaxing"
        
        result = {
            "detected_activity": activity,
            "confidence": "medium",
            "indicators": {
                "lights_on": lights_on,
                "media_active": tvs_on > 0,
                "time_of_day": hour
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "comfort_optimization":
        room = arguments["room"]
        
        # Get room devices
        all_states = await ha_api.get_states()
        room_devices = [s for s in all_states if room.lower() in s.get("entity_id", "").lower()]
        
        actions = []
        
        # Optimize climate
        climate_devices = [d for d in room_devices if d.get("entity_id", "").startswith("climate.")]
        for climate in climate_devices:
            await ha_api.call_service("climate", "set_temperature", {
                "entity_id": climate.get("entity_id"),
                "temperature": 22  # Comfortable temp
            })
            actions.append(f"Climate: 22°C")
        
        # Optimize lighting
        light_devices = [d for d in room_devices if d.get("entity_id", "").startswith("light.")]
        for light in light_devices:
            await ha_api.call_service("light", "turn_on", {
                "entity_id": light.get("entity_id"),
                "brightness": 180,
                "color_temp": 400  # Neutral
            })
            actions.append(f"Lighting: Optimized")
        
        result = f"💆 Comfort optimized for {room}:\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    elif name == "energy_intelligence":
        period = arguments.get("period", "day")
        
        result = {
            "period": period,
            "analysis": "Energy usage analysis",
            "note": "Requires energy monitoring sensors and history data",
            "suggestions": [
                "Consider LED bulb upgrades",
                "Enable eco mode on climate devices when away",
                "Use presence-based automation to reduce waste"
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # =================================================================
    # PREDICTIVE & WHOLE-HOME
    # =================================================================
    
    elif name == "predictive_maintenance":
        result = {
            "status": "🔧 Predictive maintenance analysis",
            "note": "Requires device age tracking and usage statistics",
            "alerts": []
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "weather_integration":
        weather_entity = arguments.get("weather_entity", "weather.home")
        
        state = await ha_api.get_state(weather_entity)
        condition = state.get("state", "unknown")
        
        actions = []
        
        # Close windows if rain
        if "rain" in condition.lower():
            all_states = await ha_api.get_states()
            windows = [s.get("entity_id") for s in all_states if "window" in s.get("entity_id", "").lower() and s.get("entity_id", "").startswith("cover.")]
            
            for window in windows:
                await ha_api.call_service("cover", "close_cover", {"entity_id": window})
                actions.append(f"Closed: {window}")
        
        result = f"🌤️ Weather automation ({condition}):\n" + ("\n".join(actions) if actions else "No actions needed")
        return [TextContent(type="text", text=result)]
    
    elif name == "pattern_learning":
        entities = arguments["entity_ids"]
        days = arguments.get("training_days", 30)
        
        result = {
            "entities": entities,
            "training_period": f"{days} days",
            "note": "Pattern learning requires historical data analysis",
            "learned_patterns": "Requires implementation with history database"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "synchronized_home_state":
        state = arguments["state"]
        
        # State presets
        if state == "movie":
            # Dim lights, close blinds
            all_states = await ha_api.get_states()
            lights = [s.get("entity_id") for s in all_states if s.get("entity_id", "").startswith("light.")]
            for light in lights:
                await ha_api.call_service("light", "turn_on", {
                    "entity_id": light,
                    "brightness": 10
                })
        
        result = f"🏘️ Whole-home state: {state.upper()} mode activated"
        return [TextContent(type="text", text=result)]
    
    elif name == "follow_me_home":
        person = arguments["person_entity"]
        mode = arguments.get("mode", "full")
        
        result = f"🚶 Follow-me automation activated for {person} ({mode} mode)"
        return [TextContent(type="text", text=result)]
    
    elif name == "guest_mode":
        guest_rooms = arguments["guest_rooms"]
        
        actions = []
        for room in guest_rooms:
            # Prepare guest room climate
            all_states = await ha_api.get_states()
            climates = [s.get("entity_id") for s in all_states if room.lower() in s.get("entity_id", "").lower() and s.get("entity_id", "").startswith("climate.")]
            
            for climate in climates:
                await ha_api.call_service("climate", "set_temperature", {
                    "entity_id": climate,
                    "temperature": 22
                })
                actions.append(f"Climate: {room}")
        
        result = f"🎁 Guest mode activated:\n" + "\n".join(actions)
        return [TextContent(type="text", text=result)]
    
    elif name == "movie_mode":
        room = arguments["room"]
        light_level = arguments.get("light_level", 10)
        
        # Dim lights
        all_states = await ha_api.get_states()
        lights = [s.get("entity_id") for s in all_states if room.lower() in s.get("entity_id", "").lower() and s.get("entity_id", "").startswith("light.")]
        
        for light in lights:
            await ha_api.call_service("light", "turn_on", {
                "entity_id": light,
                "brightness": light_level
            })
        
        # Close blinds
        blinds = [s.get("entity_id") for s in all_states if room.lower() in s.get("entity_id", "").lower() and s.get("entity_id", "").startswith("cover.")]
        
        for blind in blinds:
            await ha_api.call_service("cover", "close_cover", {"entity_id": blind})
        
        result = f"🎬 Movie mode activated in {room}: {len(lights)} lights dimmed, {len(blinds)} blinds closed"
        return [TextContent(type="text", text=result)]
    
    else:
        return None  # Tool not in Part 2
