# v4.0.3 Tool Renaming - Manual Fix Script
# Only renames FastAPI route handlers, NOT FileManager class methods

$serverPath = "C:\MyProjects\ha-openapi-server-v3.0.0\server.py"

# Create backup
Copy-Item $serverPath "$serverPath.backup-v4.0.2-safe" -Force
Write-Host "✅ Backup created: server.py.backup-v4.0.2-safe"

# Read file
$content = Get-Content $serverPath -Raw

# Track changes
$changes = 0

# List of all FastAPI route endpoints to rename (exclude FileManager methods!)
# Format: "old_route" -> "ha_old_route"

$replacements = @{
    # Device Control
    '@app.post\("/control_light"'       = '@app.post("/ha_control_light"'
    'async def control_light\('         = 'async def ha_control_light('
    '@app.post\("/control_switch"'      = '@app.post("/ha_control_switch"'
    'async def control_switch\('        = 'async def ha_control_switch('
    '@app.post\("/control_climate"'     = '@app.post("/ha_control_climate"'
    'async def control_climate\('       = 'async def ha_control_climate('
    '@app.post\("/control_cover"'       = '@app.post("/ha_control_cover"'
    'async def control_cover\('         = 'async def ha_control_cover('
    
    # Discovery
    '@app.post\("/discover_devices"'    = '@app.post("/ha_discover_devices"'
    'async def discover_devices\('      = 'async def ha_discover_devices('
    '@app.post\("/get_device_state"'    = '@app.post("/ha_get_device_state"'
    'async def get_device_state\('      = 'async def ha_get_device_state('
    '@app.post\("/get_area_devices"'    = '@app.post("/ha_get_area_devices"'
    'async def get_area_devices\('      = 'async def ha_get_area_devices('
    '@app.post\("/get_states"'          = '@app.post("/ha_get_states"'
    'async def get_states\('            = 'async def ha_get_states('
    
    # System
    '@app.post\("/call_service"'        = '@app.post("/ha_call_service"'
    'async def call_service\('          = 'async def ha_call_service('
    '@app.post\("/restart_homeassistant"' = '@app.post("/ha_restart_homeassistant"'
    'async def restart_homeassistant\(' = 'async def ha_restart_homeassistant('
    
    # File Operations (9 - CRITICAL FOR FIX)
    '@app.post\("/read_file"'           = '@app.post("/ha_read_file"'
    'async def read_file\('             = 'async def ha_read_file('
    '@app.post\("/write_file"'          = '@app.post("/ha_write_file"'
    'async def write_file\('            = 'async def ha_write_file('
    '@app.post\("/list_directory"'      = '@app.post("/ha_list_directory"'
    'async def list_directory\('        = 'async def ha_list_directory('
    '@app.post\("/delete_file"'         = '@app.post("/ha_delete_file"'
    'async def delete_file\('           = 'async def ha_delete_file('
    '@app.post\("/create_directory"'    = '@app.post("/ha_create_directory"'
    'async def create_directory\('      = 'async def ha_create_directory('
    '@app.post\("/move_file"'           = '@app.post("/ha_move_file"'
    'async def move_file\('             = 'async def ha_move_file('
    '@app.post\("/copy_file"'           = '@app.post("/ha_copy_file"'
    'async def copy_file\('             = 'async def ha_copy_file('
    '@app.post\("/search_files"'        = '@app.post("/ha_search_files"'
    'async def search_files\('          = 'async def ha_search_files('
    '@app.post\("/get_directory_tree"'  = '@app.post("/ha_get_directory_tree"'
    'async def get_directory_tree\('    = 'async def ha_get_directory_tree('
}

# Add more replacements (continuing from file operations...)
$replacements += @{
    # Automations (7)
    '@app.post\("/list_automations"'         = '@app.post("/ha_list_automations"'
    'async def list_automations\('           = 'async def ha_list_automations('
    '@app.post\("/trigger_automation"'       = '@app.post("/ha_trigger_automation"'
    'async def trigger_automation\('         = 'async def ha_trigger_automation('
    '@app.post\("/create_automation"'        = '@app.post("/ha_create_automation"'
    'async def create_automation\('          = 'async def ha_create_automation('
    '@app.post\("/update_automation"'        = '@app.post("/ha_update_automation"'
    'async def update_automation\('          = 'async def ha_update_automation('
    '@app.post\("/delete_automation"'        = '@app.post("/ha_delete_automation"'
    'async def delete_automation\('          = 'async def ha_delete_automation('
    '@app.post\("/get_automation_details"'   = '@app.post("/ha_get_automation_details"'
    'async def get_automation_details\('     = 'async def ha_get_automation_details('
    '@app.post\("/enable_disable_automation"' = '@app.post("/ha_enable_disable_automation"'
    'async def enable_disable_automation\('  = 'async def ha_enable_disable_automation('
    
    # Scenes (3)
    '@app.post\("/create_scene"'             = '@app.post("/ha_create_scene"'
    'async def create_scene\('               = 'async def ha_create_scene('
    '@app.post\("/activate_scene"'           = '@app.post("/ha_activate_scene"'
    'async def activate_scene\('             = 'async def ha_activate_scene('
    '@app.post\("/list_scenes"'              = '@app.post("/ha_list_scenes"'
    'async def list_scenes\('                = 'async def ha_list_scenes('
    
    # Media & Devices (4)
    '@app.post\("/vacuum_control"'           = '@app.post("/ha_vacuum_control"'
    'async def vacuum_control\('             = 'async def ha_vacuum_control('
    '@app.post\("/fan_control"'              = '@app.post("/ha_fan_control"'
    'async def fan_control\('                = 'async def ha_fan_control('
    '@app.post\("/camera_snapshot"'          = '@app.post("/ha_camera_snapshot"'
    'async def camera_snapshot\('            = 'async def ha_camera_snapshot('
    '@app.post\("/media_player_control"'     = '@app.post("/ha_media_player_control"'
    'async def media_player_control\('       = 'async def ha_media_player_control('
    
    # Code Execution (3)
    '@app.post\("/execute_python"'           = '@app.post("/ha_execute_python"'
    'async def execute_python\('             = 'async def ha_execute_python('
    '@app.post\("/analyze_states_dataframe"' = '@app.post("/ha_analyze_states_dataframe"'
    'async def analyze_states_dataframe\('   = 'async def ha_analyze_states_dataframe('
    '@app.post\("/plot_sensor_history"'      = '@app.post("/ha_plot_sensor_history"'
    'async def plot_sensor_history\('        = 'async def ha_plot_sensor_history('
}

# Continue with remaining endpoints...
Write-Host "`n🔧 Applying replacements..."

foreach ($pattern in $replacements.Keys) {
    $replacement = $replacements[$pattern]
    if ($content -match [regex]::Escape($pattern -replace '\\', '')) {
        $content = $content -replace $pattern, $replacement
        $changes++
    }
}

# Write updated content
$content | Set-Content $serverPath -NoNewline

Write-Host "`n✅ Applied $changes replacements"
Write-Host "📝 Updated: $serverPath"
Write-Host "`n🎯 Next: Add remaining endpoints (add-ons, dashboards, etc.) to this script"

# Note: This is a partial example. Full script would include all 81 endpoints.
