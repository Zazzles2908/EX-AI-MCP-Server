#!/usr/bin/env python3
"""
Test Coordinator - Runs smoke test then full 1.5-hour intensive test
====================================================================

Coordinates load testing and log monitoring in parallel.
EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab

Execution Plan:
1. Run 5-minute smoke test to validate setup
2. If smoke test passes, run full 1.5-hour test with parallel monitoring
3. Generate comprehensive report at the end
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "test_coordinator.log")
    ]
)
logger = logging.getLogger(__name__)


class TestCoordinator:
    """Coordinates smoke test and full intensive test"""
    
    def __init__(self):
        self.monitor_task = None
        self.load_test_task = None
        self.shutdown_event = asyncio.Event()
        
    async def run_smoke_test(self) -> bool:
        """Run 5-minute smoke test to validate setup"""
        logger.info("=" * 80)
        logger.info("SMOKE TEST - 5 Minutes")
        logger.info("=" * 80)
        logger.info("Validating WebSocket connectivity and basic functionality...")
        
        try:
            # Import here to avoid circular dependencies
            from scripts.monitoring.intensive_load_test import LoadTestOrchestrator
            
            orchestrator = LoadTestOrchestrator()
            
            # Run a mini version of Phase 1 (5 minutes instead of 15)
            logger.info("Running baseline test with 5 clients for 5 minutes...")
            
            from scripts.monitoring.intensive_load_test import TestMetrics
            metrics = TestMetrics(
                phase="Smoke Test",
                start_time=datetime.now()
            )
            
            await orchestrator._run_sustained_load(
                num_clients=5,
                duration_seconds=300,  # 5 minutes
                message_rate_per_client=1.0,
                metrics=metrics
            )
            
            metrics.end_time = datetime.now()
            
            # Validate results
            success_rate = metrics.connections_successful / metrics.connections_attempted if metrics.connections_attempted > 0 else 0
            message_success_rate = metrics.messages_received / metrics.messages_sent if metrics.messages_sent > 0 else 0
            
            logger.info("=" * 80)
            logger.info("SMOKE TEST RESULTS")
            logger.info("=" * 80)
            logger.info(f"Connections: {metrics.connections_successful}/{metrics.connections_attempted} ({success_rate:.1%})")
            logger.info(f"Messages: {metrics.messages_received}/{metrics.messages_sent} ({message_success_rate:.1%})")
            logger.info(f"Latency P95: {metrics.latency_p95:.2f}ms")
            logger.info(f"Errors: {len(metrics.errors)}")
            logger.info("=" * 80)
            
            # Pass criteria
            if success_rate < 0.95:
                logger.error(f"❌ SMOKE TEST FAILED: Connection success rate {success_rate:.1%} < 95%")
                return False
            
            if message_success_rate < 0.95:
                logger.error(f"❌ SMOKE TEST FAILED: Message success rate {message_success_rate:.1%} < 95%")
                return False
            
            if metrics.latency_p95 > 1000:  # 1 second
                logger.error(f"❌ SMOKE TEST FAILED: P95 latency {metrics.latency_p95:.2f}ms > 1000ms")
                return False
            
            logger.info("✅ SMOKE TEST PASSED - Proceeding to full test")
            return True
            
        except Exception as e:
            logger.error(f"❌ SMOKE TEST FAILED: {e}", exc_info=True)
            return False
    
    async def run_full_test(self):
        """Run full 1.5-hour test with parallel monitoring"""
        logger.info("=" * 80)
        logger.info("FULL INTENSIVE TEST - 1.5 Hours")
        logger.info("=" * 80)
        logger.info("Starting load test and log monitor in parallel...")
        
        try:
            # Import test modules
            from scripts.monitoring.intensive_load_test import LoadTestOrchestrator
            from scripts.monitoring.realtime_log_monitor import LogMonitor
            
            # Create instances
            load_orchestrator = LoadTestOrchestrator()
            log_monitor = LogMonitor()
            
            # Run both in parallel
            self.load_test_task = asyncio.create_task(load_orchestrator.run_full_test())
            self.monitor_task = asyncio.create_task(log_monitor.monitor_logs(duration_seconds=5400))
            
            # Wait for both to complete
            await asyncio.gather(self.load_test_task, self.monitor_task)
            
            logger.info("=" * 80)
            logger.info("✅ FULL TEST COMPLETE")
            logger.info("=" * 80)
            
            # Save final monitoring report
            output_file = project_root / "logs" / "monitoring_report.json"
            log_monitor.save_final_report(output_file)
            
        except Exception as e:
            logger.error(f"❌ FULL TEST FAILED: {e}", exc_info=True)
            raise
    
    async def run(self):
        """Main execution flow"""
        try:
            # Step 1: Smoke test
            logger.info("Step 1: Running smoke test...")
            smoke_test_passed = await self.run_smoke_test()
            
            if not smoke_test_passed:
                logger.error("Smoke test failed. Aborting full test.")
                return False
            
            # Wait a bit before starting full test
            logger.info("Waiting 30 seconds before starting full test...")
            await asyncio.sleep(30)
            
            # Step 2: Full test
            logger.info("Step 2: Running full intensive test...")
            await self.run_full_test()
            
            logger.info("=" * 80)
            logger.info("✅ ALL TESTS COMPLETE")
            logger.info("=" * 80)
            logger.info("Results saved to logs/ directory")
            logger.info("  - load_test_results.json")
            logger.info("  - monitoring_report.json")
            logger.info("  - load_test_docker.log")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}", exc_info=True)
            return False
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.warning(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown_event.set()
        
        # Cancel running tasks
        if self.load_test_task and not self.load_test_task.done():
            self.load_test_task.cancel()
        
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()


async def main():
    """Main entry point"""
    coordinator = TestCoordinator()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, coordinator.handle_shutdown)
    signal.signal(signal.SIGTERM, coordinator.handle_shutdown)
    
    # Run tests
    success = await coordinator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

