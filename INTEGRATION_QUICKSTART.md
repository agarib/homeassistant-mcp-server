# 🚀 Consolidation Quick Start - Unified HA Server

## 📋 What You Have

✅ **4 Files Ready:**

1. `tool_additions.py` - Source code (16 tools)
2. `CONSOLIDATION_GUIDE.md` - Complete integration guide
3. `NEW_TOOLS_REFERENCE.md` - Tool usage reference
4. `Deploy-Unified-HA-Server.ps1` - Deployment script

✅ **93 Total Tools:**

- 12 Native MCPO (converted to FastAPI)
- 4 NEW System Diagnostics
- 77 Existing Production Tools

---

## ⚡ 5-Minute Integration

### 1. Backup Current Server

```powershell
cd C:\MyProjects\ha-openapi-server-v3.0.0
cp server.py server.py.backup
```

### 2. Add HomeAssistantAPI Methods

Open `server.py`, find the `HomeAssistantAPI` class (~line 120), add these methods:

```python
async def get_services(self) -> dict:
    """Get all available HA services"""
    response = await http_client.get(f"{HA_URL}/api/services")
    response.raise_for_status()
    return response.json()

async def fire_event(self, event_type: str, event_data: dict = None) -> dict:
    """Fire a custom event"""
    response = await http_client.post(
        f"{HA_URL}/api/events/{event_type}",
        json=event_data or {}
    )
    response.raise_for_status()
    return response.json()

async def render_template(self, template: str) -> str:
    """Render a Jinja2 template"""
    response = await http_client.post(
        f"{HA_URL}/api/template",
        json={"template": template}
    )
    response.raise_for_status()
    return response.text

async def get_config(self) -> dict:
    """Get HA configuration"""
    response = await http_client.get(f"{HA_URL}/api/config")
    response.raise_for_status()
    return response.json()
```

### 3. Copy Tool Endpoints

1. Open `tool_additions.py`
2. Copy ALL content starting from `# 1. Control Light` to end of file
3. In `server.py`, find the `/health` endpoint (~line 3600)
4. Paste the copied content **BEFORE** `/health`

### 4. Update Docstring

At top of `server.py` (~line 10), update the tool count:

Change:

```python
"""
Home Assistant OpenAPI Server v3.0.0
77 production-ready tools...
```

To:

```python
"""
Home Assistant OpenAPI Server v3.0.0
93 unified tools with Pydantic validation...

📦 TOOL CATEGORIES (93 tools):
✅ Native MCPO Tools (12 tools) - Standard HA control
✅ System Diagnostics (4 tools) - Logs, notifications, integration status
... (rest of existing categories)
```

### 5. Test Locally

```powershell
python server.py
```

Visit: http://localhost:8001/docs

**Verify:**

- ✅ 93 endpoints visible
- ✅ Tags show `native_mcpo` and `system_diagnostics`

### 6. Deploy to Cluster

```powershell
.\Deploy-Unified-HA-Server.ps1 -Deploy
```

---

## 🧪 Quick Test - Washing Machine Fix

### Test 1: Get Notifications

```bash
curl -X POST http://localhost:8001/get_persistent_notifications \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test 2: Check LG Integration

```bash
curl -X POST http://localhost:8001/get_integration_status \
  -H "Content-Type: application/json" \
  -d '{"integration": "lg"}'
```

### Test 3: Read Error Logs

```bash
curl -X POST http://localhost:8001/get_system_logs \
  -H "Content-Type: application/json" \
  -d '{"lines": 100, "level": "ERROR"}'
```

---

## 🎯 Success Criteria

- [ ] Server starts without errors
- [ ] `/docs` shows 93 endpoints
- [ ] Tags include `native_mcpo` and `system_diagnostics`
- [ ] Can test diagnostics tools successfully
- [ ] Cluster deployment successful

---

**Estimated Time:** 10-15 minutes  
**Difficulty:** Easy (copy/paste with 4 new methods)  
**Payoff:** 93 unified tools + washing machine diagnostics! 🎯
