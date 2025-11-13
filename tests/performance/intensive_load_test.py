#!/usr/bin/env python3
"""
Intensive Load Testing Script for Phase 4 Validation
=====================================================

Tests resilient_websocket.py migration with tiered sampling strategy.
Runs 1.5-hour intensive test with 3.5x load multiplier to simulate 48-hour production period.

EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab

Test Phases:
- Phase 1 (15 min): Baseline validation at 1x load
- Phase 2 (45 min): Sustained elevated load at 3.5x
- Phase 3 (15 min): Burst testing with 10x traffic spikes
- Phase 4 (15 min): Failure injection testing

Expected Outcome: 85-90% log volume reduction while maintaining 100% critical event detection
"""

import asyncio
import json
import logging
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import websockets
from websockets.exceptions import ConnectionClosed

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestMetrics:
    """Metrics collected during testing"""
    phase: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Connection metrics
    connections_attempted: int = 0
    connections_successful: int = 0
    connections_failed: int = 0
    
    # Message metrics
    messages_sent: int = 0
    messages_received: int = 0
    messages_failed: int = 0
    
    # Latency metrics (milliseconds)
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    latency_max: float = 0.0
    
    # Log volume metrics
    log_lines_total: int = 0
    log_lines_by_level: Dict[str, int] = None
    
    # Error tracking
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.log_lines_by_level is None:
            self.log_lines_by_level = defaultdict(int)
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class LoadTestClient:
    """WebSocket client for load testing"""

    def __init__(self, client_id: int, ws_url: str, auth_token: str = "test-token-12345"):
        self.client_id = client_id
        self.ws_url = ws_url
        self.auth_token = auth_token
        self.session_id = f"load-test-{client_id}"
        self.ws = None
        self.latencies = []
        self.messages_sent = 0
        self.messages_received = 0
        self.errors = []
        self.authenticated = False

    async def connect(self) -> bool:
        """Establish WebSocket connection and authenticate"""
        try:
            # Connect to WebSocket
            self.ws = await websockets.connect(
                self.ws_url,
                max_size=100 * 1024 * 1024,  # 100MB
                ping_interval=30.0,
                ping_timeout=180.0
            )

            # Send hello message for authentication
            hello_msg = {
                "op": "hello",
                "session_id": self.session_id,
                "token": self.auth_token
            }
            await self.ws.send(json.dumps(hello_msg))

            # Wait for hello_ack
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            response_data = json.loads(response)

            if response_data.get("op") not in ["hello_res", "hello_ack"]:
                self.errors.append(f"Authentication failed: {response_data}")
                logger.error(f"Client {self.client_id} auth failed: {response_data}")
                return False

            if not response_data.get("ok", True):
                self.errors.append(f"Authentication rejected: {response_data.get('error')}")
                logger.error(f"Client {self.client_id} auth rejected: {response_data}")
                return False

            self.authenticated = True
            logger.debug(f"Client {self.client_id} connected and authenticated")
            return True

        except Exception as e:
            self.errors.append(f"Connection failed: {e}")
            logger.error(f"Client {self.client_id} connection failed: {e}")
            return False
    
    async def send_message(self, message: dict) -> Optional[float]:
        """Send message and measure latency"""
        if not self.ws or not self.authenticated:
            return None

        try:
            start_time = time.time()

            # Create MCP-compatible message using test_echo tool
            # This avoids AI API costs while generating realistic WebSocket traffic
            mcp_message = {
                "op": "call_tool",
                "request_id": f"load-test-{self.client_id}-{int(time.time() * 1000)}",
                "name": "test_echo",
                "arguments": {
                    "prompt": message.get("data", "test message"),
                    "delay_ms": 0,  # No delay for maximum throughput
                    "include_metadata": True
                }
            }

            await self.ws.send(json.dumps(mcp_message))
            self.messages_sent += 1

            # Wait for response
            response = await asyncio.wait_for(self.ws.recv(), timeout=30.0)  # Longer timeout for AI processing
            latency = (time.time() - start_time) * 1000  # Convert to ms

            self.latencies.append(latency)
            self.messages_received += 1

            return latency

        except asyncio.TimeoutError:
            self.errors.append("Message timeout")
            return None
        except ConnectionClosed:
            self.errors.append("Connection closed")
            return None
        except Exception as e:
            self.errors.append(f"Send error: {e}")
            logger.error(f"Client {self.client_id} send error: {e}")
            return None
    
    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"Client {self.client_id} close error: {e}")


