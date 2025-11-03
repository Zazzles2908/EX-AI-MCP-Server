# Batch 9 Implementation Plan: Enhanced Reliability

**Date Created:** 2025-11-02
**Status:** 📋 READY TO IMPLEMENT (with adjustments)
**Priority:** HIGH
**Estimated Duration:** 2-3 hours
**EXAI Consultation:** ✅ COMPLETE + VALIDATED (Continuation ID: 2990f86f-4ce1-457d-9398-516d599e5902)
**EXAI Model:** Kimi Thinking Preview (deep analysis mode)

---

## Executive Summary

Implement retry logic and circuit breaker patterns to improve file upload success rate from ~85% to 99%+. This builds directly on Batch 8's unified architecture and provides production-ready resilience.

**Strategic Decision:** Skip Batches 5-7 (superseded by Batch 8) and proceed directly to Batch 9 per EXAI recommendation.

---

## ⚠️ CRITICAL ADJUSTMENTS (EXAI Thinking Mode Validation)

**EXAI Deep Analysis identified these required adjustments:**

### 1. Provider-Specific Error Handling
**Issue:** Current implementation catches general exceptions but doesn't differentiate provider-specific errors.

**Required Change:**
```python
# Add to RetryHandler._should_retry()
def _should_retry(self, error: Exception) -> bool:
    """Determine if error is retryable."""
    retryable_errors = (
        ConnectionError,
        TimeoutError,
        # HTTP status codes that should retry
        # 429 (rate limit), 500, 502, 503, 504 (server errors)
    )

    # Check HTTP status codes if available
    if hasattr(error, 'status_code'):
        return error.status_code in [429, 500, 502, 503, 504]

    return isinstance(error, retryable_errors)
```

### 2. Circuit Breaker State Persistence & Provider Isolation
**Issue:** Circuit breaker state resets on process restart; need separate breakers per provider.

**Required Change:**
```python
# Provider-specific circuit breakers
class ResilientProvider:
    _circuit_breakers = {}  # Class-level shared state

    def __init__(self, provider_name: str):
        if provider_name not in self._circuit_breakers:
            self._circuit_breakers[provider_name] = CircuitBreaker(
                config=CircuitBreakerConfig(),
                provider_name=provider_name
            )
        self.circuit_breaker = self._circuit_breakers[provider_name]
```

### 3. Jitter Implementation Enhancement
**Issue:** Current jitter uses simple random which may not provide sufficient variance.

**Required Change:**
```python
def _calculate_delay(self, attempt: int) -> float:
    """Calculate delay with exponential backoff and proper jitter."""
    delay = min(
        self.config.base_delay * (self.config.exponential_base ** attempt),
        self.config.max_delay
    )
    if self.config.jitter:
        # Full jitter: random between 0 and calculated delay
        delay = random.uniform(0, delay)
    return delay
```

### 4. Supabase Tracking During Retries
**Issue:** Prevent incomplete Supabase records during failed upload attempts.

**Required Change:**
```python
# In UnifiedFileManager.upload_file()
# Only track in Supabase AFTER successful upload
try:
    result = await resilient_provider.execute(provider.upload, file_path)
    # Track ONLY on success
    if track_in_supabase:
        await self._track_in_supabase(result)
    return result
except Exception as e:
    # Do NOT track failed attempts
    raise
```

### 5. Logging Enhancements
**Issue:** Current logging doesn't include retry attempts or circuit state changes.

**Required Change:**
```python
# Add to RetryHandler
logger.info(f"[RETRY] Attempt {attempt + 1}/{self.config.max_attempts} for {func.__name__}")

# Add to CircuitBreaker
logger.warning(f"[CIRCUIT] State transition: {old_state} → {new_state} for {provider_name}")
```

---

## Pre-Implementation Checklist

**MUST complete before starting Task 9.1:**

- [ ] **Add resilience configuration to `.env.docker`:**
  ```bash
  RESILIENCE_ENABLED=true
  RESILIENCE_RETRY_ENABLED=true
  RETRY_MAX_ATTEMPTS=3
  RETRY_BASE_DELAY=1.0
  RETRY_MAX_DELAY=60.0
  RETRY_EXPONENTIAL_BASE=2.0
  RETRY_JITTER=true
  RESILIENCE_CIRCUIT_BREAKER_ENABLED=true
  CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
  CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2
  CIRCUIT_BREAKER_TIMEOUT=60.0
  CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS=1
  ```

- [ ] **Verify async/await consistency in provider methods**
- [ ] **Review current error handling in UnifiedFileManager**
- [ ] **Confirm Supabase tracking logic location**

---

## Tasks Overview

| Task | Description | Priority | Estimated Time |
|------|-------------|----------|----------------|
| 9.0 | Pre-Implementation Setup | CRITICAL | 15 mins |
| 9.1 | Implement Retry Logic | CRITICAL | 1-1.5 hours |
| 9.2 | Add Circuit Breaker Pattern | HIGH | 1-1.5 hours |

**Total Estimated Time:** 2.5-3.5 hours (including setup)

---

## Task 9.1: Implement Retry Logic

### Objective
Create RetryHandler with exponential backoff and jitter to handle transient network failures.

### Files to Create
- `src/providers/resilience.py` (new, ~200 lines)

### Files to Modify
- `.env.docker` (add retry configuration)
- `src/storage/unified_file_manager.py` (integrate retry decorator)

### Implementation Details

