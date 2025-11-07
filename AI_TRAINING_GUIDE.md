# 🤖 AI Training Guide - Home Assistant OpenAPI Server

**Version:** 4.0.1  
**Target Audience:** Cloud AI Assistants (GPT-4, Claude, Gemini, etc.)  
**Total Tools:** 85 unified endpoints  
**Success Rate:** 100% (all tools validated and working)

---

## 📋 Table of Contents

1. [Quick Start for AI Assistants](#quick-start-for-ai-assistants)
2. [Tool Categories Overview](#tool-categories-overview)
3. [Core Capabilities](#core-capabilities)
4. [Advanced Workflows](#advanced-workflows)
5. [Error Handling](#error-handling)
6. [Best Practices](#best-practices)
7. [Complete Tool Reference](#complete-tool-reference)

---

## 🚀 Quick Start for AI Assistants

### Connection Information

- **Base URL:** `http://192.168.1.203:8001` (via MCPO) or direct
- **API Docs:** `http://192.168.1.203:8001/docs`
- **Health Check:** `http://192.168.1.203:8001/health`
- **Authentication:** Handled by MCPO/HA add-on
- **All endpoints:** POST requests (except `/health` and `/`)

### Your First Request

```json
POST /get_persistent_notifications

Response:
{
  "status": "success",
  "message": "Found 0 persistent notifications",
  "data": {
    "notifications": [],
    "count": 0
  }
}
```

### Standard Response Format

**Success:**

```json
{
  "status": "success",
  "message": "Human-readable result",
  "data": {
    "key": "value"
  }
}
```

**Error:**

```json
{
  "detail": "Error description"
}
```

---

## 🗂️ Tool Categories Overview

### 1. Native MCPO Tools (8 tools)

Direct Home Assistant core API access with MCP compatibility.

### 2. System Diagnostics (4 tools)

Monitor HA health, integrations, logs, and errors.

### 3. Device Control (7 tools)

Control lights, switches, climate, covers, vacuum, fans, media players.

### 4. Discovery & State (4 tools)

Find devices, get states, explore areas.

### 5. Automations (7 tools)

Create, update, trigger, enable/disable automations.

### 6. File Operations (9 tools)

Read/write /config files, manage YAML, search, tree.

### 7. Add-on Management (9 tools)

Install, start, stop, restart HA add-ons.

### 8. Dashboards (8 tools)

Manage Lovelace dashboards, create cards.

### 9. Logs & History (6 tools)

Entity history, diagnostics, statistics.

### 10. Scenes (3 tools)

Activate, create, list scenes.

### 11. Security (3 tools)

Monitoring, anomaly detection, vacation mode.

### 12. Camera VLM (3 tools)

Vision AI analysis of camera feeds.

### 13. Code Execution (3 tools)

Python sandbox, pandas, matplotlib.

### 14. Intelligence (4 tools)

Context analysis, activity recognition, comfort optimization.

### 15. Utility (2 tools)

Health check, API info.

---

## 🎯 Core Capabilities

### Capability 1: Home Monitoring

**What you can do:**

- Check integration health
- See persistent error notifications
- Monitor system logs
- Diagnose startup issues

**Tools to use:**

1. `get_persistent_notifications` - See integration errors
2. `get_integration_status` - Check if integrations are loaded
3. `get_system_logs_diagnostics` - Read recent events
4. `get_startup_errors` - Find startup problems

**Example Workflow:**

```
User: "Are there any errors in my Home Assistant?"

Step 1: Check notifications
POST /get_persistent_notifications
→ Returns: 0 notifications (clean!)

Step 2: Check integration status
POST /get_integration_status
Body: {"integration": "hue"}
→ Returns: loaded=true, 15 entities

AI Response: "Your system is healthy! No errors found.
Hue integration is working with 15 devices."
```

### Capability 2: Device Discovery

**What you can do:**

- Find all devices by type
- Get devices in specific rooms
- Check current states

**Tools to use:**

1. `discover_devices` - Find by domain (light, switch, sensor, etc.)
2. `get_area_devices` - Find by room/area
3. `list_entities_native` - List all entities with filtering
4. `get_entity_state_native` - Get specific entity state

**Example Workflow:**

```
User: "What lights are in my living room?"

Step 1: Get area devices
POST /get_area_devices
Body: {"area_name": "living room"}
→ Returns: light.couch_light, light.tv_light, etc.

Step 2: Get states
POST /get_entity_state_native
Body: {"entity_id": "light.couch_light"}
→ Returns: state="on", brightness=150

AI Response: "You have 3 lights in the living room:
- Couch light: ON (brightness 150/255)
- TV light: OFF
- Floor lamp: ON (brightness 200/255)"
```

### Capability 3: Device Control

**What you can do:**

- Turn lights on/off, set brightness/color
- Control switches
- Adjust climate (temperature, mode)
- Open/close covers
- Control vacuum cleaners
- Adjust fans
- Control media players

**Tools to use:**

1. `control_light` - Full light control
2. `control_switch` - Switch on/off/toggle
3. `control_climate` - HVAC control
4. `control_cover` - Blinds/shades
5. `vacuum_control` - Vacuum operations
6. `fan_control` - Fan speed/oscillation
7. `media_player_control` - Media playback

**Example Workflow:**

```
User: "Turn on the living room lights to 50% brightness"

POST /control_light
Body: {
  "entity_id": "light.living_room",
  "action": "turn_on",
  "brightness": 128
}
→ Returns: success

AI Response: "Living room lights set to 50% brightness ✓"
```

### Capability 4: Automation Management

**What you can do:**

- List all automations
- Create new automations
- Trigger automations manually
- Enable/disable automations
- Update existing automations
- Delete automations

**Tools to use:**

1. `list_automations` - See all automations
2. `create_automation` - Create from YAML
3. `trigger_automation` - Manual trigger
4. `enable_disable_automation` - Toggle automation
5. `update_automation` - Modify existing
6. `delete_automation` - Remove automation
7. `get_automation_details` - Get full config

**Example Workflow:**

```
User: "Create an automation to turn on porch light at sunset"

POST /create_automation
Body: {
  "alias": "Porch Light at Sunset",
  "trigger": [{
    "platform": "sun",
    "event": "sunset"
  }],
  "action": [{
    "service": "light.turn_on",
    "target": {"entity_id": "light.porch"}
  }]
}
→ Returns: automation created

AI Response: "Automation created! Your porch light will
turn on automatically at sunset every day."
```

### Capability 5: Scene Management

**What you can do:**

- Activate predefined scenes
- Create new scenes
- List available scenes

**Tools to use:**

1. `activate_scene` - Trigger a scene
2. `create_scene` - Define new scene
3. `list_scenes` - See all scenes

**Example Workflow:**

```
User: "Activate movie mode"

POST /activate_scene
Body: {"entity_id": "scene.movie_time"}
→ Returns: scene activated

AI Response: "Movie mode activated!
Lights dimmed, blinds closed ✓"
```

### Capability 6: File Operations

**What you can do:**

- Read configuration files
- Write new configurations
- Search file contents
- Get directory tree
- Copy/move files
- Create directories

**Tools to use:**

1. `read_file` - Read from /config
2. `write_file` - Write to /config
3. `list_directory` - List contents
4. `search_files` - Search by pattern
5. `get_directory_tree` - Full tree view
6. `copy_file` - Copy files
7. `move_file` - Move/rename
8. `create_directory` - Make directories
9. `delete_file` - Remove files

**Example Workflow:**

```
User: "Show me my automations.yaml file"

POST /read_file
Body: {"file_path": "automations.yaml"}
→ Returns: file contents

AI Response: "Here are your automations:
[displays YAML content with syntax highlighting]"
```

### Capability 7: System Intelligence

**What you can do:**

- Analyze home context
- Recognize activities
- Optimize comfort
- Analyze energy usage

**Tools to use:**

1. `analyze_home_context` - Full home analysis
2. `activity_recognition` - Detect current activity
3. `comfort_optimization` - Optimize settings
4. `energy_intelligence` - Energy insights

**Example Workflow:**

```
User: "What's happening at home right now?"

POST /analyze_home_context
Body: {}
→ Returns: occupancy, activity, weather, devices on, etc.

AI Response: "Home analysis:
- 2 people home (living room, bedroom)
- Activity: Watching TV
- Temperature: 21°C (comfortable)
- 8 lights on, consuming 120W
- All doors/windows closed"
```

---

## 🔄 Advanced Workflows

### Workflow 1: Morning Routine

```
User: "Set up my morning routine"

Tools needed:
1. create_automation (sunrise trigger)
2. create_scene (morning lights)
3. control_climate (warm up)

Steps:
1. Create scene for morning lighting
2. Create automation to trigger at sunrise
3. Adjust climate 30 min before wake time
```

### Workflow 2: Security Check

```
User: "Is my home secure?"

Tools needed:
1. list_entities_native (domain: binary_sensor)
2. get_entity_state_native (for each door/window)
3. get_persistent_notifications (errors)

Steps:
1. Find all door/window sensors
2. Check each sensor state
3. Check for security system errors
4. Report: "All 5 doors closed, 8 windows closed, alarm armed"
```

### Workflow 3: Energy Optimization

```
User: "How can I save energy?"

Tools needed:
1. energy_intelligence
2. get_statistics (for power sensors)
3. list_entities_native (domain: light)
4. discover_devices (domain: climate)

Steps:
1. Analyze current energy usage
2. Identify high-consumption devices
3. Suggest automations for optimization
```

### Workflow 4: Troubleshooting Integration

```
User: "My LG washing machine isn't working"

Tools needed:
1. get_persistent_notifications
2. get_integration_status (integration: lg)
3. get_system_logs_diagnostics (level: ERROR)
4. diagnose_entity (washing machine entity)

Steps:
1. Check for LG integration errors
2. Verify integration is loaded
3. Read recent error logs
4. Check entity state and attributes
5. Provide diagnosis and fix steps
```

---

## ⚠️ Error Handling

### Common Errors and Solutions

#### Error: 404 Not Found

```json
{ "detail": "Entity not found" }
```

**Cause:** Entity ID doesn't exist  
**Solution:** Use `list_entities_native` or `discover_devices` to find correct entity ID

#### Error: 500 Internal Server Error

```json
{ "detail": "Service call failed" }
```

**Cause:** Invalid parameters or service unavailable  
**Solution:** Check entity state and valid actions with `get_entity_state_native`

#### Error: Invalid Action

```json
{ "detail": "Invalid action 'toggle' for light" }
```

**Cause:** Action not supported for this entity  
**Solution:** Use valid actions: turn_on, turn_off (avoid toggle for lights)

### Validation Before Action

**Always check before controlling:**

```
1. Does entity exist? → list_entities_native
2. What's current state? → get_entity_state_native
3. What actions are valid? → get_services_native
4. Are there errors? → get_persistent_notifications
```

---

## ✅ Best Practices

### 1. **Always Verify Before Acting**

```
❌ BAD: Assume entity exists
POST /control_light {"entity_id": "light.unknown"}

✅ GOOD: Discover first
POST /discover_devices {"domain": "light"}
Then control found entities
```

### 2. **Use Friendly Names**

```
User: "Turn on living room light"

Step 1: Find entity
POST /get_area_devices {"area_name": "living room"}
→ Find: light.living_room_main

Step 2: Control it
POST /control_light {"entity_id": "light.living_room_main", "action": "turn_on"}
```

### 3. **Provide Context in Responses**

```
❌ BAD: "Done"

✅ GOOD: "Living room light turned on to 100% brightness.
Current state: ON, brightness 255/255, color: warm white"
```

### 4. **Handle Partial Success**

```
User: "Turn off all bedroom lights"

Results:
- light.bedroom_main: ✓ OFF
- light.bedroom_side: ✓ OFF
- light.bedroom_closet: ❌ Unavailable

Response: "2 of 3 bedroom lights turned off successfully.
Closet light is currently unavailable (check connection)."
```

### 5. **Suggest Automations**

```
User: "I always forget to turn off the porch light"

Response: "I can create an automation to turn it off
automatically. Would you like to:
1. Turn off at sunrise
2. Turn off at midnight
3. Turn off 30 minutes after turning on"
```

### 6. **Check for Conflicts**

```
User: "Create automation to turn on AC at 6 PM"

Before creating:
1. Check existing automations → list_automations
2. Look for conflicting schedules
3. Warn: "You already have an automation that turns
   off AC at 6 PM. Should I disable it first?"
```

---

## 📚 Complete Tool Reference

### Category: Native MCPO Tools (8)

#### 1. `get_entity_state_native`

**Purpose:** Get entity state and all attributes  
**Input:** `{"entity_id": "light.living_room"}`  
**Output:** Full state object with attributes  
**Use when:** Need detailed entity information

#### 2. `list_entities_native`

**Purpose:** List entities with optional domain filter  
**Input:** `{"domain": "light"}` (optional)  
**Output:** Array of all entities  
**Use when:** Discovering available devices

#### 3. `get_services_native`

**Purpose:** List all available HA services  
**Input:** `{}`  
**Output:** All services by domain  
**Use when:** Need to know what services exist

#### 4. `fire_event_native`

**Purpose:** Fire custom HA events  
**Input:** `{"event_type": "my_event", "event_data": {}}`  
**Output:** Event fired confirmation  
**Use when:** Triggering custom integrations

#### 5. `render_template_native`

**Purpose:** Render Jinja2 templates  
**Input:** `{"template": "{{ states('sensor.temp') }}"}`  
**Output:** Rendered result  
**Use when:** Dynamic value calculations

#### 6. `get_config_native`

**Purpose:** Get HA system configuration  
**Input:** `{}`  
**Output:** Full HA config (version, location, components)  
**Use when:** Need system information

#### 7. `get_history_native`

**Purpose:** Get entity state history  
**Input:** `{"entity_id": "sensor.temp", "hours": 24}`  
**Output:** Historical state changes  
**Use when:** Analyzing trends

#### 8. `get_logbook_native`

**Purpose:** Get logbook entries  
**Input:** `{"hours": 24}`  
**Output:** Recent events  
**Use when:** Reviewing recent activity

---

### Category: System Diagnostics (4)

#### 9. `get_persistent_notifications`

**Purpose:** See integration errors and warnings  
**Input:** `{}`  
**Output:** All persistent notifications  
**Use when:** Checking for system errors  
**Example:**

```json
Response: {
  "status": "success",
  "data": {
    "notifications": [
      {
        "notification_id": "config_entry_reconfigure",
        "title": "LG ThinQ",
        "message": "Authentication failed - please reconfigure"
      }
    ],
    "count": 1
  }
}
```

#### 10. `get_integration_status`

**Purpose:** Check if integration is loaded and working  
**Input:** `{"integration": "hue"}` (optional)  
**Output:** Loaded components and entity count  
**Use when:** Diagnosing integration issues  
**Example:**

```json
Response: {
  "status": "success",
  "data": {
    "integration": "hue",
    "loaded": true,
    "matching_components": ["hue", "hue.light", "hue.sensor"],
    "entity_count": 15
  }
}
```

#### 11. `get_system_logs_diagnostics`

**Purpose:** Read recent system events  
**Input:** `{"lines": 50, "level": "ERROR"}`  
**Output:** Logbook entries (filtered)  
**Use when:** Debugging errors  
**Note:** Uses logbook API, not raw logs

#### 12. `get_startup_errors`

**Purpose:** Find startup and initialization errors  
**Input:** `{}`  
**Output:** Persistent notifications + recent startup events  
**Use when:** HA restart troubleshooting

---

### Category: Device Control (7)

#### 13. `control_light`

**Purpose:** Full light control  
**Input:**

```json
{
  "entity_id": "light.living_room",
  "action": "turn_on",
  "brightness": 200,
  "rgb_color": [255, 0, 0],
  "color_temp": 400
}
```

**Actions:** turn_on, turn_off  
**Optional params:** brightness (0-255), rgb_color, kelvin, color_temp

#### 14. `control_switch`

**Purpose:** Switch on/off  
**Input:** `{"entity_id": "switch.fan", "action": "turn_on"}`  
**Actions:** turn_on, turn_off, toggle

#### 15. `control_climate`

**Purpose:** HVAC control  
**Input:**

```json
{
  "entity_id": "climate.living_room",
  "action": "set_temperature",
  "temperature": 22,
  "hvac_mode": "heat"
}
```

**Actions:** set_temperature, set_hvac_mode  
**HVAC modes:** heat, cool, auto, off, fan_only, dry

#### 16. `control_cover`

**Purpose:** Blinds/shades control  
**Input:** `{"entity_id": "cover.blinds", "action": "open"}`  
**Actions:** open, close, set_position  
**Position:** 0-100 (0=closed, 100=open)

#### 17. `vacuum_control`

**Purpose:** Vacuum cleaner operations  
**Input:** `{"entity_id": "vacuum.roomba", "action": "start"}`  
**Actions:** start, pause, stop, return_to_base

#### 18. `fan_control`

**Purpose:** Fan speed and oscillation  
**Input:**

```json
{
  "entity_id": "fan.bedroom",
  "action": "turn_on",
  "speed": 50,
  "oscillate": true
}
```

**Actions:** turn_on, turn_off  
**Speed:** 0-100 percentage

#### 19. `media_player_control`

**Purpose:** Media playback control  
**Input:**

```json
{
  "entity_id": "media_player.living_room_tv",
  "action": "play",
  "volume_level": 0.5
}
```

**Actions:** play, pause, stop, volume_up, volume_down, next, previous

---

### Category: Discovery & State (4)

#### 20. `discover_devices`

**Purpose:** Find devices by domain  
**Input:** `{"domain": "light", "area": "living room"}`  
**Output:** Filtered device list

#### 21. `get_device_state`

**Purpose:** Get specific entity state  
**Input:** `{"entity_id": "sensor.temperature"}`  
**Output:** Current state and attributes

#### 22. `get_area_devices`

**Purpose:** Get all devices in an area  
**Input:** `{"area_name": "bedroom"}`  
**Output:** All entities in that area

#### 23. `get_states`

**Purpose:** Get all entity states  
**Input:** `{"domain": "sensor"}` (optional filter)  
**Output:** Array of all states

---

### Category: Automations (7)

#### 24. `list_automations`

**Purpose:** List all automations  
**Input:** `{}`  
**Output:** All automation entities with states

#### 25. `trigger_automation`

**Purpose:** Manually trigger automation  
**Input:** `{"entity_id": "automation.morning_lights"}`  
**Use:** Testing or manual execution

#### 26. `create_automation`

**Purpose:** Create new automation from YAML  
**Input:**

```json
{
  "alias": "Porch Light at Sunset",
  "trigger": [{ "platform": "sun", "event": "sunset" }],
  "action": [
    {
      "service": "light.turn_on",
      "target": { "entity_id": "light.porch" }
    }
  ]
}
```

**Trigger types:** time, state, numeric_state, sun, event, webhook  
**Condition types:** state, numeric_state, time, sun, zone  
**Action types:** service, scene, delay, wait, choose, repeat

#### 27. `update_automation`

**Purpose:** Modify existing automation  
**Input:** `{"entity_id": "automation.test", "alias": "New Name"}`

#### 28. `delete_automation`

**Purpose:** Remove automation  
**Input:** `{"entity_id": "automation.old", "confirm": true}`  
**WARNING:** Cannot be undone

#### 29. `get_automation_details`

**Purpose:** Get full automation config  
**Input:** `{"entity_id": "automation.morning"}`  
**Output:** Complete YAML definition

#### 30. `enable_disable_automation`

**Purpose:** Toggle automation on/off  
**Input:** `{"entity_id": "automation.test", "action": "disable"}`  
**Actions:** enable, disable

---

### Category: File Operations (9)

#### 31. `read_file`

**Purpose:** Read file from /config  
**Input:** `{"file_path": "automations.yaml"}`  
**Output:** File contents as string

#### 32. `write_file`

**Purpose:** Write file to /config  
**Input:** `{"file_path": "test.txt", "content": "Hello"}`  
**WARNING:** Overwrites existing files

#### 33. `list_directory`

**Purpose:** List directory contents  
**Input:** `{"directory_path": "."}`  
**Output:** Files and subdirectories

#### 34. `delete_file`

**Purpose:** Delete file  
**Input:** `{"file_path": "old.yaml", "confirm": true}`  
**WARNING:** Cannot be undone

#### 35. `create_directory`

**Purpose:** Create directory  
**Input:** `{"directory_path": "custom_automations"}`

#### 36. `move_file`

**Purpose:** Move or rename file  
**Input:** `{"source": "old.yaml", "destination": "new.yaml"}`

#### 37. `copy_file`

**Purpose:** Copy file  
**Input:** `{"source": "template.yaml", "destination": "copy.yaml"}`

#### 38. `search_files`

**Purpose:** Search file contents  
**Input:** `{"pattern": "sensor.temperature", "directory": "."}`  
**Output:** Matching files and line numbers

#### 39. `get_directory_tree`

**Purpose:** Get full directory tree  
**Input:** `{"directory_path": ".", "max_depth": 3}`  
**Output:** Nested tree structure

---

### Category: Add-on Management (9)

**Note:** Requires admin token for full functionality. 76/85 tools work with SUPERVISOR_TOKEN only.

#### 40. `list_addons`

**Purpose:** List all HA add-ons  
**Input:** `{}`  
**Output:** All add-ons with states

#### 41. `get_addon_info`

**Purpose:** Get add-on details  
**Input:** `{"addon_id": "core_ssh"}`

#### 42. `start_addon`

**Purpose:** Start add-on  
**Input:** `{"addon_id": "core_ssh"}`

#### 43. `stop_addon`

**Purpose:** Stop add-on  
**Input:** `{"addon_id": "core_ssh"}`

#### 44. `restart_addon`

**Purpose:** Restart add-on  
**Input:** `{"addon_id": "core_ssh"}`

#### 45. `install_addon`

**Purpose:** Install new add-on  
**Input:** `{"addon_id": "core_ssh", "repository": "official"}`

#### 46. `uninstall_addon`

**Purpose:** Remove add-on  
**Input:** `{"addon_id": "core_ssh"}`

#### 47. `update_addon`

**Purpose:** Update add-on  
**Input:** `{"addon_id": "core_ssh", "version": "latest"}`

#### 48. `get_addon_logs`

**Purpose:** Get add-on logs  
**Input:** `{"addon_id": "core_ssh"}`

---

### Category: Dashboards (8)

#### 49. `list_dashboards`

**Purpose:** List all Lovelace dashboards  
**Input:** `{}`

#### 50. `get_dashboard_config`

**Purpose:** Get dashboard YAML  
**Input:** `{"dashboard_id": "lovelace"}`

#### 51. `create_dashboard`

**Purpose:** Create new dashboard  
**Input:** `{"url_path": "mobile", "title": "Mobile View"}`

#### 52. `update_dashboard_config`

**Purpose:** Update dashboard YAML  
**Input:** `{"dashboard_id": "lovelace", "config": {...}}`

#### 53. `delete_dashboard`

**Purpose:** Delete dashboard  
**Input:** `{"dashboard_id": "mobile"}`

#### 54. `list_hacs_cards`

**Purpose:** List custom HACS cards  
**Input:** `{}`

#### 55. `create_button_card`

**Purpose:** Create HACS button card  
**Input:** See API docs for card schema

#### 56. `create_mushroom_card`

**Purpose:** Create HACS mushroom card  
**Input:** See API docs for card schema

---

### Category: Logs & History (6)

#### 57. `get_entity_history`

**Purpose:** Get entity state history  
**Input:** `{"entity_id": "sensor.temp", "start_time": "-24h"}`  
**Output:** State changes over time

#### 58. `get_system_logs`

**Purpose:** System logs (alternative to diagnostics version)  
**Input:** `{"severity": "error", "limit": 50}`

#### 59. `get_error_log`

**Purpose:** Quick error summary  
**Input:** `{"limit": 20}`

#### 60. `diagnose_entity`

**Purpose:** Comprehensive entity diagnostics  
**Input:** `{"entity_id": "light.broken", "include_history": true}`  
**Output:** State, attributes, history, related automations

#### 61. `get_statistics`

**Purpose:** Statistical analysis  
**Input:** `{"entity_id": "sensor.power", "period": "day"}`  
**Output:** Min, max, mean, sum values

#### 62. `get_binary_sensor`

**Purpose:** Binary sensor inspector  
**Input:** `{"entity_id": "binary_sensor.door"}`  
**Output:** on/off state with attributes

---

### Category: Scenes (3)

#### 63. `activate_scene`

**Purpose:** Trigger a scene  
**Input:** `{"entity_id": "scene.movie_time"}`

#### 64. `create_scene`

**Purpose:** Create new scene  
**Input:** `{"name": "Reading", "entities": {...}}`

#### 65. `list_scenes`

**Purpose:** List all scenes  
**Input:** `{}`

---

### Category: Security (3)

#### 66. `intelligent_security_monitor`

**Purpose:** AI security monitoring  
**Input:** `{"sensor_entities": ["binary_sensor.door_front"]}`  
**Output:** Security status and anomalies

#### 67. `anomaly_detection`

**Purpose:** Detect unusual patterns  
**Input:** `{"entity_id": "sensor.power", "baseline_days": 7}`

#### 68. `vacation_mode`

**Purpose:** Vacation settings  
**Input:** `{"start_date": "2025-12-01", "end_date": "2025-12-10"}`

---

### Category: Camera VLM (3)

#### 69. `analyze_camera_vlm`

**Purpose:** Vision AI analysis  
**Input:** `{"camera_entity": "camera.front_door", "prompt": "Describe"}`

#### 70. `object_detection`

**Purpose:** Detect objects  
**Input:** `{"camera_entity": "camera.driveway"}`

#### 71. `facial_recognition`

**Purpose:** Recognize faces  
**Input:** `{"camera_entity": "camera.entrance"}`

---

### Category: Code Execution (3)

#### 72. `execute_python`

**Purpose:** Run Python code  
**Input:** `{"code": "import pandas as pd; print(pd.__version__)"}`  
**WARNING:** Sandboxed execution

#### 73. `analyze_states_dataframe`

**Purpose:** Get states as pandas DataFrame  
**Input:** `{"domain": "sensor"}`

#### 74. `plot_sensor_history`

**Purpose:** Create matplotlib charts  
**Input:** `{"entity_id": "sensor.temp", "hours": 24}`

---

### Category: Intelligence (4)

#### 75. `analyze_home_context`

**Purpose:** Full home analysis  
**Input:** `{}`  
**Output:** Occupancy, activity, weather, devices

#### 76. `activity_recognition`

**Purpose:** AI activity detection  
**Input:** `{"rooms": ["living_room"]}`  
**Output:** Current activity (watching TV, cooking, etc.)

#### 77. `comfort_optimization`

**Purpose:** Multi-factor comfort  
**Input:** `{"room": "bedroom"}`  
**Output:** Optimized temperature, lighting, air quality

#### 78. `energy_intelligence`

**Purpose:** Energy analysis  
**Input:** `{"period": "week"}`  
**Output:** Usage stats and savings suggestions

---

### Category: System (2)

#### 79. `restart_homeassistant`

**Purpose:** Restart HA core  
**Input:** `{"confirm": true}`  
**WARNING:** Causes brief downtime

#### 80. `call_service`

**Purpose:** Call any HA service  
**Input:** `{"domain": "notify", "service": "mobile_app", "data": {...}}`  
**Use:** For services without dedicated endpoint

---

### Category: Utility (2)

#### 81. `camera_snapshot`

**Purpose:** Get camera image  
**Input:** `{"entity_id": "camera.front_door"}`  
**Output:** Base64 encoded image

---

### Additional Tools (4)

The remaining tools (82-85) include specialized functions for:

- Multi-room coordination
- Predictive analytics
- Whole-home state management
- Advanced workflows

Refer to `/docs` endpoint for complete schemas.

---

## 🎓 Training Scenarios

### Scenario 1: New User Onboarding

**User:** "I just set up Home Assistant. What can you do?"

**AI Response:**

```
I can help you control and automate your home! Let me scan
your setup...

[Calls: get_config_native, list_entities_native]

I found:
- 15 lights in 5 rooms
- 3 switches (fan, coffee maker, TV plug)
- 1 thermostat
- 2 door sensors
- Weather integration

What would you like to do?
1. Turn on/off devices by voice
2. Create automations (lights at sunset, etc.)
3. Set up scenes (movie mode, bedtime, etc.)
4. Monitor security (doors, motion)
```

### Scenario 2: Troubleshooting

**User:** "My Hue lights aren't working"

**AI Workflow:**

```
1. Check for errors
   [get_persistent_notifications]
   → Found: "Hue Bridge connection timeout"

2. Check integration status
   [get_integration_status: "hue"]
   → loaded=false

3. Get recent logs
   [get_system_logs_diagnostics: level="ERROR"]
   → Multiple Hue connection failures

4. Diagnose entities
   [list_entities_native: domain="light"]
   → All hue.* entities unavailable

Response: "Your Hue Bridge lost connection.
Possible fixes:
1. Check bridge power and network
2. Restart Hue Bridge
3. Reload integration in HA
4. Reconfigure if needed"
```

### Scenario 3: Energy Optimization

**User:** "My electricity bill is high. Help me save energy."

**AI Workflow:**

```
1. Analyze energy usage
   [energy_intelligence: period="month"]
   → High consumption devices identified

2. Get statistics
   [get_statistics: entity="sensor.total_power", period="day"]
   → Peak usage: 6-8 PM (3.5 kW)

3. List devices
   [discover_devices: domain="light"]
   → 20 lights, 12 currently on

4. Suggest automations
   Response: "Energy saving suggestions:

   1. Turn off lights when not needed
      - 8 lights on in empty rooms
      - Savings: ~$15/month

   2. Schedule thermostat
      - Lower temp 2°C at night
      - Savings: ~$30/month

   3. Power down devices
      - TV, computer on standby 24/7
      - Savings: ~$10/month

   Would you like me to create automations for these?"
```

### Scenario 4: Complex Automation

**User:** "Make my home welcome me when I arrive"

**AI Workflow:**

```
1. Discover person tracking
   [list_entities_native: domain="person"]
   → Found: person.john

2. Discover devices to control
   [get_area_devices: area="living_room"]
   → Lights, thermostat, media_player

3. Create multi-trigger automation
   [create_automation: {
     alias: "Welcome Home",
     trigger: [{
       platform: "state",
       entity_id: "person.john",
       to: "home"
     }],
     condition: [{
       condition: "sun",
       after: "sunset"
     }],
     action: [
       {service: "light.turn_on", target: {entity_id: "light.entrance"}},
       {service: "climate.set_temperature", data: {temperature: 22}},
       {service: "scene.turn_on", target: {entity_id: "scene.welcome"}}
     ]
   }]

Response: "Welcome home automation created!
When you arrive after sunset:
✓ Entrance light turns on
✓ Thermostat warms to 22°C
✓ Welcome scene activates

Would you like to customize this further?"
```

---

## 🔍 Debugging Guide for AI

### When Tool Fails

1. **Check entity exists:**

   ```
   POST /list_entities_native
   Body: {"domain": "light"}
   ```

2. **Check current state:**

   ```
   POST /get_entity_state_native
   Body: {"entity_id": "light.problematic"}
   ```

3. **Check for errors:**

   ```
   POST /get_persistent_notifications
   Body: {}
   ```

4. **Check integration:**

   ```
   POST /get_integration_status
   Body: {"integration": "hue"}
   ```

5. **Read logs:**
   ```
   POST /get_system_logs_diagnostics
   Body: {"lines": 50, "level": "ERROR"}
   ```

### Common Fixes

**Problem:** "Entity not found"  
**Fix:** User may use friendly name, translate to entity_id:

```
User says: "living room light"
→ Search: get_area_devices(area="living room", domain="light")
→ Find: light.living_room_main
→ Use that entity_id
```

**Problem:** "Service call failed"  
**Fix:** Check valid actions:

```
POST /get_services_native
→ See what services are available for that domain
```

**Problem:** "Integration not responding"  
**Fix:** Check integration health:

```
POST /get_integration_status
→ If loaded=false, suggest reload/reconfigure
```

---

## 📊 Success Metrics

### How to Know You're Doing Well

1. **Response Time:** <2 seconds for simple commands
2. **Success Rate:** >95% for valid requests
3. **User Clarity:** Responses understood without follow-up
4. **Proactive:** Suggest automations before user asks
5. **Error Recovery:** Graceful fallback when tools fail

### Example Good Interaction

```
User: "Turn on bedroom"

AI: [Searches for bedroom lights]
    [Finds: light.bedroom_main, light.bedroom_side]
    [Turns both on]

Response: "Bedroom lights turned on ✓
- Main light: 100% brightness
- Side lamp: 50% brightness
Would you like me to adjust the brightness?"

Rating: ⭐⭐⭐⭐⭐
- Found all relevant lights
- Controlled both
- Provided status
- Offered next step
```

### Example Poor Interaction

```
User: "Turn on bedroom"

AI: [Assumes entity_id without checking]
    POST /control_light {"entity_id": "light.bedroom"}
    → Error: Entity not found

Response: "Error: Entity not found"

Rating: ⭐
- Didn't discover entities
- No error recovery
- Unhelpful response
```

---

## 🚀 Quick Reference Card

### Most Used Tools (Top 20)

1. `get_entity_state_native` - Get any entity state
2. `list_entities_native` - Find all entities
3. `control_light` - Light control
4. `control_switch` - Switch control
5. `get_area_devices` - Devices by room
6. `activate_scene` - Trigger scenes
7. `list_automations` - See automations
8. `create_automation` - Make automations
9. `get_persistent_notifications` - Check errors
10. `get_integration_status` - Integration health
11. `discover_devices` - Find by type
12. `control_climate` - HVAC control
13. `get_services_native` - Available services
14. `trigger_automation` - Run automation
15. `get_system_logs_diagnostics` - Read logs
16. `read_file` - Read configs
17. `get_entity_history` - Historical data
18. `get_config_native` - System info
19. `call_service` - Any service
20. `analyze_home_context` - Home analysis

### Decision Tree

```
User Request
    │
    ├─ "Turn on X"
    │   └─ control_light / control_switch / control_climate
    │
    ├─ "What's the status of X?"
    │   └─ get_entity_state_native
    │
    ├─ "What devices do I have?"
    │   └─ list_entities_native / discover_devices
    │
    ├─ "Create automation"
    │   └─ create_automation
    │
    ├─ "Are there errors?"
    │   └─ get_persistent_notifications
    │
    ├─ "Why isn't X working?"
    │   └─ get_integration_status → diagnose_entity → get_system_logs_diagnostics
    │
    └─ "Optimize/analyze"
        └─ analyze_home_context / energy_intelligence / comfort_optimization
```

---

## 🎯 Final Tips for AI Assistants

1. **Be Conversational:** Don't just return JSON - explain in natural language
2. **Be Proactive:** Suggest automations, improvements, optimizations
3. **Be Safe:** Confirm before destructive actions (delete, restart)
4. **Be Contextual:** Remember conversation history, user preferences
5. **Be Helpful:** If one tool fails, try alternatives
6. **Be Accurate:** Verify entity IDs before acting
7. **Be Complete:** Don't just say "done" - provide status and next steps

---

## 📞 Support Resources

- **API Documentation:** http://192.168.1.203:8001/docs
- **Health Check:** http://192.168.1.203:8001/health
- **OpenAPI Spec:** http://192.168.1.203:8001/openapi.json
- **GitHub Issues:** https://github.com/agarib/homeassistant-mcp-server/issues
- **Version:** Check `/health` endpoint for current version

---

**Document Version:** 1.0.0  
**Last Updated:** November 1, 2025  
**Compatibility:** HA MCP Server v4.0.1+  
**Status:** Production Ready ✅
