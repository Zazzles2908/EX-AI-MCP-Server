"""
Tests for Graceful Degradation and Circuit Breaker

This test suite validates:
1. Fallback execution on primary failure
2. Circuit breaker opening after threshold failures
3. Circuit breaker recovery after timeout
4. Retry logic with exponential backoff
5. Timeout handling
6. Circuit status reporting
"""

import pytest
import asyncio
import time
from utils.infrastructure.error_handling import (
    GracefulDegradation,
    CircuitBreakerOpen,
    get_graceful_degradation,
    with_fallback
)


class TestFallbackExecution:
    """Test fallback execution when primary fails."""
    
    @pytest.mark.asyncio
    async def test_fallback_on_exception(self):
        """Test fallback is used when primary raises exception."""
        gd = GracefulDegradation()
        
        async def primary():
            raise Exception("Primary failed")
        
        async def fallback():
            return "fallback_result"
        
        result = await gd.execute_with_fallback(
            primary,
            fallback,
            timeout_secs=5.0,
            max_retries=0,
            operation_name="test_fallback_exception"
        )
        
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_fallback_on_timeout(self):
        """Test fallback is used when primary times out."""
        gd = GracefulDegradation()
        
        async def primary():
            await asyncio.sleep(10)  # Will timeout
            return "primary_result"
        
        async def fallback():
            return "fallback_result"
        
        result = await gd.execute_with_fallback(
            primary,
            fallback,
            timeout_secs=0.1,
            max_retries=0,
            operation_name="test_fallback_timeout"
        )
        
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_primary_success_no_fallback(self):
        """Test primary is used when it succeeds."""
        gd = GracefulDegradation()
        
        async def primary():
            return "primary_result"
        
        async def fallback():
            return "fallback_result"
        
        result = await gd.execute_with_fallback(
            primary,
            fallback,
            timeout_secs=5.0,
            max_retries=0,
            operation_name="test_primary_success"
        )
        
        assert result == "primary_result"
    
    @pytest.mark.asyncio
    async def test_no_fallback_raises_error(self):
        """Test error is raised when no fallback provided."""
        gd = GracefulDegradation()
        
        async def primary():
            raise ValueError("Primary failed")
        
        with pytest.raises(ValueError, match="Primary failed"):
            await gd.execute_with_fallback(
                primary,
                None,
                timeout_secs=5.0,
                max_retries=0,
                operation_name="test_no_fallback"
            )


class TestCircuitBreaker:
    """Test circuit breaker pattern."""
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        gd = GracefulDegradation(failure_threshold=3, recovery_timeout=60.0)
        
        async def failing_fn():
            raise Exception("Always fails")
        
        # Cause 3 failures (threshold)
        for i in range(3):
            try:
                await gd.execute_with_fallback(
                    failing_fn,
                    None,
                    timeout_secs=1.0,
                    max_retries=0,
                    operation_name="test_circuit_open"
                )
            except Exception:
                pass
        
        # Circuit breaker should be open
        status = gd.get_circuit_status("test_circuit_open")
        assert status["status"] == "open"
        assert status["failures"] == 3
    
    @pytest.mark.asyncio
    async def test_circuit_open_uses_fallback(self):
        """Test circuit breaker uses fallback when open."""
        gd = GracefulDegradation(failure_threshold=2, recovery_timeout=60.0)
        
        async def failing_fn():
            raise Exception("Always fails")
        
        async def fallback():
            return "fallback_result"
        
        # Cause 2 failures to open circuit
        for i in range(2):
            try:
                await gd.execute_with_fallback(
                    failing_fn,
                    fallback,
                    timeout_secs=1.0,
                    max_retries=0,
                    operation_name="test_circuit_fallback"
                )
            except Exception:
                pass
        
        # Next call should use fallback immediately
        result = await gd.execute_with_fallback(
            failing_fn,
            fallback,
            timeout_secs=1.0,
            max_retries=0,
            operation_name="test_circuit_fallback"
        )
        
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_circuit_open_raises_without_fallback(self):
        """Test circuit breaker raises CircuitBreakerOpen when no fallback."""
        gd = GracefulDegradation(failure_threshold=2, recovery_timeout=60.0)
        
        async def failing_fn():
            raise Exception("Always fails")
        
        # Cause 2 failures to open circuit
        for i in range(2):
            try:
                await gd.execute_with_fallback(
                    failing_fn,
                    None,
                    timeout_secs=1.0,
                    max_retries=0,
                    operation_name="test_circuit_no_fallback"
                )
            except Exception:
                pass
        
        # Next call should raise CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            await gd.execute_with_fallback(
                failing_fn,
                None,
                timeout_secs=1.0,
                max_retries=0,
                operation_name="test_circuit_no_fallback"
            )
    
    @pytest.mark.asyncio
    async def test_circuit_recovers_after_timeout(self):
        """Test circuit breaker recovers after recovery timeout."""
        gd = GracefulDegradation(failure_threshold=2, recovery_timeout=0.5)
        
        async def failing_fn():
            raise Exception("Always fails")
        
        # Cause 2 failures to open circuit
        for i in range(2):
            try:
                await gd.execute_with_fallback(
                    failing_fn,
                    None,
                    timeout_secs=1.0,
                    max_retries=0,
                    operation_name="test_circuit_recovery"
                )
            except Exception:
                pass
        
        # Circuit should be open
        status = gd.get_circuit_status("test_circuit_recovery")
        assert status["status"] == "open"
        
        # Wait for recovery timeout
        await asyncio.sleep(0.6)
        
        # Circuit should be closed
        status = gd.get_circuit_status("test_circuit_recovery")
        assert status["status"] == "closed"
    
    @pytest.mark.asyncio
    async def test_circuit_resets_on_success(self):
        """Test circuit breaker resets failure count on success."""
        gd = GracefulDegradation(failure_threshold=3, recovery_timeout=60.0)
        
        call_count = 0
        
        async def sometimes_fails():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Fails first 2 times")
            return "success"
        
        # First 2 calls fail
        for i in range(2):
            try:
                await gd.execute_with_fallback(
                    sometimes_fails,
                    None,
                    timeout_secs=1.0,
                    max_retries=0,
                    operation_name="test_circuit_reset"
                )
            except Exception:
                pass
        
        # Circuit should have 2 failures
        status = gd.get_circuit_status("test_circuit_reset")
        assert status["failures"] == 2
        
        # Third call succeeds
        result = await gd.execute_with_fallback(
            sometimes_fails,
            None,
            timeout_secs=1.0,
            max_retries=0,
            operation_name="test_circuit_reset"
        )
        
        assert result == "success"
        
        # Circuit should be reset
        status = gd.get_circuit_status("test_circuit_reset")
        assert status["failures"] == 0


