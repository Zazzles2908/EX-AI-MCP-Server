# Phase 2.4.6 - MetricsPersister Resilience Integration - PLAN

**Date**: 2025-10-31  
**Status**: 🔄 IN PROGRESS - Planning & Implementation  
**EXAI Consultation**: ac40c717-09db-4b0a-b943-6e38730a1300 (16 turns remaining)

## Objective

Integrate resilience patterns (circuit breaker + retry logic) into MetricsPersister to ensure robust data persistence with graceful failure handling.

## Implementation Plan

### Phase 2.4.6.1: MetricsPersister Resilience Integration

**File**: `src/monitoring/persistence/metrics_persister.py`

**Changes**:
1. Import resilience components
2. Wrap database operations with ResilienceWrapper
3. Add circuit breaker for database connection
4. Add retry logic for failed inserts
5. Implement graceful degradation

**Code Structure**:
```python
from src.monitoring.resilience import ResilienceWrapperFactory, RetryConfig

class MetricsPersister:
    def __init__(self):
        # Create resilience wrapper for database operations
        self.db_wrapper = ResilienceWrapperFactory.create(
            'metrics_persister_db',
            circuit_breaker_config={
                'failure_threshold': 5,
                'recovery_timeout': 60,
            },
            retry_config=RetryConfig(
                max_attempts=3,
                initial_delay=1.0,
                exponential_base=2.0,
            )
        )
    
    async def flush_metrics(self):
        """Flush metrics with resilience protection."""
        try:
            result = self.db_wrapper.execute(
                self._persist_to_database
            )
            return result
        except Exception as e:
            logger.error(f"Metrics persistence failed: {e}")
            # Implement fallback strategy
```

### Phase 2.4.6.2: Dead-Letter Queue Implementation

**File**: `src/monitoring/persistence/dead_letter_queue.py` (NEW)

**Features**:
- Store failed metrics in DLQ table
- Retry mechanism for DLQ items
- Metrics tracking for DLQ operations
- Manual recovery interface

**Schema**:
```sql
CREATE TABLE monitoring.dead_letter_queue (
    id BIGSERIAL PRIMARY KEY,
    original_payload JSONB NOT NULL,
    failure_reason TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW(),
    last_retry_at TIMESTAMP,
    recovered_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);
```

### Phase 2.4.6.3: Graceful Shutdown Implementation

**File**: `src/monitoring/persistence/graceful_shutdown.py` (NEW)

**Features**:
- Signal handling (SIGTERM, SIGINT)
- Flush pending metrics before shutdown
- Close database connections gracefully
- Log shutdown state

### Phase 2.4.6.4: Comprehensive Testing

**File**: `scripts/test_metrics_persister_resilience.py` (NEW)

**Test Coverage**:
1. Circuit breaker activation on database failures
2. Retry logic with exponential backoff
3. Dead-letter queue storage and recovery
4. Graceful shutdown handling
5. Concurrent operations with resilience
6. Metrics tracking accuracy

**Expected Tests**: 12-15 tests

## Integration Points

1. **MetricsPersister**: Wrap database operations
2. **Realtime Adapter**: Add resilience to Supabase connection
3. **WebSocket Adapter**: Add resilience to WebSocket operations
4. **Dashboard Endpoints**: Add circuit breaker to prevent cascading failures

## Success Criteria

✅ All database operations protected by circuit breaker  
✅ Failed metrics stored in dead-letter queue  
✅ Graceful shutdown without data loss  
✅ All tests passing (12-15 tests)  
✅ EXAI validation obtained  
✅ Documentation complete  

## Timeline

- **Implementation**: 1-2 days
- **Testing**: 1 day
- **EXAI Validation**: 1 day
- **Total**: 3-4 days

## Next Phase

After Phase 2.4.6 completion → Phase 2.5: Resilient Connection Layer

## Files to Create/Modify

**Create**:
- `src/monitoring/persistence/dead_letter_queue.py`
- `src/monitoring/persistence/graceful_shutdown.py`
- `scripts/test_metrics_persister_resilience.py`
- `supabase/migrations/20251101_create_dlq_table.sql`

**Modify**:
- `src/monitoring/persistence/metrics_persister.py`
- `src/daemon/monitoring_endpoint.py` (add graceful shutdown)

## Status

**Phase 2.4.6**: 🔄 **IN PROGRESS**  
**Ready for**: Implementation after Phase 2.4.5 completion  
**EXAI Guidance**: ✅ Approved  

