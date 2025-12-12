# v4.0.5 Development Folder

**Status:** Research & Planning Phase  
**Target Release:** TBD  
**Goal:** Polish tools, add diagnostics, enhance dashboards

## 📁 Folder Structure

```
v4.0.5/
├── README.md                      # This file
├── PLANNING.md                    # Master planning document
├── RESEARCH_DIAGNOSTICS.md        # Diagnostics API research guide
├── research_script.ps1            # Automated research script
├── research_data/                 # API response data (gitignored)
│   ├── config_entries.json
│   ├── device_registry.json
│   ├── lg_config_diagnostics.json
│   ├── lg_device_diagnostics.json
│   └── ... (other API responses)
└── implementation/                # Future implementation files
    └── (TBD after research)
```

## 🚀 Quick Start

### 1. Set Up Environment

```powershell
# Set your Home Assistant long-lived access token
$env:HA_TOKEN = "eyJhbGc..."  # Get from Settings → People → Long-Lived Access Tokens
```

### 2. Run Research Script

```powershell
# Run automated research
.\v4.0.5\research_script.ps1

# This will:
# - Explore diagnostics API endpoints
# - Get config entries and device registry
# - Test diagnostics download for LG ThinQ
# - Explore dashboard/Lovelace API
# - Check automation capabilities
# - Save all data to research_data/
```

### 3. Review Findings

```powershell
# View collected data
Get-ChildItem v4.0.5\research_data\ | Format-Table Name, Length, LastWriteTime

# Read specific files
Get-Content v4.0.5\research_data\config_entries.json | ConvertFrom-Json | Format-List
```

### 4. Update Documentation

After research, update:

- `RESEARCH_DIAGNOSTICS.md` - Document findings
- `PLANNING.md` - Adjust implementation plan based on discoveries

## 📋 Research Checklist

### Diagnostics API

- [ ] Test `/api/diagnostics/config_entry/{entry_id}`
- [ ] Test `/api/diagnostics/device/{device_id}`
- [ ] Document redaction patterns
- [ ] Identify authentication requirements (SUPERVISOR_TOKEN vs admin)
- [ ] Map response structure
- [ ] Test with integrations that don't support diagnostics

### Dashboard API

- [ ] Test existing 8 dashboard tools
- [ ] Identify permission errors
- [ ] Document Lovelace API endpoints
- [ ] Check dashboard creation/update/delete permissions \* (Very Important)
- [ ] Explore card management

### Device Control Gaps

- [ ] List all HA device classes
- [ ] Compare with current 7 control tools
- [ ] Identify missing types:
  - [ ] Lock control
  - [ ] Alarm control
  - [ ] Humidifier/dehumidifier
  - [ ] Water heater
  - [ ] Siren
  - [ ] Number entities
  - [ ] Others?

### Automation Enhancements **Very Important-To add**

- [ ] Check enable/disable endpoints
- [ ] Check automation history
- [ ] Check last triggered info
- [ ] Check automation reload/validation **Very Important-To add**

## 🎯 Implementation Goals

### New Tools (Estimated 5-10)

**Diagnostics (3 tools):** **Very Important-To add**

1. `ha_get_config_entry_diagnostics` - Download config entry diagnostics
2. `ha_get_device_diagnostics` - Download device diagnostics
3. `ha_list_available_diagnostics` - List all diagnostics (if endpoint exists)

**Dashboard Enhancements (2-3 tools):**

1. `ha_duplicate_dashboard` - Clone existing dashboard
2. `ha_export_dashboard` - Export dashboard YAML
3. `ha_import_dashboard` - Import dashboard from YAML (if feasible)
4. `ha_edit_button_card` - Edit button card configuration
5. `ha_edit_mushroom_card` - Edit mushroom card configuration

**Device Control (2-4 tools):**

1. `ha_control_lock` - Lock/unlock control
2. `ha_control_alarm` - Alarm panel control
3. Others based on gap analysis

### Tool Polish

- Review all 85 existing tools
- Fix any permission issues (especially dashboards-immediate)
- Improve error messages _VERY IMPORTANT-To guide Cloud AI if makes mistakes especially with wrong tool usage_
- Add missing parameters
- Ensure consistent naming _VERY IMPORTANT_

## 📊 Success Criteria

- [ ] 100% tool success rate maintained
- [ ] All diagnostics downloadable via API
- [ ] Dashboard tools work without permission errors
- [ ] Cloud AI can use all new tools
- [ ] Clear, comprehensive documentation
- [ ] No 404/500 errors introduced

## 🔧 Development Workflow

1. **Research Phase** (Current)

   - Run research_script.ps1
   - Explore APIs manually
   - Document all findings

2. **Design Phase**

   - Create Pydantic models
   - Design endpoint signatures
   - Plan error handling

3. **Implementation Phase**

   - Add new tools to server.py
   - Update documentation
   - Create test cases

4. **Testing Phase**

   - Test with Cloud AI
   - Verify permission requirements
   - Check error handling

5. **Deployment Phase**
   - Update CHANGELOG
   - Tag release
   - Deploy to production

## 📝 Notes

- Keep v4.0.4 philosophy: simple, consistent, no overcomplicated features
- Research first, implement second
- All tools must be AI-friendly
- Maintain backward compatibility
- No breaking changes unless absolutely necessary

## 🔗 Related Documents

- **[PLANNING.md](PLANNING.md)** - Master plan for v4.0.5
- **[RESEARCH_DIAGNOSTICS.md](RESEARCH_DIAGNOSTICS.md)** - Diagnostics research guide
- **[../README.md](../README.md)** - Main project README
- **[../CHANGELOG.md](../CHANGELOG.md)** - Version history

---

**Philosophy:** Research → Polish → Fill gaps → Keep it simple! 🚀
