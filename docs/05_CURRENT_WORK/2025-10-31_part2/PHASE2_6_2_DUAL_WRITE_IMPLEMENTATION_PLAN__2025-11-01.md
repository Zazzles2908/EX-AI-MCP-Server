# Phase 2.6.2 - Dual-Write Enhancement Implementation Plan

**Date**: 2025-11-01  
**Status**: PLANNING  
**EXAI Consultation**: d3e51bcb-c3ea-4122-834f-21e602a0a9b1  
**Continuation Turns Remaining**: 14

---

## 📋 Overview

Phase 2.6.2 implements the dual-write pattern with per-category feature flags, checksum validation, and reconciliation logic. This enables gradual rollout from WebSocket to Supabase Realtime with zero data loss.

---

## 🎯 Strategic Implementation Order

**Sequence**: Feature Flags → Checksum Validation → Reconciliation Logic

This minimizes risk while maximizing learning at each stage.

---

## 1️⃣ FEATURE FLAGS (Week 1)

### **Architecture: Hybrid Per-Category + Percentage-Based**

```python
DualWriteConfig:
  categories:
    CRITICAL:       {enabled: true,  percentage: 100, adapters: ["websocket", "realtime"]}
    PERFORMANCE:    {enabled: true,  percentage: 50,  adapters: ["websocket"]}
    USER_ACTIVITY:  {enabled: false, percentage: 0,   adapters: ["realtime"]}
    SYSTEM:         {enabled: true,  percentage: 100, adapters: ["websocket", "realtime"]}
    DEBUG:          {enabled: false, percentage: 0,   adapters: []}
  
  global_override: null  # Emergency kill switch
  adapter_health:
    websocket: {error_threshold: 0.05, latency_threshold_ms: 200}
    realtime:  {error_threshold: 0.05, latency_threshold_ms: 150}
```

### **Implementation Tasks**

1. Create `src/monitoring/config/dual_write_config.py`:
   - DualWriteConfig dataclass
   - Per-category configuration
   - Adapter health thresholds
   - Global override mechanism

2. Create `src/monitoring/config/config_manager.py`:
   - Load configuration from .env
   - Runtime configuration updates
   - Configuration validation
   - Change notifications

3. Update `src/monitoring/broadcaster.py`:
   - Add DualWriteConfig integration
   - Add per-category routing logic
   - Add percentage-based sampling
   - Add global override checks

4. Create admin interface (future):
   - REST API for configuration updates
   - Dashboard for monitoring
   - Audit trail for changes

### **Configuration Schema**

```yaml
# .env
DUAL_WRITE_ENABLED=true
DUAL_WRITE_CRITICAL_PERCENTAGE=100
DUAL_WRITE_PERFORMANCE_PERCENTAGE=50
DUAL_WRITE_USER_ACTIVITY_PERCENTAGE=0
DUAL_WRITE_SYSTEM_PERCENTAGE=100
DUAL_WRITE_DEBUG_PERCENTAGE=0
DUAL_WRITE_GLOBAL_OVERRIDE=null
ADAPTER_WEBSOCKET_ERROR_THRESHOLD=0.05
ADAPTER_WEBSOCKET_LATENCY_THRESHOLD_MS=200
ADAPTER_REALTIME_ERROR_THRESHOLD=0.05
ADAPTER_REALTIME_LATENCY_THRESHOLD_MS=150
```

---

## 2️⃣ CHECKSUM VALIDATION (Week 2)

### **Strategy: CRC32 + Selective SHA256**

- **CRC32**: Fast, 32-bit, for PERFORMANCE/SYSTEM/DEBUG
- **SHA256**: Secure, 256-bit, for CRITICAL/USER_ACTIVITY

### **Implementation Tasks**

1. Create `src/monitoring/validation/checksum.py`:
   - CRC32 calculation
   - SHA256 calculation
   - Category-based selection
   - Validation logic

2. Update `src/monitoring/adapters/base.py`:
   - Add checksum field to UnifiedMonitoringEvent
   - Add checksum calculation in event creation
   - Add checksum validation in adapter

