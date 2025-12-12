# 🚀 v4.0.5 Quick Deployment Guide

## What Was Fixed

1. **✅ Doubled Tool Names** - All 85 endpoints now have clean names

   - Before: `ha_control_light_ha_control_light_post` ❌
   - After: `ha_control_light` ✅

2. **✅ ha_get_error_log 500 Error** - Now reads from actual log file
   - Before: 404 Not Found (tried non-existent API) ❌
   - After: Reads from `/config/home-assistant.log` ✅

## Deploy in 3 Steps

### Step 1: Copy server.py to HA

**Option A: Via SSH/SCP**

```powershell
scp server.py homeassistant@192.168.1.203:/config/ha-mcp-server/
```

**Option B: Via Network Share**

```powershell
Copy-Item server.py -Destination "\\192.168.1.203\config\ha-mcp-server\"
```

**Option C: Via Home Assistant File Editor**

1. Open Home Assistant → Settings → Add-ons → File Editor
2. Navigate to `/config/ha-mcp-server/server.py`
3. Replace content with new version
4. Save

### Step 2: Restart the Add-on

**Via HA UI:**

1. Settings → Add-ons
2. Home Assistant MCP Server
3. Click "Restart"

**Via HA CLI:**

```bash
ha addons restart local_ha_mcp_server
```

### Step 3: Verify in Open-WebUI

1. Open http://192.168.1.11:30080
2. Go to Settings → Tools → Tool Servers
3. Find "Home Assistant OpenAPI Server - v4.0.5"
4. Refresh the connection (click refresh icon)
5. Check tool list:
   - ✅ Should see: `ha_control_light`
   - ❌ Should NOT see: `ha_control_light_ha_control_light_post`

## Quick Test

Test the fixed error log tool:

```json
{
  "limit": 10
}
```

Expected response:

```json
{
  "status": "success",
  "message": "Found X errors and Y warnings from log file",
  "data": {
    "errors": [...],
    "error_count": X,
    "warning_count": Y,
    "total": X+Y,
    "log_file": "/config/home-assistant.log"
  }
}
```

✅ Status should be 200 OK (not 500)

## Rollback (If Needed)

If issues occur, rollback to v4.0.4:

```bash
cd /config/ha-mcp-server
git checkout v4.0.4 server.py
ha addons restart local_ha_mcp_server
```

## Support

Issues? Check:

1. HA add-on logs: Settings → Add-ons → Home Assistant MCP Server → Logs
2. Look for version confirmation: "Home Assistant OpenAPI Server v4.0.5"
3. Check for operation_id in OpenAPI spec: http://192.168.1.203:8001/openapi.json

---

**🎉 That's it! Enjoy clean tool names!**
