# HA OpenAPI Server v4.0.14

**Release Date:** November 13, 2025  
**Status:** Production Ready ✅  
**Total Endpoints:** 97 (95 POST + 2 GET)  
**Success Rate:** 100%

## What's New in v4.0.14

### Cloud AI Compatibility Updates

This release adds two missing endpoints that Cloud AI agents require for full compatibility:

1. **`/ha_check_config`** - Configuration validation endpoint

   - Alias to existing `/ha_validate_config`
   - Returns configuration validity status
   - Used by Cloud AI before making system changes

2. **`/ha_system_health`** - System health monitoring
   - Returns HA version, entity count, safe_mode status
   - Fallback implementation using Config + States APIs
   - Essential for Cloud AI system monitoring

### Previous Updates (v4.0.11 - v4.0.13)

- **v4.0.11:** Added `/ha_restart` alias for Cloud AI compatibility
- **v4.0.12:** Fixed Pydantic V2 deprecation warnings
- **v4.0.13:** Improved automation validation (min_length for arrays)

## Deployment

### Home Assistant Add-on

```bash
# Upload to HA server
scp server.py root@192.168.1.203:/config/ha-mcp-server/server.py

# Restart add-on
ssh root@192.168.1.203 "ha addons restart local_ha-mcp-server"

# Verify deployment
curl http://192.168.1.203:8001/health | jq
```

### Verification Tests

```powershell
# Health check
Invoke-RestMethod http://192.168.1.203:8001/health | ConvertTo-Json

# Test new endpoints
Invoke-RestMethod http://192.168.1.203:8001/ha_check_config -Method POST
Invoke-RestMethod http://192.168.1.203:8001/ha_system_health -Method POST

# Verify endpoint count
$spec = Invoke-RestMethod http://192.168.1.203:8001/openapi.json
$spec.paths.PSObject.Properties.Name.Count  # Should be 97
```

## Architecture

- **Platform:** FastAPI + Pydantic V2
- **Deployment:** Home Assistant Add-on at 192.168.1.203:8001
- **Transport:** HTTP/REST + WebSocket (for dashboard operations)
- **Authentication:** SUPERVISOR_TOKEN from environment

## Endpoint Breakdown

| Category           | Count | Examples                                                 |
| ------------------ | ----- | -------------------------------------------------------- |
| Core HA API        | 8     | get_states, call_service, get_config                     |
| System Diagnostics | 6     | logs, notifications, **check_config**, **system_health** |
| Integration/Device | 3     | config_entry, device diagnostics                         |
| Advanced API       | 3     | template, intent, validate_config                        |
| Automations        | 8     | create, update, trigger, reload                          |
| File Operations    | 10    | read, write, list, search, tree                          |
| Add-on Management  | 9     | install, start, stop, restart, logs                      |
| Dashboards         | 12    | Lovelace + HACS card management                          |
| Device Control     | 7     | lights, switches, climate, covers                        |
| Logs & History     | 6     | entity history, diagnostics, statistics                  |
| Discovery          | 4     | states, areas, devices, entities                         |
| Intelligence       | 4     | context, activity, comfort, energy                       |
| Code Execution     | 3     | Python sandbox, pandas, matplotlib                       |
| Scenes             | 3     | activate, create, list                                   |
| Security           | 3     | monitoring, anomaly detection                            |
| Camera VLM         | 3     | Vision AI analysis                                       |
| System             | 3     | **restart** (+ alias), call_service                      |
| Camera             | 1     | snapshot                                                 |
| Utility            | 2     | health, API info                                         |

**Total:** 97 endpoints

## Cloud AI Compatibility Status

✅ All Cloud AI requested endpoints now available:

- `/ha_restart` - ✅ Working (requires confirm=true for safety)
- `/ha_check_config` - ✅ Working (validates HA configuration)
- `/ha_system_health` - ✅ Working (returns system health info)
- `/ha_create_automation` - ✅ Working (with proper validation)

## API Documentation

