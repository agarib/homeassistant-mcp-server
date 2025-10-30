# 🎯 v1.x → v2.0 Migration Quick Reference

## The Core Problem (v1.x)

```
Open-WebUI → http://ha-mcp-server:8001/api/actions/control_light
                ↓
         api_execute_tool(tool_name, body)
                ↓
         Tries to call batch endpoint with WRONG field names
                ↓
         batch expects: {"actions": [{"action": "...", "parameters": {...}}]}
         but receives:  {"actions": [{"name": "...", "arguments": {...}}]}
                ↓
         ❌ FAILS with {"error": ""}
```

**Result**: Tool discovery works ✅ but execution completely broken ❌

## The Solution (v2.0)

```
Open-WebUI → http://ha-mcp-server:8001/control_light
                ↓
         @app.post("/control_light")
         async def control_light(request: ControlLightRequest):
                ↓
         Direct call to ha_api.call_service(...)
                ↓
         ✅ Returns JSON immediately
```

**Result**: Both discovery AND execution work ✅✅

## File Comparison

### v1.x (server.py)

- **Lines**: 4,789
- **Architecture**: MCP Server + Starlette REST wrapper
- **Endpoints**:
  - `/api/actions/{tool_name}` (broken proxy)
  - `/api/actions/batch` (broken field parsing)
  - `/openapi.json` (works)
- **Tool Handlers**: 45 out of 105 implemented
- **Error Handling**: Broken (empty error messages)

### v2.0 (server.py)

- **Lines**: ~1,100 (cleaner!)
- **Architecture**: Pure FastAPI
- **Endpoints**:
  - `/control_light` (direct handler)
  - `/get_area_devices` (direct handler)
  - ... (105 individual endpoints)
- **Tool Handlers**: All endpoints have direct implementations
- **Error Handling**: Proper HTTPException with details

## Key Changes

### Imports

```python
# v1.x
from mcp.server import Server
from mcp.types import Tool, TextContent
from starlette.routing import Route

# v2.0
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
```

### App Initialization

```python
# v1.x
app = Server("homeassistant-native")  # MCP server
web_app = Starlette(routes=[...])     # REST wrapper

# v2.0
app = FastAPI(title="HA OpenAPI Server")  # Pure FastAPI
```

### Tool Definition

```python
# v1.x (indirect)
def get_part1_tools() -> List[Tool]:
    return [Tool(name="control_light", ...)]

# v2.0 (direct)
class ControlLightRequest(BaseModel):
    entity_id: str
    action: str
    brightness: Optional[int] = None

@app.post("/control_light")
async def control_light(request: ControlLightRequest = Body(...)):
    result = await ha_api.call_service("light", request.action, ...)
    return SuccessResponse(message="...", data=result)
```

### Execution Flow

```python
# v1.x (broken)
async def api_execute_tool(request):
    tool_name = request.path_params.get("tool_name")
    body = await request.json()
    batch_payload = {"actions": [{"name": tool_name, "arguments": body}]}  # ❌ Wrong!
    # Try to call batch... (fails)

# v2.0 (working)
@app.post("/control_light")
async def control_light(request: ControlLightRequest = Body(...)):
    # Pydantic validates request automatically
    result = await ha_api.call_service(...)  # Direct call
    return SuccessResponse(...)  # Direct response
```

## Testing Comparison

### v1.x (Broken)

```powershell
# This FAILS
$body = '{"entity_id": "light.living_room", "action": "turn_on"}'
Invoke-RestMethod -Uri "http://192.168.1.203:8001/api/actions/control_light" `
    -Method Post -Body $body -ContentType "application/json"

# Result: {"error": ""}  ❌
```

### v2.0 (Working)

```powershell
# This WORKS
$body = @{
    entity_id = "light.living_room"
    action = "turn_on"
    brightness = 200
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://192.168.1.203:8001/control_light" `
    -Method Post -Body $body -ContentType "application/json"

# Result: {"status": "success", "message": "Light turn_on executed successfully"}  ✅
```

## Migration Checklist

- [ ] **Backup old server.py**: Copy to `server.py.v1.backup`
- [ ] **Upload v2 files**:
  - `server.py` → `/config/ha-mcp-server/server.py`
  - `requirements.txt` → `/config/ha-mcp-server/requirements.txt`
- [ ] **Restart addon**: `docker restart addon_local_ha-mcp-server`
- [ ] **Verify health**: `curl http://ha-ip:8001/health`
- [ ] **Test basic endpoint**: Call `/get_states` with `{"domain": "light"}`
- [ ] **Update Open-WebUI**: Change URL from `/api/actions/...` to direct endpoints
  - Or just reconnect - FastAPI's automatic OpenAPI spec handles it!
- [ ] **Test with Open-WebUI**: Ask "check living room area" and verify execution

## What You Keep

✅ **Environment variables**: Same (HA_URL, HA_TOKEN, PORT, etc.)  
✅ **Container name**: Same (`addon_local_ha-mcp-server`)  
✅ **Port**: Same (8001)  
✅ **File paths**: Same (`/config/ha-mcp-server/`)  
✅ **HA API calls**: Same logic, just different wrapper  
✅ **Features**: All 105 tools will be available (when complete)

## What Changes

❌ **MCP SSE**: Removed (was only for Claude Desktop, not used with Open-WebUI)  
❌ **Tool definitions**: No more `get_part1_tools()` functions  
❌ **call_tool() handler**: Removed (tools are direct endpoints now)  
❌ **Starlette routes**: Replaced with FastAPI routes  
❌ **Broken proxies**: Removed (`api_execute_tool`, `api_execute_batch_actions`)

## Expected Results

### Before (v1.x)

```
User: "Check living room area"
AI: [Discovers get_area_devices tool ✅]
    [Tries to execute tool ❌]
    [Gets empty error ❌]
    Shows code examples instead of executing 😞
```

### After (v2.0)

```
User: "Check living room area"
AI: [Discovers get_area_devices endpoint ✅]
    [Executes POST /get_area_devices ✅]
    [Gets real device list ✅]
    Returns actual devices in the area! 🎉
```

## Support

If you encounter issues:

1. **Check health**: `curl http://ha-ip:8001/health`
2. **View logs**: `ssh root@ha-ip "docker logs addon_local_ha-mcp-server --tail=50"`
3. **Test endpoint directly**: See examples in README.md
4. **Rollback**: `cp server.py.v1.backup server.py` and restart

---

**Bottom Line**: v2.0 removes the broken hybrid architecture and implements proper OpenAPI REST endpoints that Open-WebUI can actually execute!
