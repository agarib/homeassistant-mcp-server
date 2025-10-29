#!/usr/bin/with-contenv bashio
set -e

# Get configuration
PORT=$(bashio::config 'port')
LOG_LEVEL=$(bashio::config 'log_level')

# Get Home Assistant token from Supervisor
SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-}"

# Export environment variables
export PORT="${PORT}"
export LOG_LEVEL="${LOG_LEVEL}"
export HA_TOKEN="${SUPERVISOR_TOKEN}"
export HA_URL="http://supervisor/core/api"
export HA_CONFIG_PATH="/config"

bashio::log.info "Starting Home Assistant MCP Server..."
bashio::log.info "Port: ${PORT}"
bashio::log.info "Log Level: ${LOG_LEVEL}"
bashio::log.info "Config Path: ${HA_CONFIG_PATH}"

# Use server.py from /config if it exists (persistent across restarts)
# Otherwise create a symlink to trigger manual deployment
if [ -f "/config/ha-mcp-server/server.py" ]; then
    bashio::log.info "✅ Using persistent server.py from /config/ha-mcp-server/server.py"
    SERVER_PY="/config/ha-mcp-server/server.py"
else
    bashio::log.warning "⚠️  No server.py found in /config/ha-mcp-server/"
    bashio::log.warning "    Please copy your server.py to /config/ha-mcp-server/server.py"
    bashio::log.warning "    mkdir -p /config/ha-mcp-server && cp server.py /config/ha-mcp-server/"
    exit 1
fi

# Run the MCP server
cd /app
exec python3 -u "${SERVER_PY}"
