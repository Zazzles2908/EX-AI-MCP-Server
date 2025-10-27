#!/usr/bin/env python3
"""
Test Event Generator for AI Auditor Testing
Generates realistic system events to test AI Auditor functionality
"""

import asyncio
import websockets
import json
import random
import time
from datetime import datetime
from typing import Dict, List
import argparse
import sys
import logging

# Configure logging with immediate flushing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Force line buffering for immediate output
for handler in logger.handlers:
    if hasattr(handler.stream, 'reconfigure'):
        handler.stream.reconfigure(line_buffering=True)


class TestEventGenerator:
    """Generates realistic test events for AI Auditor validation"""

    def __init__(self, ws_url: str = "ws://localhost:8080/events"):
        self.ws_url = ws_url
        self.event_count = 0
        self.start_time = time.time()
        
    def generate_health_check_event(self) -> Dict:
        """Generate routine health check event"""
        return {
            "type": "health_check",
            "severity": "info",
            "timestamp": datetime.now().isoformat(),
            "service": random.choice(["mcp-server", "redis", "websocket"]),
            "status": "healthy",
            "response_time_ms": random.randint(10, 100)
        }
    
    def generate_api_request_event(self) -> Dict:
        """Generate API request event"""
        response_time = random.randint(50, 2000)
        severity = "warning" if response_time > 1000 else "info"
        
        return {
            "type": "api_request",
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "endpoint": random.choice([
                "/api/chat/completions",
                "/api/tools/list",
                "/api/health",
                "/api/metrics"
            ]),
            "method": "POST",
            "status_code": random.choice([200, 200, 200, 201, 400, 500]),
            "response_time_ms": response_time,
            "model": random.choice(["glm-4.6", "glm-4.5-flash", "kimi-k2-0905-preview"])
        }
    
    def generate_error_event(self) -> Dict:
        """Generate error event"""
        error_types = [
            ("connection_timeout", "Database connection timeout after 30s"),
            ("rate_limit_exceeded", "API rate limit exceeded: 60 calls/hour"),
            ("invalid_request", "Invalid request: missing required parameter 'model'"),
            ("authentication_failed", "Authentication failed: invalid API key"),
            ("service_unavailable", "Service temporarily unavailable")
        ]
        
        error_type, message = random.choice(error_types)
        
        return {
            "type": "error",
            "severity": "error",
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message,
            "service": random.choice(["glm", "kimi", "supabase", "redis"]),
            "stack_trace": f"Error at line {random.randint(1, 500)}"
        }
    
    def generate_critical_event(self) -> Dict:
        """Generate critical event"""
        return {
            "type": "critical_failure",
            "severity": "critical",
            "timestamp": datetime.now().isoformat(),
            "message": "Service crash detected",
            "service": random.choice(["mcp-server", "websocket-server"]),
            "impact": "Service restart required",
            "recovery_action": "Automatic restart initiated"
        }
    
    def generate_performance_anomaly(self) -> Dict:
        """Generate performance anomaly event"""
        return {
            "type": "performance_anomaly",
            "severity": "warning",
            "timestamp": datetime.now().isoformat(),
            "metric": random.choice(["cpu_usage", "memory_usage", "response_time"]),
            "value": random.randint(80, 99),
            "threshold": 80,
            "service": random.choice(["mcp-server", "redis", "websocket"])
        }
    
    def generate_event(self, event_type: str = None) -> Dict:
        """Generate a random event or specific type"""
        if event_type:
            generators = {
                "health_check": self.generate_health_check_event,
                "api_request": self.generate_api_request_event,
                "error": self.generate_error_event,
                "critical": self.generate_critical_event,
                "performance": self.generate_performance_anomaly
            }
            return generators[event_type]()
        
        # Random event distribution (realistic mix)
        event_types = [
            ("health_check", 50),  # 50% health checks
            ("api_request", 30),   # 30% API requests
            ("error", 15),         # 15% errors
            ("performance", 4),    # 4% performance anomalies
            ("critical", 1)        # 1% critical events
        ]
        
        rand = random.randint(1, 100)
        cumulative = 0
        for event_type, weight in event_types:
            cumulative += weight
            if rand <= cumulative:
                return self.generate_event(event_type)
        
        return self.generate_health_check_event()
    
    async def send_event(self, websocket, event: Dict):
        """Send event to WebSocket server"""
        try:
            await asyncio.wait_for(websocket.send(json.dumps(event)), timeout=5.0)
            self.event_count += 1
            logger.info(f"[{self.event_count}] Sent {event['type']} event (severity: {event['severity']})")
        except asyncio.TimeoutError:
            logger.error(f"Send operation timed out after 5 seconds")
            raise
        except Exception as e:
            logger.error(f"Error sending event: {e}")
            raise
    
    async def run_baseline_test(self, duration_minutes: int = 30, events_per_minute: int = 10):
        """Run baseline test - generate events for specified duration"""
        logger.info(f"\n{'='*60}")
        logger.info(f"BASELINE TEST - AI Auditor DISABLED")
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info(f"Events per minute: {events_per_minute}")
        logger.info(f"{'='*60}\n")

        try:
            logger.info(f"Connecting to {self.ws_url}...")
            async with websockets.connect(
                self.ws_url,
                ping_interval=30,      # Send ping every 30 seconds
                ping_timeout=60,       # Wait 60 seconds for pong
                close_timeout=3600,    # 1 hour close timeout
                max_queue=512,         # Increase frame queue from default 16 to 512
                write_limit=65536      # Increase write buffer from default 32KB to 64KB
            ) as websocket:
                logger.info(f"✅ Connected to {self.ws_url}")

                end_time = time.time() + (duration_minutes * 60)
                interval = 60 / events_per_minute  # seconds between events

                logger.info(f"Starting event generation (interval: {interval:.2f}s)")

                while time.time() < end_time:
                    event = self.generate_event()
                    await self.send_event(websocket, event)
                    await asyncio.sleep(interval)

                elapsed = time.time() - self.start_time
                logger.info(f"\n{'='*60}")
                logger.info(f"✅ BASELINE TEST COMPLETE")
                logger.info(f"Total events sent: {self.event_count}")
                logger.info(f"Duration: {elapsed/60:.2f} minutes")
                logger.info(f"Events per minute: {self.event_count/(elapsed/60):.2f}")
                logger.info(f"{'='*60}\n")

        except Exception as e:
            logger.error(f"❌ Error during baseline test: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def run_stress_test(self, duration_minutes: int = 5, events_per_second: int = 5):
        """Run stress test - high volume of events"""
        print(f"\n{'='*60}")
        print(f"STRESS TEST - High Volume Events")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Events per second: {events_per_second}")
        print(f"{'='*60}\n")
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                print(f"✅ Connected to {self.ws_url}")
                
                end_time = time.time() + (duration_minutes * 60)
                interval = 1 / events_per_second
                
                while time.time() < end_time:
                    event = self.generate_event()
                    await self.send_event(websocket, event)
                    await asyncio.sleep(interval)
                
                elapsed = time.time() - self.start_time
                print(f"\n{'='*60}")
                print(f"✅ STRESS TEST COMPLETE")
                print(f"Total events sent: {self.event_count}")
                print(f"Duration: {elapsed/60:.2f} minutes")
                print(f"Events per second: {self.event_count/elapsed:.2f}")
                print(f"{'='*60}\n")
                
        except Exception as e:
            print(f"❌ Error during stress test: {e}")


async def main():
    logger.info("Test Event Generator starting...")

    parser = argparse.ArgumentParser(description="Test Event Generator for AI Auditor")
    parser.add_argument("--mode", choices=["baseline", "stress"], default="baseline",
                       help="Test mode (baseline or stress)")
    parser.add_argument("--duration", type=int, default=30,
                       help="Test duration in minutes (default: 30)")
    parser.add_argument("--rate", type=int, default=10,
                       help="Events per minute for baseline or per second for stress (default: 10)")
    parser.add_argument("--ws-url", default="ws://localhost:8080/events",
                       help="WebSocket URL (default: ws://localhost:8080/events)")

    args = parser.parse_args()

    logger.info(f"Configuration: mode={args.mode}, duration={args.duration}min, rate={args.rate}")

    generator = TestEventGenerator(ws_url=args.ws_url)

    try:
        if args.mode == "baseline":
            await generator.run_baseline_test(duration_minutes=args.duration, events_per_minute=args.rate)
        else:
            await generator.run_stress_test(duration_minutes=args.duration, events_per_second=args.rate)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Script execution starting...")
    try:
        asyncio.run(main())
        logger.info("Script execution completed successfully")
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

