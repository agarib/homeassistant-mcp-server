# v4.0.5 Research - Diagnostics API Investigation

**Date:** November 2, 2025  
**Researcher:** GitHub Copilot + User (agarib)  
**Goal:** Understand HA Diagnostics API to implement reliable diagnostic tools

## 🎯 Research Objectives

1. Map all available diagnostics endpoints
2. Understand authentication requirements
3. Document request/response formats
4. Identify data redaction patterns
5. Test with real integrations (LG ThinQ, etc.)

---

## 📋 API Endpoints to Test

### Known Endpoints (from HA docs)

```bash
# 1. Download config entry diagnostics
GET /api/diagnostics/config_entry/{entry_id}
Authorization: Bearer {token}

# 2. Download device diagnostics
GET /api/diagnostics/device/{device_id}
Authorization: Bearer {token}
```

### Unknown - Need to Discover

```bash
# 3. List available diagnostics? (TBD)
GET /api/diagnostics
GET /api/config/config_entries
GET /api/config/device_registry

# 4. Filter by integration? (TBD)
GET /api/diagnostics?integration=lg_thinq
```

---

## 🔬 Test Plan

### Test 1: Config Entry Diagnostics

**Objective:** Download config entry diagnostics for LG ThinQ

**Steps:**

1. Get list of config entries: `GET /api/config/config_entries`
2. Find LG ThinQ entry ID
3. Request diagnostics: `GET /api/diagnostics/config_entry/{entry_id}`
4. Analyze response structure
5. Document redacted fields

**Expected Response:**

```json
{
  "entry_data": {
    "username": "***REDACTED***",
    "country": "NZ",
    "language": "en-US"
  },
  "runtime_data": {
    "devices": [...],
    "api_version": "2.0"
  }
}
```

### Test 2: Device Diagnostics

**Objective:** Download device diagnostics for washing machine

**Steps:**

1. Get list of devices: `GET /api/config/device_registry/list`
2. Find washing machine device ID
3. Request diagnostics: `GET /api/diagnostics/device/{device_id}`
4. Analyze response structure
5. Compare with config entry diagnostics

**Expected Response:**

```json
{
  "device_info": {
    "model": "WM-123",
    "firmware": "v1.2.3"
  },
  "details": {
    "raw_data": {...},
    "redacted_fields": [...]
  }
}
```

### Test 3: Integration Without Diagnostics

**Objective:** Test graceful handling when integration doesn't support diagnostics

**Steps:**

1. Find integration without diagnostics support
2. Request config entry diagnostics
3. Request device diagnostics
4. Document error responses

**Expected Behavior:**

- 404 Not Found?
- 501 Not Implemented?
- Fallback to config entry diagnostics?

### Test 4: Authentication Requirements

**Objective:** Determine if admin token is required

**Steps:**

1. Test with SUPERVISOR_TOKEN (default add-on token)
2. Test with admin long-lived token
3. Document which works for which endpoints

**Questions to Answer:**

- Can SUPERVISOR_TOKEN download diagnostics?
- Is admin token required?
- Are there permission scopes?

---

## 🧪 Test Scripts

### Script 1: Explore Config Entries

```powershell
# Get all config entries
$response = Invoke-RestMethod -Uri "http://192.168.1.203:8123/api/config/config_entries" -Headers @{Authorization="Bearer YOUR_TOKEN"}

# Filter for LG ThinQ
$lg_entry = $response | Where-Object { $_.domain -eq "lg_thinq" }

Write-Output "LG ThinQ Entry ID: $($lg_entry.entry_id)"
Write-Output "LG ThinQ Title: $($lg_entry.title)"
```

### Script 2: Download Config Entry Diagnostics

```powershell
# Replace with actual entry_id from Script 1
$entry_id = "abc123..."

try {
    $diagnostics = Invoke-RestMethod `
        -Uri "http://192.168.1.203:8123/api/diagnostics/config_entry/$entry_id" `
        -Headers @{Authorization="Bearer YOUR_TOKEN"}

    $diagnostics | ConvertTo-Json -Depth 10
} catch {
    Write-Output "Error: $($_.Exception.Message)"
    Write-Output "Status Code: $($_.Exception.Response.StatusCode.Value__)"
}
```

### Script 3: Download Device Diagnostics

```powershell
# Replace with actual device_id
$device_id = "device_xyz..."

try {
    $diagnostics = Invoke-RestMethod `
        -Uri "http://192.168.1.203:8123/api/diagnostics/device/$device_id" `
        -Headers @{Authorization="Bearer YOUR_TOKEN"}

    $diagnostics | ConvertTo-Json -Depth 10
} catch {
    Write-Output "Error: $($_.Exception.Message)"
}
```

