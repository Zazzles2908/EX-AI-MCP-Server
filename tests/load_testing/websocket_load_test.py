"""
WebSocket Load Testing for Phase 2 Logging Optimization

Tests realistic WebSocket traffic patterns to validate:
- Log volume reduction (expected 90%)
- Performance improvement (expected 5-10x faster)
- Critical log preservation (WARNING/ERROR still visible)
- System stability under load

Created: 2025-10-28
EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
"""

import asyncio
import json
import time
import websockets
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import statistics


@dataclass
class LoadTestMetrics:
    """Metrics collected during load testing."""
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_errors: int = 0
    response_times: List[float] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float = 0
    
    def add_response_time(self, response_time: float):
        """Add a response time measurement."""
        self.response_times.append(response_time)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        duration = self.end_time - self.start_time
        
        if not self.response_times:
            return {
                "duration_seconds": duration,
                "messages_sent": self.total_messages_sent,
                "messages_received": self.total_messages_received,
                "errors": self.total_errors,
                "throughput_msg_per_sec": 0,
                "avg_response_time_ms": 0,
                "p50_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "p99_response_time_ms": 0,
                "max_response_time_ms": 0
            }
        
        return {
            "duration_seconds": duration,
            "messages_sent": self.total_messages_sent,
            "messages_received": self.total_messages_received,
            "errors": self.total_errors,
            "throughput_msg_per_sec": self.total_messages_sent / duration if duration > 0 else 0,
            "avg_response_time_ms": statistics.mean(self.response_times) * 1000,
            "p50_response_time_ms": statistics.median(self.response_times) * 1000,
            "p95_response_time_ms": statistics.quantiles(self.response_times, n=20)[18] * 1000,
            "p99_response_time_ms": statistics.quantiles(self.response_times, n=100)[98] * 1000,
            "max_response_time_ms": max(self.response_times) * 1000
        }


async def send_chat_request(websocket, session_id: str, prompt: str) -> float:
    """
    Send a chat request and measure response time.
    
    Returns:
        Response time in seconds
    """
    request = {
        "jsonrpc": "2.0",
        "id": f"test-{time.time()}",
        "method": "tools/call",
        "params": {
            "name": "chat_EXAI-WS-VSCode2",
            "arguments": {
                "prompt": prompt,
                "model": "glm-4.5-flash",
                "use_websearch": False
            }
        }
    }
    
    start_time = time.time()
    await websocket.send(json.dumps(request))
    
    # Wait for response
    response = await websocket.recv()
    end_time = time.time()
    
    return end_time - start_time


async def websocket_client_worker(
    worker_id: int,
    num_requests: int,
    metrics: LoadTestMetrics,
    ws_url: str = "ws://localhost:8079"
):
    """
    Worker that sends multiple WebSocket requests.
    
    Args:
        worker_id: Unique worker identifier
        num_requests: Number of requests to send
        metrics: Shared metrics object
        ws_url: WebSocket URL
    """
    session_id = f"load-test-worker-{worker_id}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            # Send initialization
            init_msg = {
                "jsonrpc": "2.0",
                "id": "init",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": f"load-test-worker-{worker_id}",
                        "version": "1.0.0"
                    }
                }
            }
            await websocket.send(json.dumps(init_msg))
            await websocket.recv()  # Wait for init response
            
            # Send requests
            for i in range(num_requests):
                try:
                    prompt = f"Test message {i} from worker {worker_id}"
                    response_time = await send_chat_request(websocket, session_id, prompt)
                    
                    metrics.total_messages_sent += 1
                    metrics.total_messages_received += 1
                    metrics.add_response_time(response_time)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"Worker {worker_id} error on request {i}: {e}")
                    metrics.total_errors += 1
    
    except Exception as e:
        print(f"Worker {worker_id} connection error: {e}")
        metrics.total_errors += 1


