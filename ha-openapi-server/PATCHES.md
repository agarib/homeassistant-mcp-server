# OpenAPI Server Patches — Permanent Documentation

## Server Info
- **Version**: 4.1.0 (HA update entity shows 4.0.27 due to HA registry not updated)
- **Location**: HA addon `e115a97f_ha-openapi-server`, files at `/config/ha-openapi-server/`
- **Restart**: `call_service("hassio", "addon_restart", addon="e115a97f_ha-openapi-server")`

## Patched Files

### 1. `app/routers/history_logs.py` — Fixed /get_history
**Problem**: `/get_history` was a stub returning "requires direct HA access" instead of actual history data.
**Fix**: Implemented real history fetch via HA REST API `/history/period/<timestamp>` with query params for entity filtering, minimal_response, and significant_changes_only.
**Original**: Stub returning hardcoded message.
**Patched**: Calls `ha_api.call_api("GET", f"/history/period/{quote(start_str)}?filter_entity_id=...")`.

### 2. `app/routers/system.py` — Added /get_repairs
**Problem**: No endpoint to list HA repair issues (Spook warnings, config errors, etc.).
**Fix**: Added `/get_repairs` endpoint using WebSocket command `repairs/list_issues`.
**New code appended** (after existing endpoints):
- `GetRepairsRequest` model (active_only filter)
- `ha_get_repairs()` function calling `ws.call_command("repairs/list_issues")`

### 3. `app/routers/device_control.py` — Added /update_device
**Problem**: No endpoint to rename devices or reassign areas in the device registry.
**Fix**: Added `/update_device` endpoint using WebSocket command `config/device_registry/update`.
**Import fix**: Added `get_ws_client` to the import from `app.core.clients`.
**New code appended** (after existing endpoints):
- `UpdateDeviceRequest` model (device_id, name_by_user, area_id)
- `ha_update_device()` function calling `ws.call_command("config/device_registry/update", **params)`

### 4. `app/routers/dashboards.py` — Rewritten with real dashboard tools
**Problem**: `/manual_create_custom_card` was a stub ("simulation"). No dashboard listing, no preview, no save.
**Fix**: Complete rewrite with:
- `/list_dashboards` — lists all Lovelace dashboards via `lovelace/dashboards/list`
- `/list_dashboard_views` — lists views/tabs in a dashboard with card counts
- `/get_dashboard_config` — fetches full dashboard config (existing, kept)
- `/save_dashboard_config` — saves full dashboard config via `lovelace/config/save`
- `/manual_create_custom_card` — creates card with `dry_run` support (parse YAML → insert into view → optionally save)
- `/preview_card` — dry-run only (parse YAML → show where card would go → don't save)
- `/manual_edit_custom_card` — replaces existing card at specified index

### 5. `app/models/dashboard.py` — Added dry_run field
**Fix**: Added `dry_run: Optional[bool]` to `ManualCreateCustomCardRequest` model.

## Backup
All patched files backed up at: `/config/ha-openapi-server/patches_backup/`
Original files: `*_orig.py` in same directory.

## Restore After Addon Update
If the addon updates and overwrites these patches:
1. Re-apply from this documentation or from the backup files
2. Restart the addon: `curl -X POST http://192.168.1.203:8001/call_service -H "Content-Type: application/json" -d '{"domain":"hassio","service":"addon_restart","service_data":{"addon":"e115a97f_ha-openapi-server"}}'`

## Verification
After restart, check all endpoints are live:
```bash
curl -s http://192.168.1.203:8001/openapi.json | python -c "import sys,json; d=json.load(sys.stdin); p=d['paths']; [print(f'  {k}: {\"✅\" if k in p else \"❌\"}') for k in ['/get_repairs','/update_device','/list_dashboards','/preview_card','/save_dashboard_config','/list_dashboard_views']]"
```
