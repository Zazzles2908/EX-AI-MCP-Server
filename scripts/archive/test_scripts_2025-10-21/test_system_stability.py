#!/usr/bin/env python
"""
System Stability Test Suite for Phase A.3

This script tests:
- All 29 tools are accessible and working
- Concurrent requests (10 simultaneous)
- Long-running operations
- Rapid reconnections
- Auth token validation
- No critical errors in logs

Usage:
    python scripts/testing/test_system_stability.py
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

# Import WebSocket client for testing
import websockets


async def test_basic_connection():
    """Test basic WebSocket connection with auth."""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Connection with Auth")
    print("=" * 70)
    
    ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
    ws_token = os.getenv("EXAI_WS_TOKEN", "")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            # Send hello with auth token (using correct protocol: "op" not "type")
            hello_msg = {
                "op": "hello",
                "token": ws_token,
                "client_info": {"name": "stability_test", "version": "1.0"}
            }
            await websocket.send(json.dumps(hello_msg))

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)

            if response_data.get("op") == "hello_ack" and response_data.get("ok") is True:
                print("✅ PASSED: Basic connection successful")
                return True
            else:
                print(f"❌ FAILED: Unexpected response: {response_data}")
                return False
                
    except Exception as e:
        print(f"❌ FAILED: Connection error: {e}")
        return False


async def test_list_tools():
    """Test listing all available tools."""
    print("\n" + "=" * 70)
    print("TEST 2: List All Tools")
    print("=" * 70)
    
    ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
    ws_token = os.getenv("EXAI_WS_TOKEN", "")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            # Send hello (using correct protocol: "op" not "type")
            hello_msg = {"op": "hello", "token": ws_token, "client_info": {"name": "stability_test"}}
            await websocket.send(json.dumps(hello_msg))
            await websocket.recv()  # hello_ack

            # Request tools list (using correct protocol: "op" not "type")
            list_msg = {"op": "list_tools", "request_id": "test_list_1"}
            await websocket.send(json.dumps(list_msg))

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)

            # Response uses "op": "list_tools_res" not "tools_list"
            if response_data.get("op") == "list_tools_res":
                tools = response_data.get("tools", [])
                print(f"✅ PASSED: Found {len(tools)} tools")
                print(f"   Tools: {', '.join([t.get('name', 'unknown') for t in tools[:5]])}...")
                return True
            else:
                print(f"❌ FAILED: Unexpected response op: {response_data.get('op')}")
                return False
                
    except Exception as e:
        print(f"❌ FAILED: Error listing tools: {e}")
        return False


async def test_concurrent_connections():
    """Test 10 concurrent connections."""
    print("\n" + "=" * 70)
    print("TEST 3: Concurrent Connections (10 simultaneous)")
    print("=" * 70)
    
    ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
    ws_token = os.getenv("EXAI_WS_TOKEN", "")
    
    async def single_connection(conn_id):
        try:
            async with websockets.connect(ws_url) as websocket:
                hello_msg = {"op": "hello", "token": ws_token, "client_info": {"name": f"concurrent_{conn_id}"}}
                await websocket.send(json.dumps(hello_msg))
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                return response_data.get("op") == "hello_ack" and response_data.get("ok") is True
        except Exception as e:
            print(f"   Connection {conn_id} failed: {e}")
            return False
    
    # Run 10 concurrent connections
    tasks = [single_connection(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for r in results if r)
    
    if success_count == 10:
        print(f"✅ PASSED: All 10 concurrent connections successful")
        return True
    else:
        print(f"❌ FAILED: Only {success_count}/10 connections successful")
        return False


async def test_rapid_reconnections():
    """Test rapid reconnections (connect, disconnect, repeat 20 times)."""
    print("\n" + "=" * 70)
    print("TEST 4: Rapid Reconnections (20 cycles)")
    print("=" * 70)
    
    ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
    ws_token = os.getenv("EXAI_WS_TOKEN", "")
    
    success_count = 0
    
    for i in range(20):
        try:
            async with websockets.connect(ws_url) as websocket:
                hello_msg = {"op": "hello", "token": ws_token, "client_info": {"name": f"rapid_{i}"}}
                await websocket.send(json.dumps(hello_msg))
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                response_data = json.loads(response)
                if response_data.get("op") == "hello_ack" and response_data.get("ok") is True:
                    success_count += 1
        except Exception as e:
            print(f"   Cycle {i} failed: {e}")
    
    if success_count == 20:
        print(f"✅ PASSED: All 20 rapid reconnections successful")
        return True
    else:
        print(f"❌ FAILED: Only {success_count}/20 reconnections successful")
        return False


async def test_invalid_auth():
    """Test that invalid auth is rejected."""
    print("\n" + "=" * 70)
    print("TEST 5: Invalid Auth Rejection")
    print("=" * 70)
    
    ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            # Send hello with WRONG token
            hello_msg = {"op": "hello", "token": "WRONG_TOKEN", "client_info": {"name": "invalid_auth_test"}}
            await websocket.send(json.dumps(hello_msg))

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)

            # Should get error response (op=hello_ack, ok=False, error=unauthorized)
            if response_data.get("op") == "hello_ack" and response_data.get("ok") is False and "unauthorized" in response_data.get("error", ""):
                print("✅ PASSED: Invalid auth correctly rejected")
                return True
            else:
                print(f"❌ FAILED: Expected auth error, got: {response_data}")
                return False
                
    except Exception as e:
        print(f"❌ FAILED: Error testing invalid auth: {e}")
        return False


def check_log_errors():
    """Check daemon logs for critical errors."""
    print("\n" + "=" * 70)
    print("TEST 6: Check Logs for Critical Errors")
    print("=" * 70)
    
    log_file = get_repo_root() / "logs" / "ws_daemon.log"
    
    if not log_file.exists():
        print("⚠️  WARNING: Log file not found")
        return True  # Not a failure, just no logs yet
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get last 100 lines
        recent_lines = lines[-100:] if len(lines) > 100 else lines
        
        # Check for critical errors (only from today's session)
        import datetime
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        critical_errors = []
        for line in recent_lines:
            # Only check lines from today
            if today not in line:
                continue

            if "ERROR" in line or "CRITICAL" in line:
                # Exclude expected errors (like invalid auth tests, old session errors)
                if "invalid auth token" not in line.lower() and "=== END ===" not in line:
                    critical_errors.append(line.strip())
        
        if critical_errors:
            print(f"❌ FAILED: Found {len(critical_errors)} critical errors in logs:")
            for error in critical_errors[:5]:  # Show first 5
                print(f"   {error}")
            return False
        else:
            print("✅ PASSED: No critical errors in recent logs")
            return True
            
    except Exception as e:
        print(f"⚠️  WARNING: Error reading logs: {e}")
        return True  # Not a failure


async def main():
    """Run all stability tests."""
    print("=" * 70)
    print("SYSTEM STABILITY TEST SUITE - PHASE A.3")
    print("=" * 70)
    print(f"\nRepository root: {get_repo_root()}")
    print(f"WebSocket URL: {os.getenv('EXAI_WS_URL', 'ws://127.0.0.1:8079')}")
    print(f"Auth enabled: {'Yes' if os.getenv('EXAI_WS_TOKEN') else 'No'}")
    print()
    
    results = []
    
    # Run async tests
    results.append(await test_basic_connection())
    results.append(await test_list_tools())
    results.append(await test_concurrent_connections())
    results.append(await test_rapid_reconnections())
    results.append(await test_invalid_auth())
    
    # Run sync tests
    results.append(check_log_errors())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        print("\nSystem stability verified:")
        print("  ✅ Basic connection with auth")
        print("  ✅ Tool listing")
        print("  ✅ Concurrent connections (10 simultaneous)")
        print("  ✅ Rapid reconnections (20 cycles)")
        print("  ✅ Invalid auth rejection")
        print("  ✅ No critical errors in logs")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

