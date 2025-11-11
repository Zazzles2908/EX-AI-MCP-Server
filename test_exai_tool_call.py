#!/usr/bin/env python
"""Test full EXAI tool execution"""
import asyncio
import websockets
import json
import sys

TOKEN = "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"

async def test_tool_execution():
    print("Testing EXAI Tool Execution")
    print("=" * 70)
    
    try:
        async with websockets.connect("ws://127.0.0.1:3000", open_timeout=5) as ws:
            # Hello
            print("\n[1] Sending hello...")
            await ws.send(json.dumps({"op": "hello", "token": TOKEN}))
            resp = await asyncio.wait_for(ws.recv(), timeout=5)
            result = json.loads(resp)
            print(f"    Result: {result.get('ok')}")
            
            # List tools
            print("\n[2] Listing tools...")
            await ws.send(json.dumps({"op": "list_tools", "request_id": "test-1"}))
            resp = await asyncio.wait_for(ws.recv(), timeout=10)
            tools_result = json.loads(resp)
            tools = tools_result.get('tools', [])
            print(f"    Found {len(tools)} tools")
            for tool in tools:
                print(f"      - {tool.get('name')}")
            
            # Test chat tool
            print("\n[3] Testing 'chat' tool with GLM model...")
            await ws.send(json.dumps({
                "op": "tool_call",
                "request_id": "test-2",
                "tool": {"name": "chat"},
                "arguments": {
                    "message": "Write a short Python function to calculate fibonacci numbers. Return only the code.",
                    "model": "glm-4.5-flash"
                }
            }))
            
            print("    Waiting for response...")
            # Receive multiple messages
            response_count = 0
            final_text = ""
            
            while response_count < 20:  # Max 20 messages
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=30)
                    msg = json.loads(resp)
                    op = msg.get('op')
                    
                    if op == 'call_tool_ack':
                        print(f"    [ACK] Request accepted, timeout: {msg.get('timeout', 'N/A')}s")
                    elif op == 'progress':
                        print(f"    [PROGRESS] {msg.get('message', 'Processing...')}")
                    elif op == 'call_tool_res' and msg.get('request_id') == 'test-2':
                        print(f"    [RESULT] Received final response")
                        if 'text' in msg:
                            final_text = msg['text']
                            print(f"\n    Response preview:")
                            print("    " + final_text[:200].replace('\n', '\n    ') + "...")
                        return True
                    elif op:
                        print(f"    [MSG] {op}")
                    
                    response_count += 1
                    
                except asyncio.TimeoutError:
                    print("    [TIMEOUT] No more messages")
                    break
            
            if final_text:
                print("\n    [SUCCESS] Tool executed successfully")
                return True
            else:
                print("\n    [INCOMPLETE] No final result received")
                return False
                
    except Exception as e:
        print(f"\n    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tool_execution())
    print("\n" + "=" * 70)
    if success:
        print("RESULT: EXAI MCP TOOLS ARE WORKING!")
    else:
        print("RESULT: Issues detected")
    print("=" * 70)
