# Home Assistant LLM Integration Analysis

**Date:** November 7, 2025  
**Purpose:** Analyze `llm.Tool` class vs REST/WebSocket for dashboard tools  
**Folder:** v4.0.7

---

## 🎯 Executive Summary

**Key Finding:** `llm.Tool` class is for **INTERNAL HA integrations**, not external API servers like ours.

**Decision:**

- ✅ Use **WebSocket** for dashboard tools (original plan)
- ✅ Use **REST API `/api/intent/handle`** for natural language support (already added in v4.0.6!)
- ✅ Document how users can create their own `llm.Tool` integrations (bonus)

---

## 📚 What is `llm.Tool`?

### Purpose

The `llm.Tool` class allows **Home Assistant integrations** to register custom tools that can be called by LLMs through HA's built-in Conversation Agent.

### Architecture

```
User → LLM (OpenAI/etc) → HA Conversation Agent → llm.Tool → HA Integration → Action
```

### Example: Custom Time Tool

```python
from homeassistant.core import HomeAssistant
from homeassistant.helper import llm
from homeassistant.util import dt as dt_util
from homeassistant.util.json import JsonObjectType

class TimeTool(llm.Tool):
    """Tool to get the current time."""

    name = "GetTime"
    description = "Returns the current time."

    parameters = vol.Schema({
        vol.Optional('timezone'): str,
    })

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: ToolInput,
        llm_context: LLMContext
    ) -> JsonObjectType:
        """Call the tool."""
        if "timezone" in tool_input.tool_args:
            tzinfo = dt_util.get_time_zone(tool_input.tool_args["timezone"])
        else:
            tzinfo = dt_util.DEFAULT_TIME_ZONE

        return dt_util.now(tzinfo).isoformat()
```

---

## ❌ Why We CANNOT Use `llm.Tool` for Dashboard Tools

### Reason 1: We're External, Not Internal

**Our Architecture:**

```
User → Open-WebUI → Our FastAPI Server → HA REST/WebSocket APIs
```

**`llm.Tool` Architecture:**

```
User → LLM → HA Conversation Agent → llm.Tool → HA Internal Code
```

**Problem:** `llm.Tool` requires code to run INSIDE Home Assistant as a custom integration.

### Reason 2: Dashboard Operations Need Direct API Access

Dashboard tools need to:

- Read/write Lovelace configurations
- Manage dashboard metadata
- Create/delete dashboards
- Update card configurations

**`llm.Tool` limitations:**

- Can only do what HA's internal APIs allow
- Limited to intent-based actions
- Cannot directly manipulate Lovelace configs
- No direct access to dashboard APIs

### Reason 3: Deployment Complexity

**To use `llm.Tool`, we would need to:**

1. Create a custom HA integration
2. Package it as HACS custom component
3. Install it on user's HA instance
4. Configure it in HA UI
5. Register API with HA LLM system

**Our current approach:**

1. Deploy FastAPI server as HA add-on ✅
2. Use it immediately ✅

---

## ✅ What We CAN Do: Hybrid Approach

### 1. Use REST API for Natural Language (DONE in v4.0.6!)

**Tool:** `ha_process_intent`

```python
@app.post("/ha_process_intent")
async def ha_process_intent(text: str, language: str = "en"):
    """
    Process natural language via HA's Assist API.

    Example: "turn on the kitchen lights"
    """
    response = await http_client.post(
        f"{HA_URL}/intent/handle",
        json={"text": text, "language": language}
    )
    return response.json()
```

**This gives us:**

- ✅ Natural language support
- ✅ Access to all HA intents
- ✅ No custom integration needed
- ✅ Already deployed!

### 2. Use WebSocket for Dashboard Tools (v4.0.7 Plan)

**Dashboard operations require WebSocket:**

```python
class HomeAssistantWebSocket:
    async def call_command(self, command_type: str, **params):
        """
        Call WebSocket command like:
        - "lovelace/dashboards/list"
        - "lovelace/config"
        - "lovelace/config/save"
        """
        ...
```

**This gives us:**

- ✅ Full dashboard management
- ✅ Real-time operations
- ✅ Official HA API compliance
- ✅ No custom integration needed

### 3. Document How Users Can Create `llm.Tool` Integrations (Bonus)

**Create guide:** `CUSTOM_LLM_TOOLS_GUIDE.md`

Show users how to:

- Create custom HA integration with `llm.Tool`
- Register it with HA LLM system
- Expose it to conversation agents
- Use it alongside our API server

---

## 🎉 What We Get from LLM Integration Docs

### Already Implemented in v4.0.6

**1. Intent Handling via REST**

```python
POST /api/intent/handle
{
  "text": "turn on the kitchen lights",
  "language": "en"
}
```

**Use Cases:**

- Natural language commands
- Voice assistant integration
- AI-powered automation
- Conversational control

**2. Template Rendering**

```python
POST /api/template
{
  "template": "{{ states('sensor.temperature') }}°C"
}
```

**Use Cases:**

