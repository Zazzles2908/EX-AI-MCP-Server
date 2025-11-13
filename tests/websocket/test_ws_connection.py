#!/usr/bin/env python3
"""
Quick test to verify WebSocket server is responding on port 8079
"""

import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://127.0.0.1:8079"  # Changed from localhost to 127.0.0.1
    print(f"Testing connection to {uri}...")

    try:
        print("Attempting websockets.connect()...")
        websocket = await websockets.connect(uri, ping_interval=None, open_timeout=10)
        print(f"✅ WebSocket connected! State: {websocket.state}")

        try:
            # Send hello message
            hello_msg = {
                "op": "hello",
                "token": "test-token-12345"
            }
            print(f"Sending: {hello_msg}")
            await websocket.send(json.dumps(hello_msg))
            print("✅ Message sent successfully")

            # Wait for response
            print("Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"✅ Received response: {response}")

            return True
        finally:
            await websocket.close()
            print("WebSocket closed")

    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
        return False
    except ConnectionRefusedError:
        print("❌ Connection refused - server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)

