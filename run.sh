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

# Run the MCP server
cd /app
exec python3 -u server.py
