# 🎯 Permission Issue - ROOT CAUSE IDENTIFIED

**Date:** November 2, 2025  
**Status:** ✅ ROOT CAUSE FOUND

---

## 🔍 The Real Problem

**Error Message:**

```
Access denied - path outside allowed directories:
/config/packages/kitchen/washing_machine.yaml not in
/workspace, /workspace/ai-workspace, /usb-storage
```

**ROOT CAUSE:** Open-WebUI is calling **its own built-in file tools**, NOT your HA server's tools!

---

## 📊 Evidence

**Your HA Server (http://192.168.1.203:8001) Has:**

- ✅ `/write_file` → Full /config access
- ✅ `/read_file` → Full /config access
- ✅ `/copy_file` → Full /config access
- ✅ `/move_file` → Full /config access
- ✅ `/delete_file` → Full /config access
- ✅ `/search_files` → Full /config access

**Open-WebUI Has Built-in Tools:**

- ❌ `tool_write_file` → Restricted to /workspace paths only
- ❌ `tool_read_file` → Restricted to /workspace paths only
- ❌ `tool_get_file_info` → Restricted to /workspace paths only

**The error message mentions `/workspace` paths** = Open-WebUI's built-in tools, NOT your HA server!

---

## 💡 Why This Happens

When you ask Open-WebUI AI to "write a file," it sees TWO sets of tools:

1. **Open-WebUI's built-in file tools** (restricted to /workspace)
2. **Your HA server's file tools** (full /config access)

The AI is choosing the **wrong tools** (Open-WebUI's built-in ones).

---

## 🔧 Solutions

### Solution 1: Rename Your Tools (Recommended)

Add `ha_` prefix to all file tools to make them unique and preferred:

**In server.py, change:**

```python
@app.post("/write_file", tags=["file_operations"])
async def write_file(request: FileWriteRequest):
```

**To:**

```python
@app.post("/ha_write_file", tags=["file_operations"])
async def ha_write_file(request: FileWriteRequest):
```

**Apply to all 9 file operations:**

- `/write_file` → `/ha_write_file`
- `/read_file` → `/ha_read_file`
- `/list_directory` → `/ha_list_directory`
- `/delete_file` → `/ha_delete_file`
- `/copy_file` → `/ha_copy_file`
- `/move_file` → `/ha_move_file`
- `/search_files` → `/ha_search_files`
- `/create_directory` → `/ha_create_directory`
- `/get_directory_tree` → `/ha_get_directory_tree`

**Benefits:**

- ✅ No tool name collision
- ✅ Clear which tools are for HA
- ✅ AI will prefer specialized tools over generic ones
- ✅ Your tools work alongside Open-WebUI's tools

---

### Solution 2: Disable Open-WebUI Built-in File Tools

If Open-WebUI allows disabling built-in tools, disable the file operation tools:

**In Open-WebUI Admin:**

1. Go to Settings → Tools
2. Find built-in file tools
3. Disable: `tool_write_file`, `tool_read_file`, `tool_get_file_info`

**Benefits:**

- ✅ Forces use of your HA tools
- ✅ No name changes needed

**Risks:**

- ❌ May break other Open-WebUI features that rely on file tools
- ❌ May not be possible if tools are hardcoded

---

### Solution 3: Explicit Tool Instructions in System Prompt

Add instructions to Open-WebUI system prompt:

```
When working with Home Assistant configuration files:
- ALWAYS use ha_write_file, ha_read_file, etc. from the HA server
- NEVER use built-in file tools (tool_write_file, tool_read_file)
- HA tools have full access to /config directory
```

**Benefits:**

- ✅ Quick fix
- ✅ No code changes

**Risks:**

- ❌ Relies on AI following instructions
- ❌ May still choose wrong tools sometimes

---

### Solution 4: Add Tool Descriptions to Prefer HA Tools

Update your HA tool descriptions to make them more appealing:

```python
@app.post("/write_file",
    summary="Write file to Home Assistant /config (PREFERRED for HA files)",
    description="Write content to any file in /config directory. Use this for Home Assistant configuration, automations, packages, etc. Full /config access.",
    tags=["file_operations"]
)
```

**Benefits:**

- ✅ Makes HA tools more specific
- ✅ AI more likely to choose them
- ✅ Better documentation

---

## 🎯 Recommended Fix (Multi-layered)

**Combine Solutions 1 + 4 + 3:**

1. **Rename tools** with `ha_` prefix (Solution 1)
2. **Enhance descriptions** to emphasize HA use case (Solution 4)
3. **Add system prompt** instruction (Solution 3)

This provides defense-in-depth:

- Unique names prevent collision
- Better descriptions guide AI choice
- System prompt provides fallback guidance

---

## 🚀 Implementation Plan

### Step 1: Update server.py (9 endpoints)

```python
# File Operations - Full /config access
@app.post("/ha_write_file",
    summary="Write file to Home Assistant /config directory",
    description="Write content to Home Assistant configuration files. Full access to /config directory including automations, packages, scripts, etc.",
    tags=["file_operations"]
)
async def ha_write_file(request: FileWriteRequest):
    """Write content to a file in /config directory"""
    try:
        result = await file_mgr.write_file(request.filepath, request.content)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Similar updates for:
# ha_read_file, ha_list_directory, ha_delete_file
# ha_copy_file, ha_move_file, ha_search_files
# ha_create_directory, ha_get_directory_tree
```

### Step 2: Update Pydantic Models

```python
class FileWriteRequest(BaseModel):
    filepath: str = Field(..., description="Path relative to /config (e.g., 'packages/kitchen/washing_machine.yaml')")
    content: str = Field(..., description="File content to write")
```

### Step 3: Test Locally

```powershell
# Test renamed endpoint
$body = @{
    filepath = "packages/kitchen/test.yaml"
    content = "test: content"
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://192.168.1.203:8001/ha_write_file' `
    -Method Post -Body $body -ContentType 'application/json'
```

### Step 4: Deploy to HA Add-on

```bash
# Copy updated server.py to HA
scp server.py root@192.168.1.203:/config/ha-mcp-server/server.py

# Restart add-on
ssh root@192.168.1.203 "ha addons restart local_ha-mcp-server"
```

### Step 5: Update Open-WebUI System Prompt

```
For Home Assistant file operations, use ha_write_file, ha_read_file, etc.
These tools have full access to /config directory.
```

### Step 6: Test in Open-WebUI

Ask AI:

```
Write a test file to /config/test.txt with content "Hello World" using the Home Assistant tools
```

Verify it calls `ha_write_file` instead of `tool_write_file`.

---

## ✅ Success Criteria

After fix:

- ✅ Open-WebUI calls `/ha_write_file` (not `tool_write_file`)
- ✅ No "Access denied" errors
- ✅ Files written successfully to /config
- ✅ Can create washing machine automation in /config/packages/kitchen/
- ✅ All 85 HA tools accessible with full permissions

---

## 📝 Files to Update

1. **server.py** - Rename 9 file operation endpoints + enhance descriptions
2. **Open-WebUI system prompt** - Add HA tool preference instruction
3. **CHANGELOG.md** - Document v4.0.3 with tool renaming

---

**Next Action:** Rename file operation tools with `ha_` prefix and deploy to production.
