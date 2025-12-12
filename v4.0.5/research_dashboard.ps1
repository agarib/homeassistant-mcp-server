# Dashboard API Research Script
# Explore Lovelace/Dashboard capabilities

$ErrorActionPreference = "Continue"

$HA_URL = "http://192.168.1.203:8123"
$HA_TOKEN = $env:HA_TOKEN

if (-not $HA_TOKEN) {
    Write-Host "ERROR: Please set HA_TOKEN environment variable" -ForegroundColor Red
    exit 1
}

$headers = @{
    Authorization = "Bearer $HA_TOKEN"
    "Content-Type" = "application/json"
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DASHBOARD API RESEARCH" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: List dashboards
Write-Host "[1] Testing dashboard list endpoints..." -ForegroundColor Green

$dashboard_endpoints = @(
    "/api/lovelace/dashboards/list",
    "/api/lovelace/dashboards",
    "/api/lovelace/config",
    "/api/panel_custom"
)

foreach ($endpoint in $dashboard_endpoints) {
    Write-Host "  Testing: $endpoint" -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$HA_URL$endpoint" -Headers $headers
        Write-Host "    ✓ Success! Found data" -ForegroundColor Green
        $result | ConvertTo-Json -Depth 5 | Out-File "v4.0.5/research_data/dashboard_$(($endpoint -replace '/', '_')).json"
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.Value__
        Write-Host "    ✗ Error: $statusCode - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 2: Try creating a test dashboard
Write-Host "`n[2] Testing dashboard creation..." -ForegroundColor Green

$test_dashboard = @{
    require_admin = $false
    show_in_sidebar = $true
    icon = "mdi:test-tube"
    title = "v4.0.5 Research Test"
    url_path = "v405-research-test"
} | ConvertTo-Json

Write-Host "  Attempting to create test dashboard..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod `
        -Uri "$HA_URL/api/lovelace/dashboards" `
        -Method POST `
        -Headers $headers `
        -Body $test_dashboard
    
    Write-Host "    ✓ Dashboard created successfully!" -ForegroundColor Green
    $created_id = $result.url_path
    Write-Host "    Dashboard ID: $created_id" -ForegroundColor Yellow
    
    # Save the created dashboard details
    $result | ConvertTo-Json -Depth 5 | Out-File "v4.0.5/research_data/dashboard_created.json"
    
    # Test 3: Try updating the dashboard
    Write-Host "`n[3] Testing dashboard update..." -ForegroundColor Green
    
    $update_data = @{
        require_admin = $false
        show_in_sidebar = $true
        icon = "mdi:test-tube-empty"
        title = "v4.0.5 Research Test (Updated)"
    } | ConvertTo-Json
    
    try {
        $update_result = Invoke-RestMethod `
            -Uri "$HA_URL/api/lovelace/dashboards/$created_id" `
            -Method POST `
            -Headers $headers `
            -Body $update_data
        
        Write-Host "    ✓ Dashboard updated successfully!" -ForegroundColor Green
    } catch {
        Write-Host "    ✗ Update failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 4: Try deleting the dashboard
    Write-Host "`n[4] Testing dashboard deletion..." -ForegroundColor Green
    
    try {
        Invoke-RestMethod `
            -Uri "$HA_URL/api/lovelace/dashboards/$created_id" `
            -Method DELETE `
            -Headers $headers
        
        Write-Host "    ✓ Dashboard deleted successfully!" -ForegroundColor Green
    } catch {
        Write-Host "    ✗ Delete failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "    ! You may need to delete manually: Settings → Dashboards → $created_id" -ForegroundColor Yellow
    }
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    Write-Host "    ✗ Creation failed: $statusCode" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($statusCode -eq 401 -or $statusCode -eq 403) {
        Write-Host "`n    ⚠️  PERMISSION ERROR DETECTED" -ForegroundColor Yellow
        Write-Host "    Dashboard tools may require admin token!" -ForegroundColor Yellow
        Write-Host "    Current token type: SUPERVISOR_TOKEN or admin?" -ForegroundColor Yellow
    }
}

# Test 5: Check Lovelace config access
Write-Host "`n[5] Testing Lovelace config access..." -ForegroundColor Green

try {
    $config = Invoke-RestMethod -Uri "$HA_URL/api/lovelace/config" -Headers $headers
    Write-Host "  ✓ Can read Lovelace config" -ForegroundColor Green
    
    Write-Host "`n  Config structure:" -ForegroundColor Yellow
    $config.PSObject.Properties.Name | ForEach-Object { Write-Host "    - $_" }
    
    $config | ConvertTo-Json -Depth 10 | Out-File "v4.0.5/research_data/lovelace_config.json"
} catch {
    Write-Host "  ✗ Cannot read config: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Check panel custom
Write-Host "`n[6] Checking custom panels..." -ForegroundColor Green

try {
    $panels = Invoke-RestMethod -Uri "$HA_URL/api/panel_custom" -Headers $headers
    Write-Host "  ✓ Can list custom panels" -ForegroundColor Green
    $panels | ConvertTo-Json -Depth 5 | Out-File "v4.0.5/research_data/custom_panels.json"
} catch {
    Write-Host "  ✗ Cannot list panels: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DASHBOARD RESEARCH FINDINGS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Check research_data/ for detailed API responses" -ForegroundColor Green
Write-Host "`nKey Questions to Answer:" -ForegroundColor Yellow
Write-Host "  1. What permission errors occurred?" -ForegroundColor White
Write-Host "  2. Does SUPERVISOR_TOKEN work for dashboards?" -ForegroundColor White
Write-Host "  3. Is admin token required?" -ForegroundColor White
Write-Host "  4. What endpoints are available?" -ForegroundColor White
Write-Host ""
