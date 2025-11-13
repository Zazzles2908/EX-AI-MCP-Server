#!/usr/bin/env python3
"""
Progressive Rate Testing for WebSocket Stability
Tests WebSocket connection with progressively increasing event rates to identify breaking point

Based on EXAI recommendations:
- Start with low rates (5 events/min)
- Gradually increase to target rate (30 events/min)
- Monitor for freezing, latency, and connection health
- Stop at first sign of instability
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_event_generator import TestEventGenerator

# Configure logging
log_dir = os.environ.get('LOG_DIR', '/app/logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/progressive_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ProgressiveRateTester:
    """Test WebSocket with progressively increasing event rates"""
    
    def __init__(self, ws_url: str = "ws://host.docker.internal:8079/ws"):
        self.ws_url = ws_url
        self.results = []
    
    async def run_single_test(self, rate: int, duration: int) -> bool:
        """Run a single test at specified rate and duration"""
        logger.info(f"\n{'='*70}")
        logger.info(f"🧪 TEST: {rate} events/min for {duration} minutes ({rate * duration} events)")
        logger.info(f"{'='*70}")
        
        generator = TestEventGenerator(ws_url=self.ws_url)
        
        try:
            await generator.run_baseline_test(
                duration_minutes=duration,
                events_per_minute=rate
            )
            
            # Test succeeded
            result = {
                'rate': rate,
                'duration': duration,
                'total_events': rate * duration,
                'events_sent': generator.event_count,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            logger.info(f"✅ TEST PASSED: {rate} events/min")
            logger.info(f"   Events sent: {generator.event_count}/{rate * duration}")
            
            return True
            
        except Exception as e:
            # Test failed
            result = {
                'rate': rate,
                'duration': duration,
                'total_events': rate * duration,
                'events_sent': generator.event_count,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            logger.error(f"❌ TEST FAILED: {rate} events/min")
            logger.error(f"   Events sent: {generator.event_count}/{rate * duration}")
            logger.error(f"   Error: {e}")
            
            return False
    
    async def run_progressive_tests(self):
        """Run progressive rate tests"""
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 PROGRESSIVE RATE TESTING")
        logger.info(f"WebSocket URL: {self.ws_url}")
        logger.info(f"Strategy: Start low, increase gradually, stop at failure")
        logger.info(f"{'='*70}\n")
        
        # Test configuration: (rate, duration)
        # OPTIMIZED: Shorter durations for faster iteration (EXAI recommendation)
        # Total time: ~1.5 hours if all tests pass
        test_configs = [
            (5, 5),     # 5 events/min for 5 min (25 events) - Very conservative
            (10, 5),    # 10 events/min for 5 min (50 events) - Conservative
            (15, 5),    # 15 events/min for 5 min (75 events) - Moderate
            (20, 5),    # 20 events/min for 5 min (100 events) - Phase 1 rate
            (25, 5),    # 25 events/min for 5 min (125 events) - Between Phase 1 and 2
            (30, 5),    # 30 events/min for 5 min (150 events) - Phase 2 rate (short)
            (30, 15),   # 30 events/min for 15 min (450 events) - Phase 2 rate (medium)
            (30, 30),   # 30 events/min for 30 min (900 events) - Phase 2 rate (extended)
        ]
        
        logger.info("📋 Test Plan:")
        for i, (rate, duration) in enumerate(test_configs, 1):
            logger.info(f"   {i}. {rate} events/min × {duration} min = {rate * duration} events")
        logger.info("")
        
        # Run tests sequentially
        for i, (rate, duration) in enumerate(test_configs, 1):
            logger.info(f"\n{'='*70}")
            logger.info(f"📊 PROGRESS: Test {i}/{len(test_configs)}")
            logger.info(f"{'='*70}")
            
            success = await self.run_single_test(rate, duration)
            
            if not success:
                logger.warning(f"\n⚠️  STOPPING: Test failed at {rate} events/min")
                logger.warning(f"   Maximum stable rate: {test_configs[i-2][0] if i > 1 else 0} events/min")
                break
            
            # Wait between tests
            if i < len(test_configs):
                logger.info(f"\n⏸️  Waiting 30 seconds before next test...")
                await asyncio.sleep(30)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 TEST SUMMARY")
        logger.info(f"{'='*70}")
        
        passed = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        logger.info(f"Total tests: {len(self.results)}")
        logger.info(f"Passed: {len(passed)}")
        logger.info(f"Failed: {len(failed)}")
        logger.info("")
        
        if passed:
            logger.info("✅ PASSED TESTS:")
            for r in passed:
                logger.info(f"   {r['rate']} events/min × {r['duration']} min = {r['events_sent']} events")
        
        if failed:
            logger.info("\n❌ FAILED TESTS:")
            for r in failed:
                logger.info(f"   {r['rate']} events/min × {r['duration']} min")
                logger.info(f"      Events sent: {r['events_sent']}/{r['total_events']}")
                logger.info(f"      Error: {r['error']}")
        
        if passed:
            max_stable = max(r['rate'] for r in passed)
            logger.info(f"\n🎯 MAXIMUM STABLE RATE: {max_stable} events/min")
        
        logger.info(f"\n{'='*70}")


async def main():
    """Main entry point"""
    logger.info("Progressive Rate Tester starting...")
    
    # Get WebSocket URL from environment or use default
    ws_url = os.environ.get('WS_URL', 'ws://host.docker.internal:8079/ws')
    
    tester = ProgressiveRateTester(ws_url=ws_url)
    
    try:
        await tester.run_progressive_tests()
        logger.info("\n✅ Progressive testing completed")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Testing interrupted by user")
        tester.print_summary()
        
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        tester.print_summary()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)

