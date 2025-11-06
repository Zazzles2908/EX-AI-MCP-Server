#!/usr/bin/env python3
"""
Test script for MCP WebSocket client.

Tests actual MCP tool invocation with a few simple tools.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.baseline_collection.mcp_client import MCPWebSocketClient


async def test_connection():
    """Test basic connection to MCP server."""
    print("="*80)
    print("TEST 1: Connection Test")
    print("="*80)
    
    client = MCPWebSocketClient()
    
    try:
        print("Connecting to MCP server...")
        connected = await client.connect()
        
        if connected:
            print("✅ Connection successful!")
            print(f"   Session ID: {client.session_id}")
            return True
        else:
            print("❌ Connection failed!")
            return False
    finally:
        await client.disconnect()


async def test_simple_tool():
    """Test calling a simple tool (status)."""
    print("\n" + "="*80)
    print("TEST 2: Simple Tool Call (status)")
    print("="*80)
    
    async with MCPWebSocketClient() as client:
        print("Calling 'status' tool...")
        success, outputs, error = await client.call_tool("status", {})
        
        if success:
            print("✅ Tool call successful!")
            print(f"   Outputs: {len(outputs)} items")
            if outputs:
                print(f"   First output: {outputs[0]}")
            return True
        else:
            print(f"❌ Tool call failed: {error}")
            return False


async def test_tool_with_params():
    """Test calling a tool with parameters (chat)."""
    print("\n" + "="*80)
    print("TEST 3: Tool with Parameters (chat)")
    print("="*80)
    
    async with MCPWebSocketClient() as client:
        print("Calling 'chat' tool...")
        success, outputs, error = await client.call_tool(
            "chat",
            {"prompt": "Say hello", "model": "glm-4.5-flash"}
        )
        
        if success:
            print("✅ Tool call successful!")
            print(f"   Outputs: {len(outputs)} items")
            return True
        else:
            print(f"❌ Tool call failed: {error}")
            return False


async def test_metrics_collection():
    """Test metrics collection."""
    print("\n" + "="*80)
    print("TEST 4: Metrics Collection")
    print("="*80)
    
    async with MCPWebSocketClient() as client:
        print("Executing 'status' tool with metrics...")
        result = await client.execute_tool_with_metrics(
            tool_name="status",
            arguments={},
            baseline_version="test-1.0.0",
            iteration=1
        )
        
        print(f"✅ Metrics collected!")
        print(f"   Tool: {result['tool_name']}")
        print(f"   Status: {result['status']}")
        print(f"   Latency: {result['latency_ms']:.2f}ms")
        print(f"   Timestamp: {result['timestamp']}")
        
        return result['status'] == 'success'


async def main():
    """Run all tests."""
    print("\n🧪 MCP WebSocket Client Test Suite\n")
    
    tests = [
        ("Connection Test", test_connection),
        ("Simple Tool Call", test_simple_tool),
        ("Tool with Parameters", test_tool_with_params),
        ("Metrics Collection", test_metrics_collection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

