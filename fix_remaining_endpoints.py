#!/usr/bin/env python3
"""
Fix remaining endpoints that escaped renaming:
- Native MCPO tools with _native suffix
- Diagnostics tools with _diagnostics suffix
"""

from pathlib import Path

# Endpoints that need ha_ prefix
REMAINING_ENDPOINTS = [
    "get_entity_state_native",
    "list_entities_native",
    "get_services_native",
    "fire_event_native",
    "render_template_native",
    "get_config_native",
    "get_history_native",
    "get_logbook_native",
    "get_system_logs_diagnostics",
]

def fix_remaining(file_path: Path):
    """Add ha_ prefix to remaining endpoints"""
    
    content = file_path.read_text(encoding='utf-8')
    changes = []
    
    for endpoint in REMAINING_ENDPOINTS:
        old_pattern = f'@app.post("/{endpoint}"'
        new_pattern = f'@app.post("/ha_{endpoint}"'
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            changes.append(f"/{endpoint} → /ha_{endpoint}")
    
    if changes:
        file_path.write_text(content, encoding='utf-8')
        print(f"\n✅ Fixed {len(changes)} remaining endpoints:")
        for change in changes:
            print(f"  {change}")
        return len(changes)
    else:
        print("⚠️  No changes needed (all endpoints already have ha_ prefix)")
        return 0

if __name__ == "__main__":
    server_path = Path(__file__).parent / "server.py"
    
    if not server_path.exists():
        print(f"❌ {server_path} not found")
        exit(1)
    
    # Create backup
    backup = server_path.with_suffix('.py.backup-remaining')
    backup.write_text(server_path.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"💾 Backup: {backup.name}")
    
    # Fix endpoints
    count = fix_remaining(server_path)
    
    if count > 0:
        print(f"\n🎉 SUCCESS! Fixed {count} endpoints")
        print("📝 All endpoints now have ha_ prefix")
    else:
        print("\n✅ Nothing to fix")
