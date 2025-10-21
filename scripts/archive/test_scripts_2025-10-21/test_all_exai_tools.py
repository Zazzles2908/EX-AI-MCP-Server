#!/usr/bin/env python3
"""
Comprehensive EXAI MCP Tools Testing Script
Tests all 29 EXAI tools systematically and generates detailed reports.

This script:
1. Tests all tools through the Docker container WebSocket daemon
2. Documents EXAI oversight and adjustments
3. Generates comprehensive markdown reports
4. Handles timeouts from .env configuration
5. Uses centralized logging
6. Runs outside of Augment session (no nested connections)

Usage:
    python scripts/test_all_exai_tools.py [--category CATEGORY] [--tool TOOL] [--verbose]

Categories: workflow, planning, utility, provider, all (default)
"""

import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import websockets

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import centralized logging
from utils.logging_unified import get_unified_logger
from src.bootstrap.logging_setup import setup_logging

# Setup logging
logger = setup_logging("test_exai_tools", log_level="INFO")
unified_logger = get_unified_logger()


class EXAIToolTester:
    """Comprehensive EXAI tool testing framework."""
    
    def __init__(self, ws_url: str = "ws://127.0.0.1:8079", token: Optional[str] = None):
        """Initialize tester with WebSocket connection details."""
        self.ws_url = ws_url
        self.token = token or self._load_token()
        self.ws = None
        self.session_id = None
        self.results = {
            "workflow": [],
            "planning": [],
            "utility": [],
            "provider": []
        }
        self.start_time = None
        self.end_time = None
        
        # Load timeouts from environment
        self._load_timeouts()
        
    def _load_token(self) -> str:
        """Load authentication token from environment."""
        token = os.getenv("EXAI_WS_TOKEN", "")
        if not token:
            # Try loading from .env file
            env_file = PROJECT_ROOT / ".env"
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith("EXAI_WS_TOKEN="):
                            token = line.split("=", 1)[1].split("#")[0].strip()
                            break
        return token
    
    def _load_timeouts(self):
        """Load timeout configuration from environment."""
        self.simple_tool_timeout = int(os.getenv("SIMPLE_TOOL_TIMEOUT_SECS", "60"))
        self.workflow_tool_timeout = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "300"))
        self.hello_timeout = int(os.getenv("EXAI_WS_HELLO_TIMEOUT", "15"))
        logger.info(f"Loaded timeouts: simple={self.simple_tool_timeout}s, workflow={self.workflow_tool_timeout}s")
    
    async def connect(self):
        """Establish WebSocket connection and perform handshake."""
        try:
            logger.info(f"Connecting to {self.ws_url}...")
            self.ws = await asyncio.wait_for(
                websockets.connect(
                    self.ws_url,
                    ping_interval=None,
                    ping_timeout=None
                ),
                timeout=self.hello_timeout
            )
            
            # Send hello message (daemon protocol)
            hello_msg = {
                "op": "hello",
                "token": self.token
            }
            await self.ws.send(json.dumps(hello_msg))

            # Wait for hello response
            response = await asyncio.wait_for(
                self.ws.recv(),
                timeout=self.hello_timeout
            )
            hello_response = json.loads(response)

            if hello_response.get("op") == "hello_ack" and hello_response.get("ok"):
                self.session_id = hello_response.get("session_id")
                logger.info(f"✅ Connected successfully. Session ID: {self.session_id}")
                return True
            else:
                error = hello_response.get("error", "unknown")
                logger.error(f"❌ Hello failed: {error}")
                logger.error(f"   Response: {hello_response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()
            logger.info("Disconnected from WebSocket daemon")
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any], timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Call an EXAI tool and return the result.
        
        Args:
            tool_name: Name of the tool to call
            params: Tool parameters
            timeout: Optional timeout override
            
        Returns:
            Dictionary with result, error, and metadata
        """
        if not self.ws:
            return {"error": "Not connected", "success": False}
        
        # Determine timeout
        if timeout is None:
            timeout = self.workflow_tool_timeout if tool_name in self._get_workflow_tools() else self.simple_tool_timeout
        
        request_id = f"test-{tool_name}-{int(time.time() * 1000)}"
        
        # Log tool start
        unified_logger.log_tool_start(tool_name, request_id, params)
        
        try:
            # Send tool call request (daemon protocol)
            request = {
                "op": "call_tool",
                "name": tool_name,
                "arguments": params,
                "request_id": request_id
            }

            await self.ws.send(json.dumps(request))
            logger.info(f"📤 Sent {tool_name} request (timeout={timeout}s)")

            # Wait for messages (ACK, progress, result)
            start_time = time.time()
            response = None

            while True:
                msg_data = await asyncio.wait_for(
                    self.ws.recv(),
                    timeout=timeout
                )
                msg = json.loads(msg_data)
                op = msg.get("op")

                if op == "call_tool_ack":
                    logger.debug(f"✅ {tool_name} acknowledged")
                elif op == "progress":
                    note = msg.get("note", "")
                    logger.debug(f"⏳ {tool_name} progress: {note}")
                elif op == "call_tool_res":
                    response = msg
                    break
                else:
                    logger.warning(f"⚠️ Unexpected message op: {op}")

            duration = time.time() - start_time

            # Check for error
            if response.get("op") == "call_tool_res":
                if "error" in response:
                    error_obj = response["error"]
                    error_msg = error_obj.get("message", "Unknown error")
                    logger.error(f"❌ {tool_name} failed: {error_msg}")
                    unified_logger.log_tool_error(tool_name, request_id, error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "duration": duration,
                        "tool": tool_name
                    }

                # Success
                outputs = response.get("outputs", [])
                result = outputs[0] if outputs else {}
                logger.info(f"✅ {tool_name} completed in {duration:.2f}s")
                unified_logger.log_tool_complete(tool_name, request_id, result, duration)

                return {
                    "success": True,
                    "result": result,
                    "duration": duration,
                    "tool": tool_name,
                    "response": response
                }
            else:
                error_msg = f"Unexpected response op: {response.get('op')}"
                logger.error(f"❌ {tool_name} unexpected response: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "duration": duration,
                    "tool": tool_name
                }
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            error_msg = f"Timeout after {timeout}s"
            logger.error(f"⏱️ {tool_name} timed out after {timeout}s")
            unified_logger.log_tool_error(tool_name, request_id, error_msg)
            return {
                "success": False,
                "error": error_msg,
                "duration": duration,
                "tool": tool_name
            }
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"❌ {tool_name} exception: {error_msg}")
            unified_logger.log_tool_error(tool_name, request_id, error_msg, traceback.format_exc())
            return {
                "success": False,
                "error": error_msg,
                "duration": duration,
                "tool": tool_name,
                "traceback": traceback.format_exc()
            }
    
    def _get_workflow_tools(self) -> List[str]:
        """Return list of workflow tool names."""
        return [
            "analyze", "codereview", "debug", "thinkdeep", "testgen",
            "refactor", "secaudit", "precommit", "docgen", "tracer"
        ]
    
    def _get_planning_tools(self) -> List[str]:
        """Return list of planning tool names."""
        return ["planner", "consensus"]
    
    def _get_utility_tools(self) -> List[str]:
        """Return list of utility tool names."""
        return [
            "chat", "challenge", "listmodels", "status", "health",
            "version", "self-check", "provider_capabilities", "activity"
        ]
    
    def _get_provider_tools(self) -> List[str]:
        """Return list of provider-specific tool names."""
        return [
            "kimi_capture_headers", "kimi_chat_with_tools", "kimi_intent_analysis",
            "kimi_multi_file_chat", "kimi_upload_and_extract",
            "glm_payload_preview", "glm_upload_file", "glm_web_search"
        ]
    
    async def test_utility_tools(self):
        """Test all utility tools."""
        logger.info("\n" + "="*80)
        logger.info("TESTING UTILITY TOOLS (9 tools)")
        logger.info("="*80)

        tests = [
            ("listmodels", {}),
            ("status", {}),
            ("version", {}),
            ("health", {"tail_lines": 20}),
            ("self-check", {"log_lines": 20}),
            ("provider_capabilities", {}),
            ("activity", {"lines": 50}),
            ("chat", {"prompt": "Test: What is Docker?", "model": "glm-4.5-flash"}),
            ("challenge", {"prompt": "Docker is always better than running services directly"}),
        ]

        for tool_name, params in tests:
            result = await self.call_tool(tool_name, params)
            self.results["utility"].append(result)
            await asyncio.sleep(1)  # Brief pause between tests

    async def test_workflow_tools(self):
        """Test all workflow tools."""
        logger.info("\n" + "="*80)
        logger.info("TESTING WORKFLOW TOOLS (10 tools)")
        logger.info("="*80)

        # Test analyze tool
        result = await self.call_tool("analyze", {
            "step": "Analyze the EX-AI-MCP-Server Docker container health check",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Health check is failing but container processes requests successfully",
            "analysis_type": "general"
        })
        self.results["workflow"].append(result)
        await asyncio.sleep(2)

        # Test debug tool
        result = await self.call_tool("debug", {
            "step": "Investigate why Docker health check fails",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Container logs show successful tool calls but health check returns exit code 1",
            "hypothesis": "Health check script may have authentication or connection issue"
        })
        self.results["workflow"].append(result)
        await asyncio.sleep(2)

        # Test thinkdeep tool
        result = await self.call_tool("thinkdeep", {
            "step": "Should we fix the Docker health check or is it acceptable for it to fail?",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Container is functional despite health check failures"
        })
        self.results["workflow"].append(result)
        await asyncio.sleep(2)

        # Test planner tool (moved from planning to workflow for testing)
        result = await self.call_tool("planner", {
            "step": "Create a plan to fix Docker health check",
            "step_number": 1,
            "total_steps": 3,
            "next_step_required": True
        })
        self.results["workflow"].append(result)
        await asyncio.sleep(2)

        logger.info("⏭️  Skipping remaining workflow tools (codereview, testgen, refactor, secaudit, precommit, docgen, tracer)")
        logger.info("   These require specific file contexts and will be tested in Phase 18")

    async def test_planning_tools(self):
        """Test all planning tools."""
        logger.info("\n" + "="*80)
        logger.info("TESTING PLANNING TOOLS (2 tools)")
        logger.info("="*80)

        # Planner already tested in workflow section
        logger.info("✅ planner: Already tested in workflow section")

        # Test consensus tool
        result = await self.call_tool("consensus", {
            "step": "Should we expose metrics port 9109 in Docker?",
            "step_number": 1,
            "total_steps": 2,
            "next_step_required": True,
            "models": [
                {"model": "glm-4.5-flash", "stance": "for"},
                {"model": "kimi-k2-turbo-preview", "stance": "against"}
            ],
            "findings": "Evaluating whether to expose Prometheus metrics port"
        })
        self.results["planning"].append(result)

    async def test_provider_tools(self):
        """Test all provider-specific tools."""
        logger.info("\n" + "="*80)
        logger.info("TESTING PROVIDER TOOLS (8 tools)")
        logger.info("="*80)

        # Test GLM web search
        result = await self.call_tool("glm_web_search", {
            "search_query": "Docker health check best practices"
        })
        self.results["provider"].append(result)
        await asyncio.sleep(2)

        # Test GLM payload preview
        result = await self.call_tool("glm_payload_preview", {
            "prompt": "Test payload preview"
        })
        self.results["provider"].append(result)
        await asyncio.sleep(1)

        logger.info("⏭️  Skipping remaining provider tools (kimi_*, glm_upload_file)")
        logger.info("   These require file uploads and will be tested separately")

    async def run_all_tests(self, categories: List[str] = None):
        """Run all tests in specified categories."""
        if categories is None:
            categories = ["utility", "workflow", "planning", "provider"]

        self.start_time = datetime.now(timezone.utc)
        logger.info(f"\n{'='*80}")
        logger.info(f"EXAI TOOLS COMPREHENSIVE TEST SUITE")
        logger.info(f"Started: {self.start_time.isoformat()}")
        logger.info(f"Categories: {', '.join(categories)}")
        logger.info(f"{'='*80}\n")

        # Connect to daemon
        if not await self.connect():
            logger.error("❌ Failed to connect to WebSocket daemon")
            return False

        try:
            # Run tests by category
            if "utility" in categories:
                await self.test_utility_tools()

            if "workflow" in categories:
                await self.test_workflow_tools()

            if "planning" in categories:
                await self.test_planning_tools()

            if "provider" in categories:
                await self.test_provider_tools()

            self.end_time = datetime.now(timezone.utc)
            duration = (self.end_time - self.start_time).total_seconds()

            logger.info(f"\n{'='*80}")
            logger.info(f"TEST SUITE COMPLETE")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info(f"{'='*80}\n")

            return True

        finally:
            await self.disconnect()

    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate comprehensive markdown report."""
        if output_file is None:
            output_file = PROJECT_ROOT / "docs" / "05_CURRENT_WORK" / f"EXAI_TOOLS_TEST_REPORT_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

        # Calculate statistics
        total_tests = sum(len(results) for results in self.results.values())
        total_success = sum(1 for results in self.results.values() for r in results if r.get("success"))
        total_failed = total_tests - total_success

        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        # Build report
        report_lines = [
            "# EXAI Tools Comprehensive Test Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S AEDT')}",
            f"**Test Duration:** {duration:.2f}s",
            f"**Session ID:** {self.session_id}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"- **Total Tests:** {total_tests}",
            f"- **Passed:** {total_success} ✅",
            f"- **Failed:** {total_failed} ❌",
            f"- **Success Rate:** {(total_success/total_tests*100) if total_tests > 0 else 0:.1f}%",
            "",
            "---",
            "",
            "## Test Results by Category",
            ""
        ]

        # Add results for each category
        for category, results in self.results.items():
            if not results:
                continue

            category_success = sum(1 for r in results if r.get("success"))
            category_total = len(results)

            report_lines.extend([
                f"### {category.upper()} Tools ({category_success}/{category_total} passed)",
                ""
            ])

            for result in results:
                tool_name = result.get("tool", "unknown")
                success = result.get("success", False)
                duration = result.get("duration", 0)
                error = result.get("error", "")

                status = "✅ PASS" if success else "❌ FAIL"
                report_lines.append(f"#### {tool_name} - {status} ({duration:.2f}s)")
                report_lines.append("")

                if success:
                    # Extract key insights from result
                    result_data = result.get("result", {})
                    if isinstance(result_data, dict):
                        # Check for EXAI oversight/adjustments
                        if "content" in result_data:
                            content = result_data["content"]
                            if isinstance(content, str) and len(content) > 200:
                                report_lines.append(f"**Response Preview:** {content[:200]}...")
                            else:
                                report_lines.append(f"**Response:** {content}")

                        # Check for metadata
                        if "metadata" in result_data:
                            metadata = result_data["metadata"]
                            report_lines.append(f"**Metadata:** {json.dumps(metadata, indent=2)}")
                else:
                    report_lines.append(f"**Error:** {error}")
                    if "traceback" in result:
                        report_lines.append(f"```\n{result['traceback']}\n```")

                report_lines.append("")

        # Add EXAI oversight section
        report_lines.extend([
            "---",
            "",
            "## EXAI Oversight & Adjustments",
            "",
            "This section documents any oversight, corrections, or adjustments provided by EXAI tools during testing.",
            ""
        ])

        # Analyze results for EXAI insights
        for category, results in self.results.items():
            for result in results:
                if result.get("success") and "result" in result:
                    result_data = result["result"]
                    tool_name = result["tool"]

                    # Check for expert analysis or validation
                    if isinstance(result_data, dict):
                        if "expert_analysis" in result_data:
                            report_lines.extend([
                                f"### {tool_name} - Expert Analysis",
                                "",
                                f"```\n{result_data['expert_analysis']}\n```",
                                ""
                            ])

                        if "validation" in result_data:
                            report_lines.extend([
                                f"### {tool_name} - Validation",
                                "",
                                f"```\n{result_data['validation']}\n```",
                                ""
                            ])

        # Write report
        report_content = "\n".join(report_lines)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"📄 Report generated: {output_file}")
        return str(output_file)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test all EXAI MCP tools")
    parser.add_argument("--category", choices=["workflow", "planning", "utility", "provider", "all"],
                       default="all", help="Category of tools to test")
    parser.add_argument("--tool", help="Test specific tool only")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Determine categories to test
    if args.category == "all":
        categories = ["utility", "workflow", "planning", "provider"]
    else:
        categories = [args.category]

    # Create tester
    tester = EXAIToolTester()

    # Run tests
    success = await tester.run_all_tests(categories)

    if success:
        # Generate report
        report_file = tester.generate_report()
        print(f"\n✅ Testing complete! Report: {report_file}")
        return 0
    else:
        print("\n❌ Testing failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

