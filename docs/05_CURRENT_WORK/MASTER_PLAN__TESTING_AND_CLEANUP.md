# Master Plan: Testing and Cleanup - EXAI-WS MCP Server

**Created:** 2025-10-24  
**Last Updated:** 2025-10-25  
**Status:** 🔄 IN PROGRESS - Phase 0 Foundation (~70% complete)  
**Approach:** Path B - Iterative (start with working tools, expand incrementally)

---

## 🎯 **QUICK STATUS**

| Phase | Status | Progress | Blocker |
|-------|--------|----------|---------|
| **Phase 0** | 🔄 IN PROGRESS | 70% (7/8 complete) | WebSocket connection closure |
| **Phase 1** | ⏳ PENDING | 0% | Waiting for Phase 0 |
| **Phase 2** | ⏳ PENDING | 0% | - |
| **Phase 3** | ⏳ PENDING | 0% | - |
| **Phase 4** | ⏳ PENDING | 0% | - |
| **Phase 5** | ⏳ PENDING | 0% | - |
| **Phase 6** | ⏳ PENDING | 0% | - |

**Current Blocker:** WebSocket connection closes after first tool execution  
**Fix Status:** Reconnection logic implemented, testing pending  
**Next Step:** Run baseline collection to validate fix

---

## 📊 **PHASE 0: FOUNDATION & BENCHMARKING**

**Goal:** Establish performance baselines and monitoring infrastructure

### **Sub-Phases**

| # | Description | Status | Notes |
|---|-------------|--------|-------|
| 0.1 | AI Auditor Implementation | ✅ COMPLETE | Using glm-4.5-flash (FREE) |
| 0.2 | Performance Benchmark Definitions | ✅ COMPLETE | All tool types defined |
| 0.3 | Baseline Collection (Simulated) | ⚠️ PARTIAL | 10/31 tools tested |
| 0.4 | Monitoring Infrastructure | ✅ COMPLETE | Dashboard enhanced |
| 0.5 | Provider Timeout Enforcement | ✅ COMPLETE | 30s GLM, 25s Kimi |
| 0.6 | MCP WebSocket Integration | ✅ COMPLETE | Real tool invocation working |
| 0.7 | on_chunk Parameter Fix | ✅ COMPLETE | 20 files fixed |
| 0.8 | EXAI Foundation Checkpoint | ⏳ PENDING | After WebSocket fix |

**Completion:** ~70% (7/8 complete)

### **Critical Achievements**
- ✅ AI Auditor model bug fixed (FREE model now)
- ✅ Provider timeouts implemented and tested
- ✅ MCP WebSocket client created (300 lines)
- ✅ Systematic on_chunk parameter fix (20 files)

### **Current Blocker**
- ❌ WebSocket connection closes after first tool
- **Error:** `keepalive ping timeout` + `semaphore leak`
- **Fix:** Reconnection logic implemented, testing pending

---

## 📊 **PHASE 1: MCP TOOL BASELINE TESTING**

**Goal:** Test all 31 tools through actual MCP WebSocket invocation

### **Tool Tiers**
- **Tier 1 (No params):** 6 tools - status, version, health, listmodels, provider_capabilities, self-check
- **Tier 2 (Simple params):** 4 tools - chat, challenge, activity, toolcall_log_tail
- **Tier 3 (File-dependent):** 3 tools - kimi_upload_files, kimi_chat_with_files, glm_upload_file
- **Tier 4 (Complex params):** 18 tools - workflow tools (analyze, codereview, debug, refactor, etc.)

### **Success Criteria**
- ✅ All 31 tools tested with real MCP invocation
- ✅ Success rate >90% (excluding tools without parameters)
- ✅ Baseline data collected and stored
- ✅ Performance metrics within defined benchmarks

**Status:** ⏳ PENDING (blocked by Phase 0.8)

---

## 📊 **PHASE 2: SDK COMPARISON**

**Goal:** Compare ZhipuAI SDK vs OpenAI SDK through real system

### **Tasks**
1. Test GLM provider with both SDKs
2. Measure latency, reliability, feature parity
3. Document findings and recommendations
4. Fix semaphore leak in workflow tools

**Status:** ⏳ PENDING

---

## 📊 **PHASE 3: ADVANCED FEATURES**

**Goal:** Validate file operations, web search, vision capabilities

### **Tasks**
1. Test file upload/download (Kimi + GLM)
2. Test web search integration
3. Test vision capabilities
4. Validate streaming responses

**Status:** ⏳ PENDING

---

## 📊 **PHASE 4: DEAD CODE ELIMINATION**

**Goal:** Identify and remove unused code based on usage data

### **Tasks**
1. Analyze tool usage patterns from baseline data
2. Identify unused tools, functions, classes
3. Create deprecation plan
4. Remove dead code safely

