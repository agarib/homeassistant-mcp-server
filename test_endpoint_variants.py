#!/usr/bin/env python3
"""Test endpoints that cloud AI might have tried (without ha_ prefix or without _native)"""

import requests

BASE_URL = "http://192.168.1.203:8001"

# Test endpoints that cloud AI might have tried incorrectly
test_variants = [
    # Without ha_ prefix
    ("/get_services", {}),
    ("/get_entity_state", {"entity_id": "light.couch_light"}),
    ("/list_entities", {}),
    
    # Without _native suffix  
    ("/ha_get_services", {}),
    ("/ha_get_entity_state", {"entity_id": "light.couch_light"}),
    ("/ha_list_entities", {}),
    
    # Correct versions
    ("/ha_get_services_native", {}),
    ("/ha_get_entity_state_native", {"entity_id": "light.couch_light"}),
    ("/ha_list_entities_native", {}),
]

print("Testing endpoint variants...")
print("=" * 80)

for endpoint, payload in test_variants:
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload, timeout=5)
        status = response.status_code
        
        if status == 404:
            print(f"❌ 404: {endpoint}")
        elif status == 200:
            print(f"✅ 200: {endpoint}")
        elif status == 405:
            print(f"⚠️  405 Method Not Allowed: {endpoint}")
        else:
            print(f"⚠️  {status}: {endpoint}")
            
    except Exception as e:
        print(f"💥 ERROR: {endpoint} - {e}")

print("=" * 80)
print("\n📋 Checking /docs to see all registered endpoints...")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if response.status_code == 200:
        print("✅ OpenAPI docs accessible at /docs")
except:
    pass

# Check OpenAPI spec  
try:
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if response.status_code == 200:
        spec = response.json()
        print(f"\n📊 Total endpoints in OpenAPI spec: {len(spec.get('paths', {}))}")
        
        # Check for specific endpoints
        paths = spec.get('paths', {})
        print("\n🔍 Checking specific endpoint existence:")
        for check_path in ["/ha_get_services", "/ha_get_services_native", "/ha_get_entity_state", "/ha_get_entity_state_native"]:
            if check_path in paths:
                print(f"  ✅ {check_path} exists in spec")
            else:
                print(f"  ❌ {check_path} NOT in spec")
except Exception as e:
    print(f"Error checking OpenAPI spec: {e}")
