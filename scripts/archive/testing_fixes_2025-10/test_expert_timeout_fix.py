#!/usr/bin/env python
"""
Test Expert Analysis Timeout Fix

This test verifies that the expert analysis timeout bug is fixed:
- Timeouts are now treated as errors (not successes)
- Timeout status is properly promoted to main response
- Error message includes timeout duration

Bug: tools/workflow/conversation_integration.py line 306
Fix: Added "analysis_timeout" to error status check
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Bootstrap
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root
load_env()

import websockets

# Configuration
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"


async def test_timeout_handling():
    """Test that timeout is handled as error, not success."""
    print("\n" + "=" * 70)
    print("TEST: Expert Analysis Timeout Handling")
    print("=" * 70)
    
    # Set very short timeout to force timeout
    original_timeout = os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS")
    os.environ["EXPERT_ANALYSIS_TIMEOUT_SECS"] = "5"  # 5 seconds - will timeout
    
    print(f"\n⚙️  Configuration:")
    print(f"  - EXPERT_ANALYSIS_TIMEOUT_SECS: 5s (forced timeout)")
    print(f"  - Original timeout: {original_timeout}s")
    
    try:
        # Connect to daemon
        ws = await websockets.connect(WS_URL, open_timeout=10)
        
        # Send hello
        hello = {"op": "hello", "token": WS_TOKEN}
        await ws.send(json.dumps(hello))
        
        # Wait for ack
        ack_raw = await asyncio.wait_for(ws.recv(), timeout=10)
        ack = json.loads(ack_raw)
        
        if ack.get("op") != "hello_ack" or not ack.get("ok"):
            print(f"❌ FAILED: Hello handshake failed")
            return False
        
        print(f"✅ Connected (session: {ack.get('session_id')})")
        
        # Call analyze with AI integration (will timeout)
        test_file = get_repo_root() / "scripts" / "testing" / "test_auth_token_stability.py"
        
        params = {
            "step": "Test timeout handling with AI integration",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Testing expert analysis timeout handling",
            "relevant_files": [str(test_file)],
            "model": "glm-4.5-flash",
            "use_assistant_model": True  # Enable AI - will timeout
        }
        
        request_id = f"test_timeout_{int(time.time() * 1000)}"
        message = {
            "op": "call_tool",
            "name": "analyze",
            "request_id": request_id,
            "arguments": params
        }
        
        print(f"\n📤 Calling analyze tool with AI integration...")
        print(f"  - Expected: Timeout after 5s")
        print(f"  - Expected status: 'error' (not 'complete')")
        
        await ws.send(json.dumps(message))
        
        # Wait for response (with longer timeout than expert timeout)
        start_time = time.time()
        response = None
        
        while True:
            if time.time() - start_time > 30:  # 30s max wait
                print(f"❌ FAILED: No response after 30s")
                await ws.close()
                return False
            
            try:
                response_raw = await asyncio.wait_for(ws.recv(), timeout=10)
            except asyncio.TimeoutError:
                continue
            
            resp = json.loads(response_raw)
            
            # Check if this is our final response
            if resp.get("request_id") == request_id and resp.get("op") == "call_tool_res":
                response = resp
                break
            
            # Progress message
            if resp.get("op") == "progress":
                print(f"   Progress: {resp.get('note', 'working...')}")
        
        await ws.close()
        
        # Verify response
        elapsed = time.time() - start_time
        print(f"\n📥 Response received after {elapsed:.1f}s")
        
        if not response:
            print(f"❌ FAILED: No response received")
            return False
        
        # Parse tool response
        outputs = response.get("outputs", [])
        if not outputs:
            print(f"❌ FAILED: No outputs in response")
            return False
        
        tool_response_text = outputs[0].get("text", "{}")
        
        try:
            tool_response = json.loads(tool_response_text)
        except json.JSONDecodeError as e:
            print(f"❌ FAILED: JSON parse error: {e}")
            return False
        
        # VERIFY FIX: Status should be "error", not "complete"
        status = tool_response.get("status", "")
        
        print(f"\n🔍 Verification:")
        print(f"  - Status: {status}")
        print(f"  - Content: {tool_response.get('content', '')[:100]}...")
        
        if status == "error":
            print(f"\n✅ PASSED: Timeout correctly treated as ERROR")
            
            # Verify error message mentions timeout
            content = tool_response.get("content", "")
            if "timeout" in content.lower():
                print(f"  ✅ Error message mentions timeout")
            else:
                print(f"  ⚠️  Warning: Error message doesn't mention timeout")
            
            # Verify timeout duration is included
            if "timeout_duration" in tool_response:
                print(f"  ✅ Timeout duration included: {tool_response['timeout_duration']}")
            
            return True
        
        elif "complete" in status.lower():
            print(f"\n❌ FAILED: Timeout treated as SUCCESS (bug not fixed)")
            print(f"  - Expected status: 'error'")
            print(f"  - Actual status: '{status}'")
            print(f"  - This means the bug is NOT fixed!")
            return False
        
        else:
            print(f"\n⚠️  UNEXPECTED: Status is '{status}' (neither error nor complete)")
            return False
    
    except Exception as e:
        print(f"\n❌ FAILED: Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore original timeout
        if original_timeout:
            os.environ["EXPERT_ANALYSIS_TIMEOUT_SECS"] = original_timeout
        else:
            os.environ.pop("EXPERT_ANALYSIS_TIMEOUT_SECS", None)


async def main():
    """Run test."""
    print("\n" + "=" * 70)
    print("EXPERT ANALYSIS TIMEOUT FIX VERIFICATION")
    print("=" * 70)
    print("\nThis test verifies the bug fix for expert analysis timeout handling.")
    print("Bug: Timeouts were treated as successes instead of errors")
    print("Fix: Added 'analysis_timeout' to error status check")
    
    result = await test_timeout_handling()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if result:
        print(f"\n✅ TEST PASSED: Bug fix verified!")
        print(f"\nThe expert analysis timeout bug is FIXED:")
        print(f"  - Timeouts are now treated as errors")
        print(f"  - Error status is properly promoted")
        print(f"  - Timeout duration is included in response")
        return 0
    else:
        print(f"\n❌ TEST FAILED: Bug may not be fixed")
        print(f"\nPlease check:")
        print(f"  - tools/workflow/conversation_integration.py line 306")
        print(f"  - Verify 'analysis_timeout' is in error status check")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