### Script 4: List All Devices

```powershell
# Get device registry
$devices = Invoke-RestMethod `
    -Uri "http://192.168.1.203:8123/api/config/device_registry/list" `
    -Headers @{Authorization="Bearer YOUR_TOKEN"}

# Filter for LG devices
$lg_devices = $devices | Where-Object { $_.manufacturer -like "*LG*" }

$lg_devices | Select-Object id, name, model, manufacturer | Format-Table
```

---

## 📊 Data Collection Template

### Endpoint: `/api/diagnostics/config_entry/{entry_id}`

- **Method:** GET / POST
- **Auth Required:** Yes / No
- **Token Type:** SUPERVISOR / ADMIN / BOTH
- **Response Format:** JSON
- **Status Codes:**
  - 200: Success
  - 401: Unauthorized
  - 404: Not Found
  - Other: \_\_\_

**Sample Response:**

```json
{
  // Paste actual response here
}
```

**Redacted Fields:**

- Field 1: `api_key`
- Field 2: `username`
- Field 3: \_\_\_

**Notes:**

- ***

---

### Endpoint: `/api/diagnostics/device/{device_id}`

- **Method:** \_\_\_
- **Auth Required:** \_\_\_
- **Token Type:** \_\_\_
- **Response Format:** \_\_\_
- **Status Codes:** \_\_\_

**Sample Response:**

```json
{
  // Paste actual response here
}
```

---

## 🎯 Research Questions

### High Priority

- [ ] What is the exact URL format for diagnostics endpoints?
- [ ] Do diagnostics require admin token or does SUPERVISOR_TOKEN work?
- [ ] What happens when integration doesn't support diagnostics?
- [ ] Is there a way to list all available diagnostics?
- [ ] What fields are commonly redacted?

### Medium Priority

- [ ] Can we filter diagnostics by integration?
- [ ] Is there a download vs view mode?
- [ ] Are diagnostics cached or generated on-demand?
- [ ] What's the size limit for diagnostics?
- [ ] Can diagnostics include file attachments?

### Low Priority

- [ ] Are diagnostics versioned?
- [ ] Can we trigger diagnostic generation?
- [ ] Is there diagnostic history?
- [ ] Can we customize redaction?

---

## 📝 Research Log

### Session 1: [Date]

**What we tested:**

- ***

**What we learned:**

- ***

**Blockers:**

- ***

**Next steps:**

- ***

---

### Session 2: [Date]

**What we tested:**

- ***

**What we learned:**

- ***

---

## 🎓 Findings Summary

### ✅ Confirmed

- ***
- ***

### ❌ Doesn't Work

- ***
- ***

### 🤔 Uncertain

- ***
- ***

---

## 🚀 Implementation Recommendations

Based on research findings:

### Tool 1: `ha_get_config_entry_diagnostics`

```python
@app.post("/ha_get_config_entry_diagnostics")
async def ha_get_config_entry_diagnostics(request: ConfigEntryDiagnosticsRequest):
    """
    Download diagnostics for a config entry.

    Helps troubleshoot integration issues by providing:
    - Redacted entry data (no sensitive info)
    - Runtime data
    - Integration-specific details
    """
    # Implementation based on research findings
    pass
```

### Tool 2: `ha_get_device_diagnostics`

```python
@app.post("/ha_get_device_diagnostics")
async def ha_get_device_diagnostics(request: DeviceDiagnosticsRequest):
    """
    Download diagnostics for a specific device.

    Provides device-specific troubleshooting data.
    Falls back to config entry diagnostics if device diagnostics not supported.
    """
    # Implementation based on research findings
    pass
```

### Tool 3: `ha_list_available_diagnostics`

```python
@app.post("/ha_list_available_diagnostics")
async def ha_list_available_diagnostics(request: Optional[ListDiagnosticsRequest]):
    """
    List all available diagnostics.

    Optionally filter by integration.
    Returns config entries and devices that support diagnostics.
    """
    # Implementation based on research findings
    pass
```

---

## 📚 References

- **HA Diagnostics Docs:** <https://developers.home-assistant.io/docs/core/integration_diagnostics/>
- **HA REST API:** <https://developers.home-assistant.io/docs/api/rest/>
- **Config Entries API:** <https://developers.home-assistant.io/docs/api/rest/#get-apiconfig_entries>
- **Device Registry API:** (TBD - need to find documentation)

---

**Next Steps:**

1. Run test scripts to gather real data
2. Document findings in Research Log
3. Update Implementation Recommendations
4. Design final Pydantic models
5. Implement tools in v4.0.5

**Let's discover how HA diagnostics really work! 🔬**
