#!/usr/bin/env python3
"""
Quick test to verify server.py can be imported and tools are accessible
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test that server.py can be imported"""
    print("🧪 Testing server.py import...")
    try:
        import server
        print("✅ Server module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tool_functions():
    """Test that tool definition functions exist"""
    print("\n🧪 Testing tool definition functions...")
    try:
        import server
        
        # Check Part 1
        tools1 = server.get_part1_tools()
        print(f"✅ Part 1: {len(tools1)} tools loaded")
        
        # Check Part 2
        tools2 = server.get_part2_tools()
        print(f"✅ Part 2: {len(tools2)} tools loaded")
        
        # Check Part 3
        tools3 = server.get_part3_dashboard_tools()
        print(f"✅ Part 3: {len(tools3)} tools loaded")
        
        total = len(tools1) + len(tools2) + len(tools3)
        print(f"\n📊 Total converted tools: {total}")
        
        return True
    except Exception as e:
        print(f"❌ Tool function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_names():
    """Test that we can extract tool names"""
    print("\n🧪 Testing tool name extraction...")
    try:
        import server
        
        tools1 = server.get_part1_tools()
        tools2 = server.get_part2_tools()
        tools3 = server.get_part3_dashboard_tools()
        
        all_tools = tools1 + tools2 + tools3
        
        # Extract names
        tool_names = [tool.name for tool in all_tools]
        
        print(f"\n📋 Sample Tool Names (first 10):")
        for name in tool_names[:10]:
            print(f"   • {name}")
        
        print(f"\n✅ All {len(tool_names)} tool names extracted successfully")
        
        # Check for duplicates
        duplicates = [name for name in set(tool_names) if tool_names.count(name) > 1]
        if duplicates:
            print(f"⚠️  Warning: Duplicate tool names found: {duplicates}")
        else:
            print("✅ No duplicate tool names")
        
        return True
    except Exception as e:
        print(f"❌ Tool name extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("  HOME ASSISTANT MCP SERVER - VALIDATION TEST")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_import()))
    results.append(("Tool Functions Test", test_tool_functions()))
    results.append(("Tool Names Test", test_tool_names()))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Server is ready to deploy.")
        print("\n📝 Next steps:")
        print("   1. Copy server.py to your HA add-on directory")
        print("   2. Update addon config with required environment variables")
        print("   3. Restart the add-on")
        print("   4. Connect via Open-WebUI or MCPO")
        print("   5. Test tool access")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
