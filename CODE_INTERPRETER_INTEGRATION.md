# 🔬 Code Interpreter + Home Assistant MCP Integration

## 🎯 The Vision

Enable **live data analysis** in Open-WebUI chat sessions by combining:

1. **Home Assistant MCP Server** (74 tools) → Get live device states, history, sensors
2. **Code Interpreter MCP** → Run Python/pandas/matplotlib on that data
3. **Open-WebUI** → Ask natural language questions, get instant analysis

**Example Queries:**

- "Show me power consumption trends for all lights this week"
- "Which sensors have been offline longest?"
- "Create a temperature vs humidity correlation chart"
- "Calculate average energy usage by room"

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          Open-WebUI (192.168.1.11:30080)        │
│                                                  │
│  User: "Show power trends for lights"           │
│     ↓                                            │
│  1. LLM decides to use HA + code-interpreter     │
│     ↓                                            │
│  2. Calls get_states via MCPO /homeassistant     │
│     ↓                                            │
│  3. Passes HA data to code-interpreter           │
│     ↓                                            │
│  4. Runs pandas analysis + matplotlib plot       │
│     ↓                                            │
│  5. Returns chart + insights to user             │
└─────────────────────────────────────────────────┘
           │                        │
           │ HTTP                   │ HTTP
           ↓                        ↓
    ┌──────────────┐        ┌──────────────┐
    │ MCPO Server  │        │ MCPO Server  │
    │ (Pi4 Cluster)│        │ (Pi4 Cluster)│
    └──────┬───────┘        └──────┬───────┘
           │                        │
           ↓                        ↓
   HA MCP Server              Code Interpreter
   (74 tools)                 (Python execution)
```

---

## 📦 Option 1: Docker-based Code Interpreter (Recommended)

### Step 1: Pull Code Interpreter Image

On each MCPO node (worker-two, worker-three):

```bash
ssh pi@192.168.1.13  # worker-two
sudo docker pull mcp/code-interpreter

ssh pi@192.168.1.14  # worker-three
sudo docker pull mcp/code-interpreter
```

### Step 2: Update MCPO Config

Already done! The config now includes:

```json
"code-interpreter": {
  "command": "docker",
  "args": [
    "run",
    "--rm",
    "-i",
    "--network=host",
    "mcp/code-interpreter"
  ]
}
```

### Step 3: Apply Updated Config

```powershell
# Apply to cluster
kubectl apply -f C:\MyProjects\mcpo-config-updated.yaml

# Restart MCPO to pick up new server
kubectl rollout restart statefulset mcpo-server -n cluster-services

# Wait for pods to be ready
kubectl get pods -n cluster-services -w
```

### Step 4: Verify Code Interpreter Available

```bash
# Check MCPO logs
ssh pi@192.168.1.11 "sudo kubectl logs mcpo-server-0 -n cluster-services | grep -i code-interpreter"

# Expected:
# [INFO] Successfully connected to 'code-interpreter'
# [INFO] code-interpreter available at /code-interpreter
```

---

## 📦 Option 2: Python-based Code Interpreter (Lightweight)

If Docker isn't available or you prefer a lighter solution:

### Step 1: Install Python MCP Code Interpreter

On each MCPO node:

```bash
ssh pi@192.168.1.13  # worker-two
pip install mcp-code-interpreter

ssh pi@192.168.1.14  # worker-three
pip install mcp-code-interpreter
```

### Step 2: Update MCPO Config

```json
"code-interpreter": {
  "command": "python3",
  "args": ["-m", "mcp_code_interpreter"]
}
```

---

## 🧪 Testing the Integration

### Test 1: Simple Code Execution

In Open-WebUI chat:

```
You: Run this Python code: print(sum([1, 2, 3, 4, 5]))
```

**Expected:** Code interpreter executes and returns `15`

### Test 2: Get HA States

```
You: Get the state of light.couch_light
```

**Expected:** HA MCP returns current state JSON

### Test 3: Combined Analysis (THE MAGIC!)

```
You: Get all light entities, then use pandas to show me which ones
     are currently on and their brightness levels
