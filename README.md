# Home Assistant MCP Server Add-on

**Stop patching SSH connection issues. Run the MCP server natively inside Home Assistant.**

## 🎯 Why This Add-on?

### The Old Way (SSH/SFTP) - Unreliable ❌

```
MCPO (Pi4/Pi5) → Network → SSH Service (port 22) → Home Assistant
                   ↓         ↓                        ↓
               Routing    Auth/Pool              /config
               Issues    Exhaustion               Files
```

**Problems:**

- SSH service availability issues (connection refused)
- Network routing complexity (hostNetwork hacks)
- Connection pool exhaustion
- Authentication failures
- Paramiko dependency issues
- **Constant patching required**

### The New Way (Native Add-on) - Bulletproof ✅

```
MCPO (Pi4/Pi5) → HTTP → HA MCP Add-on (runs INSIDE HA) → Direct /config Access
                   ↓              ↓                              ↓
               Simple        Localhost Only                Native Python I/O
               Reliable      HA Context                    Always Available
```

**Benefits:**

- ✅ **Zero network issues** (all localhost)
- ✅ **No SSH service dependency**
- ✅ **No authentication complexity**
- ✅ **No connection pool problems**
- ✅ **Always available** (runs inside HA)
- ✅ **Direct file access** (native OS operations)
- ✅ **Simpler configuration**
- ✅ **More reliable**
- ✅ **No maintenance required**

---

## 📦 What This Add-on Provides

### 74 MCP Tools - Complete Home Control

**✅ FULLY INTEGRATED** - All 62 converted tools from external server + 12 native tools

**Part 1 - Discovery & Control (18 tools):**

- Device discovery, area management, state monitoring
- Light, switch, climate, cover control
- Adaptive & circadian lighting
- Multi-room sync, presence-based automation
- Media player control, multi-room audio, party mode
- Smart thermostat, zone climate, air quality

**Part 2 - Automation & Intelligence (35 tools):**

- Security monitoring, anomaly detection, vacation mode
- Automation lifecycle (list, create, update, delete, trigger)
- System logs, diagnostics, entity history
- Scenes & scripts execution
- Morning/evening/bedtime routines
- Home context analysis, activity recognition
- Comfort & energy optimization
- Predictive maintenance, weather integration
- Synchronized home state, follow-me, guest & movie modes

**Part 3 - Dashboard & HACS (9 tools):**

- Dashboard discovery & listing
- HACS card management
- Button-card & Mushroom-card creation
- Standard card creation & editing
- Dashboard configuration inspection

**Original Native Tools (12 tools):**

- Complete file management (read, write, list, tree, create, delete, move, copy, search)
- Home Assistant API (get_states, get_state, call_service)

---

## 🚀 Installation

### Step 1: Copy Add-on to Home Assistant

**Option A: Using Samba Share** (Recommended)

```powershell
# From Windows
Copy-Item -Path "C:\MyProjects\ha-mcp-server-addon" -Destination "\\192.168.1.203\config\addons\local\ha-mcp-server" -Recurse
```

**Option B: Using SSH/SFTP** (If available)

```powershell
# Using SCP
scp -r "C:\MyProjects\ha-mcp-server-addon" root@192.168.1.203:/config/addons/local/ha-mcp-server
```

**Option C: Manual Copy**

1. Access Home Assistant file system (Samba, SSH, or File Editor add-on)
2. Create directory: `/config/addons/local/ha-mcp-server/`
3. Copy all files from `ha-mcp-server-addon/` to the new directory

### Step 2: Add Local Repository in Home Assistant

1. Open Home Assistant: <http://192.168.1.203:8123>
2. Go to **Settings** → **Add-ons**
3. Click **⋮** (three dots, top right) → **Repositories**
4. Add local repository path: `/config/addons/local`
5. Click **ADD**

### Step 3: Install Add-on

1. Refresh the Add-on Store page
2. Scroll down to **Local add-ons** section
3. Click **Home Assistant MCP Server**
4. Click **INSTALL**
5. Wait for installation to complete

### Step 4: Configure Add-on

**Configuration Tab:**

```yaml
port: 8001
log_level: info
```

**Options:**

- `port`: HTTP port (default: 8001)
- `log_level`: Logging level (debug/info/warning/error)

### Step 5: Start Add-on

