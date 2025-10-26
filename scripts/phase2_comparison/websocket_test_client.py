#!/usr/bin/env python3
"""
Fair WebSocket Test Client for Phase 2.3 Provider Comparison

This client ensures fair comparison between providers by:
- Using identical prompts for both providers
- Enforcing identical generation parameters
- Testing through MCP WebSocket server (production flow)
- Collecting comprehensive latency metrics
- Performing statistical analysis

Created: 2025-10-25
EXAI Validated: glm-4.6
"""

import asyncio
import json
import time
import random
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import websockets
from websockets.client import WebSocketClientProtocol
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FairWebSocketTestClient:
    """
    WebSocket-based test client that ensures fair provider comparison
    
    Key Features:
    - Connects to MCP WebSocket server (ws://localhost:8079)
    - Enforces identical parameters for both providers
    - Collects comprehensive latency metrics
    - Performs statistical analysis
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8079,
        token: str = "test-token-12345",
        max_message_size: int = 100 * 1024 * 1024  # 100MB
    ):
        self.host = host
        self.port = port
        self.token = token
        self.max_message_size = max_message_size
        self.ws: Optional[WebSocketClientProtocol] = None
        self.session_id = f"phase2_test_{int(time.time())}"
        self._ws_lock = asyncio.Lock()  # Serialize WebSocket communication

        # PHASE 2.3 FIX (2025-10-25): Add streaming response tracking (EXAI validated)
        self.streaming_responses = {}  # request_id -> list of chunks
        self.request_start_times = {}  # request_id -> start time
        self.latencies = []  # List of response latencies
        
    async def connect(self):
        """Connect to MCP WebSocket server and authenticate"""
        uri = f"ws://{self.host}:{self.port}"
        logger.info(f"Connecting to {uri}...")

        # PHASE 2.3 FIX (2025-10-25): Match server ping_timeout (180s) for AI processing
        # EXAI Analysis: Client/server timeout mismatch causes reliability issues
        # Server has ping_interval=30s, ping_timeout=180s
        # Client MUST match server timeout to avoid premature disconnection
        self.ws = await websockets.connect(
            uri,
            max_size=self.max_message_size,
            ping_interval=30.0,   # Match server's 30s interval
            ping_timeout=180.0    # Match server's 180s timeout (EXAI validated)
        )
        
        # Send hello message for authentication
        hello_msg = {
            "op": "hello",
            "session_id": self.session_id,
            "token": self.token
        }
        await self.ws.send(json.dumps(hello_msg))
        
        # Wait for hello response
        response = await self.ws.recv()
        response_data = json.loads(response)

        # Accept both hello_res and hello_ack as valid responses
        if response_data.get("op") not in ["hello_res", "hello_ack"] or not response_data.get("ok"):
            raise Exception(f"Authentication failed: {response_data}")

        logger.info("✅ Connected and authenticated")
        
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.ws:
            await self.ws.close()
            logger.info("Disconnected from server")

    def get_latency_stats(self) -> Dict:
        """
        Return latency statistics

        PHASE 2.3 FIX (2025-10-25): Added latency tracking (EXAI validated)
        """
        if not self.latencies:
            return {"avg": 0, "min": 0, "max": 0, "count": 0}

        return {
            "avg": sum(self.latencies) / len(self.latencies),
            "min": min(self.latencies),
            "max": max(self.latencies),
            "count": len(self.latencies)
        }
            
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict,
        timeout: float = 300.0
    ) -> Tuple[bool, Optional[Dict], float]:
        """
        Call a tool through MCP WebSocket server

        Handles both streaming and non-streaming responses.

        Returns:
            (success, result, latency_ms)
        """
        # Serialize WebSocket communication to prevent concurrent recv() calls
        async with self._ws_lock:
            request_id = f"req_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

            # Send tool call request
            request = {
                "op": "call_tool",
                "request_id": request_id,
                "name": tool_name,
                "arguments": arguments
            }

            start_time = time.perf_counter()
            self.request_start_times[request_id] = start_time
            await self.ws.send(json.dumps(request))

            # PHASE 2.3 FIX (2025-10-25): Handle streaming responses (EXAI validated)
            # Collect streaming chunks until stream_complete or call_tool_res
            streaming_chunks = []
            final_result = None
            success = False
            max_chunks = 10000  # Safety limit to prevent memory exhaustion

            try:
                while True:
                    response = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
                    response_data = json.loads(response)
                    op = response_data.get("op")

                    # Handle streaming chunk
                    if op == "stream_chunk":
                        chunk = response_data.get("chunk", "")
                        streaming_chunks.append(chunk)
                        logger.debug(f"Received chunk {len(streaming_chunks)}: {len(chunk)} chars")

                        # Safety check: prevent memory exhaustion
                        if len(streaming_chunks) > max_chunks:
                            logger.error(f"Streaming exceeded max chunks ({max_chunks}), aborting")
                            latency_ms = (time.perf_counter() - start_time) * 1000
                            if request_id in self.request_start_times:
                                del self.request_start_times[request_id]
                            return False, None, latency_ms

                        continue

                    # Handle streaming complete
                    elif op == "stream_complete":
                        latency_ms = (time.perf_counter() - start_time) * 1000
                        self.latencies.append(latency_ms)

                        # Combine all chunks into final result
                        full_content = "".join(streaming_chunks)
                        final_result = {
                            "content": full_content,
                            "metadata": response_data.get("metadata", {})
                        }
                        success = True

                        # Clean up tracking
                        if request_id in self.request_start_times:
                            del self.request_start_times[request_id]

                        logger.info(f"✅ Streaming complete: {len(streaming_chunks)} chunks, {latency_ms:.2f}ms")
                        return success, final_result, latency_ms

                    # Handle non-streaming response (legacy)
                    elif op == "call_tool_res":
                        latency_ms = (time.perf_counter() - start_time) * 1000
                        self.latencies.append(latency_ms)

                        success = response_data.get("ok", False)
                        outputs = response_data.get("outputs", [])

                        # Extract result
                        if outputs and len(outputs) > 0:
                            final_result = outputs[0]

                        # Clean up tracking
                        if request_id in self.request_start_times:
                            del self.request_start_times[request_id]

                        logger.info(f"✅ Non-streaming response: {latency_ms:.2f}ms")
                        return success, final_result, latency_ms

                    else:
                        logger.warning(f"Unexpected op: {op}")
                        continue

            except asyncio.TimeoutError:
                latency_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"Tool call timed out after {timeout}s")

                # Clean up tracking
                if request_id in self.request_start_times:
                    del self.request_start_times[request_id]

                return False, None, latency_ms
            
    async def run_single_test(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7
    ) -> Dict:
        """
        Run a single test with fair parameters
        
        Returns:
            Test result with comprehensive metrics
        """
        # Enforce fair parameters
        arguments = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "use_websearch": False  # Disable for fair comparison
        }
        
        # Call chat tool (EXAI-WS is the tool in Docker container, not EXAI-WS-VSCode2)
        success, result, latency_ms = await self.call_tool("chat_EXAI-WS", arguments)
        
        # Extract metrics
        metrics = {
            "success": success,
            "latency_ms": latency_ms,
            "model": model,
            "prompt": prompt[:100],  # First 100 chars for reference
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success and result:
            # Extract latency metrics from response
            if "metadata" in result and "latency_metrics" in result["metadata"]:
                latency_data = result["metadata"]["latency_metrics"]
                metrics.update({
                    "total_latency_ms": latency_data.get("latency_ms"),
                    "global_sem_wait_ms": latency_data.get("global_sem_wait_ms"),
                    "provider_sem_wait_ms": latency_data.get("provider_sem_wait_ms"),
                    "processing_ms": latency_data.get("processing_ms"),
                    "provider_name": latency_data.get("provider_name")
                })
                
            # Extract token counts
            if "metadata" in result:
                metadata = result["metadata"]
                metrics.update({
                    "tokens_in": metadata.get("tokens_in"),
                    "tokens_out": metadata.get("tokens_out"),
                    "model_used": metadata.get("model_used")
                })
                
        return metrics
        
    async def run_scenario(
        self,
        prompts: List[str],
        model: str,
        concurrency: int,
        temperature: float = 0.7,
        warmup_seconds: int = 30
    ) -> List[Dict]:
        """
        Run a test scenario with specified concurrency
        
        Args:
            prompts: List of test prompts
            model: Model to use
            concurrency: Number of concurrent requests
            temperature: Generation temperature
            warmup_seconds: Warmup period before measurement
            
        Returns:
            List of test results
        """
        logger.info(f"🔥 Warmup period: {warmup_seconds}s with {concurrency} concurrent requests")
        
        # Warmup period (not measured)
        warmup_prompts = prompts[:min(concurrency, len(prompts))]
        warmup_tasks = [
            self.run_single_test(prompt, model, temperature)
            for prompt in warmup_prompts
        ]
        await asyncio.gather(*warmup_tasks)
        await asyncio.sleep(warmup_seconds)
        
        logger.info(f"📊 Starting measurement with {len(prompts)} prompts, concurrency={concurrency}")
        
        # CRITICAL FIX (2025-10-25): Stagger requests to prevent overwhelming semaphores
        # Previous implementation sent all requests simultaneously with asyncio.gather(),
        # causing semaphore contention and network congestion
        results = []
        for i in range(0, len(prompts), concurrency):
            batch = prompts[i:i + concurrency]

            # Stagger request starts to prevent burst (EXAI validated)
            tasks = []
            for j, prompt in enumerate(batch):
                task = asyncio.create_task(self.run_single_test(prompt, model, temperature))
                tasks.append(task)

                # Add small delay between request starts (except last in batch)
                if j < len(batch) - 1:
                    await asyncio.sleep(0.2)  # 200ms stagger between requests

            # Wait for all tasks in batch to complete
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Small delay between batches
            if i + concurrency < len(prompts):
                await asyncio.sleep(1.0)
                
        logger.info(f"✅ Completed {len(results)} tests")
        return results
        
    def analyze_results(self, results: List[Dict]) -> Dict:
        """
        Perform statistical analysis on test results

        Returns:
            Statistical summary (ALWAYS returns expected keys)
        """
        # EXAI FIX: Always return expected structure, even for empty/error cases
        if not results:
            return {
                "total_tests": 0,
                "successful_tests": 0,
                "success_rate": 0.0,
                "mean_latency_ms": 0.0,
                "median_latency_ms": 0.0,
                "min_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "stdev_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "cv_latency": 0.0,
                "error": "No results provided"
            }

        # Filter successful results
        successful = [r for r in results if r.get("success", False)]
        latencies = [r.get("latency_ms", 0) for r in successful]
        processing_times = [r.get("processing_ms", 0) for r in successful if r.get("processing_ms")]

        # EXAI FIX: Handle case where no successful results
        if not successful or not latencies:
            return {
                "total_tests": len(results),
                "successful_tests": 0,
                "success_rate": 0.0,
                "mean_latency_ms": 0.0,
                "median_latency_ms": 0.0,
                "min_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "stdev_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "cv_latency": 0.0,
                "error": "No successful results"
            }

        # Calculate statistics
        analysis = {
            "total_tests": len(results),
            "successful_tests": len(successful),
            "success_rate": len(successful) / len(results) if results else 0.0,

            # Latency statistics
            "mean_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "stdev_latency_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0.0,

            # Percentiles
            "p50_latency_ms": statistics.median(latencies),
            "p95_latency_ms": self._percentile(latencies, 0.95),
            "p99_latency_ms": self._percentile(latencies, 0.99),
        }

        # Coefficient of variation (consistency metric)
        if analysis["mean_latency_ms"] > 0:
            analysis["cv_latency"] = analysis["stdev_latency_ms"] / analysis["mean_latency_ms"]
        else:
            analysis["cv_latency"] = 0.0

        # Processing time statistics (if available)
        if processing_times:
            analysis.update({
                "mean_processing_ms": statistics.mean(processing_times),
                "median_processing_ms": statistics.median(processing_times),
            })

        return analysis
        
    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]


async def main():
    """Example usage"""
    client = FairWebSocketTestClient()
    
    try:
        await client.connect()
        
        # Test prompts
        prompts = [
            "What is the capital of France?",
            "Explain quantum computing in simple terms.",
            "Write a Python function to reverse a string."
        ]
        
        # Run test scenario
        results = await client.run_scenario(
            prompts=prompts,
            model="glm-4.6",
            concurrency=2,
            temperature=0.7
        )
        
        # Analyze results
        analysis = client.analyze_results(results)
        print(json.dumps(analysis, indent=2))
        
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