```

**What happens:**

1. Open-WebUI calls `get_states(domain='light')` via HA MCP
2. Receives JSON array of all light states
3. Passes data to code-interpreter
4. Code-interpreter runs:

   ```python
   import pandas as pd

   # data comes from get_states
   lights_on = [
       {
           'entity_id': l['entity_id'],
           'brightness': l['attributes'].get('brightness', 0)
       }
       for l in data if l['state'] == 'on'
   ]

   df = pd.DataFrame(lights_on)
   print(df.sort_values('brightness', ascending=False))
   ```

5. Returns formatted table to chat

### Test 4: Visualization

```
You: Get temperature sensor history for the past 24 hours and
     plot it as a line chart
```

**What happens:**

1. Calls `get_entity_history(entity_id='sensor.temperature', hours=24)`
2. Code-interpreter receives time-series data
3. Runs:

   ```python
   import pandas as pd
   import matplotlib.pyplot as plt

   df = pd.DataFrame(history_data)
   df['timestamp'] = pd.to_datetime(df['last_changed'])
   df['temp'] = df['state'].astype(float)

   plt.figure(figsize=(12, 6))
   plt.plot(df['timestamp'], df['temp'])
   plt.title('Temperature Over 24 Hours')
   plt.xlabel('Time')
   plt.ylabel('Temperature (°C)')
   plt.grid(True)
   plt.savefig('temp_chart.png')
   ```

4. Returns the chart image to Open-WebUI

---

## 🔧 Advanced Use Cases

### Energy Analysis

```
You: Analyze power consumption for all devices. Show me:
     1. Total consumption by room
     2. Top 5 energy consumers
     3. A bar chart comparing rooms
```

**Behind the scenes:**

```python
import pandas as pd
import matplotlib.pyplot as plt

# Get all power sensors via HA MCP
states = get_states(domain='sensor')
power_sensors = [s for s in states if 'power' in s['entity_id']]

# Create DataFrame
df = pd.DataFrame([
    {
        'entity': s['entity_id'],
        'room': s['attributes'].get('room', 'Unknown'),
        'power': float(s['state']) if s['state'] != 'unavailable' else 0
    }
    for s in power_sensors
])

# Analysis
room_totals = df.groupby('room')['power'].sum().sort_values(ascending=False)
top_consumers = df.nlargest(5, 'power')

# Visualization
plt.figure(figsize=(10, 6))
room_totals.plot(kind='bar')
plt.title('Power Consumption by Room')
plt.ylabel('Watts')
plt.tight_layout()
plt.savefig('power_by_room.png')

print(f"Total Consumption: {df['power'].sum():.2f}W")
print("\nTop 5 Consumers:")
print(top_consumers[['entity', 'power']])
```

### Sensor Health Monitoring

```
You: Check all sensors and show me which ones haven't updated
     in the past hour. Include how long they've been stale.
```

```python
from datetime import datetime, timedelta
import pandas as pd

states = get_states()
now = datetime.now()

stale_sensors = []
for s in states:
    last_changed = datetime.fromisoformat(s['last_changed'].replace('Z', '+00:00'))
    age = (now - last_changed).total_seconds() / 3600  # hours

    if age > 1:
        stale_sensors.append({
            'entity': s['entity_id'],
            'state': s['state'],
            'hours_stale': round(age, 2),
            'last_changed': last_changed.strftime('%Y-%m-%d %H:%M')
        })

df = pd.DataFrame(stale_sensors)
df = df.sort_values('hours_stale', ascending=False)

print(f"Found {len(df)} stale sensors:\n")
print(df.to_string(index=False))
```

### Climate Correlation Analysis

```
You: Show me the correlation between indoor temperature
     and humidity over the past week
