# Phase 2.4.6 & 2.5 - Comprehensive Implementation Plan

**Date**: 2025-10-31  
**Status**: 📋 READY FOR EXECUTION  
**EXAI Consultation**: ac40c717-09db-4b0a-b943-6e38730a1300 (14 turns remaining)  
**Duration**: 3 weeks (Phase 2.4.6: 1 week, Phase 2.5: 2 weeks)

## Executive Summary

**Phase 2.4.6**: Integrate resilience patterns into MetricsPersister with DLQ and graceful shutdown  
**Phase 2.5**: Migrate dashboard from WebSocket to Supabase Realtime with dual-mode operation  

**Total Scope**: 13 files to create/modify, 50+ tests, 3-week timeline

---

## PHASE 2.4.6: MetricsPersister Resilience Integration

### Objective
Wrap MetricsPersister database operations with circuit breaker + retry logic + DLQ + graceful shutdown

### Dependency Map

**MetricsPersister Consumers**:
- `src/daemon/monitoring_endpoint.py` (lines 45-52) - Creates instance
- `src/monitoring/adapters/realtime_adapter.py` (lines 78-85) - Uses for storage
- `scripts/test_metrics_persister_resilience.py` - New tests

**MonitoringBroadcaster Consumers**:
- `src/daemon/monitoring_endpoint.py` (lines 38-44) - Creates instance
- `src/monitoring/adapters/websocket_adapter.py` - WebSocket implementation
- `src/monitoring/adapters/realtime_adapter.py` - Realtime implementation

**MonitoringEndpoint Consumers**:
- `src/daemon/main.py` - Main entry point
- Process management (systemd, supervisor)

### Configuration Strategy

**Environment Variables (.env)**:
```env
METRICS_PERSISTER_CIRCUIT_BREAKER_THRESHOLD=5
METRICS_PERSISTER_CIRCUIT_BREAKER_TIMEOUT=60
METRICS_PERSISTER_RETRY_MAX_ATTEMPTS=3
METRICS_PERSISTER_RETRY_BACKOFF_FACTOR=2
METRICS_PERSISTER_DLQ_ENABLED=true
METRICS_PERSISTER_GRACEFUL_SHUTDOWN_TIMEOUT=30
```

**Feature Flags**:
- `RESILIENCE_METRICS_PERSISTER_ENABLED`
- `RESILIENCE_CIRCUIT_BREAKER_ENABLED`
- `RESILIENCE_RETRY_ENABLED`
- `RESILIENCE_DLQ_ENABLED`
- `RESILIENCE_GRACEFUL_SHUTDOWN_ENABLED`

### Files to Create/Modify

**Create**:
1. `src/monitoring/persistence/dead_letter_queue.py` - DLQ implementation
2. `src/monitoring/persistence/graceful_shutdown.py` - Shutdown handler
3. `scripts/test_metrics_persister_resilience.py` - Tests (12-15 tests)
4. `supabase/migrations/20251101_create_dlq_table.sql` - DLQ schema

**Modify**:
1. `src/monitoring/persistence/metrics_persister.py` - Add resilience wrapper
2. `src/daemon/monitoring_endpoint.py` - Add graceful shutdown

### Test Scenarios (12-15 tests)

1. **Circuit Breaker** (3 tests):
   - Activation on database failures
   - Recovery after timeout
   - Half-open state behavior

2. **Retry Logic** (3 tests):
   - Transient error handling
   - Exponential backoff verification
   - Maximum retry enforcement

3. **Dead Letter Queue** (3 tests):
   - Failed operation storage
   - Recovery mechanisms
   - Size/retention limits

4. **Graceful Shutdown** (3 tests):
   - In-flight operation completion
   - Resource cleanup
   - Signal handling

5. **Concurrency** (2 tests):
   - Thread safety
   - Concurrent DLQ access

### Timeline

- **Day 1-2**: DLQ implementation + tests
- **Day 3-4**: Graceful shutdown + tests
- **Day 5**: Resilience integration + tests
- **Total**: 5 days

---

