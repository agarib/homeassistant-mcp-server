# 🌐 Cloud AI Integration Guide for HA MCP Server v1.0.3

**Authors**: agarib & GitHub Copilot  
**Date**: October 30, 2025  
**Server Version**: 1.0.3 (105 tools)

---

## ⚠️ Common Mistakes (READ THIS FIRST!)

### ❌ WRONG - Don't Do This:
```python
# This will FAIL with "NameError: name 'call_tool' is not defined"
call_tool('control_light', {
    'entity_id': 'light.tv_light', 
    'state': 'off'
})
```

**Why it fails**: `call_tool()` is an MCP server function, NOT a Python function you can call directly!

### ✅ CORRECT - Do This Instead:

**Natural language in chat:**
```
You: "Turn off the TV light"
AI: [calls control_light tool behind the scenes] ✅ Done!
```

---

## 🔧 Server Connection Settings

### For MCP-Compatible Cloud AI Platforms:

| Setting | Value |
|---------|-------|
| **Server URL** | `http://192.168.1.203:8001` |
| **Transport** | SSE (Server-Sent Events) |
| **Endpoint** | `/messages` |
| **Full URL** | `http://192.168.1.203:8001/messages` |
| **Health Check** | `http://192.168.1.203:8001/health` |
| **Tools List** | `http://192.168.1.203:8001/api/actions` |

### ⚠️ NOT WebSocket!
If you see **"HTTP 404 WebSocket connection rejected"**, your client is trying to use WebSocket instead of SSE.

**Fix**: Configure your MCP client to use **SSE (Server-Sent Events)** transport, not WebSocket.

---

## 📋 Available Tools (105 Total)

### Test Connectivity:
Before using tools, verify the server is accessible:

```bash
# Health check
curl http://192.168.1.203:8001/health

# List all tools
curl http://192.168.1.203:8001/api/actions

# Get Home Assistant state
curl http://192.168.1.203:8001/api/state
```

Expected response from `/health`:
```json
{
  "status": "healthy",
  "service": "ha-mcp-server",
  "version": "1.0.0"
}
```

Expected response from `/api/actions`:
```json
{
  "total_tools": 105,
  "tools": [...]
}
```

---

## 🎯 How to Use Tools (Correct Method)

### Method 1: Natural Language (RECOMMENDED)

**Lights:**
```
"Turn on the kitchen lights"
"Set bedroom lights to 50% brightness"
"Make the living room lights blue"
"Turn off all lights"
```

**Climate:**
```
"Set thermostat to 72 degrees"
"What's the current temperature in the bedroom?"
"Turn on the AC"
```

**Devices:**
```
"Turn on the TV"
"Is the front door locked?"
"Open the garage door"
```

**Home Assistant Management:**
```
"Restart Home Assistant"
"List all automations"
"Show me sensor states"
```

**File Operations:**
```
"Read the configuration.yaml file"
"Create a new automation in automations.yaml"
"List all YAML files in /config"
```

### Method 2: Explicit Tool Requests

If natural language doesn't work, be explicit:

```
"Use the control_light tool to turn off light.tv_light"
"Call the restart_homeassistant tool"
"Execute get_states to show all entities"
```

---

## 🔍 Troubleshooting

### Problem: "HTTP 404 WebSocket connection rejected"

**Cause**: Client trying to use WebSocket instead of SSE  
**Fix**: 
1. Check your MCP client configuration
2. Set transport to **SSE** or **Server-Sent Events**
3. Use URL: `http://192.168.1.203:8001/messages`
4. Do NOT use `ws://` or `wss://` URLs

### Problem: "NameError: name 'call_tool' is not defined"

**Cause**: Trying to call MCP tools as Python functions  
**Fix**: Use natural language in chat instead of Python code

### Problem: "Connection refused" or "Timeout"

**Checks**:
```powershell
# 1. Check if add-on is running
curl http://192.168.1.203:8001/health

# 2. Check from Home Assistant host
ssh root@192.168.1.203 "docker ps | grep mcp-server"

# 3. Check logs
ssh root@192.168.1.203 "docker logs addon_local_ha-mcp-server"

# 4. Restart if needed
ssh root@192.168.1.203 "docker restart addon_local_ha-mcp-server"
```

### Problem: Tools not executing / No response

**Possible causes**:
1. MCP client not properly connected to `/messages` endpoint
2. Using wrong transport (WebSocket vs SSE)
3. Server not receiving requests (check logs)

**Debug steps**:
```bash
# Test if server receives requests
curl -X POST http://192.168.1.203:8001/api/actions \
  -H "Content-Type: application/json"

# Subscribe to events (SSE test)
curl -N http://192.168.1.203:8001/subscribe_events
```

