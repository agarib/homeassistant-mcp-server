# Quick Deployment Guide - Updated ha-mcp-server (104 tools)

## Current Status

- **Local file**: `C:\MyProjects\ha-mcp-server-addon\server.py` (4,280 lines, 104 tools) ✅ READY
- **Add-on**: Running OLD version (~3,000 lines, 78 tools) ❌ NEEDS UPDATE
- **Target**: Home Assistant at 192.168.1.203:8001

## FASTEST METHOD: Home Assistant File Editor

### Step 1: Open File Editor

1. Navigate to Home Assistant UI: `http://192.168.1.203:8123`
2. Go to: **Settings** → **Add-ons** → **ha-mcp-server**
3. Click the **"Configuration"** tab (or **"Files"** if available)

### Step 2: Locate server.py

- Look for file browser or edit option
- Navigate to: `/config/ha-mcp-server-addon/server.py` (or similar path)
- If no file browser, the add-on may be read-only

### Step 3: Replace Content

1. Open local file: `C:\MyProjects\ha-mcp-server-addon\server.py`
2. Copy ALL content (Ctrl+A, Ctrl+C) - **4,280 lines**
3. In HA File Editor, select ALL existing content (Ctrl+A)
4. Paste new content (Ctrl+V)
5. Save the file

### Step 4: Restart Add-on

1. Go to **Add-ons** → **ha-mcp-server**
2. Click **"Restart"** button
3. Wait 10-15 seconds for restart

### Step 5: Verify Deployment

Run these commands in PowerShell:

```powershell
# Test health
curl http://192.168.1.203:8001/health

# Test new REST API - should return 104 tools (was 404 before)
curl http://192.168.1.203:8001/api/actions | ConvertFrom-Json | Select-Object total_tools

# Test SSE endpoint - should stream events (was 404 before)
curl -N http://192.168.1.203:8001/subscribe_events?domain=light

# Test state API
curl http://192.168.1.203:8001/api/state
```

**Expected Results:**

- `/health` → 200 OK ✅
- `/api/actions` → `{"total_tools": 104, ...}` ✅ (was 404)
- `/subscribe_events` → SSE event stream ✅ (was 404)
- `/api/state` → State summary ✅ (was 404)

---

## ALTERNATIVE METHOD 1: Docker Exec (If Add-on Uses Container)

### Find Container

```powershell
# SSH to HA host (if SSH enabled)
ssh root@192.168.1.203

# List containers
docker ps | grep mcp

# Edit file directly
docker exec -it <container_id> vi /app/server.py
# Or copy from local
docker cp server.py <container_id>:/app/server.py

# Restart container
docker restart <container_id>
```

---

## ALTERNATIVE METHOD 2: Enable SSH & Use SCP

### Enable SSH

1. Install **"Terminal & SSH"** add-on in Home Assistant
2. Configure SSH access (port 22)
3. Add your SSH key or enable password auth

### Deploy via SCP

```powershell
# Copy file
scp C:\MyProjects\ha-mcp-server-addon\server.py root@192.168.1.203:/config/ha-mcp-server-addon/server.py

# Or use deployment script
.\deploy-to-addon.ps1
```

---

## ALTERNATIVE METHOD 3: Rebuild Add-on (If Using Local Build)

### Update & Rebuild

```powershell
# On HA host
cd /usr/share/hassio/addons/local/ha-mcp-server-addon

# Replace server.py
# (upload via HA File Editor or SCP)

# Rebuild add-on
ha addons rebuild local_ha_mcp_server

# Restart
ha addons restart local_ha_mcp_server
```

---

## Troubleshooting

### Issue: Can't find file editor in HA

**Solution**: Install **"File Editor"** add-on from Add-on Store

### Issue: server.py is read-only

**Solution**: The add-on may be installed as a system add-on. Check:

```bash
# Find actual add-on location
ha addons info local_ha_mcp_server
```

### Issue: Restart doesn't load new code

**Solution**: Rebuild the add-on or restart HA core:

```bash
ha core restart
```

### Issue: Still getting 404 on new endpoints

**Solution**: Check add-on logs for startup errors:

```bash
# Via HA UI: Add-ons → ha-mcp-server → Logs
# Via SSH:
ha addons logs local_ha_mcp_server
```

---

## What Changed (104 Tools vs 78 Tools)

### NEW Features in Updated server.py:

1. **SSE Streaming** (`/subscribe_events`) - Real-time event stream
2. **Camera VLM Tools** (5 tools) - AI vision analysis
3. **Vacuum Control** (7 tools) - start/stop/fan_speed/etc
4. **Fan Control** (6 tools) - turn_on/off/percentage/direction
5. **Add-on Management** (8 tools) - install/uninstall/start/stop via Supervisor API
6. **REST API Endpoints**:
   - `GET /api/state` - HA state summary
   - `GET /api/actions` - List all 104 tools
   - `POST /api/actions/batch` - Execute multiple actions

### Code Stats:

- **Before**: 3,008 lines, 78 tools
- **After**: 4,280 lines, 104 tools
- **Added**: 1,272 lines, 26 new tools

---

## After Deployment: Next Steps

1. ✅ Verify all endpoints work (see Step 5 above)
2. 🔄 Test MCPO connectivity: `kubectl logs -n cluster-services statefulset/mcpo-server`
3. 🎥 Test VLM camera analysis (killer feature!)
4. 📦 Test batch actions workflow
5. 📤 Commit to Git: `git commit -m "feat: 104 tools + REST API + VLM"`

---

## Quick Verification Checklist

```powershell
# Run all tests
$HAHost = "192.168.1.203"

Write-Host "Testing health..." -ForegroundColor Yellow
curl http://$HAHost:8001/health

Write-Host "`nTesting /api/actions (should show 104 tools)..." -ForegroundColor Yellow
$actions = curl http://$HAHost:8001/api/actions | ConvertFrom-Json
Write-Host "Total tools: $($actions.total_tools)" -ForegroundColor Green

Write-Host "`nTesting /api/state..." -ForegroundColor Yellow
$state = curl http://$HAHost:8001/api/state | ConvertFrom-Json
Write-Host "Total entities: $($state.total_entities)" -ForegroundColor Green

Write-Host "`nTesting SSE stream (Ctrl+C to stop)..." -ForegroundColor Yellow
curl -N http://$HAHost:8001/subscribe_events?domain=binary_sensor
```

**SUCCESS = All commands return data (no 404 errors)**
