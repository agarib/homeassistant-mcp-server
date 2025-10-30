# Deploy Home Assistant OpenAPI Server v2.0
# This script uploads and restarts the server on Home Assistant

param(
    [string]$HaHost = "192.168.1.203",
    [switch]$TestFirst
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  HA OpenAPI Server v2.0 Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# File paths
$LocalServer = "C:\MyProjects\ha-openapi-server-v2\server.py"
$RemotePath = "/config/ha-mcp-server/server.py"
$RemoteRequirements = "/config/ha-mcp-server/requirements.txt"

# Step 1: Verify files exist
Write-Host "✓ Checking local files..." -ForegroundColor Yellow
if (-not (Test-Path $LocalServer)) {
    Write-Host "❌ Error: server.py not found at $LocalServer" -ForegroundColor Red
    exit 1
}
Write-Host "  Found: server.py ($(((Get-Item $LocalServer).Length / 1KB).ToString('F1')) KB)" -ForegroundColor Green

# Step 2: Optional - Test server locally first
if ($TestFirst) {
    Write-Host "`n✓ Running local tests..." -ForegroundColor Yellow
    python test_server.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Tests failed! Aborting deployment." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Tests passed!" -ForegroundColor Green
}

# Step 3: Backup current server
Write-Host "`n✓ Creating backup of current server..." -ForegroundColor Yellow
$BackupName = "server.py.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
ssh root@$HaHost "cp $RemotePath /config/ha-mcp-server/$BackupName 2>/dev/null || true"
Write-Host "  Backup created: $BackupName" -ForegroundColor Green

# Step 4: Upload new server
Write-Host "`n✓ Uploading server.py..." -ForegroundColor Yellow
scp $LocalServer root@${HaHost}:${RemotePath}
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Upload complete" -ForegroundColor Green

# Step 5: Upload requirements.txt
if (Test-Path "C:\MyProjects\ha-openapi-server-v2\requirements.txt") {
    Write-Host "`n✓ Uploading requirements.txt..." -ForegroundColor Yellow
    scp "C:\MyProjects\ha-openapi-server-v2\requirements.txt" root@${HaHost}:${RemoteRequirements}
    Write-Host "  Upload complete" -ForegroundColor Green
}

# Step 6: Restart container
Write-Host "`n✓ Restarting HA MCP Server addon..." -ForegroundColor Yellow
ssh root@$HaHost "docker restart addon_local_ha-mcp-server"
Write-Host "  Container restart initiated" -ForegroundColor Green

# Step 7: Wait for startup
Write-Host "`n✓ Waiting for server startup (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Step 8: Health check
Write-Host "`n✓ Testing server health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://${HaHost}:8001/health" -TimeoutSec 5
    Write-Host "  Server Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Version: $($health.version)" -ForegroundColor Green
    Write-Host "  Service: $($health.service)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    Write-Host "`nRolling back to previous version..." -ForegroundColor Yellow
    ssh root@$HaHost "cp /config/ha-mcp-server/$BackupName $RemotePath"
    ssh root@$HaHost "docker restart addon_local_ha-mcp-server"
    exit 1
}

# Step 9: Test a basic endpoint
Write-Host "`n✓ Testing get_states endpoint..." -ForegroundColor Yellow
try {
    $body = @{ domain = "light"; limit = 3 } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "http://${HaHost}:8001/get_states" `
        -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    
    Write-Host "  ✓ Endpoint working! Found $($result.count) states" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Warning: Endpoint test failed: $_" -ForegroundColor Yellow
    Write-Host "  (Server is up but endpoint may need debugging)" -ForegroundColor Yellow
}

# Step 10: Show API documentation URL
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nServer URLs:" -ForegroundColor White
Write-Host "  Health:  http://${HaHost}:8001/health" -ForegroundColor Cyan
Write-Host "  API Docs: http://${HaHost}:8001/docs" -ForegroundColor Cyan
Write-Host "  OpenAPI:  http://${HaHost}:8001/openapi.json" -ForegroundColor Cyan

Write-Host "`nOpen-WebUI Integration:" -ForegroundColor White
Write-Host "  Add this URL as OpenAPI server:" -ForegroundColor Cyan
Write-Host "  http://ha-mcp-server.cluster-services:8001" -ForegroundColor Green

Write-Host "`nBackup Location:" -ForegroundColor White
Write-Host "  /config/ha-mcp-server/$BackupName" -ForegroundColor Cyan

Write-Host "`n✨ You can now test with Open-WebUI!" -ForegroundColor Yellow
Write-Host ""
