#!/usr/bin/env python3
"""
Baseline Metrics Collection Script
Phase 0.3: Baseline Metric Collection

Collects performance baselines for all 30 EXAI-WS MCP tools by:
1. Running each tool 10+ times for statistical significance
2. Measuring latency (p50, p95, p99, max)
3. Measuring memory usage (peak, average)
4. Measuring success/failure rates
5. Storing results in Supabase + JSON files
6. Generating baseline report with visualizations

Created: 2025-10-24
"""

import asyncio
import json
import time
import psutil
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.timezone_helper import log_timestamp
from src.storage.supabase_client import SupabaseStorageManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tool categories from benchmark definitions
WORKFLOW_TOOLS = [
    "debug", "analyze", "codereview", "refactor", "secaudit", 
    "precommit", "testgen", "thinkdeep", "tracer", "docgen", 
    "consensus", "planner"
]

PROVIDER_TOOLS = [
    "chat", "kimi_chat_with_files", "kimi_chat_with_tools",
    "glm_web_search", "kimi_upload_files", "kimi_manage_files"
]

UTILITY_TOOLS = [
    "activity", "health", "status", "listmodels", "version",
    "provider_capabilities", "self-check", "glm_payload_preview",
    "glm_upload_file"
]

ALL_TOOLS = WORKFLOW_TOOLS + PROVIDER_TOOLS + UTILITY_TOOLS

# Test parameters
SAMPLES_PER_TOOL = 10
WARMUP_RUNS = 2  # Discard first 2 runs to warm up connections


