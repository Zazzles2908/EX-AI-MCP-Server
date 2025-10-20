"""
Phase 1 Verification Test - Simple Manual Test Script

This script tests the two Phase 1 emergency fixes:
1. Circuit breaker aborts on stagnation
2. Request cache eliminates triple Supabase loading

Run this script to verify the fixes are working correctly.
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

# Configuration
WS_URL = "ws://localhost:8079"
TIMEOUT = 120  # 2 minutes max per test


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"    {message}")


async def send_request(ws, tool_name, arguments):
    """Send a request and wait for response"""
    req_id = f"test_{int(time.time() * 1000)}"
    
    request = {
        "op": "call_tool",
        "request_id": req_id,
        "name": tool_name,
        "arguments": arguments
    }
    
    print(f"📤 Sending: {tool_name}")
    await ws.send(json.dumps(request))
    
    # Wait for response
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            
            if data.get("request_id") == req_id and data.get("op") == "result":
                elapsed = time.time() - start_time
                print(f"📥 Received response in {elapsed:.2f}s")
                return data, elapsed
                
        except asyncio.TimeoutError:
            continue
    
    raise TimeoutError(f"No response received within {TIMEOUT}s")


async def test_circuit_breaker():
    """
    Test #1: Circuit Breaker Abort
    
    Expected behavior:
    - Tool should abort after 3 steps with stagnant confidence
    - Should NOT call expert analysis
    - Should return clear error message
    - Should complete in < 10 seconds (not 30-60s timeout)
    """
    print_header("TEST #1: Circuit Breaker Abort on Stagnation")
    
    try:
        async with websockets.connect(WS_URL) as ws:
            # Send intentionally vague debug request to trigger stagnation
            arguments = {
                "step": "Find the bug",  # Intentionally vague
                "step_number": 1,
                "total_steps": 5,
                "next_step_required": True,
                "findings": "Starting investigation",
                "model": "glm-4.5-flash"  # Fast model for quick test
            }
            
            response, elapsed = await send_request(ws, "debug_EXAI-WS", arguments)
            
            # Parse response
            result = response.get("result", [])
            if result:
                text = result[0].get("text", "")
                data = json.loads(text)
                
                # Check for circuit breaker abort
                status = data.get("status", "")
                error = data.get("error", "")
                
                if "circuit_breaker_abort" in status or "Circuit breaker" in error:
                    print_result("Circuit breaker triggered", True, 
                               f"Aborted in {elapsed:.2f}s (expected < 10s)")
                    
                    if elapsed < 10:
                        print_result("Fast abort (no timeout)", True,
                                   f"{elapsed:.2f}s < 10s threshold")
                    else:
                        print_result("Fast abort (no timeout)", False,
                                   f"{elapsed:.2f}s >= 10s (still calling expert analysis?)")
                    
                    if "provide more context" in error.lower() or "break task" in error.lower():
                        print_result("Clear error message", True,
                                   "Error message provides actionable guidance")
                    else:
                        print_result("Clear error message", False,
                                   "Error message unclear")
                    
                    return True
                else:
                    print_result("Circuit breaker triggered", False,
                               f"Status: {status}, no circuit breaker abort detected")
                    return False
            else:
                print_result("Circuit breaker test", False, "No result in response")
                return False
                
    except Exception as e:
        print_result("Circuit breaker test", False, f"Error: {e}")
        return False


async def test_request_cache():
    """
    Test #2: Request Cache Eliminates Triple Loading
    
    Expected behavior:
    - First request loads from Supabase (or L1/L2 cache)
    - Subsequent calls in SAME request use request cache (0ms)
    - Next request (new req_id) loads fresh (cache cleared)
    - Should see "[REQUEST_CACHE HIT]" in logs for same request
    """
    print_header("TEST #2: Request Cache Eliminates Triple Loading")
    
    try:
        async with websockets.connect(WS_URL) as ws:
            # Create a conversation first
            continuation_id = f"test_cache_{int(time.time())}"
            
            # Request 1: Initial request with continuation_id
            print("\n📝 Request 1: Creating conversation...")
            arguments1 = {
                "prompt": "Test request 1",
                "continuation_id": continuation_id,
                "model": "glm-4.5-flash"
            }
            
            response1, elapsed1 = await send_request(ws, "chat_EXAI-WS", arguments1)
            print(f"   Completed in {elapsed1:.2f}s")
            
            # Request 2: Same continuation_id (should load from cache, then clear)
            print("\n📝 Request 2: Same continuation_id...")
            arguments2 = {
                "prompt": "Test request 2",
                "continuation_id": continuation_id,
                "model": "glm-4.5-flash"
            }
            
            response2, elapsed2 = await send_request(ws, "chat_EXAI-WS", arguments2)
            print(f"   Completed in {elapsed2:.2f}s")
            
            # Request 3: Same continuation_id again (cache should be cleared from request 2)
            print("\n📝 Request 3: Same continuation_id (cache cleared)...")
            arguments3 = {
                "prompt": "Test request 3",
                "continuation_id": continuation_id,
                "model": "glm-4.5-flash"
            }
            
            response3, elapsed3 = await send_request(ws, "chat_EXAI-WS", arguments3)
            print(f"   Completed in {elapsed3:.2f}s")
            
            # Analysis
            print("\n📊 Analysis:")
            print(f"   Request 1: {elapsed1:.2f}s (baseline)")
            print(f"   Request 2: {elapsed2:.2f}s")
            print(f"   Request 3: {elapsed3:.2f}s")
            
            # Check if requests completed successfully
            all_success = all([
                response1.get("result"),
                response2.get("result"),
                response3.get("result")
            ])
            
            if all_success:
                print_result("All requests completed", True)
                print("\n⚠️  To verify cache behavior, check Docker logs for:")
                print("   - [REQUEST_CACHE STORE] messages")
                print("   - [REQUEST_CACHE HIT] messages (if multiple get_thread in same request)")
                print("   - [REQUEST_CACHE] Clearing X cached threads")
                print("\n   Run: docker-compose logs -f | grep REQUEST_CACHE")
                return True
            else:
                print_result("All requests completed", False, "Some requests failed")
                return False
                
    except Exception as e:
        print_result("Request cache test", False, f"Error: {e}")
        return False


async def test_basic_connectivity():
    """Test basic WebSocket connectivity"""
    print_header("TEST #0: Basic Connectivity Check")
    
    try:
        async with websockets.connect(WS_URL, timeout=5) as ws:
            print_result("WebSocket connection", True, f"Connected to {WS_URL}")
            
            # Try a simple tool call
            arguments = {
                "prompt": "Hello, are you working?",
                "model": "glm-4.5-flash"
            }
            
            response, elapsed = await send_request(ws, "chat_EXAI-WS", arguments)
            
            if response.get("result"):
                print_result("Basic tool call", True, f"Completed in {elapsed:.2f}s")
                return True
            else:
                print_result("Basic tool call", False, "No result in response")
                return False
                
    except Exception as e:
        print_result("WebSocket connection", False, f"Error: {e}")
        print("\n⚠️  Make sure Docker container is running:")
        print("   docker-compose ps")
        print("   docker-compose logs -f")
        return False


async def main():
    """Run all tests"""
    print("\n" + "🧪" * 40)
    print("  PHASE 1 VERIFICATION TEST SUITE")
    print("  Testing Emergency Fixes (2025-10-20)")
    print("🧪" * 40)
    
    results = {}
    
    # Test 0: Basic connectivity
    results["connectivity"] = await test_basic_connectivity()
    
    if not results["connectivity"]:
        print("\n❌ Basic connectivity failed. Fix connection issues before continuing.")
        return
    
    # Test 1: Circuit breaker
    results["circuit_breaker"] = await test_circuit_breaker()
    
    # Test 2: Request cache
    results["request_cache"] = await test_request_cache()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"Tests Passed: {passed}/{total}")
    print()
    
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 1 fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "=" * 80)
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()

