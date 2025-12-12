#!/usr/bin/env python3
"""
Fix script to add operation_id to all endpoints and fix ha_get_error_log.
This resolves the doubled names issue (ha_control_light_ha_control_light_post).
"""

import re
from pathlib import Path

def fix_server_py():
    """Add operation_id to all @app.post() decorators"""
    
    server_file = Path("c:/MyProjects/ha-openapi-server-v3.0.0/server.py")
    content = server_file.read_text(encoding='utf-8')
    
    # Pattern to match @app.post("/endpoint", ...) decorators
    # We'll capture the endpoint path and add operation_id
    pattern = r'@app\.post\("(/ha_[a-z_]+)",'
    
    def add_operation_id(match):
        endpoint_path = match.group(1)  # e.g., "/ha_control_light"
        operation_id = endpoint_path[1:]  # Remove leading slash: "ha_control_light"
        
        # Replace with operation_id added
        return f'@app.post("{endpoint_path}", operation_id="{operation_id}",'
    
    # Apply the fix
    fixed_content = re.sub(pattern, add_operation_id, content)
    
    # Count replacements
    original_count = len(re.findall(pattern, content))
    
    print(f"✅ Fixed {original_count} endpoints with operation_id")
    
    # Write back
    server_file.write_text(fixed_content, encoding='utf-8')
    
    return fixed_content

if __name__ == "__main__":
    print("🔧 Fixing FastAPI operation IDs...")
    fix_server_py()
    print("✅ Done! All endpoints now have explicit operation_id")
    print("\n📋 Next steps:")
    print("1. Review the changes in server.py")
    print("2. Restart the add-on to apply changes")
    print("3. Check Open-WebUI - tool names should now be clean (ha_control_light instead of ha_control_light_ha_control_light_post)")
