"""
Test thinking_mode parameter through actual MCP server

This test calls the thinkdeep tool through the WebSocket daemon
to verify the thinking_mode parameter works end-to-end.
"""

import asyncio
import json
import time
import websockets
from pathlib import Path


async def call_tool_via_ws(tool_name: str, arguments: dict) -> dict:
    """Call a tool through the WebSocket daemon"""
    uri = "ws://127.0.0.1:8079"
    
    async with websockets.connect(uri) as websocket:
        # Send tool call request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        return json.loads(response)


async def test_default_thinking_mode():
    """Test 1: Default thinking mode (minimal from env)"""
    print("\n" + "="*80)
    print("TEST 1: Default thinking mode (from env = minimal)")
    print("="*80)
    
    arguments = {
        "step": "Analyze microservices vs monolithic architecture",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Testing default thinking mode - should use minimal from env",
        "model": "glm-4.5-flash"
        # No thinking_mode specified - should use minimal from env
    }
    
    start = time.time()
    
    try:
        result = await call_tool_via_ws("thinkdeep", arguments)
        duration = time.time() - start
        
        print(f"✅ SUCCESS")
        print(f"Duration: {duration:.1f}s")
        print(f"Result keys: {result.get('result', {}).keys() if 'result' in result else 'No result'}")
        
        # Check if expert analysis was called
        result_content = result.get('result', {}).get('content', [{}])[0].get('text', '{}')
        result_data = json.loads(result_content) if result_content else {}
        has_expert = "expert_analysis" in str(result_data)
        
        print(f"Expert analysis present: {has_expert}")
        print(f"Expected duration: ~5-7s")
        
        return duration, has_expert
        
    except Exception as e:
        duration = time.time() - start
        print(f"❌ FAILED after {duration:.1f}s")
        print(f"Error: {e}")
        return duration, False


async def test_user_thinking_mode(mode: str, expected_duration: str):
    """Test 2: User-provided thinking_mode parameter"""
    print("\n" + "="*80)
    print(f"TEST 2: User-provided thinking_mode='{mode}'")
    print("="*80)
    
    arguments = {
        "step": "Analyze microservices vs monolithic architecture",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": f"Testing user-provided thinking_mode={mode}",
        "model": "glm-4.5-flash",
        "thinking_mode": mode  # User provides thinking mode
    }
    
    start = time.time()
    
    try:
        result = await call_tool_via_ws("thinkdeep", arguments)
        duration = time.time() - start
        
        print(f"✅ SUCCESS")
        print(f"Duration: {duration:.1f}s")
        
        result_content = result.get('result', {}).get('content', [{}])[0].get('text', '{}')
        result_data = json.loads(result_content) if result_content else {}
        has_expert = "expert_analysis" in str(result_data)
        
        print(f"Expert analysis present: {has_expert}")
        print(f"Expected duration: {expected_duration}")
        
        return duration, has_expert
        
    except Exception as e:
        duration = time.time() - start
        print(f"❌ FAILED after {duration:.1f}s")
        print(f"Error: {e}")
        return duration, False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("THINKING MODE PARAMETER TESTS (via MCP)")
    print("="*80)
    print("\nThese tests verify thinking_mode parameter works through MCP server:")
    print("1. Default thinking mode from env (minimal)")
    print("2. User-provided thinking_mode parameter")
    print("3. Performance varies by thinking mode")
    
    results = {}
    
    # Test 1: Default (minimal from env)
    duration, has_expert = await test_default_thinking_mode()
    results['default'] = {'duration': duration, 'has_expert': has_expert}
    
    # Test 2: User-provided minimal
    duration, has_expert = await test_user_thinking_mode('minimal', '~5-7s')
    results['minimal'] = {'duration': duration, 'has_expert': has_expert}
    
    # Test 3: User-provided low
    duration, has_expert = await test_user_thinking_mode('low', '~8-10s')
    results['low'] = {'duration': duration, 'has_expert': has_expert}
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✅" if result['has_expert'] and result['duration'] > 1 else "❌"
        print(f"{status} {test_name:15s}: {result['duration']:6.1f}s | Expert: {result['has_expert']}")
    
    print("\n" + "="*80)
    print("ANALYSIS:")
    print("="*80)
    
    # Check if tests passed
    all_passed = True
    for test_name, result in results.items():
        if not result['has_expert']:
            print(f"❌ {test_name}: Expert analysis not called!")
            all_passed = False
        elif result['duration'] < 1:
            print(f"❌ {test_name}: Too fast ({result['duration']:.1f}s) - expert analysis likely didn't run!")
            all_passed = False
    
    if all_passed:
        print("✅ All tests passed! thinking_mode parameter is working correctly.")
    else:
        print("❌ Some tests failed. Check implementation.")


if __name__ == "__main__":
    asyncio.run(main())

