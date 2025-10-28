# ✅ Code Execution Tools - Testing Guide

## 🎉 Deployment Complete

**Status:** All 77 tools now available (74 original + 3 new code execution tools)

- ✅ `server.py` updated with code execution tools
- ✅ `requirements.txt` updated (pandas, matplotlib, numpy, seaborn)
- ✅ Files deployed to HA add-on
- ✅ Add-on restarted and healthy
- ✅ MCPO connected

---

## 🔬 New Tools Available

### 1. `execute_python`

**Execute arbitrary Python code with pandas/matplotlib/numpy**

**Use for:**

- Custom data analysis
- Complex calculations
- Data transformations

### 2. `analyze_states_dataframe`

**Get HA entity states as a pandas DataFrame**

**Use for:**

- Quick data exploration
- Filtering and grouping entities
- Statistical analysis

### 3. `plot_sensor_history`

**Create time-series charts from sensor data**

**Use for:**

- Temperature trends
- Power consumption over time
- Any sensor visualization

---

## 🧪 Test Prompts for Open-WebUI

### Test 1: Basic Code Execution

```
Execute this Python code: print(sum([1, 2, 3, 4, 5]))
```

**Expected Result:** `15`

---

### Test 2: Get States as DataFrame

```
Get all light entities as a pandas DataFrame and show me the first 5 rows
```

**Expected:** Table with columns like `entity_id`, `state`, `brightness`, etc.

---

### Test 3: Simple Analysis

```
Get all temperature sensors and calculate the average temperature
```

**Behind the scenes:**

1. Calls `analyze_states_dataframe(domain='sensor', query="entity_id.str.contains('temp')")`
2. Calls `execute_python(code="df['state'].astype(float).mean()")`

**Expected:** e.g., "Average temperature: 21.5°C"

---

### Test 4: Visualization

```
Plot the temperature sensor history for the past 6 hours
```

**Behind the scenes:**

1. Calls `plot_sensor_history(entity_ids=['sensor.temperature'], hours=6)`

**Expected:** Line chart image showing temperature trend

---

### Test 5: Power Analysis

```
Show me all devices with 'power' in their name, their current power
consumption, and sort by highest to lowest
```

**Behind the scenes:**

1. `analyze_states_dataframe(domain='sensor', query="entity_id.str.contains('power')")`
2. `execute_python(code="""
df['power'] = df['state'].astype(float)
df[['entity_id', 'power']].sort_values('power', ascending=False)
""")`

**Expected:** Sorted table of power consumption

---

### Test 6: Room-Based Grouping

```
Get all lights, group them by room (from attributes), and show me
how many lights are on in each room
```

**Behind the scenes:**

```python
# Via analyze_states_dataframe + execute_python
df_lights = analyze_states_dataframe(domain='light')
df_on = df_lights[df_lights['state'] == 'on']
df_on.groupby('room').size()
```

**Expected:**

```
Room          Count
Living Room   3
Kitchen       2
Bedroom       1
```

---

### Test 7: Complex Visualization

```
Create a bar chart showing average brightness of lights by room
```

**Behind the scenes:**

```python
import matplotlib.pyplot as plt
import pandas as pd

df = analyze_states_dataframe(domain='light')
df_on = df[df['state'] == 'on']
df_on['brightness'] = df_on['brightness'].astype(float)

room_avg = df_on.groupby('room')['brightness'].mean()

plt.figure(figsize=(10, 6))
room_avg.plot(kind='bar')
plt.title('Average Brightness by Room')
plt.ylabel('Brightness (0-255)')
plt.xlabel('Room')
plt.tight_layout()
plt.savefig('brightness_by_room.png')
```

**Expected:** Bar chart image

---

### Test 8: Sensor Health Check

```
Check all sensors and show me which ones haven't updated
in the past hour
```

**Behind the scenes:**

```python
from datetime import datetime, timedelta
import pandas as pd

df = analyze_states_dataframe(domain='sensor')
df['last_changed'] = pd.to_datetime(df['last_changed'])

now = datetime.now(tz=df['last_changed'].iloc[0].tz)
one_hour_ago = now - timedelta(hours=1)

stale = df[df['last_changed'] < one_hour_ago]
stale[['entity_id', 'state', 'last_changed']].sort_values('last_changed')
```

**Expected:** List of stale sensors with timestamps

---

### Test 9: Multi-Sensor Comparison

```
Plot temperature, humidity, and pressure sensors on the same
chart for the past 12 hours
```

**Behind the scenes:**

```python
plot_sensor_history(
    entity_ids=[
        'sensor.temperature',
        'sensor.humidity',
        'sensor.pressure'
    ],
    hours=12,
    chart_type='line'
)
```

