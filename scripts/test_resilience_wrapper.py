"""
Tests for Resilience Wrapper

Tests the unified resilience wrapper combining circuit breaker and retry logic.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-10-31
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.monitoring.resilience import (
    ResilienceWrapper,
    ResilienceWrapperFactory,
    RetryConfig,
)


class TestResilienceWrapper:
    """Tests for resilience wrapper."""
    
    def test_wrapper_success(self):
        """Test: Wrapper handles successful operations."""
        wrapper = ResilienceWrapper("test_success")
        
        def success_func():
            return "success"
        
        result = wrapper.execute(success_func)
        assert result == "success"
        assert wrapper.success_count == 1
        assert wrapper.failure_count == 0
    
    def test_wrapper_retry_then_success(self):
        """Test: Wrapper retries and succeeds."""
        wrapper = ResilienceWrapper(
            "test_retry",
            retry_config=RetryConfig(max_attempts=3, initial_delay=0.01)
        )
        
        call_count = 0
        
        def sometimes_failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = wrapper.execute(sometimes_failing_func)
        assert result == "success"
        assert wrapper.success_count == 1
        assert wrapper.failure_count == 0
    
    def test_wrapper_circuit_breaker_opens(self):
        """Test: Wrapper circuit breaker opens on failures."""
        wrapper = ResilienceWrapper(
            "test_circuit",
            circuit_breaker_config={'failure_threshold': 2},
            retry_config=RetryConfig(max_attempts=1, initial_delay=0.01)
        )
        
        def failing_func():
            raise Exception("Permanent failure")
        
        # Fail twice to open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                wrapper.execute(failing_func)
        
        # Circuit should be open
        assert wrapper.circuit_breaker.state.value == "open"
        
        # Next call should fail immediately
        with pytest.raises(Exception, match="Circuit breaker"):
            wrapper.execute(failing_func)
    
    def test_wrapper_metrics(self):
        """Test: Wrapper provides comprehensive metrics."""
        wrapper = ResilienceWrapper("test_metrics")
        
        def success_func():
            return "success"
        
        wrapper.execute(success_func)
        
        metrics = wrapper.get_metrics()
        assert metrics['name'] == "test_metrics"
        assert metrics['operation_count'] == 1
        assert metrics['success_count'] == 1
        assert metrics['failure_count'] == 0
        assert metrics['success_rate'] == 100.0
        assert 'circuit_breaker' in metrics
        assert 'retry_logic' in metrics
    
    def test_wrapper_reset(self):
        """Test: Wrapper can be reset."""
        wrapper = ResilienceWrapper("test_reset")
        
        def success_func():
            return "success"
        
        wrapper.execute(success_func)
        assert wrapper.operation_count == 1
        
        wrapper.reset()
        assert wrapper.operation_count == 0
        assert wrapper.success_count == 0
        assert wrapper.failure_count == 0


class TestResilienceWrapperFactory:
    """Tests for resilience wrapper factory."""
    
    def teardown_method(self):
        """Clean up after each test."""
        ResilienceWrapperFactory.clear()
    
    def test_factory_create(self):
        """Test: Factory creates wrapper."""
        wrapper = ResilienceWrapperFactory.create("test_factory")
        assert wrapper is not None
        assert wrapper.name == "test_factory"
    
    def test_factory_get_existing(self):
        """Test: Factory returns existing wrapper."""
        wrapper1 = ResilienceWrapperFactory.create("test_existing")
        wrapper2 = ResilienceWrapperFactory.get("test_existing")
        
        assert wrapper1 is wrapper2
    
    def test_factory_get_nonexistent(self):
        """Test: Factory returns None for nonexistent wrapper."""
        wrapper = ResilienceWrapperFactory.get("nonexistent")
        assert wrapper is None
    
    def test_factory_get_all_metrics(self):
        """Test: Factory returns metrics for all wrappers."""
        ResilienceWrapperFactory.create("wrapper1")
        ResilienceWrapperFactory.create("wrapper2")
        
        metrics = ResilienceWrapperFactory.get_all_metrics()
        assert len(metrics) == 2
        assert "wrapper1" in metrics
        assert "wrapper2" in metrics
    
    def test_factory_reset_all(self):
        """Test: Factory resets all wrappers."""
        wrapper1 = ResilienceWrapperFactory.create("wrapper1")
        wrapper2 = ResilienceWrapperFactory.create("wrapper2")
        
        def success_func():
            return "success"
        
        wrapper1.execute(success_func)
        wrapper2.execute(success_func)
        
        assert wrapper1.operation_count == 1
        assert wrapper2.operation_count == 1
        
        ResilienceWrapperFactory.reset_all()
        
        assert wrapper1.operation_count == 0
        assert wrapper2.operation_count == 0
    
    def test_factory_clear(self):
        """Test: Factory clears all wrappers."""
        ResilienceWrapperFactory.create("wrapper1")
        ResilienceWrapperFactory.create("wrapper2")
        
        metrics = ResilienceWrapperFactory.get_all_metrics()
        assert len(metrics) == 2
        
        ResilienceWrapperFactory.clear()
        
        metrics = ResilienceWrapperFactory.get_all_metrics()
        assert len(metrics) == 0


def run_tests():
    """Run all wrapper tests."""
    print("=" * 60)
    print("Resilience Wrapper Tests")
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

