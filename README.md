# Home Assistant OpenAPI Server

[![Version](https://img.shields.io/badge/version-4.0.27-blue.svg)](https://github.com/agarib/homeassistant-mcp-server/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.11+-green.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

Production-ready REST API server with **97 unified endpoints** for complete Home Assistant control. Perfect for AI assistants, automation platforms, and custom integrations.

## ✨ Features

- **97 Production Endpoints** - Complete coverage of HA functionality (100% success rate)
- **Zero Configuration** - Auto-discovers SUPERVISOR_TOKEN from s6-overlay
- **Full REST API** - All operations via POST/GET with Pydantic validation
- **WebSocket Support** - Real-time dashboard and Lovelace operations
- **AI Assistant Ready** - OpenAPI spec for LLM tool integration
- **MCP Compatible** - Works with Model Context Protocol servers (MCPO, Claude Desktop, etc.)

## 🚀 Quick Start

### Installation

1. **Add Repository to Home Assistant:**
   ```
   https://github.com/agarib/homeassistant-mcp-server
   ```

2. **Install the Add-on:**
   - Navigate to **Settings** → **Add-ons** → **Add-on Store**
   - Find "Home Assistant OpenAPI Server" in available add-ons
   - Click **Install**

3. **Start the Add-on:**
   - Click **Start**
   - API will be available at `http://homeassistant.local:8001`

### Configuration

Minimal configuration required:

```yaml
port: 8001           # HTTP port (default: 8001)
log_level: info      # Log level (debug|info|warning|error|critical)
```

**Note:** Authentication is handled automatically via Home Assistant's Supervisor token injection.

## 📚 API Documentation

Access interactive documentation once the addon is running:

- **Swagger UI:** `http://homeassistant.local:8001/`
- **OpenAPI Spec:** `http://homeassistant.local:8001/openapi.json`
- **Health Check:** `http://homeassistant.local:8001/health`

### Example API Calls

```bash
# Get entity states
curl -X POST http://homeassistant.local:8001/ha_get_states \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Control a light
curl -X POST http://homeassistant.local:8001/ha_control_light \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "action": "turn_on", "brightness": 255}'

# Discover devices
curl -X POST http://homeassistant.local:8001/ha_discover_devices \
  -H "Content-Type: application/json" \
  -d '{"domain": "light"}'
```

## 🛠️ Endpoint Categories

| Category           | Count | Description                         |
| ------------------ | ----- | ----------------------------------- |
| Core HA API        | 8     | Entity states, services, events     |
| System Diagnostics | 6     | Logs, notifications, health checks  |
| Integrations       | 3     | Config entries, device diagnostics  |
| Advanced API       | 3     | Templates, intents, validation      |
| Automations        | 8     | Create, update, trigger, reload     |
| File Operations    | 10    | Full `/config` directory access     |
| Add-on Management  | 9     | Install, start, stop, logs          |
| Dashboards         | 12    | Lovelace management, HACS cards     |
| Device Control     | 7     | Lights, switches, climate, covers   |
| Logs & History     | 6     | Entity history, diagnostics         |
| Discovery          | 4     | States, areas, devices, entities    |
| Intelligence       | 4     | Context, activity, comfort analysis |
| Code Execution     | 3     | Python sandbox with pandas          |
| Scenes             | 3     | Activate, create, list              |
| Security           | 3     | Monitoring, anomaly detection       |
| Camera VLM         | 3     | Vision AI analysis                  |
| System             | 3     | Restart, service calls              |
| Camera             | 1     | Snapshots                           |
| Utility            | 2     | Health check, API info              |

**Option B: Using SSH/SFTP** (If available)

```powershell
# Using SCP
scp -r "C:\MyProjects\ha-mcp-server-addon" root@192.168.1.203:/config/addons/local/ha-mcp-server
```

## 🔧 Technical Details

### Architecture

- **Runtime:** Python 3 with FastAPI + Uvicorn
- **Authentication:** Automatic SUPERVISOR_TOKEN via s6-overlay
- **Validation:** Pydantic models for all requests/responses
- **API Style:** RESTful with OpenAPI 3.0 specification
- **Persistence:** Reads directly from `/config` directory

### Requirements

- Home Assistant OS or Supervised install (requires Supervisor)
- Home Assistant 2025.11 or newer
- Architecture: aarch64, amd64, armv7, armhf, i386

### Token Authentication

The addon automatically retrieves the SUPERVISOR_TOKEN from Home Assistant's s6-overlay environment store (`/var/run/s6/container_environment/`). No manual token configuration required.

## 🐛 Troubleshooting

### Common Issues

**401 Unauthorized Errors:**
- Verify the addon is running: Check addon logs for "✅ Loaded SUPERVISOR_TOKEN"
- Ensure you're using `http://homeassistant.local:8001` (not https)
- Check Home Assistant version is 2025.11+

**Addon Won't Start:**
- Check addon logs via Settings → Add-ons → Home Assistant OpenAPI Server → Log
- Verify `/config/ha-openapi-server/server.py` exists and is readable
- Try rebuilding: Settings → Add-ons → Home Assistant OpenAPI Server → Rebuild

**API Endpoints Return Errors:**
- Verify Home Assistant core is running
- Check entity IDs exist: `/ha_get_states` endpoint
- Review addon logs for detailed error messages

## 📋 Version History

### v4.0.27 (2025-12-03) - Current

- **FIXED:** SUPERVISOR_TOKEN injection via s6-overlay environment store
- **FIXED:** Authentication now works without bashio dependency
- **Added:** Automatic token fallback mechanism (SUPERVISOR_TOKEN → HASSIO_TOKEN)
- **Enhanced:** Debug logging for s6-overlay environment troubleshooting
- **Result:** 97/97 endpoints working (100% success rate restored)

### v4.0.21 (2025-12-02)

- Fixed addon installation and startup issues
- Removed bashio dependency (BOM encoding fixes)
- Unified folder structure to `ha-openapi-server`
- Complete YAML configuration for GitHub deployment

### v4.0.14 (2025-11-13)

- Initial stable release with 97 unified endpoints
- WebSocket support for dashboard operations
- Full OpenAPI specification generated

## 🤝 Integration Examples

### Use with Open-WebUI

Add as an external tool:

```text
URL: http://homeassistant.local:8001/openapi.json
Type: OpenAPI
```

### Use with MCP Server

Configure in MCPO settings:

```json
{
  "homeassistant": {
    "command": "curl",
    "args": ["-s", "http://homeassistant.local:8001/openapi.json"]
  }
}
```

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/agarib/homeassistant-mcp-server/issues)
- **Discussions:** [GitHub Discussions](https://github.com/agarib/homeassistant-mcp-server/discussions)
- **Documentation:** [Full Changelog](CHANGELOG.md)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

**Version:** 4.0.27  
**Author:** agarib  
**Repository:** https://github.com/agarib/homeassistant-mcp-server

