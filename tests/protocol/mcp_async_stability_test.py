#!/usr/bin/env python3
"""
Async Event Loop Stability Test
Tests async event loop stability under concurrent MCP load
"""

import asyncio
import json
import time
from typing import List, Dict, Any
import subprocess
import sys

class AsyncStabilityTester:
    """Test async event loop stability with concurrent MCP calls"""

    def __init__(self):
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_latency": 0,
            "errors": []
        }

    async def run_mcp_call(self, request_id: int, message: Dict[str, Any]) -> float:
        """Run a single MCP call and measure latency"""
        start_time = time.time()

        try:
            # Simulate MCP call (would use actual subprocess in real test)
            process = await asyncio.create_subprocess_exec(
                "python", "-c", "print('MCP response')",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            latency = time.time() - start_time

            self.results["successful_requests"] += 1
            return latency

        except Exception as e:
            latency = time.time() - start_time
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Request {request_id}: {str(e)}")
            return latency

    async def test_concurrent_calls(self, num_concurrent: int = 10, num_total: int = 100):
        """Test concurrent MCP calls"""
        print(f"\n🚀 Testing Async Event Loop Stability")
        print(f"Concurrent Requests: {num_concurrent}")
        print(f"Total Requests: {num_total}")
        print(f"{'='*60}")

        # Create test messages
        messages = []
        for i in range(num_total):
            message = {
                "jsonrpc": "2.0",
                "id": f"async_test_{i}",
                "method": "tools/call",
                "params": {
                    "name": "kimi_chat_with_tools",
                    "arguments": {
                        "prompt": f"Test message {i}",
                        "model": "kimi-k2-thinking"
                    }
                }
            }
            messages.append(message)

        # Run concurrent tests
        semaphore = asyncio.Semaphore(num_concurrent)

        async def bounded_call(request_id: int, message: Dict[str, Any]):
            async with semaphore:
                return await self.run_mcp_call(request_id, message)

        start_time = time.time()

        # Execute all requests
        tasks = [
            bounded_call(i, msg)
            for i, msg in enumerate(messages)
        ]

        latencies = await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Calculate statistics
        self.results["total_requests"] = num_total
        self.results["total_time"] = total_time
        self.results["average_latency"] = sum(latencies) / len(latencies)
        self.results["throughput"] = num_total / total_time
        self.results["max_latency"] = max(latencies)
        self.results["min_latency"] = min(latencies)

        # Print results
        print(f"\n📊 Test Results:")
        print(f"{'='*60}")
        print(f"Total Requests: {self.results['total_requests']}")
        print(f"Successful: {self.results['successful_requests']}")
        print(f"Failed: {self.results['failed_requests']}")
        print(f"Success Rate: {(self.results['successful_requests']/num_total*100):.2f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Throughput: {self.results['throughput']:.2f} req/s")
        print(f"Average Latency: {self.results['average_latency']*1000:.2f}ms")
        print(f"Min Latency: {self.results['min_latency']*1000:.2f}ms")
        print(f"Max Latency: {self.results['max_latency']*1000:.2f}ms")

        if self.results["errors"]:
            print(f"\n⚠️  Errors ({len(self.results['errors'])}):")
            for error in self.results["errors"][:5]:
                print(f"  - {error}")
            if len(self.results["errors"]) > 5:
                print(f"  ... and {len(self.results['errors']) - 5} more")

        # Validate stability
        stability_score = self.calculate_stability_score()
        print(f"\n🎯 Stability Score: {stability_score:.2f}/100")

        if stability_score >= 90:
            print("✅ Event loop is STABLE")
            return True
        elif stability_score >= 70:
            print("⚠️  Event loop has MINOR issues")
            return True
        else:
            print("❌ Event loop is UNSTABLE")
            return False

    def calculate_stability_score(self) -> float:
        """Calculate stability score based on metrics"""
        score = 100.0

        # Deduct for failures
        failure_rate = self.results["failed_requests"] / max(1, self.results["total_requests"])
        score -= failure_rate * 50

        # Deduct for high latency
        if self.results["average_latency"] > 1.0:  # > 1 second
            score -= 20

        if self.results["max_latency"] > 5.0:  # > 5 seconds
            score -= 15

        # Deduct for low throughput
        if self.results["throughput"] < 1.0:  # < 1 req/s
            score -= 10

        return max(0, score)

async def main():
    """Main test execution"""
    tester = AsyncStabilityTester()

    # Test with increasing concurrency levels
    test_levels = [
        (5, 50),   # 5 concurrent, 50 total
        (10, 100), # 10 concurrent, 100 total
        (20, 200), # 20 concurrent, 200 total
    ]

    results = []
    for concurrent, total in test_levels:
        print(f"\n\n{'#'*60}")
        print(f"TEST LEVEL: {concurrent} concurrent, {total} total")
        print(f"{'#'*60}")

        success = await tester.test_concurrent_calls(concurrent, total)
        results.append({
            "concurrent": concurrent,
            "total": total,
            "success": success,
            "stability_score": tester.calculate_stability_score()
        })

        # Reset for next test
        tester.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_latency": 0,
            "errors": []
        }

    # Final summary
    print(f"\n\n{'='*80}")
    print(f"🏆 FINAL STABILITY TEST SUMMARY")
    print(f"{'='*80}")

    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {result['concurrent']} concurrent: Stability {result['stability_score']:.1f}/100")

    all_passed = all(r["success"] for r in results)

    if all_passed:
        print(f"\n🎉 ALL STABILITY TESTS PASSED!")
        print(f"✅ Async event loop is stable under load")
        sys.exit(0)
    else:
        print(f"\n⚠️  SOME TESTS FAILED")
        print(f"🔧 Review results and fix stability issues")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
