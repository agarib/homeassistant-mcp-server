# Explanation: Why You Got "name not defined" Errors

## 🎯 The Issue

You were trying to call `ha_read_file()`, `ha_write_file()`, etc. as if they were **Python functions**, but they're actually **REST API endpoints**.

---

## ❌ What You Were Trying (WRONG)

```python
# This doesn't work - these aren't Python functions!
result = ha_read_file(filepath="configuration.yaml")
content = ha_write_file(filepath="test.txt", content="data")
files = ha_list_directory(dirpath="packages")
```

**Error:** `NameError: name 'ha_read_file' is not defined`

**Why:** You're in a **code interpreter** environment. The `ha_*` tools are **HTTP REST API endpoints**, not importable Python functions.

---

## ✅ What You Should Do (CORRECT)

### Option 1: Use HTTP Requests in Code Interpreter

```python
import requests

# Read a file
response = requests.post(
    "http://192.168.1.203:8001/ha_read_file",
    json={"filepath": "configuration.yaml"}
)
print(response.json())

# Write a file
response = requests.post(
    "http://192.168.1.203:8001/ha_write_file",
    json={
        "filepath": "automations/new.yaml",
        "content": "automation:\n  - alias: Test\n..."
    }
)
print(response.json())

# List directory
response = requests.post(
    "http://192.168.1.203:8001/ha_list_directory",
    json={"dirpath": "packages"}
)
print(response.json())
```

### Option 2: Use in Open-WebUI (Recommended)

In **Open-WebUI**, these tools are available automatically:

- You don't need to write HTTP requests
- Just reference the tool name (e.g., "ha_read_file")
- Open-WebUI handles the HTTP communication for you

**Example in Open-WebUI:**

```
User: "Read my configuration.yaml file"
AI: [Uses ha_read_file tool automatically]
Open-WebUI: [Makes HTTP POST request behind the scenes]
AI: "Here's your configuration content..."
```

---

## 🔍 Understanding the Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Home Assistant OpenAPI Server (192.168.1.203:8001)        │
│  ---------------------------------------------------------- │
│  • 81 REST API endpoints (all with ha_ prefix)             │
│  • POST /ha_read_file                                      │
│  • POST /ha_write_file                                     │
│  • POST /ha_control_light                                  │
│  • POST /ha_create_automation                              │
│  • etc.                                                    │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │ HTTP POST requests
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼─────┐  ┌────────▼─────────┐
│  Open-WebUI  │  │ Code         │  │ Direct HTTP      │
│              │  │ Interpreter  │  │ (curl/Postman)   │
│ Tools: Auto  │  │ Tools: None  │  │ Tools: None      │
│ Available!   │  │ Must use     │  │ Must use         │
│              │  │ requests lib │  │ HTTP client      │
└──────────────┘  └──────────────┘  └──────────────────┘
```

---

## 🎯 Summary

**The Confusion:**

- You thought `ha_read_file` was a Python function you could call
- But it's actually an HTTP REST endpoint at `http://192.168.1.203:8001/ha_read_file`

**The Solution:**

- **In code interpreter:** Use `requests.post()` to make HTTP calls
- **In Open-WebUI:** Tools available automatically (no HTTP needed)
- **In Claude Desktop with MCP:** Tools available via MCP protocol

**The Key Insight:**

- ✅ `ha_` prefix = Home Assistant tools (full /config access)
- ❌ `tool_` prefix = Open-WebUI tools (restricted to /workspace)
- 🌐 All `ha_*` tools are **HTTP REST endpoints**, not Python functions

---

## 📚 Updated Documentation

The `AI_TRAINING_EXAMPLES.md` file has been updated with:

1. ✅ Clear explanation that these are REST API endpoints
2. ✅ How to use tools in different environments
3. ✅ Why "name not defined" error occurs
4. ✅ Correct code examples for each environment
5. ✅ Troubleshooting section for common errors

---

## 🚀 Next Steps

**If you're in Open-WebUI:**

- Configure the Home Assistant OpenAPI server URL
- Tools will appear automatically
- Use them by name (e.g., "use ha_read_file to read configuration.yaml")

**If you're in code interpreter:**

- Use the `requests` library examples above
- Make HTTP POST requests to the endpoints
- Server is at `http://192.168.1.203:8001`

**If you're testing with curl:**

```bash
curl -X POST http://192.168.1.203:8001/ha_read_file \
  -H "Content-Type: application/json" \
  -d '{"filepath": "configuration.yaml"}'
```

---

**Bottom Line:** These are web API endpoints, not Python functions. Access them via HTTP requests (or let Open-WebUI do it for you automatically).
