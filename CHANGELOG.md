# Changelog

All notable changes to the Home Assistant OpenAPI Server project.

## [3.0.0] - 2025-10-31

### 🎉 Production Release

**Status:** 77/77 endpoints fully validated and production-ready

### ✨ Added

- **Comprehensive Testing Suite**
  - `Test-MCP-Servers.ps1` validation script
  - 12 comprehensive tests covering all major features
  - Automated endpoint validation

- **Complete Documentation**
  - Production-ready README with feature overview
  - API reference documentation
  - Deployment guides
  - Open-WebUI integration guide
  - Example configurations

- **Admin Token Support**
  - Optional long-lived access token configuration
  - Enables add-on management endpoints (9 tools)
  - Backward compatible with default SUPERVISOR_TOKEN

### 🔧 Fixed

- **Add-on Management (9 endpoints)**
  - Changed from direct Supervisor API to hassio API via Core
  - Fixed 403 Forbidden errors
  - Now works with admin long-lived access token
  - Endpoints: list_addons, get_addon_info, start/stop/restart_addon, install/uninstall/update_addon, get_addon_logs

- **Token Management**
  - Separate http_client for Core API (HA_TOKEN)
  - Separate supervisor_client for Supervisor API (SUPERVISOR_TOKEN) - deprecated
  - All add-on endpoints now use hassio API: `{HA_URL}/hassio/...`

### 📊 Testing Results

**With Default Token (SUPERVISOR_TOKEN):**
- 68/77 endpoints working (88%)
- All core features operational
- Add-on management disabled (expected)

**With Admin Token:**
- 77/77 endpoints working (100%)
- Full add-on management enabled
- Complete feature set

### 📚 Documentation Created

- `README.md` - Complete project overview
- `CHANGELOG.md` - This file
- `MCP_VALIDATION_COMPLETE.md` - Comprehensive validation report
- `MCP_QUICK_START.md` - Quick reference guide
- `ADDON_MANAGEMENT_FIX.md` - Admin token setup guide
- `Test-MCP-Servers.ps1` - Automated testing script

### 🔄 Changed

- Version bumped to 3.0.0
- Updated all version strings in code and configs
- Refined endpoint descriptions for clarity
- Improved error messages

---

## [2.0.0] - 2025-10-30

### 🎯 Major Rewrite

Complete rewrite from MCP/SSE hybrid to pure FastAPI/OpenAPI architecture.

### ✨ Added

- **Pure FastAPI Architecture**
  - 105 direct POST endpoints (later refined to 77)
  - Automatic OpenAPI 3.0.0 spec generation
  - Pydantic request/response validation
  - Proper HTTP error handling
  - CORS middleware enabled

- **Tool Categories**
  - Device Control (lights, switches, climate, covers)
  - File Operations (full /config access)
  - Automations (create, update, trigger, delete)
  - Scenes & Scripts
  - Media & Devices (vacuum, fan, camera, media player)
  - System (restart, service calls)
  - Code Execution (Python sandbox, YAML, templates)
  - Discovery (states, areas, devices)
  - Logs & History
  - Dashboards (Lovelace management)
  - Intelligence (context, activity, comfort, energy)
  - Security (monitoring, anomaly detection)
  - Camera VLM (vision AI)
  - Add-on Management

### 🗑️ Removed

- MCP Server-Sent Events (SSE) bridge
- Hybrid MCP/REST architecture
- Broken tool execution via SSE

### 🔧 Fixed

- Tool execution in Open-WebUI (was broken in v1.x)
- Pydantic validation errors (Union[Dict, List] issues)
- Response formatting for OpenAPI clients

---

## [1.0.3] - 2025-10-30

### Deprecated Version

MCP hybrid architecture with broken REST bridge.

**Issues:**
- SSE streaming not compatible with Open-WebUI
- Tools discovered but execution failed
- 96/105 tools broken due to architecture mismatch

**Note:** This version was deprecated and replaced by v2.0.0 pure FastAPI rewrite.

---

## [1.0.0] - 2025-10-27

### Initial Release

- MCP Server with 104 tools
- Native add-on architecture
- Direct /config filesystem access
- SSH/SFTP connection pooling (later removed)

**Issues:**
- MCP protocol not compatible with Open-WebUI tool execution
- Needed complete rewrite for OpenAPI clients

---

## Version History Summary

| Version | Date | Status | Tools | Architecture |
|---------|------|--------|-------|--------------|
| 3.0.0 | 2025-10-31 | ✅ Production | 77 | Pure FastAPI/OpenAPI |
| 2.0.0 | 2025-10-30 | ⚠️ Beta | 105→77 | FastAPI (initial) |
| 1.0.3 | 2025-10-30 | ❌ Deprecated | 105 | MCP/SSE Hybrid |
| 1.0.0 | 2025-10-27 | ❌ Deprecated | 104 | MCP Native |

---

## Migration Guide

### From v2.0.0 to v3.0.0

**No breaking changes.** This is a refinement release.

**Recommended:**
1. Update `config.json` version to 3.0.0
2. Update `server.py` to v3.0.0
3. Add `admin_token` to config if you want add-on management
4. Restart addon

### From v1.x to v3.0.0

**Complete rewrite - fresh install recommended.**

1. Stop old addon
2. Install v3.0.0 as new addon
3. Reconfigure in Open-WebUI with new endpoint
4. Test tool discovery and execution

---

## Roadmap

### Planned for v3.1.0

- [ ] Webhook support for event-driven automation
- [ ] WebSocket support for real-time updates
- [ ] Additional dashboard card types
- [ ] Blueprint automation creation
- [ ] Enhanced VLM capabilities with more models

### Under Consideration

- [ ] Multiple Home Assistant instance support
- [ ] Authentication improvements
- [ ] Rate limiting and caching
- [ ] Prometheus metrics export
- [ ] GraphQL API option

---

**Contributors:** agarib (https://github.com/agarib) & GitHub Copilot
