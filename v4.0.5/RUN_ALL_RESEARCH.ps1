# Master Research Script for v4.0.5
# Runs all research tasks

$ErrorActionPreference = "Stop"

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║            v4.0.5 Research - Master Script                   ║
║                                                              ║
║  This script will run all research tasks to gather data      ║
║  needed for v4.0.5 implementation.                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Check for HA_TOKEN
if (-not $env:HA_TOKEN) {
    Write-Host "❌ ERROR: HA_TOKEN not set!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set your Home Assistant long-lived access token:" -ForegroundColor Yellow
    Write-Host '  $env:HA_TOKEN = "eyJhbGc..."' -ForegroundColor White
    Write-Host ""
    Write-Host "Get token from: Settings → People → Long-Lived Access Tokens" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "✓ HA_TOKEN found" -ForegroundColor Green
Write-Host ""

# Create output directory if it doesn't exist
if (-not (Test-Path "v4.0.5\research_data")) {
    New-Item -ItemType Directory -Path "v4.0.5\research_data" -Force | Out-Null
}

# Start timestamp
$start_time = Get-Date
Write-Host "Research started: $start_time" -ForegroundColor Gray
Write-Host ""

# Task 1: Diagnostics API Research
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host " TASK 1: Diagnostics API Research" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

try {
    & .\v4.0.5\research_script.ps1
    Write-Host "`n✓ Task 1 completed successfully`n" -ForegroundColor Green
} catch {
    Write-Host "`n✗ Task 1 failed: $($_.Exception.Message)`n" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Task 2: Dashboard API Research
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host " TASK 2: Dashboard API Research" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

try {
    & .\v4.0.5\research_dashboard.ps1
    Write-Host "`n✓ Task 2 completed successfully`n" -ForegroundColor Green
} catch {
    Write-Host "`n✗ Task 2 failed: $($_.Exception.Message)`n" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Task 3: Device Gap Analysis
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host " TASK 3: Device Control Gap Analysis" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

try {
    & .\v4.0.5\research_device_gaps.ps1
    Write-Host "`n✓ Task 3 completed successfully`n" -ForegroundColor Green
} catch {
    Write-Host "`n✗ Task 3 failed: $($_.Exception.Message)`n" -ForegroundColor Red
}

# End timestamp
$end_time = Get-Date
$duration = $end_time - $start_time

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  RESEARCH COMPLETE!                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Duration: $($duration.TotalSeconds) seconds" -ForegroundColor Gray
Write-Host ""

# Show collected files
Write-Host "Collected data files:" -ForegroundColor Yellow
Get-ChildItem v4.0.5\research_data\*.json -ErrorAction SilentlyContinue | 
    Select-Object Name, @{N="Size (KB)";E={[math]::Round($_.Length/1KB,2)}}, LastWriteTime |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review research data in v4.0.5/research_data/" -ForegroundColor White
Write-Host "  2. Update RESEARCH_DIAGNOSTICS.md with findings" -ForegroundColor White
Write-Host "  3. Update PLANNING.md based on discoveries" -ForegroundColor White
Write-Host "  4. Design Pydantic models for new tools" -ForegroundColor White
Write-Host "  5. Begin implementation" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan
Write-Host ""
