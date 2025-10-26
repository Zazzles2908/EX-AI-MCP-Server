#!/usr/bin/env python3
"""
Phase 0.3 Baseline Collection Script
=====================================

Comprehensive baseline collection for all 30 EXAI-MCP tools.

Approach (EXAI Recommended):
- Dedicated script with modular components
- Hybrid sequential/parallel execution
- Multi-model testing for compatible tools
- Comprehensive metrics tracking
- Automated reporting

Usage:
    python scripts/baseline_collection/main.py [--sequential] [--parallel] [--report-only]
"""

import asyncio
import json
import logging
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from supabase import create_client, Client

# Import MCP WebSocket client for actual tool invocation
from scripts.baseline_collection.mcp_client import MCPWebSocketClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Baseline collection configuration
ITERATIONS_PER_TOOL = 10
BASELINE_VERSION = "0.3.0"
BASELINE_TIMESTAMP = datetime.now(timezone.utc).isoformat()

# Tool categories (from registry.py)
CORE_TOOLS = [
    "chat", "analyze", "codereview", "debug", "refactor",
    "testgen", "planner", "thinkdeep", "kimi_chat_with_files", "status"
]

ADVANCED_TOOLS = [
    "secaudit", "docgen", "consensus", "tracer", "precommit",
    "challenge", "kimi_upload_files", "kimi_manage_files",
    "kimi_chat_with_tools", "kimi_capture_headers", "kimi_intent_analysis",
    "glm_upload_file", "glm_web_search", "glm_payload_preview",
    "provider_capabilities", "listmodels", "activity", "version",
    "toolcall_log_tail", "health", "self-check"
]

ALL_TOOLS = CORE_TOOLS + ADVANCED_TOOLS

# Path translation for Windows host to Docker container
def translate_to_container_path(windows_path: str) -> str:
    """
    Translate Windows host paths to Docker container paths.

    Args:
        windows_path: Path on Windows host (e.g., C:\\Project\\EX-AI-MCP-Server\\...)

    Returns:
        Container path (e.g., /app/...)
    """
    # Normalize path separators
    normalized_path = str(windows_path).replace("\\", "/")

    # Define project root mapping
    project_root = "C:/Project/EX-AI-MCP-Server"
    container_root = "/app"

    # Replace project root with container root
    if normalized_path.startswith(project_root):
        return normalized_path.replace(project_root, container_root, 1)

    # If path doesn't start with project root, return as-is
    return normalized_path

# Test parameters for each tool tier
TIER_1_TOOLS = ["status", "version", "health", "listmodels", "provider_capabilities", "self-check"]
TIER_2_TOOLS = ["chat", "challenge", "activity", "toolcall_log_tail"]
TIER_3_TOOLS = ["kimi_upload_files", "kimi_chat_with_files", "glm_upload_file"]
TIER_4_TOOLS = [
    "analyze", "codereview", "debug", "refactor", "testgen",
    "secaudit", "docgen", "planner", "thinkdeep", "consensus",
    "tracer", "precommit"
]

# ============================================================================
# BASELINE COLLECTION LOGIC
# ============================================================================

