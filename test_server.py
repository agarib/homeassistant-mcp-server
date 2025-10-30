#!/usr/bin/env python3
"""
Test script for Home Assistant OpenAPI Server v2.0
Tests basic connectivity and core endpoints
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Server configuration
BASE_URL = "http://192.168.1.203:8001"  # Change to your HA IP

async def test_endpoint(client: httpx.AsyncClient, endpoint: str, data: Dict[str, Any], description: str):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: POST {endpoint}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    print(f"{'='*60}")
    
    try:
        response = await client.post(f"{BASE_URL}{endpoint}", json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            print(f"Response: {json.dumps(result, indent=2)[:500]}...")  # First 500 chars
            return True
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Home Assistant OpenAPI Server v2.0 Test Suite")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = []
        
        # Test 1: Health Check
        print("\n\n📊 TEST 1: Health Check")
        try:
            response = await client.get(f"{BASE_URL}/health")
            health = response.json()
            print(f"✅ Server is healthy: {health}")
            results.append(True)
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            results.append(False)
            return  # Can't continue if server is down
        
        # Test 2: Get States (basic query)
        results.append(await test_endpoint(
            client,
            "/get_states",
            {"domain": "light", "limit": 5},
            "Get Light States"
        ))
        
        # Test 3: Discover Devices
        results.append(await test_endpoint(
            client,
            "/discover_devices",
            {"domain": "light"},
            "Discover Light Devices"
        ))
        
        # Test 4: Get Area Devices
        results.append(await test_endpoint(
            client,
            "/get_area_devices",
            {"area_name": "living room"},
            "Get Living Room Devices"
        ))
        
        # Test 5: Get Device State
        results.append(await test_endpoint(
            client,
            "/get_device_state",
            {"entity_id": "sun.sun"},
            "Get Sun State (always exists)"
        ))
        
        # Test 6: List Directory
        results.append(await test_endpoint(
            client,
            "/list_directory",
            {"dirpath": ""},
            "List /config Root Directory"
        ))
        
        # Test 7: List Automations
        results.append(await test_endpoint(
            client,
            "/list_automations",
            {"enabled_only": False},
            "List All Automations"
        ))
        
        # Test 8: List Scenes
        results.append(await test_endpoint(
            client,
            "/list_scenes",
            {},
            "List All Scenes"
        ))
        
        # Test 9: Call Service (safe - just get config)
        results.append(await test_endpoint(
            client,
            "/call_service",
            {
                "domain": "homeassistant",
                "service": "update_entity",
                "entity_id": "sun.sun"
            },
            "Call Service (Update Entity)"
        ))
        
        # Test 10: OpenAPI Spec
        print(f"\n\n📊 TEST 10: OpenAPI Spec")
        try:
            response = await client.get(f"{BASE_URL}/openapi.json")
            spec = response.json()
            paths = list(spec.get("paths", {}).keys())
            print(f"✅ OpenAPI spec retrieved")
            print(f"Total endpoints: {len(paths)}")
            print(f"Sample paths: {paths[:10]}")
            results.append(True)
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append(False)
        
        # Summary
        print(f"\n\n{'='*60}")
        print(f"📈 TEST SUMMARY")
        print(f"{'='*60}")
        passed = sum(results)
        total = len(results)
        print(f"Passed: {passed}/{total}")
        print(f"Failed: {total - passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print(f"\n✅ ALL TESTS PASSED! Server is working correctly.")
        else:
            print(f"\n⚠️ Some tests failed. Check logs above.")


if __name__ == "__main__":
    asyncio.run(main())
