#!/usr/bin/env python3
"""
Simple Kimi test to diagnose timeout issues
"""

import asyncio
import websockets
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_kimi():
    """Test single Kimi request"""
    uri = "ws://localhost:8079"
    
    print("Connecting to WebSocket...")
    async with websockets.connect(uri) as websocket:
        print("Connected!")
        
        # Initialize session
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("Sending initialize...")
        await websocket.send(json.dumps(init_msg))
        response = await websocket.recv()
        print(f"Initialize response: {response[:200]}...")
        
        # Send Kimi chat request
        chat_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Say hello in one sentence.",
                    "model": "kimi-k2-0905-preview",
                    "temperature": 0.7,
                    "use_websearch": False
                }
            }
        }
        
        print("\nSending Kimi chat request...")
        print(f"Model: kimi-k2-0905-preview")
        print(f"Prompt: Say hello in one sentence.")
        
        await websocket.send(json.dumps(chat_msg))
        
        print("\nWaiting for response...")
        response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
        
        result = json.loads(response)
        print(f"\nResponse received!")
        print(f"Status: {result.get('result', {}).get('status', 'unknown')}")
        
        if 'result' in result and 'content' in result['result']:
            content_preview = result['result']['content'][:200]
            print(f"Content preview: {content_preview}...")
        
        print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(test_kimi())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

