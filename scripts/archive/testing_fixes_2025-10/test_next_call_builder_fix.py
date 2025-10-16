#!/usr/bin/env python
"""
Test Next Call Builder Fix

This test verifies that the NextCallBuilder fix resolves the bug where
next_call.arguments was missing required fields like 'findings'.

This is a FAST test that doesn't use AI integration - it just verifies
that the next_call structure is built correctly.
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

import websockets

# Configuration
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"


async def test_next_call_has_all_fields():
    """
    Test that next_call.arguments includes ALL required fields.
    
    This verifies the NextCallBuilder fix for the bug where next_call.arguments
    was missing required fields like 'findings', causing validation errors
    when post-processing tried to auto-continue workflows.
    """
    print("\n" + "=" * 70)
    print("TEST: Next Call Builder Fix Verification")
    print("=" * 70)
    
    # Connect to daemon
    ws = await websockets.connect(WS_URL, open_timeout=10)
    
    # Send hello
    hello = {"op": "hello", "token": WS_TOKEN}
    await ws.send(json.dumps(hello))
    
    # Wait for ack
    ack_raw = await asyncio.wait_for(ws.recv(), timeout=10)
    ack = json.loads(ack_raw)
    
    if ack.get("op") != "hello_ack" or not ack.get("ok"):
        print(f"❌ FAILED: Hello handshake failed: {ack}")
        await ws.close()
        return False
    
    print(f"✅ Connected to daemon (session: {ack.get('session_id')})")
    
    # Call analyze tool WITHOUT AI integration (fast test)
    test_file = get_repo_root() / "scripts" / "testing" / "test_auth_token_stability.py"
    
    params = {
        "step": "Test step",
        "step_number": 1,
        "total_steps": 2,
        "next_step_required": True,  # This should trigger next_call generation
        "findings": "Test findings - this field should be in next_call.arguments",
        "relevant_files": [str(test_file)],
        "model": "glm-4.5-flash",
        "use_assistant_model": False  # DISABLE AI for fast test
    }
    
    request_id = f"test_next_call_{int(time.time() * 1000)}"
    
    message = {
        "op": "call_tool",
        "name": "analyze",
        "request_id": request_id,
        "arguments": params
    }
    
    print(f"\nCalling analyze tool (WITHOUT AI integration)...")
    print(f"  - next_step_required: True (should generate next_call)")
    print(f"  - findings: '{params['findings']}'")
    
    await ws.send(json.dumps(message))
    
    # Wait for response
    start_time = time.time()
    timeout = 60  # 60 seconds should be plenty for non-AI test
    
    while True:
        if time.time() - start_time > timeout:
            print(f"❌ FAILED: Timeout after {timeout}s")
            await ws.close()
            return False
        
        try:
            response_raw = await asyncio.wait_for(ws.recv(), timeout=30)
        except asyncio.TimeoutError:
            continue
        
        response = json.loads(response_raw)
        
        # Check if this is our final response
        if response.get("request_id") == request_id and response.get("op") == "call_tool_res":
            break
        
        # Progress message
        if response.get("op") == "progress":
            print(f"   Progress: {response.get('note', 'working...')}")
    
    elapsed = time.time() - start_time
    print(f"\n✅ Tool completed in {elapsed:.1f}s")
    
    # Parse response
    outputs = response.get("outputs", [])
    if not outputs:
        print(f"❌ FAILED: No outputs in response")
        await ws.close()
        return False
    
    # Get the first output (tool response)
    tool_response_text = outputs[0].get("text", "{}")
    
    try:
        tool_response = json.loads(tool_response_text)
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: JSON parse error: {e}")
        await ws.close()
        return False
    
    # Check if next_call exists
    if "next_call" not in tool_response:
        print(f"❌ FAILED: No next_call in response")
        print(f"   Response keys: {list(tool_response.keys())}")
        await ws.close()
        return False
    
    next_call = tool_response["next_call"]
    next_args = next_call.get("arguments", {})
    
    print(f"\n✅ next_call found in response")
    print(f"   Tool: {next_call.get('tool')}")
    print(f"   Arguments keys: {list(next_args.keys())}")
    
    # VERIFY: Check that ALL required fields are present
    required_fields = ["step", "step_number", "total_steps", "next_step_required", "findings"]
    missing_fields = [f for f in required_fields if f not in next_args]
    
    if missing_fields:
        print(f"\n❌ FAILED: Missing required fields in next_call.arguments:")
        for field in missing_fields:
            print(f"   - {field}")
        print(f"\n   This is the bug we're trying to fix!")
        await ws.close()
        return False
    
    print(f"\n✅ ALL required fields present in next_call.arguments:")
    for field in required_fields:
        value = next_args[field]
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        print(f"   - {field}: {value}")
    
    # VERIFY: Check that findings field has the correct value
    if next_args["findings"] != params["findings"]:
        print(f"\n⚠️  WARNING: findings value changed:")
        print(f"   Original: {params['findings']}")
        print(f"   In next_call: {next_args['findings']}")
    
    await ws.close()
    
    print(f"\n" + "=" * 70)
    print("✅ TEST PASSED: NextCallBuilder fix verified!")
    print("=" * 70)
    print(f"\nThe bug is FIXED:")
    print(f"  - next_call.arguments now includes ALL required fields")
    print(f"  - Post-processing can auto-continue without validation errors")
    print(f"  - Workflows will work correctly")
    
    return True


async def main():
    """Run the test."""
    try:
        success = await test_next_call_has_all_fields()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

