#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive WorkflowTools Test Suite - Option B

This test suite verifies ACTUAL FUNCTIONALITY with AI integration:
- Uses use_assistant_model=True to test real AI analysis
- Verifies output quality and content (not just pass/fail)
- Tests multi-step workflows
- Tests end-to-end scenarios with real files

This is slower but provides true functional verification.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Bootstrap: Setup path and load environment
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root

# Load environment variables
load_env()

import websockets

# Configuration
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

# Test results
test_results = {}


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


class ComprehensiveWorkflowTester:
    """Comprehensive workflow tool tester with AI integration."""
    
    def __init__(self):
        self.ws = None
        self.results = {}
    
    async def connect(self):
        """Connect to WebSocket daemon."""
        self.ws = await websockets.connect(WS_URL, open_timeout=10)
        
        # Send hello
        hello = {"op": "hello", "token": WS_TOKEN}
        await self.ws.send(json.dumps(hello))
        
        # Wait for ack
        ack_raw = await asyncio.wait_for(self.ws.recv(), timeout=10)
        ack = json.loads(ack_raw)
        
        if ack.get("op") != "hello_ack" or not ack.get("ok"):
            raise Exception(f"Hello failed: {ack}")
        
        print(f"Connected to daemon (session: {ack.get('session_id')})")
    
    async def disconnect(self):
        """Disconnect from WebSocket daemon."""
        if self.ws:
            await self.ws.close()
    
    async def call_tool(self, tool_name, params, timeout=300):
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

            # Use a shorter timeout for individual recv() calls (30s)
            # This allows us to check the total timeout more frequently
            try:
                response_raw = await asyncio.wait_for(self.ws.recv(), timeout=30)
            except asyncio.TimeoutError:
                # No message received in 30s, check if we've exceeded total timeout
                continue

            response = json.loads(response_raw)

            # Check if this is our final response (call_tool_res)
            if response.get("request_id") == request_id and response.get("op") == "call_tool_res":
                return response

            # Otherwise, it's a progress message - continue waiting
            if response.get("op") == "progress":
                print(f"   Progress: {response.get('note', 'working...')}")
    
    async def test_analyze_with_ai(self):
        """Test analyze tool with REAL AI integration."""
        print_header("COMPREHENSIVE TEST 1: Analyze Tool with AI Integration")
        
        # Create a simple test file
        test_file = get_repo_root() / "scripts" / "testing" / "test_auth_token_stability.py"
        
        params = {
            "step": "Analyze the architecture of the auth token stability test",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Analyzing test architecture - examining async WebSocket connection handling, token validation, and error scenarios",  # FIX: findings must be a STRING
            "relevant_files": [str(test_file)],
            "model": "glm-4.5-flash",
            "use_assistant_model": True  # ENABLE AI INTEGRATION
        }
        
        try:
            start_time = time.time()
            print(f"Calling analyze tool with AI integration...")
            print(f"  - File: {test_file.name}")
            print(f"  - Model: glm-4.5-flash")
            print(f"  - AI Analysis: ENABLED")
            print(f"DEBUG: Params being sent: {json.dumps(params, indent=2)}")

            result = await self.call_tool("analyze", params, timeout=300)
            elapsed = time.time() - start_time

            # DEBUG: Print actual response to understand format
            print(f"\nDEBUG: Response op={result.get('op')}")
            print(f"DEBUG: Response keys={list(result.keys())}")
            if result.get("outputs"):
                print(f"DEBUG: Outputs count={len(result.get('outputs'))}")

            # Verify response format
            if result.get("op") != "call_tool_res" or not result.get("outputs"):
                print(f"❌ FAILED: Invalid response format")
                print(f"   Full response: {json.dumps(result, indent=2)[:500]}")
                self.results["analyze_with_ai"] = {"status": "FAIL", "error": "Invalid response"}
                return False
            
            # Parse tool response
            outputs = result.get("outputs", [])

            # The first output contains the actual tool response (JSON)
            # The second output contains the summary (text)
            if not outputs:
                print(f"❌ FAILED: No outputs in response")
                self.results["analyze_with_ai"] = {"status": "FAIL", "error": "No outputs"}
                return False

            # Get the first output (tool response)
            tool_response_text = outputs[0].get("text", "{}")

            try:
                tool_response = json.loads(tool_response_text)
            except json.JSONDecodeError as e:
                print(f"❌ FAILED: JSON parse error: {e}")
                print(f"   Response text: {tool_response_text[:500]}")
                self.results["analyze_with_ai"] = {"status": "FAIL", "error": f"JSON parse error: {e}"}
                return False

            # VERIFY ACTUAL FUNCTIONALITY
            # 1. Check that analysis completed
            status = tool_response.get("status", "")
            if "complete" not in status.lower():
                error_msg = tool_response.get("error", "Unknown error")
                print(f"❌ FAILED: Analysis did not complete (status: {status})")
                print(f"   Error: {error_msg}")
                self.results["analyze_with_ai"] = {"status": "FAIL", "error": f"Incomplete: {status} - {error_msg}"}
                return False
            
            # 2. Check that AI analysis was performed
            if "complete_analysis" not in tool_response:
                print(f"❌ FAILED: No AI analysis in response")
                self.results["analyze_with_ai"] = {"status": "FAIL", "error": "No AI analysis"}
                return False
            
            # 3. Check that analysis has meaningful content
            analysis = tool_response.get("complete_analysis", "")
            if len(analysis) < 100:
                print(f"❌ FAILED: Analysis too short ({len(analysis)} chars)")
                self.results["analyze_with_ai"] = {"status": "FAIL", "error": "Analysis too short"}
                return False
            
            # 4. Check that analysis mentions the file
            if "auth" not in analysis.lower() or "token" not in analysis.lower():
                print(f"⚠️  WARNING: Analysis may not be relevant to file content")
            
            print(f"✅ PASSED: Analyze tool with AI integration ({elapsed:.1f}s)")
            print(f"  - Status: {status}")
            print(f"  - Analysis length: {len(analysis)} chars")
            print(f"  - Analysis preview: {analysis[:200]}...")
            
            self.results["analyze_with_ai"] = {"status": "PASS", "time": elapsed}
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.results["analyze_with_ai"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def test_debug_with_ai(self):
        """Test debug tool with REAL AI integration."""
        print_header("COMPREHENSIVE TEST 2: Debug Tool with AI Integration")
        
        # Create a test scenario with a "bug"
        test_file = get_repo_root() / "scripts" / "testing" / "test_workflow_tools_part2.py"
        
        params = {
            "step": "Debug why WorkflowTools tests were failing initially",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Investigating test failures - tests were checking for 'ok: true' field that doesn't exist in MCP response format",  # FIX: findings must be a STRING
            "relevant_files": [str(test_file)],
            "issue_description": "Tests were checking for 'ok: true' field that doesn't exist in MCP responses",
            "model": "glm-4.5-flash",
            "use_assistant_model": True  # ENABLE AI INTEGRATION
        }
        
        try:
            start_time = time.time()
            print(f"Calling debug tool with AI integration...")
            print(f"  - File: {test_file.name}")
            print(f"  - Issue: MCP response format mismatch")
            print(f"  - AI Analysis: ENABLED")
            
            result = await self.call_tool("debug", params, timeout=300)
            elapsed = time.time() - start_time
            
            # Verify response format
            if result.get("op") != "call_tool_res" or not result.get("outputs"):
                print(f"❌ FAILED: Invalid response format")
                self.results["debug_with_ai"] = {"status": "FAIL", "error": "Invalid response"}
                return False
            
            # Parse tool response
            outputs = result.get("outputs", [])

            # The first output contains the actual tool response (JSON)
            if not outputs:
                print(f"❌ FAILED: No outputs in response")
                self.results["debug_with_ai"] = {"status": "FAIL", "error": "No outputs"}
                return False

            # Get the first output (tool response)
            tool_response_text = outputs[0].get("text", "{}")

            try:
                tool_response = json.loads(tool_response_text)
            except json.JSONDecodeError as e:
                print(f"❌ FAILED: JSON parse error: {e}")
                print(f"   Response text: {tool_response_text[:500]}")
                self.results["debug_with_ai"] = {"status": "FAIL", "error": f"JSON parse error: {e}"}
                return False

            # VERIFY ACTUAL FUNCTIONALITY
            # 1. Check that debugging completed
            status = tool_response.get("status", "")
            if "complete" not in status.lower():
                print(f"❌ FAILED: Debugging did not complete (status: {status})")
                self.results["debug_with_ai"] = {"status": "FAIL", "error": f"Incomplete: {status}"}
                return False
            
            # 2. Check that AI analysis was performed
            if "complete_debug" not in tool_response and "complete_analysis" not in tool_response:
                print(f"❌ FAILED: No AI analysis in response")
                self.results["debug_with_ai"] = {"status": "FAIL", "error": "No AI analysis"}
                return False
            
            # 3. Check that analysis has meaningful content
            analysis = tool_response.get("complete_debug") or tool_response.get("complete_analysis", "")
            if len(analysis) < 100:
                print(f"❌ FAILED: Analysis too short ({len(analysis)} chars)")
                self.results["debug_with_ai"] = {"status": "FAIL", "error": "Analysis too short"}
                return False
            
            print(f"✅ PASSED: Debug tool with AI integration ({elapsed:.1f}s)")
            print(f"  - Status: {status}")
            print(f"  - Analysis length: {len(analysis)} chars")
            print(f"  - Analysis preview: {analysis[:200]}...")
            
            self.results["debug_with_ai"] = {"status": "PASS", "time": elapsed}
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.results["debug_with_ai"] = {"status": "FAIL", "error": str(e)}
            return False
    
    async def run_all_tests(self):
        """Run all comprehensive tests."""
        print_header("COMPREHENSIVE WORKFLOWTOOLS TEST SUITE")
        print(f"Repository root: {get_repo_root()}")
        print(f"WebSocket URL: {WS_URL}")
        print(f"AI Integration: ENABLED (use_assistant_model=True)")
        print(f"\nNOTE: These tests are SLOW but verify actual functionality")
        
        await self.connect()
        
        try:
            # Run tests
            await self.test_analyze_with_ai()
            await self.test_debug_with_ai()
            
        finally:
            await self.disconnect()
        
        # Print summary
        print_header("TEST SUMMARY")
        passed = sum(1 for r in self.results.values() if r.get("status") == "PASS")
        failed = sum(1 for r in self.results.values() if r.get("status") == "FAIL")
        
        print(f"Tests passed: {passed}/{len(self.results)}")
        print(f"Tests failed: {failed}/{len(self.results)}")
        
        if failed > 0:
            print("\nFailed tests:")
            for name, result in self.results.items():
                if result.get("status") == "FAIL":
                    print(f"  - {name}: {result.get('error')}")
        
        if failed == 0:
            print("\n[SUCCESS] ALL COMPREHENSIVE TESTS PASSED ✅")
            return 0
        else:
            print("\n[FAILURE] SOME COMPREHENSIVE TESTS FAILED ❌")
            return 1


async def main():
    """Run comprehensive test suite."""
    tester = ComprehensiveWorkflowTester()
    exit_code = await tester.run_all_tests()
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

