# Home Assistant API Analysis & Updates

**Date:** November 7, 2025  
**Documentation Review:** REST API, WebSocket API, LLM Integration

---

## Key Findings from Official Documentation

### 1. REST API Endpoints (Last updated: Sep 12, 2025)

**Available REST Endpoints:**

```
✅ GET  /api/                           - API information
✅ GET  /api/config                     - HA configuration
✅ GET  /api/components                 - Installed components
✅ GET  /api/events                     - Event types
✅ GET  /api/services                   - Available services
✅ GET  /api/history/period/<timestamp> - Historical data
✅ GET  /api/logbook/<timestamp>        - Logbook entries
✅ GET  /api/states                     - All entity states
✅ GET  /api/states/<entity_id>         - Specific entity state
✅ GET  /api/error_log                  - Error log (EXISTS!)
✅ GET  /api/camera_proxy/<entity_id>   - Camera snapshots
✅ GET  /api/calendars                  - Calendar list
✅ GET  /api/calendars/<id>?start&end   - Calendar events

✅ POST /api/states/<entity_id>         - Set entity state
✅ POST /api/events/<event_type>        - Fire event
✅ POST /api/services/<domain>/<service>- Call service
✅ POST /api/template                   - Render Jinja2 template
✅ POST /api/config/core/check_config   - Validate configuration
✅ POST /api/intent/handle              - Process intent

✅ DELETE /api/states/<entity_id>       - Remove entity state
```

**CRITICAL FINDING:**

- ❌ **NO /api/lovelace/\* endpoints documented!**
- ❌ **NO dashboard/Lovelace REST API in official docs**
- ✅ **GET /api/error_log DOES EXIST** - Our current implementation should try this first!

### 2. WebSocket API (Last updated: Oct 14, 2025)

**WebSocket Commands for Dashboards:**

```javascript
// Get panels (includes dashboard info)
{
  "id": 1,
  "type": "get_panels"
}

// Lovelace config is accessed via WebSocket, NOT REST!
// Commands (not in REST API docs):
- lovelace/config
- lovelace/dashboards/list
- lovelace/resources
```

**Important WebSocket Commands:**

```javascript
// Fetching states
{"type": "get_states"}

// Fetching config
{"type": "get_config"}

// Calling services
{
  "type": "call_service",
  "domain": "light",
  "service": "turn_on",
  "target": {"entity_id": "light.kitchen"},
  "service_data": {...}
}

// Fire event
{
  "type": "fire_event",
  "event_type": "custom_event",
  "event_data": {...}
}

// Validate config
{
  "type": "validate_config",
  "trigger": ...,
  "condition": ...,
  "action": ...
}
```

### 3. LLM Integration API (Last updated: Jul 17, 2025)

**Key Capabilities:**

- Built-in Assist API for LLM integration
- Custom tool registration via `llm.Tool` class
- Intent handling via `/api/intent/handle`
- Template rendering via `/api/template`

**Tool Structure:**

```python
class MyTool(llm.Tool):
    name = "ToolName"
    description = "What the tool does"
    parameters = vol.Schema({...})

    async def async_call(self, hass, tool_input, llm_context):
        return {...}  # JSON serializable dict
```

---

## Issues Identified in Current Implementation

### ❌ Dashboard Tools - BROKEN

**Current Implementation:**

```python
# WRONG - These endpoints don't exist in REST API!
url = f"{HA_URL}/lovelace/dashboards"       # 404
url = f"{HA_URL}/lovelace/config"            # 404
url = f"{HA_URL}/lovelace/config/{dashboard_id}"  # 404
```

**Root Cause:**
Lovelace/Dashboard management is **WebSocket-only**, NOT available via REST API.

**Solution Options:**

**Option A:** Add WebSocket support to server

```python
import asyncio
import json
import websockets

async def websocket_call(command):
    async with websockets.connect(f"ws://{HA_URL}/api/websocket") as ws:
        # Authenticate
        auth_msg = await ws.recv()
        await ws.send(json.dumps({
            "type": "auth",
            "access_token": HA_TOKEN
        }))
        auth_result = await ws.recv()

        # Send command
        await ws.send(json.dumps(command))
        result = await ws.recv()
        return json.loads(result)
```

**Option B:** Disable dashboard tools temporarily
Mark as "Requires WebSocket" in documentation

**Option C:** Use service calls instead

```python
# Some dashboard operations via services
await ha_api.call_service(
    "lovelace",
    "reload",
    service_data={}
)
```

### ✅ Error Log - CAN BE FIXED

**Current Issue:**
We're reading from file: `/config/home-assistant.log`

**Better Approach:**

```python
# Try REST API endpoint FIRST (it exists!)
response = await http_client.get(f"{HA_URL}/error_log")

# Fallback to file reading if REST fails
if response.status_code == 404:
    # Read from file as current implementation
```

### ✅ Automation Reload - CORRECT APPROACH

**Current Implementation:**

```python
await ha_api.call_service("automation", "reload", service_data={})
```

**Status:** ✅ This is CORRECT per REST API docs!

The error we saw is HA configuration issue, not our code.

---

## Recommended Updates

### Priority 1: Fix Error Log Tool

**Change from:**

```python
# Always read from file
async with aiofiles.open("/config/home-assistant.log", "r") as f:
```

**Change to:**

```python
# Try REST API first (per official docs)
try:
    response = await http_client.get(f"{HA_URL}/error_log")
    if response.status_code == 200:
        return parse_error_log(response.text)
except:
    pass

# Fallback to file reading
async with aiofiles.open("/config/home-assistant.log", "r") as f:
```

### Priority 2: Add WebSocket Support for Dashboards

