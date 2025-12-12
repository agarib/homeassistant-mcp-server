# 🚀 v4.0.5 Enhancement Plan - Final Implementation

## Issues to Fix & Features to Add

### 1. ✅ Dashboard API Permission Issues

**Problem:** Cloud AI refuses to use dashboard tools due to permission errors

**Investigation Needed:**

- Dashboard tools use `/lovelace/` endpoints which may require different auth
- Possible solutions:
  1. Add permission checks and better error messages
  2. Document required permissions in tool descriptions
  3. Add fallback methods for read-only operations

**Current Dashboard Tools (8):**

1. `ha_list_dashboards` - List all dashboards
2. `ha_get_dashboard_config` - Get configuration
3. `ha_create_dashboard` - Create new
4. `ha_update_dashboard_config` - Update config
5. `ha_delete_dashboard` - Delete
6. `ha_list_hacs_cards` - List HACS cards
7. `ha_create_button_card` - Create button card
8. `ha_create_mushroom_card` - Create mushroom card

**Fix Strategy:**

- Add clear permission warnings in descriptions
- Better error handling with actionable messages
- Document that these require `SUPERVISOR_TOKEN` or admin token

### 2. ✅ Add Warning to ha_restart_homeassistant

**Current Issue:** Cloud AI doesn't know it will lose connection

**Solution:**
Add prominent warning in tool description:

```
⚠️ WARNING: This will restart Home Assistant!
- Connection will be lost for ~10 seconds
- OpenAPI server (this addon) will also restart
- All active sessions will disconnect
- Only use when necessary!
```

### 3. ✅ New Tools: Manual Card Creation/Editing (2 tools)

**Tool 1: ha_manual_create_custom_card**

- Purpose: Write custom card YAML manually
- Use case: Advanced users who know Lovelace YAML syntax
- Parameters: dashboard_id, view_index, card_yaml (as string)

**Tool 2: ha_manual_edit_custom_card**

- Purpose: Edit existing card YAML
- Use case: Modify card configuration directly
- Parameters: dashboard_id, view_index, card_index, card_yaml

### 4. ✅ New Tools: Diagnostics (3 tools) - **VERY IMPORTANT**

**Tool 1: ha_get_config_entry_diagnostics**

```python
@app.post("/ha_get_config_entry_diagnostics")
async def ha_get_config_entry_diagnostics(request):
    """
    Download diagnostics for a config entry (integration).
    Essential for troubleshooting integration issues.

    Example: {"entry_id": "abc123", "integration": "lg_thinq"}
    """
    # GET /api/config/config_entries/entry/{entry_id}/diagnostics
```

**Tool 2: ha_get_device_diagnostics**

```python
@app.post("/ha_get_device_diagnostics")
async def ha_get_device_diagnostics(request):
    """
    Download diagnostics for a specific device.
    Helps troubleshoot device-specific issues.

    Example: {"device_id": "abc123"}
    """
    # GET /api/config/device_registry/device/{device_id}/diagnostics
```

**Tool 3: ha_list_available_diagnostics**

```python
@app.post("/ha_list_available_diagnostics")
async def ha_list_available_diagnostics(request):
    """
    List all config entries and devices that support diagnostics.
    First step before downloading diagnostics.

    Returns: List of integrations and devices with diagnostics available
    """
    # Combine config entries + device registry
    # Filter for those with diagnostics_available
```

### 5. ✅ New Tool: Automation Reload/Validation - **VERY IMPORTANT**

**Tool: ha_reload_automations**

```python
@app.post("/ha_reload_automations")
async def ha_reload_automations(request):
    """
    Reload automations from YAML without restarting HA.
    Essential after editing automation files.

    ⚠️ This validates YAML syntax and reloads all automations
    ⚠️ Invalid YAML will cause reload to fail

    Use cases:
    - After editing automations.yaml
    - After creating new automation files
    - To validate automation syntax

    Returns: Success/failure with validation errors if any
    """
    # POST /api/services/automation/reload
    # Or: POST /api/config/automation/config/reload
```

## Implementation Checklist

- [ ] Fix dashboard tool permissions and error messages
- [ ] Add warning to ha_restart_homeassistant
- [ ] Implement ha_manual_create_custom_card
- [ ] Implement ha_manual_edit_custom_card
- [ ] Implement ha_get_config_entry_diagnostics
- [ ] Implement ha_get_device_diagnostics
- [ ] Implement ha_list_available_diagnostics
- [ ] Implement ha_reload_automations
- [ ] Update version to 4.0.5
- [ ] Update CHANGELOG
- [ ] Test all new tools
- [ ] Deploy to production

## New Tool Count

**Current:** 85 tools  
**Adding:** 7 new tools  
**Total:** 92 tools in v4.0.5

**Breakdown:**

- Manual Card Tools: 2
- Diagnostics Tools: 3
- Automation Reload: 1
- Dashboard fixes: 8 (existing, enhanced)

## Expected Impact

**Dashboard Tools:**

- Cloud AI will understand permission requirements
- Better error messages guide users to fix permissions
- Clear warnings prevent frustration

**Restart Tool:**

- Cloud AI warns user before restarting
- Users know to expect brief disconnection
- Prevents surprise connection losses

**Manual Card Tools:**

- Power users can write raw YAML
- More flexible than pre-built card helpers
- Direct control over card configuration

**Diagnostics Tools:**

- Critical for troubleshooting integrations
- Download diagnostic data for support requests
- Identify problematic devices quickly

**Automation Reload:**

- No need to restart HA after automation changes
- Validates YAML syntax automatically
- Saves time during automation development

---

**Status:** Ready for implementation
**Priority:** High (diagnostics + automation reload are critical)
**Timeline:** Can implement all in single session
