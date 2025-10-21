#!/usr/bin/env python
"""
WorkflowTools Testing Suite Part 2 - Remaining 5 Tools

Tests the remaining 5 WorkflowTools:
8. precommit - Pre-commit checks workflow
9. docgen - Documentation generation workflow
10. tracer - Code tracing workflow
11. consensus - Multi-model consensus workflow
12. planner - Planning workflow

This is a continuation of test_all_workflow_tools.py

Usage:
    python scripts/testing/test_workflow_tools_part2.py
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


class WorkflowToolTesterPart2:
    """Test harness for remaining WorkflowTools."""
    
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
            "client_info": {"name": "workflow_tools_tester_part2", "version": "1.0"}
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

            # Ignore progress messages
            if op == "progress":
                continue
    
    async def test_precommit(self):
        """Test precommit tool."""
        print("\n" + "=" * 70)
        print("TEST 8/12: precommit - Pre-commit Checks Workflow")
        print("=" * 70)

        # FIXED: precommit requires 'path' at step 1, not 'relevant_files'
        params = {
            "step": "Run pre-commit checks on the testing directory",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Checking code quality before commit",
            "path": str(get_repo_root() / "scripts" / "testing"),
            "model": "glm-4.5-flash",
            "use_assistant_model": False  # Disable expert analysis for faster testing
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("precommit", params, timeout=120)
            elapsed = time.time() - start_time

            # Verify response format
            if result.get("op") != "call_tool_res" or not result.get("outputs"):
                print(f"FAILED: Invalid response format")
                self.results["precommit"] = {"status": "FAIL", "error": "Invalid response format"}
                return False

            # Extract and parse the actual tool output
            outputs = result.get("outputs", [])
            if not outputs:
                print(f"FAILED: No outputs in response")
                self.results["precommit"] = {"status": "FAIL", "error": "No outputs"}
                return False

            # Parse the JSON response from the tool
            import json
            tool_response = json.loads(outputs[0].get("text", "{}"))

            # VERIFY ACTUAL FUNCTIONALITY: precommit should check git status
            # Check if tool actually performed validation
            validation_status = tool_response.get("validation_status", {})

            # The tool should have checked files (even if 0 files found)
            if "files_checked" not in validation_status:
                print(f"FAILED: Tool did not perform file checking")
                self.results["precommit"] = {"status": "FAIL", "error": "No file checking performed"}
                return False

            # Check if validation completed
            if not tool_response.get("validation_complete"):
                print(f"FAILED: Validation did not complete")
                self.results["precommit"] = {"status": "FAIL", "error": "Validation incomplete"}
                return False

            print(f"PASSED: precommit completed validation in {elapsed:.1f}s")
            print(f"  - Files checked: {validation_status.get('files_checked', 0)}")
            print(f"  - Issues found: {validation_status.get('issues_found', 0)}")
            print(f"  - Confidence: {validation_status.get('current_confidence', 'unknown')}")
            self.results["precommit"] = {"status": "PASS", "time": elapsed}
            return True

        except Exception as e:
            print(f"FAILED: precommit raised exception: {e}")
            self.results["precommit"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_docgen(self):
        """Test docgen tool."""
        print("\n" + "=" * 70)
        print("TEST 9/12: docgen - Documentation Generation Workflow")
        print("=" * 70)

        # FIXED: docgen step 1 is discovery - NO required fields
        params = {
            "step": "Discover files in src/bootstrap that need documentation",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Starting documentation discovery phase",
            "document_complexity": True,
            "document_flow": True,
            "update_existing": True,
            "comments_on_complex_logic": True,
            "num_files_documented": 0,
            "total_files_to_document": 0,
            "model": "glm-4.5-flash",
            "use_assistant_model": False  # Disable expert analysis for faster testing
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("docgen", params, timeout=120)
            elapsed = time.time() - start_time

            # Verify response format
            if result.get("op") != "call_tool_res" or not result.get("outputs"):
                print(f"FAILED: Invalid response format")
                self.results["docgen"] = {"status": "FAIL", "error": "Invalid response format"}
                return False

            # Extract and parse the actual tool output
            outputs = result.get("outputs", [])
            if not outputs:
                print(f"FAILED: No outputs in response")
                self.results["docgen"] = {"status": "FAIL", "error": "No outputs"}
                return False

            # Parse the JSON response from the tool
            import json
            tool_response = json.loads(outputs[0].get("text", "{}"))

            # VERIFY ACTUAL FUNCTIONALITY: docgen step 1 should complete
            # With use_assistant_model=False, tool completes local work without AI analysis
            # Check that tool completed successfully
            status = tool_response.get("status", "")
            if "complete" not in status.lower():
                print(f"FAILED: Tool did not complete (status: {status})")
                self.results["docgen"] = {"status": "FAIL", "error": f"Incomplete status: {status}"}
                return False

            # Verify step number is correct
            if tool_response.get("step_number") != 1:
                print(f"FAILED: Expected step 1, got step {tool_response.get('step_number')}")
                self.results["docgen"] = {"status": "FAIL", "error": "Wrong step number"}
                return False

            print(f"PASSED: docgen completed discovery in {elapsed:.1f}s")
            print(f"  - Status: {tool_response.get('status', 'unknown')}")
            print(f"  - Step: {tool_response.get('step_number', 0)}/{tool_response.get('total_steps', 0)}")
            self.results["docgen"] = {"status": "PASS", "time": elapsed}
            return True

        except Exception as e:
            print(f"FAILED: docgen raised exception: {e}")
            self.results["docgen"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_tracer(self):
        """Test tracer tool."""
        print("\n" + "=" * 70)
        print("TEST 10/12: tracer - Code Tracing Workflow")
        print("=" * 70)

        # Tracer requires relevant_files at step 1 - this is correct
        test_file = get_repo_root() / "src" / "daemon" / "ws_server.py"

        params = {
            "step": "Trace the execution flow of WebSocket authentication",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Tracing authentication flow in WebSocket server",
            "relevant_files": [str(test_file)],
            "trace_mode": "precision",
            "target_description": "Trace how authentication tokens are validated in the WebSocket server",
            "model": "glm-4.5-flash",
            "use_assistant_model": False  # Disable expert analysis for faster testing
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("tracer", params, timeout=120)
            elapsed = time.time() - start_time

            # Verify response format
            if result.get("op") != "call_tool_res" or not result.get("outputs"):
                print(f"FAILED: Invalid response format")
                self.results["tracer"] = {"status": "FAIL", "error": "Invalid response format"}
                return False

            # Extract and parse the actual tool output
            outputs = result.get("outputs", [])
            if not outputs:
                print(f"FAILED: No outputs in response")
                self.results["tracer"] = {"status": "FAIL", "error": "No outputs"}
                return False

            # Parse the JSON response from the tool
            import json
            tool_response = json.loads(outputs[0].get("text", "{}"))

            # VERIFY ACTUAL FUNCTIONALITY: tracer should complete tracing
            # With use_assistant_model=False, tool completes local work without AI analysis
            # Check that tool completed successfully
            status = tool_response.get("status", "")
            if "complete" not in status.lower():
                print(f"FAILED: Tool did not complete (status: {status})")
                self.results["tracer"] = {"status": "FAIL", "error": f"Incomplete status: {status}"}
                return False

            # Verify step number is correct
            if tool_response.get("step_number") != 1:
                print(f"FAILED: Expected step 1, got step {tool_response.get('step_number')}")
                self.results["tracer"] = {"status": "FAIL", "error": "Wrong step number"}
                return False

            print(f"PASSED: tracer completed tracing in {elapsed:.1f}s")
            print(f"  - Status: {tool_response.get('status', 'unknown')}")
            print(f"  - Step: {tool_response.get('step_number', 0)}/{tool_response.get('total_steps', 0)}")
            self.results["tracer"] = {"status": "PASS", "time": elapsed}
            return True

        except Exception as e:
            print(f"FAILED: tracer raised exception: {e}")
            self.results["tracer"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_consensus(self):
        """Test consensus tool."""
        print("\n" + "=" * 70)
        print("TEST 11/12: consensus - Multi-Model Consensus Workflow")
        print("=" * 70)

        # FIXED: consensus requires 'models' at step 1
        params = {
            "step": "Should we use async/await for all WebSocket operations?",
            "step_number": 1,
            "total_steps": 2,  # 2 models to consult
            "next_step_required": True,
            "findings": "Gathering consensus on async/await usage",
            "models": ["glm-4.5-flash", "kimi-k2-0905-preview"],
            "model": "glm-4.5-flash",
            "use_assistant_model": False  # Disable expert analysis for faster testing
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("consensus", params, timeout=120)
            elapsed = time.time() - start_time

            # Verify response format
            if result.get("op") != "call_tool_res" or not result.get("outputs"):
                print(f"FAILED: Invalid response format")
                self.results["consensus"] = {"status": "FAIL", "error": "Invalid response format"}
                return False

            # Extract and parse the actual tool output
            outputs = result.get("outputs", [])
            if not outputs:
                print(f"FAILED: No outputs in response")
                self.results["consensus"] = {"status": "FAIL", "error": "No outputs"}
                return False

            # Parse the JSON response from the tool
            import json
            tool_response = json.loads(outputs[0].get("text", "{}"))

            # VERIFY ACTUAL FUNCTIONALITY: consensus should consult multiple models
            # Check if tool is tracking models to consult
            if "models" not in str(tool_response).lower():
                print(f"FAILED: Tool did not track models for consensus")
                self.results["consensus"] = {"status": "FAIL", "error": "No model tracking"}
                return False

            # Check if this is step 1 (initial analysis)
            if tool_response.get("step_number") == 1:
                # Step 1 should indicate next step required (to consult models)
                if not tool_response.get("next_step_required"):
                    print(f"WARNING: Consensus step 1 should require next step to consult models")

            print(f"PASSED: consensus completed in {elapsed:.1f}s")
            print(f"  - Status: {tool_response.get('status', 'unknown')}")
            print(f"  - Step: {tool_response.get('step_number', 0)}/{tool_response.get('total_steps', 0)}")
            self.results["consensus"] = {"status": "PASS", "time": elapsed}
            return True

        except Exception as e:
            print(f"FAILED: consensus raised exception: {e}")
            self.results["consensus"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_planner(self):
        """Test planner tool."""
        print("\n" + "=" * 70)
        print("TEST 12/12: planner - Planning Workflow")
        print("=" * 70)

        # Planner requires NO fields at step 1 - this is correct
        params = {
            "step": "Create a plan for implementing rate limiting in the WebSocket server",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Planning rate limiting implementation",
            "model": "glm-4.5-flash",
            "use_assistant_model": False  # Planner is self-contained, no expert analysis
        }
        
        try:
            start_time = time.time()
            result = await self.call_tool("planner", params, timeout=120)
            elapsed = time.time() - start_time

            # Verify response format
            if result.get("op") != "call_tool_res" or not result.get("outputs"):
                print(f"FAILED: Invalid response format")
                self.results["planner"] = {"status": "FAIL", "error": "Invalid response format"}
                return False

            # Extract and parse the actual tool output
            outputs = result.get("outputs", [])
            if not outputs:
                print(f"FAILED: No outputs in response")
                self.results["planner"] = {"status": "FAIL", "error": "No outputs"}
                return False

            # Parse the JSON response from the tool
            import json
            tool_response = json.loads(outputs[0].get("text", "{}"))

            # VERIFY ACTUAL FUNCTIONALITY: planner should create a plan
            # Check if tool actually performed planning
            status = tool_response.get("status", "")
            # Planner uses "planning_complete" status (not "local_work_complete")
            if "complete" not in status.lower():
                print(f"FAILED: Planning did not complete (status: {status})")
                self.results["planner"] = {"status": "FAIL", "error": "Planning incomplete"}
                return False

            # Verify step number is correct
            if tool_response.get("step_number") != 1:
                print(f"FAILED: Expected step 1, got step {tool_response.get('step_number')}")
                self.results["planner"] = {"status": "FAIL", "error": "Wrong step number"}
                return False

            print(f"PASSED: planner completed planning in {elapsed:.1f}s")
            print(f"  - Status: {tool_response.get('status', 'unknown')}")
            print(f"  - Step: {tool_response.get('step_number', 0)}/{tool_response.get('total_steps', 0)}")
            self.results["planner"] = {"status": "PASS", "time": elapsed}
            return True

        except Exception as e:
            print(f"FAILED: planner raised exception: {e}")
            self.results["planner"] = {"status": "FAIL", "error": str(e)}
            return False


async def main():
    """Run remaining WorkflowTools tests."""
    print("=" * 70)
    print("WORKFLOWTOOLS TESTING SUITE PART 2 - PHASE B.1")
    print("=" * 70)
    print(f"\nRepository root: {get_repo_root()}")
    print(f"WebSocket URL: {os.getenv('EXAI_WS_URL', 'ws://127.0.0.1:8079')}")
    print(f"Testing remaining 5 WorkflowTools (8-12)...")
    print()
    
    tester = WorkflowToolTesterPart2()
    
    # Run tests for remaining 5 tools
    results = []
    results.append(await tester.test_precommit())
    results.append(await tester.test_docgen())
    results.append(await tester.test_tracer())
    results.append(await tester.test_consensus())
    results.append(await tester.test_planner())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY (Tools 8-12)")
    print("=" * 70)
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    print("\nDetailed Results:")
    for tool_name, result in tester.results.items():
        status = result["status"]
        if status == "PASS":
            print(f"  [PASS] {tool_name}: {status} ({result['time']:.1f}s)")
        else:
            print(f"  [FAIL] {tool_name}: {status} - {result.get('error', 'Unknown error')}")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

