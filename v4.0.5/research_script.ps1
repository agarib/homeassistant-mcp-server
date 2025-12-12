# v4.0.5 Diagnostics API Research Script
# Run this to gather diagnostics API data

$ErrorActionPreference = "Continue"

# Configuration
$HA_URL = "http://192.168.1.203:8123"
$HA_TOKEN = $env:HA_TOKEN  # Set this: $env:HA_TOKEN = "your_token_here"

if (-not $HA_TOKEN) {
    Write-Host "ERROR: Please set HA_TOKEN environment variable" -ForegroundColor Red
    Write-Host "Example: `$env:HA_TOKEN = 'eyJhbGc...'" -ForegroundColor Yellow
    exit 1
}

$headers = @{
    Authorization = "Bearer $HA_TOKEN"
    "Content-Type" = "application/json"
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "v4.0.5 DIAGNOSTICS API RESEARCH" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Get all config entries
Write-Host "[1] Getting all config entries..." -ForegroundColor Green
try {
    $entries = Invoke-RestMethod -Uri "$HA_URL/api/config/config_entries" -Headers $headers
    Write-Host "  ✓ Found $($entries.Count) config entries" -ForegroundColor Green
    
    # Display summary
    $entries | Select-Object domain, title, entry_id | Format-Table -AutoSize
    
    # Save to file
    $entries | ConvertTo-Json -Depth 10 | Out-File "v4.0.5/research_data/config_entries.json"
    Write-Host "  ✓ Saved to v4.0.5/research_data/config_entries.json" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Get device registry
Write-Host "`n[2] Getting device registry..." -ForegroundColor Green
try {
    $devices = Invoke-RestMethod -Uri "$HA_URL/api/config/device_registry/list" -Headers $headers
    Write-Host "  ✓ Found $($devices.Count) devices" -ForegroundColor Green
    
    # Display LG devices
    $lg_devices = $devices | Where-Object { $_.manufacturer -like "*LG*" }
    Write-Host "`n  LG Devices:" -ForegroundColor Yellow
    $lg_devices | Select-Object id, name, model | Format-Table -AutoSize
    
    # Save to file
    $devices | ConvertTo-Json -Depth 10 | Out-File "v4.0.5/research_data/device_registry.json"
    Write-Host "  ✓ Saved to v4.0.5/research_data/device_registry.json" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Try to get diagnostics for LG ThinQ (if exists)
Write-Host "`n[3] Testing config entry diagnostics (LG ThinQ)..." -ForegroundColor Green
$lg_entry = $entries | Where-Object { $_.domain -eq "lg_thinq" } | Select-Object -First 1

if ($lg_entry) {
    Write-Host "  Found LG ThinQ entry: $($lg_entry.title) ($($lg_entry.entry_id))" -ForegroundColor Yellow
    
    try {
        $diagnostics = Invoke-RestMethod `
            -Uri "$HA_URL/api/diagnostics/config_entry/$($lg_entry.entry_id)" `
            -Headers $headers
        
        Write-Host "  ✓ Successfully downloaded diagnostics!" -ForegroundColor Green
        Write-Host "`n  Diagnostics structure:" -ForegroundColor Yellow
        $diagnostics.PSObject.Properties.Name | ForEach-Object { Write-Host "    - $_" }
        
        # Save to file
        $diagnostics | ConvertTo-Json -Depth 10 | Out-File "v4.0.5/research_data/lg_config_diagnostics.json"
        Write-Host "  ✓ Saved to v4.0.5/research_data/lg_config_diagnostics.json" -ForegroundColor Green
        
        # Check for redacted fields
        $json_str = $diagnostics | ConvertTo-Json -Depth 10
        if ($json_str -match "REDACTED" -or $json_str -match "\*\*\*") {
            Write-Host "  ✓ Redaction detected in diagnostics" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Status: $($_.Exception.Response.StatusCode.Value__)" -ForegroundColor Red
    }
} else {
    Write-Host "  ! LG ThinQ integration not found, trying first available entry..." -ForegroundColor Yellow
    
    $first_entry = $entries | Select-Object -First 1
    if ($first_entry) {
        Write-Host "  Testing with: $($first_entry.domain) - $($first_entry.title)" -ForegroundColor Yellow
        
        try {
            $diagnostics = Invoke-RestMethod `
                -Uri "$HA_URL/api/diagnostics/config_entry/$($first_entry.entry_id)" `
                -Headers $headers
            
            Write-Host "  ✓ Successfully downloaded diagnostics!" -ForegroundColor Green
            $diagnostics | ConvertTo-Json -Depth 10 | Out-File "v4.0.5/research_data/sample_config_diagnostics.json"
        } catch {
            Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Test 4: Try device diagnostics
Write-Host "`n[4] Testing device diagnostics..." -ForegroundColor Green
if ($lg_devices -and $lg_devices.Count -gt 0) {
    $test_device = $lg_devices[0]
    Write-Host "  Testing with device: $($test_device.name) ($($test_device.id))" -ForegroundColor Yellow
    
    try {
        $device_diag = Invoke-RestMethod `
            -Uri "$HA_URL/api/diagnostics/device/$($test_device.id)" `
            -Headers $headers
        
        Write-Host "  ✓ Successfully downloaded device diagnostics!" -ForegroundColor Green
        $device_diag | ConvertTo-Json -Depth 10 | Out-File "v4.0.5/research_data/lg_device_diagnostics.json"
        Write-Host "  ✓ Saved to v4.0.5/research_data/lg_device_diagnostics.json" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Status: $($_.Exception.Response.StatusCode.Value__)" -ForegroundColor Red
        
        if ($_.Exception.Response.StatusCode.Value__ -eq 404) {
            Write-Host "  ! Device diagnostics not supported - may fall back to config entry" -ForegroundColor Yellow
        }
    }
}

# Test 5: Explore other diagnostic endpoints
Write-Host "`n[5] Exploring other diagnostic endpoints..." -ForegroundColor Green

$test_endpoints = @(
    "/api/diagnostics",
    "/api/diagnostics/list",
    "/api/config/config_entries/diagnostics"
)

foreach ($endpoint in $test_endpoints) {
    Write-Host "  Testing: $endpoint" -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$HA_URL$endpoint" -Headers $headers
        Write-Host "    ✓ Endpoint exists!" -ForegroundColor Green
        $result | ConvertTo-Json -Depth 2 | Out-File "v4.0.5/research_data/endpoint_$(($endpoint -replace '/', '_')).json"
    } catch {
        Write-Host "    ✗ Not found (404)" -ForegroundColor Red
    }
}

# Test 6: Dashboard API exploration
Write-Host "`n[6] Exploring Dashboard/Lovelace API..." -ForegroundColor Green

try {
    $dashboards = Invoke-RestMethod -Uri "$HA_URL/api/lovelace/dashboards/list" -Headers $headers
    Write-Host "  ✓ Found dashboards endpoint!" -ForegroundColor Green
    $dashboards | ConvertTo-Json -Depth 5 | Out-File "v4.0.5/research_data/dashboards_list.json"
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Check automation endpoints
Write-Host "`n[7] Checking automation capabilities..." -ForegroundColor Green

try {
    $automations = Invoke-RestMethod -Uri "$HA_URL/api/states" -Headers $headers | 
        Where-Object { $_.entity_id -like "automation.*" }
    
    Write-Host "  ✓ Found $($automations.Count) automations" -ForegroundColor Green
    
    if ($automations.Count -gt 0) {
        $sample = $automations[0]
        Write-Host "`n  Sample automation attributes:" -ForegroundColor Yellow
        $sample.attributes.PSObject.Properties.Name | ForEach-Object { Write-Host "    - $_" }
    }
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESEARCH COMPLETE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nAll research data saved to: v4.0.5/research_data/" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Review JSON files in v4.0.5/research_data/" -ForegroundColor White
Write-Host "  2. Update RESEARCH_DIAGNOSTICS.md with findings" -ForegroundColor White
Write-Host "  3. Design Pydantic models based on API responses" -ForegroundColor White
Write-Host "  4. Implement tools in v4.0.5" -ForegroundColor White
Write-Host ""
