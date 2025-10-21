#!/usr/bin/env python3
"""
Test WebSocket connection from inside container.
"""

import asyncio
import json
import websockets


async def test_connection():
    """Test WebSocket connection."""
    try:
        print("Connecting to ws://localhost:8079...")
        async with websockets.connect('ws://localhost:8079') as ws:
            print("✅ Connected successfully!")

            # Step 1: Send MCP hello message
            hello_msg = {
                "op": "hello",
                "client_name": "test-client",
                "client_version": "1.0.0"
            }

            print(f"Sending hello: {json.dumps(hello_msg, indent=2)}")
            await ws.send(json.dumps(hello_msg))

            print("Waiting for hello_ack...")
            hello_response = await asyncio.wait_for(ws.recv(), timeout=10)
            print(f"✅ Received hello_ack: {hello_response[:200]}...")

            # Step 2: Send a tool call request
            request = {
                "op": "call_tool",
                "request_id": "test-connection",
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Hello, this is a test"
                }
            }

            print(f"\nSending tool call: {json.dumps(request, indent=2)}")
            await ws.send(json.dumps(request))

            print("Waiting for tool response...")
            response = await asyncio.wait_for(ws.recv(), timeout=30)

            print(f"✅ Received response: {response[:200]}...")

            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)

