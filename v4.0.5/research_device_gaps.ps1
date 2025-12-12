# Device Control Gap Analysis
# Identify missing device types

$ErrorActionPreference = "Continue"

$HA_URL = "http://192.168.1.203:8123"
$HA_TOKEN = $env:HA_TOKEN

if (-not $HA_TOKEN) {
    Write-Host "ERROR: Please set HA_TOKEN environment variable" -ForegroundColor Red
    exit 1
}

$headers = @{
    Authorization = "Bearer $HA_TOKEN"
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEVICE CONTROL GAP ANALYSIS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Current device control tools in v4.0.4
$current_tools = @(
    "light",
    "switch", 
    "climate",
    "cover",
    "vacuum",
    "fan",
    "media_player"
)

Write-Host "Current device control tools (7):" -ForegroundColor Green
$current_tools | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }

# Get all states to analyze device classes
Write-Host "`n[1] Fetching all entity states..." -ForegroundColor Yellow

try {
    $states = Invoke-RestMethod -Uri "$HA_URL/api/states" -Headers $headers
    Write-Host "  ✓ Found $($states.Count) entities" -ForegroundColor Green
    
    # Group by domain
    $domains = $states | Group-Object { $_.entity_id.Split('.')[0] } | 
        Sort-Object Count -Descending
    
    Write-Host "`n[2] Entities by domain:" -ForegroundColor Yellow
    $domains | Select-Object Name, Count | Format-Table -AutoSize
    
    # Identify domains not covered by current tools
    $all_domains = $domains | Select-Object -ExpandProperty Name
    $missing_domains = $all_domains | Where-Object { $current_tools -notcontains $_ }
    
    Write-Host "`n[3] Domains NOT covered by current tools:" -ForegroundColor Yellow
    
    $priority_domains = @(
        "lock",
        "alarm_control_panel",
        "humidifier",
        "water_heater",
        "siren",
        "number",
        "select",
        "button",
        "text",
        "input_boolean",
        "input_number",
        "input_select",
        "input_text",
        "input_datetime"
    )
    
    foreach ($domain in $missing_domains) {
        $count = ($domains | Where-Object { $_.Name -eq $domain }).Count
        
        if ($priority_domains -contains $domain) {
            Write-Host "  ⚠️  $domain ($count entities) - HIGH PRIORITY" -ForegroundColor Yellow
        } else {
            Write-Host "  ℹ️  $domain ($count entities)" -ForegroundColor Gray
        }
    }
    
    # Analyze specific high-priority domains
    Write-Host "`n[4] Analyzing high-priority missing domains:" -ForegroundColor Yellow
    
    $analysis = @()
    
    foreach ($domain in $priority_domains) {
        $entities = $states | Where-Object { $_.entity_id -like "$domain.*" }
        
        if ($entities.Count -gt 0) {
            Write-Host "`n  📊 $domain ($($entities.Count) entities)" -ForegroundColor Cyan
            
            # Sample entity
            $sample = $entities[0]
            Write-Host "    Sample: $($sample.entity_id)" -ForegroundColor White
            Write-Host "    State: $($sample.state)" -ForegroundColor White
            
            # Check attributes for supported actions
            if ($sample.attributes) {
                $attrs = $sample.attributes.PSObject.Properties.Name
                Write-Host "    Attributes: $($attrs -join ', ')" -ForegroundColor Gray
                
                # Check for supported features
                if ($sample.attributes.supported_features) {
                    Write-Host "    Supported Features: $($sample.attributes.supported_features)" -ForegroundColor Gray
                }
            }
            
            # Get available services for this domain
            try {
                $services = Invoke-RestMethod -Uri "$HA_URL/api/services" -Headers $headers
                $domain_services = $services | Where-Object { $_.domain -eq $domain }
                
                if ($domain_services) {
                    $service_list = $domain_services.services.PSObject.Properties.Name
                    Write-Host "    Available Services: $($service_list -join ', ')" -ForegroundColor Green
                }
            } catch {
                Write-Host "    ⚠️  Could not fetch services" -ForegroundColor Red
            }
            
            $analysis += @{
                domain = $domain
                count = $entities.Count
                sample_entity = $sample.entity_id
                attributes = $attrs
                priority = "HIGH"
            }
        }
    }
    
    # Save analysis
    $analysis | ConvertTo-Json -Depth 5 | Out-File "v4.0.5/research_data/device_gap_analysis.json"
    
    # Recommendations
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "RECOMMENDATIONS FOR v4.0.5" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "Suggested new device control tools:" -ForegroundColor Green
    Write-Host ""
    
    $recommendations = @(
        @{name="ha_control_lock"; domains=@("lock"); priority="HIGH"; reason="Security - lock/unlock control"},
        @{name="ha_control_alarm"; domains=@("alarm_control_panel"); priority="HIGH"; reason="Security - arm/disarm alarm"},
        @{name="ha_control_humidifier"; domains=@("humidifier"); priority="MEDIUM"; reason="Climate control"},
        @{name="ha_control_water_heater"; domains=@("water_heater"); priority="MEDIUM"; reason="Energy management"},
        @{name="ha_control_siren"; domains=@("siren"); priority="LOW"; reason="Alert system"},
        @{name="ha_set_number"; domains=@("number", "input_number"); priority="MEDIUM"; reason="Generic number control"},
        @{name="ha_select_option"; domains=@("select", "input_select"); priority="MEDIUM"; reason="Generic select control"},
        @{name="ha_press_button"; domains=@("button"); priority="LOW"; reason="Generic button press"}
    )
    
    foreach ($rec in $recommendations) {
        $total_count = 0
        foreach ($d in $rec.domains) {
            $count = ($states | Where-Object { $_.entity_id -like "$d.*" }).Count
            $total_count += $count
        }
        
        if ($total_count -gt 0) {
            $color = switch ($rec.priority) {
                "HIGH" { "Yellow" }
                "MEDIUM" { "White" }
                "LOW" { "Gray" }
            }
            
            Write-Host "  $($rec.priority): $($rec.name)" -ForegroundColor $color
            Write-Host "    Domains: $($rec.domains -join ', ') ($total_count entities)" -ForegroundColor Gray
            Write-Host "    Reason: $($rec.reason)" -ForegroundColor Gray
            Write-Host ""
        }
    }
    
    Write-Host "Analysis saved to: v4.0.5/research_data/device_gap_analysis.json" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
