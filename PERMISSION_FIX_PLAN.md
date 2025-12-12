# 🔧 Home Assistant OpenAPI Server - Permission Fix Plan

**Date:** November 2, 2025  
**Issue:** Open-WebUI can't access /config directory  
**Root Cause:** Server permissions/access control issue, NOT routing issue

---

## ✅ Current Status - What's CORRECT

**The Correct Server (85 tools):**

- **URL:** `http://192.168.1.203:8001`
- **Name:** Home Assistant OpenAPI Server v4.0.2
- **Location:** Running as Home Assistant Add-on
- **Tools:** 85 unified tools (all working when tested directly)
- **Status:** ✅ HEALTHY

**MCPO Configuration:**

```json
"homeassistant": {
  "transport": "sse",
  "url": "http://192.168.1.203:8001/messages"
}
```

- ✅ Points to correct server at 192.168.1.203:8001
- ✅ Uses SSE transport for MCP protocol
- ✅ MCPO is the orchestrator, server is the tool provider

**Verification (Direct API Test):**

```powershell
$body = @{filepath = "test_access.txt"; content = "Testing"} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://192.168.1.203:8001/write_file' -Method Post -Body $body -ContentType 'application/json'
```

**Result:** ✅ 200 OK - File written to /config/test_access.txt

---

## ❌ Current Status - What's WRONG

**The Problem:**

When using tools through Open-WebUI, getting error:

```
Access denied - path outside allowed directories:
/config/packages/kitchen/washing_machine.yaml not in
/workspace, /workspace/ai-workspace, /usb-storage
```

**This error message reveals:**

1. ❌ Some component is restricting access to `/workspace` paths only
2. ❌ Our server uses `/config` but something is blocking it
3. ❌ The restriction mentions paths that match MCPO's filesystem server, not HA server

---

## 🔍 Root Cause Analysis

**Theory 1: Tool Name Collision ⭐ MOST LIKELY**

Open-WebUI may be calling the wrong tool:

- MCPO has built-in `filesystem` server with restricted paths: `/workspace`, `/workspace/ai-workspace`, `/usb-storage`
- Our HA server has `write_file` tool with full `/config` access
- Open-WebUI might be routing to filesystem server instead of homeassistant server

**Evidence:**

- Error mentions exact paths from MCPO filesystem server config
- Direct API call to our server works fine
- Only fails when going through Open-WebUI tool interface

**Theory 2: MCPO Sub-route Issue**

MCPO might not be properly exposing HA tools through sub-route `/homeassistant`

**Evidence:**

- User said MCPO route `http://192.168.1.11:30008/homeassistant` is wrong
- Should use direct server `http://192.168.1.203:8001`
- But MCPO config shows SSE transport to correct server

**Theory 3: Server Permission Configuration**

The HA OpenAPI Server itself might have access control settings blocking /config

**Evidence:**

- Direct API test shows this is NOT the case
- Server has full /config access
- Problem only appears through Open-WebUI

---

## 🎯 Solution Plan

### Step 1: Verify Open-WebUI Tool Configuration

Check how Open-WebUI is configured to call HA tools:

```bash
# Access Open-WebUI at http://192.168.1.11:30080
# Navigate to: Admin → Tools → External Tools
# Look for: Home Assistant or MCP tools
# Check the configured URL
```

**Expected:**

- URL should point to MCPO: `http://mcpo-server:8000` (internal cluster DNS)
- Or external: `http://192.168.1.11:30008`

**Test:**

- Try calling a simple tool like `get_entity_state_native`
- Check if it routes to our HA server or fails

### Step 2: Check MCPO Logs for Tool Routing

```bash
ssh pi@192.168.1.11 "sudo kubectl logs -n cluster-services -l app=mcpo-server --tail=100 | grep -A5 'homeassistant\|write_file'"
```

**Look for:**

- Is MCPO receiving tool calls for homeassistant server?
- Are they being routed correctly to http://192.168.1.203:8001?
- Any errors about tool discovery or execution?

### Step 3: Test Direct MCPO Access

```powershell
# Test if MCPO can route to our HA server
$body = @{
    entity_id = "sun.sun"
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri 'http://192.168.1.11:30008/homeassistant/get_entity_state_native' `
    -Method Post `
    -Body $body `
    -ContentType 'application/json'
