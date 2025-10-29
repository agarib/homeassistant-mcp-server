# 🎯 How to Add MCP Servers to Open-WebUI (Corrected Guide)

**Date:** October 28, 2025  
**Issue:** CODE_INTERPRETER_INTEGRATION.md had outdated instructions  
**Status:** ✅ Corrected for current Open-WebUI + MCPO architecture

---

## ⚠️ Important Understanding

**Open-WebUI does NOT have a native "External Tools → MCP Server" interface!**

The old documentation was wrong. Here's how it **actually** works:

---

## 🏗️ The Real Architecture

```
Open-WebUI (192.168.1.11:30080)
       ↓
   Uses LLM with Function Calling
       ↓
   Calls MCPO HTTP Gateway (http://mcpo-server:8000)
       ↓
MCPO exposes MCP servers as HTTP sub-routes:
   • /homeassistant → HA MCP Server (104 tools)
   • /filesystem → Filesystem MCP
   • /memory → Memory Graph MCP
   • /code-interpreter → Code Execution MCP (if configured)
   • /github → GitHub MCP
   • /sqlite → SQLite MCP
```

**Key Point:** MCPO translates MCP protocol → HTTP/OpenAPI, so Open-WebUI sees regular HTTP endpoints, not MCP servers.

---

## ✅ Correct Way to Use MCP Tools in Open-WebUI

### Method 1: Direct OpenAPI Integration (Recommended)

**What MCPO Does:**

- Exposes each MCP server on a sub-route (e.g., `/homeassistant`)
- Provides OpenAPI spec at `/homeassistant/openapi.json`
- Translates MCP tool calls to HTTP requests

**How Open-WebUI Uses It:**

1. **Enable Function Calling in Model Settings**

   In Open-WebUI:

   - Go to **Settings** → **Models**
   - Select your model (e.g., llama3.1, gpt-4, etc.)
   - Enable **"Function Calling"** or **"Tools"**
   - Set **Max Tool Calls**: `10` (allows chaining multiple MCP calls)

2. **Open-WebUI Auto-Discovers Tools**

   When you chat, the LLM can automatically:

   - Detect when to use external tools
   - Call MCPO endpoints
   - Chain multiple tool calls

3. **Reference MCPO Endpoints in Prompts** (Optional)

   You can explicitly guide the LLM:

   ```
   You: "Use the Home Assistant tools to turn on light.living_room"

   LLM: [Calls http://mcpo-server:8000/homeassistant/call_tool]
   ```

---

### Method 2: Custom Functions (Manual Integration)

If Open-WebUI doesn't auto-discover MCPO tools, you can create custom functions:

1. **Go to Admin Settings → Functions**

2. **Create New Function** for Home Assistant:

```python
"""
valve: true
name: homeassistant_control
"""

import requests
from typing import Optional

class Tools:
    def __init__(self):
        self.mcpo_url = "http://mcpo-server:8000/homeassistant"

    def get_states(self, domain: Optional[str] = None) -> str:
        """
        Get Home Assistant entity states.

        Args:
            domain: Filter by domain (e.g., 'light', 'switch', 'sensor')

        Returns:
            JSON string of entity states
        """
        response = requests.post(
            f"{self.mcpo_url}/call_tool",
            json={
                "name": "get_states",
                "parameters": {"domain": domain} if domain else {}
            }
        )
        return response.json()

    def control_light(self, entity_id: str, action: str, brightness: Optional[int] = None) -> str:
        """
        Control a light entity.

        Args:
            entity_id: Light entity ID (e.g., 'light.living_room')
            action: 'turn_on', 'turn_off', or 'toggle'
            brightness: Optional brightness (0-255)

        Returns:
            Result message
        """
        params = {"entity_id": entity_id, "action": action}
        if brightness is not None:
            params["brightness"] = brightness

        response = requests.post(
            f"{self.mcpo_url}/call_tool",
            json={"name": "control_light", "parameters": params}
        )
        return response.json()
```

3. **Save and Enable** the function

4. **Use in Chat**:

```
You: "Get all light states and show me which ones are on"

LLM: [Calls homeassistant_control.get_states(domain='light')]
```

---

### Method 3: OpenAPI URL Configuration (If Supported)

Some Open-WebUI versions support adding OpenAPI endpoints:

1. **Get the OpenAPI Spec URL**:

   ```
   http://mcpo-server:8000/homeassistant/openapi.json
   ```

