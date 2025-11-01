# Home Assistant MCP Server - Add-on Deployment Guide

**Version:** 4.0.0  
**Date:** November 1, 2025  
**Deployment Model:** Home Assistant Add-on + MCPO Integration

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────┐
│   K3s Cluster (Pi4 192.168.1.11-14)    │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │         MCPO Server              │  │
│  │   (cluster-services namespace)   │  │
│  │                                  │  │
│  │  Connects to HA MCP Server via: │  │
│  │  SSE: http://192.168.1.203:8001  │  │
│  │       /messages                  │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
└─────────────────┼───────────────────────┘
                  │
                  │ SSE Transport
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Home Assistant (192.168.1.203)        │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   HA MCP Server Add-on           │  │
│  │   Port: 8001                     │  │
│  │   Endpoint: /messages (SSE)      │  │
│  │   Health: /health                │  │
│  │                                  │  │
│  │   Access:                        │  │
│  │   - /config (read/write)         │  │
│  │   - Supervisor API               │  │
│  │   - Home Assistant API           │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**Key Points:**

- ✅ Server runs **inside Home Assistant** as an add-on (not in K3s cluster)
- ✅ MCPO in K3s cluster connects **to** the add-on via SSE
- ✅ Add-on has direct access to `/config` directory
- ✅ Add-on uses `SUPERVISOR_TOKEN` for HA API calls
- ✅ Endpoint: `http://192.168.1.203:8001`
- ✅ SSE transport: `http://192.168.1.203:8001/messages`

---

## 🚀 Deployment Steps

### Step 1: Install Add-on in Home Assistant

1. **Add Repository:**

   - Go to Settings → Add-ons → Add-on Store
   - Click "⋮" menu → Repositories
   - Add: `https://github.com/agarib/homeassistant-mcp-server`

2. **Install Add-on:**

   - Find "Home Assistant MCP Server" in store
   - Click Install
   - Wait for installation to complete

3. **Configure Add-on:**

   ```yaml
   # Add-on Configuration
   port: 8001
   log_level: info
   admin_token: "your-long-lived-access-token" # Optional for add-on management
   ```

4. **Start Add-on:**
   - Click Start
   - Enable "Start on boot" (recommended)
   - Enable "Watchdog" (recommended)

### Step 2: Verify Add-on is Running

```bash
# From any machine that can reach HA
curl http://192.168.1.203:8001/health

# Expected response:
{
  "status": "healthy",
  "version": "4.0.0",
  "home_assistant_connected": true,
  "timestamp": "2025-11-01T18:30:00Z"
}
```

**Check Add-on Logs:**

- Settings → Add-ons → Home Assistant MCP Server → Logs
- Look for:
  ```
  [INFO] 🏠 Home Assistant OpenAPI Server v4.0.0
  [INFO] Config path: /config
  [INFO] Config path exists: True
  [INFO] Config path is directory: True
  [INFO] Server started on 0.0.0.0:8001
  [INFO] Uvicorn running on http://0.0.0.0:8001
  ```

### Step 3: Configure MCPO to Connect to Add-on

The MCPO config should already point to the add-on (verify):

```bash
# From Windows PC
ssh pi@192.168.1.11 "sudo kubectl get configmap mcpo-config -n cluster-services -o yaml | grep -A3 homeassistant"

# Expected output:
"homeassistant": {
  "transport": "sse",
  "url": "http://192.168.1.203:8001/messages"
}
```

**If not configured:**

```bash
# Edit MCPO config
kubectl edit configmap mcpo-config -n cluster-services

# Add homeassistant server:
{
  "mcpServers": {
    "homeassistant": {
      "transport": "sse",
      "url": "http://192.168.1.203:8001/messages"
    }
  }
}

# Restart MCPO pods
kubectl rollout restart deployment <mcpo-deployment-name> -n cluster-services
```

### Step 4: Verify MCPO Connection

```bash
# Check MCPO logs for successful connection
ssh pi@192.168.1.11 "sudo kubectl logs -n cluster-services -l app=mcpo --tail=100 | grep homeassistant"

# Expected:
[INFO] Successfully connected to 'homeassistant'
[INFO] homeassistant server ready with 85 tools
```

---

## 🔍 Troubleshooting

### Issue 1: Add-on Won't Start

**Symptoms:**

- Add-on shows "Stopped" or "Error" state
- No response from `http://192.168.1.203:8001/health`

**Check Logs:**

