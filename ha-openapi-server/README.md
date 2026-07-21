# Home Assistant OpenAPI Server v4.1.1

OpenAPI REST server with **71 endpoints** for device control, automation,
file management, diagnostics, and AI-assisted Home Assistant interaction.

## Quick Links

- **API Docs:** http://homeassistant.local:8001/docs
- **OpenAPI Spec:** http://homeassistant.local:8001/openapi.json
- **Health Check:** http://homeassistant.local:8001/health

## Endpoint Categories

| Category | Count | Description |
|---|---|---|
| Discovery | 6 | Entity states, services, events, areas, devices |
| System | 5 | Health, config check, notifications, logs, restart |
| Device Control | 7 | Lights, switches, climate, covers, fans, media, vacuums |
| Automations | 7 | List, create, update, delete, trigger, toggle, reload |
| Scenes | 3 | Activate, create, list |
| File Management | 10 | Read, write, delete, copy, move, list, search, tree, mkdir |
| Code Execution | 3 | Python sandbox (pandas/numpy/matplotlib), state analysis, charts |
| Dashboards | 2 | Get config, create custom cards |
| Diagnostics | 3 | Config entries, devices, available diagnostics |
| Intelligence | 4 | Home context, activity recognition, comfort, energy |
| Entity Registry | 4 | Get, set, remove, exposure settings |
| History & Logs | 3 | Entity history, system logs, automation traces |
| Scripts | 3 | Get, create/update, delete scripts |
| Utilities | 2 | Template evaluation, YAML config editing |

## New in v4.1.1

- **12 new endpoints**: entity registry, history/logs, scripts, template, YAML config
- **ha_ prefix removed** from all endpoints
- **Pandas auto-install** at boot
- **Package automation support**: update/delete automations in packages/
- **History via WebSocket**: uses history/history_during_period
- **Template eval fix**: handles plain-text response correctly

## Requirements

- Home Assistant 2025.11+
- Supervisor token (auto-detected)
- Optional: pandas, numpy, matplotlib, seaborn (auto-installed)
