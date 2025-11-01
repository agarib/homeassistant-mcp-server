# Home Assistant OpenAPI Server v4.0.0 - Deployment Summary

**Date:** November 1, 2025  
**Version:** 4.0.0  
**Status:** Ready for Deployment ✅

---

## 📊 What Changed

### Version Bump

- **Previous:** v3.0.0 (77 endpoints)
- **Current:** v4.0.0 (85 endpoints)
- **Added:** 12 new tools (8 native MCPO + 4 system diagnostics)

### New Capabilities

**8 Native MCPO Tools:**

1. `get_entity_state_native` - Entity state query
2. `list_entities_native` - Entity listing with domain filter
3. `get_services_native` - Available services
4. `fire_event_native` - Custom event firing
5. `render_template_native` - Jinja2 template rendering
6. `get_config_native` - HA configuration
7. `get_history_native` - Entity history
8. `get_logbook_native` - Logbook entries

**4 System Diagnostics Tools:**

1. `get_system_logs_diagnostics` - HA core logs with filtering
2. `get_persistent_notifications` - Integration errors/notifications
3. `get_integration_status` - Integration health check
4. `get_startup_errors` - Startup error diagnostics

### Code Changes

**Files Modified:**

- `server.py` - Updated header, version, added 12 new endpoints
- `CHANGELOG.md` - Added v4.0.0 entry

**HomeAssistantAPI Enhancements:**

- Added `fire_event()` method
- Added `render_template()` method

---

## 🚀 Deployment Steps

**📍 IMPORTANT:** This server runs as a **Home Assistant Add-on**, not in the K3s cluster!

- **Server Location:** Home Assistant (192.168.1.203:8001)
- **MCPO Location:** K3s Cluster (connects to add-on via SSE)
- **Connection:** MCPO → `http://192.168.1.203:8001/messages` (SSE transport)

### Step 1: Local Validation ✅

```powershell
cd C:\MyProjects\ha-openapi-server-v3.0.0
python -c "import server; print('Server imports successfully')"
```

**Result:** ✅ No syntax errors

**Endpoint Count:** 85 total (83 POST + 2 GET)

### Step 2: Update Home Assistant Add-on

**Option A: Update via GitHub (Recommended)**

```powershell
# Push changes to GitHub
git add server.py CHANGELOG.md
git commit -m "Release v4.0.0: Add 12 tools (8 native MCPO + 4 diagnostics)"
git tag v4.0.0
git push origin main
git push origin v4.0.0
```

Then in Home Assistant:

- Settings → Add-ons → Home Assistant MCP Server
- Click "Check for updates"
- Click "Update"
- Click "Restart"

**Option B: Manual Update (Development)**

1. Copy `server.py` to add-on directory in HA
2. Restart add-on via HA UI

### Step 3: Verify Add-on is Running

```bash
# Check health endpoint
curl http://192.168.1.203:8001/health

# Expected response:
{
  "status": "healthy",
  "version": "4.0.0",
  "home_assistant_connected": true
}
```

**Check Add-on Logs:**

- Settings → Add-ons → Home Assistant MCP Server → Logs
- Look for: `🏠 Home Assistant OpenAPI Server v4.0.0`

### Step 4: Verify MCPO Connection

```powershell
# Check MCPO config points to add-on
ssh pi@192.168.1.11 "sudo kubectl get configmap mcpo-config -n cluster-services -o yaml | grep -A3 homeassistant"

# Expected:
# "homeassistant": {
#   "transport": "sse",
#   "url": "http://192.168.1.203:8001/messages"
# }
```

**If MCPO pods need restart:**

```powershell
# Find deployment name
ssh pi@192.168.1.11 "sudo kubectl get deployments -n cluster-services"

# Restart (no code changes needed in cluster)
ssh pi@192.168.1.11 "sudo kubectl rollout restart deployment <mcpo-deployment-name> -n cluster-services"
```

### Step 5: Test New Endpoints

```bash
# Test system diagnostics (via add-on endpoint)
curl -X POST http://192.168.1.203:8001/get_persistent_notifications

# Test integration status
curl -X POST http://192.168.1.11:30080/homeassistant/get_integration_status `
  -H "Content-Type: application/json" `
  -d '{"integration":"lg"}'

# Test system logs
curl -X POST http://192.168.1.11:30080/homeassistant/get_system_logs_diagnostics `
  -H "Content-Type: application/json" `
  -d '{"lines":50,"level":"ERROR"}'
```

---

## 📋 Deployment Checklist

- [x] Update server.py version to 4.0.0
- [x] Add 12 new endpoint functions
- [x] Add 2 new HomeAssistantAPI methods
- [x] Update CHANGELOG.md
- [x] Validate Python syntax locally
- [x] Count endpoints (85 total confirmed)
- [ ] Push changes to GitHub repository
- [ ] Update HA add-on (via GitHub or manual copy)
- [ ] Restart add-on in Home Assistant
- [ ] Verify add-on health endpoint
- [ ] Test new diagnostics endpoints
- [ ] Test native MCPO endpoints
- [ ] Verify MCPO connection (if needed, restart MCPO pods)

---

## 🔍 Post-Deployment Verification

### Check Add-on Status

**Via Home Assistant UI:**

- Settings → Add-ons → Home Assistant MCP Server
- Status should show "Running"
- Logs should show v4.0.0 startup

**Via Health Endpoint:**

```bash
curl http://192.168.1.203:8001/health
```

**Look for:**