**Implementation Plan:**

1. Add `websockets` dependency to requirements
2. Create WebSocket client helper class
3. Implement dashboard operations via WebSocket
4. Update all 8 dashboard tools

**New Methods:**

```python
class HomeAssistantWebSocket:
    async def connect(self):
        """Establish WebSocket connection"""

    async def call_command(self, command):
        """Send command and get response"""

    async def get_lovelace_config(self, dashboard_id):
        """Get dashboard config via WebSocket"""

    async def update_lovelace_config(self, dashboard_id, config):
        """Update dashboard via WebSocket"""
```

### Priority 3: Add Intent Handling Tool

**New Tool:**

```python
@app.post("/ha_process_intent")
async def ha_process_intent(request: ProcessIntentRequest):
    """
    Process natural language intent via Assist API.

    Example: "Turn on the kitchen lights"
    """
    response = await http_client.post(
        f"{HA_URL}/intent/handle",
        json={
            "text": request.text,
            "language": request.language or "en"
        }
    )
    return response.json()
```

### Priority 4: Add Template Rendering Tool

**New Tool:**

```python
@app.post("/ha_render_template")
async def ha_render_template_new(request: RenderTemplateRequest):
    """
    Render Jinja2 template with current HA state.

    Example: "{{ states('sensor.temperature') }}"
    """
    response = await http_client.post(
        f"{HA_URL}/template",
        json={"template": request.template}
    )
    return {"rendered": response.text}
```

### Priority 5: Add Config Validation Tool

**New Tool:**

```python
@app.post("/ha_check_config")
async def ha_check_config():
    """
    Validate Home Assistant configuration.
    Checks for errors before restart.
    """
    response = await http_client.post(
        f"{HA_URL}/config/core/check_config"
    )
    return response.json()
```

---

## Updated API Endpoints Map

### Currently Working ✅

```
✅ /api/states                          - ha_get_states
✅ /api/states/<entity_id>              - ha_get_device_state
✅ /api/services                        - ha_get_services
✅ /api/services/<domain>/<service>     - ha_call_service
✅ /api/config                          - ha_get_config
✅ /api/history/period/<timestamp>      - ha_get_history
✅ /api/logbook/<timestamp>             - ha_get_logbook
✅ /api/events/<event_type>             - ha_fire_event
✅ /api/error_log                       - Should use this!
```

### Need WebSocket Implementation ⚠️

```
⚠️ WebSocket: lovelace/dashboards/list   - ha_list_dashboards
⚠️ WebSocket: lovelace/config            - ha_get_dashboard_config
⚠️ WebSocket: lovelace/config (PUT)      - ha_update_dashboard_config
⚠️ WebSocket: lovelace/dashboards (POST) - ha_create_dashboard
⚠️ WebSocket: lovelace/dashboards (DEL)  - ha_delete_dashboard
⚠️ All manual card tools                 - Depend on WebSocket
```

### Can Add New ✨ (Recommended)

```
✨ /api/template                        - Template rendering
✨ /api/intent/handle                   - Natural language intents
✨ /api/config/core/check_config        - Config validation
✨ /api/calendars                       - Calendar integration
✨ /api/camera_proxy/<entity_id>        - Already have camera snapshot (Add this REST endpoint)
```

---

## Implementation Recommendations

### Immediate Actions (Can do now)

1. **Fix ha_get_error_log:**

   - Try REST API `/api/error_log` first
   - Keep file reading as fallback
   - Update in 5 minutes ✅

2. **Add ha_render_template (REST):**

   - Simple POST to `/api/template`
   - Useful for dynamic content ✅

3. **Add ha_process_intent (REST):**

   - Natural language to actions
   - Great for LLM integration ✅

4. **Add ha_check_config (REST):**
   - Validate before restart
   - Safety feature ✅

### Next Phase (Requires WebSocket)

5. **Implement WebSocket client:**

   - Add `websockets` to requirements
   - Create connection manager
   - Handle authentication

6. **Update dashboard tools:**

   - Convert to WebSocket calls
   - Test all 8 tools
   - Update documentation

7. **Add new WebSocket tools:**
   - Real-time state monitoring
   - Event subscription
   - Trigger management

---

## Testing Plan

### Phase 1: REST API Fixes

```powershell
# Test error log
POST /ha_get_error_log

# Test template rendering
POST /ha_render_template
Body: {"template": "{{ states('sun.sun') }}"}

# Test intent handling
POST /ha_process_intent
Body: {"text": "turn on kitchen lights"}

# Test config check
POST /ha_check_config
```

### Phase 2: WebSocket Implementation

```python
# Test WebSocket connection
ws_client = HomeAssistantWebSocket()
await ws_client.connect()

# Test dashboard list
dashboards = await ws_client.call_command({
    "type": "lovelace/dashboards/list"
})

# Test config fetch
config = await ws_client.call_command({
    "type": "lovelace/config",
    "url_path": "lovelace"
})
```

---

## Summary

**Confirmed Working:**

- ✅ All core state/service endpoints
- ✅ Automation reload (HA config issue, not code)
- ✅ Error log endpoint EXISTS in REST API!

**Needs WebSocket:**

- ⚠️ All 8 dashboard tools
- ⚠️ Manual card creation/editing
- ⚠️ Real-time features

**Can Add Now:**

- ✨ Template rendering
- ✨ Intent processing
- ✨ Config validation
- ✨ Calendar integration

**Next Steps:**

1. Fix error log to use REST API
2. Add 3-4 new REST tools
3. Implement WebSocket support
4. Update dashboard tools
5. Test everything
6. Deploy v4.0.6!
