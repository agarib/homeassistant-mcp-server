# Deploy Home Assistant OpenAPI Server v4.0.5
# Simple and reliable deployment script

param(
    [string]$HA_IP = "192.168.1.203",
    [string]$HA_USER = "root",
    [string]$HA_PASSWORD = "AgAGarib122728",
    [string]$ADDON_NAME = "local_ha_mcp_server"
)

$LOCAL_FILE = "c:\MyProjects\ha-openapi-server-v3.0.0\server.py"
$REMOTE_PATH = "/config/ha-mcp-server/server.py"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  HA OpenAPI Server v4.0.5 Deployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check local file
if (-not (Test-Path $LOCAL_FILE)) {
    Write-Host "ERROR: File not found: $LOCAL_FILE" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $LOCAL_FILE).Length
$fileSizeKB = [math]::Round($fileSize/1KB, 2)
Write-Host "Local file: $LOCAL_FILE" -ForegroundColor Green
Write-Host "File size: $fileSizeKB KB" -ForegroundColor Green

# Count endpoints
$endpointCount = (Select-String -Path $LOCAL_FILE -Pattern "@app\.(post|get)\(").Count
Write-Host "Endpoints: $endpointCount" -ForegroundColor Green
Write-Host ""

# Confirm
Write-Host "Target: ${HA_USER}@${HA_IP}:${REMOTE_PATH}" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Deploy to Home Assistant? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Deployment cancelled" -ForegroundColor Red
    exit 0
}
Write-Host ""

# Deploy using pscp (PuTTY)
Write-Host "Step 1: Copying file..." -ForegroundColor Cyan
try {
    if (Get-Command pscp -ErrorAction SilentlyContinue) {
        $pscpCommand = "echo y | pscp -pw $HA_PASSWORD `"$LOCAL_FILE`" `"${HA_USER}@${HA_IP}:${REMOTE_PATH}`""
        Invoke-Expression $pscpCommand
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "SUCCESS: File copied!" -ForegroundColor Green
        } else {
            throw "pscp failed with exit code $LASTEXITCODE"
        }
    } else {
        Write-Host "ERROR: pscp not found. Please install PuTTY" -ForegroundColor Red
        Write-Host ""
        Write-Host "Manual deployment:" -ForegroundColor Yellow
        Write-Host "1. Use WinSCP or FileZilla to copy:" -ForegroundColor Yellow
        Write-Host "   $LOCAL_FILE" -ForegroundColor Yellow
        Write-Host "   to ${HA_USER}@${HA_IP}:${REMOTE_PATH}" -ForegroundColor Yellow
        Write-Host "2. Then restart add-on via HA UI or SSH" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: Failed to copy file: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Restart add-on
Write-Host "Step 2: Restarting add-on..." -ForegroundColor Cyan
Write-Host "WARNING: Connection will be lost briefly" -ForegroundColor Yellow
try {
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        $plinkCommand = "echo y | plink -pw $HA_PASSWORD `"${HA_USER}@${HA_IP}`" `"ha addons restart $ADDON_NAME`""
        Invoke-Expression $plinkCommand
        Write-Host "SUCCESS: Restart initiated!" -ForegroundColor Green
    } else {
        Write-Host "WARNING: plink not found" -ForegroundColor Yellow
        Write-Host "Please restart manually via SSH or HA UI:" -ForegroundColor Yellow
        Write-Host "  ha addons restart $ADDON_NAME" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Could not restart automatically: $_" -ForegroundColor Yellow
}
Write-Host ""

# Wait
Write-Host "Waiting 15 seconds for restart..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
Write-Host ""

# Verify
Write-Host "Step 3: Verifying deployment..." -ForegroundColor Cyan
try {
    $healthUrl = "http://${HA_IP}:8001/health"
    $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10
    
    if ($response.status -eq "healthy") {
        Write-Host "SUCCESS: Server is healthy!" -ForegroundColor Green
        Write-Host "Version: $($response.version)" -ForegroundColor Green
        Write-Host "Endpoints: $($response.endpoints)" -ForegroundColor Green
        
        if ($response.version -eq "4.0.5") {
            Write-Host ""
            Write-Host "======================================" -ForegroundColor Green
            Write-Host "  v4.0.5 DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
            Write-Host "======================================" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "WARNING: Version mismatch!" -ForegroundColor Yellow
            Write-Host "Expected: 4.0.5" -ForegroundColor Yellow
            Write-Host "Got: $($response.version)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "WARNING: Could not verify health endpoint" -ForegroundColor Yellow
    Write-Host "Server may still be starting..." -ForegroundColor Yellow
}
Write-Host ""

# Next steps
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open-WebUI: http://192.168.1.11:30080" -ForegroundColor White
Write-Host "2. Settings -> Tools -> Tool Servers" -ForegroundColor White
Write-Host "3. Refresh HA OpenAPI Server connection" -ForegroundColor White
Write-Host "4. Verify 92 tools with clean names" -ForegroundColor White
Write-Host ""
Write-Host "New Tools:" -ForegroundColor Green
Write-Host "  - ha_get_config_entry_diagnostics" -ForegroundColor White
Write-Host "  - ha_get_device_diagnostics" -ForegroundColor White
Write-Host "  - ha_list_available_diagnostics" -ForegroundColor White
Write-Host "  - ha_reload_automations (IMPORTANT!)" -ForegroundColor White
Write-Host "  - ha_manual_create_custom_card" -ForegroundColor White
Write-Host "  - ha_manual_edit_custom_card" -ForegroundColor White
Write-Host "======================================" -ForegroundColor Cyan