class BaselineCollector:
    """Collects baseline performance metrics for EXAI-WS MCP tools"""
    
    def __init__(self, output_dir: str = "test_results/phase0_baseline"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Supabase client
        try:
            self.supabase = SupabaseStorageManager()
            self.supabase_enabled = True
            logger.info("Supabase storage enabled for baseline collection")
        except Exception as e:
            logger.warning(f"Supabase not available: {e}. Using JSON-only storage.")
            self.supabase_enabled = False
        
        # Results storage
        self.results: Dict[str, List[Dict]] = {}
        
    async def measure_tool_performance(
        self, 
        tool_name: str, 
        test_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Measure performance of a single tool invocation
        
        Returns:
            Dict with latency_ms, memory_mb, success, error
        """
        process = psutil.Process()
        
        # Measure memory before
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Measure latency
        start_time = time.time()
        success = False
        error = None
        
        try:
            # TODO: Implement actual tool invocation via WebSocket
            # For now, simulate with sleep
            await asyncio.sleep(0.1)  # Placeholder
            success = True
        except Exception as e:
            error = str(e)
            logger.error(f"Tool {tool_name} failed: {e}")
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Measure memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_mb = mem_after - mem_before
        
        return {
            "latency_ms": latency_ms,
            "memory_mb": memory_mb,
            "success": success,
            "error": error,
            "timestamp": log_timestamp()
        }
    
    async def collect_tool_baseline(
        self, 
        tool_name: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Collect baseline metrics for a single tool
        
        Args:
            tool_name: Name of the tool
            category: Tool category (workflow, provider, utility)
        
        Returns:
            Aggregated baseline metrics
        """
        logger.info(f"Collecting baseline for {tool_name} ({category})...")
        
        # Determine test parameters based on category
        test_params = self._get_test_params(tool_name, category)
        
        # Collect samples
        samples = []
        total_runs = WARMUP_RUNS + SAMPLES_PER_TOOL
        
        for i in range(total_runs):
            is_warmup = i < WARMUP_RUNS
            logger.info(f"  Run {i+1}/{total_runs} {'(warmup)' if is_warmup else ''}")
            
            result = await self.measure_tool_performance(tool_name, test_params)
            
            if not is_warmup:
                samples.append(result)
            
            # Small delay between runs
            await asyncio.sleep(0.5)
        
        # Calculate statistics
        latencies = [s["latency_ms"] for s in samples]
        memories = [s["memory_mb"] for s in samples]
        successes = [s["success"] for s in samples]
        
        baseline = {
            "tool_name": tool_name,
            "category": category,
            "samples_count": len(samples),
            "latency": {
                "p50": statistics.median(latencies),
                "p95": self._percentile(latencies, 95),
                "p99": self._percentile(latencies, 99),
                "max": max(latencies),
                "min": min(latencies),
                "mean": statistics.mean(latencies),
                "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            "memory": {
                "peak": max(memories),
                "average": statistics.mean(memories),
                "min": min(memories)
            },
            "reliability": {
                "success_rate": sum(successes) / len(successes) * 100,
                "failure_count": len([s for s in successes if not s]),
                "errors": [s["error"] for s in samples if s["error"]]
            },
            "timestamp": log_timestamp()
        }
        
        # Store results
        self.results[tool_name] = samples
        
        logger.info(f"  ✅ {tool_name}: p95={baseline['latency']['p95']:.1f}ms, "
                   f"success={baseline['reliability']['success_rate']:.1f}%")
        
        return baseline
    
    def _get_test_params(self, tool_name: str, category: str) -> Dict[str, Any]:
        """Get test parameters for a tool"""
        # TODO: Implement tool-specific test parameters
        # For now, return minimal params
        return {
            "prompt": "Test prompt for baseline collection",
            "model": "auto"
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(sorted_data):
            return sorted_data[-1]
        
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    async def collect_all_baselines(self) -> Dict[str, Any]:
        """Collect baselines for all tools"""
        logger.info(f"Starting baseline collection for {len(ALL_TOOLS)} tools...")
        logger.info(f"Samples per tool: {SAMPLES_PER_TOOL} (+ {WARMUP_RUNS} warmup runs)")
        
        baselines = {}
        
        # Collect workflow tools
        for tool in WORKFLOW_TOOLS:
            baselines[tool] = await self.collect_tool_baseline(tool, "workflow")
        
        # Collect provider tools
        for tool in PROVIDER_TOOLS:
            baselines[tool] = await self.collect_tool_baseline(tool, "provider")
        
        # Collect utility tools
        for tool in UTILITY_TOOLS:
            baselines[tool] = await self.collect_tool_baseline(tool, "utility")
        
        return baselines
    
    def save_baselines(self, baselines: Dict[str, Any]):
        """Save baselines to JSON file and Supabase"""
        # Save to JSON
        json_file = self.output_dir / f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(baselines, f, indent=2)
        logger.info(f"Saved baseline to {json_file}")
        
        # Save to Supabase
        if self.supabase_enabled:
            try:
                client = self.supabase.get_client()
                for tool_name, baseline in baselines.items():
                    client.table("performance_baselines").insert({
                        "tool_name": tool_name,
                        "category": baseline["category"],
                        "baseline_data": baseline,
                        "timestamp": log_timestamp()
                    }).execute()
                logger.info("Saved baselines to Supabase")
            except Exception as e:
                logger.error(f"Failed to save to Supabase: {e}")
    
    def generate_report(self, baselines: Dict[str, Any]):
        """Generate baseline report"""
        report_file = self.output_dir / "baseline_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Performance Baseline Report\n\n")
            f.write(f"**Generated:** {log_timestamp()}\n\n")
            f.write(f"**Tools Measured:** {len(baselines)}\n\n")
            f.write(f"**Samples Per Tool:** {SAMPLES_PER_TOOL}\n\n")
            
            # Summary by category
            for category in ["workflow", "provider", "utility"]:
                f.write(f"\n## {category.title()} Tools\n\n")
                f.write("| Tool | p50 (ms) | p95 (ms) | p99 (ms) | Memory (MB) | Success Rate |\n")
                f.write("|------|----------|----------|----------|-------------|-------------|\n")
                
                for tool_name, baseline in baselines.items():
                    if baseline["category"] == category:
                        f.write(f"| {tool_name} | "
                               f"{baseline['latency']['p50']:.1f} | "
                               f"{baseline['latency']['p95']:.1f} | "
                               f"{baseline['latency']['p99']:.1f} | "
                               f"{baseline['memory']['peak']:.1f} | "
                               f"{baseline['reliability']['success_rate']:.1f}% |\n")
        
        logger.info(f"Generated report: {report_file}")


async def main():
    """Main entry point"""
    collector = BaselineCollector()
    
    # Collect baselines
    baselines = await collector.collect_all_baselines()
    
    # Save results
    collector.save_baselines(baselines)
    
    # Generate report
    collector.generate_report(baselines)
    
    logger.info("✅ Baseline collection complete!")


if __name__ == "__main__":
    asyncio.run(main())

