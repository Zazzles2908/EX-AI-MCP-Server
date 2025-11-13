# Option 3: Hybrid RouterService + MiniMax M2 Implementation Plan

> **Version:** 1.0.0
> **Date:** 2025-11-11
> **Status:** Implementation Plan

> **Concept:** Combine RouterService infrastructure with MiniMax M2 intelligence for resilient, adaptive routing

---

## Executive Summary

**Hybrid Approach:** Use RouterService as the infrastructure layer (preflight, caching, logging) with MiniMax M2 as the intelligence layer (decision making), plus fallback for reliability.

**Target:** Replace 2,538 lines of complex routing with 500-600 lines of clean, hybrid architecture

---

## Architecture Overview

### Layer 1: Infrastructure (RouterService)
**File:** `src/router/service.py` (existing, 410 lines)
**Responsibilities:**
- ✅ Provider preflight checks
- ✅ Availability caching (5-minute TTL)
- ✅ JSON decision logging
- ✅ Fallback when MiniMax fails
- ✅ Environment configuration

### Layer 2: Intelligence (MiniMax M2)
**File:** `src/router/minimax_m2_router.py` (to be built, ~150 lines)
**Responsibilities:**
- AI-powered routing decisions
- Context-aware provider selection
- Adaptive learning
- Reasoning and confidence scoring

### Layer 3: Integration
**File:** `src/router/hybrid_router.py` (new, ~100 lines)
**Responsibilities:**
- Orchestrate RouterService + MiniMax M2
- Handle fallbacks gracefully
- Cache MiniMax decisions
- Monitor both systems

---

## Implementation Phases

### Phase 1: Enhance RouterService (Day 1)
**Task:** Make RouterService production-ready
- [ ] Verify preflight checks work
- [ ] Test routing cache
- [ ] Ensure JSON logging is correct
- [ ] Add basic hardcoded fallback rules
- [ ] Test in isolation

### Phase 2: Build MiniMax M2 Intelligence (Day 1-2)
**Task:** Implement the full MiniMax M2 router as designed
- [ ] Create `minimax_m2_router.py` with full 150-line implementation
- [ ] Add Anthropic SDK integration
- [ ] Implement decision caching
- [ ] Add error handling
- [ ] Test with simple prompts

### Phase 3: Hybrid Integration (Day 2-3)
**Task:** Combine both systems
- [ ] Create `hybrid_router.py`
- [ ] RouterService handles preflight + cache + logging
- [ ] MiniMax M2 makes routing decisions
- [ ] Graceful fallback to RouterService logic
- [ ] Environment flag to enable/disable MiniMax

### Phase 4: Connect to Tools (Day 3)
**Task:** Make SimpleTool use the hybrid router
- [ ] Modify `tools/simple/base.py`
- [ ] Remove complex routing logic
- [ ] Import hybrid router
- [ ] Log all routing decisions
- [ ] Test with all 29 tools

### Phase 5: Testing & Validation (Day 3-4)
**Task:** Ensure everything works
- [ ] Test normal operation (MiniMax + RouterService)
- [ ] Test fallback (RouterService only)
- [ ] Test all 29 tools route correctly
- [ ] Performance testing
- [ ] Document new architecture

---

## Technical Design

### Hybrid Flow

```
Tool Request
    ↓
Hybrid Router
    ↓
┌─────────────────────────┐
│  Check Routing Cache    │
│  (5-minute TTL)         │
└─────────────────────────┘
    ↓ Cache Hit?
┌─────────────────────────┐
│  Use Cached Decision    │
└─────────────────────────┘
    ↓ Cache Miss
┌─────────────────────────┐
│  Call MiniMax M2        │
│  (with timeout + retry) │
└─────────────────────────┘
    ↓ MiniMax Success
┌─────────────────────────┐
│  Log Decision           │
│  Cache Result           │
│  Return Routing Info    │
└─────────────────────────┘
    ↓ MiniMax Fails
┌─────────────────────────┐
│  Use RouterService      │
│  Fallback Rules         │
│  (web_search=glm, etc.) │
│  Log Fallback           │
└─────────────────────────┘
    ↓
Provider Execution
```

### Configuration

```python
# .env
ROUTER_MODE=hybrid  # hybrid | minimax | basic
MINIMAX_ENABLED=true
MINIMAX_TIMEOUT=5
MINIMAX_RETRY=2
ROUTER_CACHE_TTL=300
ROUTER_DIAGNOSTICS=true
```

