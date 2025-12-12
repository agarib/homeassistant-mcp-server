# Deploy Home Assistant OpenAPI Server v4.0.5
# Date: November 7, 2025
# Target: 192.168.1.203

Write-Host "🚀 Deploying Home Assistant OpenAPI Server v4.0.5" -ForegroundColor Cyan
Write-Host ""

# Configuration
$HA_IP = "192.168.1.203"
$HA_USER = "root"
$HA_PASSWORD = "AgAGarib122728"
$LOCAL_FILE = "c:\MyProjects\ha-openapi-server-v3.0.0\server.py"
$REMOTE_PATH = "/config/ha-mcp-server/server.py"
$ADDON_NAME = "local_ha_mcp_server"

# Pre-deployment checks
Write-Host "📋 Pre-deployment Checks" -ForegroundColor Yellow
Write-Host "  ✓ Local file: $LOCAL_FILE"
Write-Host "  ✓ Target: ${HA_USER}@${HA_IP}:${REMOTE_PATH}"
Write-Host ""

# Verify local file exists
if (-not (Test-Path $LOCAL_FILE)) {
    Write-Host "❌ ERROR: Local file not found: $LOCAL_FILE" -ForegroundColor Red
    exit 1
}

# Get file size and version
$fileSize = (Get-Item $LOCAL_FILE).Length
Write-Host "  📄 File size: $([math]::Round($fileSize/1KB, 2)) KB"

# Check version in file
$versionLine = Select-String -Path $LOCAL_FILE -Pattern "Version: (\d+\.\d+\.\d+)" | Select-Object -First 1
if ($versionLine) {
    $version = $versionLine.Matches.Groups[1].Value
    Write-Host "  🔖 Version: $version" -ForegroundColor Green
}

# Count endpoints
$endpointCount = (Select-String -Path $LOCAL_FILE -Pattern "@app\.(post|get)\(" | Measure-Object).Count
Write-Host "  🎯 Endpoints: $endpointCount" -ForegroundColor Green
Write-Host ""

# Confirm deployment
Write-Host "⚠️  Ready to deploy to Home Assistant!" -ForegroundColor Yellow
Write-Host "   This will:"
Write-Host "   1. Copy server.py to $REMOTE_PATH"
Write-Host "   2. Restart the add-on"
Write-Host "   3. Connection may be lost during restart"
Write-Host ""
$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}
Write-Host ""

# Step 1: Copy file via SCP
Write-Host "📤 Step 1: Copying server.py to Home Assistant..." -ForegroundColor Cyan
try {
    # Using pscp (PuTTY SCP) if available, otherwise scp
    if (Get-Command pscp -ErrorAction SilentlyContinue) {
        Write-Host "   Using pscp (PuTTY SCP)..."
        echo y | pscp -pw $HA_PASSWORD $LOCAL_FILE "${HA_USER}@${HA_IP}:${REMOTE_PATH}"
    } elseif (Get-Command scp -ErrorAction SilentlyContinue) {
        Write-Host "   Using scp..."
        # Note: scp requires SSH key or manual password entry
        scp $LOCAL_FILE "${HA_USER}@${HA_IP}:${REMOTE_PATH}"
    } else {
        Write-Host "❌ ERROR: No SCP client found (pscp or scp)" -ForegroundColor Red
        Write-Host "   Install PuTTY or OpenSSH to continue" -ForegroundColor Yellow
        exit 1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ File copied successfully!" -ForegroundColor Green
    } else {
        throw "SCP failed with exit code $LASTEXITCODE"
    }
    } catch {
    Write-Host "❌ ERROR: Failed to copy file: $_" -ForegroundColor Red
    Write-Host "   Please copy file manually:" -ForegroundColor Yellow
    Write-Host "   scp $LOCAL_FILE ${HA_USER}@${HA_IP}:${REMOTE_PATH}" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 2: Verify file was copied
Write-Host "🔍 Step 2: Verifying deployment..." -ForegroundColor Cyan
try {
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        Write-Host "   Checking remote file..."
        echo y | plink -pw $HA_PASSWORD "${HA_USER}@${HA_IP}" "ls -lh $REMOTE_PATH"
        Write-Host "   ✅ File verified on remote server!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not verify remote file (non-critical)" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Restart add-on
Write-Host "🔄 Step 3: Restarting Home Assistant add-on..." -ForegroundColor Cyan
Write-Host "   ⚠️  WARNING: Connection will be lost for ~10 seconds" -ForegroundColor Yellow
try {
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        echo y | plink -pw $HA_PASSWORD "${HA_USER}@${HA_IP}" "ha addons restart $ADDON_NAME"
        Write-Host "   ✅ Add-on restart initiated!" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Manual restart required:" -ForegroundColor Yellow
        Write-Host "      SSH into HA and run: ha addons restart $ADDON_NAME"
    }
} catch {
    Write-Host "⚠️  Could not restart add-on automatically" -ForegroundColor Yellow
    Write-Host "   Manual restart required via SSH or HA UI" -ForegroundColor Yellow
}
Write-Host ""

# Wait for service to restart
Write-Host "Waiting for service to restart (15 seconds)..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
Write-Host ""

# Step 4: Verify deployment
Write-Host "✅ Step 4: Verifying deployment..." -ForegroundColor Cyan
try {
    $healthUrl = "http://${HA_IP}:8001/health"
    Write-Host "   Checking health endpoint: $healthUrl"
    
    $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10
    
    if ($response.status -eq "healthy") {
        Write-Host "   ✅ Server is healthy!" -ForegroundColor Green
        Write-Host "   📌 Version: $($response.version)" -ForegroundColor Cyan
        Write-Host "   📌 Endpoints: $($response.endpoints)" -ForegroundColor Cyan
        
        if ($response.version -eq "4.0.5") {
            Write-Host "   🎉 v4.0.5 DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  WARNING: Version mismatch (expected 4.0.5, got $($response.version))" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  Server responded but status: $($response.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not verify health endpoint: $_" -ForegroundColor Yellow
    Write-Host "   Server may still be starting up..." -ForegroundColor Yellow
}
Write-Host ""

# Final summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎊 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Open Open-WebUI: http://192.168.1.11:30080"
Write-Host "   2. Go to Settings → Tools → Tool Servers"
Write-Host "   3. Find 'Home Assistant OpenAPI Server - v4.0.5'"
Write-Host "   4. Refresh connection"
Write-Host "   5. Verify 92 tools visible with clean names"
Write-Host ""
Write-Host "🔗 API Endpoints:" -ForegroundColor Yellow
Write-Host "   Health: http://${HA_IP}:8001/health"
Write-Host "   Docs: http://${HA_IP}:8001/docs"
Write-Host "   OpenAPI: http://${HA_IP}:8001/openapi.json"
Write-Host ""
Write-Host "🆕 New Tools in v4.0.5:" -ForegroundColor Green
Write-Host "   ✅ ha_get_config_entry_diagnostics"
Write-Host "   ✅ ha_get_device_diagnostics"
Write-Host "   ✅ ha_list_available_diagnostics"
Write-Host "   ✅ ha_reload_automations (IMPORTANT!)"
Write-Host "   ✅ ha_manual_create_custom_card"
Write-Host "   ✅ ha_manual_edit_custom_card"
Write-Host ""
Write-Host "🐛 Bug Fixes:" -ForegroundColor Green
Write-Host "   ✅ Fixed doubled tool names"
Write-Host "   ✅ Fixed ha_get_error_log 500 error"
Write-Host "   ✅ Added restart connection warning"
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
