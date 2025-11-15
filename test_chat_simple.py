#!/usr/bin/env python3
"""Simple MCP Chat Test"""

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

async def test_chat():
    load_dotenv('.env')
    
    host = "127.0.0.1"
    port = "3010"
    token = os.getenv("EXAI_WS_TOKEN", "")
    
    uri = f"ws://{host}:{port}"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send hello
            hello_msg = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"},
                "token": token
            }
            
            await websocket.send(json.dumps(hello_msg))
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(response)
            print(f"Hello response: {data.get('ok')}")
            
            # Test chat tool
            chat_msg = {
                "op": "call_tool",
                "id": "test_chat",
                "name": "chat",
                "arguments": {
                    "prompt": "Hello! Please respond with a brief greeting to confirm the EX-AI MCP system is working.",
                    "model": "auto"
                }
            }
            
            print("Testing chat tool...")
            await websocket.send(json.dumps(chat_msg))
            response = await asyncio.wait_for(websocket.recv(), timeout=60)
            data = json.loads(response)
            print(f"Chat response: {data}")
            
            # Check if we got a response
            result = data.get("outputs", data.get("result", []))
            if result:
                print("✓ Chat tool responded successfully!")
                print(f"Response: {result[0].get('text', '')[:200]}...")
                return True
            else:
                print("✗ Chat tool failed")
                return False
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_chat())
    print(f"Test {'PASSED' if success else 'FAILED'}")