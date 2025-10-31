"""Quick WebSocket connection test"""
import asyncio
import websockets
import json

async def test_connection():
    url = "ws://localhost:8080/events"
    print(f"Attempting to connect to {url}...")

    try:
        async with websockets.connect(url) as ws:
            print("✅ Connected successfully!")
            
            # Send test event
            test_event = {"type": "test", "data": "hello"}
            await ws.send(json.dumps(test_event))
            print(f"Sent: {test_event}")
            
            # Receive response
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Received: {response}")
            
    except asyncio.TimeoutError:
        print("❌ Connection timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())

