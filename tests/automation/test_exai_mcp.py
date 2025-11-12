#!/usr/bin/env python
"""Test EXAI MCP Server Integration"""
import json
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath('.'))

def test_config():
    """Test configuration"""
    print("=" * 70)
    print("EXAI MCP SERVER INTEGRATION TEST")
    print("=" * 70)
    
    # Check .env file
    print("\n1. Checking .env file...")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'EXAI_WS_TOKEN' in env_content:
                print("   [OK] EXAI_WS_TOKEN found in .env")
            else:
                print("   [FAIL] EXAI_WS_TOKEN missing in .env")
                return False
    else:
        print("   [FAIL] .env file not found")
        return False
    
    # Check .mcp.json
    print("\n2. Checking .mcp.json...")
    if os.path.exists('.mcp.json'):
        with open('.mcp.json', 'r') as f:
            mcp_config = json.load(f)
            exai_config = mcp_config.get('mcpServers', {}).get('exai-mcp', {})
            port = exai_config.get('env', {}).get('EXAI_WS_PORT', '')
            if port == '3000':
                print(f"   [OK] MCP configured for port {port}")
            else:
                print(f"   [WARN] MCP configured for port {port} (expected 3000)")
    
    return True

def test_websocket():
    """Test WebSocket daemon connection"""
    print("\n3. Testing WebSocket daemon connection...")
    
    import asyncio
    import websockets
    
    async def test():
        token = "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
        
        try:
            async with websockets.connect("ws://127.0.0.1:3000", open_timeout=5) as ws:
                # Hello
                await ws.send(json.dumps({"op": "hello", "token": token}))
                resp = await asyncio.wait_for(ws.recv(), timeout=5)
                result = json.loads(resp)
                
                if result.get('ok'):
                    print("   [OK] WebSocket daemon responding")
                    
                    # List tools
                    await ws.send(json.dumps({"op": "list_tools", "request_id": "test-1"}))
                    resp = await asyncio.wait_for(ws.recv(), timeout=10)
                    tools_result = json.loads(resp)
                    tools = tools_result.get('tools', [])
                    print(f"   [OK] Found {len(tools)} tools")
                    
                    return True
                else:
                    print(f"   [FAIL] Daemon refused: {result}")
                    return False
                    
        except Exception as e:
            print(f"   [FAIL] Connection error: {e}")
            return False
    
    return asyncio.run(test())

def main():
    config_ok = test_config()
    ws_ok = test_websocket()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Configuration: {'[OK]' if config_ok else '[FAIL]'}")
    print(f"WebSocket:     {'[OK]' if ws_ok else '[FAIL]'}")
    
    if config_ok and ws_ok:
        print("\n[SUCCESS] EXAI MCP Server is properly configured!")
        print("\nTo use with Claude Code:")
        print("1. Make sure .mcp.json is in your VSCode workspace folder")
        print("2. The MCP shim will auto-start when VSCode launches")
        print("3. Check logs: logs/ws_shim_*.log")
    else:
        print("\n[INCOMPLETE] Issues found - see above for details")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
