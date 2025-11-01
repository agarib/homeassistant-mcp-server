# Deployment Guide - Home Assistant OpenAPI Server v3.0.0

Complete guide for deploying the Home Assistant OpenAPI Server as an add-on.

## Prerequisites

- Home Assistant OS or Supervised installation
- SSH access to Home Assistant (for file copying)
- Basic understanding of Home Assistant add-ons

## Installation Methods

### Method 1: Via Local Add-on (Recommended)

This method creates a local add-on that persists across restarts.

#### Step 1: Copy Files to Home Assistant

**Via SSH:**

```bash
# Connect to Home Assistant
ssh root@YOUR_HA_IP

# Create addon directory
mkdir -p /addons/local/ha-openapi-server

# Create persistent server location
mkdir -p /config/ha-openapi-server
```

**Copy required files** to `/addons/local/ha-openapi-server/`:

- `config.json`
- `Dockerfile`
- `run.sh`
- `requirements.txt`

**Copy server.py** to `/config/ha-openapi-server/`:

- `server.py` (136 KB)

#### Step 2: Set Permissions

```bash
chmod +x /addons/local/ha-openapi-server/run.sh
chmod 644 /config/ha-openapi-server/server.py
```

#### Step 3: Install via Home Assistant UI

1. Navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click **⋮** (three dots menu) → **Repositories**
3. Click **Reload** (refresh icon)
4. Scroll down to **Local add-ons** section
5. Find **Home Assistant OpenAPI Server**
6. Click the addon → **Install**
7. Wait for installation to complete

#### Step 4: Configure

**Basic Configuration (68/77 tools):**

```json
{
  "port": 8001,
  "log_level": "info"
}
```

**Full Configuration (77/77 tools):**

```json
{
  "port": 8001,
  "log_level": "info",
  "admin_token": "YOUR_LONG_LIVED_TOKEN"
}
```

To generate admin token:

1. Profile → Security → Long-Lived Access Tokens
2. Create Token → Name: "OpenAPI Server Admin"
3. Copy token and paste into config

#### Step 5: Start the Add-on

1. Go to **Configuration** tab
2. Paste your configuration JSON
3. Click **Save**
4. Go to **Info** tab
5. Toggle **Start on boot** (optional)
6. Click **Start**

#### Step 6: Verify Installation

**Check logs:**

- Go to **Log** tab
- Look for: `🏠 Home Assistant OpenAPI Server v3.0.0`
- Should see: `✅ Using admin token` (if configured) or `⚠️ Using SUPERVISOR_TOKEN`

**Test endpoint:**

```bash
curl http://YOUR_HA_IP:8001/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "homeassistant-openapi-server",
  "version": "3.0.0",
  "timestamp": "2025-10-31T..."
}
```

### Method 2: Via File Copy (Advanced)

If you have direct file access to `/addons/local/` directory:

**Windows (via network share):**

```powershell
# Map network drive to HA
net use Z: \\YOUR_HA_IP\addons

# Copy addon files
Copy-Item -Recurse "ha-openapi-server-v3.0.0\*" "Z:\local\ha-openapi-server\"

# Copy server.py to persistent location
Copy-Item "server.py" "\\YOUR_HA_IP\config\ha-openapi-server\"
```

**Linux/Mac (via SCP):**

```bash
# Copy addon structure
scp -r config.json Dockerfile run.sh requirements.txt \
  root@YOUR_HA_IP:/addons/local/ha-openapi-server/

# Copy server.py
scp server.py root@YOUR_HA_IP:/config/ha-openapi-server/
```

## Configuration Options

### Port

Default: `8001`

```json
{
  "port": 8001
}
```

**Notes:**

- Must be between 1024-65535
- Avoid ports used by other services
- Update Open-WebUI URL if changed

### Log Level

Options: `debug`, `info`, `warning`, `error`, `critical`

```json
{
  "log_level": "info"
}
```

**Recommendations:**

- Development: `debug`
- Production: `info` or `warning`
- Troubleshooting: `debug`

### Admin Token

Optional long-lived access token for add-on management.

```json
{
  "admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Required for:**

- list_addons
- get_addon_info
- start/stop/restart_addon
- install/uninstall/update_addon
- get_addon_logs

**Without admin token:**

- 68/77 tools available
- All core features work
- Add-on management disabled

## Post-Installation

### Verify Tool Discovery

```bash
# Get OpenAPI spec
curl http://YOUR_HA_IP:8001/openapi.json

# Count endpoints
curl http://YOUR_HA_IP:8001/openapi.json | jq '.paths | length'
# Should return: 77 (with admin token) or 68 (without)
```

### Browse API Documentation

Open in browser:

- **Swagger UI:** `http://YOUR_HA_IP:8001/docs`
- **ReDoc:** `http://YOUR_HA_IP:8001/redoc`

### Test Basic Functionality

