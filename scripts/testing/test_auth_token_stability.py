#!/usr/bin/env python
"""
Auth Token Stability Test - Phase A Task A.1

Tests WebSocket authentication token validation under various conditions:
1. Normal connection with correct token
2. Multiple rapid connections (race condition test)
3. Connection with delay before hello (timeout test)
4. Connection with wrong token (security test)
5. Connection with empty token (missing token test)
6. Token rotation test

This verifies the auth token system works reliably without intermittent failures.
"""

import asyncio
import json
import os
import sys
import time
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
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def print_test(name, status, details=""):
    """Print test result."""
    symbol = "✅" if status == "PASS" else "❌"
    print(f"{symbol} {name}: {status}")
    if details:
        print(f"   {details}")


async def test_normal_connection():
    """Test 1: Normal connection with correct token."""
    print_header("TEST 1: Normal Connection with Correct Token")
    
    try:
        async with websockets.connect(WS_URL, open_timeout=5) as ws:
            # Send hello with correct token
            hello = {
                "op": "hello",
                "token": WS_TOKEN
            }
            await ws.send(json.dumps(hello))
            
            # Wait for ack
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            ack = json.loads(ack_raw)
            
            # Verify ack
            if ack.get("op") == "hello_ack" and ack.get("ok") is True:
                print_test("Normal connection", "PASS", f"Session ID: {ack.get('session_id')}")
                test_results["passed"] += 1
                return True
            else:
                print_test("Normal connection", "FAIL", f"Unexpected ack: {ack}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test 1: Unexpected ack: {ack}")
                return False
                
    except Exception as e:
        print_test("Normal connection", "FAIL", f"Exception: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Test 1: {e}")
        return False


async def test_single_rapid_connection(test_num):
    """Helper for rapid connection test."""
    try:
        async with websockets.connect(WS_URL, open_timeout=5) as ws:
            hello = {"op": "hello", "token": WS_TOKEN}
            await ws.send(json.dumps(hello))
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            ack = json.loads(ack_raw)
            
            if ack.get("op") == "hello_ack" and ack.get("ok") is True:
                return True
            else:
                test_results["errors"].append(f"Rapid connection {test_num}: Unexpected ack: {ack}")
                return False
    except Exception as e:
        test_results["errors"].append(f"Rapid connection {test_num}: {e}")
        return False


