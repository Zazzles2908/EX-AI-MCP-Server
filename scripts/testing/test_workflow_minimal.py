#!/usr/bin/env python
"""
Minimal WorkflowTools Test - Debug version

Tests a single WorkflowTool with detailed error reporting.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Bootstrap
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root
load_env()

import websockets


async def test_analyze():
    """Test analyze tool with minimal params."""
    ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
    ws_token = os.getenv("EXAI_WS_TOKEN", "")
    
    print(f"Connecting to {ws_url}...")
    ws = await websockets.connect(ws_url)
    
    try:
        # Send hello
        hello_msg = {
            "op": "hello",
            "token": ws_token,
            "client_info": {"name": "minimal_test", "version": "1.0"}
        }
        await ws.send(json.dumps(hello_msg))
        
        # Wait for hello_ack
        response = await asyncio.wait_for(ws.recv(), timeout=5.0)
        response_data = json.loads(response)
        print(f"Hello response: {response_data}")
        
        if not response_data.get("ok"):
            print(f"❌ Auth failed: {response_data}")
            return False
        
        # Send tool call
        call_msg = {
            "op": "call_tool",
            "request_id": "test_analyze_minimal",
            "name": "analyze",
            "arguments": {
                "step": "Test analyze tool",
                "step_number": 1,
                "total_steps": 1,
                "next_step_required": False,
                "findings": "Testing analyze tool",
                "relevant_files": [str(get_repo_root() / "src" / "bootstrap" / "env_loader.py")],
                "model": "glm-4.5-flash",
                "use_assistant_model": True
            }
        }
        
        print(f"\nSending tool call:")
        print(json.dumps(call_msg, indent=2))
        await ws.send(json.dumps(call_msg))
        
        # Wait for response (keep connection open until tool completes)
        result = None
        error_occurred = False

        while True:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=120.0)
            except asyncio.TimeoutError:
                print(f"⚠️ No message received in 120s, continuing to wait...")
                continue

            response_data = json.loads(response)
            op = response_data.get('op')
            print(f"\nReceived: {op}")

            if op == "call_tool_ack":
                print(f"✅ Tool call acknowledged, waiting for result...")
                continue

            if op == "call_tool_res":
                print(f"✅ Tool result received!")
                if "error" in response_data:
                    print(f"❌ Tool returned error: {response_data.get('error')}")
                    error_occurred = True
                    break
                else:
                    print(f"✅ Tool completed successfully")
                    print(f"Result preview: {str(response_data.get('result', {}))[:200]}...")
                    result = True
                    break

            if op == "error":
                print(f"❌ Error: {json.dumps(response_data, indent=2)}")
                error_occurred = True
                break

            if op == "progress":
                msg = response_data.get('message', 'No message')
                print(f"📊 Progress: {msg}")
                continue

            # Unknown message type
            print(f"⚠️ Unknown message type: {op}")

        # Close connection AFTER receiving final result
        await ws.close()
        return result if result is not None else False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        # Close connection on exception
        try:
            await ws.close()
        except:
            pass
        return False


async def main():
    print("=" * 70)
    print("MINIMAL WORKFLOWTOOLS TEST")
    print("=" * 70)
    result = await test_analyze()
    print(f"\nResult: {'✅ PASS' if result else '❌ FAIL'}")
    return 0 if result else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

