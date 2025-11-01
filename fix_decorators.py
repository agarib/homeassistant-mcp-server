#!/usr/bin/env python3
"""
Fix decorators - Add ha_ prefix to route paths
Function names already have ha_ prefix, just need to fix @app.post() paths
"""

from pathlib import Path
import re

# All endpoints that need ha_ prefix in their route
ENDPOINTS = [
    "control_light", "control_switch", "control_climate", "control_cover",
    "discover_devices", "get_device_state", "get_area_devices", "get_states",
    "call_service", "restart_homeassistant",
    "read_file", "write_file", "list_directory", "delete_file",
    "create_directory", "move_file", "copy_file", "search_files", "get_directory_tree",
    "list_automations", "trigger_automation", "create_automation",
    "update_automation", "delete_automation", "get_automation_details",
    "enable_disable_automation",
    "create_scene", "activate_scene", "list_scenes",
    "vacuum_control", "fan_control", "camera_snapshot", "media_player_control",
    "execute_python", "analyze_states_dataframe", "plot_sensor_history",
    "list_addons", "get_addon_info", "start_addon", "stop_addon",
    "restart_addon", "install_addon", "uninstall_addon", "update_addon", "get_addon_logs",
    "get_entity_history", "get_system_logs", "get_error_log",
    "diagnose_entity", "get_statistics", "get_binary_sensor",
    "list_dashboards", "get_dashboard_config", "create_dashboard",
    "update_dashboard_config", "delete_dashboard", "list_hacs_cards",
    "create_button_card", "create_mushroom_card",
    "analyze_home_context", "activity_recognition", "comfort_optimization", "energy_intelligence",
    "intelligent_security_monitor", "anomaly_detection", "vacation_mode",
    "analyze_camera_vlm", "object_detection", "facial_recognition",
    "get_entity_state", "list_entities", "get_services",
    "fire_event", "render_template", "get_config",
    "get_history", "get_logbook",
    "get_persistent_notifications",
    "get_integration_status", "get_startup_errors",
]

def fix_decorators(file_path: Path):
    """Add ha_ prefix to @app.post() and @app.get() route paths"""
    
    content = file_path.read_text(encoding='utf-8')
    changes = []
    
    for endpoint in ENDPOINTS:
        # Fix POST routes
        old_pattern = f'@app.post("/{endpoint}"'
        new_pattern = f'@app.post("/ha_{endpoint}"'
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            changes.append(f"POST /{endpoint} → /ha_{endpoint}")
        
        # Fix GET routes
        old_pattern_get = f'@app.get("/{endpoint}"'
        new_pattern_get = f'@app.get("/ha_{endpoint}"'
        if old_pattern_get in content:
            content = content.replace(old_pattern_get, new_pattern_get)
            changes.append(f"GET /{endpoint} → /ha_{endpoint}")
    
    if changes:
        file_path.write_text(content, encoding='utf-8')
        print(f"\n✅ Fixed {len(changes)} route decorators:")
        for change in changes[:10]:  # Show first 10
            print(f"  {change}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more")
        return len(changes)
    
    return 0

if __name__ == "__main__":
    server_path = Path(__file__).parent / "server.py"
    
    if not server_path.exists():
        print(f"❌ {server_path} not found")
        exit(1)
    
    # Create backup
    backup = server_path.with_suffix('.py.backup-decorators')
    backup.write_text(server_path.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"💾 Backup: {backup.name}")
    
    # Fix decorators
    count = fix_decorators(server_path)
    
    if count > 0:
        print(f"\n🎉 SUCCESS! Fixed {count} route decorators")
        print(f"📝 All endpoints now have ha_ prefix in routes")
    else:
        print("\n⚠️  No changes made - decorators already correct")
