# 🚀 Quick Start - Home Assistant OpenAPI Server v2.0

## 📍 You Are Here

✅ **Phase 1 Complete**: Core v2.0 server implementation done  
📁 **Location**: `C:\MyProjects\ha-openapi-server-v2\`  
🎯 **Next**: Deploy and test with Open-WebUI

## ⚡ Deploy in 3 Steps

### Step 1: Deploy to Home Assistant

```powershell
cd C:\MyProjects\ha-openapi-server-v2
.\deploy.ps1 -HaHost 192.168.1.203
```

**What it does**:

- ✅ Backs up your old server to `server.py.backup.TIMESTAMP`
- ✅ Uploads new `server.py` and `requirements.txt`
- ✅ Restarts the addon container
- ✅ Waits 15 seconds for startup
- ✅ Runs health check
- ✅ Tests basic endpoint
- ✅ Auto-rolls back if health check fails

**Expected output**:

```
✅ DEPLOYMENT SUCCESSFUL!

Server URLs:
  Health:   http://192.168.1.203:8001/health
  API Docs: http://192.168.1.203:8001/docs
  OpenAPI:  http://192.168.1.203:8001/openapi.json

Open-WebUI Integration:
  Add this URL as OpenAPI server:
  http://ha-mcp-server.cluster-services:8001
```

### Step 2: Test Your Original Request

```powershell
# "check living room area to test how ha mcp behaves"
$body = @{ area_name = "living room" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://192.168.1.203:8001/get_area_devices" `
    -Method Post -Body $body -ContentType "application/json"
```

**Expected result (v2.0)**:

```json
{
  "area": "living room",
  "devices": [
    {
      "entity_id": "light.couch_light",
      "friendly_name": "Couch Light",
      "state": "on",
      "domain": "light"
    },
    {
      "entity_id": "light.tv_light",
      "friendly_name": "TV Light",
      "state": "off",
      "domain": "light"
    },
    ...
  ],
  "count": 5
}
```

**Old result (v1.x)**:

```json
{"error": ""}  ❌
```

### Step 3: Add to Open-WebUI

1. Open Open-WebUI: `http://192.168.1.11:30080` (or your Open-WebUI URL)
2. Go to: **Settings** → **Tools** → **OpenAPI Servers**
3. Click: **Add Server**
4. Enter URL: `http://ha-mcp-server.cluster-services:8001`
   - (Or direct IP: `http://192.168.1.203:8001`)
5. Click: **Connect**

**Verify connection**:

- ✅ Should show "Connection successful"
- ✅ Should discover ~30 tools (Phase 1 endpoints)
- ✅ Should show tool list in UI

## 🧪 Test Execution (The Critical Part!)

In Open-WebUI chat, try these:

### Test 1: Your Original Request

```
User: "Check what devices are in my living room"

Expected AI behavior:
✅ Discovers get_area_devices tool
✅ EXECUTES POST /get_area_devices with {"area_name": "living room"}
✅ Returns actual device list from your HA
✅ Shows you real devices, not code examples!
```

### Test 2: Device Control

```
User: "Turn on the couch light at 50% brightness"

Expected AI behavior:
✅ Discovers control_light tool
✅ EXECUTES POST /control_light with appropriate params
✅ Light actually turns on in your home!
✅ Confirms with success message
```

### Test 3: State Query

```
User: "Show me all my light switches"

Expected AI behavior:
✅ Discovers discover_devices or get_states tool
✅ EXECUTES with {"domain": "light"}
✅ Returns list of all light entities
✅ Shows current states (on/off)
```

## 🎯 Success Criteria

You'll know v2.0 is working when:

1. **Deployment**: `deploy.ps1` completes with "✅ DEPLOYMENT SUCCESSFUL!"
2. **Health Check**: `http://192.168.1.203:8001/health` returns `{"status": "healthy", "version": "2.0.0"}`
3. **Direct Test**: PowerShell test above returns real device data
4. **Open-WebUI Connection**: Shows "Connection successful"
5. **Tool Discovery**: Lists ~30 tools (will be 105 when Phase 2 complete)
6. **Tool Execution**: AI **actually executes** tools, doesn't just show code

## 🔍 Troubleshooting

### Problem: deploy.ps1 fails with "Upload failed"

**Solution**:

```powershell
# Check SSH access
ssh root@192.168.1.203 "echo 'Connection OK'"

# Check SCP works
scp C:\MyProjects\ha-openapi-server-v2\server.py root@192.168.1.203:/tmp/test.py
```

### Problem: Health check fails after deployment

**Solution**:

```powershell
# Check container logs
ssh root@192.168.1.203 "docker logs addon_local_ha-mcp-server --tail=50"

# Check if server is running
ssh root@192.168.1.203 "docker ps | grep ha-mcp-server"

# Manual restart
ssh root@192.168.1.203 "docker restart addon_local_ha-mcp-server"
```

### Problem: get_area_devices returns empty list

**Solution**:

- Check area name spelling (lowercase, spaces)
- Try different areas: "bedroom", "kitchen", "office"
- Use discover_devices to see all devices first

### Problem: Open-WebUI shows "Connection failed"

**Solution**:

```powershell
# Test from cluster pod
kubectl run test-ha3 --rm -i --restart=Never --image=curlimages/curl -- \
  curl -s http://ha-mcp-server.cluster-services:8001/health

# If that fails, check Kubernetes Service
kubectl get svc ha-mcp-server -n cluster-services
kubectl get endpoints ha-mcp-server -n cluster-services
```

### Problem: Tools discovered but execution fails

**Check**:

1. View browser console in Open-WebUI (F12)
2. Check request payload format
3. Verify endpoint URL in request
4. Check HA API token is valid: `echo $HA_TOKEN` in container

## 📊 View API Documentation

FastAPI auto-generates beautiful docs:

**Swagger UI** (Interactive):

```
http://192.168.1.203:8001/docs
```

- Try each endpoint live
- See request/response schemas
- View examples

**ReDoc** (Clean docs):

```
http://192.168.1.203:8001/redoc
```

- Better for reading
- Search functionality
- Clean layout

**OpenAPI JSON** (Machine-readable):

```
http://192.168.1.203:8001/openapi.json
```

- Used by Open-WebUI
- Can import to Postman
- For API clients

## 📈 What's Next?

After successful deployment and testing:

### Phase 2: Add Remaining 65 Endpoints

- Dashboard management (9 tools)
- Security & Intelligence (8 tools)
- Energy optimization (6 tools)
- Workflows & Scripts (16 tools)
- Add-on management (9 tools)
- Code execution (3 tools)
- Advanced camera/VLM (4 tools)
- Misc utilities (10 tools)

**Estimate**: 4-6 hours implementation

### Phase 3: Production Hardening

- Rate limiting
- Authentication middleware
- Request caching
- Performance monitoring
- Load balancing
- Docker containerization
- Kubernetes deployment

## 🎬 Your Next Command

```powershell
# Do it now! 🚀
cd C:\MyProjects\ha-openapi-server-v2
.\deploy.ps1 -HaHost 192.168.1.203

# Then test your original request
$body = @{ area_name = "living room" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://192.168.1.203:8001/get_area_devices" `
    -Method Post -Body $body -ContentType "application/json"

# Then add to Open-WebUI and ask:
# "Check what devices are in my living room"
```

---

**You've got this!** The hard part (architecture redesign) is done. Now it's just deployment and validation. 🎉