```bash
# Get all states
curl -X POST http://YOUR_HA_IP:8001/get_states \
  -H "Content-Type: application/json" \
  -d '{}'

# Control a light
curl -X POST http://YOUR_HA_IP:8001/control_light \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room",
    "action": "turn_on",
    "brightness": 128
  }'

# List automations
curl -X POST http://YOUR_HA_IP:8001/list_automations \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Integration with Open-WebUI

### Add OpenAPI Server

1. Open Open-WebUI
2. Navigate to **Settings** → **Tools**
3. Click **Add Tool** or **Import Tools**
4. Enter URL: `http://YOUR_HA_IP:8001`
5. Click **Import** or **Add**

### Verify Tools Discovered

Open-WebUI should discover:

- **With admin token:** 77 tools
- **Without admin token:** 68 tools

### Test Tool Execution

In Open-WebUI chat:

```
"Turn on the living room lights"
"What's the temperature in the bedroom?"
"List all my automations"
"Show me devices in the kitchen"
```

## Troubleshooting

### Add-on Won't Start

**Check logs:**

```bash
ha addons logs local_ha-openapi-server
```

**Common issues:**

1. **Missing server.py:**

   - Verify `/config/ha-openapi-server/server.py` exists
   - Re-copy server.py to persistent location

2. **Port conflict:**

   - Change port in configuration
   - Check `netstat -tulpn | grep 8001`

3. **Permission errors:**
   - Run: `chmod +x /addons/local/ha-openapi-server/run.sh`

### Tools Not Discovered in Open-WebUI

**Verify server is running:**

```bash
curl http://YOUR_HA_IP:8001/health
```

**Check OpenAPI spec:**

```bash
curl http://YOUR_HA_IP:8001/openapi.json
```

**Common issues:**

1. **Wrong URL:**

   - Use `http://` not `https://`
   - Verify IP address and port

2. **Firewall blocking:**

   - Check HA firewall rules
   - Verify port 8001 is accessible

3. **Open-WebUI can't reach HA:**
   - Test from Open-WebUI host: `curl http://YOUR_HA_IP:8001/health`
   - Check network connectivity

### Add-on Management Returns 403

**This is expected without admin token.**

**To fix:**

1. Generate long-lived access token in HA
2. Add to addon configuration:
   ```json
   {
     "admin_token": "YOUR_TOKEN_HERE"
   }
   ```
3. Restart addon

**Verify:**

```bash
curl -X POST http://YOUR_HA_IP:8001/list_addons \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Server Logs Show Errors

**Enable debug logging:**

```json
{
  "log_level": "debug"
}
```

**Common error patterns:**

**`httpx.HTTPStatusError: Client error '401 Unauthorized'`**

- Token not set or invalid
- Check SUPERVISOR_TOKEN in environment

**`httpx.HTTPStatusError: Client error '403 Forbidden'`**

- Admin token required for this endpoint
- Add admin_token to configuration

**`FileNotFoundError: [Errno 2] No such file`**

- Missing server.py in /config/ha-openapi-server/
- Re-copy server.py

## Updating

### Update Server Code

```bash
# Copy new server.py
scp server.py root@YOUR_HA_IP:/config/ha-openapi-server/

# Restart addon
ha addons restart local_ha-openapi-server
```

### Update Configuration

1. Go to add-on **Configuration** tab
2. Update JSON
3. Click **Save**
4. Restart add-on

### Update Requirements

```bash
# Update requirements.txt in addon folder
scp requirements.txt root@YOUR_HA_IP:/addons/local/ha-openapi-server/

# Rebuild addon
ha addons rebuild local_ha-openapi-server
```

## Uninstallation

### Via UI

1. Settings → Add-ons
2. Find **Home Assistant OpenAPI Server**
3. Click addon
4. Click **Uninstall**

### Clean Up Files

```bash
# Remove addon
rm -rf /addons/local/ha-openapi-server

# Remove persistent server (optional)
rm -rf /config/ha-openapi-server
```

## Performance Tuning

### Optimize for High Load

**Increase workers** (modify run.sh):

```bash
exec uvicorn server:app --host 0.0.0.0 --port $PORT \
  --workers 4 --log-level $LOG_LEVEL
```

### Monitor Resource Usage

```bash
# Check addon resource usage
ha addons stats local_ha-openapi-server
```

### Enable Caching (Future)

Currently not implemented, planned for v3.1.0.

## Security Considerations

### Long-Lived Token Security

**Best practices:**

- Use separate token for each service
- Rotate tokens periodically
- Revoke unused tokens
- Store tokens securely (not in git)

### Network Security

**Recommendations:**

- Use internal network only (don't expose to internet)
- Use reverse proxy with SSL if external access needed
- Implement rate limiting (planned for v3.1.0)
- Monitor access logs

### File System Access

**Notes:**

- Server has full /config access
- Be careful with file operations
- Backup config before bulk changes

## Backup and Restore

### Backup Configuration

```bash
# Backup addon config
ha addons info local_ha-openapi-server > addon-config-backup.json

# Backup server.py
cp /config/ha-openapi-server/server.py /backup/
```

### Restore Configuration

```bash
# Restore server.py
cp /backup/server.py /config/ha-openapi-server/

# Rebuild addon
ha addons rebuild local_ha-openapi-server
ha addons restart local_ha-openapi-server
```

---

**Need help?** Open an issue: https://github.com/agarib/homeassistant-mcp-server/issues
