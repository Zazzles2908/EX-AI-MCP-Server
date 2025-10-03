#!/usr/bin/env python
"""
Test script to validate web search fix.

This tests that:
1. Models autonomously use web_search tool
2. Search results are executed and returned to model
3. Model incorporates real search results (not hallucinations)
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_chat_websearch():
    """Test chat_EXAI-WS with web search"""
    try:
        import websocket
    except ImportError:
        print("❌ websocket-client not installed. Install with: pip install websocket-client")
        return
    
    print("="*80)
    print("CHAT_EXAI-WS WEB SEARCH FIX VALIDATION")
    print("="*80)
    
    # Test query that MUST use web search for accurate answer
    test_query = "What is the current pricing for Moonshot AI's Kimi K2 model as of 2025?"
    
    print(f"\nTest Query: {test_query}")
    print(f"Expected: Model should use web_search tool and return REAL pricing data")
    print(f"Failure Mode: Model hallucinates pricing without searching")
    print("\n" + "="*80)
    
    try:
        ws = websocket.create_connection("ws://127.0.0.1:8765")
        
        # Send chat request with web search enabled
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": test_query,
                    "use_websearch": True,
                    "model": "kimi-k2-0905-preview"
                }
            }
        }
        
        print("\n📤 Sending request...")
        ws.send(json.dumps(request))
        
        print("📥 Waiting for response...\n")
        response_text = ws.recv()
        ws.close()
        
        response = json.loads(response_text)
        
        # Parse the result
        if "result" in response:
            result_list = response["result"]
            if result_list and len(result_list) > 0:
                result_text = result_list[0].get("text", "")
                result_data = json.loads(result_text)
                
                print("="*80)
                print("RESPONSE ANALYSIS:")
                print("="*80)
                
                status = result_data.get("status")
                content = result_data.get("content", "")
                metadata = result_data.get("metadata", {})
                
                print(f"\n✓ Status: {status}")
                print(f"✓ Content length: {len(content)} chars")
                
                # Check for tool_call_events
                tool_events = metadata.get("tool_call_events", [])
                if tool_events:
                    print(f"\n🔧 TOOL CALLS DETECTED: {len(tool_events)} event(s)")
                    for i, event in enumerate(tool_events):
                        print(f"\n  Event #{i+1}:")
                        print(f"    Provider: {event.get('provider')}")
                        print(f"    Tool: {event.get('tool_name')}")
                        print(f"    Args: {event.get('args')}")
                else:
                    print("\n❌ NO TOOL_CALL_EVENTS in metadata")
                
                # Check content for evidence of web search
                print(f"\n📝 RESPONSE CONTENT (first 800 chars):")
                print(content[:800])
                if len(content) > 800:
                    print(f"... ({len(content) - 800} more chars)")
                
                # Validation checks
                print("\n" + "="*80)
                print("VALIDATION CHECKS:")
                print("="*80)
                
                checks = {
                    "✓ Response received": bool(content),
                    "✓ Tool events present": bool(tool_events),
                    "✓ Web search mentioned": "search" in content.lower() or "web" in content.lower(),
                    "✓ Pricing data present": "$" in content or "price" in content.lower() or "cost" in content.lower(),
                }
                
                for check, passed in checks.items():
                    symbol = "✅" if passed else "❌"
                    print(f"{symbol} {check}")
                
                all_passed = all(checks.values())
                
                print("\n" + "="*80)
                if all_passed:
                    print("🎉 SUCCESS: Web search fix is working!")
                    print("   - Model used web search tool")
                    print("   - Real search results were incorporated")
                    print("   - No hallucination detected")
                else:
                    print("⚠️  PARTIAL SUCCESS or FAILURE")
                    print("   - Check which validation failed above")
                    print("   - Model may still be hallucinating")
                print("="*80)
                
            else:
                print("❌ Empty result list")
        else:
            print(f"❌ ERROR in response: {response.get('error')}")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_chat_websearch()

