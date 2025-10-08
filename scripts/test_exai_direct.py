"""
Direct test of EXAI MCP tools through WebSocket daemon.

This script connects to the running ws_daemon and calls EXAI tools directly,
allowing us to see real model outputs with proper API keys.

Usage:
    python scripts/test_exai_direct.py
"""

import asyncio
import json
import websockets
import uuid
from datetime import datetime


async def call_exai_tool(tool_name: str, arguments: dict):
    """Call an EXAI tool through the WebSocket daemon."""
    uri = "ws://127.0.0.1:8079"
    
    request_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    message = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected! Sending request...")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Tool: {tool_name}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Arguments: {json.dumps(arguments, indent=2)[:200]}...")
            
            await websocket.send(json.dumps(message))
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for response...")
            
            response = await websocket.recv()
            data = json.loads(response)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Response received!")
            
            return data
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_chat_basic():
    """Test basic chat functionality."""
    print("\n" + "=" * 80)
    print("TEST 1: Basic Chat (No Web Search)")
    print("=" * 80)
    
    arguments = {
        "prompt": "Explain Python's asyncio in exactly 2 sentences.",
        "model": "glm-4.5-flash",
        "use_websearch": False
    }
    
    result = await call_exai_tool("chat", arguments)
    
    if result and "result" in result:
        content = result["result"]["content"][0]["text"]
        print(f"\n✅ Response:\n{content}\n")
        return True
    else:
        print(f"\n❌ Failed: {result}")
        return False


async def test_chat_with_websearch():
    """Test chat with web search enabled."""
    print("\n" + "=" * 80)
    print("TEST 2: Chat with Web Search")
    print("=" * 80)
    
    arguments = {
        "prompt": "What are the top 2 AI news headlines today? Provide URLs.",
        "model": "glm-4.6",
        "use_websearch": True
    }
    
    result = await call_exai_tool("chat", arguments)
    
    if result and "result" in result:
        content = result["result"]["content"][0]["text"]
        print(f"\n✅ Response:\n{content}\n")
        return True
    else:
        print(f"\n❌ Failed: {result}")
        return False


async def test_thinkdeep_basic():
    """Test thinkdeep without web search."""
    print("\n" + "=" * 80)
    print("TEST 3: ThinkDeep (No Web Search)")
    print("=" * 80)
    
    arguments = {
        "step": "Analyze whether microservices or monolithic architecture is better for a real-time monitoring system with 5ms latency requirements",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Testing thinkdeep with architectural analysis. Need to consider latency, scalability, and operational complexity.",
        "model": "glm-4.5-flash",
        "use_websearch": False,
        "confidence": "high"
    }
    
    result = await call_exai_tool("thinkdeep", arguments)
    
    if result and "result" in result:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        print(f"\n✅ Status: {data.get('status', 'unknown')}")
        print(f"✅ Has expert_analysis: {'expert_analysis' in data}")
        
        if 'expert_analysis' in data:
            expert = data['expert_analysis']
            print(f"✅ Expert analysis status: {expert.get('status', 'unknown')}")
            
            if 'raw_analysis' in expert and expert['raw_analysis']:
                print(f"\n📊 Expert Analysis (first 500 chars):")
                print(expert['raw_analysis'][:500])
        
        return True
    else:
        print(f"\n❌ Failed: {result}")
        return False


async def test_thinkdeep_with_websearch():
    """Test thinkdeep with web search enabled."""
    print("\n" + "=" * 80)
    print("TEST 4: ThinkDeep (With Web Search)")
    print("=" * 80)
    
    arguments = {
        "step": "Research and analyze the latest Python 3.13 async/await best practices and performance improvements",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Testing thinkdeep with web search. Need to find current documentation and community insights on Python 3.13 async improvements.",
        "model": "glm-4.6",
        "use_websearch": True,
        "confidence": "medium"
    }
    
    result = await call_exai_tool("thinkdeep", arguments)
    
    if result and "result" in result:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        print(f"\n✅ Status: {data.get('status', 'unknown')}")
        print(f"✅ Has expert_analysis: {'expert_analysis' in data}")
        
        if 'expert_analysis' in data:
            expert = data['expert_analysis']
            print(f"✅ Expert analysis status: {expert.get('status', 'unknown')}")
            
            if 'raw_analysis' in expert and expert['raw_analysis']:
                print(f"\n📊 Expert Analysis (first 500 chars):")
                print(expert['raw_analysis'][:500])
        
        return True
    else:
        print(f"\n❌ Failed: {result}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("EXAI MCP DIRECT TEST SUITE")
    print("=" * 80)
    print("\nThis test suite calls EXAI tools through the WebSocket daemon")
    print("to verify real model outputs with proper API keys.")
    print("\n" + "=" * 80)
    
    results = []
    
    # Test 1: Basic chat
    result1 = await test_chat_basic()
    results.append(("Chat Basic", result1))
    
    # Test 2: Chat with web search
    result2 = await test_chat_with_websearch()
    results.append(("Chat Web Search", result2))
    
    # Test 3: ThinkDeep basic
    result3 = await test_thinkdeep_basic()
    results.append(("ThinkDeep Basic", result3))
    
    # Test 4: ThinkDeep with web search
    result4 = await test_thinkdeep_with_websearch()
    results.append(("ThinkDeep Web Search", result4))
    
    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe EXAI MCP tools are working correctly with real model outputs.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nCheck the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    import sys
    sys.exit(exit_code)