- Dynamic content
- Complex queries
- Custom formatting
- State calculations

**3. Config Validation**

```python
POST /api/config/core/check_config
```

**Use Cases:**

- Pre-restart validation
- Safety checks
- Error prevention

---

## 🚀 v4.0.7 Implementation Plan (UPDATED)

### Phase 1: REST API Tools (DONE in v4.0.6!)

- ✅ `ha_process_intent` - Natural language
- ✅ `ha_render_template` - Jinja2 rendering
- ✅ `ha_validate_config` - Config check

### Phase 2: WebSocket for Dashboards (v4.0.7)

- ⏳ Implement WebSocket client
- ⏳ Update 10 dashboard tools
- ⏳ Test all operations
- ⏳ Deploy to production

### Phase 3: Documentation (v4.0.7)

- ⏳ Create `CUSTOM_LLM_TOOLS_GUIDE.md`
- ⏳ Document intent usage patterns
- ⏳ Show integration examples
- ⏳ Explain hybrid architecture

---

## 📊 Architecture Comparison

### Option A: `llm.Tool` (Internal Integration)

```
Pros:
- Native HA integration
- Conversation agent support
- Intent-based control

Cons:
- Requires custom integration development
- Complex deployment (HACS/manual)
- Limited to intent capabilities
- Cannot directly access dashboard APIs
- Users must install custom integration
```

### Option B: Our FastAPI Server (Current)

```
Pros:
- Simple deployment (HA add-on)
- Full REST/WebSocket API access
- Direct dashboard management
- No user installation needed
- Flexible architecture

Cons:
- External to HA
- Not native conversation agent
```

### ✅ Option C: Hybrid (BEST CHOICE!)

```
Our API Server:
- Dashboard management (WebSocket)
- Direct API access (REST)
- Natural language via /api/intent/handle
- Template rendering
- Config validation

Users Can Add (Optional):
- Custom llm.Tool integrations for specialized tasks
- Conversation agent customization
- Domain-specific tools
```

---

## 🎓 Key Learnings

### 1. Intent Handling is Available via REST

**We can use natural language WITHOUT `llm.Tool`:**

```python
response = await http_client.post(
    f"{HA_URL}/intent/handle",
    json={"text": "turn on the kitchen lights"}
)
```

**This gives us 90% of the benefit with 10% of the complexity!**

### 2. `llm.Tool` is for Integration Developers

**Not for us (external API consumers), but we can:**

- Document it for users who want custom tools
- Show examples in our guides
- Explain how it complements our server

### 3. WebSocket is Still the Right Choice for Dashboards

**Dashboard operations are not intent-based:**

- Reading dashboard configs
- Creating/deleting dashboards
- Updating card configurations
- Managing Lovelace resources

**These require direct WebSocket commands, not intents.**

---

## 📝 Recommendations

### For v4.0.7 (Immediate)

1. ✅ **Stick with WebSocket plan** for dashboard tools
2. ✅ **Keep REST API tools** from v4.0.6 (`ha_process_intent`, etc.)
3. ✅ **Create comprehensive documentation** showing:
   - How to use our intent handler
   - When to use REST vs WebSocket
   - How users can create custom `llm.Tool` integrations (optional)

### For Future (v4.1.0+)

1. 🌟 **Create companion HA integration** (optional):

   - Uses `llm.Tool` for specialized tasks
   - Complements our API server
   - Registered with HA conversation agent
   - Available in HACS

2. 🌟 **Hybrid architecture**:
   - Our server: Dashboard management, direct API access
   - Custom integration: Domain-specific tools, conversation agent features

---

## ✅ Final Decision

**For v4.0.7:**

- ✅ Use **WebSocket** for 10 dashboard tools (as originally planned)
- ✅ Keep **REST API** tools from v4.0.6 (intent, template, config)
- ✅ Create documentation explaining both approaches
- ✅ Show users how to create custom `llm.Tool` if they want

**Why:**

- WebSocket gives us full dashboard control
- REST intent handler gives us natural language
- No custom integration deployment complexity
- Users can still add `llm.Tool` integrations if desired
- Best of both worlds!

---

## 🎯 Success Metrics (Updated)

**v4.0.6 (DONE):**

- ✅ 95 tools total
- ✅ 85 working (89%)
- ✅ Natural language support via `/api/intent/handle`
- ✅ Template rendering via `/api/template`
- ✅ Config validation via `/api/config/core/check_config`

**v4.0.7 (In Progress):**

- ⏳ 95 tools total
- ⏳ 95 working (100%) ← **MILESTONE!**
- ⏳ Full dashboard management via WebSocket
- ⏳ No more 404 errors
- ⏳ Complete API coverage

---

**Conclusion:** `llm.Tool` is exciting, but it's for a different use case! Our WebSocket + REST hybrid approach is the right choice for our external API server. 🚀

**Analysis Completed:** November 7, 2025  
**Decision:** Proceed with WebSocket implementation as planned  
**Status:** ✅ Ready to implement v4.0.7
