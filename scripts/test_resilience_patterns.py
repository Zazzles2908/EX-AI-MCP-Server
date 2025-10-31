"""
Tests for Resilience Patterns

Tests circuit breaker and retry logic implementations.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-10-31
"""

import os
import sys
import time
from typing import Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.monitoring.resilience import (
    CircuitBreaker,
    CircuitState,
    RetryConfig,
    RetryLogic,
    retry_with_backoff,
)


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""
    
    def test_circuit_breaker_closed_state(self):
        """Test: Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_breaker_success(self):
        """Test: Successful calls maintain CLOSED state."""
        cb = CircuitBreaker("test")
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_breaker_opens_on_failures(self):
        """Test: Circuit breaker opens after threshold failures."""
        cb = CircuitBreaker("test", failure_threshold=3)
        
        def failing_func():
            raise Exception("Test failure")
        
        # Fail 3 times
        for _ in range(3):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        # Circuit should be OPEN
        assert cb.state == CircuitState.OPEN
        
        # Next call should fail immediately
        with pytest.raises(Exception, match="Circuit breaker"):
            cb.call(failing_func)
    
    def test_circuit_breaker_half_open_recovery(self):
        """Test: Circuit breaker attempts recovery in HALF_OPEN state."""
        cb = CircuitBreaker(
            "test",
            failure_threshold=2,
            recovery_timeout=1,
            success_threshold=1
        )
        
        def failing_func():
            raise Exception("Test failure")
        
        # Fail twice to open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Next call should attempt recovery (HALF_OPEN)
        def success_func():
            return "recovered"
        
        result = cb.call(success_func)
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_breaker_metrics(self):
        """Test: Circuit breaker provides metrics."""
        cb = CircuitBreaker("test")
        
        metrics = cb.get_metrics()
        assert metrics['name'] == "test"
        assert metrics['state'] == "closed"
        assert metrics['failure_count'] == 0
    
    def test_circuit_breaker_reset(self):
        """Test: Circuit breaker can be manually reset."""
        cb = CircuitBreaker("test", failure_threshold=1)
        
        def failing_func():
            raise Exception("Test failure")
        
        # Fail once to open circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Reset
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestRetryLogic:
    """Tests for retry logic with exponential backoff."""
    
    def test_retry_success_first_attempt(self):
        """Test: Successful first attempt returns immediately."""
        config = RetryConfig(max_attempts=3)
        retry = RetryLogic(config)
        
        def success_func():
            return "success"
        
        result = retry.execute(success_func)
        assert result == "success"
        assert retry.attempt_count == 1
    
    def test_retry_success_after_failures(self):
        """Test: Retry succeeds after initial failures."""
        config = RetryConfig(max_attempts=3, initial_delay=0.1)
        retry = RetryLogic(config)
        
        call_count = 0
        
        def sometimes_failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = retry.execute(sometimes_failing_func)
        assert result == "success"
        assert retry.attempt_count == 3
    
    def test_retry_exhaustion(self):
        """Test: Retry exhaustion raises exception."""
        config = RetryConfig(max_attempts=2, initial_delay=0.01)
        retry = RetryLogic(config)
        
        def always_failing_func():
            raise Exception("Permanent failure")
        
        with pytest.raises(Exception, match="Permanent failure"):
            retry.execute(always_failing_func)
        
        assert retry.attempt_count == 2
    
    def test_retry_exponential_backoff(self):
        """Test: Retry uses exponential backoff."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            exponential_base=2.0,
            jitter=False
        )
        retry = RetryLogic(config)
        
        # Verify delay calculation
        delay_1 = retry._calculate_delay(1)
        delay_2 = retry._calculate_delay(2)
        delay_3 = retry._calculate_delay(3)
        
        assert delay_1 == 0.1
        assert delay_2 == 0.2
        assert delay_3 == 0.4
    
    def test_retry_max_delay_cap(self):
        """Test: Retry respects max delay cap."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=False
        )
        retry = RetryLogic(config)
        
        # Delay should be capped at max_delay
        delay = retry._calculate_delay(10)
        assert delay == 5.0
    
    def test_retry_metrics(self):
        """Test: Retry provides metrics."""
        config = RetryConfig(max_attempts=3)
        retry = RetryLogic(config)
        
        metrics = retry.get_metrics()
        assert metrics['max_attempts'] == 3
        assert metrics['attempt_count'] == 0
    
    def test_retry_decorator(self):
        """Test: Retry decorator works correctly."""
        call_count = 0
        
        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        def sometimes_failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = sometimes_failing_func()
        assert result == "success"
        assert call_count == 2


def run_tests():
    """Run all resilience tests."""
    print("=" * 60)
    print("Resilience Patterns Tests")
    print("=" * 60)
    
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-s',
    ])
    
    return exit_code


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)

