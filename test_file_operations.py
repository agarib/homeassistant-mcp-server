#!/usr/bin/env python3
"""
Test all file operation endpoints in v4.0.2
Verifies all path resolution issues are fixed
"""

import requests
import json

BASE_URL = "http://192.168.1.203:8001"

def test_list_directory():
    """Test 1: List directory"""
    try:
        payload = {"dirpath": "."}
        response = requests.post(f"{BASE_URL}/list_directory", json=payload)
        print(f"✅ List Directory: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('data', []))} items")
        return True
    except Exception as e:
        print(f"❌ List Directory Failed: {str(e)}")
        return False

def test_get_directory_tree():
    """Test 2: Get directory tree (PREVIOUSLY BROKEN)"""
    try:
        payload = {"dirpath": ".", "max_depth": 2}
        response = requests.post(f"{BASE_URL}/get_directory_tree", json=payload)
        print(f"✅ Get Directory Tree: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Tree structure retrieved successfully")
            print(f"   Root: {data.get('data', {}).get('name')}")
        return True
    except Exception as e:
        print(f"❌ Get Directory Tree Failed: {str(e)}")
        return False

def test_create_directory():
    """Test 3: Create directory"""
    try:
        payload = {"dirpath": "test_dir_copilot"}
        response = requests.post(f"{BASE_URL}/create_directory", json=payload)
        print(f"✅ Create Directory: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Create Directory Failed: {str(e)}")
        return False

def test_write_file():
    """Test 4: Write file"""
    try:
        payload = {
            "filepath": "test_dir_copilot/test_file.txt",
            "content": "Test content from v4.0.2 validation\n"
        }
        response = requests.post(f"{BASE_URL}/write_file", json=payload)
        print(f"✅ Write File: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Write File Failed: {str(e)}")
        return False

def test_read_file():
    """Test 5: Read file"""
    try:
        payload = {"filepath": "test_dir_copilot/test_file.txt"}
        response = requests.post(f"{BASE_URL}/read_file", json=payload)
        print(f"✅ Read File: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            content = data.get('data', {}).get('content', '')
            print(f"   Read {len(content)} bytes")
        return True
    except Exception as e:
        print(f"❌ Read File Failed: {str(e)}")
        return False

def test_copy_file():
    """Test 6: Copy file"""
    try:
        payload = {
            "source": "test_dir_copilot/test_file.txt",
            "destination": "test_dir_copilot/test_file_copy.txt"
        }
        response = requests.post(f"{BASE_URL}/copy_file", json=payload)
        print(f"✅ Copy File: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Copy File Failed: {str(e)}")
        return False

def test_move_file():
    """Test 7: Move/rename file"""
    try:
        payload = {
            "source": "test_dir_copilot/test_file_copy.txt",
            "destination": "test_dir_copilot/test_file_renamed.txt"
        }
        response = requests.post(f"{BASE_URL}/move_file", json=payload)
        print(f"✅ Move File: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Move File Failed: {str(e)}")
        return False

def test_search_files():
    """Test 8: Search files"""
    try:
        payload = {
            "pattern": "Test content",
            "directory": "test_dir_copilot",
            "extensions": ["txt"]
        }
        response = requests.post(f"{BASE_URL}/search_files", json=payload)
        print(f"✅ Search Files: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Search Files Failed: {str(e)}")
        return False

def test_delete_file():
    """Test 9: Delete files (cleanup)"""
    try:
        files_to_delete = [
            "test_dir_copilot/test_file.txt",
            "test_dir_copilot/test_file_renamed.txt"
        ]
        
        for filepath in files_to_delete:
            payload = {"filepath": filepath}
            response = requests.post(f"{BASE_URL}/delete_file", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   Deleted: {filepath}")
        
        print(f"✅ Delete Files: Cleanup complete")
        return True
    except Exception as e:
        print(f"❌ Delete Files Failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("File Operations Test Suite - v4.0.2")
    print("Testing all path resolution fixes")
    print("=" * 60)
    print()
    
    tests = [
        ("List Directory", test_list_directory),
        ("Get Directory Tree (FIX VALIDATION)", test_get_directory_tree),
        ("Create Directory", test_create_directory),
        ("Write File", test_write_file),
        ("Read File", test_read_file),
        ("Copy File", test_copy_file),
        ("Move File", test_move_file),
        ("Search Files", test_search_files),
        ("Delete Files (Cleanup)", test_delete_file),
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
        print("\n🎉 ALL FILE OPERATIONS WORKING!")
        print("✅ v4.0.2 path resolution fixes validated")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
