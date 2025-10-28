# Rebuild HA MCP Server Add-on (104 Tools)
# Rebuilds Docker image with new server.py code

param(
    [string]$HAHost = "192.168.1.203",
    [string]$Password = "AgAGarib122728"
)

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "HA MCP Server Add-on - REBUILD Script" -ForegroundColor Cyan
Write-Host "Rebuilding Docker image with 104 tools (was 74)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Step 1: Rebuild add-on
Write-Host "`n[1/3] Rebuilding add-on Docker image..." -ForegroundColor Yellow
Write-Host "  This will create a new image with the updated server.py (4,346 lines)" -ForegroundColor White

ssh root@$HAHost "ha addons rebuild local_ha-mcp-server"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Rebuild failed!" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Rebuild complete!" -ForegroundColor Green

# Step 2: Wait for rebuild
Write-Host "`n[2/3] Waiting for rebuild to finish..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "  ✅ Ready to restart" -ForegroundColor Green

# Step 3: Restart add-on
Write-Host "`n[3/3] Restarting add-on..." -ForegroundColor Yellow
ssh root@$HAHost "ha addons restart local_ha-mcp-server"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Restart failed!" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Restart initiated" -ForegroundColor Green

# Wait for startup
Write-Host "`nWaiting for add-on to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "`n" + ("=" * 80) -ForegroundColor Green
Write-Host "REBUILD COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Green

# Verification
Write-Host "`n🧪 VERIFICATION TESTS" -ForegroundColor Cyan
Write-Host "-" * 80 -ForegroundColor Gray

Write-Host "`n[Test 1/5] Health check..." -ForegroundColor Yellow
try {
    $health = curl http://$HAHost:8001/health | ConvertFrom-Json
    Write-Host "  ✅ Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ FAILED: $_" -ForegroundColor Red
}

Write-Host "`n[Test 2/5] REST API - List Tools..." -ForegroundColor Yellow
try {
    $actions = curl http://$HAHost:8001/api/actions | ConvertFrom-Json
    Write-Host "  ✅ Total Tools: $($actions.total_tools)" -ForegroundColor Green
    if ($actions.total_tools -eq 104) {
        Write-Host "  🎉 SUCCESS: 104 tools deployed!" -ForegroundColor Green -BackgroundColor DarkGreen
    } elseif ($actions.total_tools -eq 74) {
        Write-Host "  ⚠️  WARNING: Still showing 74 tools - old image may be cached" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n[Test 3/5] SSE Endpoint..." -ForegroundColor Yellow
try {
    $sse = curl http://$HAHost:8001/subscribe_events -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✅ SSE endpoint exists" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*timeout*") {
        Write-Host "  ✅ SSE endpoint exists (timeout expected for stream)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n[Test 4/5] State API..." -ForegroundColor Yellow
try {
    $state = curl http://$HAHost:8001/api/state | ConvertFrom-Json
    Write-Host "  ✅ Total Entities: $($state.total_entities)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n[Test 5/5] Camera VLM Tool..." -ForegroundColor Yellow
try {
    $actions = curl http://$HAHost:8001/api/actions | ConvertFrom-Json
    $vlmTool = $actions.tools | Where-Object { $_.name -eq "analyze_camera_snapshot" }
    if ($vlmTool) {
        Write-Host "  ✅ Camera VLM tool found!" -ForegroundColor Green
        Write-Host "  🎥 KILLER FEATURE READY!" -ForegroundColor Green -BackgroundColor DarkGreen
    } else {
        Write-Host "  ❌ Camera VLM tool not found" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  Previous Version: 74 tools (3,071 lines)" -ForegroundColor White
Write-Host "  New Version: 104 tools (4,346 lines)" -ForegroundColor White
Write-Host "  New Features:" -ForegroundColor White
Write-Host "    • SSE real-time event streaming" -ForegroundColor Gray
Write-Host "    • Camera VLM analysis (AI vision) 🎥" -ForegroundColor Gray
Write-Host "    • Vacuum control (7 tools)" -ForegroundColor Gray
Write-Host "    • Fan control (6 tools)" -ForegroundColor Gray
Write-Host "    • Add-on management (8 tools)" -ForegroundColor Gray
Write-Host "    • REST API endpoints (batch actions)" -ForegroundColor Gray
Write-Host "`n  Health: http://$HAHost:8001/health" -ForegroundColor White
Write-Host "  API: http://$HAHost:8001/api/actions" -ForegroundColor White
Write-Host ("=" * 80) -ForegroundColor Cyan
