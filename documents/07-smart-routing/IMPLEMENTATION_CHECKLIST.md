# Implementation Checklist - Smart Routing
# Implementation Checklist - Smart Routing

> **Version:** 1.0.0
> **Date:** 2025-11-10
> **Status:** IMPLEMENTATION GUIDE

---

## Executive Summary

Complete step-by-step checklist for implementing smart routing:
1. Fix provider capabilities (GLM/Kimi context windows, web search)
2. Build EXAI-MCP orchestrator (replaces 29 tools with intelligent interface)
3. Integrate MiniMax M2 smart router (2,500 lines → 150 lines)
4. Test and deploy

---

## Phase 1: Fix Provider Capabilities (Week 1)

### 1.1 Update Context Windows

**GLM-4.6:** 200,000 tokens (not 128K)
**Kimi K2:** 256,000 tokens (not 128K)

**Files to modify:**
- src/providers/capability_router.py (lines 38-66)
- src/providers/glm_config.py
- src/providers/kimi_config.py

**Tasks:**
- [ ] Update GLM max_tokens: 200000
- [ ] Update Kimi max_tokens: 256000
- [ ] Verify model lists are accurate
- [ ] Test context windows

### 1.2 Fix Web Search Support

**Issue:** Code says Kimi NO web search, user says YES

**Tasks:**
- [ ] Research Kimi web search support
- [ ] Update capability_router.py:45 if confirmed
- [ ] Test web search with both providers
- [ ] Update routing logic

### 1.3 Update Model Lists

**GLM Models:**
- glm-4.6 (200K) - PRIMARY
- glm-4.5 (128K)
- glm-4.5-flash
- glm-4.5v (65K, vision)

**Kimi Models:**
- kimi-k2-thinking (256K) - PRIMARY
- kimi-k2-thinking-turbo (256K)
- kimi-k2-0905-preview (256K)
- kimi-k2-0711-preview (128K)

**Tasks:**
- [ ] Verify all models exist
- [ ] Test each model availability
- [ ] Document capabilities

---

## Phase 2: Build EXAI-MCP Orchestrator (Week 2-3)

### 2.1 Create Orchestrator

**New File:** src/orchestrator/exai_orchestrator.py

**Components:**
- IntentRecognitionEngine (parse user goals)
- ToolOrchestrator (execute automatically)
- NaturalLanguageInterface (no tool selection)

**Tasks:**
- [ ] Build orchestrator class
- [ ] Connect to EXAI-MCP WebSocket (port 3000)
- [ ] Implement intent recognition
- [ ] Implement tool chaining

### 2.2 Replace Tool Registry

**Current:** 33 tools, users choose which to use
**New:** 1 orchestrator, users describe goals

**Tasks:**
- [ ] Remove get_model_category() from all tools
- [ ] Remove tool selection UI
- [ ] Create intent-based interface
- [ ] Users say "debug my code" not "use debug tool"

### 2.3 Test Orchestrator

**Tasks:**
- [ ] Unit tests for intent recognition
- [ ] Integration tests for tool chaining
- [ ] Load tests for WebSocket
- [ ] User acceptance tests

---

## Phase 3: MiniMax M2 Smart Router (Week 4)

### 3.1 Implement Router

**New File:** src/router/minimax_m2_router.py

**Benefits:**
- 94% code reduction (2,500 lines → 150 lines)
- Intelligent routing
- Easy to extend
- No hardcoded logic

**Tasks:**
- [ ] Create MiniMax M2 router class
- [ ] Build routing prompt
- [ ] Add caching (5-minute TTL)
- [ ] Test routing decisions

### 3.2 Replace Current Routing

**Location:** tools/simple/base.py:369-396

**Tasks:**
- [ ] Remove category-based routing
- [ ] Add MiniMax M2 routing
- [ ] Test routing accuracy
- [ ] Test performance

---

## Phase 4: Testing & Deployment (Week 5-6)

### 4.1 End-to-End Testing

**Test Scenarios:**
1. "Debug my Python API with timeouts"
2. "Review code for security issues"
3. "Analyze database performance"
4. "Refactor function for performance"
5. "Generate tests for module"

**Success Criteria:**
- [ ] 90% scenarios complete successfully
- [ ] Average time to solution < 5 minutes
- [ ] User satisfaction > 8/10

### 4.2 Gradual Rollout

**Strategy:** Feature flags

**Phases:**
- [ ] Phase 1: Internal testing (5% traffic)
- [ ] Phase 2: Power users (20% traffic)
- [ ] Phase 3: General availability (50% traffic)
- [ ] Phase 4: Full deployment (100% traffic)

### 4.3 Success Metrics

**User Experience:**
- Task completion rate: 70% → 90%
- Time to solution: 10 min → 3 min
- User satisfaction: 6/10 → 8/10
- Error rate: 15% → 5%

**System Performance:**
- Routing accuracy: 60% → 95%
- Response time: 5 sec → 3 sec
- WebSocket uptime: 95% → 99.9%

**Business Impact:**
- Support tickets: 100/week → 50/week
- User adoption: N/A → 80%
- Feature usage: 50% → 90%

---

## File Changes Summary

**Create:**
- src/orchestrator/exai_orchestrator.py
- src/router/minimax_m2_router.py
- src/utils/intent_parser.py

**Modify:**
- src/providers/capability_router.py
- tools/simple/base.py
- src/providers/glm_config.py
- src/providers/kimi_config.py

**Remove:**
- tools/models.py (ToolModelCategory)
- Category methods from all tools
- registry_selection.py (optional - keep fallback)

---

## Risk Mitigation

**Risk 1: Capability Misinformation**
- Verify with API documentation
- Test each model
- Keep fallback system

**Risk 2: WebSocket Bottleneck**
- Load test performance
- Implement connection pooling
- Monitor resource usage

**Risk 3: MiniMax M2 Costs**
- Aggressive caching
- Set cost limits
- Fallback to local routing

**Risk 4: User Adoption**
- Clear documentation
- Onboarding guide
- Gradual migration

**Risk 5: Performance Regression**
- Measure baseline
- Continuous monitoring
- Quick rollback

---

## Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Fix Capabilities | Updated contexts, verified web search |
| 2-3 | Build Orchestrator | EXAI orchestrator, intent recognition |
| 4 | MiniMax Router | Smart router, caching |
| 5 | Testing | E2E tests, UAT |
| 6 | Deployment | Gradual rollout, monitoring |

**Total:** 6 weeks
**Team:** 2-3 developers
**Risk:** Medium

---

## Next Steps

1. Review checklist with team
2. Prioritize phases
3. Assign tasks
4. Begin Phase 1
5. Report progress weekly

**Goal:** Users describe WHAT they want, system handles HOW

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-10
**Status:** Implementation Guide - Ready for Execution
