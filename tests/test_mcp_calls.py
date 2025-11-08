#!/usr/bin/env python3
"""
Test EXAI MCP Tools via proper MCP protocol
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from scripts.baseline_collection.mcp_client import MCPWebSocketClient

async def test_status_tool():
    """Test the status tool"""
    print("="*60)
    print("TEST 1: Calling @exai-mcp status")
    print("="*60)
    
    client = MCPWebSocketClient(
        host="127.0.0.1",
        port=3000,
        token=os.getenv("EXAI_WS_TOKEN", "")
    )
    
    try:
        await client.connect()
        success, outputs, error = await client.call_tool("status", {})
        
        if success:
            print("[OK] Status tool call SUCCESSFUL")
            print(f"[OK] Outputs: {outputs}")
        else:
            print(f"[ERROR] Status tool call FAILED: {error}")
    finally:
        await client.disconnect()

async def test_chat_tool():
    """Test the chat tool"""
    print("\n" + "="*60)
    print("TEST 2: Calling @exai-mcp chat")
    print("="*60)
    
    client = MCPWebSocketClient(
        host="127.0.0.1",
        port=3000,
        token=os.getenv("EXAI_WS_TOKEN", "")
    )
    
    try:
        await client.connect()
        # Note: chat tool uses 'prompt' argument, not 'messages'
        success, outputs, error = await client.call_tool(
            "chat", 
            {"prompt": "Please respond with: 'EXAI MCP is working correctly via proper MCP protocol!'"}
        )
        
        if success:
            print("[OK] Chat tool call SUCCESSFUL")
            print(f"[OK] Outputs: {outputs}")
            # Extract text content if present
            for output in outputs:
                if 'text' in output:
                    print(f"[OK] Response: {output['text']}")
        else:
            print(f"[ERROR] Chat tool call FAILED: {error}")
    finally:
        await client.disconnect()

async def main():
    """Run all tests"""
    print("Testing EXAI MCP Tools via Proper MCP Protocol")
    print("="*60)
    
    await test_status_tool()
    await test_chat_tool()
    
    print("\n" + "="*60)
    print("All MCP protocol tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