```

**Expected:** Should return sun.sun entity state if routing works

### Step 4: Check Tool Discovery in Open-WebUI

In Open-WebUI interface:

1. Start a new chat
2. Type: "List all available tools"
3. Check response:
   - Are HA tools listed? (write_file, read_file, etc.)
   - Are they from homeassistant server or filesystem server?
   - Do tool descriptions match our 85 tools?

### Step 5: Explicit Tool Calling Test

In Open-WebUI chat, try explicit tool call:

```
Use the homeassistant server's write_file tool to create a test file at /config/test.txt with content "Hello World"
```

**Watch for:**

- Does it call the correct tool?
- What error appears?
- Check MCPO logs during this call

---

## 🔧 Potential Fixes

### Fix 1: Configure Open-WebUI Tool URL (if wrong)

If Open-WebUI is using wrong URL:

**In Open-WebUI Admin:**

1. Go to Tools → External Tools
2. Find MCP/MCPO configuration
3. Set URL to: `http://mcpo-server:8000` (cluster DNS)
4. Or: `http://192.168.1.11:30008` (external NodePort)

### Fix 2: Add Sub-route Prefix to Tool Names

If tool names collide, we can namespace them:

**In server.py:**

```python
@app.post("/ha_write_file", tags=["file_operations"])
async def ha_write_file(request: FileWriteRequest):
    # ... existing code
```

This makes tool names unique: `ha_write_file` instead of `write_file`

### Fix 3: Update MCPO Sub-route Configuration

Ensure MCPO properly exposes HA tools on `/homeassistant` sub-route.

**Check current config:**

```bash
ssh pi@192.168.1.11 "sudo kubectl get configmap mcpo-config -n cluster-services -o jsonpath='{.data.config\.json}' | python3 -m json.tool"
```

**Should have:**

```json
{
  "mcpServers": {
    "homeassistant": {
      "transport": "sse",
      "url": "http://192.168.1.203:8001/messages"
    }
  }
}
```

### Fix 4: Bypass MCPO Entirely (Direct Connection)

If MCPO routing is problematic, configure Open-WebUI to call our server directly:

**Option A: HTTP Transport (if MCPO supports it)**

```json
{
  "homeassistant": {
    "transport": "http",
    "url": "http://192.168.1.203:8001"
  }
}
```

**Option B: Direct OpenAPI Integration**

Configure as OpenAPI tool in Open-WebUI:

- Name: Home Assistant Tools
- OpenAPI Spec URL: `http://192.168.1.203:8001/openapi.json`
- This bypasses MCPO completely

---

## 📋 Investigation Checklist

- [ ] Check Open-WebUI tool configuration URL
- [ ] Review MCPO logs for homeassistant server connections
- [ ] Test MCPO sub-route with curl/Invoke-WebRequest
- [ ] Verify tool discovery in Open-WebUI interface
- [ ] Check which tools are being called (filesystem vs homeassistant)
- [ ] Test explicit tool calling in Open-WebUI chat
- [ ] Review server.py for any access control logic
- [ ] Check HA add-on logs for denied requests

---

## 🎯 Expected Outcome

After fixes:

1. ✅ Open-WebUI can call all 85 HA tools
2. ✅ File operations work with /config paths
3. ✅ No "Access denied" errors
4. ✅ Can write washing machine automation to /config/packages/kitchen/
5. ✅ All automations, dashboards, file tools fully accessible

---

## 📚 Old 12-Tool Server Cleanup

**Status:** ✅ ALREADY CLEANED UP

Confirmed no old server running:

```bash
kubectl get all -n cluster-services -l app=homeassistant-mcp-server
# Result: No resources found
```

**Remaining artifacts (harmless):**

- `homeassistant-mcp-config` ConfigMap (only has HA_URL env var)
- `homeassistant-mcp-server` ConfigMap (contains server.py code used by MCPO init container)

These are NOT the old 12-tool server - they're part of MCPO's current setup!

**The MCPO initContainer copies server.py from the ConfigMap:**

- ConfigMap `homeassistant-mcp-server` → `/workspace/homeassistant-mcp/server.py`
- This is our 85-tool server.py being staged for potential future use
- Currently NOT used (MCPO connects via SSE to http://192.168.1.203:8001)

---

## 🚀 Next Steps

1. **Investigate Open-WebUI configuration** - Find out what URL/tools it's using
2. **Test MCPO routing** - Verify sub-route works correctly
3. **Check tool discovery** - See which tools Open-WebUI sees
4. **Apply appropriate fix** - Based on findings above
5. **Validate access** - Ensure /config paths work
6. **Write washing machine config** - Complete original goal!

---

**Current Understanding:**

- ✅ Server is correct (192.168.1.203:8001, 85 tools, v4.0.2)
- ✅ Server works perfectly (tested directly)
- ✅ MCPO config is correct (SSE to correct server)
- ✅ Old 12-tool server is gone
- ❌ Open-WebUI tool routing issue (calling wrong tools or wrong server)
- 🔍 Need to investigate Open-WebUI configuration and MCPO routing

**Goal:**
Enable full /config access for all 85 tools through Open-WebUI interface.
