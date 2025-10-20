"""
Quick test to verify Pydantic validation error is fixed.
"""
import asyncio
import json
import sys
import uuid
from datetime import datetime

try:
    import websockets
except ImportError:
    print("ERROR: websockets module not installed")
    sys.exit(1)

from dotenv import load_dotenv
import os

load_dotenv()

WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URI = f"ws://{WS_HOST}:{WS_PORT}"


async def test_analyze():
    """Test analyze tool for Pydantic error"""
    request_id = uuid.uuid4().hex
    session_id = f"test-{uuid.uuid4().hex[:6]}"
    
    arguments = {
        "step": "Test Pydantic fix",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Testing validation error fix",
        "use_assistant_model": False,  # Disable expert analysis for speed
        "model": "glm-4.5-flash",
    }
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing analyze tool...")
    
    try:
        async with websockets.connect(WS_URI, max_size=20 * 1024 * 1024) as websocket:
            # Hello handshake
            await websocket.send(json.dumps({
                "op": "hello",
                "session_id": session_id,
                "token": WS_TOKEN
            }))
            
            ack = json.loads(await websocket.recv())
            if not ack.get("ok"):
                print(f"❌ Auth failed: {ack}")
                return False
            
            # Send tool call
            await websocket.send(json.dumps({
                "op": "call_tool",
                "request_id": request_id,
                "name": "analyze_EXAI-WS",
                "arguments": arguments
            }))
            
            # Wait for response
            while True:
                response = json.loads(await asyncio.wait_for(websocket.recv(), timeout=30))

                if response.get("op") == "call_tool_ack":
                    # Acknowledgment received, continue waiting
                    continue

                if response.get("op") == "progress":
                    continue

                if response.get("op") == "call_tool_res":
                    if response.get("error"):
                        print(f"❌ Tool error: {response.get('error')}")
                        return False

                    print(f"✅ Tool completed successfully!")
                    return True

                print(f"❌ Unexpected response: {response.get('op')}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


async def main():
    print("="*60)
    print("Testing Pydantic Validation Fix")
    print("="*60)
    
    success = await test_analyze()
    
    print("\n" + "="*60)
    if success:
        print("✅ TEST PASSED - No Pydantic validation error!")
        print("\nCheck terminal logs - should NOT see:")
        print("  'ERROR tools.workflow.orchestration: Error in analyze work'")
        return 0
    else:
        print("❌ TEST FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