class BaselineCollector:
    """Orchestrates baseline collection for all tools."""

    def __init__(self, use_real_mcp: bool = True):
        """
        Initialize baseline collector.

        Args:
            use_real_mcp: If True, use actual MCP WebSocket client. If False, simulate execution.
        """
        self.supabase: Optional[Client] = None
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.use_real_mcp = use_real_mcp
        self.mcp_client: Optional[MCPWebSocketClient] = None
        self.tools_to_test: List[str] = ALL_TOOLS  # Default to all tools

    def initialize_supabase(self):
        """Initialize Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("⚠️  WARNING: Supabase credentials not found. Results will only be saved to JSON.")
            return

        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
            self.supabase = None

    async def connect_mcp(self):
        """Establish WebSocket connection to MCP server."""
        if not self.use_real_mcp:
            print("ℹ️  Using simulated execution (no MCP connection)")
            return

        try:
            self.mcp_client = MCPWebSocketClient()
            connected = await self.mcp_client.connect()

            if connected:
                print("✅ Connected to MCP server")
            else:
                print("❌ Failed to connect to MCP server")
                raise ConnectionError("MCP connection failed")

        except Exception as e:
            print(f"❌ MCP connection error: {e}")
            raise

    async def disconnect_mcp(self):
        """Close WebSocket connection to MCP server."""
        if self.mcp_client:
            await self.mcp_client.disconnect()
            self.mcp_client = None
    
    def get_test_parameters(self, tool_name: str) -> Dict[str, Any]:
        """Get standardized test parameters for a tool."""

        # Tier 1: No parameters
        if tool_name in TIER_1_TOOLS:
            return {}

        # Tier 2: Simple parameters
        if tool_name in TIER_2_TOOLS:
            if tool_name == "chat":
                return {"prompt": "Hello, this is a baseline test. Please respond with 'test complete'.", "model": "glm-4.5-flash"}
            elif tool_name == "challenge":
                return {"prompt": "Is this a baseline test?"}
            elif tool_name == "activity":
                return {"lines": 50}
            elif tool_name == "toolcall_log_tail":
                return {}

        # Tier 3: File-dependent
        if tool_name in TIER_3_TOOLS:
            test_file_path = str(Path(__file__).parent / "test_files" / "sample_text.txt")
            # Translate Windows path to container path for Docker environment
            container_path = translate_to_container_path(test_file_path)

            if tool_name == "kimi_upload_files":
                return {"files": [container_path]}
            elif tool_name == "kimi_chat_with_files":
                # Note: This requires file_ids from kimi_upload_files
                # For baseline, we'll skip this and handle it separately
                return {"_skip": True, "reason": "Requires file_ids from kimi_upload_files"}
            elif tool_name == "glm_upload_file":
                return {"file": container_path}

        # Tier 4: Complex workflow parameters
        if tool_name in TIER_4_TOOLS:
            # Minimal valid parameters for baseline testing
            base_params = {
                "step": "Baseline test step",
                "step_number": 1,
                "total_steps": 1,
                "next_step_required": False,
                "findings": "Baseline test findings"
            }

            if tool_name == "analyze":
                return {**base_params, "relevant_files": []}
            elif tool_name == "codereview":
                return {**base_params, "relevant_files": []}
            elif tool_name == "debug":
                return {**base_params, "hypothesis": "Baseline test hypothesis"}
            elif tool_name == "refactor":
                return {**base_params}
            elif tool_name == "testgen":
                return {**base_params}
            elif tool_name == "secaudit":
                return {**base_params}
            elif tool_name == "docgen":
                return {
                    **base_params,
                    "document_complexity": True,
                    "document_flow": True,
                    "update_existing": True,
                    "comments_on_complex_logic": True,
                    "num_files_documented": 0,
                    "total_files_to_document": 0
                }
            elif tool_name == "planner":
                return {**base_params}
            elif tool_name == "thinkdeep":
                return {**base_params}
            elif tool_name == "consensus":
                return {
                    "step": "Baseline test consensus",
                    "step_number": 1,
                    "total_steps": 1,
                    "next_step_required": False,
                    "models": [{"model": "glm-4.5-flash", "stance": "neutral"}]
                }
            elif tool_name == "tracer":
                return {
                    **base_params,
                    "target_description": "Baseline test target",
                    "trace_mode": "ask"
                }
            elif tool_name == "precommit":
                return {**base_params, "path": "."}

        # Default: skip unknown tools
        return {"_skip": True, "reason": "Unknown tool tier"}
    
    async def test_tool(self, tool_name: str, iteration: int) -> Dict[str, Any]:
        """Test a single tool and collect metrics."""
        
        params = self.get_test_parameters(tool_name)

        # Skip if parameters indicate skip
        if params.get("_skip"):
            return {
                "tool_name": tool_name,
                "iteration": iteration,
                "status": "skipped",
                "reason": params.get("reason", "Unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "baseline_version": BASELINE_VERSION
            }
        
        # Execute tool and collect metrics
        if self.use_real_mcp and self.mcp_client:
            # ACTUAL MCP TOOL INVOCATION
            result = await self.mcp_client.execute_tool_with_metrics(
                tool_name=tool_name,
                arguments=params,
                baseline_version=BASELINE_VERSION,
                iteration=iteration
            )
            return result
        else:
            # SIMULATED EXECUTION (fallback)
            start_time = time.time()

            try:
                await asyncio.sleep(0.106)  # Simulate ~106ms latency

                latency_ms = (time.time() - start_time) * 1000

                return {
                    "tool_name": tool_name,
                    "iteration": iteration,
                    "status": "success",
                    "latency_ms": latency_ms,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "baseline_version": BASELINE_VERSION
                }

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000

                return {
                    "tool_name": tool_name,
                    "iteration": iteration,
                    "status": "error",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "latency_ms": latency_ms,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "baseline_version": BASELINE_VERSION
                }
    
    async def collect_sequential(self):
        """Collect baseline data sequentially with connection management."""
        print(f"\n🔄 Starting sequential baseline collection...")
        print(f"📊 Testing {len(self.tools_to_test)} tools × {ITERATIONS_PER_TOOL} iterations = {len(self.tools_to_test) * ITERATIONS_PER_TOOL} total executions")
        print(f"🔌 Mode: {'REAL MCP' if self.use_real_mcp else 'SIMULATED'}\n")

        try:
            # Connect to MCP server (if using real MCP)
            if self.use_real_mcp:
                await self.connect_mcp()

            # Run baseline collection
            for tool_idx, tool_name in enumerate(self.tools_to_test, 1):
                print(f"[{tool_idx}/{len(self.tools_to_test)}] Testing {tool_name}...")

                for iteration in range(1, ITERATIONS_PER_TOOL + 1):
                    result = await self.test_tool(tool_name, iteration)
                    self.results.append(result)

                    # Progress indicator
                    if result["status"] == "success":
                        print(f"  ✅ Iteration {iteration}/{ITERATIONS_PER_TOOL}: {result['latency_ms']:.2f}ms")
                    elif result["status"] == "skipped":
                        print(f"  ⏭️  Iteration {iteration}/{ITERATIONS_PER_TOOL}: Skipped ({result.get('reason', 'Unknown')})")
                    else:
                        error_msg = result.get('error', result.get('error_message', 'Unknown error'))
                        print(f"  ❌ Iteration {iteration}/{ITERATIONS_PER_TOOL}: {error_msg}")

                print()

        finally:
            # Disconnect from MCP server
            if self.use_real_mcp:
                await self.disconnect_mcp()
    
    def save_results(self):
        """Save results to Supabase and JSON files."""
        
        # Save to JSON
        output_dir = project_root / "baseline_results"
        output_dir.mkdir(exist_ok=True)
        
        json_file = output_dir / f"baseline_{BASELINE_VERSION}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(json_file, 'w') as f:
            json.dump({
                "baseline_version": BASELINE_VERSION,
                "timestamp": BASELINE_TIMESTAMP,
                "total_executions": len(self.results),
                "duration_seconds": time.time() - self.start_time,
                "results": self.results
            }, f, indent=2)
        
        print(f"✅ Results saved to: {json_file}")
        
        # Save to Supabase (if available)
        if self.supabase:
            try:
                # TODO: Create baseline_results table in Supabase
                print("⚠️  Supabase storage not yet implemented")
            except Exception as e:
                print(f"❌ Failed to save to Supabase: {e}")
    
    def generate_report(self):
        """Generate baseline collection report."""
        
        # Calculate summary statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r["status"] == "success")
        skipped = sum(1 for r in self.results if r["status"] == "skipped")
        failed = sum(1 for r in self.results if r["status"] == "error")
        
        print("\n" + "="*80)
        print("📊 BASELINE COLLECTION REPORT")
        print("="*80)
        print(f"Baseline Version: {BASELINE_VERSION}")
        print(f"Timestamp: {BASELINE_TIMESTAMP}")
        print(f"Duration: {time.time() - self.start_time:.2f}s")
        print(f"\nTotal Executions: {total}")
        print(f"  ✅ Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"  ⏭️  Skipped: {skipped} ({skipped/total*100:.1f}%)")
        print(f"  ❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print("="*80 + "\n")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for baseline collection."""
    
    print("="*80)
    print("🚀 PHASE 0.3 - BASELINE COLLECTION")
    print("="*80)
    print(f"Version: {BASELINE_VERSION}")
    print(f"Timestamp: {BASELINE_TIMESTAMP}")
    print(f"Tools: {len(ALL_TOOLS)}")
    print(f"Iterations per tool: {ITERATIONS_PER_TOOL}")
    print("="*80)
    
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Phase 0.3 Baseline Collection")
    parser.add_argument(
        "--simulated",
        action="store_true",
        help="Use simulated execution instead of real MCP calls"
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        help="Specific tools to test (e.g., --tools toolcall_log_tail glm_upload_file)"
    )
    args = parser.parse_args()

    # Determine execution mode (default to real MCP)
    use_real_mcp = not args.simulated

    # Filter tools if specified
    tools_to_test = ALL_TOOLS
    if args.tools:
        # Validate tool names
        invalid_tools = [t for t in args.tools if t not in ALL_TOOLS]
        if invalid_tools:
            print(f"❌ Invalid tool names: {', '.join(invalid_tools)}")
            print(f"Available tools: {', '.join(ALL_TOOLS)}")
            return
        tools_to_test = args.tools
        print(f"🎯 Targeted testing: {len(tools_to_test)} tools")

    collector = BaselineCollector(use_real_mcp=use_real_mcp)
    collector.tools_to_test = tools_to_test  # Set filtered tools
    collector.initialize_supabase()

    try:
        # Run sequential collection
        await collector.collect_sequential()

        # Save results
        collector.save_results()

        # Generate report
        collector.generate_report()

        print("✅ Baseline collection complete!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Collection interrupted by user")
        if collector.results:
            print("💾 Saving partial results...")
            collector.save_results()
    except Exception as e:
        print(f"\n\n❌ Collection failed: {e}")
        logger.error(f"Collection failed: {e}", exc_info=True)
        if collector.results:
            print("💾 Saving partial results...")
            collector.save_results()
        raise

if __name__ == "__main__":
    asyncio.run(main())

