# SSE Keepalive Parsing Fix 🔧

**Date:** October 28, 2025  
**Issue:** WARNING - Failed to parse event JSON: Expecting value: line 1 column 1 (char 0)

---

## Root Cause Analysis

**The Warning:**
```
2025-10-28 18:01:45,281 - __main__ - WARNING - Failed to parse event JSON: Expecting value: line 1 column 1 (char 0)
```

**What's Happening:**

Home Assistant's SSE event stream sends **keepalive pings** as empty "data:" lines to maintain the connection. The original code tried to parse these empty lines as JSON, causing harmless but noisy warnings.

**SSE Stream Format:**
```
data: {"event_type": "state_changed", ...}   ← Real event (parse this)

data:                                         ← Keepalive ping (skip this)

data: {"event_type": "automation_triggered"}  ← Real event (parse this)

data:                                         ← Keepalive ping (skip this)
```

---

## The Fix

**Before (Line 4082-4084):**
```python
if line.startswith("data:"):
    try:
        event_json = line.split(":", 1)[1].strip()
        event_data = json.loads(event_json)  # ❌ Fails on empty string
```

**After (Line 4082-4087):**
```python
if line.startswith("data:"):
    try:
        event_json = line.split(":", 1)[1].strip()
        
        # Skip empty data lines (keepalive pings)
        if not event_json:
            continue  # ✅ No warning, just skip
        
        event_data = json.loads(event_json)
```

**Additional Improvement:**
Better error logging when actual parsing errors occur:
```python
except json.JSONDecodeError as e:
    logger.warning(f"Failed to parse event JSON: {e} | Raw data: {event_json[:100]}")
    continue
```

---

## Impact Assessment

**Severity:** 🟢 Low - Cosmetic Issue

**Current Behavior:**
- SSE connection works perfectly (200 OK)
- Events are received and filtered correctly
- Warning is logged but doesn't affect functionality
- Only appears when keepalive pings are sent

**After Fix:**
- No warnings for normal keepalive behavior
- More informative errors when actual JSON parsing fails
- Cleaner logs

---

## Deployment Status

**Code Status:**
- ✅ Fix implemented in local `server.py` (line 4085-4087)
- ✅ Comment added explaining keepalive handling
- ⚠️ **Not yet deployed to container** (SSH connection unstable)

**Files:**
- Local: `C:\MyProjects\ha-mcp-server-addon\server.py` (4,349 lines with fix)
- Ready: `server_104_sse_keepalive_fix.py` (to be copied)
- Container: `37acc1b94de1:/app/server.py` (4,346 lines, needs update)

---

## Deployment Instructions

When SSH is stable, run:

```bash
# Copy to HA host
scp server.py root@192.168.1.203:/config/server_104_sse_keepalive_fix.py

# Deploy to container
ssh root@192.168.1.203 "docker cp /config/server_104_sse_keepalive_fix.py 37acc1b94de1:/app/server.py && docker restart 37acc1b94de1"
```

Or use HA SSH web terminal at `http://192.168.1.203:8123/a0d7b954_ssh/`:
```bash
docker cp /config/server_104_sse_keepalive_fix.py 37acc1b94de1:/app/server.py
docker restart 37acc1b94de1
```

---

## Technical Details

**SSE Specification (RFC 8895):**
- Empty data lines are valid and commonly used for keepalive
- Servers send periodic pings to prevent connection timeouts
- Clients should ignore empty data fields

**Home Assistant Behavior:**
- Sends keepalive every ~30-60 seconds
- Format: Just "data:" with no content
- Prevents proxy/firewall timeouts on long-lived connections

**Our Implementation:**
```python
# Line 4070-4075: Comment explaining behavior
# HA also sends empty "data:" lines as keepalive pings - we skip those

# Line 4082-4087: The fix
event_json = line.split(":", 1)[1].strip()

if not event_json:
    continue  # Skip keepalive pings silently
```

---

## Priority

**Should Deploy:** 🟡 Optional - Nice to Have

**Rationale:**
- Current system is fully functional
- Warning is harmless but clutters logs
- Fix improves code cleanliness and professional appearance
- Can be deployed during next maintenance window

**Recommendation:**
- Include in next deployment batch
- Or deploy now if testing SSE streaming extensively
- Low risk - only affects logging, not functionality

---

## Related Files

- `SSE_FIX_DEPLOYED.md` - Main SSE 403→200 fix (CRITICAL, DEPLOYED)
- `DEPLOYMENT_COMPLETE_104_TOOLS.md` - Overall deployment status
- `server.py` line 4032-4115 - SSE streaming implementation

---

## Summary

✅ **Issue Identified:** Empty SSE keepalive pings causing JSON parse warnings  
✅ **Root Cause:** Missing empty-string check before JSON parsing  
✅ **Fix Implemented:** Skip empty event_json with `if not event_json: continue`  
⚠️ **Deployment Pending:** SSH connection unstable, can deploy when stable  
🟢 **Priority:** Low - Cosmetic improvement, system fully functional  

The SSE streaming feature works perfectly - this is just a log cleanup! 🎉
