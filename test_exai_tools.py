#!/usr/bin/env python3
"""
Comprehensive EXAI Tools Test Suite

Tests all EXAI tools to ensure they work correctly after refactoring.
"""

import asyncio
import json
import sys
import websockets
from typing import Dict, Any, Tuple

WS_URL = "ws://localhost:8079"

async def send_tool_call(ws, tool_name: str, arguments: Dict[str, Any], timeout: float = 30.0) -> Tuple[bool, str, Any]:
    """Send a tool call and wait for response."""
    import uuid
    
    req_id = uuid.uuid4().hex
    message = {
        "op": "call_tool",
        "request_id": req_id,
        "name": tool_name,
        "arguments": arguments
    }
    
    await ws.send(json.dumps(message))
    
    try:
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
            msg = json.loads(raw)
            
            if msg.get("op") == "call_tool_res" and msg.get("request_id") == req_id:
                if msg.get("error"):
                    return False, f"Error: {msg.get('error')}", msg
                
                outputs = msg.get("outputs", [])
                if outputs:
                    # Extract text from first output
                    first_output = outputs[0]
                    if isinstance(first_output, dict):
                        text = first_output.get("text", str(first_output))
                    else:
                        text = str(first_output)
                    return True, text, msg
                
                return True, "Success (no output)", msg
    
    except asyncio.TimeoutError:
        return False, f"Timeout after {timeout}s", None


async def test_system_tools():
    """Test EXAI system tools."""
    print("\n" + "="*60)
    print("TESTING EXAI SYSTEM TOOLS")
    print("="*60)
    
    async with websockets.connect(WS_URL) as ws:
        # Authenticate
        auth_msg = {"op": "auth", "token": "test-token"}
        await ws.send(json.dumps(auth_msg))
        await ws.recv()  # Consume auth response
        
        tests = [
            ("listmodels_EXAI-WS", {}, "List available models"),
            ("version_EXAI-WS", {}, "Get server version"),
            ("status_EXAI-WS", {}, "Get server status"),
            ("health_EXAI-WS", {}, "Get health status"),
            ("activity_EXAI-WS", {"lines": 10}, "Get recent activity"),
        ]
        
        passed = 0
        failed = 0
        
        for tool_name, args, description in tests:
            print(f"\nTesting {tool_name}: {description}")
            success, result, _ = await send_tool_call(ws, tool_name, args, timeout=15.0)
            
            if success:
                print(f"✅ PASS: {tool_name}")
                passed += 1
            else:
                print(f"❌ FAIL: {tool_name}")
                print(f"   Error: {result}")
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"System Tools: {passed} passed, {failed} failed")
        print(f"{'='*60}")
        
        return passed, failed


async def test_utility_tools():
    """Test EXAI utility tools."""
    print("\n" + "="*60)
    print("TESTING EXAI UTILITY TOOLS")
    print("="*60)
    
    async with websockets.connect(WS_URL) as ws:
        # Authenticate
        auth_msg = {"op": "auth", "token": "test-token"}
        await ws.send(json.dumps(auth_msg))
        await ws.recv()
        
        tests = [
            ("chat_EXAI-WS", {
                "prompt": "Test: What is 2+2?",
                "model": "glm-4.5-flash",
                "use_websearch": False
            }, "Simple chat test"),
            
            ("challenge_EXAI-WS", {
                "prompt": "The sky is green"
            }, "Challenge incorrect statement"),
            
            ("planner_EXAI-WS", {
                "step": "Plan a simple task",
                "step_number": 1,
                "total_steps": 1,
                "next_step_required": False
            }, "Simple planning task"),
        ]
        
        passed = 0
        failed = 0
        
        for tool_name, args, description in tests:
            print(f"\nTesting {tool_name}: {description}")
            success, result, _ = await send_tool_call(ws, tool_name, args, timeout=30.0)
            
            if success:
                print(f"✅ PASS: {tool_name}")
                passed += 1
            else:
                print(f"❌ FAIL: {tool_name}")
                print(f"   Error: {result}")
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"Utility Tools: {passed} passed, {failed} failed")
        print(f"{'='*60}")
        
        return passed, failed


async def test_workflow_tools():
    """Test EXAI workflow tools."""
    print("\n" + "="*60)
    print("TESTING EXAI WORKFLOW TOOLS")
    print("="*60)
    
    async with websockets.connect(WS_URL) as ws:
        # Authenticate
        auth_msg = {"op": "auth", "token": "test-token"}
        await ws.send(json.dumps(auth_msg))
        await ws.recv()
        
        tests = [
            ("thinkdeep_EXAI-WS", {
                "step": "Test thinking workflow",
                "step_number": 1,
                "total_steps": 1,
                "next_step_required": False,
                "findings": "Testing thinkdeep tool",
                "use_assistant_model": False
            }, "ThinkDeep workflow"),
            
            ("debug_EXAI-WS", {
                "step": "Test debug workflow",
                "step_number": 1,
                "total_steps": 1,
                "next_step_required": False,
                "findings": "Testing debug tool",
                "hypothesis": "Test hypothesis",
                "use_assistant_model": False
            }, "Debug workflow"),
            
            ("analyze_EXAI-WS", {
                "step": "Test analyze workflow",
                "step_number": 1,
                "total_steps": 1,
                "next_step_required": False,
                "findings": "Testing analyze tool",
                "use_assistant_model": False
            }, "Analyze workflow"),
        ]
        
        passed = 0
        failed = 0
        
        for tool_name, args, description in tests:
            print(f"\nTesting {tool_name}: {description}")
            success, result, _ = await send_tool_call(ws, tool_name, args, timeout=45.0)
            
            if success:
                print(f"✅ PASS: {tool_name}")
                passed += 1
            else:
                print(f"❌ FAIL: {tool_name}")
                print(f"   Error: {result}")
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"Workflow Tools: {passed} passed, {failed} failed")
        print(f"{'='*60}")
        
        return passed, failed


async def main():
    """Run all EXAI tool tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE EXAI TOOLS TEST SUITE")
    print("="*60)
    print(f"WebSocket URL: {WS_URL}")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    
    # Test system tools
    passed, failed = await test_system_tools()
    total_passed += passed
    total_failed += failed
    
    # Test utility tools
    passed, failed = await test_utility_tools()
    total_passed += passed
    total_failed += failed
    
    # Test workflow tools
    passed, failed = await test_workflow_tools()
    total_passed += passed
    total_failed += failed
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed} ({100*total_passed/(total_passed+total_failed):.1f}%)")
    print(f"Failed: {total_failed}")
    print("="*60)
    
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

