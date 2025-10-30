# Quick Start Guide - HA MCP Infrastructure

## Current Status 🎉

**Working Now (No Setup Required):**

- ✅ 68/77 HA endpoints (88%) - All core features
- ✅ 10 MCP servers (83 tools) - Full stack operational
- ✅ 151 total tools ready for AI

**Optional (Need Admin Token):**

- ⭐ +9 HA endpoints (add-on management) → 77/77 (100%)
- ⭐ Total: 160 tools

---

## Access URLs

### MCPO Server (Pi4 Cluster)

```
Main Gateway: http://192.168.1.11:30008
Servers: /filesystem, /memory, /github, /puppeteer, /sqlite, /fetch, /jupyter, /time, /sequential-thinking, /homeassistant
```

### HA OpenAPI v2.0

```
API: http://192.168.1.203:8001
Docs: http://192.168.1.203:8001/docs
Health: http://192.168.1.203:8001/health
OpenAPI: http://192.168.1.203:8001/openapi.json
```

---

## Test Everything Works

### Quick Health Check

```powershell
# MCPO servers
Invoke-RestMethod http://192.168.1.11:30008/filesystem/openapi.json
Invoke-RestMethod http://192.168.1.11:30008/memory/openapi.json

# HA v2.0
Invoke-RestMethod http://192.168.1.203:8001/health

# Get all device states
Invoke-RestMethod -Uri "http://192.168.1.203:8001/get_states" `
    -Method POST -Body '{}' -ContentType "application/json"
```

### Control a Device

```powershell
# Turn on living room couch light
Invoke-RestMethod -Uri "http://192.168.1.203:8001/control_light" `
    -Method POST -ContentType "application/json" `
    -Body '{"entity_id":"light.couch_light","action":"turn_on","brightness":255}'
```

---

## Enable Add-on Management (Optional)

Only needed if you want to install/manage add-ons via API.

### 1. Generate Token

- HA UI → Profile → Security → Long-Lived Access Tokens
- Create token named `HA MCP Admin`
- Copy token (starts with `eyJ...`)

### 2. Add to Addon Config

Edit via HA UI or file: `/addons/local/ha-mcp-server/options.json`

```json
{
  "port": 8001,
  "log_level": "info",
  "admin_token": "YOUR_TOKEN_HERE"
}
```

### 3. Restart

```bash
ha addons restart local_ha-mcp-server
```

### 4. Test

```powershell
Invoke-RestMethod -Uri "http://192.168.1.203:8001/list_addons" `
    -Method POST -Body '{}' -ContentType "application/json"
```

---

## What Works Right Now (68 Endpoints)

### Device Control

```powershell
# Lights, switches, climate, covers
POST /control_light
POST /control_switch
POST /control_climate
POST /control_cover
```

### Smart Home

```powershell
# Automations (full lifecycle)
POST /list_automations
POST /create_automation
POST /trigger_automation

# Scenes
POST /activate_scene
POST /list_scenes

# Discovery
POST /get_states
POST /list_areas
POST /get_area_devices
```

### Files & Config

```powershell
# Full file system access
POST /read_file
POST /write_file
POST /list_files
POST /search_files
```

### Intelligence

```powershell
# Context-aware features
POST /get_context_awareness
POST /get_activity_summary
POST /get_comfort_score
POST /get_energy_insights
```

### Advanced

```powershell
# Code execution
POST /execute_python  # Sandboxed Python
POST /validate_yaml
POST /render_template

# History & analytics
POST /get_entity_history
POST /get_statistics

# Dashboards
POST /list_dashboards
POST /create_dashboard
POST /add_card
```

---

## Integration with Open-WebUI

### Add MCP Servers (10 URLs)

```
http://192.168.1.11:30008/filesystem       (14 tools)
http://192.168.1.11:30008/memory           (9 tools)
http://192.168.1.11:30008/github           (26 tools)
http://192.168.1.11:30008/puppeteer        (7 tools)
http://192.168.1.11:30008/sqlite           (5 tools)
http://192.168.1.11:30008/fetch            (1 tool)
http://192.168.1.11:30008/jupyter          (6 tools)
http://192.168.1.11:30008/time             (2 tools)
http://192.168.1.11:30008/sequential-thinking (1 tool)
http://192.168.1.203:8001                  (77 tools)
```

**Total:** 160 tools for AI control

---

## Common Tasks

### Restart HA Server

```powershell
POST http://192.168.1.203:8001/restart_ha
```

### Get Living Room Devices

```powershell
Invoke-RestMethod -Uri "http://192.168.1.203:8001/get_area_devices" `
    -Method POST -Body '{"area_name":"living room"}' -ContentType "application/json"
```

### Execute Python in Sandbox

```powershell
$code = @"
import datetime
print(f"Current time: {datetime.datetime.now()}")
print("Hello from HA!")
"@

Invoke-RestMethod -Uri "http://192.168.1.203:8001/execute_python" `
    -Method POST -Body "{`"code`":`"$code`"}" -ContentType "application/json"
```

### Create Automation

```powershell
$automation = @{
    automation_id = "motion_lights"
    config = @{
        alias = "Motion → Lights"
        trigger = @(
            @{
                platform = "state"
                entity_id = "binary_sensor.motion"
                to = "on"
            }
        )
        action = @(
            @{
                service = "light.turn_on"
                target = @{
                    entity_id = "light.living_room"
                }
            }
        )
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://192.168.1.203:8001/create_automation" `
    -Method POST -Body $automation -ContentType "application/json"
```

---

## Troubleshooting

### Check Addon Status

```bash
# Via SSH
ssh root@192.168.1.203
ha addons info local_ha-mcp-server
ha addons logs local_ha-mcp-server
```

### Restart Addon

```bash
ha addons restart local_ha-mcp-server
```

### Check Health

```powershell
Invoke-RestMethod http://192.168.1.203:8001/health
```

### View API Docs

```
Browser: http://192.168.1.203:8001/docs
```

---

## Files Reference

| File                         | Purpose                     |
| ---------------------------- | --------------------------- |
| `Test-MCP-Servers.ps1`       | Automated validation script |
| `MCP_VALIDATION_COMPLETE.md` | Full validation report      |
| `ADDON_MANAGEMENT_FIX.md`    | Admin token setup guide     |
| `AI_TRAINING_EXAMPLES.md`    | 56+ training scenarios      |
| `MCP_QUICK_REFERENCE.md`     | This document               |

---

## What's Next?

### Immediate

1. ✅ Test core features (already working)
2. ⭐ Add admin token (optional, for add-on management)
3. 🔧 Fix USB write access (for ai-workspace)

### Integration

1. Add all MCP servers to Open-WebUI
2. Test AI chat control
3. Fine-tune LLMs for tool-calling

### Advanced

1. Create AI automation workflows
2. Build custom integrations
3. Deploy on Pi5 cluster (dual-node setup)

---

## Success ✅

You now have **151-160 working tools** across:

- 🏠 Home automation (lights, climate, media)
- 📁 File management (config access)
- 🤖 Automations (create, trigger, manage)
- 🧠 Intelligence (context, activity, energy)
- 🎨 Dashboards (Lovelace control)
- ⚙️ System (restart, services, templates)
- 📊 Analytics (history, statistics, diagnostics)
- 🔒 Security (monitoring, anomaly detection)
- 📸 Vision AI (camera analysis, change detection)

**Everything works!** Add-on management is the only optional feature requiring extra setup.
