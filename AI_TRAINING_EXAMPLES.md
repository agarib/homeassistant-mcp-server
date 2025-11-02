# Home Assistant OpenAPI Server - AI Training Examples

**Version:** 4.0.3  
**Purpose:** Training data for AI models to learn how to control Home Assistant via OpenAPI  
**Base URL:** `http://192.168.1.203:8001`

---

## 🚨 CRITICAL: Understanding How to Use These Tools

### 📡 THESE ARE REST API ENDPOINTS - NOT PYTHON FUNCTIONS

**IMPORTANT:** The `ha_*` tools are **HTTP REST API endpoints**, not Python functions you can import or call directly.

#### ❌ WRONG - Trying to call as Python functions

```python
# This will FAIL - "name not defined"
result = ha_read_file(filepath="configuration.yaml")  # ❌ NO!
content = ha_write_file("test.txt", "content")         # ❌ NO!
```

#### ✅ CORRECT - Making HTTP POST requests

```python
import requests

# Method 1: Using requests library
response = requests.post(
    "http://192.168.1.203:8001/ha_read_file",
    json={"filepath": "configuration.yaml"}
)
print(response.json())

# Method 2: If in Open-WebUI environment, the tools are automatically available
# Open-WebUI handles the HTTP calls for you when you reference the tool name
```

**For Open-WebUI AI Assistants:**

- Open-WebUI provides these tools automatically when configured
- You reference them by name (e.g., "ha_read_file")
- Open-WebUI translates your tool calls into HTTP POST requests
- No need to make manual HTTP requests

**For Claude Desktop / Other AI Environments:**

- Must make HTTP POST requests to `http://192.168.1.203:8001/ha_*` endpoints
- Use `requests`, `httpx`, `fetch`, or similar HTTP client
- Follow the JSON request/response format shown in examples below

---

## 🚨 CRITICAL: Common Endpoint Naming Mistakes

### ⚠️ THESE ENDPOINTS DON'T EXIST - Use _native Versions!

**Cloud AIs frequently make this mistake:**

```
❌ /ha_get_services         ← DOES NOT EXIST! Returns 404!
❌ /ha_get_entity_state     ← DOES NOT EXIST! Returns 404!
❌ /ha_list_entities        ← DOES NOT EXIST! Returns 404!
❌ /ha_get_config           ← DOES NOT EXIST! Returns 404!

✅ /ha_get_services_native      ← USE THIS! (with _native suffix)
✅ /ha_get_entity_state_native  ← USE THIS! (with _native suffix)
✅ /ha_list_entities_native     ← USE THIS! (with _native suffix)
✅ /ha_get_config_native        ← USE THIS! (with _native suffix)
```

**Why _native suffix?**
These endpoints were converted from the native MCP protocol and retained the `_native` suffix to distinguish them from other HA API wrappers.

**Complete list of _native endpoints:**
1. `ha_get_entity_state_native` - Get entity state
2. `ha_list_entities_native` - List all entities
3. `ha_get_services_native` - List available services
4. `ha_fire_event_native` - Fire custom events
5. `ha_render_template_native` - Render Jinja2 templates
6. `ha_get_config_native` - Get HA configuration
7. `ha_get_history_native` - Get entity history
8. `ha_get_logbook_native` - Get logbook entries

**If you get a 404 error, check if you forgot the _native suffix!**

---

## 🚨 CRITICAL: Tool Naming Convention

### ⚠️ NAMESPACE SEPARATION - READ THIS FIRST

**ALL Home Assistant tools use the `ha_` prefix to prevent conflicts with Open-WebUI built-in tools.**

#### ❌ WRONG - These are Open-WebUI's Built-in Tools (Restricted Access)

```
tool_write_file    ← Only works in /workspace (WILL FAIL for /config)
tool_read_file     ← Only works in /workspace (WILL FAIL for /config)
tool_list_files    ← Only works in /workspace (WILL FAIL for /config)
```

#### ✅ CORRECT - These are Home Assistant Tools (Full /config Access)

```
ha_write_file      ← Full /config access (USE THIS!)
ha_read_file       ← Full /config access (USE THIS!)
ha_list_directory  ← Full /config access (USE THIS!)
```

### 🎯 Rule for AI Assistants