1. Click **START** button
2. Enable **Start on boot** (optional but recommended)
3. Enable **Watchdog** (optional, auto-restart on failure)

### Step 6: Verify Add-on is Running

**Check Logs:**

```
[INFO] Starting Home Assistant MCP Server...
[INFO] Supervisor URL: http://supervisor
[INFO] Config path: /config
[INFO] Starting server on port 8001...
[INFO] Server ready at http://localhost:8001
```

**Test Endpoint:**

```powershell
# From your PC or Pi cluster
curl http://192.168.1.203:8001/health

# Expected response:
# {"status":"healthy","service":"ha-mcp-server","version":"1.0.0"}
```

---

## 🔧 Update MCPO Configuration

### Current MCPO Configuration (SSH-based)

Your current `mcpo-config-updated.yaml` has:

```yaml
"homeassistant":
  {
    "command": "python3",
    "args": ["/workspace/homeassistant-mcp/server.py"],
    "env":
      {
        "HA_URL": "http://192.168.1.203:8123",
        "HA_TOKEN": "eyJhbGci...",
        "HA_SSH_HOST": "192.168.1.203",
        "HA_SSH_PORT": "22",
        "HA_SSH_USER": "root",
        "HA_SSH_PASSWORD": "your_ssh_password",
        "HA_CONFIG_PATH": "/config",
      },
  }
```

### New MCPO Configuration (HTTP-based)

Replace with:

```yaml
"homeassistant":
  {
    "command": "npx",
    "args":
      ["-y", "@modelcontextprotocol/client-http", "http://192.168.1.203:8001"],
    "env": { "HA_URL": "http://192.168.1.203:8123", "HA_TOKEN": "eyJhbGci..." },
  }
```

**What changed:**

- ❌ Removed: `HA_SSH_HOST`, `HA_SSH_PORT`, `HA_SSH_USER`, `HA_SSH_PASSWORD`
- ❌ Removed: `/workspace/homeassistant-mcp/server.py` (no longer runs in MCPO)
- ✅ Changed: Use MCP HTTP client to connect to add-on at port 8001
- ✅ Kept: `HA_URL` and `HA_TOKEN` (may still be used by other tools)

### Apply Updated Configuration

```powershell
# Edit the config
notepad C:\MyProjects\mcpo-config-updated.yaml

# Apply to cluster
kubectl apply -f C:\MyProjects\mcpo-config-updated.yaml

# Restart MCPO pods to pick up new config
kubectl rollout restart statefulset mcpo-server -n cluster-services

# Watch pods restart
kubectl get pods -n cluster-services -w
```

### Verify MCPO Connection

```bash
# Check MCPO logs for successful connection
kubectl logs -n cluster-services mcpo-server-0 | grep homeassistant

# Expected output:
# [INFO] Successfully connected to 'homeassistant' server
# [INFO] homeassistant available at /homeassistant
```

---

## ✅ Testing

### Test 1: File Read

```bash
# From Open-WebUI connected to MCPO
# Use tool: read_file
# Arguments: {"filepath": "configuration.yaml"}
# Expected: Contents of /config/configuration.yaml
```

### Test 2: File Write

```bash
# Use tool: write_file
# Arguments: {
#   "filepath": "ai_test.txt",
#   "content": "Hello from HA MCP Add-on!",
#   "backup": true
# }
# Expected: File created at /config/ai_test.txt
#          Backup created at /config/ai_test.txt.backup.TIMESTAMP
```

### Test 3: Directory Listing

```bash
# Use tool: list_directory
# Arguments: {"path": "/config/packages"}
# Expected: List of all files in /config/packages/
```

### Test 4: Home Assistant State

```bash
# Use tool: get_state
# Arguments: {"entity_id": "light.couch_light"}
# Expected: Current state of the light
```

### Test 5: Control Light

```bash
# Use tool: control_light
# Arguments: {
#   "entity_id": "light.couch_light",
#   "action": "turn_on",
#   "brightness": 255
# }
# Expected: Light turns on at full brightness
```

---

## 🔍 Troubleshooting

### Issue 1: Add-on Won't Start

**Check logs:**

```bash
# In Home Assistant UI
Settings → Add-ons → Home Assistant MCP Server → Logs
```

**Common causes:**

