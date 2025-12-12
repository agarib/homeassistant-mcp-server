#!/usr/bin/env pwsh
# Fix doubled tool names by adding operation_id to all endpoints

$serverFile = "c:\MyProjects\ha-openapi-server-v3.0.0\server.py"
$content = Get-Content $serverFile -Raw

Write-Host "Fixing all endpoint operation_ids..." -ForegroundColor Cyan

# All 85 endpoints
$endpoints = @(
    "ha_control_light", "ha_control_switch", "ha_control_climate", "ha_control_cover",
    "ha_discover_devices", "ha_get_device_state", "ha_get_area_devices", "ha_get_states",
    "ha_call_service", "ha_read_file", "ha_write_file", "ha_list_directory", "ha_delete_file",
    "ha_create_directory", "ha_move_file", "ha_copy_file", "ha_search_files", "ha_get_directory_tree",
    "ha_list_automations", "ha_trigger_automation", "ha_create_automation", "ha_update_automation",
    "ha_delete_automation", "ha_get_automation_details", "ha_enable_disable_automation",
    "ha_create_scene", "ha_activate_scene", "ha_list_scenes",
    "ha_vacuum_control", "ha_fan_control", "ha_camera_snapshot", "ha_media_player_control",
    "ha_restart_homeassistant", "ha_execute_python", "ha_analyze_states_dataframe",
    "ha_plot_sensor_history", "ha_list_addons", "ha_get_addon_info", "ha_start_addon",
    "ha_stop_addon", "ha_restart_addon", "ha_install_addon", "ha_uninstall_addon",
    "ha_update_addon", "ha_get_addon_logs", "ha_get_entity_history", "ha_get_system_logs",
    "ha_get_error_log", "ha_diagnose_entity", "ha_get_statistics", "ha_get_binary_sensor",
    "ha_list_dashboards", "ha_get_dashboard_config", "ha_create_dashboard",
    "ha_update_dashboard_config", "ha_delete_dashboard", "ha_list_hacs_cards",
    "ha_create_button_card", "ha_create_mushroom_card", "ha_analyze_home_context",
    "ha_activity_recognition", "ha_comfort_optimization", "ha_energy_intelligence",
    "ha_intelligent_security_monitor", "ha_anomaly_detection", "ha_vacation_mode",
    "ha_analyze_camera_vlm", "ha_object_detection", "ha_facial_recognition",
    "ha_get_entity_state", "ha_list_entities", "ha_get_services", "ha_fire_event",
    "ha_render_template", "ha_get_config", "ha_get_history", "ha_get_logbook",
    "ha_get_system_logs_diagnostics", "ha_get_persistent_notifications",
    "ha_get_integration_status", "ha_get_startup_errors"
)

$fixCount = 0

foreach ($endpoint in $endpoints) {
    $oldPattern = "@app.post(`"/$endpoint`", summary="
    $newPattern = "@app.post(`"/$endpoint`", operation_id=`"$endpoint`", summary="
    
    if ($content -match [regex]::Escape($oldPattern)) {
        $content = $content -replace [regex]::Escape($oldPattern), $newPattern
        $fixCount++
        Write-Host "  Fixed: $endpoint" -ForegroundColor Green
    }
}

Set-Content -Path $serverFile -Value $content -NoNewline

Write-Host ""
Write-Host "Done! Fixed $fixCount endpoints" -ForegroundColor Green
Write-Host "Tool names in Open-WebUI will now be clean (e.g., 'ha_control_light' instead of 'ha_control_light_ha_control_light_post')" -ForegroundColor Cyan
