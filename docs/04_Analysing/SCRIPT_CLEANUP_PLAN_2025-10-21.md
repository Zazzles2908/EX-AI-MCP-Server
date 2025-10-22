# Script Cleanup Plan - 2025-10-21
**Purpose:** Systematic script audit and cleanup  
**Method:** Evidence-based categorization

---

## 🎯 Scripts Actually Used in Production

### **CRITICAL - Docker Entry Points**
✅ **KEEP** - Referenced in Dockerfile/docker-compose.yml
1. `scripts/ws/run_ws_daemon.py` - Docker CMD, main entry point
2. `scripts/health_check.py` - Docker HEALTHCHECK
3. `scripts/run_ws_shim.py` - MCP shim (Augment Code connection)

### **CRITICAL - WebSocket Tools**
✅ **KEEP** - Active WebSocket utilities
4. `scripts/ws/health_check.py` - WebSocket health validation
5. `scripts/ws/ws_status.py` - Status checking
6. `scripts/ws/ws_chat_once.py` - Single chat test
7. `scripts/ws/ws_chat_roundtrip.py` - Roundtrip test
8. `scripts/ws/ws_chat_analyze_files.py` - File analysis test
9. `scripts/ws/ws_chat_review_once.py` - Code review test

### **OPERATIONAL - Maintenance**
✅ **KEEP** - Regular operations
10. `scripts/maintenance/glm_files_cleanup.py` - File cleanup
11. `scripts/health/validate_system_health.py` - Health validation

### **DEVELOPMENT - Testing Infrastructure**
✅ **KEEP** - Active testing
12. `scripts/testing/run_tests.py` - Test runner
13. `scripts/testing/benchmark_performance.py` - Performance benchmarking
14. `scripts/testing/monitor_24h_stability.py` - Stability monitoring
15. `scripts/testing/retrieve_exai_conversation.py` - Conversation retrieval

### **DEVELOPMENT - Validation**
✅ **KEEP** - Configuration validation
16. `scripts/audit/audit_env_vars.py` - Environment variable audit
17. `scripts/validate_timeout_hierarchy.py` - Timeout validation
18. `scripts/validate_mcp_configs.py` - MCP config validation
19. `scripts/validate_context_engineering.py` - Context validation

### **AUTOMATION - CI/CD**
✅ **KEEP** - GitHub Actions
20. `scripts/bump_version.py` - Version bumping (used in .github/workflows/auto-version.yml)

---

## ⚠️ Scripts to Review - Potentially Redundant

### **Diagnostic Tools - Overlap?**
21. `scripts/exai_diagnose.py` (2,703 bytes) - EXAI diagnostics
22. `scripts/diagnose_mcp.py` (12,932 bytes) - MCP diagnostics
23. `scripts/diagnostics/backbone_tracer.py` (2,596 bytes) - Call graph tracer

**Question:** Do we need 3 diagnostic scripts? Can we consolidate?

### **Documentation Tools**
24. `scripts/create_documentation.py` (7,058 bytes) - Doc generation
25. `scripts/evidence_map.py` (1,633 bytes) - Evidence mapping

**Question:** Are these actively used or one-time scripts?

### **Code Review Tools**
26. `scripts/kimi_code_review.py` (18,994 bytes) - Kimi-powered code review

**Question:** Is this redundant with codereview_EXAI-WS tool?

### **MCP Tools**
27. `scripts/mcp_tool_sweep.py` (14,397 bytes) - Tool discovery
28. `scripts/mcp_server_wrapper.py` (5,321 bytes) - MCP wrapper

**Question:** Are these still needed or superseded by server.py?

### **Cleanup Scripts**
29. `scripts/cleanup_phase3.py` (6,607 bytes) - Phase 3 cleanup

**Question:** One-time migration script? Can be archived?

### **Strategic Guidance**
30. `scripts/get_strategic_guidance.py` (4,436 bytes) - Strategic planning

**Question:** Is this redundant with planner_EXAI-WS tool?

### **Metrics**
31. `scripts/metrics_server.py` (3,126 bytes) - Metrics server

**Question:** Is this superseded by src/monitoring/metrics.py?

### **Load Testing**
32. `scripts/load_testing/config.py` (3,353 bytes)
33. `scripts/load_testing/__init__.py` (441 bytes)

**Question:** Is load testing infrastructure complete or abandoned?

### **Stress Testing**
34. `scripts/stress_test_exai.py` (13,468 bytes) - EXAI stress testing

**Question:** Active or one-time test?

### **Migration Scripts**
35. `scripts/update_p0_8_supabase.py` (1,343 bytes) - Supabase migration

**Question:** One-time migration? Can be archived?

---

## 📋 Cleanup Actions

### **Phase 1: Archive One-Time Scripts**
Move to `scripts/archive/migrations_2025-10-21/`:
- `cleanup_phase3.py` - Phase 3 cleanup (one-time)
- `update_p0_8_supabase.py` - Supabase migration (one-time)

### **Phase 2: Consolidate Diagnostic Tools**
**Decision:** Keep `diagnose_mcp.py` (most comprehensive), archive others
- ✅ KEEP: `diagnose_mcp.py` (12,932 bytes) - Most comprehensive
- 🗄️ ARCHIVE: `exai_diagnose.py` (2,703 bytes) - Smaller, less features
- 🗄️ ARCHIVE: `diagnostics/backbone_tracer.py` (2,596 bytes) - Specialized, rarely used

### **Phase 3: Evaluate Tool Redundancy**
**Compare with EXAI tools:**
- `kimi_code_review.py` vs `codereview_EXAI-WS` - Check if redundant
- `get_strategic_guidance.py` vs `planner_EXAI-WS` - Check if redundant
- `mcp_tool_sweep.py` - Check if superseded by server.py tool discovery

### **Phase 4: Consolidate Documentation Tools**
**Decision:** Keep if actively used, archive if one-time
- Review `create_documentation.py` usage
- Review `evidence_map.py` usage

### **Phase 5: Load Testing Infrastructure**
**Decision:** Complete or remove
- If incomplete: Remove `scripts/load_testing/`
- If active: Document usage and keep

### **Phase 6: Metrics Server**
**Decision:** Check if superseded
- Compare `scripts/metrics_server.py` with `src/monitoring/metrics.py`
- Keep only one implementation

---

## 🎯 Expected Results

**Before:**
- 35 scripts (excluding archived test scripts)
- Unclear which are used
- Potential redundancy

**After:**
- ~20 core scripts (production + development)
- ~15 scripts archived (one-time + redundant)
- Clear documentation of what's used

**Reduction:** ~43% fewer active scripts

---

## 📊 Next Steps

1. ✅ Create this plan
2. ⏳ Archive one-time migration scripts
3. ⏳ Consolidate diagnostic tools
4. ⏳ Check tool redundancy with EXAI tools
5. ⏳ Evaluate documentation tools
6. ⏳ Review load testing infrastructure
7. ⏳ Consolidate metrics implementation
8. ⏳ Update documentation with final script list

---

**Status:** Plan created, ready for systematic execution