- Port 8001 already in use → Change port in configuration
- Python dependencies failed → Check Dockerfile and requirements.txt
- Permission issues → Ensure /config is mounted with `rw` in config.json

### Issue 2: MCPO Can't Connect

**Verify add-on endpoint:**

```powershell
curl http://192.168.1.203:8001/health
```

**Check MCPO config:**

```bash
kubectl get configmap mcpo-config -n cluster-services -o yaml
```

**Verify MCPO pods restarted:**

```bash
kubectl get pods -n cluster-services
# Both pods should have recent restart time
```

### Issue 3: File Operations Fail

**Check add-on has /config access:**

```bash
# In add-on logs, should see:
[INFO] Config path: /config
[INFO] Config path exists: True
[INFO] Config path is directory: True
```

**Verify file permissions:**

```bash
# SSH into Home Assistant
ls -la /config
# Ensure add-on user has read/write permissions
```

---

## 🎓 Architecture Details

### How It Works

```
┌─────────────────────────────────────────────────┐
│          Home Assistant (192.168.1.203)         │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │     HA MCP Server Add-on (Container)     │  │
│  │                                           │  │
│  │  ┌─────────────┐    ┌──────────────┐    │  │
│  │  │ FileManager │    │ HomeAssistant│    │  │
│  │  │             │    │     API      │    │  │
│  │  │ Direct I/O  │    │  (localhost) │    │  │
│  │  └─────┬───────┘    └──────┬───────┘    │  │
│  │        │                   │             │  │
│  │        ↓                   ↓             │  │
│  │   /config (mounted)   localhost:8123    │  │
│  │                                           │  │
│  │  Exposes: HTTP :8001                     │  │
│  └──────────────┬────────────────────────────┘  │
│                 │                                │
└─────────────────┼────────────────────────────────┘
                  │
                  │ HTTP
                  ↓
         ┌────────────────┐
         │  MCPO (Pi4/5)  │
         │                │
         │  Uses MCP HTTP │
         │  Client        │
         └────────────────┘
```

### Security Model

**Add-on runs in Home Assistant's security context:**

- Has direct access to `/config` via mounted volume
- Uses Supervisor API token for HA API calls
- No external network exposure (only internal :8001)
- Path validation prevents directory traversal
- Automatic backups before file writes

---

## 📚 Complete Tool Reference

### File Management Tools

#### 1. read_file

Read contents of any file in /config

**Arguments:**

```json
{
  "filepath": "string (relative to /config)"
}
```

**Example:**

```json
{
  "filepath": "configuration.yaml"
}
```

**Returns:** File contents as string

---

#### 2. write_file

Write or update file with automatic backup

**Arguments:**

```json
{
  "filepath": "string",
  "content": "string",
  "backup": "boolean (optional, default: true)"
}
```

**Example:**

```json
{
  "filepath": "packages/ai_package.yaml",
  "content": "automation:\n  - alias: Test\n",
  "backup": true
}
```

**Returns:** Success message with backup location

**Note:** Creates timestamped backup before writing (e.g., `file.yaml.backup.20250122_143052`)

---

#### 3. list_directory

List files and folders in directory

**Arguments:**

```json
{
  "path": "string (relative to /config)"
}
```

**Example:**

```json
{
  "path": "packages"
}
```

**Returns:** Array of entries with name, type, size, modified time

---

#### 4. get_directory_tree

Get recursive directory tree structure

**Arguments:**

```json
{
  "path": "string",
  "max_depth": "integer (optional, default: 3)"
}
```

**Example:**

```json
{
  "path": "packages",
  "max_depth": 2
}
```

**Returns:** Nested tree structure with all files and folders

---

#### 5. create_directory

Create directory (with parent directories if needed)

**Arguments:**

```json
{
  "path": "string"
}
```

**Example:**

```json
{
  "path": "packages/new_area/devices"
}
```

**Returns:** Success message

---

#### 6. delete_file

Delete file or directory

**Arguments:**

```json
{
  "path": "string"
}
```

**Example:**

```json
{
  "path": "packages/old_automation.yaml"
}
```

**Returns:** Success message

**Warning:** For directories, deletes recursively (including all contents)

---

#### 7. move_file

Move or rename file/directory

**Arguments:**

```json
{
  "source": "string",
  "destination": "string"
}
```

**Example:**

