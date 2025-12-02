# Home Assistant OpenAPI Server Add-on

OpenAPI REST server with 97 production-ready endpoints for comprehensive Home Assistant control.

## Features

- **97 Unified Endpoints**: Complete device control, automation management, and system configuration
- **Full REST API**: All operations via POST/GET requests with Pydantic validation
- **WebSocket Support**: Real-time dashboard/Lovelace operations
- **100% Success Rate**: All tools tested and working in production
- **Open-WebUI Compatible**: Direct integration with AI assistants

## Installation

1. Add this repository to your Home Assistant Add-on Store:
   ```
   https://github.com/agarib/homeassistant-mcp-server
   ```

2. Find "Home Assistant OpenAPI Server" in Local Add-ons

3. Click Install

4. Start the add-on

5. Access the API at `http://homeassistant.local:8001`

## Configuration

```yaml
port: 8001              # HTTP port for the API server
log_level: info         # Logging level (debug|info|warning|error|critical)
```

## API Documentation

Once started, access the interactive API documentation at:
- Swagger UI: `http://homeassistant.local:8001/`
- OpenAPI Spec: `http://homeassistant.local:8001/openapi.json`

## Tool Categories (97 endpoints)

- ✅ Core HA API Tools (8 tools) - Entity states, services, events
- ✅ System Diagnostics (6 tools) - Logs, notifications, health
- ✅ Integration/Device Diagnostics (3 tools) - Config entries, devices
- ✅ Advanced API Tools (3 tools) - Templates, intents, validation
- ✅ Automations (8 tools) - Create, update, trigger, reload
- ✅ File Operations (10 tools) - Full /config access
- ✅ Add-on Management (9 tools) - Install, start, stop, logs
- ✅ Dashboards (12 tools) - Lovelace management, HACS cards
- ✅ Device Control (7 tools) - Lights, switches, climate, covers
- ✅ Logs & History (6 tools) - Entity history, diagnostics
- ✅ Discovery (4 tools) - States, areas, devices, entities
- ✅ Intelligence (4 tools) - Context, activity, comfort analysis
- ✅ Code Execution (3 tools) - Python sandbox, pandas
- ✅ Scenes (3 tools) - Activate, create, list
- ✅ Security (3 tools) - Monitoring, anomaly detection
- ✅ Camera VLM (3 tools) - Vision AI analysis
- ✅ System (3 tools) - Restart, call service
- ✅ Camera (1 tool) - Snapshots
- ✅ Utility (2 tools) - Health check, API info

## Support

- GitHub: https://github.com/agarib/homeassistant-mcp-server
- Issues: https://github.com/agarib/homeassistant-mcp-server/issues

## Version History

### 4.0.21 (2025-12-03)
- Fixed addon installation and startup issues
- Unified folder structure (ha-openapi-server)
- Complete YAML configuration
- GitHub repository deployment

### 4.0.14 (2025-11-13)
- Added 97 unified endpoints
- WebSocket support for dashboards
- 100% tool success rate achieved
