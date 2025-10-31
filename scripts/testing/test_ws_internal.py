"""Test WebSocket from inside container"""
import asyncio
import websockets
import json

async def test():
    try:
        print("Connecting to ws://localhost:8080/events...")
        ws = await websockets.connect('ws://localhost:8080/events')
        print("✅ Connected!")
        
        await ws.send(json.dumps({'type': 'test', 'data': 'hello'}))
        print("Sent test event")
        
        response = await ws.recv()
        print(f"Received: {response}")
        
        await ws.close()
        print("✅ Test successful!")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test())