---

## 📱 Platform-Specific Setup

### Claude Desktop / MCP Inspector

Add to your MCP settings:

```json
{
  "mcpServers": {
    "homeassistant": {
      "url": "http://192.168.1.203:8001/messages",
      "transport": "sse"
    }
  }
}
```

### Open-WebUI

**External Tool Server Configuration**:
1. Go to Settings → Tools
2. Click "Add Tool Server"
3. Enter:
   - **Name**: Home Assistant MCP
   - **URL**: `http://192.168.1.203:8001/messages`
   - **Type**: MCP over SSE
4. Save and test connection

### Python MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Note: For HTTP/SSE servers, use appropriate client
    # This is just an example structure
    
    server_params = StdioServerParameters(
        command="curl",
        args=["-N", "http://192.168.1.203:8001/messages"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")
            
            # Call a tool
            result = await session.call_tool(
                "control_light",
                arguments={
                    "entity_id": "light.tv_light",
                    "action": "turn_off"
                }
            )
            print(result)

asyncio.run(main())
```

---

## 🎨 Example Use Cases

### 1. Morning Routine Automation
```
"Create a morning routine that:
1. Turns on bedroom lights to 30%
2. Sets thermostat to 72°F
3. Reads today's weather from sensors"
```

The AI will use multiple tools:
- `control_light` for lights
- `control_climate` for thermostat
- `get_states` to read sensors
- `write_file` to save automation

### 2. Security Check
```
"Check all doors and windows, tell me which ones are open"
```

The AI will:
- Call `get_states` with domain filter for sensors
- Parse binary_sensor states
- Report open/closed status

### 3. Energy Analysis
```
"Show me power consumption for the last 24 hours as a chart"
```

The AI will:
- Call `plot_sensor_history` with energy sensor
- Return matplotlib chart as base64 image

### 4. Custom Card Installation
```
"Install the mini-graph-card from HACS, then restart Home Assistant"
```

The AI will:
- Call HACS installation tools
- Call `restart_homeassistant` after install

---

## 🔐 Security Notes

### Network Access
- Server listens on `0.0.0.0:8001` (all interfaces)
- Recommended: Use firewall rules to restrict access
- Consider VPN for remote access

### Authentication
Current version: **No authentication** (runs inside HA with supervisor token)

**For production use**, consider:
1. Reverse proxy with authentication (nginx, Caddy)
2. VPN tunnel (WireGuard, Tailscale)
3. Cloudflare Tunnel with access policies

---

## 📊 Monitoring & Logs

### Check Server Status
```bash
# Via API
curl http://192.168.1.203:8001/health

# Container logs
ssh root@192.168.1.203 "docker logs -f addon_local_ha-mcp-server"

# Last 50 lines
ssh root@192.168.1.203 "docker logs addon_local_ha-mcp-server --tail 50"
```

### Logs Show Tool Calls
When a tool is executed, you'll see:
```
2025-10-30 00:00:00 - INFO - 💡 Controlling light: light.tv_light
2025-10-30 00:00:01 - INFO - ✅ Light controlled successfully
```

---

## 🆘 Getting Help

### Check Documentation
- [README.md](README.md) - Installation and setup
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [GitHub Issues](https://github.com/agarib/homeassistant-mcp-server/issues)

### Report Issues
If you encounter problems:
1. Check logs: `docker logs addon_local_ha-mcp-server`
2. Test endpoints: `/health`, `/api/actions`, `/api/state`
3. Verify network connectivity
4. Create GitHub issue with logs and error details

### Version Info
```bash
# Server version
curl http://192.168.1.203:8001/health | jq .version

# Tool count
curl http://192.168.1.203:8001/api/actions | jq .total_tools

# Expected: 105 tools in v1.0.3
```

---

## ✅ Quick Verification Checklist

Before reporting issues, verify:

- [ ] Server responds to `/health` endpoint
- [ ] `/api/actions` returns 105 tools
- [ ] `/api/state` returns Home Assistant entities
- [ ] You're using SSE transport (not WebSocket)
- [ ] You're using natural language, not Python `call_tool()`
- [ ] Network connectivity between client and server
- [ ] Firewall allows port 8001

---

## 🎯 Success Indicators

You know it's working when:
- ✅ `/health` returns `{"status": "healthy"}`
- ✅ `/api/actions` returns `{"total_tools": 105}`
- ✅ Natural language commands execute tools
- ✅ Lights turn on/off when requested
- ✅ Files can be read/written
- ✅ Home Assistant restarts when requested

---

**Happy Automating! 🏠🤖**

For updates and more tools, visit:  
https://github.com/agarib/homeassistant-mcp-server

Authors: agarib & GitHub Copilot
