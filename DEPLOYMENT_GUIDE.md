# Home Assistant OpenAPI Server - Deployment Guide

## 🎯 Critical Information: Correct File Locations

### ⚠️ IMPORTANT: Where to Upload server.py

The Home Assistant add-on reads `server.py` from the **runtime location**, NOT the add-on source directory!

```
❌ WRONG: /addons/local/ha-mcp-server/server.py    (source code only)
✅ CORRECT: /config/ha-mcp-server/server.py         (runtime location)
```

### Why Two Locations Exist

1. **`/addons/local/ha-mcp-server/`** - Add-on source code

   - Contains Dockerfile, run.sh, config.json
   - Used during Docker build
   - Changing files here requires rebuilding the add-on

2. **`/config/ha-mcp-server/`** - Runtime execution location
   - Server reads Python code from here at startup
   - Changes take effect immediately after restart
   - Persistent across add-on updates
   - **THIS IS WHERE YOU UPLOAD server.py!**

---

## 📋 Step-by-Step Deployment Process

### Method 1: Automated Deployment (Recommended)

```powershell
# From C:\MyProjects\ha-openapi-server-v3.0.0\
$password = "AgAGarib122628"  # Your SSH password
$sourceFile = "C:\MyProjects\ha-openapi-server-v3.0.0\v4.0.7\server.py"

# 1. Create runtime directory
echo y | plink -batch -pw $password root@192.168.1.203 "mkdir -p /config/ha-mcp-server"

# 2. Backup current version (optional but recommended)
echo y | plink -batch -pw $password root@192.168.1.203 "cp /config/ha-mcp-server/server.py /config/ha-mcp-server/server.py.backup.$(date +%Y%m%d_%H%M%S)"

# 3. Upload new server.py to CORRECT location
echo y | pscp -batch -pw $password $sourceFile root@192.168.1.203:/config/ha-mcp-server/server.py

# 4. Upload requirements.txt (if dependencies changed)
echo y | pscp -batch -pw $password requirements.txt root@192.168.1.203:/config/ha-mcp-server/requirements.txt

# 5. Verify upload
echo y | plink -batch -pw $password root@192.168.1.203 "head -5 /config/ha-mcp-server/server.py | grep Version"

# 6. Restart add-on
echo y | plink -batch -pw $password root@192.168.1.203 "ha addons restart local_ha-mcp-server"

# 7. Wait 35 seconds for startup
Start-Sleep -Seconds 35

# 8. Verify deployment
Invoke-RestMethod -Uri "http://192.168.1.203:8001/health"
```

### Method 2: Manual Deployment via HA File Editor

1. **Access File Editor**

   - Open Home Assistant: http://192.168.1.203:8123
   - Go to Settings → Add-ons → File Editor
   - Enable "Show in sidebar" if needed

2. **Navigate to Runtime Location**

   ```
   /config/ha-mcp-server/server.py
   ```

   - If directory doesn't exist, create it via Terminal add-on:
     ```bash
     mkdir -p /config/ha-mcp-server
     ```

3. **Upload/Paste New Code**

   - Open your local `v4.0.7/server.py`
   - Copy entire contents
   - Paste into `/config/ha-mcp-server/server.py`
   - Save file

4. **Restart Add-on**

   - Settings → Add-ons → local_ha-mcp-server
   - Click "Restart"
   - Wait ~30-40 seconds

5. **Verify Version**
   ```powershell
   Invoke-RestMethod -Uri "http://192.168.1.203:8001/health"
   ```

### Method 3: SSH Manual Upload

```bash
# SSH into Home Assistant
ssh root@192.168.1.203

# Create directory if needed
mkdir -p /config/ha-mcp-server

# Upload file (from local machine)
scp /path/to/server.py root@192.168.1.203:/config/ha-mcp-server/server.py

# Verify upload
head -5 /config/ha-mcp-server/server.py | grep Version

# Restart add-on
ha addons restart local_ha-mcp-server

# Check logs
ha addons logs local_ha-mcp-server
```

---

## 🔍 Verification Checklist

After deployment, verify these items:

### 1. File Location Check

```bash
ssh root@192.168.1.203
ls -lh /config/ha-mcp-server/server.py
# Should show recent timestamp and correct size
```

### 2. Version Check

```bash
head -5 /config/ha-mcp-server/server.py | grep Version
# Should show: Version: 4.0.7 (or your target version)
```

### 3. Add-on Running

```bash
ha addons info local_ha-mcp-server | grep state
# Should show: state: started
```

### 4. Health Endpoint

```powershell
$health = Invoke-RestMethod -Uri "http://192.168.1.203:8001/health"
$health.version  # Should match your deployed version
$health.status   # Should be "healthy"
```

### 5. Add-on Logs

```bash
ha addons logs local_ha-mcp-server | tail -20
# Should show no errors
# Should show correct version in startup message
```

---

## 🚨 Common Issues and Solutions

### Issue 1: "Still showing old version after restart"

**Cause:** Uploaded to wrong location (`/addons/local/` instead of `/config/`)

**Solution:**

