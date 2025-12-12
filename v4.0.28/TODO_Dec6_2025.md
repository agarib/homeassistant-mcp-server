# TODO - Pi Cluster Post-Power Outage Recovery

**Date:** December 6, 2025  
**Status:** Most critical services restored ✅

---

## ✅ COMPLETED (December 5, 2025)

### Services Restored

- **Homepage Dashboard** - <http://192.168.1.11:3000>
  - Docker container restarted
  - Auto-restart policy set to `always`
  - All services configured and accessible
- **MCPO MCP Servers** - <http://192.168.1.11:30008>

  - Cleaned up StatefulSet (removed broken init container and missing ConfigMap)
  - Both replicas running (mcpo-server-0, mcpo-server-1)
  - All MCP tools connected: filesystem, memory, github, puppeteer, sqlite, fetch, jupyter, time, sequential-thinking
  - Ready for Open-WebUI integration

- **Argon Fan Control**

  - Daemon stopped and disabled (`argononed.service`)
  - Masterpi rebooted to fully stop fan hardware

- **Auto-Restart Configuration**
  - Homepage: Docker restart policy = `always`
  - MCPO: Kubernetes `restartPolicy: Always`
  - Services will auto-start after power outages

### Cluster Status

- **5/6 nodes operational:**
  - ✅ masterpi (192.168.1.11) - Ready
  - ✅ worker-one (192.168.1.12) - Ready
  - ✅ worker-pi5-a (192.168.1.15) - Ready
  - ✅ worker-pi5-b (192.168.1.16) - Ready
  - ⚠️ worker-two (192.168.1.13) - NotReady
  - ⚠️ worker-three (192.168.1.14) - NotReady

---

## 🔴 HIGH PRIORITY - Fix Tomorrow

### 1. Worker Node Recovery (worker-two & worker-three)

**Problem:** Both nodes NotReady due to TLS certificate mismatch after masterpi reboot

**Root Cause:**

```
Error: tls: failed to verify certificate: x509: certificate signed by unknown authority
```

**Solution Steps:**

```bash
# For worker-two (192.168.1.13):
ssh pi@192.168.1.13
sudo systemctl stop k3s-agent
sudo rm -rf /var/lib/rancher/k3s/agent/
sudo systemctl start k3s-agent
sudo systemctl status k3s-agent

# For worker-three (192.168.1.14):
ssh pi@192.168.1.14
sudo systemctl stop k3s-agent
sudo rm -rf /var/lib/rancher/k3s/agent/
sudo systemctl start k3s-agent
sudo systemctl status k3s-agent

# Verify nodes are Ready:
ssh pi@192.168.1.11 "sudo kubectl get nodes"
```

**Impact:** Low - no workloads currently scheduled on these nodes, but should be fixed for full cluster availability

---

## 🟡 MEDIUM PRIORITY - Investigate Performance Issues

### 2. Open-WebUI Slow First Load

**Problem:** Open-WebUI takes time to load on first access (used to load instantly)

**Possible Causes:**

- PVC storage performance after power outage
- Network latency to Pi5 nodes
- Database migration after auto-update
- Resource contention

**Investigation Steps:**

```bash
# Check Open-WebUI pod resources:
ssh pi@192.168.1.11 "sudo kubectl top pods -n cluster-services | grep openwebui"

# Check logs for startup time:
ssh pi@192.168.1.11 "sudo kubectl logs -n cluster-services -l app=open-webui --tail=100"

# Check PVC status:
ssh pi@192.168.1.11 "sudo kubectl get pvc -n cluster-services"

# Test network latency:
ping -c 10 192.168.1.15
ping -c 10 192.168.1.16
```

**Location:** Open-WebUI running on worker-pi5-a and worker-pi5-b  
**Access:** <http://192.168.1.11:30080>

---

### 3. Cloud AI Tool Hanging Issue

**Problem:** Cloud AI stops responding quietly when using OpenAPI server tools

**Context:**

- HA OpenAPI Server v4.0.28 working perfectly (97/97 endpoints, 100% success rate)
- Cloud AI parameter compatibility added (v4.0.28) - both `filepath` and `file_path` work
- May be timeout/rate limit issue on Cloud AI side

**Investigation Steps:**

```bash
# Check HA OpenAPI server logs for hung requests:
ssh pi@192.168.1.203 "docker logs e115a97f_ha-openapi-server --tail=100 | grep -E 'timeout|error|hang'"

# Test specific endpoint that causes hanging:
curl -X POST http://192.168.1.203:8001/read_file \
  -H "Content-Type: application/json" \
  -d '{"filepath": "configuration.yaml"}'

# Check for rate limiting or timeout settings
```

**Endpoint:** <http://192.168.1.203:8001>  
**Current Status:** Server healthy, may be Cloud AI client-side issue