## PHASE 2.5: Dashboard Migration Strategy

### Objective
Transition from WebSocket to Supabase Realtime with dual-mode operation

### Architecture Decision: Option C

**Modular JavaScript with Supabase Integration**
- Minimal disruption to existing system
- Gradual migration capability
- Lower risk during transition
- Future-proof for framework migration

### Dependency Map

**Dashboard WebSocket Consumers**:
- `static/js/dashboard-core.js` (lines 23-45) - Connection management
- `static/js/session-tracker.js` (lines 67-89) - Session tracking
- `static/js/chart-manager.js` (lines 112-134) - Chart updates

**Server-side WebSocket**:
- `src/monitoring/adapters/websocket_adapter.py` - WebSocket server

### Files to Create/Modify

**Create**:
1. `static/js/supabase-client.js` - Supabase client initialization
2. `static/js/realtime-adapter.js` - Supabase Realtime wrapper
3. `static/js/cross-session-state.js` - State management layer
4. `static/js/feature-flag-client.js` - Client-side feature flags

**Modify**:
1. `static/monitoring_dashboard.html` - Add Supabase client
2. `static/js/dashboard-core.js` - Data source abstraction
3. `static/js/session-tracker.js` - Dual data source support
4. `static/js/chart-manager.js` - Dual data source support

### Implementation Phases

**Week 1: Infrastructure Setup**
- Create Supabase client components
- Implement state management layer
- Set up feature flag system
- Create realtime adapter

**Week 2: Dual-Mode Implementation**
- Modify dashboard-core.js for data source abstraction
- Update session-tracker.js for dual support
- Update chart-manager.js for dual support
- Add feature flag toggling

**Week 3: Migration & Testing**
- Deploy dual-mode dashboard
- Gradually migrate users to Supabase
- Monitor performance and reliability
- Remove WebSocket code after successful migration

### Risk Mitigation

**Phase 2.4.6 Risks**:
1. Data Loss → DLQ with persistent storage + recovery
2. Performance Degradation → Circuit breaker prevents cascades
3. Complexity → Use existing patterns + comprehensive testing

**Phase 2.5 Risks**:
1. User Disruption → Dual-mode with feature flags + gradual rollout
2. Backward Compatibility → Maintain WebSocket during transition
3. Real-time Performance → Performance testing + optimization

### Success Criteria

**Phase 2.4.6**:
✅ All database operations protected by circuit breaker  
✅ Failed metrics stored in DLQ  
✅ Graceful shutdown without data loss  
✅ All 12-15 tests passing  
✅ EXAI validation obtained  

**Phase 2.5**:
✅ Dual-mode dashboard operational  
✅ Data sync latency < 500ms  
✅ Dashboard load time < 2 seconds  
✅ System uptime > 99.9%  
✅ Error rate < 0.1%  

---

## EXAI Tool Usage Strategy

**Working Tools**:
- ✅ `chat_EXAI-WS-VSCode2` with embedded files
- ✅ `continuation_id` for context preservation
- ✅ High thinking mode for complex decisions
- ✅ `codebase-retrieval` for code patterns
- ✅ `view` tool for reading files

**Workarounds**:
- Use `chat` instead of `smart_file_query` (upload failures)
- Use sequential execution instead of parallel (GLM rate limiting)
- Use Kimi provider as fallback for GLM (rate limiting)
- Use full absolute paths for all file references

**Consultation Approach**:
- Provide FULL CONTEXT to EXAI (not interpretation)
- Use continuation_id to maintain conversation context
- Ask specific, targeted questions
- Get EXAI approval before implementation

---

## Next Steps

1. ✅ Complete Phase 2.4 (DONE)
2. 🔄 **Implement Phase 2.4.6** (MetricsPersister Resilience)
3. 📋 Implement Phase 2.5 (Dashboard Migration)
4. 📋 Complete Phase 2.6 (Full Migration)

---

**Status**: 📋 **READY FOR EXECUTION**  
**EXAI Validation**: ✅ **APPROVED**  
**Remaining Turns**: 14 of 20

