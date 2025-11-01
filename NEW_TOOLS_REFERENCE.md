# 🆕 New Tools Quick Reference

## System Diagnostics Tools (4 NEW Tools)

These tools solve the **washing machine automation problem** by providing visibility into Home Assistant errors and integration status.

---

### 1️⃣ `get_persistent_notifications`

**Purpose:** See all active error notifications in Home Assistant  
**Use Case:** Find integration errors, configuration warnings, system alerts  
**Tags:** `system_diagnostics`

**Request:**

```json
POST /get_persistent_notifications
{}
```

**Response:**

```json
{
  "message": "Found 2 persistent notifications",
  "data": {
    "notifications": [
      {
        "notification_id": "lg_integration_error",
        "title": "LG ThinQ Integration Error",
        "message": "Authentication failed for LG ThinQ",
        "created_at": "2025-11-01T10:30:00",
        "status": "lg_thinq_setup"
      },
      {
        "notification_id": "update_available",
        "title": "Update Available",
        "message": "Home Assistant 2025.11.1 is available",
        "created_at": "2025-11-01T09:00:00"
      }
    ],
    "count": 2
  }
}
```

**Why This Fixes Your Washing Machine:**

- Shows if LG ThinQ integration has errors
- Reveals authentication issues
- Identifies why automation isn't triggering

---

### 2️⃣ `get_integration_status`

**Purpose:** Check health of specific integrations  
**Use Case:** Verify LG ThinQ is loaded and working  
**Tags:** `system_diagnostics`

**Request:**

```json
POST /get_integration_status
{
  "integration": "lg"
}
```

**Response:**

```json
{
  "message": "Found 1 integrations",
  "data": {
    "integrations": [
      {
        "domain": "lg_thinq",
        "title": "LG ThinQ",
        "state": "loaded", // or "setup_error", "not_loaded"
        "entry_id": "abc123",
        "disabled_by": null,
        "supports_options": true
      }
    ],
    "count": 1
  }
}
```

**Integration States:**

- `loaded` ✅ - Working correctly
- `setup_error` ❌ - Integration failed to load
- `not_loaded` ⚠️ - Integration exists but not configured

---

### 3️⃣ `get_system_logs`

**Purpose:** Read Home Assistant error logs with filtering  
**Use Case:** Debug integration failures, see startup errors  
**Tags:** `system_diagnostics`

**Request:**

```json
POST /get_system_logs
{
  "lines": 100,
  "level": "ERROR"
}
```

**Response:**

```json
{
  "message": "Retrieved 12 log entries (level: ERROR)",
  "data": {
    "log_lines": [
      "2025-11-01 10:30:15 ERROR (MainThread) [homeassistant.components.lg_thinq] Authentication failed",
      "2025-11-01 10:30:16 ERROR (MainThread) [homeassistant.components.lg_thinq] Failed to connect to LG server",
      ...
    ],
    "count": 12,
    "level_filter": "ERROR"
  }
}
```

**Log Levels:**

- `ERROR` - Critical errors (integration failures)
- `WARNING` - Potential issues
- `INFO` - General information
- `DEBUG` - Detailed debugging info

---

### 4️⃣ `get_startup_errors`

**Purpose:** Get errors from last Home Assistant restart  
**Use Case:** Diagnose why integrations fail at startup  
**Tags:** `system_diagnostics`

**Request:**

```json
POST /get_startup_errors
{}
```

**Response:**

```json
{
  "message": "Found 5 startup-related errors",
  "data": {
    "startup_errors": [
      "ERROR (MainThread) [homeassistant.setup] Setup failed for lg_thinq: Integration failed to initialize",
      "ERROR (MainThread) [homeassistant.components.lg_thinq] Platform not ready, retrying in 30s",
      ...
    ],
    "count": 5
  }
}
```

**When to Use:**

- After restarting Home Assistant
- When automation stops working
- When new integrations don't appear

---

## Native MCPO Tools (12 Converted Tools)

Previously in native MCP server, now unified with FastAPI/Pydantic validation.

### Device Control

#### `control_light`

Full light control with brightness, color, and temperature.

**Request:**

```json
POST /control_light
{
  "entity_id": "light.living_room",
  "action": "turn_on",
  "brightness": 200,
  "rgb_color": [255, 200, 100]
}
```

**Actions:**

- `turn_on` - Turn light on (+ optional brightness/color)
- `turn_off` - Turn light off
- `toggle` - Toggle state
- `brightness` - Set brightness only
- `color` - Set RGB color only

---

#### `control_switch`

Simple switch control.

**Request:**

```json
POST /control_switch
{
  "entity_id": "switch.coffee_maker",
  "action": "turn_on"
}
```

**Actions:** `turn_on`, `turn_off`, `toggle`

---

#### `control_climate`

Thermostat and HVAC control.

**Request:**

```json
POST /control_climate
{
  "entity_id": "climate.living_room",
  "temperature": 22,
  "hvac_mode": "heat"
}
```

**HVAC Modes:** `heat`, `cool`, `auto`, `off`, `heat_cool`, `fan_only`, `dry`

---

### Discovery & State

#### `get_entity_state`

Get current state and all attributes of any entity.

**Request:**

```json
POST /get_entity_state
{
  "entity_id": "sensor.washing_machine_status"
}
```

**Response:**

