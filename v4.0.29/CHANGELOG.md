# Changelog

## v4.0.29 (2025-12-13)
### 🏗️ Major Refactoring
- **Modular Architecture**: Split the 5000+ line monolithic `server.py` into a maintainable `app/` package structure.
  - `app/core/`: Centralized configuration and clients.
  - `app/models/`: Dedicated Pydantic models for all 97 endpoints.
  - `app/routers/`: Endpoints split by functional domain (discovery, device_control, automations, etc.).
- **Configuration Management**: Introduced `pydantic-settings` for robust environment variable handling (`app/core/config.py`).
- **Improved Clients**: 
  - `HomeAssistantAPI` using `httpx` with proper error handling.
  - `HomeAssistantWebSocket` singleton with thread-safe locking and connection pooling.
- **AI Compatibility**: 
  - Added specialized `README_AI.md` guide for agents.
  - Maintained consistent `ha_` prefix for all tools.
  - Preserved parameter aliases (snake_case/camelCase) for maximizing AI success rates.

## v4.0.28 (2025-12-03)
- 🤖 **CLOUD AI COMPATIBILITY FIX**: Added parameter name aliases (`file_path` vs `filepath`).
- ✅ **FIXED**: File operation endpoints now accept both snake_case and camelCase parameter names.
- 🎯 **RESULT**: Cloud AI assistants (Claude, ChatGPT, Gemini) can now use intuitive parameter names.
- 🚀 **IMPACT**: No more 422 validation errors from AI-generated code.

## v4.0.27 (2025-12-03)
- 🎉 **CRITICAL FIX**: SUPERVISOR_TOKEN injection resolved for s6-overlay based HA installs.
- ✅ **SOLUTION**: Added fallback token reading from `/var/run/s6/container_environment/SUPERVISOR_TOKEN`.
- 🎯 **RESULT**: 100% endpoint success rate restored for Add-on deployments.

## v4.0.14 (2025-11-13)
- ✅ **ADDED**: `/ha_check_config` alias endpoint.
- ✅ **ADDED**: `/ha_system_health` endpoint.
- 📊 **ENDPOINTS**: 97 total endpoints.

## v4.0.13 (2025-11-13)
- 🐛 **FIX**: Improved `ha_create_automation` validation (min_length=1 for lists).

## v4.0.12 (2025-11-13)
- 🐛 **FIX**: Pydantic V2 deprecation warning resolved (json_schema_extra).

## v4.0.11 (2025-11-13)
- 🐛 **FIX**: Added `/ha_restart` alias for Cloud AI compatibility.

## v4.0.10 (2025-11-13)
- 🆕 **NEW**: `ha_list_files` tool with extension filtering and recursive search.
- ✅ **FIXED**: `ha_search_files` regex validation.
- ✅ **FIXED**: `ha_get_automation_details` attribute error.

## v4.0.9 (2025-11-12)
- 🐛 **FIX**: `ha_reload_automations` validation and logic.

## v4.0.8 (2025-11-11)
- 🐛 **FIX**: `ha_process_intent` endpoint path corrected for Supervisor proxy.

## v4.0.7 (2025-11-08)
- 🎉 **MILESTONE**: 100% tool success rate.
- ✅ **WEBSOCKET**: Full WebSocket client for real-time Dashboard/Lovelace operations.

## v4.0.6 (2025-11-07)
- ✅ **API COMPLIANCE**: Full alignment with official HA REST docs.
- 🆕 **NEW**: `ha_render_template`, `ha_process_intent`, `ha_validate_config`.

## v4.0.5 (2025-11-07)
- 🆕 **NEW**: Diagnostics tools (config entry, device, list available).
- 🆕 **NEW**: Automation reload without restart.
- 🆕 **NEW**: Manual custom card creation/editing.

## v4.0.4 (2025-11-02)
- 🎯 **SIMPLIFIED**: Removed `_native` suffixes. All tools use `ha_` prefix.

## v4.0.3 (2025-11-02)
- 🔧 **BREAKING**: Renamed all endpoints with `ha_` prefix to prevent conflicts.

## v4.0.2 (2025-11-01)
- 🐛 **FIX**: `get_directory_tree` typo.

## v4.0.1 (2025-11-01)
- 🐛 **FIX**: Diagnostic tool API naming.

## v4.0.0 (2025-11-01)
- 🎯 **MAJOR**: Unified architecture (FastAPI + Pydantic).
- 🔧 **CONSOLIDATED**: Replaced separate MCP/OpenAPI servers with single unified server.
