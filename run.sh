#!/usr/bin/with-contenv bashio
set -e

# Get configuration
PORT=$(bashio::config 'port')
LOG_LEVEL=$(bashio::config 'log_level')
ADMIN_TOKEN=$(bashio::config 'admin_token' || echo "")

# Get Home Assistant token from Supervisor (automatically available in addon)
SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-}"

# Use admin token if provided (for full hassio API access), otherwise use SUPERVISOR_TOKEN
if [ -n "$ADMIN_TOKEN" ]; then
    export HA_TOKEN="$ADMIN_TOKEN"
    bashio::log.info "✅ Using admin token - Full API access enabled (77/77 endpoints)"
else
    export HA_TOKEN="$SUPERVISOR_TOKEN"
    bashio::log.warning "⚠️  Using SUPERVISOR_TOKEN - Add-on management disabled (68/77 endpoints)"
    bashio::log.warning "    To enable add-on management, add 'admin_token' to addon options"
fi

# Export environment variables
export PORT="${PORT}"
export LOG_LEVEL="${LOG_LEVEL}"
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN}"
export HA_URL="http://supervisor/core/api"
export HA_CONFIG_PATH="/config"

bashio::log.info "Starting Home Assistant OpenAPI Server v2.0..."
bashio::log.info "Port: ${PORT}"
bashio::log.info "Log Level: ${LOG_LEVEL}"
bashio::log.info "Config Path: ${HA_CONFIG_PATH}"
bashio::log.info "Token available: $([ -n "$HA_TOKEN" ] && echo 'YES' || echo 'NO')"

# Use server.py from /config if it exists (persistent across restarts)
# Otherwise create a symlink to trigger manual deployment
if [ -f "/config/ha-mcp-server/server.py" ]; then
    bashio::log.info "Using persistent server.py from /config/ha-mcp-server/server.py"
    SERVER_PY="/config/ha-mcp-server/server.py"
else
    bashio::log.warning "No server.py found in /config/ha-mcp-server/"
    bashio::log.warning "    Please copy your server.py to /config/ha-mcp-server/server.py"
    bashio::log.warning "    mkdir -p /config/ha-mcp-server && cp server.py /config/ha-mcp-server/"
    exit 1
fi

# Run the OpenAPI server
cd /app
exec python3 -u "${SERVER_PY}"
