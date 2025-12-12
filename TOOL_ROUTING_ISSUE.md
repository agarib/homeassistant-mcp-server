# 🚨 CRITICAL: Open-WebUI Tool Routing Issue

**Date:** November 2, 2025  
**Issue:** Open-WebUI using wrong file tools with restricted access  
**Impact:** All file operations blocked despite having 85 working tools

---

## 🔍 The Problem

**What's Happening:**

Open-WebUI is calling its **built-in file tools** instead of our **HA MCP Server tools**:

**Wrong Tools (Restricted Access):**

- ❌ `tool_write_file_post` → Only `/workspace`, `/workspace/ai-workspace`, `/usb-storage`
- ❌ `tool_get_file_info_post` → Restricted paths
- ❌ `tool_read_file_post` → Restricted paths

**Correct Tools (Full /config Access):**

- ✅ `write_file` → Full `/config` access
- ✅ `read_file` → Full `/config` access
- ✅ `list_directory` → Full `/config` access
- ✅ All 85 HA MCP Server tools → Unrestricted

---

## 🧪 Proof Our Tools Work

```powershell
# Test direct access to our server:
$body = @{
    filepath = "test_access.txt"
    content = "Testing /config access"
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://192.168.1.203:8001/write_file' `
    -Method Post -Body $body -ContentType 'application/json'

# Result: ✅ 200 OK - File written to /config/test_access.txt
```

Our server has **FULL /config access** and works perfectly!

---

## 🔧 Root Cause

**Tool Name Collision:**

1. Open-WebUI has built-in file tools with restricted access
2. Our HA MCP Server has file tools with full access
3. Open-WebUI is choosing its own tools instead of ours
4. MCPO might not be properly exposing our tool names

**Evidence:**

Error message shows:

```
Access denied - path outside allowed directories:
/config/packages/kitchen/washing_machine.yaml not in
/workspace, /workspace/ai-workspace, /usb-storage
```

But our server uses `/config` as base path, not `/workspace`!

---

## ✅ Solutions

### Solution 1: Use Correct Tool Names in Open-WebUI

Tell Cloud AI to use:

- `/write_file` (our tool)
- NOT `tool_write_file_post` (Open-WebUI's restricted tool)

### Solution 2: Check MCPO Configuration

MCPO should be exposing our tools properly. Check MCPO config:

```yaml
servers:
  homeassistant:
    url: "http://192.168.1.203:8001/messages"
    transport: "sse"
```

### Solution 3: Verify Open-WebUI Tool Configuration

In Open-WebUI:

1. Go to Admin → Tools
2. Find "Home Assistant" tools
3. Verify tool names don't have `tool_` prefix
4. Check base URL points to MCPO route

### Solution 4: Rename Our Tools to Avoid Collision

If needed, we can rename our tools to be more specific:

- `write_file` → `ha_write_file`
- `read_file` → `ha_read_file`
- etc.

---

## 🎯 Quick Fix

**For the washing machine file:**

Instead of using Open-WebUI's restricted `tool_write_file_post`, the AI should call:

```json
POST http://192.168.1.203:8001/write_file
{
  "filepath": "packages/kitchen/washing_machine.yaml",
  "content": "... yaml content ..."
}
```

Or through MCPO (if configured):

```json
POST http://mcpo-server:8000/homeassistant/write_file
{
  "filepath": "packages/kitchen/washing_machine.yaml",
  "content": "... yaml content ..."
}
```

---

## 📋 Action Items

1. **Check MCPO routing** - Is it properly exposing our tools?
2. **Check Open-WebUI tool config** - Are our tools visible?
3. **Instruct AI** - Use correct tool names without `tool_` prefix
4. **Test direct access** - Verify our server works (already confirmed ✅)
5. **Consider renaming** - Add `ha_` prefix to avoid collision

---

## 🔍 Investigation Needed

1. Check MCPO logs for tool registration
2. Check Open-WebUI tool list
3. Verify MCPO sub-route configuration
4. Test tool calling from Open-WebUI UI

---

**Status:** Investigation in progress  
**Server:** Working perfectly ✅  
**Issue:** Tool routing/naming in Open-WebUI/MCPO layer