**When working with Home Assistant:**

- ✅ **ALWAYS use `ha_` prefixed tools** for Home Assistant operations
- ✅ **File operations:** Use `ha_write_file`, `ha_read_file`, `ha_list_directory`
- ✅ **Device control:** Use `ha_control_light`, `ha_control_switch`, etc.
- ✅ **Automations:** Use `ha_create_automation`, `ha_trigger_automation`, etc.

**Common Mistake to Avoid:**

```
❌ User: "Create automation file in HA"
❌ AI uses: tool_write_file → FAILS (restricted to /workspace)

✅ User: "Create automation file in HA"
✅ AI uses: ha_write_file → SUCCESS (full /config access)
```

---

## 📋 Table of Contents

1. [Understanding Tool Access](#understanding-tool-access)
2. [Tool Naming Reference](#tool-naming-reference)
3. [Device Discovery](#device-discovery)
4. [Light Control](#light-control)
5. [Switch Control](#switch-control)
6. [Climate Control](#climate-control)
7. [File Operations](#file-operations)
8. [Automation Management](#automation-management)
9. [Scene Management](#scene-management)
10. [System Operations](#system-operations)
11. [Quick Reference Table](#quick-reference-table)

---

## Understanding Tool Access

### 🔍 Different AI Environments Access Tools Differently

#### Environment 1: Open-WebUI (Primary Use Case)

**How it works:**

1. Open-WebUI is configured with Home Assistant OpenAPI server URL
2. Tools are automatically discovered from `/openapi.json`
3. AI references tools by name (e.g., "ha_read_file")
4. Open-WebUI handles HTTP communication transparently

**Example in Open-WebUI:**

```
User: "Read my configuration.yaml file"
AI thinks: "I need to use ha_read_file tool"
Open-WebUI: Makes HTTP POST to http://192.168.1.203:8001/ha_read_file
Response: Returns file content to AI
AI responds: "Here's your configuration..."
```

**No code needed** - tools appear automatically in Open-WebUI interface!

---

#### Environment 2: Claude Desktop / MCP (Model Context Protocol)

**How it works:**

1. MCP server connects Claude Desktop to Home Assistant
2. Tools exposed via MCP protocol
3. Claude calls tools by name
4. MCP server handles HTTP translation

**Configuration:** Requires `claude_desktop_config.json` with MCP server settings

---

#### Environment 3: Code Interpreter / Python Scripts

**How it works:**

- **No automatic tool access** - must make manual HTTP requests
- Use `requests` or `httpx` library
- Construct HTTP POST requests manually

**Example Python Code:**

```python
import requests

# Read a file from Home Assistant
response = requests.post(
    "http://192.168.1.203:8001/ha_read_file",
    json={"filepath": "configuration.yaml"},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    print(f"File content: {data['content']}")
else:
    print(f"Error: {response.status_code}")
```

**Important:** If you're in a code interpreter and trying to call `ha_read_file()` directly, you'll get "name not defined" because these are **REST API endpoints**, not Python functions!

---

#### Environment 4: Direct HTTP Clients (curl, Postman, etc.)

**How it works:**

- Direct HTTP POST to endpoint URLs
- Manual JSON payload construction
- Used for testing and debugging

**Example with curl:**

```bash
curl -X POST http://192.168.1.203:8001/ha_read_file \
  -H "Content-Type: application/json" \
  -d '{"filepath": "configuration.yaml"}'
```

**Example with PowerShell:**

```powershell
$body = @{filepath="configuration.yaml"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://192.168.1.203:8001/ha_read_file" `
  -Method POST -Body $body -ContentType "application/json"
```

---

### ⚠️ Common Error: "name 'ha_read_file' is not defined"

**This error means:**

- You're in a **code interpreter** environment
- You're trying to call `ha_read_file()` as a Python function
- But it's actually an **HTTP REST endpoint**

**Solution:**

```python
# ❌ WRONG - Trying to call as function
result = ha_read_file(filepath="test.yaml")  # ERROR!

# ✅ CORRECT - Make HTTP request
import requests
response = requests.post(
    "http://192.168.1.203:8001/ha_read_file",
    json={"filepath": "test.yaml"}
)
result = response.json()
```

---

### 🎯 Which Environment Are You In?

**Ask yourself:**

1. **Are you in Open-WebUI?**

   - ✅ Tools available by name automatically
   - ✅ Just reference "ha_read_file" and it works
   - ✅ No HTTP requests needed

2. **Are you in Claude Desktop with MCP?**

   - ✅ Tools available by name via MCP
   - ✅ MCP server handles communication
   - ✅ No HTTP requests needed

3. **Are you in a Python/code interpreter?**

   - ❌ No automatic tools
   - ✅ Must use `requests.post()` manually
   - ✅ Treat as REST API calls

4. **Are you testing with curl/Postman?**
   - ✅ Direct HTTP POST requests
   - ✅ Manual JSON construction

---

## 📋 Table of Contents (continued)

---

## Tool Naming Reference

### All 81 Home Assistant Endpoints (v4.0.3)

#### Device Control (7 endpoints)

- `ha_control_light` - Control lights (on/off, brightness, color)
- `ha_control_switch` - Control switches (on/off, toggle)
- `ha_control_climate` - Control thermostats/HVAC
- `ha_control_cover` - Control blinds/garage doors
- `ha_vacuum_control` - Control vacuum cleaners
- `ha_fan_control` - Control fans
- `ha_media_player_control` - Control media players

#### Discovery (4 endpoints)

- `ha_discover_devices` - Find devices by domain/area
- `ha_get_device_state` - Get specific device state
- `ha_get_area_devices` - Get all devices in an area
- `ha_get_states` - Get all entity states

#### File Operations (9 endpoints) 🔥 CRITICAL

- `ha_write_file` - Write files to /config
- `ha_read_file` - Read files from /config
- `ha_list_directory` - List directory contents
- `ha_delete_file` - Delete files
- `ha_create_directory` - Create directories
- `ha_move_file` - Move/rename files
- `ha_copy_file` - Copy files
- `ha_search_files` - Search file contents
- `ha_get_directory_tree` - Get directory tree

#### Automations (7 endpoints)

- `ha_list_automations` - List all automations
- `ha_trigger_automation` - Trigger automation manually
- `ha_create_automation` - Create new automation
- `ha_update_automation` - Update existing automation
- `ha_delete_automation` - Delete automation
- `ha_get_automation_details` - Get automation config
- `ha_enable_disable_automation` - Enable/disable automation

#### Scenes (3 endpoints)

- `ha_create_scene` - Create new scene
- `ha_activate_scene` - Activate scene
- `ha_list_scenes` - List all scenes

#### Add-ons (9 endpoints)

- `ha_list_addons` - List installed add-ons
- `ha_get_addon_info` - Get add-on details
- `ha_start_addon` - Start add-on
- `ha_stop_addon` - Stop add-on
- `ha_restart_addon` - Restart add-on
- `ha_install_addon` - Install add-on
- `ha_uninstall_addon` - Uninstall add-on
- `ha_update_addon` - Update add-on
- `ha_get_addon_logs` - Get add-on logs

#### Logs & History (6 endpoints)

- `ha_get_entity_history` - Get entity state history
- `ha_get_system_logs` - Get system logs
- `ha_get_error_log` - Get error logs
- `ha_diagnose_entity` - Diagnose entity issues
- `ha_get_statistics` - Get statistical data
- `ha_get_binary_sensor` - Get binary sensor data

#### Dashboards (8 endpoints)

- `ha_list_dashboards` - List all dashboards
- `ha_get_dashboard_config` - Get dashboard config
- `ha_create_dashboard` - Create new dashboard
- `ha_update_dashboard_config` - Update dashboard
- `ha_delete_dashboard` - Delete dashboard
- `ha_list_hacs_cards` - List available HACS cards
- `ha_create_button_card` - Create button card
- `ha_create_mushroom_card` - Create mushroom card

#### Intelligence (4 endpoints)

- `ha_analyze_home_context` - Analyze home state
- `ha_activity_recognition` - Detect current activity
- `ha_comfort_optimization` - Optimize comfort settings
- `ha_energy_intelligence` - Analyze energy usage

#### Security (3 endpoints)

- `ha_intelligent_security_monitor` - Monitor security
- `ha_anomaly_detection` - Detect anomalies
- `ha_vacation_mode` - Activate vacation mode

#### Camera VLM (3 endpoints)

- `ha_analyze_camera_vlm` - Analyze camera with AI
- `ha_object_detection` - Detect objects in camera
- `ha_facial_recognition` - Recognize faces

#### Code Execution (3 endpoints)

- `ha_execute_python` - Execute Python code
- `ha_analyze_states_dataframe` - Analyze states with pandas
- `ha_plot_sensor_history` - Plot sensor data

#### Native MCPO Tools (9 endpoints)

- `ha_get_entity_state_native` - Get entity state (MCP native)
- `ha_list_entities_native` - List entities (MCP native)
- `ha_get_services_native` - List services (MCP native)
- `ha_fire_event_native` - Fire custom event (MCP native)
- `ha_render_template_native` - Render Jinja2 template (MCP native)
- `ha_get_config_native` - Get HA configuration (MCP native)
- `ha_get_history_native` - Get history (MCP native)
- `ha_get_logbook_native` - Get logbook (MCP native)
- `ha_get_system_logs_diagnostics` - Get system logs (diagnostics)

#### System (4 endpoints)

- `ha_call_service` - Call any HA service
- `ha_restart_homeassistant` - Restart HA
- `ha_camera_snapshot` - Get camera snapshot
- `ha_get_persistent_notifications` - Get notifications
- `ha_get_integration_status` - Check integration status
- `ha_get_startup_errors` - Get startup errors

#### Utility (2 endpoints)

- `/health` - Health check (no ha\_ prefix)
- `/` - API info (no ha\_ prefix)

---

## Device Discovery

### Example 1: Discover All Devices in an Area

**User Request:** "What devices are in the living room?"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_get_area_devices
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

**AI Learning Points:**

- ✅ Tool name: `ha_get_area_devices` (with `ha_` prefix!)
- Use `area_name` to search for devices
- Returns all entities with that area name in their friendly_name
- Check `count` to know how many devices were found

---

### Example 2: Discover Devices by Type

**User Request:** "Show me all the lights in the house"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_get_states
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

**AI Learning Points:**

- ✅ Tool name: `ha_get_states` (with `ha_` prefix!)
- Use `domain` parameter to filter by device type
- Common domains: `light`, `switch`, `climate`, `sensor`, `binary_sensor`, `media_player`, `fan`, `cover`, `vacuum`

---

### Example 3: Get Specific Device State

**User Request:** "Is the couch light on?"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_get_device_state
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
  "last_changed": "2025-11-02T19:00:00"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_get_device_state` (with `ha_` prefix!)
- Always verify entity_id exists before controlling
- Check `state` field: "on", "off", "unavailable"

---

## Light Control

### Example 4: Turn Light On

**User Request:** "Turn on the couch light"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_light
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

**AI Learning Points:**

- ✅ Tool name: `ha_control_light` (with `ha_` prefix!)
- `action` must be: `turn_on`, `turn_off`, or `toggle`
- Always use exact entity_id

---

### Example 5: Dim Light to 50%

**User Request:** "Dim the couch light to 50%"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_light
Content-Type: application/json

{
  "entity_id": "light.couch_light",
  "action": "turn_on",
  "brightness": 127
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_control_light` (with `ha_` prefix!)
- Brightness range: 0-255 (0 = 0%, 255 = 100%)
- Calculate: brightness = (percentage / 100) × 255
- 50% = 127, 75% = 191, 25% = 64

---

### Example 6: Set Light Color to Red

**User Request:** "Make the couch light red"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_light
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

**AI Learning Points:**

- ✅ Tool name: `ha_control_light` (with `ha_` prefix!)
- RGB values: 0-255 for each channel [R, G, B]

---

### Example 7: Gradual Transition

**User Request:** "Slowly turn on the living room light over 5 seconds"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_light
Content-Type: application/json

{
  "entity_id": "light.living_room",
  "action": "turn_on",
  "brightness": 255,
  "transition": 5
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_control_light` (with `ha_` prefix!)
- `transition` is in seconds
- Creates smooth fade effect

---

## Switch Control

### Example 8: Turn On Switch

**User Request:** "Turn on the coffee maker"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_switch
Content-Type: application/json

{
  "entity_id": "switch.coffee_maker",
  "action": "turn_on"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_control_switch` (with `ha_` prefix!)
- Actions: `turn_on`, `turn_off`, `toggle`

---

### Example 9: Toggle Switch

**User Request:** "Toggle the fan"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_switch
Content-Type: application/json

{
  "entity_id": "switch.fan",
  "action": "toggle"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_control_switch` (with `ha_` prefix!)
- Toggle flips current state (on→off, off→on)

---

## Climate Control

### Example 10: Set Temperature

**User Request:** "Set bedroom temperature to 21 degrees"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_climate
Content-Type: application/json

{
  "entity_id": "climate.bedroom",
  "action": "set_temperature",
  "temperature": 21
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_control_climate` (with `ha_` prefix!)
- Temperature in Celsius or Fahrenheit (depends on HA config)

---

### Example 11: Change HVAC Mode

**User Request:** "Turn on heating in the living room"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_control_climate
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

**AI Learning Points:**

- ✅ Tool name: `ha_control_climate` (with `ha_` prefix!)

---

## File Operations

### 🔥 CRITICAL: File Operations Namespace

**These are the most important endpoints to get right!**

❌ **NEVER use these (Open-WebUI built-in, restricted to /workspace):**

- `tool_write_file`
- `tool_read_file`
- `tool_list_files`

✅ **ALWAYS use these (HA server, full /config access):**

- `ha_write_file`
- `ha_read_file`
- `ha_list_directory`

---

### Example 12: Read Configuration File

**User Request:** "Show me the contents of configuration.yaml"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_read_file
Content-Type: application/json

{
  "filepath": "configuration.yaml"
}
```

**Response:**

```json
{
  "filepath": "configuration.yaml",
  "content": "homeassistant:\n  name: Home\n  latitude: 51.5\n...",
  "size": 1234
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_read_file` (with `ha_` prefix!)
- ❌ DO NOT use `tool_read_file` (wrong tool, will fail!)
- Filepath is relative to `/config/`
- Returns content as string

---

### Example 13: Create New Automation File

**User Request:** "Create a new automation file for the bedroom"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_write_file
Content-Type: application/json

{
  "filepath": "packages/bedroom_automations.yaml",
  "content": "automation:\n  - alias: 'Morning Light'\n    trigger:\n      - platform: time\n        at: '07:00:00'\n    action:\n      - service: light.turn_on\n        target:\n          entity_id: light.bedroom\n"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Successfully wrote 234 bytes to packages/bedroom_automations.yaml"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_write_file` (with `ha_` prefix!)
- ❌ DO NOT use `tool_write_file` (wrong tool, will fail!)
- Automatically creates parent directories (`packages/`)
- Filepath is relative to `/config/`

---

### Example 14: List Directory Contents

**User Request:** "What files are in the packages folder?"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_list_directory
Content-Type: application/json

{
  "dirpath": "packages"
}
```

**Response:**

```json
{
  "directory": "packages",
  "items": [
    {
      "name": "bedroom_automations.yaml",
      "type": "file",
      "path": "packages/bedroom_automations.yaml"
    },
    {
      "name": "climate",
      "type": "directory",
      "path": "packages/climate"
    }
  ],
  "count": 2
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_list_directory` (with `ha_` prefix!)
- ❌ DO NOT use `tool_list_files` (wrong tool!)
- Returns both files and directories
- Check `type` field: "file" or "directory"

---

### Example 15: Delete File

**User Request:** "Delete the old_automation.yaml file"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_delete_file
Content-Type: application/json

{
  "filepath": "packages/old_automation.yaml"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_delete_file` (with `ha_` prefix!)
- Cannot be undone - use with caution

---

### Example 16: Search Files

**User Request:** "Find all files that mention light.couch_light"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_search_files
Content-Type: application/json

{
  "pattern": "light.couch_light",
  "directory": ".",
  "extensions": ["yaml"]
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_search_files` (with `ha_` prefix!)
- Searches file contents (not just filenames)
- Use `extensions` to filter by file type

---

## Automation Management

### Example 17: List All Automations

**User Request:** "Show me all automations"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_list_automations
Content-Type: application/json

{
  "enabled_only": false
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_list_automations` (with `ha_` prefix!)
- Set `enabled_only: true` to show only active automations

---

### Example 18: Trigger Automation

**User Request:** "Run the morning routine automation"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_trigger_automation
Content-Type: application/json

{
  "automation_id": "automation.morning_routine"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_trigger_automation` (with `ha_` prefix!)
- Use entity_id format: `automation.{name}`

---

### Example 19: Create New Automation

**User Request:** "Create automation to turn on porch light at sunset"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_create_automation
Content-Type: application/json

{
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
  ],
  "mode": "single"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_create_automation` (with `ha_` prefix!)
- Follow Home Assistant YAML automation format
- Common triggers: `time`, `sun`, `state`, `template`, `event`
- Modes: `single`, `restart`, `queued`, `parallel`

---

### Example 20: Enable/Disable Automation

**User Request:** "Disable the bedtime automation"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_enable_disable_automation
Content-Type: application/json

{
  "automation_id": "automation.bedtime_routine",
  "action": "disable"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_enable_disable_automation` (with `ha_` prefix!)
- Actions: `enable` or `disable`

---

## Scene Management

### Example 21: Create Scene

**User Request:** "Create a movie night scene"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_create_scene
Content-Type: application/json

{
  "scene_id": "scene.movie_night",
  "entities": {
    "light.living_room": {
      "state": "on",
      "brightness": 30
    },
    "light.couch_light": {
      "state": "on",
      "brightness": 50,
      "rgb_color": [255, 100, 0]
    }
  }
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_create_scene` (with `ha_` prefix!)
- Captures current state of specified entities

---

### Example 22: Activate Scene

**User Request:** "Activate movie night scene"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_activate_scene
Content-Type: application/json

{
  "scene_id": "scene.movie_night"
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_activate_scene` (with `ha_` prefix!)
- Restores all entity states from scene

---

## System Operations

### Example 23: Call Any Service

**User Request:** "Turn on all lights in the house"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_call_service
Content-Type: application/json

{
  "domain": "light",
  "service": "turn_on",
  "service_data": {
    "brightness": 255
  }
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_call_service` (with `ha_` prefix!)
- Most flexible endpoint - can call ANY HA service
- Prefer specific endpoints when available (more user-friendly)

---

### Example 24: Restart Home Assistant

**User Request:** "Restart Home Assistant"

**API Call:**

```http
POST http://192.168.1.203:8001/ha_restart_homeassistant
Content-Type: application/json

{
  "confirm": true
}
```

**AI Learning Points:**

- ✅ Tool name: `ha_restart_homeassistant` (with `ha_` prefix!)
- Requires `confirm: true` for safety

---

## Quick Reference Table

| Task                 | Endpoint Name              | Key Parameters                                   |
| -------------------- | -------------------------- | ------------------------------------------------ |
| Turn on light        | `ha_control_light`         | `entity_id`, `action: "turn_on"`                 |
| Set brightness       | `ha_control_light`         | `brightness` (0-255)                             |
| Set color            | `ha_control_light`         | `rgb_color: [R, G, B]`                           |
| Turn on switch       | `ha_control_switch`        | `entity_id`, `action: "turn_on"`                 |
| Set temperature      | `ha_control_climate`       | `temperature`, `hvac_mode`                       |
| Get device state     | `ha_get_device_state`      | `entity_id`                                      |
| Find devices in area | `ha_get_area_devices`      | `area_name`                                      |
| **Read file**        | **`ha_read_file`**         | **`filepath`** (NOT tool_read_file!)             |
| **Write file**       | **`ha_write_file`**        | **`filepath`, `content`** (NOT tool_write_file!) |
| **List directory**   | **`ha_list_directory`**    | **`dirpath`** (NOT tool_list_files!)             |
| Create automation    | `ha_create_automation`     | `alias`, `trigger`, `action`                     |
| Trigger automation   | `ha_trigger_automation`    | `automation_id`                                  |
| Create scene         | `ha_create_scene`          | `scene_id`, `entities`                           |
| Activate scene       | `ha_activate_scene`        | `scene_id`                                       |
| Call any service     | `ha_call_service`          | `domain`, `service`, `service_data`              |
| Restart HA           | `ha_restart_homeassistant` | `confirm: true`                                  |

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Using Open-WebUI Built-in Tools for HA Operations

**WRONG:**

```http
POST /tool_write_file
{
  "filepath": "/config/automations.yaml",
  "content": "..."
}
```

**Error:** `Access denied - path outside allowed directories`

**CORRECT:**

```http
POST /ha_write_file
{
  "filepath": "automations.yaml",
  "content": "..."
}
```

**Result:** ✅ Success!

---

### ❌ Mistake 2: Forgetting the ha\_ Prefix

**WRONG:**

```http
POST /control_light
```

**Error:** `404 Not Found`

**CORRECT:**

```http
POST /ha_control_light
```

**Result:** ✅ Success!

---

### ❌ Mistake 3: Wrong Brightness Scale

**WRONG:**

```http
POST /ha_control_light
{
  "brightness": 50  ← This is 19% brightness!
}
```

**CORRECT:**

```http
POST /ha_control_light
{
  "brightness": 127  ← This is 50% brightness
}
```

---

## AI Assistant Best Practices

### 1. Always Discover Before Controlling

```
User: "Turn on the living room light"

AI Steps:
1. Find entity: POST /ha_get_area_devices {"area_name": "living room"}
2. Verify state: POST /ha_get_device_state {"entity_id": "light.living_room"}
3. Control: POST /ha_control_light {"entity_id": "light.living_room", "action": "turn_on"}
```

### 2. Double-Check Tool Names

Before making ANY file operation:

- ✅ Is it `ha_write_file`? Good!
- ❌ Is it `tool_write_file`? STOP! Wrong tool!

### 3. Handle Percentages Correctly

**Brightness (0-255):**

- User says "50%" → Send `brightness: 127`
- User says "75%" → Send `brightness: 191`
- Formula: `brightness = Math.round((percentage / 100) * 255)`

**Volume (0.0-1.0):**

- User says "50%" → Send `volume_level: 0.5`
- User says "75%" → Send `volume_level: 0.75`

### 4. Provide Clear Feedback

**Good:**

```
AI: "I've turned on the couch light and set it to 50% brightness (127/255)
with a warm white color. The command was sent to ha_control_light successfully."
```

**Bad:**

```
AI: "Done."
```

---

## Testing Checklist for AI Assistants

Before deploying to production, verify:

- ✅ Used `ha_` prefix for ALL Home Assistant operations
- ✅ Used `ha_write_file` (NOT `tool_write_file`) for file writes
- ✅ Used `ha_read_file` (NOT `tool_read_file`) for file reads
- ✅ Used `ha_list_directory` (NOT `tool_list_files`) for directory listings
- ✅ Verified entity_id exists before controlling
- ✅ Used correct brightness scale (0-255)
- ✅ Used correct volume scale (0.0-1.0)
- ✅ Handled errors gracefully
- ✅ Provided clear feedback to user

---

## Version History

### v4.0.3 (2025-11-02) - Current

- **BREAKING:** All 81 endpoints renamed with `ha_` prefix
- **CRITICAL:** FileManager methods also prefixed (`ha_write_file`, `ha_read_file`, etc.)
- **REASON:** Prevents conflicts with Open-WebUI built-in tools
- **IMPACT:** AI models MUST use `ha_` prefixed endpoints for all HA operations

### v4.0.2 (2025-11-01)

- Fixed directory tree endpoint
- Improved diagnostics integration

### v4.0.0 (2025-11-01)

- Added native MCPO tools
- Added system diagnostics tools
- Unified architecture (85 total endpoints)

### v3.0.0 (2025-10-31)

- Production release with 77 validated endpoints
- No `ha_` prefix (deprecated)

---

## Summary

**For AI Models Training on This Document:**

1. **CRITICAL RULE:** Always use `ha_` prefixed endpoints for Home Assistant operations
2. **File Operations:** Use `ha_write_file`, `ha_read_file`, `ha_list_directory` (NEVER use `tool_*` variants)
3. **Device Control:** Use `ha_control_light`, `ha_control_switch`, etc.
4. **Namespace Separation:** `ha_*` = Home Assistant (full access) | `tool_*` = Open-WebUI (restricted)
5. **Total Endpoints:** 81 with `ha_` prefix + 2 utility endpoints (`/health`, `/`)

**Version:** 4.0.3  
**Last Updated:** November 2, 2025  
**Status:** Production-Ready ✅

---

**Ready for AI Training!** 🚀
