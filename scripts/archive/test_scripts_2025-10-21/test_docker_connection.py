"""
Test Direct Connection to Docker Daemon
========================================

This script tests direct WebSocket connection to the EXAI daemon running in Docker.

Usage:
    python scripts/test_docker_connection.py

What it does:
    1. Connects to ws://localhost:8079
    2. Sends an MCP initialize request
    3. Calls the chat tool with a simple prompt
    4. Displays the response

Author: EXAI Team
Date: 2025-10-14
"""

import asyncio
import json
import websockets
from datetime import datetime


async def test_connection():
    """Test WebSocket connection to Docker daemon."""
    
    uri = "ws://localhost:8079"
    print(f"\n{'='*60}")
    print(f"🔌 Testing Connection to EXAI Docker Daemon")
    print(f"{'='*60}\n")
    print(f"📍 URI: {uri}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Connect to WebSocket
        print("🔄 Connecting to daemon...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!\n")

            # Step 1: Send hello (EXAI daemon protocol requirement)
            print("📤 Sending hello message...")
            hello_msg = {
                "op": "hello",
                "token": "test-token-12345"  # Auth token from .env.docker
            }
            await websocket.send(json.dumps(hello_msg))

            # Wait for hello_ack
            response = await websocket.recv()
            hello_ack = json.loads(response)

            if not hello_ack.get("ok"):
                print(f"❌ Hello failed: {hello_ack.get('error')}")
                return

            session_id = hello_ack.get("session_id")
            print(f"✅ Hello acknowledged! Session ID: {session_id}\n")
            
            # Step 2: Call chat tool (using EXAI daemon protocol)
            print("📤 Calling chat tool...")
            chat_request = {
                "op": "call_tool",
                "request_id": "test-123",
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Say hello and confirm you're running in Docker!"
                }
            }

            await websocket.send(json.dumps(chat_request))

            # Wait for responses (daemon sends multiple messages: ack, progress, result)
            print("⏳ Waiting for response...\n")

            result_received = False
            while not result_received:
                response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                msg = json.loads(response)
                op = msg.get("op")

                if op == "call_tool_ack":
                    print(f"✅ Tool call acknowledged")
                elif op == "progress":
                    note = msg.get("note", "")
                    print(f"⏳ Progress: {note}")
                elif op == "call_tool_res":
                    result_received = True

                    # Display result
                    print(f"\n{'='*60}")
                    print(f"📨 EXAI Response:")
                    print(f"{'='*60}\n")

                    if "error" in msg:
                        print(f"❌ Error: {msg['error']}")
                    else:
                        outputs = msg.get("outputs", [])
                        for output in outputs:
                            if output.get("type") == "text":
                                print(output.get("text", ""))
                else:
                    print(f"📥 Received: {op}")
            
            print(f"\n{'='*60}")
            print(f"✅ Test Complete!")
            print(f"{'='*60}\n")
            
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response (30s)")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting EXAI Docker Connection Test...\n")
    asyncio.run(test_connection())

