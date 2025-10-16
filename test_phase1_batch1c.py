#!/usr/bin/env python3
"""Phase 1 Batch 1C Testing: kimi_intent_analysis."""

import asyncio
import websockets
import json
import os
import sys

async def test_tool(websocket, tool_name, arguments, timeout=120):
    """Test a single tool and return results."""
    test_msg = {
        "jsonrpc": "2.0",
        "id": tool_name,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    print(f"\n📤 Testing {tool_name}...")
    print(f"   Arguments: {json.dumps(arguments, indent=2)}")
    
    await websocket.send(json.dumps(test_msg))
    
    try:
        response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        result = json.loads(response)
        
        if "error" in result:
            print(f"❌ FAILED: {result['error'].get('message', 'Unknown error')}")
            print(f"   Error details: {json.dumps(result['error'], indent=2)}")
            return False, result['error']
        else:
            print(f"✅ SUCCESS!")
            content = result.get("result", {}).get("content", [])
            if content:
                first_msg = content[0]
                text = first_msg.get("text", "")
                print(f"   Response length: {len(text)} characters")
                print(f"   Response: {text}")
            return True, result
    except asyncio.TimeoutError:
        print(f"⏱️ TIMEOUT after {timeout}s")
        return False, {"error": "timeout"}

async def run_batch_1c_tests():
    """Run all Batch 1C tests."""
    uri = "ws://127.0.0.1:8079"
    token = os.getenv("EXAI_WS_TOKEN", "test-token-12345")
    
    print("=" * 80)
    print("PHASE 1 BATCH 1C: KIMI INTENT ANALYSIS")
    print("=" * 80)
    print(f"Connecting to {uri}...")
    
    async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
        # Send hello message
        hello_msg = {"op": "hello", "token": token}
        await websocket.send(json.dumps(hello_msg))
        response = await websocket.recv()
        hello_result = json.loads(response)
        
        if hello_result.get("op") != "hello_ack" or not hello_result.get("ok"):
            print(f"❌ Hello failed: {hello_result.get('error', 'unknown')}")
            return False
        
        session_id = hello_result.get("session_id", "N/A")
        print(f"✅ Connected. Session: {session_id}\n")
        
        results = {}
        
        # Test 1: kimi_intent_analysis - Simple query
        success, result = await test_tool(
            websocket,
            "kimi_intent_analysis",
            {
                "prompt": "I need to systematically test all EXAI tools",
                "context": "Testing EXAI MCP server tools",
                "use_websearch": False
            }
        )
        results["kimi_intent_analysis_simple"] = {"success": success, "result": result}
        
        # Test 2: kimi_intent_analysis - Complex query
        success, result = await test_tool(
            websocket,
            "kimi_intent_analysis",
            {
                "prompt": "How do I implement a WebSocket server with authentication and file upload support?",
                "context": "Building a real-time communication system",
                "use_websearch": False
            }
        )
        results["kimi_intent_analysis_complex"] = {"success": success, "result": result}
        
        # Summary
        print("\n" + "=" * 80)
        print("BATCH 1C SUMMARY")
        print("=" * 80)
        total = len(results)
        passed = sum(1 for r in results.values() if r["success"])
        print(f"Total: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        for tool_name, result in results.items():
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {tool_name}")
        
        return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_batch_1c_tests())
    sys.exit(0 if success else 1)

