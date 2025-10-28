# Deploy Updated ha-mcp-server Add-on (104 tools, REST endpoints)
# Copies new server.py to Home Assistant host and restarts add-on

param(
    [string]$HAHost = "192.168.1.203",
    [string]$Username = "root",
    [string]$AddonPath = "/usr/share/hassio/addons/local/ha-mcp-server-addon"
)

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "HA-MCP-Server Add-on Deployment Script" -ForegroundColor Cyan
Write-Host "Deploying: server.py (4,280 lines, 104 tools)" -ForegroundColor Cyan
Write-Host "Target: $HAHost`:$AddonPath" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Step 1: Verify local file exists
$LocalServerPy = "C:\MyProjects\ha-mcp-server-addon\server.py"
if (-not (Test-Path $LocalServerPy)) {
    Write-Host "ERROR: Local server.py not found at $LocalServerPy" -ForegroundColor Red
    exit 1
}

$LineCount = (Get-Content $LocalServerPy | Measure-Object -Line).Lines
Write-Host "`n[1/5] Local file verified:" -ForegroundColor Green
Write-Host "  - Path: $LocalServerPy"
Write-Host "  - Lines: $LineCount"
Write-Host "  - Expected: 4280 lines"

if ($LineCount -ne 4280) {
    Write-Host "  WARNING: Line count mismatch! Expected 4280, got $LineCount" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
}

# Step 2: Test SSH connectivity
Write-Host "`n[2/5] Testing SSH connectivity to $HAHost..." -ForegroundColor Yellow
try {
    $sshTest = ssh -o ConnectTimeout=5 -o BatchMode=yes $Username@$HAHost "echo OK" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: SSH connection failed. Please ensure:" -ForegroundColor Red
        Write-Host "  1. SSH is enabled in Home Assistant (Port 22 add-on)" -ForegroundColor Red
        Write-Host "  2. SSH key is configured (or use password auth)" -ForegroundColor Red
        Write-Host "  3. Host $HAHost is reachable" -ForegroundColor Red
        
        Write-Host "`nAttempting alternative deployment methods..." -ForegroundColor Yellow
        Write-Host "`nOPTION A: Use Home Assistant File Editor" -ForegroundColor Cyan
        Write-Host "  1. Open HA UI -> Supervisor -> ha-mcp-server" -ForegroundColor White
        Write-Host "  2. Click 'Configuration' tab -> Edit server.py" -ForegroundColor White
        Write-Host "  3. Replace entire content with: C:\MyProjects\ha-mcp-server-addon\server.py" -ForegroundColor White
        Write-Host "  4. Save and restart add-on" -ForegroundColor White
        
        Write-Host "`nOPTION B: Manual SCP (if SSH works with password)" -ForegroundColor Cyan
        Write-Host "  scp $LocalServerPy ${Username}@${HAHost}:${AddonPath}/server.py" -ForegroundColor White
        
        exit 1
    }
    Write-Host "  SSH connection successful!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Backup existing server.py on remote host
Write-Host "`n[3/5] Creating backup of existing server.py..." -ForegroundColor Yellow
$BackupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupPath = "$AddonPath/server.py.backup_$BackupTimestamp"

ssh $Username@$HAHost "cp $AddonPath/server.py $BackupPath && wc -l $AddonPath/server.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to backup existing server.py" -ForegroundColor Red
    exit 1
}
Write-Host "  Backup created: $BackupPath" -ForegroundColor Green

# Step 4: Copy new server.py to add-on
Write-Host "`n[4/5] Copying new server.py to add-on..." -ForegroundColor Yellow
scp $LocalServerPy "${Username}@${HAHost}:${AddonPath}/server.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to copy server.py" -ForegroundColor Red
    Write-Host "  Attempting to restore backup..." -ForegroundColor Yellow
    ssh $Username@$HAHost "cp $BackupPath $AddonPath/server.py"
    exit 1
}

# Verify copy
$RemoteLineCount = ssh $Username@$HAHost "wc -l $AddonPath/server.py | awk '{print `$1}'"
Write-Host "  Remote server.py lines: $RemoteLineCount" -ForegroundColor Green
if ($RemoteLineCount -ne "4280") {
    Write-Host "  WARNING: Remote line count mismatch!" -ForegroundColor Yellow
}

# Step 5: Restart add-on
Write-Host "`n[5/5] Restarting ha-mcp-server add-on..." -ForegroundColor Yellow
Write-Host "  Please restart the add-on manually:" -ForegroundColor Cyan
Write-Host "  1. Open HA UI -> Supervisor -> ha-mcp-server" -ForegroundColor White
Write-Host "  2. Click 'Restart' button" -ForegroundColor White
Write-Host "`n  OR use SSH:" -ForegroundColor Cyan
Write-Host "  ssh $Username@$HAHost 'ha addons restart local_ha_mcp_server'" -ForegroundColor White

Write-Host "`n" + ("=" * 80) -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Restart add-on (see above)" -ForegroundColor White
Write-Host "2. Verify health: curl http://$HAHost:8001/health" -ForegroundColor White
Write-Host "3. Test new endpoints:" -ForegroundColor White
Write-Host "   - curl http://$HAHost:8001/api/actions | ConvertFrom-Json | Select-Object total_tools" -ForegroundColor Gray
Write-Host "   - curl http://$HAHost:8001/api/state" -ForegroundColor Gray
Write-Host "   - curl -N http://$HAHost:8001/subscribe_events?domain=light" -ForegroundColor Gray
Write-Host "4. Check MCPO connectivity" -ForegroundColor White

Write-Host "`nDeployment Summary:" -ForegroundColor Cyan
Write-Host "  Local file: $LineCount lines" -ForegroundColor White
Write-Host "  Remote file: $RemoteLineCount lines" -ForegroundColor White
Write-Host "  Backup: $BackupPath" -ForegroundColor White
Write-Host "  Expected tools: 104" -ForegroundColor White
Write-Host "  Expected features: SSE streaming, VLM camera, REST API, vacuum/fan, add-on management" -ForegroundColor White