async def run_load_test(
    num_workers: int = 5,
    requests_per_worker: int = 20,
    ws_url: str = "ws://localhost:8079"
) -> LoadTestMetrics:
    """
    Run load test with multiple concurrent workers.
    
    Args:
        num_workers: Number of concurrent WebSocket clients
        requests_per_worker: Number of requests each worker sends
        ws_url: WebSocket URL
    
    Returns:
        LoadTestMetrics with results
    """
    print(f"\n{'='*60}")
    print(f"WebSocket Load Test - Phase 2 Logging Optimization")
    print(f"{'='*60}")
    print(f"Workers: {num_workers}")
    print(f"Requests per worker: {requests_per_worker}")
    print(f"Total requests: {num_workers * requests_per_worker}")
    print(f"WebSocket URL: {ws_url}")
    print(f"{'='*60}\n")
    
    metrics = LoadTestMetrics()
    
    # Create worker tasks
    tasks = [
        websocket_client_worker(i, requests_per_worker, metrics, ws_url)
        for i in range(num_workers)
    ]
    
    # Run all workers concurrently
    print(f"Starting {num_workers} workers...")
    await asyncio.gather(*tasks)
    
    metrics.end_time = time.time()
    
    return metrics


def print_results(metrics: LoadTestMetrics):
    """Print load test results."""
    summary = metrics.get_summary()
    
    print(f"\n{'='*60}")
    print(f"Load Test Results")
    print(f"{'='*60}")
    print(f"Duration: {summary['duration_seconds']:.2f}s")
    print(f"Messages sent: {summary['messages_sent']}")
    print(f"Messages received: {summary['messages_received']}")
    print(f"Errors: {summary['errors']}")
    print(f"Throughput: {summary['throughput_msg_per_sec']:.2f} msg/sec")
    print(f"\nResponse Times:")
    print(f"  Average: {summary['avg_response_time_ms']:.2f}ms")
    print(f"  Median (P50): {summary['p50_response_time_ms']:.2f}ms")
    print(f"  P95: {summary['p95_response_time_ms']:.2f}ms")
    print(f"  P99: {summary['p99_response_time_ms']:.2f}ms")
    print(f"  Max: {summary['max_response_time_ms']:.2f}ms")
    print(f"{'='*60}\n")
    
    # Performance assessment
    avg_response = summary['avg_response_time_ms']
    if avg_response < 500:
        print("✅ EXCELLENT: Average response time < 500ms")
    elif avg_response < 1000:
        print("✅ GOOD: Average response time < 1s")
    elif avg_response < 2000:
        print("⚠️  ACCEPTABLE: Average response time < 2s")
    else:
        print("❌ POOR: Average response time > 2s")
    
    error_rate = summary['errors'] / summary['messages_sent'] if summary['messages_sent'] > 0 else 0
    if error_rate == 0:
        print("✅ EXCELLENT: No errors")
    elif error_rate < 0.01:
        print("✅ GOOD: Error rate < 1%")
    elif error_rate < 0.05:
        print("⚠️  ACCEPTABLE: Error rate < 5%")
    else:
        print("❌ POOR: Error rate > 5%")


async def main():
    """Main entry point."""
    # Test scenarios
    scenarios = [
        {"name": "Light Load", "workers": 2, "requests": 10},
        {"name": "Medium Load", "workers": 5, "requests": 20},
        {"name": "Heavy Load", "workers": 10, "requests": 30},
    ]
    
    all_results = []
    
    for scenario in scenarios:
        print(f"\n{'#'*60}")
        print(f"# Scenario: {scenario['name']}")
        print(f"{'#'*60}")
        
        metrics = await run_load_test(
            num_workers=scenario['workers'],
            requests_per_worker=scenario['requests']
        )
        
        print_results(metrics)
        all_results.append({
            "scenario": scenario['name'],
            "metrics": metrics.get_summary()
        })
        
        # Wait between scenarios
        print("Waiting 5 seconds before next scenario...")
        await asyncio.sleep(5)
    
    # Summary comparison
    print(f"\n{'='*60}")
    print(f"Scenario Comparison")
    print(f"{'='*60}")
    print(f"{'Scenario':<20} {'Avg Response (ms)':<20} {'Throughput (msg/s)':<20}")
    print(f"{'-'*60}")
    for result in all_results:
        scenario = result['scenario']
        metrics = result['metrics']
        print(f"{scenario:<20} {metrics['avg_response_time_ms']:<20.2f} {metrics['throughput_msg_per_sec']:<20.2f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())

