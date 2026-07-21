# Home Assistant OpenAPI Server

[![Version](https://img.shields.io/badge/version-4.1.1-blue.svg)](https://github.com/agarib/homeassistant-mcp-server/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.10+-green.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

Production-ready REST API server with **71 unified endpoints** for comprehensive Home Assistant control, automation, diagnostics, and AI-assisted interaction. Endpoints use **modern bare syntax** (no `ha_` prefix) compatible with Home Assistant 2024.10+.

## ✨ Features

- **71 Production Endpoints** — Device control, automations, files, dashboards, diagnostics, intelligence, code execution
- **Modern Endpoint Naming** — Bare paths (`/get_entity_state`, `/control_light`); no `ha_` prefix (HA 2024.10+)
- **Modular Architecture** — FastAPI app split into `app/routers/` (13 routers), `app/models/` (6 models), `app/core/` (config, clients, logging)
- **WebSocket + REST Hybrid** — REST for state/control, WebSocket for dashboards, repairs, device registry, history
- **Zero Configuration** — Auto-discovers SUPERVISOR_TOKEN from s6-overlay
- **Pydantic Validation** — All requests/responses validated
- **AI Assistant Ready** — OpenAPI spec for LLM tool integration
- **MCP Compatible** — Works with Model Context Protocol servers (MCPO, Claude Desktop, etc.)

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

- **Swagger UI:** `http://homeassistant.local:8001/docs`
- **OpenAPI Spec:** `http://homeassistant.local:8001/openapi.json`
- **Health Check:** `http://homeassistant.local:8001/health`

### Example API Calls (modern bare syntax)

```bash
# Get entity states
curl -X POST http://homeassistant.local:8001/get_entity_state \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Control a light
curl -X POST http://homeassistant.local:8001/control_light \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "action": "turn_on", "brightness": 255}'

# List devices
curl -X POST http://homeassistant.local:8001/list_devices \
  -H "Content-Type: application/json" \
  -d '{"domain": "light"}'
```

## 🛠️ Endpoint Categories

| Category           | Count | Description                              |
| ------------------ | ----- | ---------------------------------------- |
| Discovery          | 6     | Entity states, services, areas, devices  |
| System             | 5     | Health, config check, notifications, restart |
| Device Control     | 7     | Lights, switches, climate, covers, fans, media, vacuums |
| Automations        | 7     | List, create, update, delete, trigger, toggle, reload |
| Scenes             | 3     | Activate, create, list                   |
| File Management    | 10    | Read, write, delete, copy, move, list, search, tree, mkdir |
| Code Execution     | 3     | Python sandbox (pandas/numpy/matplotlib), state analysis, charts |
| Dashboards         | 2     | Get config, create custom cards          |
| Diagnostics        | 3     | Config entries, devices, available diagnostics |
| Intelligence       | 4     | Home context, activity recognition, comfort, energy |
| Entity Registry    | 4     | Get, set, remove, exposure settings      |
| History & Logs     | 3     | Entity history, system logs, automation traces |
| Scripts            | 3     | Get, create/update, delete scripts       |
| Utilities         | 2     | Template evaluation, YAML config editing |

## 🔧 Technical Details

### Architecture

```
ha-openapi-server/
├── config.yaml          # HA addon manifest (v4.1.1)
├── build.yaml            # HA build targets (arch base images)
├── Dockerfile            # Builds image, COPYs app/, runs from /app
├── requirements.txt      # Python deps (FastAPI, uvicorn, pandas, etc.)
├── server.py             # Entry point: loads deps, runs uvicorn app.main:app
├── README.md             # Addon-specific docs
├── PATCHES.md            # Patch documentation
└── app/
    ├── main.py           # FastAPI app, CORS, router registration
    ├── core/
    │   ├── config.py     # Settings (APP_TITLE, version, tokens)
    │   ├── clients.py    # HA REST + WebSocket clients
    │   └── logging.py    # Logger setup
    ├── routers/          # 13 endpoint routers
    │   ├── device_control.py
    │   ├── discovery.py
    │   ├── automations.py
    │   ├── file_management.py
    │   ├── system.py
    │   ├── dashboards.py
    │   ├── diagnostics.py
    │   ├── intelligence.py
    │   ├── code_execution.py
    │   ├── entity_registry.py
    │   ├── history_logs.py
    │   ├── scripts.py
    │   └── utilities.py
    └── models/           # 6 Pydantic model modules
        ├── common.py
        ├── automation.py
        ├── device.py
        ├── dashboard.py
        ├── intelligence.py
        └── utilities.py
```

- **Runtime:** Python 3 with FastAPI + Uvicorn
- **Authentication:** Automatic SUPERVISOR_TOKEN via s6-overlay
- **Validation:** Pydantic models for all requests/responses
- **API Style:** RESTful with OpenAPI 3.0 specification

### Requirements

- Home Assistant OS or Supervised install (requires Supervisor)
- Home Assistant 2024.10 or newer
- Architecture: aarch64, amd64, armv7, armhf, i386

### Token Authentication

The addon automatically retrieves the SUPERVISOR_TOKEN from Home Assistant's s6-overlay environment store (`/var/run/s6/container_environment/`). No manual token configuration required.

## 🐛 Troubleshooting

**401 Unauthorized Errors:**
- Verify the addon is running: Check addon logs for token presence
- Ensure you're using `http://homeassistant.local:8001` (not https)
- Check Home Assistant version is 2024.10+

**Addon Won't Start:**
- Check addon logs via Settings → Add-ons → Home Assistant OpenAPI Server → Log
- Try rebuilding: Settings → Add-ons → Home Assistant OpenAPI Server → Rebuild

**API Endpoints Return Errors:**
- Verify Home Assistant core is running
- Check entity IDs exist via `/list_entities`
- Review addon logs for detailed error messages

## 📋 Version History

### v4.1.1 - Current

- **12 new endpoints**: entity registry, history/logs, scripts, template, YAML config
- **`ha_` prefix removed** from all endpoints (modern bare syntax, HA 2024.10+)
- **Modular architecture**: monolithic `server.py` split into `app/routers/`, `app/models/`, `app/core/`
- **Dockerfile fix**: `COPY` app source into image (self-contained rebuilds)
- **Pandas auto-install** at boot
- **Package automation support**: update/delete automations in packages/
- **History via WebSocket**: uses history/history_during_period
- **Template eval fix**: handles plain-text response correctly

See [CHANGELOG.md](CHANGELOG.md) for older versions.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

**Version:** 4.1.1  
**Author:** agarib  
**Repository:** https://github.com/agarib/homeassistant-mcp-server