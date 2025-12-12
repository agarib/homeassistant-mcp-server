# v4.0.5 Planning - Diagnostics & Dashboard Polish

**Date:** November 2, 2025  
**Goal:** Polish existing tools, add diagnostic capabilities, enhance dashboards  
**Philosophy:** Research → Polish → Fill gaps → Keep it simple & consistent

## 🎯 Primary Objectives

### 1. Integration Diagnostics (NEW)

**Reference:** https://developers.home-assistant.io/docs/core/integration_diagnostics/

Home Assistant integrations can provide diagnostics to help troubleshoot issues. Two types:

#### Config Entry Diagnostics

- Download from integration config entry options menu
- Returns redacted entry data + runtime data
- Helps diagnose integration-level issues

#### Device Diagnostics

- Download from device info section
- Returns device-specific diagnostic data
- Falls back to config entry diagnostics if not implemented

**Proposed Tools:**

```python
# 1. Get config entry diagnostics
POST /ha_get_config_entry_diagnostics
{
    "config_entry_id": "abc123",
    "integration": "lg_thinq"  # optional, for filtering
}

# 2. Get device diagnostics
POST /ha_get_device_diagnostics
{
    "device_id": "device_xyz",
    "integration": "lg_thinq"  # optional
}

# 3. List available diagnostics
POST /ha_list_diagnostics
{
    "integration": "lg_thinq"  # optional filter
}
```

**API Endpoints to Research:**

- `/api/diagnostics/config_entry/{entry_id}` - Download config entry diagnostics
- `/api/diagnostics/device/{device_id}` - Download device diagnostics
- Need to investigate if there's a list endpoint

**Implementation Notes:**

- Auto-redacts sensitive data (API keys, tokens, etc.)
- Returns JSON diagnostic data
- May need authentication with admin token
- Should handle integrations that don't support diagnostics gracefully

---

### 2. Dashboard Tools Enhancement

**Current Issue:** Dashboard tools need proper permissions

**Existing Tools (8 total):**

- `ha_create_dashboard`
- `ha_update_dashboard`
- `ha_delete_dashboard`
- `ha_list_dashboards`
- `ha_get_dashboard`
- `ha_create_dashboard_card`
- `ha_update_dashboard_card`
- `ha_delete_dashboard_card`

**Problems to Investigate:**

- [ ] What permissions are needed?
- [ ] Are we using correct API endpoints?
- [ ] Do we need admin token vs supervisor token?
- [ ] Are there missing dashboard operations?

**Potential Additions:**

- `ha_duplicate_dashboard` - Clone existing dashboard
- `ha_export_dashboard` - Export dashboard YAML
- `ha_import_dashboard` - Import dashboard from YAML
- `ha_get_dashboard_views` - List views in a dashboard
- `ha_reorder_dashboard_cards` - Change card order

**Research Needed:**

- Dashboard API documentation
- Lovelace dashboard structure
- Permission requirements
- YAML vs UI dashboard differences

---

### 3. Tool Polish & Gap Analysis

**Approach:**

1. Review all 85 existing tools
2. Identify gaps in functionality
3. Enhance tools that need it (without overcomplicating)
4. Ensure naming consistency

**Areas to Review:**

#### File Operations (9 tools)

- ✅ Naming consistent (`ha_read_file`, `ha_write_file`, etc.)
- 🔍 Check: Any missing operations? (chmod, file stats, etc.)

#### Add-on Management (9 tools)

- ✅ Naming consistent
- 🔍 Check: Backup/restore operations?
- 🔍 Check: Add-on configuration management?

#### Automation Tools (10 tools)

- ✅ Good coverage
- 🔍 Check: Automation enable/disable?
- 🔍 Check: Automation history/last triggered?

#### Device Control (7 tools)

- ✅ Good coverage
- 🔍 Check: Any device types missing? (locks, alarms, humidifiers, etc.)

#### Discovery & State (4 tools)

- ✅ Good coverage
- 🔍 Check: State history? Attribute filtering?

#### Intelligence Tools (4 tools)

- 🔍 Check: Conversation API integration?
- 🔍 Check: AI assist features?

---

## 📋 Research Tasks

### High Priority