```bash
# Upload to correct location
pscp server.py root@192.168.1.203:/config/ha-mcp-server/server.py

# Verify correct location
ssh root@192.168.1.203 "ls -lh /config/ha-mcp-server/server.py"

# Restart
ssh root@192.168.1.203 "ha addons restart local_ha-mcp-server"
```

### Issue 2: "Add-on won't start after update"

**Cause:** Syntax error or missing dependencies

**Solution:**

```bash
# Check logs for errors
ha addons logs local_ha-mcp-server

# Common fixes:
# 1. Restore backup
cp /config/ha-mcp-server/server.py.backup /config/ha-mcp-server/server.py

# 2. Install missing dependencies (if requirements.txt changed)
# Update /config/ha-mcp-server/requirements.txt
# Rebuild add-on to install new deps
```

### Issue 3: "Can't reach health endpoint"

**Cause:** Server not started or port misconfiguration

**Solution:**

```bash
# Check if add-on is running
ha addons info local_ha-mcp-server

# Check logs
ha addons logs local_ha-mcp-server

# Verify port (should be 8001)
cat /addons/local/ha-mcp-server/config.json | grep port
```

### Issue 4: "Permission denied when uploading"

**Cause:** SSH permissions or authentication issue

**Solution:**

```bash
# Use batch mode with password
echo y | pscp -batch -pw YOUR_PASSWORD server.py root@IP:/config/ha-mcp-server/server.py

# Or fix SSH permissions
ssh root@192.168.1.203
chmod 755 /config/ha-mcp-server
```

---

## 📦 Dependencies Management

### When requirements.txt Changes

If you've added new Python dependencies (e.g., `websockets>=12.0` in v4.0.7):

1. **Upload new requirements.txt**

   ```bash
   pscp requirements.txt root@192.168.1.203:/config/ha-mcp-server/requirements.txt
   ```

2. **Update add-on source** (for Docker rebuild)

   ```bash
   pscp requirements.txt root@192.168.1.203:/addons/local/ha-mcp-server/requirements.txt
   ```

3. **Rebuild add-on** (installs new dependencies)

   - Go to Settings → Add-ons → local_ha-mcp-server
   - Click three dots menu → "Rebuild"
   - Wait for build to complete (~2-5 minutes)
   - Start add-on

4. **Verify dependencies installed**
   ```bash
   ha addons logs local_ha-mcp-server | grep -i "successfully installed"
   ```

---

## 🎯 Quick Reference

### Key Paths on HA Server

| Path                                           | Purpose                         | Update Frequency |
| ---------------------------------------------- | ------------------------------- | ---------------- |
| `/config/ha-mcp-server/server.py`              | **Runtime code** (UPLOAD HERE!) | Every update     |
| `/config/ha-mcp-server/requirements.txt`       | Runtime dependencies            | When deps change |
| `/addons/local/ha-mcp-server/server.py`        | Source backup only              | Optional         |
| `/addons/local/ha-mcp-server/requirements.txt` | Build-time deps                 | When deps change |
| `/addons/local/ha-mcp-server/Dockerfile`       | Container build                 | Rarely           |
| `/addons/local/ha-mcp-server/run.sh`           | Startup script                  | Rarely           |
| `/addons/local/ha-mcp-server/config.json`      | Add-on config                   | Rarely           |

### Server Details

- **Server:** 192.168.1.203
- **SSH User:** root
- **Add-on Name:** local_ha-mcp-server
- **API Port:** 8001
- **Health Endpoint:** http://192.168.1.203:8001/health

### Essential Commands

```bash
# Quick deployment
pscp server.py root@192.168.1.203:/config/ha-mcp-server/server.py
ssh root@192.168.1.203 "ha addons restart local_ha-mcp-server"

# Quick verification
ssh root@192.168.1.203 "head -5 /config/ha-mcp-server/server.py | grep Version"
curl http://192.168.1.203:8001/health | jq .version

# Check logs
ssh root@192.168.1.203 "ha addons logs local_ha-mcp-server | tail -50"

# Backup before update
ssh root@192.168.1.203 "cp /config/ha-mcp-server/server.py /config/ha-mcp-server/server.py.backup.$(date +%Y%m%d)"
```

---

## 📝 Version History Example

Keep track of deployments:

```bash
# On HA server, maintain backups
/config/ha-mcp-server/
├── server.py                    # Current version
├── server.py.v4.0.7.backup     # v4.0.7 backup
├── server.py.v4.0.6.backup     # v4.0.6 backup (removed)
└── requirements.txt             # Current dependencies
```

---

## ✅ Success Criteria

After deployment, you should see:

```json
{
  "status": "healthy",
  "service": "homeassistant-openapi-server",
  "version": "4.0.7", // Your deployed version
  "endpoints": 95,
  "working": 95,
  "success_rate": "100%",
  "websocket": "enabled", // For v4.0.7+
  "timestamp": "2025-11-08T..."
}
```

Add-on logs should show:

```
[INFO] Starting Home Assistant OpenAPI Server v4.0.7
[INFO] Using persistent server.py from /config/ha-mcp-server/server.py
[INFO] Port: 8001
[INFO] Log Level: info
[INFO] Token available: YES
```

---

**Last Updated:** November 8, 2025  
**Current Version:** 4.0.7  
**Status:** Deployment successful, documenting process for future updates