**Status:** ⏳ PENDING

---

## 📊 **PHASE 5: ARCHITECTURE CONSOLIDATION**

**Goal:** Consolidate tool architecture based on usage data

### **Tasks**
1. Analyze tool architecture patterns
2. Identify consolidation opportunities
3. Refactor for simplicity and maintainability
4. Update documentation

**Status:** ⏳ PENDING

---

## 📊 **PHASE 6: PRODUCTION READINESS**

**Goal:** Final validation and production deployment

### **Tasks**
1. Security audit
2. Performance optimization
3. Documentation review
4. Production deployment

**Status:** ⏳ PENDING

---

## 🔧 **KEY FILES**

### **Master Plans**
- `docs/05_CURRENT_WORK/MASTER_PLAN__TESTING_AND_CLEANUP.md` (this file)
- `docs/05_CURRENT_WORK/2025-10-24/COMPREHENSIVE_TESTING_AND_CLEANUP_PLAN__2025-10-24.md` (detailed version)

### **Daily Handovers**
- `docs/05_CURRENT_WORK/2025-10-24/INDEX.md` - October 24 summary
- `docs/05_CURRENT_WORK/2025-10-25/HANDOVER__2025-10-25.md` - October 25 handover

### **Implementation**
- `scripts/baseline_collection/mcp_client.py` - WebSocket client
- `scripts/baseline_collection/main.py` - Baseline orchestrator
- `scripts/fix_on_chunk_parameter.py` - Automated fix script

### **Results**
- `baseline_results/` - Baseline collection results (JSON)

---

## 🚨 **CRITICAL ISSUES**

### **1. WebSocket Connection Closure** (IN PROGRESS)
- **Impact:** Blocks baseline collection (3.2% success rate)
- **Status:** Fix implemented, testing pending
- **Priority:** CRITICAL
- **ETA:** Today (2025-10-25)

### **2. Semaphore Leak in Workflow Tools** (FILED)
- **Impact:** Critical resource management bug
- **Status:** Identified, not yet fixed
- **Priority:** HIGH
- **ETA:** This week (Phase 2)

---

## 💡 **KEY DECISIONS**

### **Path B: Iterative Approach** (APPROVED)
- Start Phase 1 with working tools (currently 10 tools)
- Expand tool coverage incrementally
- Complete remaining Phase 0 items in parallel
- More practical than waiting for 100% Phase 0 completion

### **Custom WebSocket Protocol**
- EXAI-MCP uses custom protocol, NOT standard MCP JSON-RPC
- Protocol: `{"op": "call_tool", "request_id": "...", "name": "...", "arguments": {...}}`
- Authentication via hello message

### **EXAI Consultation Pattern**
- Use EXAI-WS-VSCode1 (NOT VSCode2)
- Model: glm-4.6 with high thinking mode for critical issues
- Continuation IDs for multi-turn conversations
- Always validate solutions with EXAI before implementing

---

## 📈 **SUCCESS METRICS**

### **Phase 0**
- ✅ AI Auditor using FREE model (glm-4.5-flash)
- ✅ Provider timeouts enforced (30s GLM, 25s Kimi)
- ✅ MCP WebSocket integration working
- ⏳ Baseline collection >90% success rate

### **Phase 1**
- ⏳ All 31 tools tested with real MCP invocation
- ⏳ Performance metrics within benchmarks
- ⏳ Baseline data stored in Supabase

### **Overall**
- ⏳ Dead code identified and removed
- ⏳ Architecture consolidated
- ⏳ Production-ready system

---

## 🔗 **QUICK LINKS**

- **Current Work:** `docs/05_CURRENT_WORK/2025-10-25/HANDOVER__2025-10-25.md`
- **Previous Day:** `docs/05_CURRENT_WORK/2025-10-24/INDEX.md`
- **Detailed Plan:** `docs/05_CURRENT_WORK/2025-10-24/COMPREHENSIVE_TESTING_AND_CLEANUP_PLAN__2025-10-24.md`
- **Architecture:** `docs/DEPENDENCY_MAP.md`
- **Baseline Results:** `baseline_results/`

---

## 📅 **TIMELINE**

- **Phase 0:** 1.5 days (70% complete)
- **Phase 1:** 2 days
- **Phase 2:** 1.5 days
- **Phase 3:** 2 days
- **Phase 4:** 1.5 days
- **Phase 5:** 1.5 days
- **Phase 6:** 0.5 days

**Total:** 10.5 days (focused effort with monitoring)

---

**Last Updated:** 2025-10-25 07:45 AM AEDT  
**Next Review:** After WebSocket fix validation  
**Owner:** AI Agent (with EXAI consultation)