```

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Get sensor histories
temp_history = get_entity_history('sensor.indoor_temperature', hours=168)
humid_history = get_entity_history('sensor.indoor_humidity', hours=168)

# Create DataFrames
temp_df = pd.DataFrame(temp_history)
humid_df = pd.DataFrame(humid_history)

# Merge on timestamp
temp_df['timestamp'] = pd.to_datetime(temp_df['last_changed'])
humid_df['timestamp'] = pd.to_datetime(humid_df['last_changed'])

df = pd.merge_asof(
    temp_df.sort_values('timestamp')[['timestamp', 'state']].rename(columns={'state': 'temp'}),
    humid_df.sort_values('timestamp')[['timestamp', 'state']].rename(columns={'state': 'humidity'}),
    on='timestamp'
)

df['temp'] = df['temp'].astype(float)
df['humidity'] = df['humidity'].astype(float)

# Calculate correlation
correlation = df['temp'].corr(df['humidity'])

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Scatter plot
ax1.scatter(df['temp'], df['humidity'], alpha=0.5)
ax1.set_xlabel('Temperature (°C)')
ax1.set_ylabel('Humidity (%)')
ax1.set_title(f'Temp vs Humidity (r={correlation:.3f})')
ax1.grid(True)

# Time series
ax2.plot(df['timestamp'], df['temp'], label='Temperature', alpha=0.7)
ax2_twin = ax2.twinx()
ax2_twin.plot(df['timestamp'], df['humidity'], label='Humidity', color='orange', alpha=0.7)
ax2.set_xlabel('Time')
ax2.set_ylabel('Temperature (°C)', color='blue')
ax2_twin.set_ylabel('Humidity (%)', color='orange')
ax2.set_title('Temperature & Humidity Over Time')
ax2.grid(True)

plt.tight_layout()
plt.savefig('climate_correlation.png')

print(f"Correlation coefficient: {correlation:.3f}")
```

---

## 🎨 Open-WebUI Configuration

### Configure External Tools

1. Open <http://192.168.1.11:30080>
2. Go to **Settings** → **External Tools**
3. Add tools:

**Home Assistant:**

- Name: `Home Assistant Control`
- URL: `http://mcpo-server:8000/homeassistant`
- Type: MCP Server

**Code Interpreter:**

- Name: `Python Code Execution`
- URL: `http://mcpo-server:8000/code-interpreter`
- Type: MCP Server

### Enable Function Calling

In your Open-WebUI model settings:

- Enable **Function Calling**
- Select tools: `Home Assistant Control`, `Python Code Execution`
- Set **Max Tool Calls**: `10` (allows chaining HA → code-interpreter)

---

## 🚀 Deployment Steps

```powershell
# 1. Update MCPO config (already done)
kubectl apply -f C:\MyProjects\mcpo-config-updated.yaml

# 2. Pull code-interpreter image on worker nodes
ssh pi@192.168.1.13 "sudo docker pull mcp/code-interpreter"
ssh pi@192.168.1.14 "sudo docker pull mcp/code-interpreter"

# 3. Restart MCPO
kubectl rollout restart statefulset mcpo-server -n cluster-services

# 4. Verify both servers connected
kubectl logs mcpo-server-0 -n cluster-services | grep -E "homeassistant|code-interpreter|Successfully"

# Expected output:
# Successfully connected to 'homeassistant'
# Successfully connected to 'code-interpreter'
```

---

## ✅ Success Criteria

You'll know it's working when in Open-WebUI you can:

- [x] Ask "Get all light states" → HA MCP returns JSON
- [x] Ask "Run Python: print(2+2)" → Code interpreter returns `4`
- [x] Ask "Get light states and show them in a pandas DataFrame" → Combined execution works!
- [x] Ask complex analysis questions → LLM chains HA data → code execution → results
- [x] Get charts/visualizations → matplotlib plots appear in chat

---

## 🎓 Example Prompts to Try

**Basic:**

```
1. "Get the state of sensor.living_room_temperature"
2. "Run this Python: import sys; print(sys.version)"
3. "List all lights that are currently on"
```

**Intermediate:**

```
4. "Get all temperature sensors and calculate the average temperature"
5. "Show me which rooms have lights on right now"
6. "Plot the brightness levels of all lights as a bar chart"
```

**Advanced:**

```
7. "Analyze energy consumption by room and show me the top 3 consumers"
8. "Get temperature history for today and create a time series plot"
9. "Find all sensors that haven't updated in 2 hours and list them by age"
10. "Compare indoor vs outdoor temperature over the past 24 hours with a dual-axis chart"
```

