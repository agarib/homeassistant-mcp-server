# 404 TROUBLESHOOTING GUIDE

## ✅ ISSUE RESOLVED IN v4.0.4

This document described 404 errors caused by the `_native` suffix on 8 endpoints.

**As of v4.0.4 (2025-11-02):**
- The confusing `_native` suffix has been REMOVED
- All endpoints now use simple `ha_` prefix only
- No more special naming cases to remember

**Old naming (v4.0.3):**
```
ha_get_services_native
ha_get_entity_state_native
ha_list_entities_native
ha_fire_event_native
ha_render_template_native
ha_get_config_native
ha_get_history_native
ha_get_logbook_native
```

**New naming (v4.0.4+):**
```
ha_get_services          ← Simplified!
ha_get_entity_state      ← Simplified!
ha_list_entities         ← Simplified!
ha_fire_event            ← Simplified!
ha_render_template       ← Simplified!
ha_get_config            ← Simplified!
ha_get_history           ← Simplified!
ha_get_logbook           ← Simplified!
```

**Result:** Clean, consistent API with no confusing suffixes.

---

## Historical Context (Pre-v4.0.4)

This file was created to help troubleshoot 404 errors when AI assistants forgot the `_native` suffix. The suffix was causing significant confusion and was ultimately deemed unnecessary ("All come from same server anyway").

See CHANGELOG.md for v4.0.4 release notes.

These 8 endpoints were originally from the MCP (Model Context Protocol) native server and were converted to OpenAPI/FastAPI format. They retained the `_native` suffix to:

1. Distinguish them from other HA API wrapper endpoints
2. Maintain compatibility with existing documentation
3. Make it clear they're direct MCP protocol conversions

### How to verify endpoints exist:

```bash
# Check OpenAPI spec
curl http://192.168.1.203:8001/openapi.json | jq '.paths | keys'

# Or visit the docs
open http://192.168.1.203:8001/docs
```

### Complete list of \_native endpoints (8 total):

| Endpoint                     | Purpose                 | Example                                           |
| ---------------------------- | ----------------------- | ------------------------------------------------- |
| `ha_get_entity_state_native` | Get state of any entity | `{"entity_id": "light.living_room"}`              |
| `ha_list_entities_native`    | List all entities       | `{"domain": "light"}` (optional)                  |
| `ha_get_services_native`     | List available services | `{}`                                              |
| `ha_fire_event_native`       | Fire custom event       | `{"event_type": "my_event", "event_data": {...}}` |
| `ha_render_template_native`  | Render Jinja2 template  | `{"template": "{{ states('sensor.temp') }}"}`     |
| `ha_get_config_native`       | Get HA configuration    | `{}`                                              |
| `ha_get_history_native`      | Get entity history      | `{"entity_id": "...", "start_time": "..."}`       |
| `ha_get_logbook_native`      | Get logbook entries     | `{"entity_id": "...", "start_time": "..."}`       |

### Other tools that ALSO have specific naming:

**Diagnostics tools (no \_native, but specific naming):**

- `ha_get_system_logs_diagnostics` (not `ha_get_system_logs`)
- `ha_get_persistent_notifications`
- `ha_get_integration_status`
- `ha_get_startup_errors`

**File operations (no \_native):**

- `ha_write_file` (NOT `tool_write_file`)
- `ha_read_file` (NOT `tool_read_file`)
- `ha_list_directory` (NOT `tool_list_files`)

### Quick Test:

```python
import requests

# ❌ This will fail with 404
response = requests.post(
    "http://192.168.1.203:8001/ha_get_services",
    json={}
)
# Result: 404 Not Found

# ✅ This will work
response = requests.post(
    "http://192.168.1.203:8001/ha_get_services_native",
    json={}
)
# Result: 200 OK
```

### For Open-WebUI AI Assistants:

If you're getting 404 errors:

1. Check if you're missing the `_native` suffix
2. Verify the endpoint name matches exactly
3. All endpoints except `/health` and `/` have the `ha_` prefix
4. 8 specific endpoints require `_native` suffix
5. Refer to AI_TRAINING_EXAMPLES.md for complete list

### Verification Checklist:

- [ ] Does the endpoint start with `ha_`?
- [ ] If it's a native endpoint, does it end with `_native`?
- [ ] Are you using POST method (not GET)?
- [ ] Is your JSON payload correct?
- [ ] Are you testing against the right URL (http://192.168.1.203:8001)?

### Still Getting 404?

Check the OpenAPI spec to see all available endpoints:

```bash
curl http://192.168.1.203:8001/openapi.json | jq '.paths | keys' | grep "ha_"
```

Or use the interactive docs:
http://192.168.1.203:8001/docs
