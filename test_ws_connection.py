#!/usr/bin/env python3
"""Test WebSocket connection to EXAI daemon"""

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

async def test_daemon_connection():
    """Test WebSocket connection to the EXAI daemon"""
    
    # Load environment
    load_dotenv('.env')
    
    # Get configuration
    host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
    port = os.getenv("EXAI_WS_PORT", "3010")
    token = os.getenv("EXAI_WS_TOKEN", "")
    
    uri = f"ws://{host}:{port}"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Send hello message
            hello_msg = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
                "token": token
            }
            
            print("Sending hello message...")
            await websocket.send(json.dumps(hello_msg))
            
            # Wait for response
            print("Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            
            print(f"Response: {response}")
            
            data = json.loads(response)
            if data.get("ok"):
                print("SUCCESS: Daemon connection successful!")
                
                # Try listing tools
                print("Testing list_tools...")
                list_msg = {
                    "op": "list_tools",
                    "id": "test_list"
                }
                
                await websocket.send(json.dumps(list_msg))
                tools_response = await asyncio.wait_for(websocket.recv(), timeout=10)
                print(f"Tools response: {tools_response}")
                
                return True
            else:
                print(f"ERROR: Daemon rejected connection: {data.get('error', 'Unknown error')}")
                return False
                
    except asyncio.TimeoutError:
        print("ERROR: Timeout connecting to daemon")
        return False
    except Exception as e:
        print(f"ERROR: Error connecting to daemon: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_daemon_connection())
    exit(0 if success else 1)