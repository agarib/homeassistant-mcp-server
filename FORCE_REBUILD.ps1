# Force Rebuild HA MCP Server (Clear Cache)
# Ensures new server.py is used by forcing Docker rebuild

$HAHost = "192.168.1.203"

Write-Host "🔄 FORCE REBUILD - ha-mcp-server-addon" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Step 1: Verify local file has new routes
Write-Host "`n[1/5] Verifying local server.py has new features..." -ForegroundColor Yellow
$routeCount = (Select-String -Path "C:\MyProjects\ha-mcp-server-addon\server.py" -Pattern "Route\(").Count
$lineCount = (Get-Content "C:\MyProjects\ha-mcp-server-addon\server.py" | Measure-Object -Line).Lines

Write-Host "  Local file:" -ForegroundColor White
Write-Host "    Lines: $lineCount" -ForegroundColor Gray
Write-Host "    Routes: $routeCount" -ForegroundColor Gray

if ($lineCount -lt 4000) {
    Write-Host "  ❌ ERROR: Local file seems wrong (too few lines)" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Local file OK" -ForegroundColor Green

# Step 2: Re-copy server.py to ensure it's fresh
Write-Host "`n[2/5] Re-copying server.py to add-on directory..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
scp C:\MyProjects\ha-mcp-server-addon\server.py root@${HAHost}:/config/addons/local/ha-mcp-server/server.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ SCP failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ File copied" -ForegroundColor Green

# Step 3: Verify remote file
Write-Host "`n[3/5] Verifying remote server.py..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$remoteLines = ssh root@$HAHost "wc -l /config/addons/local/ha-mcp-server/server.py | awk '{print `$1}'"
Write-Host "  Remote lines: $remoteLines" -ForegroundColor Gray

if ([int]$remoteLines -lt 4000) {
    Write-Host "  ❌ ERROR: Remote file has too few lines!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Remote file OK" -ForegroundColor Green

# Step 4: Stop add-on
Write-Host "`n[4/5] Stopping add-on..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
ssh root@$HAHost "ha addons stop local_ha-mcp-server"
Write-Host "  Waiting for shutdown..." -ForegroundColor Gray
Start-Sleep -Seconds 10
Write-Host "  ✅ Add-on stopped" -ForegroundColor Green

# Step 5: Rebuild with --no-cache (if possible) then start
Write-Host "`n[5/5] Rebuilding add-on (this may take 60-90 seconds)..." -ForegroundColor Yellow
ssh root@$HAHost "ha addons rebuild local_ha-mcp-server"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Rebuild failed!" -ForegroundColor Red
    Write-Host "  Attempting to start anyway..." -ForegroundColor Yellow
    ssh root@$HAHost "ha addons start local_ha-mcp-server"
    exit 1
}

Write-Host "  ✅ Rebuild complete" -ForegroundColor Green
Write-Host "`n  Starting add-on..." -ForegroundColor Gray
ssh root@$HAHost "ha addons start local_ha-mcp-server"
Write-Host "  Waiting for startup..." -ForegroundColor Gray
Start-Sleep -Seconds 20

Write-Host "`n" + ("=" * 60) -ForegroundColor Green
Write-Host "🎉 REBUILD COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green

# Verification
Write-Host "`n🧪 TESTING NEW ENDPOINTS..." -ForegroundColor Cyan

Write-Host "`n[1] Health Check..." -ForegroundColor Yellow
try {
    $health = curl http://$HAHost:8001/health -ErrorAction Stop | ConvertFrom-Json
    Write-Host "  ✅ $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ FAILED" -ForegroundColor Red
}

Write-Host "`n[2] REST API - /api/actions..." -ForegroundColor Yellow
try {
    $actions = curl http://$HAHost:8001/api/actions -ErrorAction Stop | ConvertFrom-Json
    Write-Host "  ✅ Total Tools: $($actions.total_tools)" -ForegroundColor Green
    
    if ($actions.total_tools -eq 104) {
        Write-Host "`n  🎉🎉🎉 SUCCESS! 104 TOOLS DEPLOYED! 🎉🎉🎉" -ForegroundColor Green -BackgroundColor DarkGreen
    } else {
        Write-Host "  ⚠️  WARNING: Expected 104, got $($actions.total_tools)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ FAILED: Still getting 404" -ForegroundColor Red
    Write-Host "  This means the rebuild didn't pick up the new code." -ForegroundColor Yellow
    Write-Host "  Try manually rebuilding via HA UI: Settings → Add-ons → ha-mcp-server → Rebuild" -ForegroundColor Yellow
}

Write-Host "`n[3] Camera VLM Tool..." -ForegroundColor Yellow
try {
    $actions = curl http://$HAHost:8001/api/actions -ErrorAction Stop | ConvertFrom-Json
    $vlmTool = $actions.tools | Where-Object { $_.name -eq 'analyze_camera_snapshot' }
    if ($vlmTool) {
        Write-Host "  ✅ 🎥 KILLER FEATURE FOUND!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Not found" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Can't check (API not available)" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