---

## 🟢 LOW PRIORITY - Cleanup & Optimization

### 4. Remove Leftover Configurations

**What was cleaned:**

- Removed `homeassistant-mcp-server` ConfigMap reference (was causing MCPO startup failure)
- Removed init container trying to copy non-existent server.py
- Updated MCPO to use SSE transport to HA OpenAPI server at <http://192.168.1.203:8001/messages>

**Additional Cleanup:**

```bash
# Check for orphaned ConfigMaps:
ssh pi@192.168.1.11 "sudo kubectl get configmap -A | grep -E 'homeassistant|mcp'"

# Check for unused PVCs:
ssh pi@192.168.1.11 "sudo kubectl get pvc -A | grep -E 'Pending|Lost'"

# Clean up old deployment files in home directory:
ssh pi@192.168.1.11 "ls -la ~/*.yaml | grep -E 'old|backup|temp'"
```

---

### 5. Verify All Auto-Restart Policies

**Docker Containers on masterpi:**

```bash
ssh pi@192.168.1.11 "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.State}}' | grep -v 'Exited'"

# Set restart=always for any missing:
docker update --restart=always <container_name>
```

**Kubernetes Deployments:**

```bash
# Check all critical deployments have restartPolicy: Always
ssh pi@192.168.1.11 "sudo kubectl get deploy,statefulset -A -o yaml | grep -A 2 'restartPolicy'"
```

---

## 📝 NOTES

### Current Service URLs

- **Homepage Dashboard:** <http://192.168.1.11:3000>
- **Open-WebUI:** <http://192.168.1.11:30080>
- **MCPO Gateway:** <http://192.168.1.11:30008>
- **MCPO Docs:** <http://192.168.1.11:30008/docs>
- **HA OpenAPI Server:** <http://192.168.1.203:8001>
- **HA OpenAPI Docs:** <http://192.168.1.203:8001/docs>
- **HA OpenAPI Health:** <http://192.168.1.203:8001/health>
- **Grafana:** <http://192.168.1.11:30030>
- **FileBrowser:** <http://192.168.1.11:30081>
- **JupyterLab:** <http://192.168.1.11:30892>
- **PairDrop:** <http://192.168.1.11:30300>
- **Syncthing:** <http://192.168.1.11:30384>

### MCP Server Routes (via MCPO)

All accessed through <http://192.168.1.11:30008/[server_name>]:

- `/filesystem` - File operations
- `/memory` - Memory/knowledge graph
- `/github` - GitHub integration
- `/puppeteer` - Browser automation
- `/sqlite` - Database operations
- `/fetch` - Web fetching
- `/jupyter` - Notebook execution
- `/time` - Time operations
- `/sequential-thinking` - Reasoning tools
- `/homeassistant` - HA control (⚠️ needs SSE endpoint at HA server)

### Key File Locations

- **MCPO StatefulSet:** `c:\MyProjects\mcpo-statefulset-cleaned.yaml`
- **Homepage Deployment:** `c:\MyProjects\homepage-dashboard-deployment.yaml`
- **HA OpenAPI Server:** `c:\MyProjects\ha-openapi-server-v3.0.0\v4.0.28\server.py`
- **HA Server Running:** `\\192.168.1.203\config\ha-openapi-server\server.py`

### Cluster Architecture

- **Master:** masterpi (192.168.1.11, 8GB) - control plane, Homepage, utility services
- **Worker-one:** (192.168.1.12, 4GB) - MCPO replicas (tainted for utility workloads)
- **Worker-two/three:** (192.168.1.13/.14, 8GB) - ⚠️ NotReady, needs fixing
- **Worker-pi5-a/b:** (192.168.1.15/.16, 16GB) - Open-WebUI replicas, primary workloads

---

## 🎯 Tomorrow's Action Plan

1. **Morning:** Fix worker-two and worker-three TLS certificate issues (15 minutes)
2. **Mid-day:** Investigate Open-WebUI slow load performance (30 minutes)
3. **Afternoon:** Test and debug Cloud AI hanging issue (45 minutes)
4. **Optional:** Run cleanup tasks and verify auto-restart policies

---

## 💡 Power Outage Prevention

**What's Now Protected:**

- Homepage auto-restarts via Docker `restart=always`
- MCPO auto-restarts via Kubernetes `restartPolicy: Always`
- All Kubernetes deployments have restart policies

**What Still Needs Work:**

- Worker node automatic rejoin after master certificate rotation
- Consider UPS for masterpi to prevent sudden k3s shutdowns
- Document proper shutdown sequence for maintenance

---

**Last Updated:** December 5, 2025 04:20 NZDT  
**Next Review:** December 6, 2025

---

Good night! Great work today getting everything back online! 🚀