3. Create `src/monitoring/validation/mismatch_handler.py`:
   - Log mismatches
   - Alert on high mismatch rates
   - Graceful degradation (don't fail events)

### **Validation Points**

- **Adapter level**: Each adapter validates outgoing checksum
- **Aggregator level**: Validates incoming checksums
- **Mismatch handling**: Log, alert, but don't fail the event

---

## 3️⃣ RECONCILIATION LOGIC (Week 3)

### **Strategy: Event-Driven with Batch Cleanup**

```python
ReconciliationStrategy:
  primary_key: sequence_id + event_type + timestamp_window(±5s)
  match_criteria:
    - exact_data_match: 100%  # CRITICAL events
    - semantic_equivalence: 95%  # PERFORMANCE events
    - presence_only: 90%  # DEBUG events
  
  out_of_order_handling:
    buffer_window: 30s
    max_delay: 5min
    strategy: "deliver_then_reconcile"
```

### **Implementation Tasks**

1. Create `src/monitoring/reconciliation/reconciler.py`:
   - Event matching logic
   - Sequence ID-based matching
   - Out-of-order handling
   - Batch reconciliation jobs

2. Create `src/monitoring/reconciliation/event_store.py`:
   - Store events for reconciliation
   - Query by sequence_id
   - Cleanup old events
   - Statistics tracking

3. Update broadcaster:
   - Add reconciliation integration
   - Add event store updates
   - Add reconciliation metrics

---

## 4️⃣ RISK MITIGATION (Week 4)

### **Circuit Breaker Pattern**

```python
CircuitBreakerConfig:
  failure_threshold: 5%
  recovery_time: 30s
  half_open_requests: 5
  latency_multiplier: 2.0x
  
  actions:
    on_trip: "fallback_to_single_adapter"
    on_recovery: "gradual_dual_write_restore"
```

### **Implementation Tasks**

1. Create `src/monitoring/circuit_breaker.py`:
   - Circuit breaker state machine
   - Failure tracking
   - Recovery logic
   - Metrics collection

2. Update broadcaster:
   - Add circuit breaker checks
   - Add fallback logic
   - Add recovery handling

3. Create monitoring dashboard:
   - Dual-write success rate per category
   - Checksum mismatch rate
   - Reconciliation lag
   - Circuit breaker state

---

## 📊 Testing Strategy

### **Unit Tests**
- Feature flag configuration and validation
- Checksum calculation and validation
- Reconciliation matching logic
- Circuit breaker state transitions

### **Integration Tests**
- End-to-end dual-write flow
- Checksum validation with adapters
- Reconciliation with real events
- Circuit breaker triggering

### **Load Tests**
- 1000 events/second dual-write
- Checksum calculation overhead
- Reconciliation performance
- Circuit breaker recovery time

---

## 🎯 Success Criteria

- [x] Phase 2.6.1 complete (63 tests passing)
- [ ] Feature flags implemented and tested
- [ ] Checksum validation working
- [ ] Reconciliation logic functional
- [ ] Circuit breaker operational
- [ ] All tests passing (target: 100+ tests)
- [ ] Zero data loss in dual-write
- [ ] <5% performance overhead

---

## 📅 Timeline

- **Week 1**: Feature flags (Nov 1-7)
- **Week 2**: Checksum validation (Nov 8-14)
- **Week 3**: Reconciliation logic (Nov 15-21)
- **Week 4**: Risk mitigation & hardening (Nov 22-28)

---

## 🔑 Key Architectural Decisions

1. **Event Sequence IDs as Primary Keys**: Leverage existing sequence_id system
2. **Graceful Degradation**: Never fail events due to dual-write issues
3. **Configurable Everything**: Make thresholds configurable without restarts
4. **Observability First**: Build monitoring before optimization

---

## 📝 Files to Create/Modify

### **Create**
- `src/monitoring/config/dual_write_config.py`
- `src/monitoring/config/config_manager.py`
- `src/monitoring/validation/checksum.py`
- `src/monitoring/validation/mismatch_handler.py`
- `src/monitoring/reconciliation/reconciler.py`
- `src/monitoring/reconciliation/event_store.py`
- `src/monitoring/circuit_breaker.py`

### **Modify**
- `src/monitoring/broadcaster.py`
- `src/monitoring/adapters/base.py`
- `.env` (add configuration)

### **Test**
- `tests/test_dual_write_config.py`
- `tests/test_checksum_validation.py`
- `tests/test_reconciliation.py`
- `tests/test_circuit_breaker.py`

---

## ✅ Next Immediate Steps

1. **Implement Feature Flags** (Week 1):
   - Create DualWriteConfig dataclass
   - Create ConfigManager
   - Update broadcaster with routing logic
   - Add comprehensive tests

2. **Validate with EXAI** before proceeding to Week 2

3. **Commit and merge** to main after Week 1 completion

---

## 📚 References

- EXAI Consultation: d3e51bcb-c3ea-4122-834f-21e602a0a9b1
- Phase 2.6.1 Documentation: PHASE2_6_1_EVENT_CLASSIFICATION_SYSTEM__2025-11-01.md
- Strategic Plan: PHASE2_6_7_STRATEGIC_IMPLEMENTATION_PLAN__2025-11-01.md

