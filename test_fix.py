#!/usr/bin/env python3
"""
Minimal WebSocket test to verify the fix
"""
import asyncio
import json
import websockets
import sys

async def test_websocket_fix():
    """Test that WebSocket responses are now working"""
    print("Testing WebSocket response fix...")

    try:
        # Connect without timeout parameter (websockets 15.x compatibility)
        uri = "ws://127.0.0.1:3010"
        async with websockets.connect(uri) as ws:
            print("Connected to WebSocket")

            # Send hello with token
            hello = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "token": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
            }
            await ws.send(json.dumps(hello))
            print("Hello sent with token")

            # Receive hello_ack
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            result = json.loads(response)
            print(f"Hello ACK received: {result.get('ok')}")

            # Send a simple tool call
            tool_call = {
                "op": "tool_call",
                "name": "version",
                "arguments": {}
            }
            await ws.send(json.dumps(tool_call))
            print("Tool call sent (version)")

            # Wait for response
            print("Waiting for tool response...")
            response = await asyncio.wait_for(ws.recv(), timeout=15)
            result = json.loads(response)

            print(f"\n=== RESPONSE RECEIVED ===")
            print(f"Operation: {result.get('op')}")
            print(f"Request ID: {result.get('request_id')}")

            if result.get('op') == 'call_tool_res':
                print("SUCCESS: Received call_tool_res with tool outputs!")
                outputs = result.get('outputs', [])
                print(f"Number of outputs: {len(outputs)}")
                if outputs:
                    print(f"First output type: {outputs[0].get('type')}")
                    print(f"First output preview: {str(outputs[0].get('text', ''))[:100]}")
                return True
            elif result.get('op') == 'stream_complete':
                print("ISSUE: Only received stream_complete, missing call_tool_res")
                return False
            else:
                print(f"Unexpected response: {result}")
                return False

    except asyncio.TimeoutError:
        print("ERROR: Timeout waiting for response")
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket_fix())
    sys.exit(0 if success else 1)
