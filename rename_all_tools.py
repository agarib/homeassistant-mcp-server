#!/usr/bin/env python3
"""
Script to rename all Home Assistant OpenAPI Server endpoints with ha_ prefix
This ensures no conflicts with Open-WebUI built-in tools
"""

import re
from pathlib import Path

# List of all endpoints to rename (excluding /health and / which are standard)
ENDPOINTS_TO_RENAME = [
    # Device Control
    "control_light", "control_switch", "control_climate", "control_cover",
    
    # Discovery
    "discover_devices", "get_device_state", "get_area_devices", "get_states",
    
    # System
    "call_service", "restart_homeassistant",
    
    # File Operations (9 tools)
    "read_file", "write_file", "list_directory", "delete_file",
    "create_directory", "move_file", "copy_file", "search_files", "get_directory_tree",
    
    # Automations (7 tools)
    "list_automations", "trigger_automation", "create_automation",
    "update_automation", "delete_automation", "get_automation_details",
    "enable_disable_automation",
    
    # Scenes
    "create_scene", "activate_scene", "list_scenes",
    
    # Media & Devices
    "vacuum_control", "fan_control", "camera_snapshot", "media_player_control",
    
    # Code Execution
    "execute_python", "analyze_states_dataframe", "plot_sensor_history",
    
    # Add-ons (9 tools)
    "list_addons", "get_addon_info", "start_addon", "stop_addon",
    "restart_addon", "install_addon", "uninstall_addon", "update_addon", "get_addon_logs",
    
    # Logs & History (6 tools)
    "get_entity_history", "get_system_logs", "get_error_log",
    "diagnose_entity", "get_statistics", "get_binary_sensor",
    
    # Dashboards (8 tools)
    "list_dashboards", "get_dashboard_config", "create_dashboard",
    "update_dashboard_config", "delete_dashboard", "list_hacs_cards",
    "create_button_card", "create_mushroom_card",
    
    # Intelligence (4 tools)
    "analyze_home_context", "activity_recognition", "comfort_optimization", "energy_intelligence",
    
    # Security (3 tools)
    "intelligent_security_monitor", "anomaly_detection", "vacation_mode",
    
    # Camera VLM (3 tools)
    "analyze_camera_vlm", "object_detection", "facial_recognition",
    
    # Native MCPO (8 tools) - already have _native suffix, rename to ha_
    "get_entity_state_native", "list_entities_native", "get_services_native",
    "fire_event_native", "render_template_native", "get_config_native",
    "get_history_native", "get_logbook_native",
    
    # System Diagnostics (4 tools) - already have _diagnostics suffix, rename to ha_
    "get_system_logs_diagnostics", "get_persistent_notifications",
    "get_integration_status", "get_startup_errors",
]

def rename_endpoints(file_path: Path):
    """Rename all endpoints in server.py with ha_ prefix - ONLY FastAPI route handlers"""
    
    print(f"📝 Reading {file_path}")
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    lines = content.split('\n')
    
    # Track changes
    changes = []
    modified_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        modified = False
        
        # Check if this line is a FastAPI route decorator
        for endpoint in ENDPOINTS_TO_RENAME:
            # Pattern: @app.post("/endpoint" or @app.get("/endpoint"
            if f'@app.post("/{endpoint}"' in line or f'@app.get("/{endpoint}"' in line:
                # New name: ha_ + endpoint (without _native or _diagnostics suffix)
                clean_name = endpoint.replace("_native", "").replace("_diagnostics", "")
                new_name = f"ha_{clean_name}"
                
                # Rename the route
                old_line = line
                line = line.replace(f'@app.post("/{endpoint}"', f'@app.post("/{new_name}"')
                line = line.replace(f'@app.get("/{endpoint}"', f'@app.get("/{new_name}"')
                
                # Rename the function on the next line (it should be: async def endpoint(...))
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if f'async def {endpoint}(' in next_line:
                        lines[i + 1] = next_line.replace(f'async def {endpoint}(', f'async def {new_name}(')
                        changes.append(f"  /{endpoint} → /{new_name}")
                        modified = True
                
                break
        
        modified_lines.append(line)
        i += 1
    
    # Rejoin lines
    if modified:
        content = '\n'.join(lines)
    
    if content != original_content:
        print(f"\n✅ Found {len(changes)} endpoints to rename:\n")
        for change in changes:
            print(change)
        
        # Write updated content
        file_path.write_text(content, encoding='utf-8')
        print(f"\n✅ Updated {file_path}")
        print(f"📊 Total changes: {len(changes)} endpoints renamed")
        
        return len(changes)
    else:
        print("⚠️  No changes made")
        return 0

def update_version(file_path: Path):
    """Update version to 4.0.3"""
    content = file_path.read_text(encoding='utf-8')
    
    # Update version string
    content = re.sub(
        r'__version__ = "4\.0\.2"',
        '__version__ = "4.0.3"',
        content
    )
    
    # Update module docstring
    content = re.sub(
        r'Version: 4\.0\.2',
        'Version: 4.0.3',
        content
    )
    
    # Update endpoint count description
    content = re.sub(
        r'Home Assistant OpenAPI Server v4\.0\.2',
        'Home Assistant OpenAPI Server v4.0.3',
        content
    )
    
    file_path.write_text(content, encoding='utf-8')
    print("\n✅ Updated version to 4.0.3")

if __name__ == "__main__":
    server_path = Path(__file__).parent / "server.py"
    
    if not server_path.exists():
        print(f"❌ Error: {server_path} not found")
        exit(1)
    
    print("🚀 Home Assistant OpenAPI Server - Tool Renaming Script")
    print("=" * 70)
    print(f"\n📂 File: {server_path}")
    print(f"🔧 Adding 'ha_' prefix to {len(ENDPOINTS_TO_RENAME)} endpoints\n")
    
    # Create backup
    backup_path = server_path.with_suffix('.py.backup-v4.0.2')
    backup_path.write_text(server_path.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"💾 Backup created: {backup_path}\n")
    
    # Rename endpoints
    changes_made = rename_endpoints(server_path)
    
    if changes_made > 0:
        # Update version
        update_version(server_path)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! All endpoints renamed to ha_* format")
        print("=" * 70)
        print(f"\n📋 Summary:")
        print(f"  • {changes_made} endpoints renamed")
        print(f"  • Version updated to 4.0.3")
        print(f"  • Backup saved to {backup_path.name}")
        print(f"\n🎯 Next steps:")
        print(f"  1. Review changes: diff {backup_path.name} server.py")
        print(f"  2. Test locally: python server.py")
        print(f"  3. Deploy to HA add-on")
        print(f"  4. Update Open-WebUI configuration")
    else:
        print("\n⚠️  No changes were made - endpoints may already be renamed")