2. **Check Open-WebUI Settings**:

   - Look for **"External APIs"** or **"OpenAPI Specs"**
   - Add the MCPO endpoint URL
   - Open-WebUI will auto-import tool schemas

3. **If this option doesn't exist** → Use Method 1 or 2

---

## 🧪 Testing the Integration

### Test 1: Verify MCPO is Accessible

From Open-WebUI pod or your browser:

```bash
# Check MCPO health
curl http://mcpo-server:8000/health

# Get Home Assistant OpenAPI spec
curl http://mcpo-server:8000/homeassistant/openapi.json | jq .

# List available routes
curl http://mcpo-server:8000/ | jq .
```

**Expected:** Returns JSON with server info

### Test 2: Manual Tool Call

```bash
# Call a tool directly
curl -X POST http://mcpo-server:8000/homeassistant/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_states",
    "parameters": {"domain": "light"}
  }'
```

**Expected:** Returns Home Assistant light states

### Test 3: In Open-WebUI Chat

**Simple Query:**

```
You: "What lights are currently on in Home Assistant?"

LLM: [Internally calls MCPO /homeassistant endpoint]
     "Currently, the following lights are on:
      - light.living_room (brightness: 180)
      - light.kitchen (brightness: 255)"
```

**Complex Query:**

```
You: "Turn off all lights in the living room area"

LLM: [Calls control_light or execute_service via MCPO]
     "I've turned off 3 lights in the living room area."
```

---

## 🔧 Adding Code Interpreter MCP

Based on your CODE_INTERPRETER_INTEGRATION.md, here's the **corrected** process:

### Step 1: Add Code Interpreter to MCPO Config

Update `mcpo-config-updated.yaml`:

```yaml
data:
  config.json: |
    {
      "mcpServers": {
        "homeassistant": {
          "transport": "sse",
          "url": "http://192.168.1.203:8001/messages"
        },
        "code-interpreter": {
          "command": "uvx",
          "args": ["mcp-server-jupyter"],
          "env": {
            "JUPYTER_WORKING_DIR": "/workspace/ai-workspace"
          }
        }
      }
    }
```

**Note:** Use Jupyter MCP server instead of a separate code-interpreter, as it provides:

- Python code execution
- pandas/matplotlib/numpy pre-installed
- Persistent workspace
- Better integration with MCPO

### Step 2: Apply Config and Restart MCPO

```bash
kubectl apply -f mcpo-config-updated.yaml
kubectl rollout restart statefulset mcpo-server -n cluster-services
```

### Step 3: Verify Code Interpreter Available

```bash
kubectl logs mcpo-server-0 -n cluster-services | grep -E "jupyter|code"

# Expected:
# Successfully connected to 'jupyter'
```

### Step 4: Test in Open-WebUI

```
You: "Run Python code: import pandas as pd; print(pd.__version__)"

LLM: [Calls http://mcpo-server:8000/jupyter/call_tool]
     "Pandas version: 2.1.0"
```

### Step 5: Combined HA + Code Analysis

```
You: "Get all temperature sensors from Home Assistant and create
     a pandas DataFrame showing their current values"

What happens:
1. LLM calls /homeassistant → get_states(domain='sensor')
2. Filters for temperature sensors
3. LLM calls /jupyter → execute_code with DataFrame creation
4. Returns formatted table
```

---

## 📊 MCPO Sub-Routes Reference

Your current MCPO setup exposes these MCP servers:

| Route            | MCP Server   | Tools | Purpose              |
| ---------------- | ------------ | ----- | -------------------- |
| `/homeassistant` | HA MCP       | 104   | Smart home control   |
| `/filesystem`    | Filesystem   | ~10   | File operations      |
| `/memory`        | Memory Graph | ~5    | Knowledge graph      |
| `/github`        | GitHub       | ~20   | Git operations       |
| `/sqlite`        | SQLite       | ~10   | Database queries     |
| `/jupyter`       | Jupyter      | ~8    | Code execution       |
| `/time`          | Time         | ~3    | Time operations      |
| `/puppeteer`     | Puppeteer    | ~15   | Web automation       |
| `/fetch`         | Fetch        | ~5    | Web content fetching |

**Access Pattern:**

```
http://mcpo-server:8000/<route>/call_tool
```

---

## 🎯 Practical Examples

### Example 1: Home Control

**User:**