```
Settings → Add-ons → Home Assistant MCP Server → Logs
```

**Common Causes:**

1. **Port 8001 Already in Use**

   ```
   Error: [Errno 48] Address already in use
   ```

   **Solution:** Change port in add-on configuration:

   ```yaml
   port: 8002 # Or any other available port
   ```

   Then update MCPO config to match new port.

2. **Python Dependencies Failed**

   ```
   Error: Could not find a version that satisfies the requirement...
   ```

   **Solution:**

   - Check `Dockerfile` has correct Python version
   - Check `requirements.txt` has pinned versions
   - Rebuild add-on

3. **Permission Issues**
   ```
   Error: Permission denied: '/config'
   ```
   **Solution:** Ensure add-on config.json has:
   ```json
   {
     "map": ["config:rw"]
   }
   ```

### Issue 2: MCPO Can't Connect to Add-on

**Symptoms:**

- MCPO logs show connection errors
- Tools not available in Open-WebUI

**Verify Add-on Endpoint:**

```bash
# From K3s cluster node
curl http://192.168.1.203:8001/health

# If this fails, add-on is not accessible from cluster
```

**Check Network:**

```bash
# Ping from K3s node to HA
ssh pi@192.168.1.11 "ping -c 3 192.168.1.203"

# If ping fails, network issue between cluster and HA
```

**Verify MCPO Config:**

```bash
ssh pi@192.168.1.11 "sudo kubectl get configmap mcpo-config -n cluster-services -o yaml"
```

**Check URL is correct:**

- ✅ Correct: `"url": "http://192.168.1.203:8001/messages"`
- ❌ Wrong: `"url": "http://192.168.1.203:8001"` (missing `/messages`)
- ❌ Wrong: `"url": "http://localhost:8001/messages"` (not accessible from cluster)

**Restart MCPO Pods:**

```bash
# Find MCPO deployment name
ssh pi@192.168.1.11 "sudo kubectl get deployments -n cluster-services"

# Restart (replace <deployment-name> with actual name)
ssh pi@192.168.1.11 "sudo kubectl rollout restart deployment <deployment-name> -n cluster-services"
```

### Issue 3: File Operations Fail

**Symptoms:**

- `list_files`, `read_file`, `write_file` return errors
- "Permission denied" or "Path not found" errors

**Check Add-on Has /config Access:**

View add-on logs for startup messages:

```
[INFO] Config path: /config
[INFO] Config path exists: True
[INFO] Config path is directory: True
```

If `False`, add-on doesn't have proper mount.

**Verify File Permissions:**

SSH into Home Assistant OS:

```bash
# Login to HA OS (if using HA OS)
ssh root@192.168.1.203

# Check /config permissions
ls -la /config

# Should show:
drwxr-xr-x  homeassistant  homeassistant  /config
```

**Verify Add-on Mapping:**

Check `config.json` in add-on repository:

```json
{
  "name": "Home Assistant MCP Server",
  "map": ["config:rw"],
  "homeassistant": "2023.1.0"
}
```

### Issue 4: Tools Return "Unauthorized" Errors

**Symptoms:**

- API calls return 401 Unauthorized
- Add-on management tools fail

**Check Token Configuration:**

1. **SUPERVISOR_TOKEN (automatic):**

   - Automatically provided by HA Supervisor
   - Works for 68/85 tools
   - No configuration needed

2. **Admin Token (optional, for add-on management):**
   - Required for 9 add-on management tools
   - Set in add-on configuration:
   ```yaml
   admin_token: "your-long-lived-access-token"
   ```
   - Create token: Settings → People → Long-Lived Access Tokens

**Verify Token in Add-on Logs:**

```
[INFO] Using SUPERVISOR_TOKEN for HA API
[INFO] Admin token configured: Yes
```

### Issue 5: SSE Connection Drops

**Symptoms:**

- MCPO logs show "Connection lost to homeassistant"
- Intermittent tool availability in Open-WebUI

**Check Add-on Stability:**

```bash
# View add-on logs for crashes
Settings → Add-ons → Home Assistant MCP Server → Logs

# Look for:
# - Memory errors
# - Timeout errors
# - Restart messages
```

**Enable Watchdog:**

```yaml
# Add-on Configuration
watchdog: true
```

**Increase Resources (if needed):**

```yaml
# config.json (in add-on repo)
{ "resources": { "memory": "512M", "cpu": "1.0" } }
```

---