- **Interactive Docs:** <http://192.168.1.203:8001/docs>
- **OpenAPI Spec:** <http://192.168.1.203:8001/openapi.json>
- **Health Check:** <http://192.168.1.203:8001/health>

## Configuration

Environment variables (set in Home Assistant add-on):

```yaml
HA_URL: http://supervisor/core/api
SUPERVISOR_TOKEN: <auto-provided-by-ha>
HA_CONFIG_PATH: /config
PORT: 8001
LOG_LEVEL: info
```

## Known Issues & Notes

1. **Restart endpoint security:** `/ha_restart` requires `confirm=true` to prevent accidental restarts (returns 400 if confirm=false)
2. **System health fallback:** Uses Config + States APIs as fallback when `/api/system_health/info` is unavailable
3. **Dashboard operations:** Use WebSocket API for Lovelace operations (automatically handled)

## Migration from v4.0.13

No breaking changes - direct drop-in replacement.

**Changes:**

- Added 2 new endpoints (+2 total)
- Corrected endpoint count documentation (was incorrectly showing 99, actual was 95, now 97)

## Testing Checklist

- [x] Health check returns v4.0.14
- [x] Endpoint count shows 97
- [x] `/ha_check_config` returns valid=true
- [x] `/ha_system_health` returns entity count
- [x] `/ha_restart` requires confirm=true
- [x] OpenAPI spec contains 97 paths
- [x] All existing endpoints still working
- [x] No Pydantic deprecation warnings

---

## Related: Open-WebUI Auto-Update Fix (November 28, 2025)

While HA OpenAPI Server v4.0.14 continues running smoothly, the Open-WebUI auto-update system was fixed on this date.

### Issues Found & Fixed

The CronJob was running daily but jobs were failing. Root causes:

1. **Wrong `nodeSelector`:** Was `node.kubernetes.io/instance-type: pi5`, should be `kubernetes.io/hostname: masterpi`
2. **Missing RBAC `watch` verb:** Needed for `kubectl rollout status` command
3. **Invalid kubectl image tag:** `bitnami/kubectl:1.28` didn't exist, changed to `latest`
4. **Image pinned to version:** Deployment used `v0.6.36` instead of `:main` tag

### Fixes Applied

```bash
# Updated RBAC Role to include watch verb
verbs: ["get", "list", "watch", "patch", "update"]

# Changed nodeSelector to masterpi (has kubectl access)
nodeSelector:
  kubernetes.io/hostname: masterpi

# Changed kubectl image to latest
image: bitnami/kubectl:latest

# Updated deployment to use :main tag (always latest)
kubectl set image deployment/open-webui -n cluster-services \
  open-webui=ghcr.io/open-webui/open-webui:main
```

### Current Configuration

- **Open-WebUI Version:** 0.6.40 (was 0.6.36)
- **Image Tag:** `ghcr.io/open-webui/open-webui:main` (always latest)
- **ImagePullPolicy:** `Always`
- **Schedule:** `0 14 * * *` (3 AM NZDT / 14:00 UTC daily)
- **Pods:** 2 replicas on worker-pi5-a and worker-pi5-b
- **Data:** Preserved on NFS at `/srv/nfs/openwebui-ha`

### Verification Commands

```bash
# Check CronJob status
ssh pi@192.168.1.11 "sudo k3s kubectl get cronjob -n cluster-services"

# Check pods
ssh pi@192.168.1.11 "sudo k3s kubectl get pods -n cluster-services -l app=open-webui -o wide"

# Check version
curl -s http://192.168.1.11:30080/api/version

# Manual update trigger
ssh pi@192.168.1.11 "sudo k3s kubectl create job openwebui-manual-update-now \
  --from=cronjob/openwebui-auto-update -n cluster-services"
```

### Files Modified

- `c:\MyProjects\pi5-deployments\openwebui-auto-update.yaml` - Fixed nodeSelector, RBAC, image tag

---

## Support

- **GitHub:** <https://github.com/agarib/homeassistant-mcp-server>
- **Author:** agarib & GitHub Copilot
- **License:** MIT
