#!/usr/bin/env python
"""
Test script to validate auth token handling in WebSocket daemon and shim.

This script tests:
1. Normal connection with correct token
2. Connection with wrong token (should fail gracefully)
3. Connection with empty token when daemon expects token (should fail)
4. Multiple rapid connections (stress test)
5. Connection after delay (timing test)

Usage:
    python scripts/testing/test_auth_token_validation.py
"""

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

# Bootstrap: Setup path and load environment
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root

# Load environment variables
load_env()

import websockets

# Configuration
HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
CORRECT_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WRONG_TOKEN = "wrong-token-12345"
EMPTY_TOKEN = ""


async def test_connection(token: str, test_name: str, should_succeed: bool = True) -> bool:
    """Test a single connection with given token."""
    uri = f"ws://{HOST}:{PORT}"
    try:
        async with websockets.connect(uri, max_size=20 * 1024 * 1024) as ws:
            hello = {
                "op": "hello",
                "session_id": f"test-{uuid.uuid4().hex[:6]}",
                "token": token
            }
            await ws.send(json.dumps(hello))
            
            # Wait for response with timeout
            try:
                response_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
                response = json.loads(response_raw)
                
                if response.get("ok"):
                    if should_succeed:
                        print(f"✅ {test_name}: SUCCESS (connection accepted)")
                        return True
                    else:
                        print(f"❌ {test_name}: FAILED (connection should have been rejected)")
                        return False
                else:
                    if not should_succeed:
                        error = response.get("error", "unknown")
                        print(f"✅ {test_name}: SUCCESS (connection rejected as expected: {error})")
                        return True
                    else:
                        error = response.get("error", "unknown")
                        print(f"❌ {test_name}: FAILED (connection rejected: {error})")
                        return False
                        
            except asyncio.TimeoutError:
                print(f"❌ {test_name}: FAILED (timeout waiting for response)")
                return False
                
    except Exception as e:
        if not should_succeed:
            print(f"✅ {test_name}: SUCCESS (connection failed as expected: {e})")
            return True
        else:
            print(f"❌ {test_name}: FAILED (exception: {e})")
            return False


async def test_rapid_connections(count: int = 10) -> bool:
    """Test multiple rapid connections with correct token."""
    print(f"\n🔄 Testing {count} rapid connections...")
    tasks = []
    for i in range(count):
        tasks.append(test_connection(CORRECT_TOKEN, f"Rapid connection {i+1}/{count}", should_succeed=True))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_count = sum(1 for r in results if r is True)
    
    if success_count == count:
        print(f"✅ Rapid connections test: ALL {count} connections succeeded")
        return True
    else:
        print(f"❌ Rapid connections test: Only {success_count}/{count} succeeded")
        return False


async def test_delayed_hello() -> bool:
    """Test connection with delay before sending hello."""
    uri = f"ws://{HOST}:{PORT}"
    try:
        async with websockets.connect(uri, max_size=20 * 1024 * 1024) as ws:
            # Delay 3 seconds before sending hello
            await asyncio.sleep(3)
            
            hello = {
                "op": "hello",
                "session_id": f"test-delayed-{uuid.uuid4().hex[:6]}",
                "token": CORRECT_TOKEN
            }
            await ws.send(json.dumps(hello))
            
            try:
                response_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
                response = json.loads(response_raw)
                
                if response.get("ok"):
                    print(f"✅ Delayed hello test: SUCCESS")
                    return True
                else:
                    error = response.get("error", "unknown")
                    print(f"❌ Delayed hello test: FAILED (rejected: {error})")
                    return False
                    
            except asyncio.TimeoutError:
                print(f"❌ Delayed hello test: FAILED (timeout)")
                return False
                
    except Exception as e:
        print(f"❌ Delayed hello test: FAILED (exception: {e})")
        return False


async def main():
    """Run all auth token validation tests."""
    print("=" * 70)
    print("AUTH TOKEN VALIDATION TEST SUITE")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Host: {HOST}")
    print(f"  Port: {PORT}")
    print(f"  Configured token: {CORRECT_TOKEN[:10]}..." if CORRECT_TOKEN else "  Configured token: <empty>")
    print()
    
    if not CORRECT_TOKEN:
        print("⚠️  WARNING: EXAI_WS_TOKEN is empty in .env")
        print("   Auth tests will be limited. Set EXAI_WS_TOKEN to test auth properly.")
        print()
    
    results = []
    
    # Test 1: Normal connection with correct token
    print("\n📝 Test 1: Normal connection with correct token")
    results.append(await test_connection(CORRECT_TOKEN, "Normal connection", should_succeed=True))
    
    # Test 2: Connection with wrong token (should fail if auth is enabled)
    if CORRECT_TOKEN:
        print("\n📝 Test 2: Connection with wrong token")
        results.append(await test_connection(WRONG_TOKEN, "Wrong token", should_succeed=False))
    else:
        print("\n⏭️  Test 2: SKIPPED (auth disabled)")
    
    # Test 3: Connection with empty token when daemon expects token (should fail)
    if CORRECT_TOKEN:
        print("\n📝 Test 3: Connection with empty token")
        results.append(await test_connection(EMPTY_TOKEN, "Empty token", should_succeed=False))
    else:
        print("\n⏭️  Test 3: SKIPPED (auth disabled)")
    
    # Test 4: Multiple rapid connections
    print("\n📝 Test 4: Multiple rapid connections")
    results.append(await test_rapid_connections(10))
    
    # Test 5: Connection with delay before hello
    print("\n📝 Test 5: Connection with delayed hello")
    results.append(await test_delayed_hello())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

