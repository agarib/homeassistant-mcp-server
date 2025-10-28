# 🔍 DIAGNOSIS: Why New Endpoints Return 404

## Problem

✅ server.py deployed (4,346 lines, confirmed via `wc -l`)
✅ Routes defined in code (lines 4322-4327)
✅ Add-on rebuilt
✅ Add-on restarted
✅ Health endpoint works

❌ New REST endpoints return 404:

- `/api/actions` → 404
- `/api/state` → 404
- `/subscribe_events` → 404

## Root Cause

**Docker Build Cache**

When you rebuild a Home Assistant add-on that has `build: true`, it uses Docker to build an image from the Dockerfile. Docker aggressively caches layers to speed up builds.

The Dockerfile has:

```dockerfile
COPY server.py .
```

If Docker thinks `server.py` hasn't changed (based on file timestamps or checksums), it uses the CACHED layer instead of copying the new file.

**This means:**

- New `server.py` exists in `/config/addons/local/ha-mcp-server/`
- But the Docker image contains the OLD `server.py` from cache
- The running container is using the old code

## Solution Options

### Option 1: Force Docker Rebuild (No Cache) ⭐ RECOMMENDED

**Via SSH:**

```bash
ssh root@192.168.1.203
cd /config/addons/local/ha-mcp-server
# Touch the file to update timestamp
touch server.py
# Force rebuild
ha addons rebuild local_ha-mcp-server --no-cache 2>&1 || ha addons rebuild local_ha-mcp-server
ha addons restart local_ha-mcp-server
```

**Note:** Home Assistant CLI may not support `--no-cache`, but touching the file should help.

### Option 2: Modify Dockerfile to Bust Cache

Add a build arg that changes each time:

```dockerfile
# At top of Dockerfile
ARG CACHE_BUST=1

# Before COPY
RUN echo "Cache bust: ${CACHE_BUST}"
COPY server.py .
```

Then increment `CACHE_BUST` in `build.json`:

```json
{
  "build_from": {
    "aarch64": "ghcr.io/home-assistant/aarch64-base-python:3.11"
  },
  "args": {
    "CACHE_BUST": "2"  ← Increment this each time
  }
}
```

### Option 3: Delete Image and Rebuild

**Via SSH:**

```bash
ssh root@192.168.1.203

# Find the image
docker images | grep ha-mcp-server

# Delete it (use actual image ID from above)
docker rmi <image_id> --force

# Rebuild
ha addons rebuild local_ha-mcp-server
ha addons start local_ha-mcp-server
```

### Option 4: Change Dockerfile Copy Method

Instead of `COPY server.py .`, use a wildcard or change the order:

```dockerfile
# Before
COPY server.py .

# After (forces re-evaluation)
COPY *.py .
```

Or add a RUN command before COPY:

```dockerfile
RUN echo "Building at $(date)" > /tmp/build_time
COPY server.py .
```

### Option 5: Manual Container Exec (TEMPORARY TEST)

**For testing only - changes lost on restart:**

```bash
# Find container
docker ps | grep mcp

# Copy file into running container
docker cp /config/addons/local/ha-mcp-server/server.py <container_id>:/app/server.py

# Restart container
docker restart <container_id>
```

## Verification Commands

After trying any solution, test:

```powershell
# Should return 104 tools
curl http://192.168.1.203:8001/api/actions | ConvertFrom-Json | Select-Object total_tools

# Should return state summary
curl http://192.168.1.203:8001/api/state

# Should stream events (Ctrl+C to stop)
curl -N http://192.168.1.203:8001/subscribe_events
```

## What We Know Works

✅ File is deployed correctly (4,346 lines on disk)
✅ Code is correct (routes defined properly)
✅ Container runs (health endpoint works)

The ONLY issue is the Docker image build process isn't picking up the new file.

## Recommended Next Step

**Try Option 1 first** (touch + rebuild):

```bash
ssh root@192.168.1.203
touch /config/addons/local/ha-mcp-server/server.py
ha addons rebuild local_ha-mcp-server
# Wait 60 seconds
ha addons restart local_ha-mcp-server
# Wait 20 seconds
curl http://localhost:8001/api/actions
```

If that shows 104 tools, SUCCESS! 🎉

If still 404, try **Option 3** (delete image and rebuild).

---

**Current Status:** Code is ready, just need Docker to use the new version!