### Decision Structure

```python
{
    "provider": "GLM",
    "model": "glm-4.6",
    "reasoning": "Web search requested, GLM supports it better",
    "confidence": 0.95,
    "execution_path": "STANDARD",
    "source": "minimax",  # or "fallback"
    "cached": false,
    "timestamp": "2025-11-11T21:30:00Z"
}
```

---

## File Changes

### Modified Files
- `src/router/service.py` - Add basic fallback rules
- `src/router/minimax_m2_router.py` - Full implementation
- `tools/simple/base.py` - Use hybrid router

### New Files
- `src/router/hybrid_router.py` - Main orchestrator
- `src/router/minimax_client.py` - Anthropic SDK wrapper
- `config/routing_config.yaml` - Routing configuration

### Removed Files (after migration)
- `src/providers/capability_router.py` (434 lines)
- `src/providers/registry_selection.py` (552 lines)
- **Total removal: 986 lines**

### Code Reduction
```
Current routing system:  2,538 lines
Hybrid system:             600 lines
Net reduction:           1,938 lines (76% reduction)
```

---

## Benefits

### 1. **Intelligent & Resilient**
- AI makes smart routing decisions
- Falls back gracefully if AI fails
- Caches decisions for performance

### 2. **Production-Ready**
- Won't die if MiniMax is unavailable
- Structured logging for debugging
- Environment-configurable

### 3. **Simplified Architecture**
- 76% less code than current system
- Clear separation of concerns
- Easy to understand and maintain

### 4. **Future-Proof**
- Add new providers via config
- AI learns routing patterns
- Easy to upgrade/extend

---

## Risks & Mitigation

### Risk 1: MiniMax API Downtime
**Mitigation:** Automatic fallback to RouterService rules
**Detection:** Log all fallbacks, alert if >10% fallback rate

### Risk 2: MiniMax Decisions Wrong
**Mitigation:** Confidence threshold (require >0.7 confidence)
**Detection:** Monitor success/failure rates per decision source

### Risk 3: Performance Degradation
**Mitigation:** 5-minute cache TTL, async calls
**Detection:** Monitor routing decision latency

### Risk 4: Cost Overrun
**Mitigation:** Cache all decisions, batch monitoring calls
**Detection:** Track MiniMax API calls per day

---

## Testing Strategy

### Unit Tests
- [ ] RouterService preflight
- [ ] MiniMax M2 decision parsing
- [ ] Hybrid router orchestration
- [ ] Fallback logic

### Integration Tests
- [ ] All 29 tools route correctly
- [ ] Web search goes to GLM
- [ ] Thinking mode goes to Kimi
- [ ] Vision works with both
- [ ] File uploads route correctly

### Failure Tests
- [ ] MiniMax timeout → fallback works
- [ ] MiniMax error → fallback works
- [ ] Cache works correctly
- [ ] No infinite loops

### Performance Tests
- [ ] Routing decision < 100ms
- [ ] Fallback decision < 10ms
- [ ] Cache hit rate > 80%
- [ ] No memory leaks

---

## Success Metrics

### Code Quality
- [ ] 76% line reduction achieved
- [ ] All tests pass
- [ ] Code coverage > 85%

### Performance
- [ ] Routing latency < 100ms
- [ ] Cache hit rate > 80%
- [ ] No timeout errors

### Reliability
- [ ] Fallback rate < 5% (healthy)
- [ ] Zero crashes during testing
- [ ] All 29 tools work

### Functionality
- [ ] Web search always goes to GLM
- [ ] Thinking mode prefers Kimi
- [ ] Smart routing adapts to context
- [ ] Clear logging for debugging

---

## Timeline

**Total: 3-4 days**

- **Day 1:** RouterService enhancement + MiniMax M2 build
- **Day 2:** Hybrid integration + basic testing
- **Day 3:** Tool connection + full testing
- **Day 4:** Performance tuning + documentation

---

## Next Steps

1. **Review this plan** with team
2. **Get MiniMax M2 API key** (already have it)
3. **Start Phase 1:** Enhance RouterService
4. **Measure progress** daily
5. **Deploy when ready**

---

**Ready to build the "smarter AND stronger" system? Let's do this!**

---

> **Document Version:** 1.0
> **Last Updated:** 2025-11-11
> **Status:** Ready for Implementation
