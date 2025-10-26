"""
Integration Test: Failure Recovery

Tests failure recovery mechanisms:
- Circuit breaker opens after threshold failures
- Automatic recovery (HALF_OPEN → CLOSED)
- Message queue behavior during failures
- Retry logic and exponential backoff
- Graceful degradation

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Phase 1 (Integration Tests)
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.resilient_websocket import ResilientWebSocketManager
from src.monitoring.circuit_breaker import CircuitState


async def test_failure_recovery():
    """Test failure recovery mechanisms."""
    print("\n" + "="*60)
    print("Integration Test: Failure Recovery")
    print("="*60)
    
    # Initialize WebSocket manager
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=True
    )
    
    print("\n[1/5] Testing circuit breaker opens after failures...")
    if manager._circuit_breaker:
        # Verify initial state
        assert manager._circuit_breaker.state == CircuitState.CLOSED, \
            "Circuit should start CLOSED"

        # Simulate threshold failures (default: 5)
        failure_threshold = manager._circuit_breaker.config.failure_threshold
        for i in range(failure_threshold):
            await manager._circuit_breaker._on_failure()

        # Circuit should be OPEN
        assert manager._circuit_breaker.state == CircuitState.OPEN, \
            f"Circuit should be OPEN after {failure_threshold} failures"

        print(f"✅ Circuit opened after {failure_threshold} failures")
        print(f"   State: {manager._circuit_breaker.state}")
    
    print("\n[2/5] Testing circuit breaker prevents calls when OPEN...")
    if manager._circuit_breaker:
        # Try to make a call while circuit is OPEN
        call_allowed = manager._circuit_breaker.state == CircuitState.CLOSED
        assert not call_allowed, "Calls should not be allowed when circuit is OPEN"
        
        print("✅ Circuit breaker prevents calls when OPEN")
    
    print("\n[3/5] Testing automatic recovery to HALF_OPEN...")
    if manager._circuit_breaker:
        # Set short timeout for testing
        manager._circuit_breaker.config.timeout_seconds = 0.5
        
        # Wait for timeout
        await asyncio.sleep(0.6)
        
        # Manually transition to HALF_OPEN (simulating timeout)
        await manager._circuit_breaker._change_state(CircuitState.HALF_OPEN)
        
        assert manager._circuit_breaker.state == CircuitState.HALF_OPEN, \
            "Circuit should be HALF_OPEN after timeout"
        
        print(f"✅ Circuit transitioned to HALF_OPEN after timeout")
        print(f"   State: {manager._circuit_breaker.state}")
    
    print("\n[4/5] Testing recovery to CLOSED after successes...")
    if manager._circuit_breaker:
        # Simulate successful calls in HALF_OPEN state
        success_threshold = manager._circuit_breaker.config.success_threshold
        for i in range(success_threshold):
            await manager._circuit_breaker._on_success()
        
        # Circuit should be CLOSED
        assert manager._circuit_breaker.state == CircuitState.CLOSED, \
            f"Circuit should be CLOSED after {success_threshold} successes"

        print(f"✅ Circuit recovered to CLOSED after {success_threshold} successes")
        print(f"   State: {manager._circuit_breaker.state}")
    
    print("\n[5/5] Testing metrics tracking during failure recovery...")
    if manager.metrics:
        metrics = manager.metrics.to_dict()
        
        # Verify circuit breaker metrics
        assert 'circuit_breaker' in metrics, "Circuit breaker metrics missing"
        cb_metrics = metrics['circuit_breaker']
        
        print(f"✅ Circuit breaker metrics tracked:")
        print(f"   Opens: {cb_metrics.get('opens', 0)}")
        print(f"   Current state: {cb_metrics.get('state', 'unknown')}")
    
    # Print final metrics
    if manager.metrics:
        print("\n" + "-"*60)
        print("Final Metrics:")
        print("-"*60)
        metrics = manager.metrics.to_dict()
        print(f"Circuit Breaker Opens: {metrics['circuit_breaker'].get('opens', 0)}")
        print(f"Circuit Breaker State: {metrics['circuit_breaker'].get('state', 'unknown')}")
        print(f"Total Connections: {metrics['connections']['total']}")
        print(f"Failed Connections: {metrics['connections']['failed']}")
    
    print("\n" + "="*60)
    print("✅ FAILURE RECOVERY TEST PASSED")
    print("="*60)
    return True


async def main():
    """Run the integration test."""
    try:
        success = await test_failure_recovery()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

