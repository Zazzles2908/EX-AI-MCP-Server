#!/usr/bin/env python
"""
Test script for Epic 2.2: Web Search Prompt Injection Fix

This script validates that the chat_EXAI-WS tool with use_websearch=true
now properly enables autonomous web search instead of asking Claude to search.

Tests:
1. Research query - "What are the latest features in zai-sdk v0.0.4?"
2. Documentation query - "How does GLM-4.6 compare to GLM-4.5?"
3. Current events query - "What are the latest AI model releases in October 2025?"

Expected behavior:
- Model should autonomously use web search tool
- Response should include search results integrated into answer
- No "SEARCH REQUIRED: Please immediately perform a web search..." messages
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import websockets


async def test_chat_websearch(query: str, test_name: str):
    """Test chat tool with web search enabled"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
    port = int(os.getenv("EXAI_WS_PORT", "8765"))
    uri = f"ws://{host}:{port}"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send chat request with use_websearch=true
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "chat_EXAI-WS",
                    "arguments": {
                        "prompt": query,
                        "use_websearch": True,
                        "model": "glm-4.5",
                        "temperature": 0.3
                    }
                }
            }
            
            await websocket.send(json.dumps(request))
            
            # Receive response
            response_text = await websocket.recv()
            response = json.loads(response_text)
            
            # Extract content
            if "result" in response and "content" in response["result"]:
                content_items = response["result"]["content"]
                if content_items and len(content_items) > 0:
                    text_content = content_items[0].get("text", "")
                    
                    # Check for the old prompt injection pattern
                    if "SEARCH REQUIRED: Please immediately perform a web search" in text_content:
                        print("❌ FAIL: Old prompt injection detected!")
                        print("Model is still asking Claude to search instead of searching autonomously")
                        return False
                    
                    if "Please perform a web search" in text_content or "Please search for" in text_content:
                        print("⚠️  WARNING: Model may be delegating search instead of using it autonomously")
                        print(f"Response preview: {text_content[:500]}...")
                        return False
                    
                    # Success - model should have used web search autonomously
                    print("✅ PASS: No prompt injection detected")
                    print(f"Response length: {len(text_content)} characters")
                    print(f"\nResponse preview:\n{text_content[:800]}...")
                    return True
                else:
                    print("❌ FAIL: No content in response")
                    return False
            else:
                print(f"❌ FAIL: Unexpected response format: {response}")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all web search tests"""
    print("\n" + "="*80)
    print("EPIC 2.2: WEB SEARCH PROMPT INJECTION FIX - VALIDATION TESTS")
    print("="*80)
    
    # Check if server is running
    host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
    port = int(os.getenv("EXAI_WS_PORT", "8765"))
    print(f"\nConnecting to EXAI-WS server at ws://{host}:{port}")
    
    tests = [
        ("What are the latest features in zai-sdk v0.0.4?", "Research Query"),
        ("How does GLM-4.6 compare to GLM-4.5 in terms of context window and pricing?", "Documentation Query"),
        ("What are the top 3 AI news stories from October 2025?", "Current Events Query"),
    ]
    
    results = []
    for query, test_name in tests:
        result = await test_chat_websearch(query, test_name)
        results.append((test_name, result))
        await asyncio.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Web search fix is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

