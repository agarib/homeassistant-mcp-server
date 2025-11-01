# Home Assistant MCP Server Consolidation Guide

## 🎯 Overview

**Goal:** Unified Home Assistant control server with all 93 tools under one FastAPI server

**Before:**

- ❌ 12 tools in native MCP server (`mcp-server-homeassistant`)
- ❌ 77 tools in OpenAPI server (`ha-openapi-server-v3.0.0`)
- ❌ Different protocols, validation, and deployment

**After:**

- ✅ **93 tools** in single FastAPI server with Pydantic validation
- ✅ 12 native MCPO tools converted to FastAPI
- ✅ 4 NEW system diagnostics tools
- ✅ 77 existing production tools
- ✅ Consistent error handling and documentation

---

## 📦 Tool Inventory (93 Total)

### **Native MCPO Tools (12 tools)** 🆕

Converted from MCP protocol to FastAPI with Pydantic validation:

1. **`control_light`** - Full light control (brightness, color, temperature)
2. **`control_switch`** - Switch on/off/toggle
3. **`get_entity_state`** - Query any entity state
4. **`list_entities`** - List all entities by domain
5. **`call_service`** - Generic service caller
6. **`get_services`** - List available services
7. **`fire_event`** - Fire custom events
8. **`render_template`** - Jinja2 template rendering
9. **`get_config`** - HA system configuration
10. **`control_climate`** - Thermostat control
11. **`get_history`** - Entity state history
12. **`get_logbook`** - Logbook entries

### **System Diagnostics (4 tools)** 🆕

New tools for troubleshooting and monitoring:

13. **`get_system_logs`** - Read HA core logs with filtering
14. **`get_persistent_notifications`** - Get error notifications
15. **`get_integration_status`** - Check integration health
16. **`get_startup_errors`** - Startup errors after restart

### **Existing Production Tools (77 tools)** ✅

From `ha-openapi-server-v3.0.0`:

- Device Control (4 tools)
- File Operations (9 tools)
- Automations (10 tools)
- Scenes (3 tools)
- Media & Devices (4 tools)
- System (2 tools)
- Code Execution (3 tools)
- Discovery (5 tools)
- Logs & History (6 tools)
- Dashboards (9 tools)
- Intelligence (4 tools)
- Security (3 tools)
- Camera VLM (3 tools)
- Add-on Management (9 tools)

---

## 🔧 Integration Steps

### Step 1: Add Tool Definitions to `server.py`

```bash
# Navigate to server directory
cd C:\MyProjects\ha-openapi-server-v3.0.0

# Backup current server
cp server.py server.py.backup

# Open server.py in editor
code server.py
```

**Insert the tool additions:**

1. Copy all Pydantic models from `tool_additions.py`
2. Paste **BEFORE** the `/health` endpoint (around line 3600)
3. Update the module docstring to reflect 93 tools

### Step 2: Add Missing HomeAssistantAPI Methods

Some native tools use methods not in the current `HomeAssistantAPI` class. Add these to the class (around line 120):

```python
class HomeAssistantAPI:
    # ... existing methods ...

    async def get_services(self) -> dict:
        """Get all available HA services"""
        response = await http_client.get(f"{HA_URL}/api/services")
        response.raise_for_status()
        return response.json()

    async def fire_event(self, event_type: str, event_data: dict = None) -> dict:
        """Fire a custom event"""
        response = await http_client.post(
            f"{HA_URL}/api/events/{event_type}",
            json=event_data or {}
        )
        response.raise_for_status()
        return response.json()

    async def render_template(self, template: str) -> str:
        """Render a Jinja2 template"""
        response = await http_client.post(
            f"{HA_URL}/api/template",
            json={"template": template}
        )
        response.raise_for_status()
        return response.text

    async def get_config(self) -> dict:
        """Get HA configuration"""
        response = await http_client.get(f"{HA_URL}/api/config")
        response.raise_for_status()
        return response.json()
```

### Step 3: Update Dependencies (if needed)

Check `requirements.txt` - should already have:

```txt
fastapi>=0.104.0
pydantic>=2.0.0
httpx>=0.25.0
uvicorn[standard]>=0.24.0
aiofiles
python-multipart
```

### Step 4: Test Locally

```powershell
# Activate environment
cd C:\MyProjects\ha-openapi-server-v3.0.0

# Run server
python server.py

# Check OpenAPI docs
# Navigate to: http://localhost:8001/docs
```

Verify:

- ✅ All 93 endpoints visible
- ✅ Tags show: `native_mcpo` and `system_diagnostics`
- ✅ Pydantic models render correctly

### Step 5: Deploy to K3s Cluster

Update your MCPO config to use the unified server:

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "python3",
      "args": ["/workspace/homeassistant-openapi/server.py"],
      "env": {
        "HA_URL": "http://supervisor/core/api",
        "HA_TOKEN": "your_token_here",
        "HOST": "0.0.0.0",
        "PORT": "8001"
      }
    }
  }
}
```

Deploy:

```powershell
# Update ConfigMap with new server.py
kubectl delete configmap homeassistant-openapi-server -n cluster-services
kubectl create configmap homeassistant-openapi-server --from-file=server.py -n cluster-services

# Restart MCPO pods
kubectl rollout restart deployment mcpo-server -n cluster-services