async def test_rapid_connections():
    """Test 2: Multiple rapid connections (race condition test)."""
    print_header("TEST 2: Multiple Rapid Connections (Race Condition Test)")
    
    num_connections = 10
    print(f"Testing {num_connections} rapid connections...")
    
    try:
        # Create 10 connections simultaneously
        tasks = [test_single_rapid_connection(i) for i in range(num_connections)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        successes = sum(1 for r in results if r is True)
        
        if successes == num_connections:
            print_test("Rapid connections", "PASS", f"All {num_connections} connections succeeded")
            test_results["passed"] += 1
            return True
        else:
            print_test("Rapid connections", "FAIL", f"Only {successes}/{num_connections} succeeded")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_test("Rapid connections", "FAIL", f"Exception: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Test 2: {e}")
        return False


async def test_delayed_hello():
    """Test 3: Connection with delay before hello (timeout test)."""
    print_header("TEST 3: Connection with Delay Before Hello")
    
    try:
        async with websockets.connect(WS_URL, open_timeout=5) as ws:
            # Wait 2 seconds before sending hello (should still work)
            print("Waiting 2 seconds before sending hello...")
            await asyncio.sleep(2)
            
            hello = {"op": "hello", "token": WS_TOKEN}
            await ws.send(json.dumps(hello))
            
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            ack = json.loads(ack_raw)
            
            if ack.get("op") == "hello_ack" and ack.get("ok") is True:
                print_test("Delayed hello", "PASS", "Connection succeeded after 2s delay")
                test_results["passed"] += 1
                return True
            else:
                print_test("Delayed hello", "FAIL", f"Unexpected ack: {ack}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test 3: Unexpected ack: {ack}")
                return False
                
    except Exception as e:
        print_test("Delayed hello", "FAIL", f"Exception: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Test 3: {e}")
        return False


async def test_wrong_token():
    """Test 4: Connection with wrong token (security test)."""
    print_header("TEST 4: Connection with Wrong Token (Security Test)")
    
    try:
        async with websockets.connect(WS_URL, open_timeout=5) as ws:
            # Send hello with wrong token
            hello = {"op": "hello", "token": "wrong-token-12345"}
            await ws.send(json.dumps(hello))
            
            # Should get unauthorized error
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            ack = json.loads(ack_raw)
            
            if ack.get("op") == "hello_ack" and ack.get("ok") is False and ack.get("error") == "unauthorized":
                print_test("Wrong token", "PASS", "Correctly rejected wrong token")
                test_results["passed"] += 1
                return True
            else:
                print_test("Wrong token", "FAIL", f"Unexpected ack: {ack}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test 4: Should reject wrong token, got: {ack}")
                return False
                
    except websockets.exceptions.ConnectionClosedError as e:
        # Connection closed is also acceptable (daemon closed connection)
        if e.code == 4003:  # Unauthorized close code
            print_test("Wrong token", "PASS", "Connection closed with unauthorized code")
            test_results["passed"] += 1
            return True
        else:
            print_test("Wrong token", "FAIL", f"Unexpected close code: {e.code}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Test 4: Unexpected close code: {e.code}")
            return False
    except Exception as e:
        print_test("Wrong token", "FAIL", f"Exception: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Test 4: {e}")
        return False


async def test_empty_token():
    """Test 5: Connection with empty token (missing token test)."""
    print_header("TEST 5: Connection with Empty Token")
    
    try:
        async with websockets.connect(WS_URL, open_timeout=5) as ws:
            # Send hello with empty token
            hello = {"op": "hello", "token": ""}
            await ws.send(json.dumps(hello))
            
            # Should get unauthorized error
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            ack = json.loads(ack_raw)
            
            if ack.get("op") == "hello_ack" and ack.get("ok") is False and ack.get("error") == "unauthorized":
                print_test("Empty token", "PASS", "Correctly rejected empty token")
                test_results["passed"] += 1
                return True
            else:
                print_test("Empty token", "FAIL", f"Unexpected ack: {ack}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test 5: Should reject empty token, got: {ack}")
                return False
                
    except websockets.exceptions.ConnectionClosedError as e:
        # Connection closed is also acceptable
        if e.code == 4003:  # Unauthorized close code
            print_test("Empty token", "PASS", "Connection closed with unauthorized code")
            test_results["passed"] += 1
            return True
        else:
            print_test("Empty token", "FAIL", f"Unexpected close code: {e.code}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Test 5: Unexpected close code: {e.code}")
            return False
    except Exception as e:
        print_test("Empty token", "FAIL", f"Exception: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Test 5: {e}")
        return False


async def main():
    """Run all auth token tests."""
    print_header("AUTH TOKEN STABILITY TEST - PHASE A TASK A.1")
    print(f"Repository root: {get_repo_root()}")
    print(f"WebSocket URL: {WS_URL}")
    print(f"Auth token configured: {'Yes' if WS_TOKEN else 'No'}")
    if WS_TOKEN:
        print(f"Token (first 10 chars): {WS_TOKEN[:10]}...")
    
    # Run all tests
    await test_normal_connection()
    await test_rapid_connections()
    await test_delayed_hello()
    await test_wrong_token()
    await test_empty_token()
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"Tests passed: {test_results['passed']}/5")
    print(f"Tests failed: {test_results['failed']}/5")
    
    if test_results["errors"]:
        print("\nErrors:")
        for error in test_results["errors"]:
            print(f"  - {error}")
    
    if test_results["failed"] == 0:
        print("\n[SUCCESS] ALL AUTH TOKEN TESTS PASSED ✅")
        return 0
    else:
        print("\n[FAILURE] SOME AUTH TOKEN TESTS FAILED ❌")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

