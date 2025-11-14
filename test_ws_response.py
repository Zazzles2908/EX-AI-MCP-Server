#!/usr/bin/env python3
"""
Simple WebSocket test to isolate response issue
"""

import asyncio
import json
import websockets

async def test_response():
    """Test if responses are being sent"""
    print("Testing WebSocket response...")

    try:
        async with websockets.connect("ws://127.0.0.1:3010", timeout=5) as ws:
            print("✓ Connected")

            # Send hello
            hello = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "token": ""
            }
            await ws.send(json.dumps(hello))
            print("✓ Hello sent")

            # Receive hello_ack
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            result = json.loads(response)
            print(f"✓ Hello ACK: {result.get('ok')}")

            # Test a simple tool that should respond quickly
            await ws.send(json.dumps({
                "op": "tool_call",
                "name": "version",
                "arguments": {}
            }))
            print("✓ Version tool call sent")

            # Wait for response with shorter timeout
            print("Waiting for response...")
            response = await asyncio.wait_for(ws.recv(), timeout=15)
            result = json.loads(response)
            print(f"✓ Received response: {result.get('op', 'unknown')}")

            return True

    except asyncio.TimeoutError:
        print("✗ Timeout waiting for response")
        return False
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_response())
    exit(0 if success else 1)