**RetryHandler Class:**
```python
# src/providers/resilience.py
import asyncio
import random
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class RetryHandler:
    """Handles retry logic with exponential backoff and jitter."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        if self.config.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        return delay
    
    def _should_retry(self, error: Exception) -> bool:
        """Determine if error is retryable."""
        # Retry on network errors, rate limits, server errors
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            # Add provider-specific errors
        )
        return isinstance(error, retryable_errors)
    
    async def retry_async(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.config.max_attempts}")
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e):
                    logger.warning(f"Non-retryable error: {e}")
                    raise
                
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retry after {delay:.2f}s due to: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max retries exceeded: {e}")
        
        raise last_exception
```

**Environment Configuration:**
```bash
# .env.docker additions
RESILIENCE_ENABLED=true
RESILIENCE_RETRY_ENABLED=true
RETRY_MAX_ATTEMPTS=3
RETRY_BASE_DELAY=1.0
RETRY_MAX_DELAY=60.0
RETRY_EXPONENTIAL_BASE=2.0
RETRY_JITTER=true
```

### Integration Points
- Wrap provider upload methods with retry decorator
- Integrate with UnifiedFileManager from Batch 8.1
- Log retry attempts for monitoring

### Testing Requirements
1. Unit tests for exponential backoff calculation
2. Unit tests for jitter randomization
3. Integration tests with simulated network failures (429, 500, 502, 503, 504)
4. Verify max retries enforcement
5. Test non-retryable errors (immediate failure)

### Acceptance Criteria
- ✅ Retry logic handles transient failures
- ✅ Exponential backoff with jitter implemented correctly
- ✅ Configurable via environment variables
- ✅ Comprehensive logging at appropriate levels
- ✅ No breaking changes to existing API

---

## Task 9.2: Add Circuit Breaker Pattern

### Objective
Implement circuit breaker to prevent cascading failures when providers are down.

### Files to Modify
- `src/providers/resilience.py` (add CircuitBreaker class)
- `.env.docker` (add circuit breaker configuration)

### Implementation Details

**CircuitBreaker Class:**
```python
# src/providers/resilience.py (continued)
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        half_open_max_calls: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls

class CircuitBreaker:
    """Circuit breaker pattern for provider resilience."""
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self.state != CircuitState.OPEN:
            return False
        if self.last_failure_time is None:
            return True
        timeout_elapsed = (
            datetime.now() - self.last_failure_time
        ).total_seconds() >= self.config.timeout
        return timeout_elapsed
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        
        # Check if circuit should attempt reset
        if self._should_attempt_reset():
            logger.info("Circuit breaker entering HALF_OPEN state")
            self.state = CircuitState.HALF_OPEN
            self.half_open_calls = 0
        
        # Reject if circuit is open
        if self.state == CircuitState.OPEN:
            raise Exception("Circuit breaker is OPEN - provider unavailable")
        
        # Limit calls in half-open state
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                raise Exception("Circuit breaker HALF_OPEN - max calls exceeded")
            self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                logger.info("Circuit breaker closing - provider recovered")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker opening - recovery failed")
            self.state = CircuitState.OPEN
            self.success_count = 0
        elif self.failure_count >= self.config.failure_threshold:
            logger.error(f"Circuit breaker opening - {self.failure_count} failures")
            self.state = CircuitState.OPEN
```

**Environment Configuration:**
```bash
# .env.docker additions
RESILIENCE_CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2
CIRCUIT_BREAKER_TIMEOUT=60.0
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS=1
```

### Integration Points
- Wrap provider calls with circuit breaker
- Share circuit breaker state across all calls to same provider
- Log state transitions for monitoring

### Testing Requirements
1. Unit tests for state transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
2. Test failure threshold enforcement
3. Test timeout and reset behavior
4. Test half-open state call limiting
5. Integration tests with provider downtime simulation

### Acceptance Criteria
- ✅ Circuit breaker prevents cascading failures
- ✅ State transitions work correctly
- ✅ Timeout and reset logic functional
- ✅ Configurable via environment variables
- ✅ Clear logging of state changes

---

## Combined Implementation: ResilientProvider

**Decorator Pattern:**
```python
# src/providers/resilience.py (continued)
class ResilientProvider:
    """Combines retry and circuit breaker patterns."""
    
    def __init__(
        self,
        retry_config: Optional[RetryConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None
    ):
        self.retry_handler = RetryHandler(retry_config)
        self.circuit_breaker = CircuitBreaker(circuit_config)
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with both retry and circuit breaker protection."""
        return await self.retry_handler.retry_async(
            self.circuit_breaker.call,
            func,
            *args,
            **kwargs
        )
```

---

## Testing Strategy

### Priority 1 (Critical Path)
1. Circuit breaker state transitions
2. Exponential backoff calculation

### Priority 2 (Integration)
3. Simulated network failures
4. Provider-specific error handling

### Priority 3 (Edge Cases)
5. Concurrent requests
6. Configuration boundaries

---

## Backward Compatibility

**Strategy:** Enabled by default with opt-out

- No breaking changes to existing API
- Clear logging when resilience features activate
- Configuration allows disabling if needed

---

## Success Metrics

- Upload success rate: 85% → 99%+
- Mean time to recovery: <60 seconds
- Retry overhead: <5% additional latency
- Circuit breaker false positives: <1%

---

## Next Steps After Batch 9

1. **Batch 10:** Configuration Optimization (reduce .env.docker from 738 to <200 lines)
2. **Batch 11:** Advanced Monitoring (Prometheus metrics, provider health dashboards)
3. **Future:** Batch operations, provider plugin architecture

