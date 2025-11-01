# v4.0.0 Deployment Quick Reference

**Date:** November 1, 2025  
**Version:** 4.0.0 → 85 endpoints (8 native MCPO + 4 diagnostics + 73 existing)

---

## 🎯 Critical Info

**Where Server Runs:** Home Assistant Add-on (NOT K3s cluster!)

- **HA Address:** 192.168.1.203:8001
- **Health Check:** `curl http://192.168.1.203:8001/health`
- **SSE Endpoint:** `http://192.168.1.203:8001/messages` (for MCPO)
- **API Docs:** `http://192.168.1.203:8001/docs`

**MCPO Connection:** K3s cluster connects TO the add-on via SSE

- **MCPO Config:** `homeassistant.url = "http://192.168.1.203:8001/messages"`
- **Transport:** SSE (Server-Sent Events)
- **Config Location:** `kubectl get configmap mcpo-config -n cluster-services`

---

## ✅ Files Updated

- ✅ `server.py` - v4.0.0, 85 endpoints, add-on deployment notes
- ✅ `CHANGELOG.md` - v4.0.0 entry with tool distribution
- ✅ `ADDON_DEPLOYMENT_GUIDE.md` - Comprehensive add-on guide
- ✅ `V4_DEPLOYMENT_SUMMARY.md` - Deployment summary

---

## 🚀 Deployment Commands

### Option 1: Update via GitHub (Recommended)

```powershell
cd C:\MyProjects\ha-openapi-server-v3.0.0

git status
git add server.py CHANGELOG.md ADDON_DEPLOYMENT_GUIDE.md V4_DEPLOYMENT_SUMMARY.md
git commit -m "Release v4.0.0: Add-on deployment + 12 new tools"
git tag v4.0.0
git push origin main
git push origin v4.0.0
```

Then in Home Assistant:

1. Settings → Add-ons → Home Assistant MCP Server
2. Click "Check for updates"
3. Click "Update"
4. Click "Restart"

### Option 2: Manual Copy (Development)

Copy `server.py` to add-on directory and restart add-on via HA UI.

---

## 🔍 Verification

```bash
# 1. Check add-on health
curl http://192.168.1.203:8001/health
# Expect: {"status":"healthy","version":"4.0.0"}

# 2. Check add-on logs in HA UI
# Look for: "🏠 Home Assistant OpenAPI Server v4.0.0"

# 3. Verify MCPO config
ssh pi@192.168.1.11 "sudo kubectl get configmap mcpo-config -n cluster-services -o yaml | grep -A3 homeassistant"
# Expect: "url": "http://192.168.1.203:8001/messages"

# 4. Test endpoint
curl -X POST http://192.168.1.203:8001/get_persistent_notifications
```

---

## 🆕 New Tools (12 total)

**8 Native MCPO:**

- `get_entity_state_native`, `list_entities_native`
- `get_services_native`, `fire_event_native`
- `render_template_native`, `get_config_native`
- `get_history_native`, `get_logbook_native`

**4 System Diagnostics:**

- `get_system_logs_diagnostics` - Read HA logs
- `get_persistent_notifications` - See integration errors
- `get_integration_status` - Check integration health (e.g., LG ThinQ)
- `get_startup_errors` - Diagnose startup issues

---

## ⚠️ Common Mistakes

❌ **WRONG:** Deploy to K3s cluster (server is HA add-on!)  
✅ **RIGHT:** Update HA add-on, MCPO connects to it

❌ **WRONG:** MCPO config: `"command": "python3"`  
✅ **RIGHT:** MCPO config: `"transport": "sse", "url": "http://192.168.1.203:8001/messages"`

❌ **WRONG:** Health check at cluster IP  
✅ **RIGHT:** Health check at `http://192.168.1.203:8001/health`

---

## 🐛 Troubleshooting

**Add-on won't start:**

- Check port 8001 not in use
- Review add-on logs: Settings → Add-ons → HA MCP Server → Logs

**MCPO can't connect:**

- Verify health endpoint: `curl http://192.168.1.203:8001/health`
- Check MCPO config has correct SSE URL
- Ensure network between cluster (192.168.1.11-14) and HA (192.168.1.203)

**File operations fail:**

- Verify add-on config.json has `"map": ["config:rw"]`
- Check add-on logs show: `Config path exists: True`

**Full troubleshooting:** See `ADDON_DEPLOYMENT_GUIDE.md`

---

## 📊 Architecture Diagram

```
┌──────────────────┐
│  Windows PC      │
│  (Development)   │
└────────┬─────────┘
         │ git push
         ▼
┌──────────────────┐
│  GitHub Repo     │
└────────┬─────────┘
         │ pull update
         ▼
┌──────────────────────────────┐
│  Home Assistant Add-on       │  ◄─── Server runs HERE!
│  192.168.1.203:8001          │
│  - Health: /health           │
│  - SSE: /messages            │
│  - API: /docs                │
└────────┬─────────────────────┘
         │ SSE connection
         ▼
┌──────────────────────────────┐
│  MCPO (K3s Cluster)          │
│  cluster-services namespace  │
│  192.168.1.11-14             │
└────────┬─────────────────────┘
         │ tool calls
         ▼
┌──────────────────────────────┐
│  Open-WebUI                  │
│  http://192.168.1.11:30080   │
└──────────────────────────────┘
```

---

## 📁 Key Files

| File                        | Purpose                            |
| --------------------------- | ---------------------------------- |
| `server.py`                 | Main FastAPI server (85 endpoints) |
| `CHANGELOG.md`              | Version history                    |
| `ADDON_DEPLOYMENT_GUIDE.md` | **Comprehensive add-on guide**     |
| `V4_DEPLOYMENT_SUMMARY.md`  | Deployment checklist               |
| `NEW_TOOLS_REFERENCE.md`    | Tool documentation                 |
| `CONSOLIDATION_GUIDE.md`    | Migration guide                    |

---

**Next Steps:**

1. Push to GitHub
2. Update HA add-on
3. Test new diagnostics tools
4. Verify MCPO connection

**Ready to deploy! 🚀**