```
"Turn on the living room lights to 50% brightness"
```

**What Happens:**

1. LLM detects need for Home Assistant control
2. Calls MCPO: `POST /homeassistant/call_tool`

   ```json
   {
     "name": "control_light",
     "parameters": {
       "entity_id": "light.living_room",
       "action": "turn_on",
       "brightness": 128
     }
   }
   ```

3. MCPO translates to MCP call → HA MCP server executes
4. Returns success message

### Example 2: Data Analysis

**User:**

```
"Show me a chart of my temperature sensors over the last 24 hours"
```

**What Happens:**

1. LLM calls `/homeassistant` → `get_entity_history`
2. Receives time-series data
3. LLM calls `/jupyter` → `execute_code`:

   ```python
   import pandas as pd
   import matplotlib.pyplot as plt

   df = pd.DataFrame(history_data)
   df['timestamp'] = pd.to_datetime(df['last_changed'])
   df['temp'] = df['state'].astype(float)

   plt.plot(df['timestamp'], df['temp'])
   plt.title('Temperature - Last 24 Hours')
   plt.savefig('temp_chart.png')
   ```

4. Returns chart image

### Example 3: Complex Workflow

**User:**

```
"Which sensors haven't updated in 2 hours? Save the list to a file."
```

**What Happens:**

1. `/homeassistant` → `get_states()` (all sensors)
2. `/jupyter` → Filter by last_changed timestamp
3. `/filesystem` → `write_file` with results
4. Returns: "Found 5 stale sensors, saved to stale_sensors.txt"

---

## 🔍 Debugging

### MCPO Not Responding

**Check MCPO logs:**

```bash
kubectl logs mcpo-server-0 -n cluster-services
```

**Look for:**

- "Successfully connected to 'homeassistant'" ✅
- Connection errors ❌
- Tool execution logs

### Tools Not Being Called

**Verify OpenAPI spec:**

```bash
curl http://mcpo-server:8000/homeassistant/openapi.json
```

**Should return:** JSON with tool definitions

**Check Open-WebUI logs:**

```bash
kubectl logs -l app=open-webui -n cluster-services
```

### Network Issues

**Test from Open-WebUI pod:**

```bash
kubectl exec -it <openwebui-pod> -n cluster-services -- sh
curl http://mcpo-server:8000/health
```

**Should return:** `{"status": "healthy"}`

---

## ✅ Correct Configuration Summary

**MCPO Config** (`mcpo-config-updated.yaml`):

```yaml
"homeassistant":
  { "transport": "sse", "url": "http://192.168.1.203:8001/messages" }
```

**MCPO Service** (already deployed):

```
http://mcpo-server:8000 (internal)
http://192.168.1.13:31634 (external NodePort)
```

**Open-WebUI Access**:

- **Internal**: `http://open-webui:8080` (pod-to-pod)
- **External**: `http://192.168.1.11:30080` (NodePort)

**How Open-WebUI Calls MCPO**:

```
Open-WebUI LLM → Function Call Decision →
http://mcpo-server:8000/homeassistant/call_tool →
MCPO translates to MCP → HA MCP Server executes →
Response back through chain
```

---

## 📚 Key Differences from Old Docs

| Old (Incorrect)                            | New (Correct)              |
| ------------------------------------------ | -------------------------- |
| Settings → External Tools → Add MCP Server | No such menu exists        |
| Type: "MCP Server"                         | Use OpenAPI/Functions      |
| Direct MCP URL                             | Use MCPO HTTP gateway      |
| Manual tool configuration                  | Auto-discovery via OpenAPI |

---

## 🎉 Summary

**TO ADD MCP SERVERS TO OPEN-WEBUI:**

1. ✅ **Already Done**: MCPO exposes MCP servers as HTTP endpoints
2. ✅ **Already Done**: Home Assistant MCP at `/homeassistant`
3. ⚠️ **Optional**: Add Jupyter MCP for code execution
4. ✅ **Enable** Function Calling in Open-WebUI model settings
5. ✅ **Use** natural language queries - LLM handles tool calls automatically

**YOU DON'T NEED TO "ADD" ANYTHING TO OPEN-WEBUI!**

MCPO is already configured and running. Open-WebUI accesses tools through the MCPO HTTP gateway automatically when function calling is enabled on your model.

---

**Status**: ✅ Corrected  
**Next**: Just enable function calling on your Open-WebUI model and start chatting!
