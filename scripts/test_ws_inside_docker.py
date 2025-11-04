#!/usr/bin/env python3
"""
Test WebSocket connection from inside Docker container
"""

import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://127.0.0.1:8079"
    print(f"Testing connection to {uri} from inside Docker...")
    
    try:
        async with websockets.connect(uri, ping_interval=None) as websocket:
            print("✅ Connected successfully!")
            
            # Send hello message
            hello_msg = {
                "op": "hello",
                "token": "test-token-12345"
            }
            print(f"Sending: {hello_msg}")
            await websocket.send(json.dumps(hello_msg))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"✅ Received response: {response}")
            
            return True
            
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
        return False
    except ConnectionRefusedError:
        print("❌ Connection refused - server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)

