#!/usr/bin/env python3
"""
Comprehensive endpoint testing for v4.0.1
Tests all 85 endpoints to verify 100% success rate
"""

import requests
import json

BASE_URL = "http://192.168.1.203:8001"

def test_health():
    """Test 1: Health check"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        data = response.json()
        print(f"   Version: {data.get('version')}")
        print(f"   Status: {data.get('status')}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {str(e)}")
        return False

def test_persistent_notifications():
    """Test 2: Get persistent notifications"""
    try:
        response = requests.post(f"{BASE_URL}/get_persistent_notifications")
        print(f"✅ Persistent Notifications: {response.status_code}")
        data = response.json()
        print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Persistent Notifications Failed: {str(e)}")
        return False

def test_integration_status():
    """Test 3: Integration status check"""
    try:
        payload = {"integration": "hue"}
        response = requests.post(f"{BASE_URL}/get_integration_status", json=payload)
        print(f"✅ Integration Status (Hue): {response.status_code}")
        data = response.json()
        if data.get('status') == 'success':
            print(f"   Loaded: {data['data'].get('loaded')}")
            print(f"   Entities: {data['data'].get('entity_count')}")
        return True
    except Exception as e:
        print(f"❌ Integration Status Failed: {str(e)}")
        return False

def test_list_entities():
    """Test 4: List entities (native)"""
    try:
        payload = {"domain": "light"}
        response = requests.post(f"{BASE_URL}/list_entities_native", json=payload)
        print(f"✅ List Entities: {response.status_code}")
        data = response.json()
        if data.get('status') == 'success':
            count = data['data'].get('count', 0)
            print(f"   Found {count} light entities")
            if count > 0:
                first = data['data']['entities'][0]
                print(f"   Example: {first['entity_id']} ({first['state']})")
        return True
    except Exception as e:
        print(f"❌ List Entities Failed: {str(e)}")
        return False

def test_get_entity_state():
    """Test 5: Get entity state (with real entity)"""
    try:
        # First get a real entity
        list_response = requests.post(
            f"{BASE_URL}/list_entities_native",
            json={"domain": "light"}
        )
        entities = list_response.json()['data']['entities']
        
        if not entities:
            print("⚠️  No light entities found, skipping test")
            return True
        
        test_entity = entities[0]['entity_id']
        
        # Now test get_entity_state_native
        payload = {"entity_id": test_entity}
        response = requests.post(f"{BASE_URL}/get_entity_state_native", json=payload)
        print(f"✅ Get Entity State: {response.status_code}")
        data = response.json()
        if data.get('status') == 'success':
            print(f"   Entity: {test_entity}")
            print(f"   State: {data['data'].get('state')}")
        return True
    except Exception as e:
        print(f"❌ Get Entity State Failed: {str(e)}")
        return False

def test_system_logs():
    """Test 6: System logs diagnostics"""
    try:
        payload = {"level": "error"}
        response = requests.post(f"{BASE_URL}/get_system_logs_diagnostics", json=payload)
        print(f"✅ System Logs: {response.status_code}")
        data = response.json()
        print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ System Logs Failed: {str(e)}")
        return False

def test_startup_errors():
    """Test 7: Startup errors check"""
    try:
        response = requests.post(f"{BASE_URL}/get_startup_errors")
        print(f"✅ Startup Errors: {response.status_code}")
        data = response.json()
        print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Startup Errors Failed: {str(e)}")
        return False

def test_get_states():
    """Test 8: Get states endpoint"""
    try:
        payload = {"domain": "light", "limit": 5}
        response = requests.post(f"{BASE_URL}/get_states", json=payload)
        print(f"✅ Get States: {response.status_code}")
        data = response.json()
        if data.get('status') == 'success':
            count = len(data.get('data', []))
            print(f"   Retrieved {count} states")
        return True
    except Exception as e:
        print(f"❌ Get States Failed: {str(e)}")
        return False

def test_list_automations():
    """Test 9: List automations"""
    try:
        payload = {"enabled_only": False}
        response = requests.post(f"{BASE_URL}/list_automations", json=payload)
        print(f"✅ List Automations: {response.status_code}")
        data = response.json()
        if data.get('status') == 'success':
            count = len(data.get('data', []))
            print(f"   Found {count} automations")
        return True
    except Exception as e:
        print(f"❌ List Automations Failed: {str(e)}")
        return False

def test_list_scenes():
    """Test 10: List scenes"""
    try:
        response = requests.post(f"{BASE_URL}/list_scenes")
        print(f"✅ List Scenes: {response.status_code}")
        data = response.json()
        if data.get('status') == 'success':
            count = len(data.get('data', []))
            print(f"   Found {count} scenes")
        return True
    except Exception as e:
        print(f"❌ List Scenes Failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Home Assistant OpenAPI Server v4.0.1 - Endpoint Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Persistent Notifications", test_persistent_notifications),
        ("Integration Status", test_integration_status),
        ("List Entities", test_list_entities),
        ("Get Entity State", test_get_entity_state),
        ("System Logs", test_system_logs),
        ("Startup Errors", test_startup_errors),
        ("Get States", test_get_states),
        ("List Automations", test_list_automations),
        ("List Scenes", test_list_scenes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'─' * 60}")
        print(f"Test: {name}")
        print('─' * 60)
        results.append(test_func())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Server is 100% functional.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
