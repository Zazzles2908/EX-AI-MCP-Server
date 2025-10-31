#!/usr/bin/env python3
"""Quick test to verify WebSocket server is accepting connections and completing handshakes."""

import asyncio
import websockets
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

async def test_connection():
    """Test WebSocket connection and handshake."""
    uri = "ws://localhost:8079"
    token = os.getenv("EXAI_WS_TOKEN", "test-token-12345")
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri, open_timeout=10) as websocket:
            print("✅ Connection established!")

            # Send hello message
            hello_msg = {
                "op": "hello",
                "session_id": "test-session-123",
                "token": token
            }
            print(f"Sending hello: {hello_msg}")
            await websocket.send(json.dumps(hello_msg))

            # Wait for hello_ack
            print("Waiting for hello_ack...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"✅ Received response: {response}")
            
            response_data = json.loads(response)
            if response_data.get("op") == "hello_ack":
                print("✅ Handshake completed successfully!")
                return True
            else:
                print(f"❌ Unexpected response: {response_data}")
                return False
                
    except asyncio.TimeoutError:
        print("❌ Timeout during handshake")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)

