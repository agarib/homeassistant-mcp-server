# Deployment Guide - v4.0.29

This guide outlines the steps to upgrade the running Home Assistant OpenAPI Server from v4.0.28 to the new modular v4.0.29.

**Target**: `\\192.168.1.203\config\addons\local\ha-openapi-server`
**Version**: v4.0.29

## 📋 Pre-Deployment Check
1.  **Backup**: Ensure you have a backup of the current `ha-openapi-server` folder.
2.  **Access**: Verify SMB access to `\\192.168.1.203\config`.

## 🚀 Deployment Steps

### 1. Stop the Addon
Run this via SSH or HA Terminal:
```bash
ha addons stop local_ha_openapi_server
```

### 2. File Replacement
Navigate to `\\192.168.1.203\config\addons\local\ha-openapi-server` via your file explorer.

1.  **Delete** (or rename to `.bak`) the old `server.py`.
2.  **Copy** the entire contents of the `v4.0.29` folder to this location.
    - You should see the `app/` folder, `CHANGELOG.md`, `README.md`, `requirements.txt`, and the new `server.py` shim.

### 3. Verify Structure
The remote folder should look like this:
```
ha-openapi-server/
├── app/
│   ├── main.py
│   ├── core/
│   ├── models/
│   └── routers/
├── server.py       # New shim file
├── requirements.txt
├── CHANGELOG.md
├── README.md
├── README_AI.md
└── config.json     # (Existing addon config, distinct from app config)
```

### 4. Restart Addon
Run via SSH or HA Terminal:
```bash
# Rebuild to ensure new requirements are installed if needed (though we use same packages mostly)
ha addons rebuild local_ha_openapi_server

# Start the addon
ha addons start local_ha_openapi_server
```

## ✅ Verification
1.  **Check Logs**:
    ```bash
    ha addons logs local_ha_openapi_server
    ```
    Look for: `🚀 Starting Home Assistant OpenAPI Server v4.0.29 (Modular)`

2.  **Health Check**:
    ```powershell
    Invoke-RestMethod http://192.168.1.203:8001/health | ConvertTo-Json
    ```
    Should return: `"version": "4.0.29"`

3.  **Test Endpoint**:
    ```powershell
    Invoke-RestMethod http://192.168.1.203:8001/ha_list_devices | ConvertTo-Json
    ```

## 📝 Changes Overview
- **Refactored Codebase**: `server.py` is now a small shim. Logic lives in `app/`.
- **New Features**: Check `CHANGELOG.md` for full details.
- **AI Guide**: See `README_AI.md` for AI usage patterns.
