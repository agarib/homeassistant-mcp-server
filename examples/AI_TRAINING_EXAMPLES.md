# Home Assistant OpenAPI Server - AI Training Examples

**Version:** 2.0.0  
**Purpose:** Training data for AI models to learn how to control Home Assistant via OpenAPI  
**Base URL:** `http://ha-mcp-server.cluster-services:8001` or `http://192.168.1.203:8001`

---

## 📋 Table of Contents

1. [Device Discovery](#device-discovery)
2. [Light Control](#light-control)
3. [Switch Control](#switch-control)
4. [Climate Control](#climate-control)
5. [Cover Control](#cover-control)
6. [Media & Entertainment](#media--entertainment)
7. [File Operations](#file-operations)
8. [Automation Management](#automation-management)
9. [Scene Management](#scene-management)
10. [Code Execution & Analysis](#code-execution--analysis)
11. [Add-on Management](#add-on-management)
12. [Logs & History](#logs--history)
13. [Dashboard Management](#dashboard-management)
14. [Context-Aware Intelligence](#context-aware-intelligence)
15. [Security & Monitoring](#security--monitoring)
16. [Camera & Vision](#camera--vision)
17. [System Operations](#system-operations)

---

## Device Discovery

### Example 1: Discover All Devices in an Area

**User Request:** "What devices are in the living room?"

**API Call:**

```http
POST /get_area_devices
Content-Type: application/json

{
  "area_name": "living room"
}
```

**Response:**

```json
{
  "area": "living room",
  "devices": [
    {
      "entity_id": "light.couch_light",
      "friendly_name": "Couch Light",
      "state": "on",
      "domain": "light"
    },
    {
      "entity_id": "binary_sensor.living_room_motion",
      "friendly_name": "Living Room Motion",
      "state": "off",
      "domain": "binary_sensor"
    }
  ],
  "count": 2
}
```

**AI Learning:**

- Use `area_name` to search for devices
- Returns all entities with that area name in their friendly_name
- Check `count` to know how many devices were found

---

### Example 2: Discover Devices by Type

**User Request:** "Show me all the lights in the house"

**API Call:**

```http
POST /get_states
Content-Type: application/json

{
  "domain": "light",
  "limit": 50
}
```

**Response:**

```json
{
  "states": [
    {
      "entity_id": "light.couch_light",
      "state": "on",
      "attributes": {
        "friendly_name": "Couch Light",
        "brightness": 255,
        "rgb_color": [255, 200, 100]
      }
    }
  ],
  "count": 15
}
```

**AI Learning:**

- Use `domain` parameter to filter by device type
- Common domains: `light`, `switch`, `climate`, `sensor`, `binary_sensor`, `media_player`, `fan`, `cover`, `vacuum`
- Use `limit` to control response size

---

### Example 3: Get Specific Device State

**User Request:** "Is the couch light on?"

**API Call:**

```http
POST /get_device_state
Content-Type: application/json

{
  "entity_id": "light.couch_light"
}
```

**Response:**

```json
{
  "entity_id": "light.couch_light",
  "state": "on",
  "attributes": {
    "friendly_name": "Couch Light",
    "brightness": 255,
    "supported_color_modes": ["brightness", "rgb"]
  },
  "last_changed": "2025-10-30T19:00:00"
}
```

**AI Learning:**

- Always verify entity_id exists before controlling
- Check `state` field: "on", "off", "unavailable"
- Read `attributes` for device capabilities

---

## Light Control

### Example 4: Turn Light On

**User Request:** "Turn on the couch light"

**API Call:**

```http
POST /control_light
Content-Type: application/json

{
  "entity_id": "light.couch_light",
  "action": "turn_on"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Light turn_on executed successfully",
  "data": []
}
```

**AI Learning:**

- `action` must be: `turn_on`, `turn_off`, or `toggle`
- Always use exact entity_id (e.g., `light.couch_light` not `light.couch`)

---

### Example 5: Dim Light to 50%

**User Request:** "Dim the couch light to 50%"

**API Call:**

```http
POST /control_light
Content-Type: application/json

{
  "entity_id": "light.couch_light",
  "action": "turn_on",
  "brightness": 127
}
```

**AI Learning:**

- Brightness range: 0-255 (0 = 0%, 255 = 100%)
- Calculate: brightness = (percentage / 100) \* 255
- 50% = 127, 75% = 191, 25% = 64

---

### Example 6: Set Light Color to Red

**User Request:** "Make the couch light red"

**API Call:**

```http
POST /control_light
Content-Type: application/json

{
  "entity_id": "light.couch_light",
  "action": "turn_on",
  "rgb_color": [255, 0, 0]
}
```

**Common Colors:**

- Red: `[255, 0, 0]`
- Green: `[0, 255, 0]`
- Blue: `[0, 0, 255]`
- White: `[255, 255, 255]`
- Yellow: `[255, 255, 0]`
- Purple: `[128, 0, 128]`
- Orange: `[255, 165, 0]`

---

### Example 7: Set Warm White

**User Request:** "Set bedroom light to warm white"

**API Call:**

```http
POST /control_light
Content-Type: application/json

{
  "entity_id": "light.bedroom",
  "action": "turn_on",
  "color_temp": 454
}
```

**AI Learning:**

- Color temperature in mireds (micro reciprocal degrees)
- Warm white: 454 (2200K)
- Neutral white: 370 (2700K)
- Cool white: 250 (4000K)
- Daylight: 154 (6500K)

---

### Example 8: Gradual Transition

**User Request:** "Slowly turn on the living room light over 5 seconds"

**API Call:**

```http
POST /control_light
Content-Type: application/json

{
  "entity_id": "light.living_room",
  "action": "turn_on",
  "brightness": 255,
  "transition": 5
}
```

**AI Learning:**

- `transition` is in seconds
- Creates smooth fade effect
- Useful for bedtime/wake-up routines

---

## Switch Control

### Example 9: Turn On Switch

**User Request:** "Turn on the coffee maker"

**API Call:**

```http
POST /control_switch
Content-Type: application/json

{
  "entity_id": "switch.coffee_maker",
  "action": "turn_on"
}
```

---

### Example 10: Toggle Switch

**User Request:** "Toggle the fan"

**API Call:**

```http
POST /control_switch
Content-Type: application/json

{
  "entity_id": "switch.fan",
  "action": "toggle"
}
```

**AI Learning:**

- Switches have 3 actions: `turn_on`, `turn_off`, `toggle`
- Toggle flips current state (on→off, off→on)

---

## Climate Control

### Example 11: Set Temperature

**User Request:** "Set bedroom temperature to 21 degrees"

**API Call:**

```http
POST /control_climate
Content-Type: application/json

{
  "entity_id": "climate.bedroom",
  "action": "set_temperature",
  "temperature": 21
}
```

---

### Example 12: Change HVAC Mode

**User Request:** "Turn on heating in the living room"

**API Call:**

```http
POST /control_climate
Content-Type: application/json

{
  "entity_id": "climate.living_room",
  "action": "set_hvac_mode",
  "hvac_mode": "heat"
}
```

**HVAC Modes:**

- `heat` - Heating only
- `cool` - Cooling only
- `auto` - Auto heat/cool
- `heat_cool` - Both heat and cool
- `off` - Turn off
- `dry` - Dehumidify
- `fan_only` - Fan only

---

## Cover Control

### Example 13: Open Blinds

**User Request:** "Open the bedroom blinds"

**API Call:**

```http
POST /control_cover
Content-Type: application/json

{
  "entity_id": "cover.bedroom_blinds",
  "action": "open_cover"
}
```

---

### Example 14: Set Cover Position

**User Request:** "Set living room blinds to 50%"

**API Call:**

```http
POST /control_cover
Content-Type: application/json

{
  "entity_id": "cover.living_room_blinds",
  "action": "set_cover_position",
  "position": 50
}
```

**AI Learning:**

- Position: 0 = closed, 100 = fully open
- Actions: `open_cover`, `close_cover`, `stop_cover`, `set_cover_position`

---

## Media & Entertainment

### Example 15: Vacuum Control

**User Request:** "Start the vacuum cleaner"

**API Call:**

```http
POST /vacuum_control
Content-Type: application/json

{
  "entity_id": "vacuum.living_room",
  "action": "start"
}
```

**Vacuum Actions:**

- `start` - Start cleaning
- `stop` - Stop cleaning
- `return_to_base` - Return to dock
- `locate` - Play sound to find vacuum

---

### Example 16: Media Player Control

**User Request:** "Play music in the living room and set volume to 50%"

**API Call:**

```http
POST /media_player_control
Content-Type: application/json

{
  "entity_id": "media_player.living_room",
  "action": "volume_set",
  "volume_level": 0.5
}
```

**Media Actions:**

- `turn_on`, `turn_off`
- `media_play`, `media_pause`, `media_stop`
- `media_next_track`, `media_previous_track`
- `volume_up`, `volume_down`, `volume_set`, `volume_mute`

**AI Learning:**

- Volume: 0.0 to 1.0 (0% to 100%)
- 50% = 0.5, 75% = 0.75, 25% = 0.25

---

### Example 17: Get Camera Snapshot

**User Request:** "Show me the front door camera"

**API Call:**

```http
POST /camera_snapshot
Content-Type: application/json

{
  "entity_id": "camera.front_door"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Camera snapshot retrieved",
  "data": {
    "entity_id": "camera.front_door",
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
}
```

**AI Learning:**

- Returns base64-encoded image
- Can be displayed directly in `<img src="data:image/jpeg;base64,..."/>`

---

## File Operations

### Example 18: Read Configuration File

**User Request:** "Show me the contents of configuration.yaml"

**API Call:**

```http
POST /read_file
Content-Type: application/json

{
  "filepath": "configuration.yaml"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "File read successfully",
  "data": {
    "filepath": "configuration.yaml",
    "content": "homeassistant:\n  name: Home\n  latitude: 51.5\n...",
    "size": 1234
  }
}
```

---

### Example 19: Create New Automation File

**User Request:** "Create a new automation file for the bedroom"

**API Call:**

```http
POST /write_file
Content-Type: application/json

{
  "filepath": "packages/bedroom_automations.yaml",
  "content": "automation:\n  - alias: 'Morning Light'\n    trigger:\n      - platform: time\n        at: '07:00:00'\n    action:\n      - service: light.turn_on\n        target:\n          entity_id: light.bedroom\n",
  "backup": true
}
```

**AI Learning:**

- Automatically creates parent directories
- `backup: true` creates timestamped backup before overwriting
- Filepath is relative to `/config/`

---

### Example 20: List Directory Contents

**User Request:** "What files are in the packages folder?"

**API Call:**

```http
POST /list_directory
Content-Type: application/json

{
  "path": "packages"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Directory listed successfully",
  "data": {
    "path": "packages",
    "entries": [
      {
        "name": "bedroom_automations.yaml",
        "type": "file",
        "size": 456,
        "modified": "2025-10-30T10:30:00"
      }
    ]
  }
}
```

---

### Example 21: Search Files for Entity

**User Request:** "Find all files that mention light.couch_light"

**API Call:**

```http
POST /search_files
Content-Type: application/json

{
  "path": "packages",
  "pattern": "light.couch_light",
  "file_pattern": "*.yaml"
}
```

**AI Learning:**

- Searches file contents (not just filenames)
- Use `file_pattern` to filter by extension
- Returns matches with line numbers

---

### Example 22: Move File

**User Request:** "Move old_automation.yaml to archive folder"

**API Call:**

```http
POST /move_file
Content-Type: application/json

{
  "source": "packages/old_automation.yaml",
  "destination": "archive/old_automation.yaml"
}
```

---

## Automation Management

### Example 23: List All Automations

**User Request:** "Show me all automations"

**API Call:**

```http
POST /list_automations
Content-Type: application/json

{}
```

**Response:**

```json
{
  "status": "success",
  "message": "Found 12 automations",
  "data": {
    "automations": [
      {
        "id": "1635789012345",
        "alias": "Morning Routine",
        "state": "on",
        "mode": "single"
      }
    ],
    "count": 12
  }
}
```

---

### Example 24: Trigger Automation

**User Request:** "Run the morning routine automation"

**API Call:**

```http
POST /trigger_automation
Content-Type: application/json

{
  "entity_id": "automation.morning_routine"
}
```

---

### Example 25: Create New Automation

**User Request:** "Create automation to turn on porch light at sunset"

**API Call:**

```http
POST /create_automation
Content-Type: application/json

{
  "automation_config": {
    "alias": "Porch Light at Sunset",
    "trigger": [
      {
        "platform": "sun",
        "event": "sunset"
      }
    ],
    "action": [
      {
        "service": "light.turn_on",
        "target": {
          "entity_id": "light.porch"
        }
      }
    ]
  }
}
```

**AI Learning:**

- Follow Home Assistant YAML automation format
- Common triggers: `time`, `sun`, `state`, `template`, `event`
- Common actions: service calls, delays, conditions

---

### Example 26: Enable/Disable Automation

**User Request:** "Disable the bedtime automation"

**API Call:**

```http
POST /enable_disable_automation
Content-Type: application/json

{
  "entity_id": "automation.bedtime_routine",
  "enable": false
}
```

---

## Scene Management

### Example 27: Create Scene

**User Request:** "Create a movie night scene"

**API Call:**

```http
POST /create_scene
Content-Type: application/json

{
  "scene_name": "Movie Night",
  "entities": {
    "light.living_room": {
      "state": "on",
      "brightness": 30
    },
    "light.couch_light": {
      "state": "on",
      "brightness": 50,
      "rgb_color": [255, 100, 0]
    },
    "media_player.tv": {
      "state": "on"
    }
  }
}
```

---

### Example 28: Activate Scene

**User Request:** "Activate movie night scene"

**API Call:**

```http
POST /activate_scene
Content-Type: application/json

{
  "entity_id": "scene.movie_night"
}
```

---

## Code Execution & Analysis

### Example 29: Execute Python Code

**User Request:** "Calculate average temperature from bedroom sensor over last 24 hours"

**API Call:**

```http
POST /execute_python
Content-Type: application/json

{
  "code": "import pandas as pd\nimport numpy as np\n\n# Sample data\ntemps = [20.5, 21.0, 20.8, 21.2, 20.9]\navg_temp = np.mean(temps)\nprint(f'Average: {avg_temp:.1f}°C')\navg_temp"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Code executed successfully",
  "data": {
    "stdout": "Average: 20.9°C\n",
    "result": 20.88,
    "execution_time": 0.05
  }
}
```

**AI Learning:**

- Available libraries: pandas, numpy, matplotlib, seaborn
- Returns both stdout and final result
- Use for data analysis, calculations, charts

---

### Example 30: Analyze States as DataFrame

**User Request:** "Analyze all temperature sensors"

**API Call:**

```http
POST /analyze_states_dataframe
Content-Type: application/json

{
  "domain": "sensor",
  "attributes_to_include": ["temperature", "unit_of_measurement"]
}
```

**Response:**

```json
{
  "status": "success",
  "message": "States converted to DataFrame",
  "data": {
    "columns": ["entity_id", "state", "temperature", "unit_of_measurement"],
    "row_count": 25,
    "summary": {
      "temperature": {
        "mean": 21.3,
        "min": 18.5,
        "max": 24.2
      }
    }
  }
}
```

---

### Example 31: Plot Sensor History

**User Request:** "Show me a chart of bedroom temperature for the last 24 hours"

**API Call:**

```http
POST /plot_sensor_history
Content-Type: application/json

{
  "entity_id": "sensor.bedroom_temperature",
  "hours": 24,
  "chart_type": "line",
  "title": "Bedroom Temperature (24h)"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Chart generated",
  "data": {
    "chart_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "format": "png"
  }
}
```

**Chart Types:**

- `line` - Line chart
- `bar` - Bar chart
- `scatter` - Scatter plot

---

## Add-on Management

### Example 32: List Add-ons

**User Request:** "What add-ons are installed?"

**API Call:**

```http
POST /list_addons
Content-Type: application/json

{}
```

---

### Example 33: Restart Add-on

**User Request:** "Restart the Zigbee2MQTT add-on"

**API Call:**

```http
POST /restart_addon
Content-Type: application/json

{
  "addon_slug": "45df7312_zigbee2mqtt"
}
```

---

### Example 34: Get Add-on Logs

**User Request:** "Show me the last 50 lines of ESPHome logs"

**API Call:**

```http
POST /get_addon_logs
Content-Type: application/json

{
  "addon_slug": "5c53de3b_esphome",
  "lines": 50
}
```

---

## Logs & History

### Example 35: Get Entity History

**User Request:** "Show me when the front door was opened in the last 24 hours"

**API Call:**

```http
POST /get_entity_history
Content-Type: application/json

{
  "entity_id": "binary_sensor.front_door",
  "start_time": "-24h"
}
```

**AI Learning:**

- Relative times: `-24h`, `-7d`, `-1w`, `-1M`
- Or ISO timestamps: `2025-10-30T00:00:00`

---

### Example 36: Get Error Logs

**User Request:** "Show me recent errors"

**API Call:**

```http
POST /get_error_log
Content-Type: application/json

{
  "lines": 50
}
```

---

### Example 37: Diagnose Entity

**User Request:** "Diagnose why the bedroom light is not responding"

**API Call:**

```http
POST /diagnose_entity
Content-Type: application/json

{
  "entity_id": "light.bedroom"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Entity diagnosis complete",
  "data": {
    "entity_id": "light.bedroom",
    "current_state": "unavailable",
    "last_changed": "2025-10-30T08:00:00",
    "issues": [
      "Entity state is 'unavailable'",
      "No state changes in last 24 hours"
    ],
    "recommendations": [
      "Check device power",
      "Verify network connectivity",
      "Restart integration"
    ]
  }
}
```

---

### Example 38: Get Statistics

**User Request:** "What's the average, min, and max bedroom temperature today?"

**API Call:**

```http
POST /get_statistics
Content-Type: application/json

{
  "entity_id": "sensor.bedroom_temperature",
  "start_time": "-24h"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Statistics calculated",
  "data": {
    "entity_id": "sensor.bedroom_temperature",
    "statistics": {
      "mean": 21.3,
      "median": 21.2,
      "min": 19.5,
      "max": 23.1,
      "std_dev": 0.8
    }
  }
}
```

---

## Dashboard Management

### Example 39: List Dashboards

**User Request:** "Show me all dashboards"

**API Call:**

```http
POST /list_dashboards
Content-Type: application/json

{}
```

---

### Example 40: Create Dashboard

**User Request:** "Create a new dashboard for bedroom controls"

**API Call:**

```http
POST /create_dashboard
Content-Type: application/json

{
  "dashboard_name": "bedroom",
  "title": "Bedroom",
  "icon": "mdi:bed",
  "initial_config": {
    "views": [
      {
        "title": "Overview",
        "cards": []
      }
    ]
  }
}
```

---

### Example 41: Create Button Card

**User Request:** "Add a button card for the bedroom light"

**API Call:**

```http
POST /create_button_card
Content-Type: application/json

{
  "entity_id": "light.bedroom",
  "name": "Bedroom Light",
  "icon": "mdi:lightbulb",
  "tap_action": "toggle"
}
```

---

## Context-Aware Intelligence

### Example 42: Analyze Home Context

**User Request:** "What's the current state of my home?"

**API Call:**

```http
POST /analyze_home_context
Content-Type: application/json

{}
```

**Response:**

```json
{
  "status": "success",
  "message": "Home context analyzed",
  "data": {
    "timestamp": "2025-10-30T19:30:00",
    "occupancy": {
      "total_people": 2,
      "home": 2,
      "away": 0
    },
    "time_context": "evening",
    "active_devices": {
      "lights": 5,
      "switches": 2,
      "total": 7
    },
    "weather": {
      "condition": "clear",
      "temperature": 18,
      "humidity": 65
    }
  }
}
```

---

### Example 43: Activity Recognition

**User Request:** "What activity am I doing right now?"

**API Call:**

```http
POST /activity_recognition
Content-Type: application/json

{
  "rooms": ["living_room", "kitchen"]
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Detected activity: watching_tv",
  "data": {
    "activity": "watching_tv",
    "confidence": 0.85,
    "time_of_day": 19,
    "occupancy": true,
    "factors": {
      "hour": 19,
      "people_home": 2
    }
  }
}
```

**Detected Activities:**

- `sleeping`, `cooking`, `working`, `watching_tv`, `relaxing`, `away`

---

### Example 44: Comfort Optimization

**User Request:** "Optimize comfort in the living room"

**API Call:**

```http
POST /comfort_optimization
Content-Type: application/json

{
  "room": "living_room",
  "preferences": {
    "target_temp": 21,
    "brightness": 80
  }
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Comfort analysis for living_room",
  "data": {
    "room": "living_room",
    "recommendations": [
      {
        "type": "temperature",
        "action": "Adjust climate.living_room to 21°C",
        "current": 23,
        "target": 21
      },
      {
        "type": "lighting",
        "action": "Adjust light.living_room brightness to 80",
        "current": 255,
        "target": 80
      }
    ]
  }
}
```

---

### Example 45: Energy Intelligence

**User Request:** "Analyze my energy usage and suggest savings"

**API Call:**

```http
POST /energy_intelligence
Content-Type: application/json

{
  "period": "day",
  "suggest_savings": true
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Energy analysis for day",
  "data": {
    "period": "day",
    "total_power": 1250.5,
    "sensor_count": 15,
    "top_consumers": [
      {
        "entity_id": "sensor.washer_power",
        "name": "Washing Machine",
        "value": 450,
        "unit": "W"
      }
    ],
    "suggestions": [
      {
        "category": "lighting",
        "suggestion": "Consider turning off unused lights (8 currently on)",
        "potential_saving": "5-10%"
      }
    ]
  }
}
```

---

## Security & Monitoring

### Example 46: Security Monitor

**User Request:** "Monitor my doors and windows for unusual activity"

**API Call:**

```http
POST /intelligent_security_monitor
Content-Type: application/json

{
  "sensor_entities": [
    "binary_sensor.front_door",
    "binary_sensor.back_door",
    "binary_sensor.bedroom_window"
  ],
  "baseline_hours": 24
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Security monitoring: 1 alerts",
  "data": {
    "sensors_monitored": 3,
    "alerts": [
      {
        "severity": "high",
        "sensor": "binary_sensor.back_door",
        "message": "Unusual activity: binary_sensor.back_door active at 3:00",
        "timestamp": "2025-10-30T03:00:00"
      }
    ],
    "risk_score": 20,
    "recommendation": "All clear"
  }
}
```

---

### Example 47: Anomaly Detection

**User Request:** "Check if my power consumption is normal"

**API Call:**

```http
POST /anomaly_detection
Content-Type: application/json

{
  "entity_id": "sensor.power_consumption",
  "baseline_days": 7,
  "sensitivity": "medium"
}
```

---

### Example 48: Vacation Mode

**User Request:** "Activate vacation mode from Nov 1 to Nov 10"

**API Call:**

```http
POST /vacation_mode
Content-Type: application/json

{
  "start_date": "2025-11-01",
  "end_date": "2025-11-10",
  "simulate_presence": true,
  "security_mode": "high"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Vacation mode activated for 9 days",
  "data": {
    "duration_days": 9,
    "actions_taken": [
      {
        "action": "climate_adjustment",
        "message": "Set to energy-saving mode (16°C)"
      },
      {
        "action": "presence_simulation",
        "message": "Will randomly activate 3 lights during evenings"
      }
    ],
    "estimated_savings": "27% energy reduction"
  }
}
```

---

## Camera & Vision

### Example 49: Analyze Camera with VLM

**User Request:** "Is there a package at the front door?"

**API Call:**

```http
POST /analyze_camera_vlm
Content-Type: application/json

{
  "camera_entity_id": "camera.front_door",
  "prompt": "Is there a package at the door?",
  "model": "gpt-4-vision"
}
```

**AI Learning:**

- Requires VLM API integration (OpenAI, Claude, or local)
- Returns natural language analysis of camera image

---

### Example 50: Object Detection

**User Request:** "Detect people and cars in the driveway camera"

**API Call:**

```http
POST /object_detection
Content-Type: application/json

{
  "camera_entity_id": "camera.driveway",
  "object_types": ["person", "car"]
}
```

---

## System Operations

### Example 51: Call Any Service

**User Request:** "Restart the Home Assistant core"

**API Call:**

```http
POST /restart_homeassistant
Content-Type: application/json

{}
```

---

### Example 52: Universal Service Call

**User Request:** "Turn on all lights in the house"

**API Call:**

```http
POST /call_service
Content-Type: application/json

{
  "domain": "light",
  "service": "turn_on",
  "target": {
    "area_id": "all"
  }
}
```

**AI Learning:**

- This is the most flexible endpoint
- Can call ANY Home Assistant service
- Use specific endpoints when available (more user-friendly)

---

## Multi-Step Workflows

### Example 53: Morning Routine

**User Request:** "Execute my morning routine"

**Workflow:**

1. Get current home context

```http
POST /analyze_home_context
```

2. Turn on bedroom lights gradually

```http
POST /control_light
{
  "entity_id": "light.bedroom",
  "action": "turn_on",
  "brightness": 255,
  "transition": 30
}
```

3. Set comfortable temperature

```http
POST /control_climate
{
  "entity_id": "climate.bedroom",
  "action": "set_temperature",
  "temperature": 21
}
```

4. Start coffee maker

```http
POST /control_switch
{
  "entity_id": "switch.coffee_maker",
  "action": "turn_on"
}
```

---

### Example 54: Bedtime Routine

**User Request:** "Prepare the house for bedtime"

**Workflow:**

1. Check all doors/windows

```http
POST /intelligent_security_monitor
{
  "sensor_entities": ["binary_sensor.front_door", "binary_sensor.back_door"]
}
```

2. Turn off all lights except bedroom

```http
POST /call_service
{
  "domain": "light",
  "service": "turn_off",
  "target": {
    "area_id": "all"
  }
}

POST /control_light
{
  "entity_id": "light.bedroom",
  "action": "turn_on",
  "brightness": 50
}
```

3. Lower temperature

```http
POST /control_climate
{
  "entity_id": "climate.bedroom",
  "action": "set_temperature",
  "temperature": 18
}
```

---

## Error Handling Patterns

### Example 55: Handle Unknown Entity

**Bad Request:**

```http
POST /control_light
{
  "entity_id": "light.invalid",
  "action": "turn_on"
}
```

**Response:**

```json
{
  "error": "HTTP error 500: Entity not found"
}
```

**AI Learning:**

- Always verify entity exists with `/get_device_state` first
- Use `/get_area_devices` or `/get_states` to discover valid entity_ids
- Entity IDs follow pattern: `{domain}.{name}` (e.g., `light.bedroom`)

---

### Example 56: Handle Validation Errors

**Bad Request:**

```http
POST /control_light
{
  "entity_id": "light.bedroom",
  "brightness": 300
}
```

**Response:**

```json
{
  "error": "Validation error: brightness must be 0-255"
}
```

**AI Learning:**

- Brightness: 0-255
- Volume: 0.0-1.0
- Cover position: 0-100
- RGB: [0-255, 0-255, 0-255]

---

## Best Practices for AI

### 1. Always Discover Before Controlling

```
User: "Turn on the living room light"

AI Steps:
1. Search for entity: POST /get_area_devices {"area_name": "living room"}
2. Verify entity: POST /get_device_state {"entity_id": "light.living_room"}
3. Control device: POST /control_light {"entity_id": "light.living_room", "action": "turn_on"}
```

### 2. Use Specific Endpoints Over Generic

**Prefer:**

```http
POST /control_light
```

**Over:**

```http
POST /call_service
{
  "domain": "light",
  "service": "turn_on"
}
```

### 3. Handle Percentages Correctly

**Brightness (0-255):**

- User says "50%" → Send `brightness: 127`
- User says "75%" → Send `brightness: 191`

**Volume (0.0-1.0):**

- User says "50%" → Send `volume_level: 0.5`
- User says "75%" → Send `volume_level: 0.75`

### 4. Understand Entity ID Patterns

**Common Patterns:**

- Lights: `light.{location}` or `light.{location}_{fixture}`

  - ✅ `light.bedroom`, `light.couch_light`
  - ❌ `light.bedroom_lamp_1` (might be too specific)

- Switches: `switch.{device}`

  - ✅ `switch.coffee_maker`, `switch.fan`

- Climate: `climate.{location}`
  - ✅ `climate.bedroom`, `climate.living_room`

### 5. Context Awareness

Before executing commands, consider:

- Time of day (morning vs. night brightness)
- Current state (don't turn on if already on)
- User preferences (color temperature, transition times)

### 6. Provide Feedback

After actions:

```
AI: "I've turned on the couch light and set it to 50% brightness with a warm white color."
```

Not just:

```
AI: "Done."
```

---

## Common Use Cases

### Use Case 1: "Goodnight"

1. Turn off all lights except bedroom
2. Set bedroom light to 10% warm
3. Lower temperature to 18°C
4. Lock all doors
5. Arm security system

### Use Case 2: "I'm leaving"

1. Turn off all lights
2. Turn off all switches
3. Set climate to away mode (16°C)
4. Lock doors
5. Arm security

### Use Case 3: "Movie time"

1. Close living room blinds
2. Dim living room lights to 20%
3. Turn on TV
4. Set volume to 40%

### Use Case 4: "Wake me up"

1. Gradual bedroom light (0→100% over 10 min)
2. Increase temperature to 21°C
3. Start coffee maker
4. Open bedroom blinds

---

## Quick Reference

| Task              | Endpoint                | Key Parameters                                         |
| ----------------- | ----------------------- | ------------------------------------------------------ |
| Turn on light     | `/control_light`        | `entity_id`, `action: "turn_on"`, `brightness` (0-255) |
| Set color         | `/control_light`        | `rgb_color: [R, G, B]`                                 |
| Turn on switch    | `/control_switch`       | `entity_id`, `action: "turn_on"`                       |
| Set temperature   | `/control_climate`      | `temperature`, `hvac_mode`                             |
| Open blinds       | `/control_cover`        | `action: "open_cover"`                                 |
| Play media        | `/media_player_control` | `action: "media_play"`, `volume_level`                 |
| Get device state  | `/get_device_state`     | `entity_id`                                            |
| Find devices      | `/get_area_devices`     | `area_name`                                            |
| Read file         | `/read_file`            | `filepath`                                             |
| Create automation | `/create_automation`    | `automation_config`                                    |
| Get history       | `/get_entity_history`   | `entity_id`, `start_time`                              |
| Analyze home      | `/analyze_home_context` | (none)                                                 |

---

## Testing Checklist

✅ Discovered devices before controlling  
✅ Verified entity_id exists  
✅ Used correct brightness scale (0-255)  
✅ Used correct volume scale (0.0-1.0)  
✅ Handled errors gracefully  
✅ Provided clear feedback to user  
✅ Considered time of day and context  
✅ Checked current state before toggling

---

**Version:** 2.0.0  
**Total Endpoints:** 77  
**Last Updated:** October 30, 2025

**Ready for AI Training!** 🚀
