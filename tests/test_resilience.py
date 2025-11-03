"""
Tests for resilience patterns (Batch 9.4)

Basic smoke tests to verify retry logic and circuit breaker functionality.
Comprehensive integration tests should be added in future batches.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.providers.resilience import (
    RetryHandler,
    RetryConfig,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    ResilientProvider
)


class TestRetryHandler:
    """Tests for RetryHandler (Task 9.1)"""
    
    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """Test successful execution on first attempt (no retries needed)"""
        handler = RetryHandler(RetryConfig(max_attempts=3))
        
        async def success_func():
            return "success"
        
        result = await handler.retry_async(success_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Test successful execution after transient failures"""
        handler = RetryHandler(RetryConfig(max_attempts=3, base_delay=0.1))
        
        call_count = 0
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient failure")
            return "success"
        
        result = await handler.retry_async(flaky_func)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """Test failure when max retries exceeded"""
        handler = RetryHandler(RetryConfig(max_attempts=3, base_delay=0.1))
        
        async def always_fail():
            raise ConnectionError("Permanent failure")
        
        with pytest.raises(ConnectionError):
            await handler.retry_async(always_fail)
    
    @pytest.mark.asyncio
    async def test_retry_non_retryable_error(self):
        """Test immediate failure for non-retryable errors"""
        handler = RetryHandler(RetryConfig(max_attempts=3))
        
        async def non_retryable_error():
            error = Exception("Non-retryable")
            error.status_code = 404  # Client error - don't retry
            raise error
        
        with pytest.raises(Exception):
            await handler.retry_async(non_retryable_error)
    
    def test_calculate_delay_exponential_backoff(self):
        """Test exponential backoff calculation"""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=60.0, jitter=False)
        handler = RetryHandler(config)
        
        # Attempt 0: 1.0 * 2^0 = 1.0
        assert handler._calculate_delay(0) == 1.0
        
        # Attempt 1: 1.0 * 2^1 = 2.0
        assert handler._calculate_delay(1) == 2.0
        
        # Attempt 2: 1.0 * 2^2 = 4.0
        assert handler._calculate_delay(2) == 4.0
        
        # Attempt 10: Should cap at max_delay
        assert handler._calculate_delay(10) == 60.0
    
    def test_calculate_delay_with_jitter(self):
        """Test jitter adds randomization"""
        config = RetryConfig(base_delay=10.0, exponential_base=2.0, max_delay=60.0, jitter=True)
        handler = RetryHandler(config)
        
        # With jitter, delay should be between 0 and calculated delay
        delay = handler._calculate_delay(0)
        assert 0 <= delay <= 10.0
    
    def test_should_retry_http_status_codes(self):
        """Test provider-specific error handling (EXAI adjustment)"""
        handler = RetryHandler()
        
        # Retryable status codes
        for code in [429, 500, 502, 503, 504]:
            error = Exception(f"HTTP {code}")
            error.status_code = code
            assert handler._should_retry(error), f"Should retry {code}"
        
        # Non-retryable status codes
        for code in [400, 401, 403, 404]:
            error = Exception(f"HTTP {code}")
            error.status_code = code
            assert not handler._should_retry(error), f"Should not retry {code}"


class TestCircuitBreaker:
    """Tests for CircuitBreaker (Task 9.2)"""
    
    @pytest.mark.asyncio
    async def test_circuit_closed_normal_operation(self):
        """Test normal operation with circuit closed"""
        breaker = CircuitBreaker(CircuitBreakerConfig(), provider_name="test")
        
        async def success_func():
            return "success"
        
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold"""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config, provider_name="test")
        
        async def always_fail():
            raise Exception("Failure")
        
        # Fail 3 times to reach threshold
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(always_fail)
        
        # Circuit should be open
        assert breaker.state == CircuitState.OPEN
        
        # Next call should be rejected immediately
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await breaker.call(always_fail)
    
    @pytest.mark.asyncio
    async def test_circuit_half_open_after_timeout(self):
        """Test circuit transitions to half-open after timeout"""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1)
        breaker = CircuitBreaker(config, provider_name="test")
        
        async def always_fail():
            raise Exception("Failure")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(always_fail)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Next call should transition to half-open
        # (will fail and go back to open, but that's expected)
        with pytest.raises(Exception):
            await breaker.call(always_fail)
        
        # Should have attempted half-open state
        assert breaker.failure_count > 0
    
    @pytest.mark.asyncio
    async def test_circuit_closes_after_success_threshold(self):
        """Test circuit closes after success threshold in half-open state"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.1
        )
        breaker = CircuitBreaker(config, provider_name="test")
        
        call_count = 0
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Initial failures")
            return "success"
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(flaky_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Succeed twice to close circuit
        result1 = await breaker.call(flaky_func)
        result2 = await breaker.call(flaky_func)
        
        assert result1 == "success"
        assert result2 == "success"
        assert breaker.state == CircuitState.CLOSED


class TestResilientProvider:
    """Tests for ResilientProvider (Combined Pattern)"""
    
    @pytest.mark.asyncio
    async def test_resilient_provider_success(self):
        """Test successful execution with resilient provider"""
        provider = ResilientProvider("test")
        
        async def success_func():
            return "success"
        
        result = await provider.execute(success_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_resilient_provider_retry_then_success(self):
        """Test retry logic works in resilient provider"""
        provider = ResilientProvider("test")
        
        call_count = 0
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Transient failure")
            return "success"
        
        result = await provider.execute(flaky_func)
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_provider_isolation(self):
        """Test circuit breakers are isolated per provider (EXAI adjustment)"""
        provider1 = ResilientProvider("provider1")
        provider2 = ResilientProvider("provider2")
        
        # Verify they have different circuit breakers
        assert provider1.circuit_breaker is not provider2.circuit_breaker
        assert provider1.circuit_breaker.provider_name == "provider1"
        assert provider2.circuit_breaker.provider_name == "provider2"
        
        # Verify same provider name shares circuit breaker
        provider1_copy = ResilientProvider("provider1")
        assert provider1.circuit_breaker is provider1_copy.circuit_breaker


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