class TestRetryLogic:
    """Test retry logic with exponential backoff."""
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test function is retried on failure."""
        gd = GracefulDegradation()
        
        call_count = 0
        
        async def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Fails first 2 times")
            return "success"
        
        result = await gd.execute_with_fallback(
            fails_twice,
            None,
            timeout_secs=5.0,
            max_retries=2,
            operation_name="test_retry"
        )
        
        assert result == "success"
        assert call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff between retries."""
        gd = GracefulDegradation()
        
        call_times = []
        
        async def failing_fn():
            call_times.append(time.time())
            raise Exception("Always fails")
        
        try:
            await gd.execute_with_fallback(
                failing_fn,
                None,
                timeout_secs=5.0,
                max_retries=2,
                operation_name="test_backoff"
            )
        except Exception:
            pass
        
        # Should have 3 calls (initial + 2 retries)
        assert len(call_times) == 3
        
        # Check backoff intervals (approximately 1s, 2s)
        interval1 = call_times[1] - call_times[0]
        interval2 = call_times[2] - call_times[1]
        
        assert 0.9 < interval1 < 1.5  # ~1s backoff
        assert 1.9 < interval2 < 2.5  # ~2s backoff


class TestCircuitStatus:
    """Test circuit breaker status reporting."""
    
    def test_circuit_status_closed(self):
        """Test circuit status when closed."""
        gd = GracefulDegradation()
        
        status = gd.get_circuit_status("nonexistent_operation")
        
        assert status["status"] == "closed"
        assert status["failures"] == 0
        assert status["last_failure"] is None
        assert status["time_until_recovery"] == 0
    
    @pytest.mark.asyncio
    async def test_circuit_status_open(self):
        """Test circuit status when open."""
        gd = GracefulDegradation(failure_threshold=2, recovery_timeout=60.0)
        
        async def failing_fn():
            raise Exception("Always fails")
        
        # Cause 2 failures to open circuit
        for i in range(2):
            try:
                await gd.execute_with_fallback(
                    failing_fn,
                    None,
                    timeout_secs=1.0,
                    max_retries=0,
                    operation_name="test_status_open"
                )
            except Exception:
                pass
        
        status = gd.get_circuit_status("test_status_open")
        
        assert status["status"] == "open"
        assert status["failures"] == 2
        assert status["last_failure"] is not None
        assert 55 < status["time_until_recovery"] <= 60
    
    @pytest.mark.asyncio
    async def test_get_all_circuit_statuses(self):
        """Test getting all circuit statuses."""
        gd = GracefulDegradation(failure_threshold=2, recovery_timeout=60.0)
        
        async def failing_fn():
            raise Exception("Always fails")
        
        # Create failures for multiple operations
        for op_name in ["op1", "op2"]:
            for i in range(2):
                try:
                    await gd.execute_with_fallback(
                        failing_fn,
                        None,
                        timeout_secs=1.0,
                        max_retries=0,
                        operation_name=op_name
                    )
                except Exception:
                    pass
        
        all_statuses = gd.get_all_circuit_statuses()
        
        assert "op1" in all_statuses
        assert "op2" in all_statuses
        assert all_statuses["op1"]["status"] == "open"
        assert all_statuses["op2"]["status"] == "open"


class TestGlobalInstance:
    """Test global graceful degradation instance."""
    
    def test_get_graceful_degradation_singleton(self):
        """Test get_graceful_degradation returns singleton."""
        gd1 = get_graceful_degradation()
        gd2 = get_graceful_degradation()
        
        assert gd1 is gd2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