# Verify
kubectl logs -n cluster-services -l app=mcpo-server --tail=100 | Select-String "homeassistant"
```

---

## 🎯 Key Benefits

### **1. Unified Validation**

All tools use Pydantic models with consistent error handling:

```python
class ControlLightRequest(BaseModel):
    entity_id: str = Field(..., description="Light entity ID")
    brightness: Optional[int] = Field(None, ge=0, le=255)
```

### **2. Better Documentation**

OpenAPI spec auto-generates from Pydantic models:

- Type hints → automatic validation
- Field descriptions → API docs
- Examples in docstrings

### **3. Easier Maintenance**

Single codebase instead of two:

- One set of dependencies
- One deployment process
- One test suite

### **4. Tool Consistency**

All tools follow same patterns:

```python
@app.post("/tool_name", summary="...", tags=["category"])
async def tool_name(request: ToolRequest = Body(...)):
    try:
        # Tool logic
        return SuccessResponse(message="...", data={...})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### **5. System Diagnostics** 🆕

The 4 new tools solve the washing machine automation problem:

- `get_persistent_notifications` - See integration errors
- `get_integration_status` - Check if LG integration is loaded
- `get_system_logs` - Read error logs with filters
- `get_startup_errors` - Diagnose startup issues

---

## 📝 Usage Examples

### Example 1: Control Light with Color

```json
POST /control_light
{
  "entity_id": "light.living_room",
  "action": "turn_on",
  "brightness": 200,
  "rgb_color": [255, 200, 100]
}
```

### Example 2: Get Persistent Notifications (Washing Machine Fix!)

```json
POST /get_persistent_notifications
{}

Response:
{
  "message": "Found 2 persistent notifications",
  "data": {
    "notifications": [
      {
        "notification_id": "lg_integration_error",
        "title": "LG ThinQ Integration Error",
        "message": "Authentication failed...",
        "created_at": "2025-11-01T10:30:00"
      }
    ],
    "count": 2
  }
}
```

### Example 3: Check Integration Status

```json
POST /get_integration_status
{
  "integration": "lg"
}

Response:
{
  "message": "Found 1 integrations",
  "data": {
    "integrations": [
      {
        "domain": "lg_thinq",
        "title": "LG ThinQ",
        "state": "setup_error",
        "disabled_by": null
      }
    ],
    "count": 1
  }
}
```

### Example 4: Generic Service Call

```json
POST /call_service
{
  "domain": "climate",
  "service": "set_temperature",
  "entity_id": "climate.living_room",
  "service_data": {
    "temperature": 22,
    "hvac_mode": "heat"
  }
}
```

---

## 🔍 Testing Checklist

After deployment, verify these scenarios:

### Native MCPO Tools

- [ ] `control_light` - Turn on light with brightness
- [ ] `control_switch` - Toggle switch
- [ ] `get_entity_state` - Query sensor state
- [ ] `list_entities` - List all lights
- [ ] `call_service` - Generic service call
- [ ] `render_template` - Render Jinja2 template
- [ ] `get_history` - Get sensor history
- [ ] `get_logbook` - Get state changes

### System Diagnostics

- [ ] `get_system_logs` - Read error log
- [ ] `get_persistent_notifications` - See HA notifications
- [ ] `get_integration_status` - Check integration health
- [ ] `get_startup_errors` - Get startup errors

### Existing Tools (Spot Check)

- [ ] `control_device` - Turn on light
- [ ] `read_file` - Read automation YAML
- [ ] `execute_python` - Run Python code
- [ ] `get_areas` - List areas

---

## 📊 Migration Comparison

| Aspect             | Before (Native MCP)          | After (Unified OpenAPI) |
| ------------------ | ---------------------------- | ----------------------- |
| **Tools**          | 12 (MCP) + 77 (OpenAPI)      | 93 (all FastAPI)        |
| **Validation**     | Mixed (MCP types + Pydantic) | Consistent Pydantic     |
| **Docs**           | MCP schema                   | OpenAPI/Swagger         |
| **Deployment**     | 2 servers                    | 1 server                |
| **Testing**        | 2 test suites                | 1 test suite            |
| **Error Handling** | Inconsistent                 | Unified HTTPException   |
| **Performance**    | 2 connections                | 1 connection            |

---

## 🚀 Next Steps

1. **Complete Integration** ✅

   - Add 16 new tools to `server.py`
   - Update `HomeAssistantAPI` class
   - Test locally at http://localhost:8001/docs

2. **Deploy to Cluster** ⏳

   - Update ConfigMap
   - Restart MCPO pods
   - Verify in Open-WebUI

3. **Test Washing Machine Fix** ⏳

   - Use `get_persistent_notifications`
   - Use `get_integration_status` for LG integration
   - Fix automation based on diagnostics

4. **Create Comprehensive Guide** ⏳
   - Document all 93 tools
   - Add usage examples
   - Create troubleshooting guide

---

## 📖 Related Files

- `server.py` - Main FastAPI server (3672 → ~4200 lines)
- `tool_additions.py` - New tools to add (16 tools)
- `requirements.txt` - Python dependencies
- `README.md` - Server documentation
- `todo.md` - Project tasks

---

## 🎉 Benefits Summary

✅ **Single Source of Truth** - All HA tools in one place  
✅ **Pydantic Validation** - Type safety and auto-docs  
✅ **System Diagnostics** - Fix washing machine automation!  
✅ **Easier Deployment** - One server, one config  
✅ **Better Testing** - Unified test suite  
✅ **OpenAPI Docs** - Auto-generated at `/docs`

**Total: 93 unified tools with consistent validation! 🎯**