1. **Diagnostics API Research**

   - [ ] Explore `/api/diagnostics/` endpoints
   - [ ] Test config entry diagnostics download
   - [ ] Test device diagnostics download
   - [ ] Document authentication requirements
   - [ ] Check for list/discovery endpoints

2. **Dashboard Permissions Research**
   - [ ] Test existing dashboard tools
   - [ ] Identify permission errors
   - [ ] Document required token scope
   - [ ] Check Lovelace API documentation

### Medium Priority

3. **Gap Analysis - Device Control**

   - [ ] List all HA device types
   - [ ] Compare with current 7 control tools
   - [ ] Identify missing device types
   - [ ] Prioritize by user value

4. **Gap Analysis - Automation**
   - [ ] Review automation API capabilities
   - [ ] Check enable/disable endpoints
   - [ ] Check history/statistics
   - [ ] Document findings

### Low Priority

5. **Tool Enhancement Opportunities**
   - [ ] Review each tool for potential improvements
   - [ ] Check error handling consistency
   - [ ] Verify response format consistency
   - [ ] Document enhancement ideas

---

## 🎨 Design Principles for v4.0.5

### Naming Consistency

- ✅ All tools use `ha_` prefix
- ✅ No confusing suffixes (`_native`, `_diagnostics`, etc.)
- ✅ Verb_noun pattern: `ha_get_diagnostics`, `ha_create_dashboard`
- ✅ Plural for lists: `ha_list_diagnostics`, `ha_list_dashboards`

### Simplicity

- ❌ No overcomplicated features
- ✅ One tool does one thing well
- ✅ Clear, predictable behavior
- ✅ Sensible defaults

### Consistency

- ✅ All tools follow same response format:
  ```json
  {
    "status": "success",
    "message": "Description",
    "data": { ... }
  }
  ```
- ✅ All errors use FastAPI HTTPException
- ✅ All tools use Pydantic models
- ✅ All tools have proper OpenAPI documentation

### User Value

- ✅ Tools solve real problems
- ✅ Tools enable AI to help users
- ✅ Tools are discoverable and understandable
- ✅ Tools work reliably

---

## 🚀 Implementation Phases

### Phase 1: Research (Week 1)

1. Diagnostics API exploration
2. Dashboard permissions investigation
3. Gap analysis completion
4. Document findings

### Phase 2: Design (Week 1)

1. Design new diagnostic tools
2. Design dashboard enhancements
3. Design any gap-filling tools
4. Review for consistency

### Phase 3: Implementation (Week 2)

1. Implement diagnostic tools
2. Fix dashboard permission issues
3. Implement gap-filling tools
4. Update documentation

### Phase 4: Testing & Polish (Week 2)

1. Test all new tools
2. Test existing tools still work
3. Update AI training examples
4. Update CHANGELOG
5. Deploy to production

---

## 📊 Success Metrics

- [ ] 100% tool success rate maintained
- [ ] No new 404/500 errors introduced
- [ ] All diagnostics downloadable via API
- [ ] Dashboard tools work without permission errors
- [ ] Clear documentation for all new tools
- [ ] Cloud AI can use all new tools successfully

---

## 🎯 Target Tool Count

**Current:** 85 tools  
**Estimated v4.0.5:** 90-95 tools

**Breakdown:**

- Diagnostics: +3 tools (config entry, device, list)
- Dashboard enhancements: +2-3 tools (duplicate, export, import)
- Gap filling: +2-4 tools (TBD based on research)
- Polish: 0 new tools (improve existing)

---

## 📝 Notes

- Keep v4.0.4 philosophy: "All come from same server anyway" - no unnecessary distinctions
- Research first, implement second - understand HA APIs before coding
- Test with Cloud AI - if AI can't use it easily, redesign it
- Document everything - future you will thank present you
- Version control - commit often, tag releases

---

## 🔗 Resources

- **HA Integration Diagnostics:** https://developers.home-assistant.io/docs/core/integration_diagnostics/
- **HA Developer Docs:** https://developers.home-assistant.io/
- **HA REST API:** https://developers.home-assistant.io/docs/api/rest/
- **Lovelace Dashboard:** https://www.home-assistant.io/dashboards/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

**Let's build v4.0.5 the right way: research, polish, simplify! 🚀**
