# Auto-Deploy Home Assistant OpenAPI Server v4.0.5
# No confirmation required - direct deployment

$HA_IP = "192.168.1.203"
$HA_USER = "root"
$HA_PASSWORD = "AgAGarib122728"
$ADDON_NAME = "local_ha_mcp_server"
$LOCAL_FILE = "c:\MyProjects\ha-openapi-server-v3.0.0\server.py"
$REMOTE_PATH = "/config/ha-mcp-server/server.py"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  HA OpenAPI v4.0.5 Auto-Deploy" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verify file
if (-not (Test-Path $LOCAL_FILE)) {
    Write-Host "ERROR: File not found!" -ForegroundColor Red
    exit 1
}

$fileSize = [math]::Round((Get-Item $LOCAL_FILE).Length/1KB, 2)
$endpoints = (Select-String -Path $LOCAL_FILE -Pattern "@app\.(post|get)\(").Count

Write-Host "File: $fileSize KB, $endpoints endpoints" -ForegroundColor Green
Write-Host "Target: ${HA_USER}@${HA_IP}" -ForegroundColor Yellow
Write-Host ""

# Copy file
Write-Host "[1/3] Copying file..." -ForegroundColor Cyan
try {
    if (Get-Command pscp -ErrorAction SilentlyContinue) {
        $null = echo y | pscp -pw $HA_PASSWORD "$LOCAL_FILE" "${HA_USER}@${HA_IP}:${REMOTE_PATH}" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "      SUCCESS!" -ForegroundColor Green
        } else {
            throw "pscp exit code: $LASTEXITCODE"
        }
    } else {
        Write-Host "      ERROR: pscp not found (install PuTTY)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "      ERROR: $_" -ForegroundColor Red
    exit 1
}

# Restart add-on
Write-Host ""
Write-Host "[2/3] Restarting add-on..." -ForegroundColor Cyan
Write-Host "      (connection will be lost briefly)" -ForegroundColor Yellow
try {
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        $null = echo y | plink -pw $HA_PASSWORD "${HA_USER}@${HA_IP}" "ha addons restart $ADDON_NAME" 2>&1
        Write-Host "      Restart initiated!" -ForegroundColor Green
    } else {
        Write-Host "      WARNING: plink not found - manual restart needed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      WARNING: $_" -ForegroundColor Yellow
}

# Wait and verify
Write-Host ""
Write-Host "[3/3] Waiting 15s then verifying..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

try {
    $response = Invoke-RestMethod -Uri "http://${HA_IP}:8001/health" -TimeoutSec 10
    
    if ($response.version -eq "4.0.5") {
        Write-Host ""
        Write-Host "======================================" -ForegroundColor Green
        Write-Host "  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
        Write-Host "  Version: $($response.version)" -ForegroundColor Green
        Write-Host "  Endpoints: $($response.endpoints)" -ForegroundColor Green
        Write-Host "======================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next: Open-WebUI -> Tools -> Refresh" -ForegroundColor Yellow
    } else {
        Write-Host "      Version: $($response.version) (expected 4.0.5)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      WARNING: Health check failed - server may still be starting" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
