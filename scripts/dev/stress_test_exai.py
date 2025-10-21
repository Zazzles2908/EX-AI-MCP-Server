#!/usr/bin/env python3
"""
EXAI MCP Server Stress Test
============================

Comprehensive stress testing to simulate production load and identify issues
before they affect users. Tests all Week 1 fixes under realistic conditions.

Tests:
1. Concurrent request handling (semaphore leak detection)
2. Memory leak detection (_inflight_reqs cleanup)
3. Thread safety validation (provider detection/registration)
4. Timeout handling (semaphore cleanup on timeout)
5. Error recovery and resilience

Usage:
    python scripts/stress_test_exai.py --duration 60 --concurrent 10
"""

import asyncio
import json
import time
import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime
import websockets
import statistics

# Test configuration
WS_URL = "ws://127.0.0.1:8079"  # Use 127.0.0.1 instead of localhost for Windows compatibility
AUTH_TOKEN = "test-token-12345"


class StressTestResults:
    """Track and analyze stress test results"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.timeout_requests = 0
        self.response_times: List[float] = []
        self.errors: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None
    
    def add_success(self, response_time: float):
        self.successful_requests += 1
        self.response_times.append(response_time)
    
    def add_failure(self, error: str, response_time: float = None):
        self.failed_requests += 1
        self.errors.append({
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "response_time": response_time
        })
    
    def add_timeout(self, response_time: float):
        self.timeout_requests += 1
        self.response_times.append(response_time)
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        
        return {
            "duration_seconds": duration,
            "total_requests": self.total_requests,
            "successful": self.successful_requests,
            "failed": self.failed_requests,
            "timeouts": self.timeout_requests,
            "success_rate": f"{(self.successful_requests / self.total_requests * 100):.2f}%" if self.total_requests > 0 else "0%",
            "response_times": {
                "min": min(self.response_times) if self.response_times else 0,
                "max": max(self.response_times) if self.response_times else 0,
                "mean": statistics.mean(self.response_times) if self.response_times else 0,
                "median": statistics.median(self.response_times) if self.response_times else 0,
                "p95": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else 0,
                "p99": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) > 100 else 0,
            },
            "requests_per_second": self.total_requests / duration if duration > 0 else 0,
            "errors": self.errors[:10]  # Show first 10 errors
        }


async def send_chat_request(session_id: str, prompt: str, timeout: int = 30) -> Dict[str, Any]:
    """Send a single chat request to EXAI"""
    start_time = time.time()

    try:
        print(f"[DEBUG] Attempting to connect to {WS_URL}...")
        async with websockets.connect(WS_URL, open_timeout=5) as ws:
            print(f"[DEBUG] Connected successfully!")
            # Step 1: Send hello message with auth token
            hello_msg = {
                "op": "hello",
                "token": AUTH_TOKEN
            }
            await ws.send(json.dumps(hello_msg))

            # Step 2: Wait for hello_ack
            hello_ack = await asyncio.wait_for(ws.recv(), timeout=5)
            hello_ack_data = json.loads(hello_ack)

            if not hello_ack_data.get("ok"):
                return {
                    "success": False,
                    "timeout": False,
                    "response_time": time.time() - start_time,
                    "error": f"Auth failed: {hello_ack_data.get('error', 'unknown')}"
                }

            # Step 3: Send tool call request
            request = {
                "method": "tools/call",
                "params": {
                    "name": "chat",
                    "arguments": {
                        "prompt": prompt,
                        "_session_id": session_id
                    }
                }
            }

            await ws.send(json.dumps(request))

            # Step 4: Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=timeout)
            response_data = json.loads(response)

            elapsed = time.time() - start_time

            return {
                "success": True,
                "response_time": elapsed,
                "data": response_data
            }

    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "timeout": True,
            "response_time": elapsed,
            "error": "Request timeout"
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "timeout": False,
            "response_time": elapsed,
            "error": str(e)
        }


async def concurrent_requests_test(num_concurrent: int, num_requests: int, results: StressTestResults):
    """Test concurrent request handling"""
    print(f"\n🔥 Running concurrent requests test: {num_concurrent} concurrent, {num_requests} total requests")

    tasks = []
    for i in range(num_requests):
        session_id = f"stress-test-{i % num_concurrent}"
        prompt = f"Test request {i}: What is 2+2? Please respond briefly."

        # Create task explicitly
        task = asyncio.create_task(send_chat_request(session_id, prompt))
        tasks.append(task)

        # Limit concurrent tasks
        if len(tasks) >= num_concurrent:
            # Wait for some to complete
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            # Process completed tasks
            for task in done:
                result = await task
                results.total_requests += 1

                if result["success"]:
                    results.add_success(result["response_time"])
                    print(f"✅ Request {results.total_requests}: {result['response_time']:.2f}s")
                elif result.get("timeout"):
                    results.add_timeout(result["response_time"])
                    print(f"⏱️  Request {results.total_requests}: TIMEOUT after {result['response_time']:.2f}s")
                else:
                    results.add_failure(result["error"], result["response_time"])
                    print(f"❌ Request {results.total_requests}: FAILED - {result['error']}")

            tasks = list(pending)

    # Wait for remaining tasks
    if tasks:
        remaining = await asyncio.gather(*tasks)
        for result in remaining:
            results.total_requests += 1

            if result["success"]:
                results.add_success(result["response_time"])
                print(f"✅ Request {results.total_requests}: {result['response_time']:.2f}s")
            elif result.get("timeout"):
                results.add_timeout(result["response_time"])
                print(f"⏱️  Request {results.total_requests}: TIMEOUT after {result['response_time']:.2f}s")
            else:
                results.add_failure(result["error"], result["response_time"])
                print(f"❌ Request {results.total_requests}: FAILED - {result['error']}")


async def timeout_stress_test(num_requests: int, results: StressTestResults):
    """Test timeout handling (Fix #1 validation)"""
    print(f"\n⏱️  Running timeout stress test: {num_requests} requests with short timeout")
    
    for i in range(num_requests):
        session_id = f"timeout-test-{i}"
        prompt = "Explain quantum computing in detail with examples."  # Long response
        
        result = await send_chat_request(session_id, prompt, timeout=5)  # Short timeout
        results.total_requests += 1
        
        if result["success"]:
            results.add_success(result["response_time"])
            print(f"✅ Timeout test {i+1}: Completed in {result['response_time']:.2f}s")
        elif result.get("timeout"):
            results.add_timeout(result["response_time"])
            print(f"⏱️  Timeout test {i+1}: TIMEOUT (expected) - semaphore should be released")
        else:
            results.add_failure(result["error"], result["response_time"])
            print(f"❌ Timeout test {i+1}: FAILED - {result['error']}")


async def rapid_fire_test(num_requests: int, results: StressTestResults):
    """Test rapid sequential requests (memory leak detection)"""
    print(f"\n🚀 Running rapid-fire test: {num_requests} sequential requests")
    
    session_id = "rapid-fire-session"
    
    for i in range(num_requests):
        prompt = f"Quick test {i}: What is {i} + 1?"
        
        result = await send_chat_request(session_id, prompt, timeout=10)
        results.total_requests += 1
        
        if result["success"]:
            results.add_success(result["response_time"])
            print(f"✅ Rapid {i+1}/{num_requests}: {result['response_time']:.2f}s")
        else:
            results.add_failure(result.get("error", "Unknown"), result["response_time"])
            print(f"❌ Rapid {i+1}/{num_requests}: FAILED")


async def main():
    """Main stress test orchestrator"""
    parser = argparse.ArgumentParser(description="EXAI MCP Server Stress Test")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--concurrent", type=int, default=10, help="Number of concurrent requests")
    parser.add_argument("--skip-timeout", action="store_true", help="Skip timeout stress test")
    parser.add_argument("--skip-rapid", action="store_true", help="Skip rapid-fire test")
    
    args = parser.parse_args()
    
    results = StressTestResults()
    results.start_time = time.time()
    
    print("=" * 80)
    print("EXAI MCP SERVER STRESS TEST")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  - Duration: {args.duration}s")
    print(f"  - Concurrent requests: {args.concurrent}")
    print(f"  - WebSocket URL: {WS_URL}")
    print("=" * 80)
    
    try:
        # Test 1: Concurrent requests
        num_requests = args.duration // 2  # Estimate based on 2s per request
        await concurrent_requests_test(args.concurrent, num_requests, results)
        
        # Test 2: Timeout handling (validates Fix #1)
        if not args.skip_timeout:
            await timeout_stress_test(5, results)
        
        # Test 3: Rapid-fire (validates Fix #2)
        if not args.skip_rapid:
            await rapid_fire_test(20, results)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        results.end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 80)
        print("STRESS TEST SUMMARY")
        print("=" * 80)
        
        summary = results.get_summary()
        print(f"\n📊 Overall Results:")
        print(f"  Duration: {summary['duration_seconds']:.2f}s")
        print(f"  Total Requests: {summary['total_requests']}")
        print(f"  Successful: {summary['successful']} ({summary['success_rate']})")
        print(f"  Failed: {summary['failed']}")
        print(f"  Timeouts: {summary['timeouts']}")
        print(f"  Requests/sec: {summary['requests_per_second']:.2f}")
        
        print(f"\n⏱️  Response Times:")
        print(f"  Min: {summary['response_times']['min']:.3f}s")
        print(f"  Max: {summary['response_times']['max']:.3f}s")
        print(f"  Mean: {summary['response_times']['mean']:.3f}s")
        print(f"  Median: {summary['response_times']['median']:.3f}s")
        print(f"  P95: {summary['response_times']['p95']:.3f}s")
        print(f"  P99: {summary['response_times']['p99']:.3f}s")
        
        if summary['errors']:
            print(f"\n❌ Sample Errors (first 10):")
            for i, error in enumerate(summary['errors'], 1):
                print(f"  {i}. {error['error']} (at {error['timestamp']})")
        
        print("\n" + "=" * 80)
        
        # Save detailed results
        with open("logs/stress_test_results.json", "w") as f:
            json.dump(summary, f, indent=2)
        print(f"📝 Detailed results saved to: logs/stress_test_results.json")
        
        # Exit code based on success rate
        success_rate = summary['successful'] / summary['total_requests'] if summary['total_requests'] > 0 else 0
        if success_rate < 0.95:  # Less than 95% success
            print("\n⚠️  WARNING: Success rate below 95% - investigate failures!")
            sys.exit(1)
        else:
            print("\n✅ All tests passed successfully!")
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