class LoadTestOrchestrator:
    """Orchestrates multi-phase load testing"""
    
    def __init__(self, ws_url: str = "ws://localhost:8079"):
        self.ws_url = ws_url
        self.metrics_by_phase = {}
        self.docker_log_file = project_root / "logs" / "load_test_docker.log"
        self.results_file = project_root / "logs" / "load_test_results.json"
        
    async def run_phase_1_baseline(self) -> TestMetrics:
        """Phase 1: Baseline validation at 1x load (15 minutes)"""
        logger.info("=" * 80)
        logger.info("PHASE 1: Baseline Validation (1x load, 15 minutes)")
        logger.info("=" * 80)
        
        metrics = TestMetrics(
            phase="Phase 1: Baseline",
            start_time=datetime.now()
        )
        
        # Run baseline test with 10 concurrent connections
        num_clients = 10
        duration_seconds = 15 * 60  # 15 minutes
        
        await self._run_sustained_load(
            num_clients=num_clients,
            duration_seconds=duration_seconds,
            message_rate_per_client=1.0,  # 1 message per second per client
            metrics=metrics
        )
        
        metrics.end_time = datetime.now()
        self.metrics_by_phase["phase_1"] = metrics
        
        logger.info(f"Phase 1 Complete: {metrics.messages_sent} messages sent, "
                   f"{metrics.connections_successful}/{metrics.connections_attempted} connections")
        
        return metrics
    
    async def run_phase_2_sustained(self) -> TestMetrics:
        """Phase 2: Sustained elevated load at 3.5x (45 minutes)"""
        logger.info("=" * 80)
        logger.info("PHASE 2: Sustained Elevated Load (3.5x load, 45 minutes)")
        logger.info("=" * 80)
        
        metrics = TestMetrics(
            phase="Phase 2: Sustained 3.5x",
            start_time=datetime.now()
        )
        
        # Run sustained test with 35 concurrent connections (3.5x multiplier)
        num_clients = 35
        duration_seconds = 45 * 60  # 45 minutes
        
        await self._run_sustained_load(
            num_clients=num_clients,
            duration_seconds=duration_seconds,
            message_rate_per_client=1.0,
            metrics=metrics
        )
        
        metrics.end_time = datetime.now()
        self.metrics_by_phase["phase_2"] = metrics
        
        logger.info(f"Phase 2 Complete: {metrics.messages_sent} messages sent, "
                   f"{metrics.connections_successful}/{metrics.connections_attempted} connections")
        
        return metrics
    
    async def run_phase_3_burst(self) -> TestMetrics:
        """Phase 3: Burst testing with 10x traffic spikes (15 minutes)"""
        logger.info("=" * 80)
        logger.info("PHASE 3: Burst Testing (10x spikes, 15 minutes)")
        logger.info("=" * 80)
        
        metrics = TestMetrics(
            phase="Phase 3: Burst 10x",
            start_time=datetime.now()
        )
        
        # Run burst test: 2 minutes normal, 3 minutes 10x burst, repeat
        duration_seconds = 15 * 60  # 15 minutes
        burst_cycle_seconds = 5 * 60  # 5-minute cycles
        
        await self._run_burst_load(
            normal_clients=10,
            burst_clients=100,
            duration_seconds=duration_seconds,
            burst_cycle_seconds=burst_cycle_seconds,
            metrics=metrics
        )
        
        metrics.end_time = datetime.now()
        self.metrics_by_phase["phase_3"] = metrics
        
        logger.info(f"Phase 3 Complete: {metrics.messages_sent} messages sent, "
                   f"{metrics.connections_successful}/{metrics.connections_attempted} connections")
        
        return metrics
    
    async def run_phase_4_failure_injection(self) -> TestMetrics:
        """Phase 4: Failure injection testing (15 minutes)"""
        logger.info("=" * 80)
        logger.info("PHASE 4: Failure Injection Testing (15 minutes)")
        logger.info("=" * 80)
        
        metrics = TestMetrics(
            phase="Phase 4: Failure Injection",
            start_time=datetime.now()
        )
        
        # Run failure injection test
        duration_seconds = 15 * 60  # 15 minutes
        
        await self._run_failure_injection(
            num_clients=20,
            duration_seconds=duration_seconds,
            metrics=metrics
        )
        
        metrics.end_time = datetime.now()
        self.metrics_by_phase["phase_4"] = metrics
        
        logger.info(f"Phase 4 Complete: {metrics.messages_sent} messages sent, "
                   f"{metrics.connections_successful}/{metrics.connections_attempted} connections")
        
        return metrics
    
    async def _run_sustained_load(self, num_clients: int, duration_seconds: int, 
                                  message_rate_per_client: float, metrics: TestMetrics):
        """Run sustained load test"""
        clients = []
        
        # Create and connect clients
        for i in range(num_clients):
            client = LoadTestClient(i, self.ws_url)
            metrics.connections_attempted += 1
            
            if await client.connect():
                metrics.connections_successful += 1
                clients.append(client)
            else:
                metrics.connections_failed += 1
        
        logger.info(f"Connected {len(clients)}/{num_clients} clients")
        
        # Send messages at specified rate
        end_time = time.time() + duration_seconds
        message_interval = 1.0 / message_rate_per_client
        
        while time.time() < end_time:
            # Send one message from each client
            tasks = []
            for client in clients:
                message = {
                    "type": "test_message",
                    "client_id": client.client_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": "x" * 100  # 100-byte payload
                }
                tasks.append(client.send_message(message))
            
            # Wait for all messages to complete
            latencies = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update metrics
            for latency in latencies:
                if isinstance(latency, float):
                    metrics.messages_sent += 1
                    metrics.messages_received += 1
                elif isinstance(latency, Exception):
                    metrics.messages_failed += 1
            
            # Wait for next interval
            await asyncio.sleep(message_interval)
        
        # Close all clients
        for client in clients:
            await client.close()
        
        # Calculate latency percentiles
        all_latencies = []
        for client in clients:
            all_latencies.extend(client.latencies)
        
        if all_latencies:
            all_latencies.sort()
            metrics.latency_p50 = all_latencies[int(len(all_latencies) * 0.50)]
            metrics.latency_p95 = all_latencies[int(len(all_latencies) * 0.95)]
            metrics.latency_p99 = all_latencies[int(len(all_latencies) * 0.99)]
            metrics.latency_max = all_latencies[-1]

    async def _run_burst_load(self, normal_clients: int, burst_clients: int,
                             duration_seconds: int, burst_cycle_seconds: int, metrics: TestMetrics):
        """Run burst load test with periodic traffic spikes"""
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            # Normal load period (2 minutes)
            logger.info(f"Burst test: Normal load ({normal_clients} clients)")
            await self._run_sustained_load(
                num_clients=normal_clients,
                duration_seconds=min(120, int(end_time - time.time())),
                message_rate_per_client=1.0,
                metrics=metrics
            )

            if time.time() >= end_time:
                break

            # Burst load period (3 minutes)
            logger.info(f"Burst test: BURST LOAD ({burst_clients} clients)")
            await self._run_sustained_load(
                num_clients=burst_clients,
                duration_seconds=min(180, int(end_time - time.time())),
                message_rate_per_client=2.0,  # 2x message rate during burst
                metrics=metrics
            )

    async def _run_failure_injection(self, num_clients: int, duration_seconds: int, metrics: TestMetrics):
        """Run failure injection test"""
        clients = []

        # Create and connect clients
        for i in range(num_clients):
            client = LoadTestClient(i, self.ws_url)
            metrics.connections_attempted += 1

            if await client.connect():
                metrics.connections_successful += 1
                clients.append(client)
            else:
                metrics.connections_failed += 1

        logger.info(f"Failure injection: Connected {len(clients)}/{num_clients} clients")

        # Run test with periodic connection drops
        end_time = time.time() + duration_seconds
        drop_interval = 60  # Drop connections every 60 seconds
        last_drop = time.time()

        while time.time() < end_time:
            # Send messages
            tasks = []
            for client in clients:
                message = {
                    "type": "test_message",
                    "client_id": client.client_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": "x" * 100
                }
                tasks.append(client.send_message(message))

            latencies = await asyncio.gather(*tasks, return_exceptions=True)

            for latency in latencies:
                if isinstance(latency, float):
                    metrics.messages_sent += 1
                    metrics.messages_received += 1
                elif isinstance(latency, Exception):
                    metrics.messages_failed += 1

            # Periodic connection drops
            if time.time() - last_drop >= drop_interval:
                logger.info("Failure injection: Dropping 50% of connections")

                # Close half the clients
                for i in range(len(clients) // 2):
                    await clients[i].close()

                # Reconnect them
                for i in range(len(clients) // 2):
                    metrics.connections_attempted += 1
                    if await clients[i].connect():
                        metrics.connections_successful += 1
                    else:
                        metrics.connections_failed += 1

                last_drop = time.time()

            await asyncio.sleep(1.0)

        # Close all clients
        for client in clients:
            await client.close()

    async def collect_docker_logs(self):
        """Collect Docker logs for analysis"""
        logger.info("Collecting Docker logs...")

        try:
            # Run docker logs command
            process = await asyncio.create_subprocess_exec(
                "docker", "logs", "exai-mcp-daemon", "--tail", "10000",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # Save logs to file
            self.docker_log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.docker_log_file, 'wb') as f:
                f.write(stdout)
                f.write(stderr)

            logger.info(f"Docker logs saved to {self.docker_log_file}")

            # Analyze log volume
            log_lines = stdout.decode('utf-8', errors='ignore').split('\n')
            log_lines.extend(stderr.decode('utf-8', errors='ignore').split('\n'))

            log_counts = defaultdict(int)
            for line in log_lines:
                if 'ERROR' in line:
                    log_counts['ERROR'] += 1
                elif 'WARNING' in line:
                    log_counts['WARNING'] += 1
                elif 'INFO' in line:
                    log_counts['INFO'] += 1
                elif 'DEBUG' in line:
                    log_counts['DEBUG'] += 1

            return {
                'total_lines': len(log_lines),
                'by_level': dict(log_counts)
            }

        except Exception as e:
            logger.error(f"Failed to collect Docker logs: {e}")
            return None

    def save_results(self):
        """Save test results to JSON file"""
        results = {
            'test_date': datetime.now().isoformat(),
            'total_duration_minutes': 90,
            'phases': {}
        }

        for phase_name, metrics in self.metrics_by_phase.items():
            results['phases'][phase_name] = {
                'phase': metrics.phase,
                'start_time': metrics.start_time.isoformat(),
                'end_time': metrics.end_time.isoformat() if metrics.end_time else None,
                'duration_seconds': (metrics.end_time - metrics.start_time).total_seconds() if metrics.end_time else 0,
                'connections': {
                    'attempted': metrics.connections_attempted,
                    'successful': metrics.connections_successful,
                    'failed': metrics.connections_failed,
                    'success_rate': metrics.connections_successful / metrics.connections_attempted if metrics.connections_attempted > 0 else 0
                },
                'messages': {
                    'sent': metrics.messages_sent,
                    'received': metrics.messages_received,
                    'failed': metrics.messages_failed,
                    'success_rate': metrics.messages_received / metrics.messages_sent if metrics.messages_sent > 0 else 0
                },
                'latency_ms': {
                    'p50': metrics.latency_p50,
                    'p95': metrics.latency_p95,
                    'p99': metrics.latency_p99,
                    'max': metrics.latency_max
                },
                'errors': metrics.errors,
                'warnings': metrics.warnings
            }

        # Save to file
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Test results saved to {self.results_file}")

    async def run_full_test(self):
        """Run complete 1.5-hour test suite"""
        logger.info("=" * 80)
        logger.info("STARTING 1.5-HOUR INTENSIVE LOAD TEST")
        logger.info("=" * 80)
        logger.info(f"Test start time: {datetime.now().isoformat()}")
        logger.info(f"Expected end time: {(datetime.now() + timedelta(minutes=90)).isoformat()}")
        logger.info("=" * 80)

        try:
            # Phase 1: Baseline (15 minutes)
            await self.run_phase_1_baseline()

            # Phase 2: Sustained (45 minutes)
            await self.run_phase_2_sustained()

            # Phase 3: Burst (15 minutes)
            await self.run_phase_3_burst()

            # Phase 4: Failure Injection (15 minutes)
            await self.run_phase_4_failure_injection()

            # Collect Docker logs
            log_analysis = await self.collect_docker_logs()

            # Save results
            self.save_results()

            # Print summary
            logger.info("=" * 80)
            logger.info("TEST COMPLETE - SUMMARY")
            logger.info("=" * 80)

            total_messages = sum(m.messages_sent for m in self.metrics_by_phase.values())
            total_connections = sum(m.connections_attempted for m in self.metrics_by_phase.values())

            logger.info(f"Total messages sent: {total_messages}")
            logger.info(f"Total connections attempted: {total_connections}")

            if log_analysis:
                logger.info(f"Total log lines: {log_analysis['total_lines']}")
                logger.info(f"Log breakdown: {log_analysis['by_level']}")

            logger.info(f"Results saved to: {self.results_file}")
            logger.info(f"Docker logs saved to: {self.docker_log_file}")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Test failed: {e}", exc_info=True)
            raise


async def main():
    """Main entry point"""
    orchestrator = LoadTestOrchestrator()
    await orchestrator.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())