**Expected:** Multi-line chart with 3 series

---

### Test 10: Energy Cost Calculation

```
Get all power sensors, calculate total power consumption,
and estimate daily cost at $0.15 per kWh
```

**Behind the scenes:**

```python
df = analyze_states_dataframe(domain='sensor', query="entity_id.str.contains('power')")
df['power_w'] = df['state'].astype(float)

total_power_w = df['power_w'].sum()
daily_kwh = (total_power_w / 1000) * 24  # Convert W to kWh over 24h
daily_cost = daily_kwh * 0.15

print(f"Total Power: {total_power_w:.2f}W")
print(f"Daily Consumption: {daily_kwh:.2f} kWh")
print(f"Daily Cost: ${daily_cost:.2f}")
```

**Expected:**

```
Total Power: 458.3W
Daily Consumption: 11.0 kWh
Daily Cost: $1.65
```

---

## 🎯 Advanced Use Cases

### Correlation Analysis

```
Analyze the correlation between indoor temperature and
outdoor temperature over the past week
```

### Anomaly Detection

```
Get power consumption data for all devices and flag any
that are using more than 2 standard deviations above their mean
```

### Predictive Insights

```
Based on the past 7 days of temperature data, predict when
heating will be needed (when temp drops below 18°C)
```

### Custom Dashboards

```
Create a summary dashboard showing:
- Total lights on
- Average temperature
- Total power consumption
- Number of motion sensors triggered in past hour
```

---

## 🔍 How to Use in Open-WebUI

### Method 1: Natural Language (Recommended)

Just ask questions naturally:

- "Show me all lights"
- "Plot temperature for today"
- "Which sensors are offline?"

The LLM will automatically:

1. Choose the right tool(s)
2. Make the API calls
3. Process the data
4. Return results

### Method 2: Explicit Tool Calls

Be specific about which tool to use:

- "Use analyze_states_dataframe to get all lights"
- "Use execute_python to calculate average temperature"
- "Use plot_sensor_history for living room temp"

---

## 📊 What You Can Now Do

✅ **Instant State Data** - Get any entity state as structured data  
✅ **Pandas Analysis** - Filter, group, aggregate, transform  
✅ **Matplotlib Plots** - Time series, bar charts, scatter plots  
✅ **Custom Python** - Run any analysis code you can imagine  
✅ **Real-time Insights** - All data is live from Home Assistant  
✅ **No Manual Exports** - No need to download CSVs or logs

---

## 🚀 Next Steps

1. **Open <http://192.168.1.11:30080>** (Open-WebUI)
2. **Start a new chat**
3. **Try Test Prompt #1** (basic code execution)
4. **Try Test Prompt #2** (get states as DataFrame)
5. **Try Test Prompt #3** (simple analysis)
6. **Get creative!** Ask complex questions about your smart home

---

## 🎓 Tips for Best Results

### Be Specific

❌ "Show me data"  
✅ "Show me all light entities with their current state and brightness"

### Chain Operations

❌ Single complex request  
✅ "First get all sensors, then filter for temperature, then calculate average"

### Request Visualizations

✅ "...and show as a chart"  
✅ "...and create a bar graph"  
✅ "...and plot over time"

### Use Domain Filters

✅ "Get all lights" → faster than "get all entities"  
✅ "Get temperature sensors" → more targeted results

---

## 🔥 Real-World Examples

### Morning Energy Report

```
Give me a morning report:
1. Total lights left on overnight
2. Current power consumption
3. Temperature in each room
4. Any sensors that are offline
```

### Weekly Climate Analysis

```
Analyze temperature and humidity trends for the past week.
Show me:
- Average daily temperature
- Peak humidity times
- Correlation between temp and humidity
- A chart showing both over time
```

### Device Health Dashboard

```
Create a health dashboard showing:
- How many devices are online vs offline
- Which sensors are stale (no update in 6 hours)
- Battery levels for battery-powered devices
- A summary chart of device health
```

---

## ✅ Success

You now have **77 tools** at your disposal:

- **74 Home Assistant control tools** (discovery, automation, dashboards, etc.)
- **3 Code execution tools** (analyze, execute, plot)

**All accessible in natural language via Open-WebUI!** 🎉

Start chatting and explore your smart home data like never before! 🚀

---

**Next Phase:** When this is working well, we'll add **Option 2** (separate MCP code-interpreter server) for even more advanced capabilities like:

- Jupyter notebook integration
- Persistent analysis sessions
- Multi-step workflows
- Complex ML/AI models

But for now, you have everything you need for powerful live data analysis! 💪
