# 🚀 QUICK SOLUTION: Add Code Execution to HA MCP Server

## The Better Approach

Instead of adding a separate code-interpreter MCP server, we can **add code execution tools directly to the HA MCP server** since it already runs Python!

This gives you instant state data + pandas analysis in the same tool call.

---

## New Tools to Add

Add these 3 tools to `server.py`:

### 1. `execute_python` - Run arbitrary Python code

```python
Tool(
    name="execute_python",
    description="Execute Python code with access to pandas, matplotlib, numpy. Can analyze HA data.",
    inputSchema={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
            "return_stdout": {"type": "boolean", "description": "Return print() output", "default": True},
            "return_plots": {"type": "boolean", "description": "Return matplotlib plots as base64", "default": True}
        },
        "required": ["code"]
    }
)
```

### 2. `analyze_states_dataframe` - Get HA states as pandas DataFrame

```python
Tool(
    name="analyze_states_dataframe",
    description="Get all HA entity states as a pandas DataFrame for analysis",
    inputSchema={
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Filter by domain (light, sensor, etc)"},
            "query": {"type": "string", "description": "Pandas query string to filter results"}
        }
    }
)
```

### 3. `plot_sensor_history` - Quick time-series plots

```python
Tool(
    name="plot_sensor_history",
    description="Plot sensor history as a time-series chart",
    inputSchema={
        "type": "object",
        "properties": {
            "entity_ids": {"type": "array", "items": {"type": "string"}},
            "hours": {"type": "number", "default": 24},
            "chart_type": {"type": "string", "enum": ["line", "bar", "scatter"], "default": "line"}
        },
        "required": ["entity_ids"]
    }
)
```

---

## Implementation

I'll create an updated `server.py` with these 3 code execution tools integrated.

**Deploy to HA add-on:**

```bash
scp server.py root@192.168.1.203:/config/addons/local/ha-mcp-server/
# Then restart add-on in HA UI
```

**Total tools: 74 + 3 = 77 tools!**

---

## Usage Examples

### In Open-WebUI:

**Example 1: Get states as DataFrame**

```
You: Show me all lights as a pandas DataFrame

Tool call: analyze_states_dataframe(domain="light")
Result: DataFrame with columns: entity_id, state, brightness, color, etc.
```

**Example 2: Custom analysis**

```
You: Get all temperature sensors and calculate the average

Tool call: analyze_states_dataframe(domain="sensor", query="entity_id.str.contains('temp')")
Then: execute_python(code="df['state'].astype(float).mean()")
Result: 22.4°C
```

**Example 3: Visualization**

```
You: Plot living room temperature for the past 12 hours

Tool call: plot_sensor_history(
    entity_ids=["sensor.living_room_temperature"],
    hours=12
)
Result: <base64 PNG image displayed in chat>
```

**Example 4: Complex analysis**

```
You: Which rooms have the highest power consumption right now?

Tool calls:
1. analyze_states_dataframe(domain="sensor", query="entity_id.str.contains('power')")
2. execute_python(code='''
df_grouped = df.groupby('room')['state'].apply(lambda x: x.astype(float).sum())
df_grouped.sort_values(ascending=False).head(5)
''')

Result:
Room            Power (W)
Living Room     245.3
Kitchen         189.7
Bedroom         67.2
...
```

---

## Benefits

✅ **No separate MCP server needed** - Code execution built into HA server  
✅ **Direct HA data access** - No need to pass data between servers  
✅ **Faster** - Single tool call instead of chaining  
✅ **Simpler deployment** - Just update one file  
✅ **Safe sandbox** - Uses Python's `exec()` with restricted globals

---

## Ready to Deploy?

Say "yes" and I'll:

1. Create the updated `server.py` with 3 new code execution tools
2. Show you how to deploy it
3. Give you example prompts to test

This will give you **instant live data analysis** in Open-WebUI! 🚀
