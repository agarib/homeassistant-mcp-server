#!/usr/bin/env python3
"""Verify naming consistency after FileManager rename"""
import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all ha_ prefixed elements
routes = re.findall(r'@app\.post\("/ha_(\w+)"', content)
fm_methods = re.findall(r'async def ha_(\w+)\(self', content)
handler_funcs = re.findall(r'^async def ha_(\w+)\(request:', content, re.MULTILINE)
fm_calls = re.findall(r'file_mgr\.ha_(\w+)\(', content)

print("=" * 70)
print("NAMING CONSISTENCY VERIFICATION")
print("=" * 70)
print(f"\n✅ Routes with ha_ prefix: {len(routes)}")
print(f"✅ FileManager methods with ha_ prefix: {len(set(fm_methods))}")
print(f"✅ Handler functions with ha_ prefix: {len(handler_funcs)}")
print(f"✅ FileManager method calls with ha_ prefix: {len(set(fm_calls))}")

print(f"\n📋 FileManager Methods:")
for method in sorted(set(fm_methods)):
    print(f"   - ha_{method}()")

print(f"\n📋 FileManager Calls:")
for call in sorted(set(fm_calls)):
    print(f"   - file_mgr.ha_{call}()")

print(f"\n📋 Sample Routes:")
for route in routes[:10]:
    print(f"   - /ha_{route}")

# Check for old patterns (should be none)
old_file_mgr = re.findall(r'file_mgr\.(write_file|read_file|list_directory|delete_file|resolve_path)\(', content)
if old_file_mgr:
    print(f"\n⚠️  WARNING: Found {len(old_file_mgr)} old FileManager calls without ha_ prefix!")
    for call in set(old_file_mgr):
        print(f"   - file_mgr.{call}()")
else:
    print(f"\n✅ NO old FileManager calls found - all renamed!")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