- ✅ `{"status": "healthy", "version": "4.0.0"}`
- ✅ `"home_assistant_connected": true`
- ✅ Response time < 1 second

### Check MCPO Connection

```bash
ssh pi@192.168.1.11 "sudo kubectl logs -n cluster-services <mcpo-pod-name> --tail=50 | grep homeassistant"
```

**Look for:**

- ✅ `Successfully connected to 'homeassistant'`
- ✅ `homeassistant server ready with 85 tools`
- ✅ No connection errors or timeouts

### Test Endpoint Discovery

Visit Open-WebUI and check:

- ✅ 85 endpoints visible in tool list
- ✅ Tags include `native_mcpo` and `system_diagnostics`
- ✅ All endpoints have proper descriptions

### Test Functionality

Test key new endpoints:

- ✅ `get_persistent_notifications` - Returns notification list
- ✅ `get_integration_status` - Returns integration health
- ✅ `get_system_logs_diagnostics` - Returns filtered logs
- ✅ `fire_event_native` - Successfully fires events
- ✅ `render_template_native` - Renders Jinja2 templates

---

## 🎯 Success Criteria

**Deployment Successful When:**

1. ✅ Home Assistant add-on shows "Running" status
2. ✅ Health endpoint returns version 4.0.0
3. ✅ MCPO successfully connects to add-on via SSE
4. ✅ 85 endpoints accessible via Open-WebUI
5. ✅ New diagnostics tools return data
6. ✅ No regression in existing 73 endpoints

**Known Good State:**

- Add-on: Running at 192.168.1.203:8001
- Version: 4.0.0
- Endpoints: 85 (83 POST + 2 GET)
- Tags: `native_mcpo`, `system_diagnostics`, + existing
- Health: `http://192.168.1.203:8001/health` returns v4.0.0
- MCPO: Connected via `http://192.168.1.203:8001/messages` (SSE)

---

## 🐛 Troubleshooting

**See comprehensive guide:** [ADDON_DEPLOYMENT_GUIDE.md](./ADDON_DEPLOYMENT_GUIDE.md)

### Common Issues

**Issue 1: Add-on Won't Start**

- Check port 8001 not in use
- Review add-on logs in HA UI
- Verify dependencies installed correctly

**Issue 2: MCPO Can't Connect**

- Verify add-on health endpoint responds
- Check MCPO config has correct URL: `http://192.168.1.203:8001/messages`
- Ensure network connectivity between cluster and HA

**Issue 3: File Operations Fail**

- Verify add-on has `/config` mount (check add-on config.json)
- Check file permissions in `/config`
- Review add-on logs for path errors

**For detailed troubleshooting, see:** [ADDON_DEPLOYMENT_GUIDE.md](./ADDON_DEPLOYMENT_GUIDE.md)

---

## 📁 Deployment Architecture

```
Windows PC (Development)
  └─> GitHub Repository
       └─> Home Assistant Add-on (192.168.1.203:8001)
            └─> MCPO in K3s Cluster (SSE connection)
                 └─> Open-WebUI (http://192.168.1.11:30080)
```

**Update Flow:**

1. Edit code on Windows PC
2. Push to GitHub
3. Update add-on in HA (pulls from GitHub)
4. MCPO auto-reconnects to updated server
5. Tools available in Open-WebUI

---

## 🐛 Troubleshooting (Deprecated - K3s Deployment)

**⚠️ NOTE:** The sections below are for reference only. This server now runs as a HA add-on, not in K3s.

<details>
<summary>Click to expand K3s troubleshooting (deprecated)</summary>

### Pod Won't Start (Not Applicable)

```powershell
# Check pod events
kubectl describe pod -n cluster-services -l app=mcpo-server

# Check ConfigMap
kubectl get configmap homeassistant-openapi-server -n cluster-services -o yaml
```

</details>

---

## 📖 Documentation

**Updated Files:**

- `server.py` - Main server with v4.0.0 (add-on deployment)
- `CHANGELOG.md` - Version history
- `ADDON_DEPLOYMENT_GUIDE.md` - **NEW** Comprehensive add-on deployment guide
- `V4_DEPLOYMENT_SUMMARY.md` - This file (deployment summary)
- `CONSOLIDATION_GUIDE.md` - Integration guide
- `NEW_TOOLS_REFERENCE.md` - Tool reference

**Next Steps:**

- Push v4.0.0 to GitHub repository
- Update HA add-on (via GitHub or manual)
- Test new diagnostics tools
- Test washing machine diagnostics workflow
- Verify MCPO connection

---

## 🎉 Benefits

**What Users Get:**

- ✅ System visibility into HA errors and notifications
- ✅ Integration health monitoring (diagnose LG ThinQ, etc.)
- ✅ Startup error diagnostics
- ✅ Enhanced event and template tools
- ✅ Unified architecture (single FastAPI server)
- ✅ Consistent Pydantic validation across all 85 endpoints
- ✅ Easier deployment (HA add-on, not cluster management)
- ✅ Direct `/config` access for file operations

**Use Case: Washing Machine Fix**

1. Check `get_persistent_notifications` for LG ThinQ errors
2. Use `get_integration_status` to verify integration state
3. Read `get_system_logs_diagnostics` for auth errors
4. Review `get_startup_errors` for initialization issues
5. Fix integration based on diagnostic findings

---

**Ready to Deploy! 🚀**

**Deployment Model:** Home Assistant Add-on (192.168.1.203:8001) ↔ MCPO (K3s) ↔ Open-WebUI
