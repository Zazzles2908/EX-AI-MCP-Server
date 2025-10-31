#!/usr/bin/env python3
"""Test Phase 2.4.3 Dashboard Endpoints"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_endpoint(method, endpoint, description):
    """Test a single endpoint"""
    print(f"\n📋 Testing: {description}")
    print(f"   {method.upper()} {endpoint}")
    
    try:
        if method == "get":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        elif method == "post":
            response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
        else:
            print(f"   ❌ Unknown method: {method}")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                print(f"   ✅ PASSED")
                return True
            except:
                print(f"   Response: {response.text[:200]}...")
                print(f"   ✅ PASSED (non-JSON)")
                return True
        else:
            print(f"   Response: {response.text[:200]}...")
            print(f"   ❌ FAILED")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection refused - is the server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all endpoint tests"""
    print("=" * 60)
    print("Phase 2.4.3 Dashboard Endpoints Test")
    print("=" * 60)
    
    # Wait for server to be ready
    print("\n⏳ Waiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/status", timeout=1)
            if response.status_code == 200:
                print("✅ Server is ready")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("❌ Server not responding")
        return
    
    # Test endpoints
    results = []
    
    results.append(test_endpoint("get", "/status", "Status endpoint"))
    results.append(test_endpoint("get", "/flags/status", "Get flags status"))
    results.append(test_endpoint("get", "/health/flags", "Get flags health check"))
    results.append(test_endpoint("get", "/metrics/validation", "Get validation metrics"))
    results.append(test_endpoint("get", "/metrics/adapter", "Get adapter metrics"))
    results.append(test_endpoint("post", "/metrics/flush", "Manual metrics flush"))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