```json
{
  "source": "packages/temp.yaml",
  "destination": "packages/living_room/lights.yaml"
}
```

**Returns:** Success message

---

#### 8. copy_file

Copy file or directory

**Arguments:**

```json
{
  "source": "string",
  "destination": "string"
}
```

**Example:**

```json
{
  "source": "packages/template.yaml",
  "destination": "packages/new_automation.yaml"
}
```

**Returns:** Success message

---

#### 9. search_files

Search file contents (grep-like)

**Arguments:**

```json
{
  "path": "string (directory to search)",
  "pattern": "string (text or regex)",
  "file_pattern": "string (optional, e.g., '*.yaml')"
}
```

**Example:**

```json
{
  "path": "packages",
  "pattern": "light.couch_light",
  "file_pattern": "*.yaml"
}
```

**Returns:** Array of matches with file, line number, content

---

### Home Assistant API Tools

#### 10. get_states

Get all entity states

**Arguments:** None

**Returns:** Array of all entity states with attributes

---

#### 11. get_state

Get specific entity state

**Arguments:**

```json
{
  "entity_id": "string"
}
```

**Example:**

```json
{
  "entity_id": "light.couch_light"
}
```

**Returns:** Entity state with attributes

---

#### 12. call_service

Call any Home Assistant service

**Arguments:**

```json
{
  "domain": "string",
  "service": "string",
  "entity_id": "string (optional)",
  "data": "object (optional)"
}
```

**Example:**

```json
{
  "domain": "light",
  "service": "turn_on",
  "entity_id": "light.couch_light",
  "data": {
    "brightness": 255,
    "rgb_color": [255, 0, 0]
  }
}
```

**Returns:** Service call result

---

#### 13. control_light

Control lights (convenience wrapper)

**Arguments:**

```json
{
  "entity_id": "string",
  "action": "turn_on | turn_off",
  "brightness": "integer (0-255, optional)",
  "rgb_color": "[r, g, b] (optional)",
  "color_temp": "integer (optional)"
}
```

**Example:**

```json
{
  "entity_id": "light.couch_light",
  "action": "turn_on",
  "brightness": 128,
  "rgb_color": [255, 200, 100]
}
```

**Returns:** Service call result

---

## 🎉 Success Criteria

**You'll know it's working when:**

✅ Add-on shows as **Running** in Home Assistant
✅ Add-on logs show: `Server ready at http://localhost:8001`
✅ `curl http://192.168.1.203:8001/health` returns JSON
✅ MCPO logs show: `Successfully connected to 'homeassistant'`
✅ Open-WebUI can execute file read/write tools
✅ File operations complete without SSH errors
✅ **No more SSH connection issues forever!** 🎊

---

## 📝 What Gets Eliminated

With this add-on deployed:

❌ No more `HA_SSH_HOST`, `HA_SSH_PORT`, `HA_SSH_USER`, `HA_SSH_PASSWORD`
❌ No more paramiko library
❌ No more SSH connection pool code
❌ No more connection retry logic
❌ No more hostNetwork hacks in MCPO
❌ No more SSH service monitoring
❌ No more authentication failures
❌ No more network routing issues
❌ **No more patching SSH problems!**

✅ **Just simple, reliable HTTP endpoint that always works**

---

## 🛠️ Development

### Local Testing

```bash
# Test server locally (on your PC)
cd C:\MyProjects\ha-mcp-server-addon
python server.py

# Or in WSL
cd /mnt/c/MyProjects/ha-mcp-server-addon
python3 server.py
```

### Rebuild Add-on

```bash
# After code changes
# 1. Copy updated files to HA
# 2. In HA, go to Add-on → Home Assistant MCP Server
# 3. Click "Rebuild"
# 4. Click "Restart"
```

---

## 📞 Support

**If you encounter issues:**

1. Check add-on logs in Home Assistant UI
2. Verify endpoint: `curl http://192.168.1.203:8001/health`
3. Check MCPO configuration updated correctly
4. Verify MCPO pods restarted after config change
5. Test file operations manually via curl/Postman

**This add-on eliminates the root cause of SSH issues. Once deployed, you should never need to troubleshoot connection problems again!**

---

**Version:** 1.0.0
**Author:** agarib (homeassistant-mcp-server project)
**License:** MIT
**Repository:** <https://github.com/agarib/homeassistant-mcp-server>
