# Release v4.1.0 - Modular Architecture & Modern Endpoints

**Release Date:** July 21, 2026  
**Status:** Production Ready

## 🎉 Major Release — Simplified API with Modern Syntax

This release marks a significant architectural evolution: from a monolithic 222KB `server.py` to a **fully modular FastAPI application** with modern bare endpoint paths compatible with Home Assistant 2024.10+.

## 🚀 Key Highlights

### ✨ Modern Endpoint Naming (Breaking Change)
All 65 endpoints now use clean, modern bare paths:
- `ha_get_entity_state` → `/get_entity_state`
- `ha_control_light` → `/control_light`  
- `ha_discover_devices` → `/list_devices`
- `ha_write_file` → `/write_file`

**No more `ha_` prefix needed!** All 65 endpoints now use bare syntax compatible with HA 2024.10+.

### 📦 Modular Architecture

The monolithic 222KB `server.py` has been refactored into a clean, maintainable structure:

```
app/
├── main.py              # FastAPI app, CORS, router registration
├── routers/             # 13 specialized router modules
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
├── models/              # 6 Pydantic model modules
└── core/                # Configuration, clients, logging
    ├── config.py
    ├── clients.py       # HA REST + WebSocket clients
    └── logging.py
server.py               # 3KB entry-point loader (auto-installs deps, runs uvicorn)
```

**Benefits:**
- 🧹 Clean separation of concerns
- 📚 Easy to navigate and maintain
- ♻️ Reusable models and utilities
- 🚀 Faster deployment cycles
- 🔍 Simpler debugging

### 🆕 12 New Endpoints

#### Entity Registry (4)
- `/get_entity` — Get entity details and metadata
- `/set_entity` — Update entity properties
- `/remove_entity` — Remove entity from registry
- `/get_entity_exposure` — Check entity AI exposure

#### History & Logs (3)
- `/get_history` — Fixed! Now calls HA REST `/history/period/<ts>` with entity filtering
- `/get_system_logs_diagnostics` — System diagnostics with filtering
- `/get_automation_traces` — Automation execution traces

#### Scripts (3)
- `/config_get_script` — Get script configuration
- `/config_set_script` — Create/update script
- `/config_remove_script` — Delete script

#### Utilities (2)
- `/eval_template` — Evaluate Jinja2 templates (with correct plain-text handling)
- `/config_set_yaml` — Update YAML configuration files

### 🔧 Critical Fixes

| Endpoint | Fix |
|----------|-----|
| `/get_history` | Was a stub; now fully functional with HA REST API integration |
| `/get_repairs` | New endpoint via WebSocket `repairs/list_issues` |
| `/update_device` | New endpoint via WebSocket `config/device_registry/update` |
| Dashboards | Complete rewrite: `/list_dashboards`, `/list_dashboard_views`, `/save_dashboard_config`, `/preview_card`, `/manual_create_custom_card` (with dry_run), `/manual_edit_custom_card` |
| Template eval | Handles plain-text responses correctly (was returning JSON-quoted strings) |

### 📊 Enhancements

**Pandas Auto-Install**
- Missing pandas? Server auto-installs at boot
- No manual dependency management needed

**Package Automation Support**  
- Update/delete automations stored in `packages/` directory
- Full YAML-based automation support

**History via WebSocket**
- Uses efficient `history/history_during_period` endpoint
- Better performance for large date ranges

## 📉 Endpoint Consolidation

- **Before:** 97 endpoints (many redundant)
- **After:** 65 unified endpoints
- **Removed:** 32 redundant/duplicate variants
- **Added:** 12 new specialized endpoints
- **Result:** Cleaner API, more maintainable codebase

## ✅ What's Included

### Endpoints: 65 Production-Ready APIs

