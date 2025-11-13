#!/usr/bin/env python3
"""
Test EXAI MCP Tools with CORRECT protocol format
"""
import asyncio
import json
import websockets
import os
import uuid

async def test_status_tool():
    """Test the status tool with correct protocol"""
    print("="*60)
    print("TEST 1: Calling @exai-mcp status (CORRECTED PROTOCOL)")
    print("="*60)
    
    uri = 'ws://127.0.0.1:3000'
    token = os.getenv("EXAI_WS_TOKEN", "")
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    
    async with websockets.connect(uri) as ws:
        # Send hello
        await ws.send(json.dumps({
            "op": "hello",
            "session_id": session_id,
            "token": token
        }))
        await ws.recv()  # ack
        
        print("[OK] Connected")
        
        # Send tool call with CORRECT format
        req_id = str(uuid.uuid4())
        await ws.send(json.dumps({
            "op": "tool_call",  # Correct!
            "request_id": req_id,
            "tool": {"name": "status"},  # Correct format!
            "arguments": {}
        }))
        
        print("[OK] Sent tool_call request")
        
        # Read response
        timeout = 15
        try:
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                msg = json.loads(raw)
                
                if msg.get("op") == "call_tool_ack":
                    print("[OK] Received ack, waiting for result...")
                    continue
                
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == req_id:
                    if msg.get("error"):
                        print(f"[ERROR] Tool failed: {msg.get('error')}")
                    else:
                        print(f"[SUCCESS] Tool call succeeded!")
                        print(f"[OK] Outputs: {msg.get('outputs', [])}")
                    return
                
                print(f"[DEBUG] Ignoring message: {msg.get('op')}")
        except asyncio.TimeoutError:
            print(f"[ERROR] Timeout waiting for response")

async def test_chat_tool():
    """Test the chat tool with correct protocol"""
    print("\n" + "="*60)
    print("TEST 2: Calling @exai-mcp chat (CORRECTED PROTOCOL)")
    print("="*60)
    
    uri = 'ws://127.0.0.1:3000'
    token = os.getenv("EXAI_WS_TOKEN", "")
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    
    async with websockets.connect(uri) as ws:
        # Send hello
        await ws.send(json.dumps({
            "op": "hello",
            "session_id": session_id,
            "token": token
        }))
        await ws.recv()  # ack
        
        print("[OK] Connected")
        
        # Send tool call with CORRECT format
        req_id = str(uuid.uuid4())
        await ws.send(json.dumps({
            "op": "tool_call",  
            "request_id": req_id,
            "tool": {"name": "chat"},
            "arguments": {"prompt": "Please respond with: 'EXAI MCP is working via corrected protocol!'"}
        }))
        
        print("[OK] Sent tool_call request")
        
        # Read streaming response
        timeout = 30
        try:
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                msg = json.loads(raw)
                
                if msg.get("op") == "stream_data":
                    content = msg.get("data", {}).get("content", "")
                    if content:
                        print(f"[STREAM] {content}")
                elif msg.get("op") == "stream_complete":
                    print("\n[SUCCESS] Stream complete!")
                    return
                elif msg.get("op") == "call_tool_res" and msg.get("request_id") == req_id:
                    if msg.get("error"):
                        print(f"[ERROR] Tool failed: {msg.get('error')}")
                    else:
                        print(f"[SUCCESS] Tool call succeeded!")
                    return
                elif msg.get("op") == "call_tool_ack":
                    print("[OK] Received ack...")
                    continue
        except asyncio.TimeoutError:
            print(f"[ERROR] Timeout waiting for response")

async def main():
    print("Testing EXAI MCP with CORRECTED Protocol Format")
    print("="*60)
    
    await test_status_tool()
    await test_chat_tool()
    
    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
