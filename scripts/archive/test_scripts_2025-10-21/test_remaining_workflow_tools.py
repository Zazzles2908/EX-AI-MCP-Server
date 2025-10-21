#!/usr/bin/env python
"""
Test Remaining WorkflowTools (testgen) + challenge SimpleTool

This test verifies the last untested WorkflowTool to achieve 100% coverage.

WorkflowTools tested so far (10/11):
- analyze ✅
- debug ✅
- precommit ✅
- docgen ✅
- tracer ✅
- consensus ✅
- planner ✅
- codereview ✅
- refactor ✅
- secaudit ✅

Remaining to test (1/11):
- testgen (this script)

Bonus:
- challenge (SimpleTool, not WorkflowTool - uses 'prompt' parameter)
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Bootstrap
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root
load_env()

import websockets

# Configuration
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"


class WorkflowToolTester:
    """Test harness for WorkflowTools."""
    
    def __init__(self):
        self.ws = None
        self.session_id = None
    
    async def connect(self):
        """Connect to daemon and authenticate."""
        self.ws = await websockets.connect(WS_URL, open_timeout=10)
        
        # Send hello
        hello = {"op": "hello", "token": WS_TOKEN}
        await self.ws.send(json.dumps(hello))
        
        # Wait for ack
        ack_raw = await asyncio.wait_for(self.ws.recv(), timeout=10)
        ack = json.loads(ack_raw)
        
        if ack.get("op") != "hello_ack" or not ack.get("ok"):
            raise Exception(f"Hello handshake failed: {ack}")
        
        self.session_id = ack.get("session_id")
        return self.session_id
    
    async def call_tool(self, tool_name, params, timeout=60):
        """Call a tool and wait for response."""
        request_id = f"test_{tool_name}_{int(time.time() * 1000)}"
        
        message = {
            "op": "call_tool",
            "name": tool_name,
            "request_id": request_id,
            "arguments": params
        }
        
        await self.ws.send(json.dumps(message))
        
        # Wait for response
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Tool {tool_name} timed out after {timeout}s")
            
            try:
                response_raw = await asyncio.wait_for(self.ws.recv(), timeout=30)
            except asyncio.TimeoutError:
                continue
            
            response = json.loads(response_raw)
            
            # Check if this is our final response
            if response.get("request_id") == request_id and response.get("op") == "call_tool_res":
                return response
            
            # Progress message
            if response.get("op") == "progress":
                print(f"   Progress: {response.get('note', 'working...')}")
    
    async def close(self):
        """Close connection."""
        if self.ws:
            await self.ws.close()


async def test_testgen_tool():
    """Test testgen workflow tool."""
    print("\n" + "=" * 70)
    print("TEST 1: testgen Tool")
    print("=" * 70)
    
    tester = WorkflowToolTester()
    session_id = await tester.connect()
    print(f"✅ Connected (session: {session_id})")
    
    # Get a test file
    test_file = get_repo_root() / "scripts" / "testing" / "test_auth_token_stability.py"
    
    params = {
        "step": "Generate unit tests for the auth token stability test",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Analyzing test file to generate comprehensive unit tests",
        "relevant_files": [str(test_file)],
        "model": "glm-4.5-flash",
        "use_assistant_model": False  # Fast test
    }
    
    print(f"\nCalling testgen tool...")
    print(f"  - File: {test_file.name}")
    print(f"  - Model: glm-4.5-flash")
    print(f"  - AI Analysis: DISABLED (fast test)")
    
    response = await tester.call_tool("testgen", params, timeout=60)
    
    # Parse response
    outputs = response.get("outputs", [])
    if not outputs:
        print(f"❌ FAILED: No outputs in response")
        await tester.close()
        return False
    
    # Get the first output (tool response)
    tool_response_text = outputs[0].get("text", "{}")
    
    try:
        tool_response = json.loads(tool_response_text)
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: JSON parse error: {e}")
        await tester.close()
        return False
    
    # Check status
    status = tool_response.get("status", "")
    
    if "testgen" in status.lower() or "complete" in status.lower():
        print(f"\n✅ testgen tool completed successfully")
        print(f"   Status: {status}")
        
        # Check for test generation output
        if "test" in tool_response_text.lower():
            print(f"   ✅ Response contains test-related content")
        
        await tester.close()
        return True
    else:
        print(f"\n❌ FAILED: Unexpected status: {status}")
        await tester.close()
        return False


async def test_challenge_tool():
    """Test challenge simple tool (NOT a workflow tool)."""
    print("\n" + "=" * 70)
    print("TEST 2: challenge Tool (SimpleTool)")
    print("=" * 70)
    print("NOTE: challenge is a SimpleTool, not a WorkflowTool")
    print("      It takes 'prompt' parameter, not workflow parameters")

    tester = WorkflowToolTester()
    session_id = await tester.connect()
    print(f"✅ Connected (session: {session_id})")

    # Challenge tool uses 'prompt' parameter, not workflow parameters
    params = {
        "prompt": "The workflow tools test suite is comprehensive and covers all edge cases."
    }

    print(f"\nCalling challenge tool...")
    print(f"  - Prompt: '{params['prompt']}'")
    print(f"  - Type: SimpleTool (no AI model needed)")

    response = await tester.call_tool("challenge", params, timeout=60)
    
    # Parse response
    outputs = response.get("outputs", [])
    if not outputs:
        print(f"❌ FAILED: No outputs in response")
        await tester.close()
        return False
    
    # Get the first output (tool response)
    tool_response_text = outputs[0].get("text", "{}")
    
    try:
        tool_response = json.loads(tool_response_text)
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: JSON parse error: {e}")
        await tester.close()
        return False
    
    # Check status
    status = tool_response.get("status", "")

    # Challenge tool returns "success" or "continuation_available"
    if status in ["success", "continuation_available"] or "challenge" in status.lower():
        print(f"\n✅ challenge tool completed successfully")
        print(f"   Status: {status}")

        # Check for challenge-related output
        if "challenge" in tool_response_text.lower() or "assumption" in tool_response_text.lower() or "original_statement" in tool_response_text.lower():
            print(f"   ✅ Response contains challenge-related content")

        await tester.close()
        return True
    else:
        print(f"\n❌ FAILED: Unexpected status: {status}")
        await tester.close()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("REMAINING WORKFLOWTOOLS TEST SUITE")
    print("=" * 70)
    print(f"Testing 2 remaining WorkflowTools to achieve 100% coverage")
    
    results = {}
    
    # Test testgen
    try:
        results["testgen"] = await test_testgen_tool()
    except Exception as e:
        print(f"\n❌ testgen test failed with exception: {e}")
        results["testgen"] = False
    
    # Test challenge
    try:
        results["challenge"] = await test_challenge_tool()
    except Exception as e:
        print(f"\n❌ challenge test failed with exception: {e}")
        results["challenge"] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print(f"\n✅ ALL TESTS PASSED!")
        print(f"\n🎉 WorkflowTools Coverage: 11/11 (100%)")
        print(f"\nAll WorkflowTools tested:")
        print(f"  1. analyze ✅")
        print(f"  2. debug ✅")
        print(f"  3. precommit ✅")
        print(f"  4. docgen ✅")
        print(f"  5. tracer ✅")
        print(f"  6. consensus ✅")
        print(f"  7. planner ✅")
        print(f"  8. codereview ✅")
        print(f"  9. refactor ✅")
        print(f" 10. secaudit ✅")
        print(f" 11. testgen ✅")
        print(f"\nBonus: challenge tool tested (SimpleTool, not WorkflowTool) ✅")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED")
        for tool, passed in results.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {tool}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

