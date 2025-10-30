# MCP Servers Validation Script (ASCII only)
# Tests Filesystem USB access and Home Assistant v2.0 endpoints

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MCP SERVERS VALIDATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test counters
$totalTests = 0
$passedTests = 0

# ===== FILESYSTEM SERVER =====
Write-Host "=== FILESYSTEM SERVER ===`n" -ForegroundColor Yellow

$fsUrl = "http://192.168.1.11:30008/filesystem"

# Test 1: USB Storage Access
Write-Host "[TEST] USB Storage Access..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{ path = "/usb-storage" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$fsUrl/list_directory" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] /usb-storage accessible ($($result.entries.Count) items)`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 2: Write File
Write-Host "[TEST] Write file to USB storage..." -ForegroundColor Cyan
$totalTests++
try {
    $testContent = "MCP Test - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $body = @{
        path = "/usb-storage/mcp-test.txt"
        content = $testContent
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "$fsUrl/write_file" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] File written successfully`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 3: Read File
Write-Host "[TEST] Read file from USB storage..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{ path = "/usb-storage/mcp-test.txt" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$fsUrl/read_file" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] File read successfully ($($result.content.Length) chars)`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 4: Delete File (cleanup)
Write-Host "[TEST] Delete test file..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{ path = "/usb-storage/mcp-test.txt" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$fsUrl/delete_file" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] File deleted successfully`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# ===== HOME ASSISTANT v2.0 =====
Write-Host "`n=== HOME ASSISTANT v2.0 SERVER ===`n" -ForegroundColor Yellow

$haUrl = "http://192.168.1.203:8001"

# Test 5: Health Check
Write-Host "[TEST] Health endpoint..." -ForegroundColor Cyan
$totalTests++
try {
    $result = Invoke-RestMethod -Uri "$haUrl/health" -TimeoutSec 5
    Write-Host "[PASS] Health: $($result.status) | Version: $($result.version)`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 6: Get States
Write-Host "[TEST] Get states (lights)..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{ domain = "light"; limit = 5 } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$haUrl/get_states" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] Found $($result.count) lights`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 7: Get Device State
Write-Host "[TEST] Get device state (light.couch_light)..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{ entity_id = "light.couch_light" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$haUrl/get_device_state" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] light.couch_light is $($result.state)`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 8: Get Area Devices
Write-Host "[TEST] Get area devices (living room)..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{ area_name = "living room" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$haUrl/get_area_devices" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] Found $($result.count) devices in living room`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 9: List Automations
Write-Host "[TEST] List automations..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$haUrl/list_automations" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] Found $($result.data.count) automations`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 10: List Add-ons
Write-Host "[TEST] List add-ons..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$haUrl/list_addons" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] Found $($result.data.addons.Count) add-ons`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 11: Analyze Home Context
Write-Host "[TEST] Analyze home context..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$haUrl/analyze_home_context" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "[PASS] Time: $($result.data.time_context) | Active devices: $($result.data.active_devices.total)`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# Test 12: Read Configuration File
Write-Host "[TEST] Read configuration file..." -ForegroundColor Cyan
$totalTests++
try {
    $body = @{ filepath = "configuration.yaml" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$haUrl/read_file" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "[PASS] Read configuration.yaml ($($result.data.content.Length) chars)`n" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "[FAIL] $_`n" -ForegroundColor Red
}

# ===== SUMMARY =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$successRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "Tests Passed: $passedTests / $totalTests" -ForegroundColor White
Write-Host "Success Rate: $successRate%`n" -ForegroundColor $(if ($successRate -eq 100) { "Green" } elseif ($successRate -ge 80) { "Yellow" } else { "Red" })

if ($successRate -eq 100) {
    Write-Host "*** ALL TESTS PASSED ***" -ForegroundColor Green
    Write-Host "Both servers are fully operational!`n" -ForegroundColor Green
} elseif ($successRate -ge 80) {
    Write-Host "*** MOST TESTS PASSED ***" -ForegroundColor Yellow
    Write-Host "Review failed tests above.`n" -ForegroundColor Yellow
} else {
    Write-Host "*** MULTIPLE FAILURES ***" -ForegroundColor Red
    Write-Host "Please check server configurations.`n" -ForegroundColor Red
}

Write-Host "Filesystem Server: http://192.168.1.11:30008/filesystem" -ForegroundColor Gray
Write-Host "Home Assistant v2: http://192.168.1.203:8001" -ForegroundColor Gray
Write-Host ""
