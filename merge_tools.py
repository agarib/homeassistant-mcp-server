#!/usr/bin/env python3
"""
Script to merge all converted tool parts into main server.py
This creates a complete server.py with all 74 tools
"""

import re
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
SERVER_FILE = BASE_DIR / "server.py"
PART1_FILE = BASE_DIR / "server-converted-part1.py"
PART2_FILE = BASE_DIR / "server-converted-part2.py"
PART3_FILE = BASE_DIR / "server-converted-part3-dashboards.py"
OUTPUT_FILE = BASE_DIR / "server-complete.py"

def extract_function(filepath: Path, function_name: str) -> str:
    """Extract a complete function definition from a file"""
    content = filepath.read_text(encoding='utf-8')
    
    # Find function start
    pattern = rf'^(def {function_name}\([^)]*\).*?:)'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        return ""
    
    start_pos = match.start()
    lines = content[start_pos:].split('\n')
    
    # Find function end (next def or end of file)
    function_lines = [lines[0]]  # First line
    indent_level = len(lines[0]) - len(lines[0].lstrip())
    
    for i, line in enumerate(lines[1:], 1):
        # Stop at next function at same or lower indent level
        if line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.strip().startswith('#'):
            if line.startswith('def ') or line.startswith('class ') or line.startswith('async def '):
                break
        function_lines.append(line)
    
    return '\n'.join(function_lines)

def main():
    print("🔧 Merging all tool parts into complete server.py...")
    
    # Read base server.py
    base_content = SERVER_FILE.read_text(encoding='utf-8')
    
    # Extract tool definition functions from each part
    print("📦 Extracting tool definitions from Part 1...")
    part1_tools_func = extract_function(PART1_FILE, "get_part1_tools")
    
    print("📦 Extracting tool definitions from Part 2...")
    part2_tools_func = extract_function(PART2_FILE, "get_part2_tools")
    
    print("📦 Extracting tool definitions from Part 3...")
    part3_tools_func = extract_function(PART3_FILE, "get_part3_dashboard_tools")
    
    # Extract handler functions
    print("🔨 Extracting tool handlers from Part 1...")
    part1_handlers_func = extract_function(PART1_FILE, "handle_part1_tools")
    
    print("🔨 Extracting tool handlers from Part 2...")
    part2_handlers_func = extract_function(PART2_FILE, "handle_part2_tools")
    
    print("🔨 Extracting tool handlers from Part 3...")
    part3_handlers_func = extract_function(PART3_FILE, "handle_part3_dashboard_tools")
    
    # Insert helper functions before list_tools
    helper_functions = f"""

# ============================================================================
# TOOL DEFINITIONS FROM CONVERTED PARTS
# ============================================================================

{part1_tools_func}


{part2_tools_func}


{part3_tools_func}


# ============================================================================
# TOOL HANDLERS FROM CONVERTED PARTS
# ============================================================================

{part1_handlers_func}


{part2_handlers_func}


{part3_handlers_func}

"""
    
    # Find where to insert (before @app.list_tools())
    list_tools_pos = base_content.find('@app.list_tools()')
    
    if list_tools_pos == -1:
        print("❌ Could not find @app.list_tools() decorator")
        return
    
    # Insert helper functions
    output_content = base_content[:list_tools_pos] + helper_functions + '\n' + base_content[list_tools_pos:]
    
    # Now modify the list_tools function to include all tools
    # Find the return [ line
    pattern = r'(@app\.list_tools\(\)\nasync def list_tools\(\) -> list\[Tool\]:.*?return \[)'
    match = re.search(pattern, output_content, re.DOTALL)
    
    if match:
        # Add tool calls after "return ["
        insertion_point = match.end()
        
        new_tools = """
        # ===================================================================
        # CONVERTED TOOLS FROM PART 1: Discovery, Control, Lighting, Media, Climate
        # ===================================================================
        *get_part1_tools(),
        
        # ===================================================================
        # CONVERTED TOOLS FROM PART 2: Security, Automation, Workflows, Intelligence
        # ===================================================================
        *get_part2_tools(),
        
        # ===================================================================
        # CONVERTED TOOLS FROM PART 3: Dashboard & HACS Management
        # ===================================================================
        *get_part3_dashboard_tools(),
        
        # ===================================================================
        # ORIGINAL NATIVE ADD-ON TOOLS (File & API Operations)
        # ===================================================================
"""
        
        output_content = output_content[:insertion_point] + new_tools + output_content[insertion_point:]
    
    # Now modify call_tool to include all handlers
    # Find the call_tool function's try block and add handler calls at the end before the final else
    call_tool_pattern = r'(elif name == "call_service":.*?return \[TextContent\(type="text", text=json\.dumps\(result, indent=2\)\)\])\s+(else:\s+raise ValueError)'
    
    handler_calls = r'''\1
        
        # ===================================================================
        # CONVERTED TOOL HANDLERS - Try all three parts
        # ===================================================================
        else:
            # Try Part 1 handlers
            result = await handle_part1_tools(name, arguments, ha_api, file_mgr)
            if result is not None:
                return result
            
            # Try Part 2 handlers
            result = await handle_part2_tools(name, arguments, ha_api, file_mgr)
            if result is not None:
                return result
            
            # Try Part 3 handlers
            result = await handle_part3_dashboard_tools(name, arguments, ha_api, file_mgr)
            if result is not None:
                return result
            
            # Unknown tool
            \2'''
    
    output_content = re.sub(call_tool_pattern, handler_calls, output_content, flags=re.DOTALL)
    
    # Write output
    OUTPUT_FILE.write_text(output_content, encoding='utf-8')
    
    print(f"\n✅ Successfully created {OUTPUT_FILE.name}")
    print(f"📊 File size: {OUTPUT_FILE.stat().st_size / 1024:.2f} KB")
    print("\n📋 Summary:")
    print("   - File Operations: 9 tools")
    print("   - Basic HA API: 3 tools")
    print("   - Part 1 (Discovery/Control/Lighting/Media/Climate): 18 tools")
    print("   - Part 2 (Security/Automation/Workflows/Intelligence): 35 tools")
    print("   - Part 3 (Dashboard/HACS Management): 9 tools")
    print("   " + "="*50)
    print("   TOTAL: 74 TOOLS! 🎉")
    print(f"\n💡 Review {OUTPUT_FILE.name} and then replace server.py if it looks good.")

if __name__ == "__main__":
    main()
