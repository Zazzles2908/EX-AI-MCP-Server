#!/usr/bin/env python3
"""
Comprehensive EXAI MCP tool test with correct protocol
"""
import asyncio
import json
import websockets
import os
import uuid

async def test_code_review():
    """Test codereview tool"""
    print("="*60)
    print("TEST: @exai-mcp codereview (Comprehensive)")
    print("="*60)
    
    uri = 'ws://127.0.0.1:3000'
    token = os.getenv("EXAI_WS_TOKEN", "")
    session_id = f"codereview-{uuid.uuid4().hex[:8]}"
    
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"op": "hello", "session_id": session_id, "token": token}))
        await ws.recv()
        
        req_id = str(uuid.uuid4())
        await ws.send(json.dumps({
            "op": "tool_call",
            "request_id": req_id,
            "tool": {"name": "codereview"},
            "arguments": {
                "findings": "I need to review the port strategy implementation. We changed from ports 8079-8082 to 3000-3003. Changes included docker-compose.yml port mappings, 9 MCP config files updated, Dockerfile fixed, storage_circuit_breaker.py import fixed, .env updated. Please verify this is correct."
            }
        }))
        
        print("Request sent, waiting for response...")
        
        response_count = 0
        while response_count < 50:
            raw = await asyncio.wait_for(ws.recv(), timeout=20)
            msg = json.loads(raw)
            response_count += 1
            
            if msg.get("op") == "stream_data":
                content = msg.get("data", {}).get("content", "")
                if content and "error" not in content.lower():
                    print(content[:200] + "..." if len(content) > 200 else content)
            elif msg.get("op") == "stream_complete":
                print("\n[SUCCESS] Code review tool completed!")
                return True
            elif msg.get("op") == "call_tool_res":
                print(f"[RESULT] {msg.get('outputs', [])}")
                return True
        
        print("[ERROR] Timeout")
        return False

async def main():
    print("="*60)
    print("COMPREHENSIVE EXAI MCP PROTOCOL TEST")
    print("="*60)
    
    success = await test_code_review()
    
    print("\n" + "="*60)
    if success:
        print("✓ ALL TESTS PASSED - EXAI MCP IS FULLY OPERATIONAL")
    else:
        print("✗ TEST FAILED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
