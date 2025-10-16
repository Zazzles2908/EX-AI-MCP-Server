#!/usr/bin/env python3
"""Quick test script to validate the kimi_upload_and_extract fix."""

import asyncio
import websockets
import json
import os

async def test_kimi_upload():
    """Test kimi_upload_and_extract with the fixed code."""
    uri = "ws://127.0.0.1:8079"
    token = os.getenv("EXAI_WS_TOKEN", "")
    
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
        # Send hello message (daemon protocol)
        hello_msg = {
            "op": "hello",
            "token": token
        }
        await websocket.send(json.dumps(hello_msg))
        response = await websocket.recv()
        hello_result = json.loads(response)

        if hello_result.get("op") != "hello_ack" or not hello_result.get("ok"):
            print(f"❌ Hello failed: {hello_result.get('error', 'unknown')}")
            return False

        session_id = hello_result.get("session_id", "N/A")
        print(f"✅ Connected. Session: {session_id}")
        
        # Test kimi_upload_and_extract
        test_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "kimi_upload_and_extract",
                "arguments": {
                    "files": ["c:/Project/EX-AI-MCP-Server/test_files/sample_code.py"],
                    "purpose": "file-extract"
                }
            }
        }
        
        print("\n📤 Testing kimi_upload_and_extract...")
        print(f"   File: test_files/sample_code.py (1,317 bytes)")
        
        await websocket.send(json.dumps(test_msg))
        response = await websocket.recv()
        result = json.loads(response)
        
        if "error" in result:
            print(f"\n❌ FAILED: {result['error'].get('message', 'Unknown error')}")
            print(f"   Error details: {result['error']}")
            return False
        else:
            print(f"\n✅ SUCCESS!")
            content = result.get("result", {}).get("content", [])
            if content:
                first_msg = content[0]
                text = first_msg.get("text", "")
                print(f"   Extracted {len(text)} characters")
                print(f"   Preview: {text[:200]}...")
            return True

if __name__ == "__main__":
    success = asyncio.run(test_kimi_upload())
    exit(0 if success else 1)

