"""
Test model locking in continuations (Bug #4 fix verification)

This script tests that the model stays consistent across conversation turns
when using continuations, verifying the fix for Bug #4.

Bug #4 Fix:
- src/server/context/thread_context.py: Sets _model_locked_by_continuation flag
- src/server/handlers/request_handler_model_resolution.py: Respects the lock flag

Expected Behavior:
- Turn 1: User specifies kimi-thinking-preview
- Turn 2: User continues without specifying model
- Result: Turn 2 should use kimi-thinking-preview (locked from Turn 1)

Before Fix:
- Turn 2 would switch to glm-4.5-flash (routing override)

After Fix:
- Turn 2 uses kimi-thinking-preview (model locked)
"""

import asyncio
import websockets
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WS_URL = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")

async def test_model_locking():
    """Test that model is locked during continuations"""

    print("=" * 80)
    print("Bug #4 Fix Verification: Model Locking in Continuations")
    print("=" * 80)

    try:
        async with websockets.connect(WS_URL) as ws:
            # Step 1: Authenticate
            print("\n[1/4] Authenticating...")
            await ws.send(json.dumps({
                "op": "hello",
                "token": WS_TOKEN,
                "client_info": {"name": "test_model_locking", "version": "1.0"}
            }))
            hello_response = await ws.recv()
            hello_data = json.loads(hello_response)

            if not hello_data.get("ok"):
                print(f"❌ Auth failed: {hello_data}")
                return False

            print(f"✅ Authenticated successfully")
            
            # Step 2: Turn 1 - Start with kimi-thinking-preview
            print("\n[2/4] Turn 1: Starting conversation with kimi-thinking-preview...")
            request_id_1 = "test_turn_1"
            await ws.send(json.dumps({
                "op": "call_tool",
                "request_id": request_id_1,
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Explain quantum computing in one sentence",
                    "model": "kimi-thinking-preview"
                }
            }))

            # Wait for response (skip ack)
            while True:
                response1 = await ws.recv()
                data1 = json.loads(response1)
                if data1.get("op") == "call_tool_res":
                    break

            if data1.get("op") == "error":
                print(f"❌ Turn 1 failed: {data1.get('error')}")
                return False
            
            continuation_id = data1.get("continuation_id")
            model_used_1 = data1.get("metadata", {}).get("model_name")
            content_1 = data1.get("content", "")[:100]
            
            print(f"   Model used: {model_used_1}")
            print(f"   Continuation ID: {continuation_id}")
            print(f"   Response preview: {content_1}...")
            
            if not continuation_id:
                print("❌ No continuation_id returned!")
                return False
            
            if model_used_1 != "kimi-thinking-preview":
                print(f"⚠️  Warning: Expected kimi-thinking-preview, got {model_used_1}")
            
            # Step 3: Turn 2 - Continue without specifying model
            print("\n[3/4] Turn 2: Continuing conversation (no model specified)...")
            print("   Expected: Should use kimi-thinking-preview (locked from Turn 1)")

            request_id_2 = "test_turn_2"
            await ws.send(json.dumps({
                "op": "call_tool",
                "request_id": request_id_2,
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "What about quantum entanglement?",
                    "continuation_id": continuation_id
                    # NO MODEL SPECIFIED - should use kimi-thinking-preview
                }
            }))

            # Wait for response (skip ack)
            while True:
                response2 = await ws.recv()
                data2 = json.loads(response2)
                if data2.get("op") == "call_tool_res":
                    break

            if data2.get("op") == "error":
                print(f"❌ Turn 2 failed: {data2.get('error')}")
                return False
            
            model_used_2 = data2.get("metadata", {}).get("model_name")
            content_2 = data2.get("content", "")[:100]
            
            print(f"   Model used: {model_used_2}")
            print(f"   Response preview: {content_2}...")
            
            # Step 4: Verify model is locked
            print("\n[4/4] Verifying model lock...")
            print(f"   Turn 1 model: {model_used_1}")
            print(f"   Turn 2 model: {model_used_2}")
            
            if model_used_2 == model_used_1:
                print("\n" + "=" * 80)
                print("✅ SUCCESS: Model locked correctly!")
                print("=" * 80)
                print(f"   Both turns used: {model_used_1}")
                print(f"   Bug #4 fix is working as intended!")
                return True
            else:
                print("\n" + "=" * 80)
                print("❌ FAILURE: Model switched!")
                print("=" * 80)
                print(f"   Turn 1: {model_used_1}")
                print(f"   Turn 2: {model_used_2}")
                print(f"   Bug #4 fix is NOT working!")
                return False
                
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
        print("   Make sure the daemon is running:")
        print("   powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\ws_start.ps1")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_user_can_override():
    """Test that user can still explicitly override the model"""

    print("\n" + "=" * 80)
    print("Additional Test: User Can Override Model")
    print("=" * 80)

    try:
        async with websockets.connect(WS_URL) as ws:
            # Authenticate
            await ws.send(json.dumps({
                "op": "hello",
                "token": WS_TOKEN,
                "client_info": {"name": "test_override", "version": "1.0"}
            }))
            hello_resp = await ws.recv()
            if not json.loads(hello_resp).get("ok"):
                print("❌ Auth failed")
                return False

            # Turn 1: Start with kimi-thinking-preview
            print("\n[1/3] Turn 1: Starting with kimi-thinking-preview...")
            await ws.send(json.dumps({
                "op": "call_tool",
                "request_id": "override_test_1",
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Hello",
                    "model": "kimi-thinking-preview"
                }
            }))

            # Wait for response
            while True:
                response1 = await ws.recv()
                data1 = json.loads(response1)
                if data1.get("op") == "call_tool_res":
                    break

            continuation_id = data1.get("continuation_id")
            model_used_1 = data1.get("metadata", {}).get("model_name")
            print(f"   Model used: {model_used_1}")

            # Turn 2: User explicitly changes model
            print("\n[2/3] Turn 2: User explicitly changes to glm-4.6...")
            await ws.send(json.dumps({
                "op": "call_tool",
                "request_id": "override_test_2",
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Continue",
                    "continuation_id": continuation_id,
                    "model": "glm-4.6"  # User explicitly changes model
                }
            }))

            # Wait for response
            while True:
                response2 = await ws.recv()
                data2 = json.loads(response2)
                if data2.get("op") == "call_tool_res":
                    break

            model_used_2 = data2.get("metadata", {}).get("model_name")
            print(f"   Model used: {model_used_2}")
            
            # Verify user override works
            print("\n[3/3] Verifying user can override...")
            if model_used_2 == "glm-4.6":
                print("✅ SUCCESS: User override works!")
                print(f"   Turn 1: {model_used_1}")
                print(f"   Turn 2: {model_used_2} (user override)")
                return True
            else:
                print("❌ FAILURE: User override didn't work!")
                print(f"   Expected: glm-4.6")
                print(f"   Got: {model_used_2}")
                return False
                
    except Exception as e:
        print(f"❌ Error in override test: {e}")
        return False

async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("BUG #4 FIX VERIFICATION TEST SUITE")
    print("=" * 80)
    print(f"WebSocket URL: {WS_URL}")
    print(f"Auth Token: {'*' * len(WS_TOKEN) if WS_TOKEN else 'NOT SET'}")
    
    if not WS_TOKEN:
        print("\n❌ ERROR: EXAI_WS_TOKEN not set in .env file!")
        return False
    
    # Test 1: Model locking
    test1_passed = await test_model_locking()
    
    # Test 2: User override
    test2_passed = await test_user_can_override()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Model Locking):  {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (User Override):  {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("=" * 80)
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! Bug #4 fix is working correctly!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED! Bug #4 fix needs investigation!")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)

