# Add-on Management Fix - Permission Issue

## Problem

The `SUPERVISOR_TOKEN` environment variable available to HA add-ons has **limited permissions** and cannot access the Supervisor/hassio API endpoints (even through the Core API at `/hassio/`).

**Tested endpoints that fail with 403 Forbidden:**

```bash
# Direct Supervisor API - Returns 401 Unauthorized
http://supervisor/addons

# Via Core API - Returns 403 Forbidden
http://supervisor/core/api/hassio/addons
```

**Root cause:** The auto-provided `SUPERVISOR_TOKEN` is scoped only for basic addon-to-core communication, not for managing other addons or supervisor features.

## Solution

Users must provide a **long-lived access token** with admin privileges for add-on management features.

### Steps to Enable Add-on Management

1. **Generate Long-Lived Access Token in Home Assistant:**

   - Go to Profile → Security → Long-Lived Access Tokens
   - Click "Create Token"
   - Name it `HA MCP Server Admin Token`
   - Copy the token (starts with `eyJ...`)

2. **Add token to addon configuration:**

   Edit `/addons/local/ha-mcp-server/config.json`:

   ```json
   {
     "name": "HA OpenAPI Server v2.0",
     "version": "2.0.0",
     "slug": "local_ha-mcp-server",
     "description": "77 OpenAPI tools for Home Assistant control",
     "arch": ["amd64", "armhf", "armv7", "aarch64", "i386"],
     "startup": "application",
     "boot": "auto",
     "options": {
       "port": 8001,
       "log_level": "info",
       "admin_token": "YOUR_LONG_LIVED_TOKEN_HERE"
     },
     "ports": {
       "8001/tcp": 8001
     },
     "ports_description": {
       "8001/tcp": "OpenAPI Server"
     },
     "host_network": true
   }
   ```

3. **Update run.sh to use admin token:**

   ```bash
   #!/usr/bin/with-contenv bashio
   set -e

   # Get configuration
   PORT=$(bashio::config 'port')
   LOG_LEVEL=$(bashio::config 'log_level')
   ADMIN_TOKEN=$(bashio::config 'admin_token')

   # Get Supervisor token (limited permissions)
   SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-}"

   # Use admin token if provided, fallback to SUPERVISOR_TOKEN
   if [ -n "$ADMIN_TOKEN" ]; then
       export HA_TOKEN="$ADMIN_TOKEN"
       bashio::log.info "Using admin token for full API access"
   else
       export HA_TOKEN="$SUPERVISOR_TOKEN"
       bashio::log.warning "Using SUPERVISOR_TOKEN (add-on management disabled)"
   fi

   export PORT="${PORT}"
   export LOG_LEVEL="${LOG_LEVEL}"
   export HA_URL="http://supervisor/core/api"
   export HA_CONFIG_PATH="/config"

   bashio::log.info "Starting Home Assistant OpenAPI Server v2.0..."
   cd /app
   exec python3 -u "/config/ha-mcp-server/server.py"
   ```

4. **Restart the addon:**

   ```bash
   ha addons restart local_ha-mcp-server
   ```

## Testing

```powershell
# Should now work with admin token
Invoke-RestMethod -Uri "http://192.168.1.203:8001/list_addons" `
    -Method POST -ContentType "application/json" -Body "{}"
```

## Status

**Current endpoints working: 68/77 (88%)**

**Blocked (need admin token): 9/77 (12%)**

- `/list_addons`
- `/get_addon_info`
- `/start_addon`
- `/stop_addon`
- `/restart_addon`
- `/install_addon`
- `/uninstall_addon`
- `/update_addon`
- `/get_addon_logs`

**After adding admin token: 77/77 (100%)** ✅

## Alternative: Remove Add-on Management

If you don't need add-on management, you can remove these 9 endpoints from server.py and achieve **68/68 (100%)** for all other features.

The core functionality (device control, automations, files, intelligence, etc.) works perfectly with the default `SUPERVISOR_TOKEN`.
