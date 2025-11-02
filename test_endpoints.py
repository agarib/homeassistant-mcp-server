#!/usr/bin/env python3
"""Quick test to check which endpoints return 404"""

import requests
import json

BASE_URL = "http://192.168.1.203:8001"

# Test these specific endpoints that cloud AI mentioned
test_endpoints = [
    # File operations (working according to cloud AI)
    ("/ha_read_file", {"filepath": "configuration.yaml"}),
    ("/ha_list_directory", {"dirpath": "packages"}),
    
    # Native endpoints (failing according to cloud AI)
    ("/ha_get_services_native", {}),
    ("/ha_get_entity_state_native", {"entity_id": "light.couch_light"}),
    ("/ha_list_entities_native", {}),
    ("/ha_get_config_native", {}),
    
    # Add-on endpoints
    ("/ha_list_addons", {}),
    ("/ha_get_addon_info", {"addon_slug": "core_mosquitto"}),
]

print("Testing endpoints...")
print("=" * 80)

for endpoint, payload in test_endpoints:
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload, timeout=5)
        status = response.status_code
        
        if status == 404:
            print(f"❌ 404 NOT FOUND: {endpoint}")
        elif status == 200:
            print(f"✅ {status} OK: {endpoint}")
        else:
            print(f"⚠️  {status}: {endpoint} - {response.text[:100]}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 ERROR: {endpoint} - {e}")
        
print("=" * 80)