```json
{
  "message": "State for sensor.washing_machine_status",
  "data": {
    "entity_id": "sensor.washing_machine_status",
    "state": "Running",
    "attributes": {
      "friendly_name": "Washing Machine Status",
      "device_class": "enum",
      "remaining_time": "00:45:00"
    },
    "last_changed": "2025-11-01T10:30:00",
    "last_updated": "2025-11-01T10:35:00"
  }
}
```

---

#### `list_entities`

List all entities, optionally filtered by domain.

**Request:**

```json
POST /list_entities
{
  "domain": "light"
}
```

**Response:**

```json
{
  "message": "Found 12 entities in domain 'light'",
  "data": {
    "entities": [
      {
        "entity_id": "light.living_room",
        "state": "on",
        "friendly_name": "Living Room Light"
      },
      {
        "entity_id": "light.bedroom",
        "state": "off",
        "friendly_name": "Bedroom Light"
      }
    ],
    "count": 12
  }
}
```

**Common Domains:** `light`, `switch`, `sensor`, `binary_sensor`, `climate`, `media_player`, `automation`

---

### Generic Service Calls

#### `call_service`

Call any Home Assistant service with custom data.

**Request:**

```json
POST /call_service
{
  "domain": "notify",
  "service": "mobile_app_phone",
  "service_data": {
    "message": "Washing machine finished!",
    "title": "Laundry Alert"
  }
}
```

**Common Services:**

- `notify.mobile_app_*` - Send notifications
- `climate.set_temperature` - Set thermostat
- `media_player.play_media` - Play media
- `automation.trigger` - Trigger automation

---

#### `get_services`

List all available services in Home Assistant.

**Request:**

```json
POST /get_services
{}
```

**Response:** Full service registry with domains and available actions.

---

### Events & Templates

#### `fire_event`

Fire custom events for automations.

**Request:**

```json
POST /fire_event
{
  "event_type": "washing_machine_finished",
  "event_data": {
    "cycle": "normal",
    "duration": "45 minutes"
  }
}
```

**Use Case:** Trigger custom automations based on AI decisions

---

#### `render_template`

Render Jinja2 templates using Home Assistant's engine.

**Request:**

```json
POST /render_template
{
  "template": "{{ states('sensor.temperature') }} °C in {{ state_attr('sensor.temperature', 'friendly_name') }}"
}
```

**Response:**

```json
{
  "message": "Template rendered",
  "data": {
    "template": "{{ states(...) }}",
    "result": "22.5 °C in Living Room"
  }
}
```

---

### History & Logs

#### `get_history`

Get historical states for an entity.

**Request:**

```json
POST /get_history
{
  "entity_id": "sensor.washing_machine_status",
  "start_time": "2025-11-01T00:00:00",
  "end_time": "2025-11-01T23:59:59"
}
```

**Use Case:** Analyze when washing machine runs, how long cycles take

---

#### `get_logbook`

Get Home Assistant logbook (state changes, events).

**Request:**

```json
POST /get_logbook
{
  "entity_id": "sensor.washing_machine_status",
  "start_time": "2025-11-01T00:00:00"
}
```

**Response:** List of all state changes and events for the entity

---

### System Info

#### `get_config`

Get Home Assistant configuration (version, location, units, etc.).

**Request:**

```json
POST /get_config
{}
```

**Response:**

```json
{
  "message": "Configuration retrieved",
  "data": {
    "latitude": 52.52,
    "longitude": 13.405,
    "elevation": 34,
    "unit_system": "metric",
    "time_zone": "Europe/Berlin",
    "version": "2025.11.0",
    "config_dir": "/config"
  }
}
```

---

## 🎯 Washing Machine Automation Workflow

**Problem:** Automation not triggering when washing machine finishes

**Solution using new tools:**

### Step 1: Check for Errors

```json
POST /get_persistent_notifications
{}
```

→ Look for LG ThinQ errors

### Step 2: Verify Integration

```json
POST /get_integration_status
{
  "integration": "lg"
}
```

→ Check if integration is `loaded` or has `setup_error`

### Step 3: Read Error Logs

```json
POST /get_system_logs
{
  "lines": 100,
  "level": "ERROR"
}
```

→ Find authentication or connection errors

### Step 4: Check Entity State

```json
POST /get_entity_state
{
  "entity_id": "sensor.washing_machine_status"
}
```

→ Verify sensor is reporting correct state

### Step 5: Review History

```json
POST /get_history
{
  "entity_id": "sensor.washing_machine_status",
  "start_time": "2025-11-01T00:00:00"
}
```

→ See if state changes are being recorded

---

## 📊 Tool Count Summary

| Category                | Count  | Tags                 |
| ----------------------- | ------ | -------------------- |
| **Native MCPO Tools**   | 12     | `native_mcpo`        |
| **System Diagnostics**  | 4      | `system_diagnostics` |
| **Existing Production** | 77     | Various              |
| **TOTAL**               | **93** | 🎯                   |

---

## 🚀 Usage Tips

1. **Use `/docs` endpoint** - FastAPI auto-generates interactive docs
2. **Check response.message** - Human-readable status
3. **Read response.data** - Actual payload
4. **Filter by tags** - Group related tools in UI
5. **Test locally first** - Verify before deploying to cluster

---

## 📖 Related Documentation

- `CONSOLIDATION_GUIDE.md` - Complete integration guide
- `tool_additions.py` - Full source code for 16 new tools
- `server.py` - Main FastAPI server (after integration)
- `README.md` - Server overview and deployment

---

**✨ All 93 tools now unified with Pydantic validation! 🎉**