## 🧪 Testing & Validation

### Test 1: Health Check

```bash
curl http://192.168.1.203:8001/health
```

**Expected:** `{"status": "healthy", "version": "4.0.0"}`

### Test 2: API Documentation

Visit: `http://192.168.1.203:8001/docs`
**Expected:** Swagger UI showing all 85 endpoints

### Test 3: Call a Simple Tool

```bash
curl -X POST http://192.168.1.203:8001/get_entity_state_native \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "sun.sun"}'
```

**Expected:** JSON with entity state

### Test 4: File Operations

```bash
curl -X POST http://192.168.1.203:8001/list_files \
  -H "Content-Type: application/json" \
  -d '{"path": "/config"}'
```

**Expected:** List of files in /config

### Test 5: MCPO Integration

```bash
# Via Open-WebUI at http://192.168.1.11:30080
# Ask: "What's the current temperature in the living room?"
# Should use homeassistant tools to answer
```

---

## 📊 Endpoint Distribution (85 Tools)

| Category           | Count | Tag                  |
| ------------------ | ----- | -------------------- |
| File Operations    | 9     | `files`              |
| Add-on Management  | 9     | `addons`             |
| Native MCPO        | 8     | `native_mcpo`        |
| Dashboards         | 8     | `dashboards`         |
| Automations        | 7     | `Automations`        |
| Logs & History     | 6     | `logs_history`       |
| Intelligence       | 4     | `intelligence`       |
| System Diagnostics | 4     | `system_diagnostics` |
| Discovery          | 4     | `discovery`          |
| Code Execution     | 3     | `code_execution`     |
| Scenes             | 3     | `scenes`             |
| Camera VLM         | 3     | `camera_vlm`         |
| Security           | 3     | `security`           |
| System             | 2     | `system`             |
| Device Control     | 7+    | Various              |

---

## 🔄 Update Workflow

### Update Add-on Code

1. **Update server.py:**

   ```bash
   cd C:\MyProjects\ha-openapi-server-v3.0.0
   # Make changes to server.py
   ```

2. **Test Locally (optional):**

   ```bash
   python server.py
   # Test at http://localhost:8001
   ```

3. **Push to GitHub:**

   ```bash
   git add server.py
   git commit -m "Update to v4.0.0"
   git push origin main
   ```

4. **Update Add-on in HA:**

   - Settings → Add-ons → Home Assistant MCP Server
   - Click "Check for updates"
   - Click "Update"
   - Restart add-on

5. **Verify Update:**

   ```bash
   curl http://192.168.1.203:8001/health
   # Check version in response
   ```

6. **Restart MCPO (if needed):**
   ```bash
   ssh pi@192.168.1.11 "sudo kubectl rollout restart deployment <mcpo-deployment-name> -n cluster-services"
   ```

---

## 📚 Related Documentation

- **CHANGELOG.md** - Version history
- **CONSOLIDATION_GUIDE.md** - Migration from separate servers
- **NEW_TOOLS_REFERENCE.md** - Tool documentation
- **INTEGRATION_QUICKSTART.md** - Quick start guide
- **copilot-instructions.md** - AI assistant context

---

## 🆘 Getting Help

**Check Logs:**

1. Add-on logs: Settings → Add-ons → Home Assistant MCP Server → Logs
2. MCPO logs: `ssh pi@192.168.1.11 "sudo kubectl logs -n cluster-services -l app=mcpo --tail=100"`
3. Open-WebUI logs: `ssh pi@192.168.1.11 "sudo kubectl logs -n cluster-services -l app=open-webui --tail=100"`

**Common Success Indicators:**

- ✅ Add-on shows "Running" state
- ✅ Health check returns HTTP 200
- ✅ MCPO logs show "Successfully connected to 'homeassistant'"
- ✅ 85 tools visible in Open-WebUI
- ✅ File operations can list `/config`
- ✅ Test queries return expected data

**Common Failure Indicators:**

- ❌ Add-on shows "Stopped" or "Error"
- ❌ Health check returns connection refused
- ❌ MCPO logs show connection errors
- ❌ No homeassistant tools in Open-WebUI
- ❌ 401 Unauthorized on API calls
- ❌ "Path not found" on file operations

---

**Deployment Model:** HA Add-on (192.168.1.203:8001) ↔ MCPO (K3s cluster) ↔ Open-WebUI  
**Version:** 4.0.0  
**Last Updated:** November 1, 2025