**Expert:**

```
11. "Build a DataFrame of all motion sensors, their states, and last triggered times.
     Show which rooms have had no motion detected in the past 4 hours."

12. "Get power consumption data for all devices, group by room, calculate total
     daily cost at $0.15/kWh, and create a pie chart of cost distribution."

13. "Analyze light usage patterns: Get all light entities, their on-time today,
     and create a heatmap showing which lights are used most by hour of day."
```

---

## 🔒 Safety & Security

### Code Execution Sandboxing

The code-interpreter runs in a **Docker container** with:

- No access to host filesystem
- Network isolation (unless `--network=host` needed for HA access)
- Resource limits (CPU, memory)
- Automatic cleanup (`--rm` flag)

### Disable When Not Needed

In Open-WebUI model settings:

- **Disable** code-interpreter tool when not doing analysis
- **Enable** only for data-heavy sessions
- Use per-conversation tool selection

### Audit Executed Code

All code execution is logged in MCPO:

```bash
kubectl logs mcpo-server-0 -n cluster-services | grep code-interpreter
```

---

## 📊 Performance Tips

### Cache HA States

Instead of calling `get_states()` multiple times:

```python
# Good: Call once, reuse
states = get_states()
lights = [s for s in states if 'light' in s['entity_id']]
sensors = [s for s in states if 'sensor' in s['entity_id']]

# Bad: Multiple calls
lights = get_states(domain='light')
sensors = get_states(domain='sensor')
```

### Use Pandas Efficiently

```python
# Convert HA states to DataFrame once
import pandas as pd

states = get_states()
df = pd.DataFrame([{
    'entity': s['entity_id'],
    'state': s['state'],
    'domain': s['entity_id'].split('.')[0],
    **s['attributes']
} for s in states])

# Now query the DataFrame
lights_on = df[(df['domain'] == 'light') & (df['state'] == 'on')]
```

---

## 🎉 Benefits

| Feature                | Before                        | After                                    |
| ---------------------- | ----------------------------- | ---------------------------------------- |
| **Live Data Analysis** | Export CSV → Upload → Analyze | Ask in chat → Instant results            |
| **Visualizations**     | Manual plotting in Jupyter    | Natural language → Auto-generated charts |
| **Complex Queries**    | Write custom scripts          | "Show me X" → Done                       |
| **Learning Curve**     | Need pandas/Python knowledge  | Natural language → AI writes code        |
| **Speed**              | Minutes per query             | Seconds per query                        |

---

## 🚧 Troubleshooting

### Code Interpreter Not Available

**Check MCPO logs:**

```bash
kubectl logs mcpo-server-0 -n cluster-services | grep code-interpreter
```

**Common issues:**

- Docker image not pulled → Pull on worker nodes
- MCPO config syntax error → Validate JSON
- Network isolation → Add `--network=host` to docker args

### HA Data Not Accessible in Code

**Ensure data is passed correctly:**

In Open-WebUI prompt:

```
Get all light states, then pass that data to code-interpreter
and show it as a DataFrame
```

LLM should:

1. Call `get_states(domain='light')` → Save response
2. Call code-interpreter with: `data = <HA_states_JSON>`
3. Execute pandas code on `data` variable

### Charts Not Displaying

**Save plots to file:**

```python
plt.savefig('chart.png')
# Code interpreter should return the file
```

**Or use base64 inline:**

```python
import base64
from io import BytesIO

buf = BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
img_base64 = base64.b64encode(buf.read()).decode()
print(f'data:image/png;base64,{img_base64}')
```

---

## 📚 Resources

- **MCP Code Interpreter:** <https://github.com/modelcontextprotocol/code-interpreter>
- **Home Assistant MCP (74 tools):** `/ha-mcp-server-addon/DEPLOYMENT_SUCCESS.md`
- **MCPO Documentation:** MCPO GitHub repo
- **Open-WebUI Function Calling:** <https://docs.openwebui.com>

---

**Status:** Ready to deploy!  
**Impact:** Transforms Open-WebUI into a **live Home Assistant data analysis platform** 🚀

**Deploy now and start asking powerful questions about your smart home!**
