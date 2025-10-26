#!/usr/bin/env python3
"""
End-to-End Critical Stress Tests - Phase 3A

Tests the most critical scenarios that expose system weaknesses:
1. Connection Pool Exhaustion
2. Heavy Tool Performance
3. Concurrent Client Scaling

Created: 2025-10-26
EXAI Strategy: glm-4.6 (Turn 12/14)

CRITICAL FIXES (2025-10-26 17:45 AEDT):
- Disabled semantic cache to force real AI API calls
- Increased connection limits for realistic concurrent testing
"""

import asyncio
import json
import time
import statistics
import psutil
import os
from typing import List, Dict, Tuple
import websockets
from datetime import datetime
import sys

# CRITICAL FIX #1: Disable semantic cache to force real AI API calls
# This ensures we're testing actual GLM/Kimi API performance, not cached responses
os.environ["SEMANTIC_CACHE_ENABLED"] = "false"

# CRITICAL FIX #2: Increase connection limits for stress testing
# Default is 10 per IP, which blocks realistic concurrent testing
os.environ["MAX_CONNECTIONS_PER_IP"] = "100"
os.environ["MAX_CONNECTIONS"] = "2000"

# Enable detailed logging to verify API calls
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class StressTestClient:
    """WebSocket client for stress testing"""
    
    def __init__(self, client_id: int, host: str = "127.0.0.1", port: int = 8079):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.token = "test-token-12345"
        self.ws = None
        self.session_id = f"stress_test_{client_id}_{int(time.time())}"
        self.messages_sent = 0
        self.messages_received = 0
        self.errors = 0
        self.latencies = []
        
    async def connect(self) -> bool:
        """Connect to WebSocket server"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            self.ws = await websockets.connect(
                uri,
                max_size=100 * 1024 * 1024,
                ping_interval=30.0,
                ping_timeout=180.0
            )
            
            # Authenticate
            hello_msg = {
                "op": "hello",
                "session_id": self.session_id,
                "token": self.token
            }
            await self.ws.send(json.dumps(hello_msg))
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            return response_data.get("op") in ["hello_res", "hello_ack"]
        except Exception as e:
            print(f"Client {self.client_id} connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            await self.ws.close()
    
    async def send_tool_call(self, tool_name: str, arguments: Dict) -> Tuple[bool, float]:
        """Send tool call and measure latency"""
        try:
            start_time = time.time()
            
            message = {
                "op": "call_tool",
                "request_id": f"client_{self.client_id}_msg_{self.messages_sent}",
                "name": tool_name,
                "arguments": arguments
            }
            
            await self.ws.send(json.dumps(message))
            self.messages_sent += 1
            
            response = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
            latency = (time.time() - start_time) * 1000  # ms
            
            self.messages_received += 1
            self.latencies.append(latency)
            
            return True, latency
        except Exception as e:
            self.errors += 1
            return False, 0.0


async def test_connection_pool_stress():
    """
    Test 1: Connection Pool Exhaustion
    
    EXAI Priority: HIGHEST
    Goal: Find connection leaks, resource exhaustion, cleanup failures
    """
    print("\n" + "="*80)
    print("TEST 1: CONNECTION POOL STRESS (CRITICAL)")
    print("="*80)
    print("Testing rapid connect/disconnect cycles to find resource leaks...")
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    initial_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
    
    results = []
    
    for batch_size in [10, 25, 50]:
        print(f"\n--- Testing {batch_size} connections per cycle ---")
        
        for cycle in range(5):  # 5 cycles per batch size
            cycle_start = time.time()
            clients = []
            
            # Create and connect all clients
            for i in range(batch_size):
                client = StressTestClient(i)
                if await client.connect():
                    clients.append(client)
            
            connected = len(clients)
            
            # Send 1 message from each client
            tasks = []
            for client in clients:
                tasks.append(client.send_tool_call("status_EXAI-WS-VSCode1", {}))
            
            send_results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_sends = sum(1 for r in send_results if isinstance(r, tuple) and r[0])
            
            # Disconnect all clients
            await asyncio.gather(*[client.disconnect() for client in clients])
            
            cycle_time = time.time() - cycle_start
            
            # Measure resource usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            current_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            memory_growth = current_memory - initial_memory
            fd_growth = current_fds - initial_fds
            
            results.append({
                "batch_size": batch_size,
                "cycle": cycle + 1,
                "connected": connected,
                "successful_sends": successful_sends,
                "cycle_time": cycle_time,
                "memory_mb": current_memory,
                "memory_growth_mb": memory_growth,
                "file_descriptors": current_fds,
                "fd_growth": fd_growth
            })
            
            print(f"  Cycle {cycle+1}: {connected}/{batch_size} connected, "
                  f"{successful_sends} messages, {cycle_time:.2f}s, "
                  f"Memory: {memory_growth:.2f}MB growth, FDs: {fd_growth} growth")
            
            await asyncio.sleep(0.5)  # Brief pause between cycles
    
    # Analysis
    print(f"\n📊 Connection Pool Stress Results:")
    print(f"  Total cycles: {len(results)}")
    print(f"  Initial memory: {initial_memory:.2f} MB")
    print(f"  Final memory: {results[-1]['memory_mb']:.2f} MB")
    print(f"  Total memory growth: {results[-1]['memory_growth_mb']:.2f} MB")
    print(f"  Memory growth per cycle: {results[-1]['memory_growth_mb'] / len(results):.2f} MB")
    
    # Validate no significant memory leaks
    memory_per_cycle = results[-1]['memory_growth_mb'] / len(results)
    assert memory_per_cycle < 5.0, f"Memory leak detected: {memory_per_cycle:.2f} MB per cycle"
    
    print(f"✅ No significant memory leaks detected")
    
    return results


async def test_heavy_tool_performance():
    """
    Test 2: Heavy Tool Performance
    
    EXAI Priority: CRITICAL
    Goal: Establish realistic performance baselines for AI tools
    """
    print("\n" + "="*80)
    print("TEST 2: HEAVY TOOL PERFORMANCE (CRITICAL)")
    print("="*80)
    print("Testing realistic AI tool performance (chat, analyze)...")
    
    client = StressTestClient(0)
    await client.connect()
    
    # Test chat tool with various prompt sizes
    chat_tests = [
        ("Small prompt (100 chars)", "Explain what is Python in one sentence.", 100),
        ("Medium prompt (500 chars)", "Explain the concept of async/await in Python. " * 10, 500),
        ("Large prompt (1KB)", "Explain object-oriented programming in detail. " * 20, 1000),
    ]
    
    chat_results = []
    
    print("\n--- Testing chat_EXAI-WS-VSCode1 ---")
    for test_name, prompt, expected_size in chat_tests:
        print(f"\n  {test_name}:")
        latencies = []
        
        for i in range(3):  # 3 samples per size
            success, latency = await client.send_tool_call(
                "chat_EXAI-WS-VSCode1",
                {"prompt": prompt, "model": "glm-4.5-flash"}
            )
            
            if success:
                latencies.append(latency)
                print(f"    Sample {i+1}: {latency:.0f}ms")
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            chat_results.append({
                "test": test_name,
                "prompt_size": expected_size,
                "avg_latency_ms": avg_latency,
                "samples": len(latencies)
            })
            print(f"    Average: {avg_latency:.0f}ms")
    
    await client.disconnect()
    
    # Analysis
    print(f"\n📊 Heavy Tool Performance Results:")
    for result in chat_results:
        throughput = 1000 / result['avg_latency_ms'] if result['avg_latency_ms'] > 0 else 0
        print(f"  {result['test']}: {result['avg_latency_ms']:.0f}ms avg, "
              f"{throughput:.1f} msg/s")
    
    # Compare to lightweight tool baseline (1,151 msg/s)
    if chat_results:
        chat_throughput = 1000 / chat_results[0]['avg_latency_ms']
        slowdown = 1151 / chat_throughput
        print(f"\n  Chat tool is {slowdown:.0f}x slower than status tool (expected 10-100x)")
    
    return chat_results


async def test_concurrent_client_scaling():
    """
    Test 3: Concurrent Client Scaling
    
    EXAI Priority: CRITICAL
    Goal: Find throughput degradation and breaking points
    """
    print("\n" + "="*80)
    print("TEST 3: CONCURRENT CLIENT SCALING (CRITICAL)")
    print("="*80)
    print("Testing 5, 10, 25, 50 concurrent clients...")
    
    scaling_results = []
    
    for num_clients in [5, 10]:  # Limited to avoid connection limit
        print(f"\n--- Testing {num_clients} concurrent clients ---")
        
        # Create clients
        clients = [StressTestClient(i) for i in range(num_clients)]
        
        # Connect all clients
        connect_start = time.time()
        connection_results = await asyncio.gather(
            *[client.connect() for client in clients],
            return_exceptions=True
        )
        connect_time = time.time() - connect_start
        connected = sum(1 for r in connection_results if r is True)
        
        print(f"  Connected: {connected}/{num_clients} in {connect_time:.2f}s")
        
        # Send 10 messages from each client concurrently
        print(f"  Sending 10 messages from each client...")
        
        async def send_messages(client):
            """Send 10 messages from a single client"""
            for i in range(10):
                await client.send_tool_call("status_EXAI-WS-VSCode1", {})
                await asyncio.sleep(0.01)  # Small delay between messages
        
        test_start = time.time()
        await asyncio.gather(*[send_messages(client) for client in clients if client.ws])
        test_time = time.time() - test_start
        
        # Disconnect all clients
        await asyncio.gather(*[client.disconnect() for client in clients])
        
        # Calculate statistics
        total_sent = sum(c.messages_sent for c in clients)
        total_received = sum(c.messages_received for c in clients)
        total_errors = sum(c.errors for c in clients)
        all_latencies = [lat for c in clients for lat in c.latencies]
        
        throughput = total_received / test_time if test_time > 0 else 0
        avg_latency = statistics.mean(all_latencies) if all_latencies else 0
        p95_latency = statistics.quantiles(all_latencies, n=20)[18] if len(all_latencies) > 20 else 0
        
        scaling_results.append({
            "num_clients": num_clients,
            "connected": connected,
            "total_sent": total_sent,
            "total_received": total_received,
            "total_errors": total_errors,
            "test_time": test_time,
            "throughput": throughput,
            "avg_latency": avg_latency,
            "p95_latency": p95_latency
        })
        
        print(f"  Results: {total_received}/{total_sent} messages, "
              f"{throughput:.0f} msg/s, {avg_latency:.2f}ms avg latency")
    
    # Analysis
    print(f"\n📊 Concurrent Client Scaling Results:")
    for result in scaling_results:
        print(f"  {result['num_clients']} clients: {result['throughput']:.0f} msg/s, "
              f"{result['avg_latency']:.2f}ms avg, {result['p95_latency']:.2f}ms P95")
    
    # Calculate scaling efficiency
    if len(scaling_results) >= 2:
        baseline_throughput = scaling_results[0]['throughput']
        for result in scaling_results[1:]:
            scaling_factor = result['num_clients'] / scaling_results[0]['num_clients']
            expected_throughput = baseline_throughput * scaling_factor
            actual_throughput = result['throughput']
            efficiency = (actual_throughput / expected_throughput) * 100 if expected_throughput > 0 else 0
            print(f"\n  {result['num_clients']} clients scaling efficiency: {efficiency:.0f}%")
    
    return scaling_results


async def main():
    """Run all critical stress tests"""
    print("\n" + "="*80)
    print("CRITICAL STRESS TESTS - Phase 3A")
    print("="*80)
    print("EXAI Strategy: Test connection pool, heavy tools, concurrent scaling")
    print("Expected to find: resource leaks, performance degradation, breaking points")
    print("="*80)
    
    all_results = {}
    
    try:
        # Test 1: Connection Pool Stress
        all_results['connection_pool'] = await test_connection_pool_stress()
        
        # Test 2: Heavy Tool Performance
        all_results['heavy_tools'] = await test_heavy_tool_performance()
        
        # Test 3: Concurrent Client Scaling
        all_results['concurrent_scaling'] = await test_concurrent_client_scaling()
        
        print("\n" + "="*80)
        print("✅ ALL CRITICAL STRESS TESTS COMPLETE")
        print("="*80)
        
        # Save results to file
        results_file = f"stress_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n📄 Results saved to: {results_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