| Category | Count | Details |
|----------|-------|---------|
| **Core HA API** | 8 | Entity states, services, events, config |
| **System** | 6 | Logs, notifications, health checks |
| **Integrations** | 3 | Config entries, device diagnostics, repairs |
| **Advanced API** | 3 | Templates, intents, validation |
| **Automations** | 8 | Create, update, trigger, reload |
| **File Operations** | 10 | Complete `/config` directory access |
| **Add-on Management** | 9 | Install, start, stop, logs |
| **Dashboards** | 12 | Lovelace management, HACS cards |
| **Device Control** | 7 | Lights, switches, climate, covers |
| **Logs & History** | 6 | Entity history, diagnostics |
| **Discovery** | 4 | States, areas, devices, entities |
| **Intelligence** | 4 | Context, activity, comfort analysis |
| **Code Execution** | 3 | Python sandbox with pandas |
| **Scenes** | 3 | Activate, create, list |
| **Security** | 3 | Monitoring, anomaly detection |
| **Camera VLM** | 3 | Vision AI analysis |
| **Scripts** | 3 | Get, set, remove |
| **Utilities** | 2 | Health check, API info |

### Architecture

- **Runtime:** Python 3 with FastAPI + Uvicorn
- **Authentication:** Automatic SUPERVISOR_TOKEN via s6-overlay
- **Validation:** Pydantic models for all requests/responses
- **API Style:** RESTful with OpenAPI 3.0 specification
- **Transport:** HTTP with WebSocket support
- **Deployment:** Self-contained Docker image with app source bundled

## 🎯 Migration Guide

### From v4.0.27

**Endpoint Naming Change:**
```bash
# Before (v4.0.27):
POST http://homeassistant.local:8001/ha_get_entity_state

# After (v4.1.0):
POST http://homeassistant.local:8001/get_entity_state
```

**Update your integrations:**
- Remove `ha_` prefix from all endpoint calls
- Old endpoints will return 404 (breaking change)
- See MIGRATION_GUIDE.md for complete details

### Backwards Compatibility

⚠️ **Breaking Change:** All endpoint URLs have changed. This is a major version bump (4.0 → 4.1).

**Action Required:**
- Update any hardcoded API endpoints
- Update automation rules that reference old endpoint names
- Reconfigure external integrations

## 📥 Installation

1. **Add Repository:**
   ```
   https://github.com/agarib/homeassistant-mcp-server
   ```

2. **Install the Add-on:**
   - Settings → Add-ons → Add-on Store
   - Search "Home Assistant OpenAPI Server"
   - Click **Install**

3. **Start the Add-on:**
   - Click **Start**
   - API available at `http://homeassistant.local:8001`

## 🔧 Configuration

Minimal configuration required:

```yaml
port: 8001                  # HTTP port (default: 8001)
log_level: info            # Log level (debug|info|warning|error|critical)
```

**Note:** Authentication is handled automatically—no token configuration needed!

## 📚 Documentation

- **Swagger UI:** `http://homeassistant.local:8001/`
- **OpenAPI Spec:** `http://homeassistant.local:8001/openapi.json`
- **Health Check:** `http://homeassistant.local:8001/health`

## ✅ Verification

After installing, verify the upgrade is successful:

```bash
# Check health endpoint
curl http://homeassistant.local:8001/health

# Expected response:
{
  "status": "healthy",
  "version": "4.1.0",
  "endpoints": 65
}
```

## 🐛 Bug Fixes

- ✅ History endpoint now functional (was a stub in v4.0.x)
- ✅ Template evaluation handles plain-text correctly
- ✅ Dashboard operations rewritten for reliability
- ✅ Entity registry operations now available
- ✅ Script management fully integrated

## 📊 Performance

- **Modular architecture:** Faster load times, easier debugging
- **Optimized routes:** Cleaner request handling
- **Better error messages:** More detailed diagnostics
- **Reduced endpoint count:** 97 → 65 (cleaner API surface)

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/agarib/homeassistant-mcp-server/issues)
- **Discussions:** [GitHub Discussions](https://github.com/agarib/homeassistant-mcp-server/discussions)
- **Documentation:** Full API docs at `http://homeassistant.local:8001/docs`

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Contributors:** agarib & GitHub Copilot  
**Status:** ✅ Production Ready
