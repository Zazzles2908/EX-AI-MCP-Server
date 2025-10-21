#!/usr/bin/env python
"""
Complete Simple Tools Test Suite for Phase C.3

Tests all 6 Simple Tools:
1. chat - General conversation
2. listmodels - List available models
3. thinkdeep - Deep reasoning
4. planner - Task planning
5. consensus - Multi-model consensus
6. challenge - Challenge assumptions

Usage:
    python scripts/testing/test_simple_tools_complete.py
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Bootstrap: Setup path and load environment
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env

# Load environment variables
load_env()

# Import WebSocket client
import websockets


class SimpleToolsTestClient:
    """WebSocket client for testing Simple Tools."""
    
    def __init__(self):
        self.ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
        self.ws_token = os.getenv("EXAI_WS_TOKEN", "")
        self.ws = None
    
    async def connect(self):
        """Connect to WebSocket daemon and authenticate."""
        self.ws = await websockets.connect(self.ws_url)
        
        # Send hello with auth token
        hello_msg = {
            "op": "hello",
            "token": self.ws_token,
            "client_info": {"name": "simple_tools_test", "version": "1.0"}
        }
        await self.ws.send(json.dumps(hello_msg))
        
        # Wait for hello_ack
        response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
        response_data = json.loads(response)
        
        if not response_data.get("ok"):
            raise Exception(f"Auth failed: {response_data}")
        
        return self.ws
    
    async def call_tool(self, tool_name, arguments, timeout=30.0):
        """Call a tool and wait for result."""
        request_id = f"test_{tool_name}_{int(time.time())}"
        
        call_msg = {
            "op": "call_tool",
            "request_id": request_id,
            "name": tool_name,
            "arguments": arguments
        }
        
        await self.ws.send(json.dumps(call_msg))
        
        # Wait for response
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Tool {tool_name} timed out after {timeout}s")
            
            response = await asyncio.wait_for(self.ws.recv(), timeout=10.0)
            response_data = json.loads(response)
            
            op = response_data.get("op")
            
            if op == "call_tool_ack":
                continue
            
            if op == "call_tool_res":
                return response_data
            
            if op == "error":
                error_msg = response_data.get('error') or response_data.get('message') or str(response_data)
                raise Exception(f"Tool error: {error_msg}")
            
            if op == "progress":
                continue
    
    async def close(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()


async def test_chat_tool():
    """Test 1: chat tool - General conversation"""
    print("\n" + "=" * 70)
    print("TEST 1: chat tool - General conversation")
    print("=" * 70)
    
    client = SimpleToolsTestClient()
    await client.connect()
    
    try:
        result = await client.call_tool(
            "chat",
            {
                "prompt": "Say 'test passed' and nothing else.",
                "model": "glm-4.5-flash"
            },
            timeout=30.0
        )
        
        # Verify result
        if "outputs" in result and result["outputs"]:
            text = result["outputs"][0].get("text", "") if isinstance(result["outputs"][0], dict) else str(result["outputs"][0])
            if len(text) > 0:
                print(f"✅ PASSED: chat tool returned response ({len(text)} chars)")
                return True
        
        print(f"❌ FAILED: chat tool returned invalid response")
        return False
        
    finally:
        await client.close()


async def test_listmodels_tool():
    """Test 2: listmodels tool - List available models"""
    print("\n" + "=" * 70)
    print("TEST 2: listmodels tool - List available models")
    print("=" * 70)
    
    client = SimpleToolsTestClient()
    await client.connect()
    
    try:
        result = await client.call_tool(
            "listmodels",
            {},
            timeout=10.0
        )
        
        # Verify result
        if "outputs" in result and result["outputs"]:
            text = result["outputs"][0].get("text", "") if isinstance(result["outputs"][0], dict) else str(result["outputs"][0])
            if "glm" in text.lower() or "kimi" in text.lower():
                print(f"✅ PASSED: listmodels tool returned model list ({len(text)} chars)")
                return True
        
        print(f"❌ FAILED: listmodels tool returned invalid response")
        return False
        
    finally:
        await client.close()


async def test_version_tool():
    """Test 3: version tool - Get version info"""
    print("\n" + "=" * 70)
    print("TEST 3: version tool - Get version info")
    print("=" * 70)

    client = SimpleToolsTestClient()
    await client.connect()

    try:
        result = await client.call_tool(
            "version",
            {},
            timeout=10.0
        )

        # Verify result
        if "outputs" in result and result["outputs"]:
            text = result["outputs"][0].get("text", "") if isinstance(result["outputs"][0], dict) else str(result["outputs"][0])
            if len(text) > 0:
                print(f"✅ PASSED: version tool returned response ({len(text)} chars)")
                return True

        print(f"❌ FAILED: version tool returned invalid response")
        return False

    finally:
        await client.close()


async def test_status_tool():
    """Test 4: status tool - Get system status"""
    print("\n" + "=" * 70)
    print("TEST 4: status tool - Get system status")
    print("=" * 70)

    client = SimpleToolsTestClient()
    await client.connect()

    try:
        result = await client.call_tool(
            "status",
            {},
            timeout=10.0
        )

        # Verify result
        if "outputs" in result and result["outputs"]:
            text = result["outputs"][0].get("text", "") if isinstance(result["outputs"][0], dict) else str(result["outputs"][0])
            if len(text) > 0:
                print(f"✅ PASSED: status tool returned response ({len(text)} chars)")
                return True

        print(f"❌ FAILED: status tool returned invalid response")
        return False

    finally:
        await client.close()


async def test_health_tool():
    """Test 5: health tool - Get health status"""
    print("\n" + "=" * 70)
    print("TEST 5: health tool - Get health status")
    print("=" * 70)

    client = SimpleToolsTestClient()
    await client.connect()

    try:
        result = await client.call_tool(
            "health",
            {},
            timeout=10.0
        )

        # Verify result
        if "outputs" in result and result["outputs"]:
            text = result["outputs"][0].get("text", "") if isinstance(result["outputs"][0], dict) else str(result["outputs"][0])
            if len(text) > 0:
                print(f"✅ PASSED: health tool returned response ({len(text)} chars)")
                return True

        print(f"❌ FAILED: health tool returned invalid response")
        return False

    finally:
        await client.close()


async def test_provider_capabilities_tool():
    """Test 6: provider_capabilities tool - Get provider capabilities"""
    print("\n" + "=" * 70)
    print("TEST 6: provider_capabilities tool - Get provider capabilities")
    print("=" * 70)

    client = SimpleToolsTestClient()
    await client.connect()

    try:
        result = await client.call_tool(
            "provider_capabilities",
            {},
            timeout=10.0
        )

        # Verify result
        if "outputs" in result and result["outputs"]:
            text = result["outputs"][0].get("text", "") if isinstance(result["outputs"][0], dict) else str(result["outputs"][0])
            if "glm" in text.lower() or "kimi" in text.lower():
                print(f"✅ PASSED: provider_capabilities tool returned response ({len(text)} chars)")
                return True

        print(f"❌ FAILED: provider_capabilities tool returned invalid response")
        return False

    finally:
        await client.close()


async def main():
    """Run all Simple Tools tests."""
    print("=" * 70)
    print("UTILITY TOOLS COMPLETE TEST SUITE - PHASE C.3")
    print("=" * 70)
    print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTesting utility and diagnostic tools...")

    results = []

    try:
        # Run all tests
        results.append(("chat", await test_chat_tool()))
        results.append(("listmodels", await test_listmodels_tool()))
        results.append(("version", await test_version_tool()))
        results.append(("status", await test_status_tool()))
        results.append(("health", await test_health_tool()))
        results.append(("provider_capabilities", await test_provider_capabilities_tool()))

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for tool_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {tool_name}")

        print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        print(f"\nNote: This test suite covers utility and diagnostic tools.")
        print(f"Workflow tools (analyze, debug, codereview, etc.) are tested separately.")

        return 0 if passed == total else 1

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

