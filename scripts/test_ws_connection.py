#!/usr/bin/env python3
"""Simple WebSocket connection test"""
import asyncio
import websockets
import json

async def test_connection():
    """Test basic WebSocket connection"""
    try:
        print("Connecting to ws://127.0.0.1:8079...")
        async with websockets.connect("ws://127.0.0.1:8079", open_timeout=5) as ws:
            print("✅ Connected successfully!")
            
            # Send hello message
            hello_msg = {
                "op": "hello",
                "token": "test-token-12345"
            }
            print(f"Sending hello: {hello_msg}")
            await ws.send(json.dumps(hello_msg))
            
            # Wait for hello_ack
            print("Waiting for hello_ack...")
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"✅ Received: {response}")
            
            return True
    except asyncio.TimeoutError:
        print("❌ Connection timeout!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")

