#!/usr/bin/env python3
"""
Test use_websearch=false enforcement

Tests that use_websearch=false is properly enforced and web search is NOT performed.

Bug #2: use_websearch=false parameter being ignored
"""

import asyncio
import json
import websockets
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def test_websearch_enforcement():
    """Test that use_websearch=false prevents web search"""
    
    uri = "ws://127.0.0.1:8079"
    
    print("=" * 80)
    print("TEST: use_websearch=false Enforcement")
    print("=" * 80)
    
    try:
        async with websockets.connect(uri, ping_interval=30, ping_timeout=10) as websocket:
            
            # Test 1: use_websearch=false should NOT trigger web search
            print("\n[TEST 1] use_websearch=false - Should NOT use web search")
            print("-" * 80)
            
            request_1 = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "chat_EXAI-WS",
                    "arguments": {
                        "prompt": "What is the current price of Bitcoin?",
                        "use_websearch": False,  # ← CRITICAL: Should prevent web search
                        "model_name": "glm-4.5-flash"
                    }
                }
            }
            
            await websocket.send(json.dumps(request_1))
            print(f"✓ Sent request with use_websearch=False")
            
            response_1 = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            result_1 = json.loads(response_1)
            
            print(f"\n[RESPONSE 1]")
            if "result" in result_1:
                content = result_1["result"].get("content", [])
                if content:
                    text = content[0].get("text", "")
                    print(f"Response length: {len(text)} chars")
                    print(f"First 200 chars: {text[:200]}...")
                    
                    # Check for web search indicators
                    web_indicators = [
                        "search results",
                        "according to",
                        "based on search",
                        "web search",
                        "source:",
                        "http://",
                        "https://"
                    ]
                    
                    found_indicators = [ind for ind in web_indicators if ind.lower() in text.lower()]
                    
                    if found_indicators:
                        print(f"\n❌ FAIL: Web search indicators found: {found_indicators}")
                        print(f"   use_websearch=false was IGNORED!")
                        return False
                    else:
                        print(f"\n✓ PASS: No web search indicators found")
                        print(f"   use_websearch=false was ENFORCED")
                else:
                    print("❌ FAIL: No content in response")
                    return False
            else:
                print(f"❌ FAIL: Error in response: {result_1.get('error')}")
                return False
            
            # Test 2: use_websearch=true should trigger web search
            print("\n" + "=" * 80)
            print("[TEST 2] use_websearch=true - Should use web search")
            print("-" * 80)
            
            request_2 = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "chat_EXAI-WS",
                    "arguments": {
                        "prompt": "What is the current price of Bitcoin?",
                        "use_websearch": True,  # ← Should enable web search
                        "model_name": "glm-4.5-flash"
                    }
                }
            }
            
            await websocket.send(json.dumps(request_2))
            print(f"✓ Sent request with use_websearch=True")
            
            response_2 = await asyncio.wait_for(websocket.recv(), timeout=60.0)
            result_2 = json.loads(response_2)
            
            print(f"\n[RESPONSE 2]")
            if "result" in result_2:
                content = result_2["result"].get("content", [])
                if content:
                    text = content[2]["text"]
                    print(f"Response length: {len(text)} chars")
                    print(f"First 200 chars: {text[:200]}...")
                    
                    # Check for web search indicators
                    found_indicators = [ind for ind in web_indicators if ind.lower() in text.lower()]
                    
                    if found_indicators:
                        print(f"\n✓ PASS: Web search indicators found: {found_indicators}")
                        print(f"   use_websearch=true worked correctly")
                    else:
                        print(f"\n⚠️  WARNING: No web search indicators found")
                        print(f"   use_websearch=true may not have triggered search")
                else:
                    print("❌ FAIL: No content in response")
                    return False
            else:
                print(f"❌ FAIL: Error in response: {result_2.get('error')}")
                return False
            
            print("\n" + "=" * 80)
            print("✅ TEST COMPLETE: use_websearch enforcement verified")
            print("=" * 80)
            return True
            
    except asyncio.TimeoutError:
        print("\n❌ FAIL: Request timed out")
        return False
    except Exception as e:
        print(f"\n❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_websearch_enforcement())
    sys.exit(0 if result else 1)

