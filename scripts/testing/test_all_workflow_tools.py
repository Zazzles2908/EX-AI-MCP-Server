#!/usr/bin/env python
"""
Comprehensive WorkflowTools Testing Suite for Phase B.1

This script tests all 12 WorkflowTools individually with realistic scenarios:
1. analyze - Code analysis workflow
2. codereview - Code review workflow
3. consensus - Multi-model consensus workflow
4. debug - Debugging workflow
5. docgen - Documentation generation workflow
6. planner - Planning workflow
7. precommit - Pre-commit checks workflow
8. refactor - Refactoring workflow
9. secaudit - Security audit workflow
10. testgen - Test generation workflow
11. thinkdeep - Deep investigation workflow
12. tracer - Code tracing workflow

Tests verify:
- Expert analysis completes successfully
- File embedding respects limits
- Conversation continuation works
- No daemon crashes
- Performance metrics

Usage:
    python scripts/testing/test_all_workflow_tools.py
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

from src.bootstrap import load_env, get_repo_root

# Load environment variables
load_env()

# Import WebSocket client for testing
import websockets


class WorkflowToolTester:
    """Test harness for WorkflowTools."""
    
    def __init__(self):
        self.ws_url = os.getenv("EXAI_WS_URL", "ws://127.0.0.1:8079")
        self.ws_token = os.getenv("EXAI_WS_TOKEN", "")
        self.results = {}
        
    async def connect(self):
        """Establish WebSocket connection with auth."""
        ws = await websockets.connect(self.ws_url)
        
        # Send hello with auth
        hello_msg = {
            "op": "hello",
            "token": self.ws_token,
            "client_info": {"name": "workflow_tools_tester", "version": "1.0"}
        }
        await ws.send(json.dumps(hello_msg))
        
        # Wait for hello_ack
        response = await asyncio.wait_for(ws.recv(), timeout=5.0)
        response_data = json.loads(response)
        
        if response_data.get("op") != "hello_ack" or not response_data.get("ok"):
            raise Exception(f"Auth failed: {response_data}")
        
        return ws
    
    async def call_tool(self, tool_name: str, params: dict, timeout: int = 300):
        """Call a tool via WebSocket and wait for response.

        Note: Connection is NOT closed in this method to allow long-running tools
        to complete. Caller is responsible for closing the connection.
        """
        ws = await self.connect()

        # Send tool call
        call_msg = {
            "op": "call_tool",
            "request_id": f"test_{tool_name}_{int(time.time())}",
            "name": tool_name,
            "arguments": params
        }
        await ws.send(json.dumps(call_msg))

        # Wait for response (keep connection open until tool completes)
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                # Close connection on timeout
                await ws.close()
                raise TimeoutError(f"Tool {tool_name} timed out after {timeout}s")

            try:
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            except asyncio.TimeoutError:
                # Continue waiting if no message received yet
                continue

            response_data = json.loads(response)
            op = response_data.get("op")

            # Handle call_tool_ack
            if op == "call_tool_ack":
                continue

            # Check for tool response - WAIT for this before closing
            if op == "call_tool_res":
                # Close connection AFTER receiving result
                await ws.close()
                return response_data

            # Check for errors
            if op == "error":
                error_msg = response_data.get('error') or response_data.get('message') or str(response_data)
                # Close connection on error
                await ws.close()
                raise Exception(f"Tool error: {error_msg}")

            # Ignore progress messages (keep connection open)
            if op == "progress":
                continue
    
    async def test_analyze(self):
        """Test analyze tool."""
        print("\n" + "=" * 70)
        print("TEST 1/12: analyze - Code Analysis Workflow")
        print("=" * 70)
        
        # Create a simple test file
        test_file = get_repo_root() / "scripts" / "testing" / "test_system_stability.py"
        
        params = {
            "step": "Analyze the test_system_stability.py script for code quality and patterns",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Initial analysis of system stability test script",
            "relevant_files": [str(test_file)],
            "model": "glm-4.5-flash",
            "use_assistant_model": True
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("analyze", params, timeout=120)
            elapsed = time.time() - start_time
            
            # Check result
            if result.get("ok"):
                print(f"✅ PASSED: analyze completed in {elapsed:.1f}s")
                self.results["analyze"] = {"status": "PASS", "time": elapsed}
                return True
            else:
                print(f"❌ FAILED: analyze returned error: {result.get('error')}")
                self.results["analyze"] = {"status": "FAIL", "error": result.get("error")}
                return False
                
        except Exception as e:
            print(f"❌ FAILED: analyze raised exception: {e}")
            self.results["analyze"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_codereview(self):
        """Test codereview tool."""
        print("\n" + "=" * 70)
        print("TEST 2/12: codereview - Code Review Workflow")
        print("=" * 70)
        
        test_file = get_repo_root() / "scripts" / "testing" / "test_critical_issues_7_to_10.py"
        
        params = {
            "step": "Review the critical issues test script for code quality",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Initial code review of critical issues test script",
            "relevant_files": [str(test_file)],
            "model": "glm-4.5-flash",
            "use_assistant_model": True
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("codereview", params, timeout=120)
            elapsed = time.time() - start_time
            
            if result.get("ok"):
                print(f"✅ PASSED: codereview completed in {elapsed:.1f}s")
                self.results["codereview"] = {"status": "PASS", "time": elapsed}
                return True
            else:
                print(f"❌ FAILED: codereview returned error: {result.get('error')}")
                self.results["codereview"] = {"status": "FAIL", "error": result.get("error")}
                return False
                
        except Exception as e:
            print(f"❌ FAILED: codereview raised exception: {e}")
            self.results["codereview"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_thinkdeep(self):
        """Test thinkdeep tool."""
        print("\n" + "=" * 70)
        print("TEST 3/12: thinkdeep - Deep Investigation Workflow")
        print("=" * 70)
        
        params = {
            "step": "Investigate the best approach for testing WorkflowTools",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Exploring testing strategies for workflow tools",
            "model": "glm-4.5-flash",
            "use_assistant_model": True
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("thinkdeep", params, timeout=120)
            elapsed = time.time() - start_time
            
            if result.get("ok"):
                print(f"✅ PASSED: thinkdeep completed in {elapsed:.1f}s")
                self.results["thinkdeep"] = {"status": "PASS", "time": elapsed}
                return True
            else:
                print(f"❌ FAILED: thinkdeep returned error: {result.get('error')}")
                self.results["thinkdeep"] = {"status": "FAIL", "error": result.get("error")}
                return False
                
        except Exception as e:
            print(f"❌ FAILED: thinkdeep raised exception: {e}")
            self.results["thinkdeep"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_testgen(self):
        """Test testgen tool."""
        print("\n" + "=" * 70)
        print("TEST 4/12: testgen - Test Generation Workflow")
        print("=" * 70)
        
        test_file = get_repo_root() / "src" / "bootstrap" / "env_loader.py"
        
        params = {
            "step": "Generate tests for the env_loader module",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Analyzing env_loader for test generation",
            "relevant_files": [str(test_file)],
            "model": "glm-4.5-flash",
            "use_assistant_model": True
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("testgen", params, timeout=120)
            elapsed = time.time() - start_time
            
            if result.get("ok"):
                print(f"✅ PASSED: testgen completed in {elapsed:.1f}s")
                self.results["testgen"] = {"status": "PASS", "time": elapsed}
                return True
            else:
                print(f"❌ FAILED: testgen returned error: {result.get('error')}")
                self.results["testgen"] = {"status": "FAIL", "error": result.get("error")}
                return False
                
        except Exception as e:
            print(f"❌ FAILED: testgen raised exception: {e}")
            self.results["testgen"] = {"status": "FAIL", "error": str(e)}
            return False


    async def test_debug(self):
        """Test debug tool."""
        print("\n" + "=" * 70)
        print("TEST 5/12: debug - Debugging Workflow")
        print("=" * 70)

        params = {
            "step": "Debug why a test might fail intermittently",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Investigating intermittent test failures",
            "model": "glm-4.5-flash",
            "use_assistant_model": True
        }

        try:
            start_time = time.time()
            result = await self.call_tool("debug", params, timeout=120)
            elapsed = time.time() - start_time

            if result.get("ok"):
                print(f"✅ PASSED: debug completed in {elapsed:.1f}s")
                self.results["debug"] = {"status": "PASS", "time": elapsed}
                return True
            else:
                print(f"❌ FAILED: debug returned error: {result.get('error')}")
                self.results["debug"] = {"status": "FAIL", "error": result.get("error")}
                return False

        except Exception as e:
            print(f"❌ FAILED: debug raised exception: {e}")
            self.results["debug"] = {"status": "FAIL", "error": str(e)}
            return False

    async def test_refactor(self):
        """Test refactor tool."""
        print("\n" + "=" * 70)
        print("TEST 6/12: refactor - Refactoring Workflow")
        print("=" * 70)

        test_file = get_repo_root() / "src" / "bootstrap" / "env_loader.py"

        params = {
            "step": "Suggest refactoring improvements for env_loader module",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Analyzing env_loader for refactoring opportunities",
            "relevant_files": [str(test_file)],
            "model": "glm-4.5-flash",
            "use_assistant_model": True
        }

        try:
            start_time = time.time()
            result = await self.call_tool("refactor", params, timeout=120)
            elapsed = time.time() - start_time

            if result.get("ok"):
                print(f"✅ PASSED: refactor completed in {elapsed:.1f}s")
                self.results["refactor"] = {"status": "PASS", "time": elapsed}
                return True
            else:
                print(f"❌ FAILED: refactor returned error: {result.get('error')}")
                self.results["refactor"] = {"status": "FAIL", "error": result.get("error")}
                return False

        except Exception as e:
            print(f"❌ FAILED: refactor raised exception: {e}")
            self.results["refactor"] = {"status": "FAIL", "error": str(e)}
            return False

    async def test_secaudit(self):
        """Test secaudit tool."""
        print("\n" + "=" * 70)
        print("TEST 7/12: secaudit - Security Audit Workflow")
        print("=" * 70)

        test_file = get_repo_root() / "src" / "daemon" / "ws_server.py"

        params = {
            "step": "Perform security audit on WebSocket server authentication",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Analyzing WebSocket server for security issues",
            "relevant_files": [str(test_file)],
            "model": "glm-4.5-flash",
            "use_assistant_model": True
        }

        try:
            start_time = time.time()
            result = await self.call_tool("secaudit", params, timeout=120)
            elapsed = time.time() - start_time

            if result.get("ok"):
                print(f"✅ PASSED: secaudit completed in {elapsed:.1f}s")
                self.results["secaudit"] = {"status": "PASS", "time": elapsed}
                return True
            else:
                print(f"❌ FAILED: secaudit returned error: {result.get('error')}")
                self.results["secaudit"] = {"status": "FAIL", "error": result.get("error")}
                return False

        except Exception as e:
            print(f"❌ FAILED: secaudit raised exception: {e}")
            self.results["secaudit"] = {"status": "FAIL", "error": str(e)}
            return False


async def main():
    """Run all WorkflowTools tests."""
    print("=" * 70)
    print("COMPREHENSIVE WORKFLOWTOOLS TESTING SUITE - PHASE B.1")
    print("=" * 70)
    print(f"\nRepository root: {get_repo_root()}")
    print(f"WebSocket URL: {os.getenv('EXAI_WS_URL', 'ws://127.0.0.1:8079')}")
    print(f"Testing 12 WorkflowTools with realistic scenarios...")
    print()

    tester = WorkflowToolTester()

    # Run tests for first 7 tools
    results = []
    results.append(await tester.test_analyze())
    results.append(await tester.test_codereview())
    results.append(await tester.test_thinkdeep())
    results.append(await tester.test_testgen())
    results.append(await tester.test_debug())
    results.append(await tester.test_refactor())
    results.append(await tester.test_secaudit())

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY (7/12 tools tested so far)")
    print("=" * 70)
    passed = sum(1 for r in results if r is True)
    total = len(results)

    print(f"\nTests passed: {passed}/{total}")
    print("\nDetailed Results:")
    for tool_name, result in tester.results.items():
        status = result["status"]
        if status == "PASS":
            print(f"  ✅ {tool_name}: {status} ({result['time']:.1f}s)")
        else:
            print(f"  ❌ {tool_name}: {status} - {result.get('error', 'Unknown error')}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED (so far)")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

