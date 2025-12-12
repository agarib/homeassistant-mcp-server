#!/usr/bin/env python3
"""
Smart rename script - ONLY renames FastAPI route handlers
Does NOT touch FileManager class methods
"""

from pathlib import Path
import re

# Endpoints to rename (route level only)
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
    "get_entity_state_native", "list_entities_native", "get_services_native",
    "fire_event_native", "render_template_native", "get_config_native",
    "get_history_native", "get_logbook_native",
    "get_system_logs_diagnostics", "get_persistent_notifications",
    "get_integration_status", "get_startup_errors",
]

def smart_rename(file_path: Path):
    """Only rename FastAPI route handlers, not class methods"""
    
    lines = file_path.read_text(encoding='utf-8').split('\n')
    modified_lines = []
    changes = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        renamed = False
        
        # Check if this is a FastAPI decorator line
        for endpoint in ENDPOINTS:
            decorator_pattern = f'@app.post("/{endpoint}"'
            
            if decorator_pattern in line or f'@app.get("/{endpoint}"' in line:
                # Clean up name (remove _native, _diagnostics suffixes)
                clean_name = endpoint.replace("_native", "").replace("_diagnostics", "")
                new_name = f"ha_{clean_name}"
                
                # Rename the decorator
                line = line.replace(f'@app.post("/{endpoint}"', f'@app.post("/{new_name}"')
                line = line.replace(f'@app.get("/{endpoint}"', f'@app.get("/{new_name}"')
                
                # Rename the function definition on next line (but ONLY if it's a route handler)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Match: "async def endpoint(" with possible whitespace
                    func_pattern = f'async def {endpoint}\\('
                    if re.search(func_pattern, next_line):
                        # Make sure this is NOT inside a class (class methods are indented)
                        if not next_line.startswith('    async def'):  # Class methods have 4-space indent
                            lines[i + 1] = re.sub(func_pattern, f'async def {new_name}(', next_line)
                            changes.append(f"/{endpoint} → /{new_name}")
                            renamed = True
                
                break
        
        modified_lines.append(line)
        i += 1
    
    if changes:
        # Write back
        output = '\n'.join(lines)
        file_path.write_text(output, encoding='utf-8')
        
        print(f"\n✅ Renamed {len(changes)} route handlers:")
        for change in changes:
            print(f"  {change}")
        
        return len(changes)
    
    return 0

def update_version(file_path: Path):
    """Update version strings"""
    content = file_path.read_text(encoding='utf-8')
    content = re.sub(r'__version__ = "4\.0\.2"', '__version__ = "4.0.3"', content)
    content = re.sub(r'Version: 4\.0\.2', 'Version: 4.0.3', content)
    file_path.write_text(content, encoding='utf-8')
    print("\n✅ Version updated to 4.0.3")

if __name__ == "__main__":
    server_path = Path(__file__).parent / "server.py"
    
    if not server_path.exists():
        print(f"❌ {server_path} not found")
        exit(1)
    
    # Create backup
    backup = server_path.with_suffix('.py.backup-safe')
    backup.write_text(server_path.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"💾 Backup: {backup.name}\n")
    
    # Rename
    count = smart_rename(server_path)
    
    if count > 0:
        update_version(server_path)
        print(f"\n🎉 SUCCESS! {count} route handlers renamed")
        print(f"📝 FileManager class methods unchanged (correct!)")
    else:
        print("\n⚠️  No changes made")
