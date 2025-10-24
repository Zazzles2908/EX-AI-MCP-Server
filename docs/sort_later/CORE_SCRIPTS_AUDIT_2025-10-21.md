# Core Scripts Audit - 2025-10-21
**Purpose:** Identify essential scripts vs bloat  
**Action Taken:** Archived 41 test scripts to `scripts/archive/test_scripts_2025-10-21/`

---

## Cleanup Summary

**Before:** 48 test scripts scattered across scripts/, scripts/testing/, scripts/diagnostics/  
**After:** 41 test scripts archived, 7 remain in archive subdirectories  
**Reduction:** 85% of test scripts removed from active directories

---

## Core Scripts Remaining (Essential)

### **Entry Points (CRITICAL)**
1. `run_ws_shim.py` - Main MCP entry point for Augment Code
2. `scripts/ws/run_ws_daemon.py` - WebSocket daemon

### **Health & Diagnostics (ESSENTIAL)**
3. `health_check.py` - System health monitoring
4. `scripts/ws/health_check.py` - WebSocket health
5. `scripts/ws/ws_status.py` - WebSocket status
6. `scripts/health/validate_system_health.py` - Comprehensive health validation
7. `scripts/diagnostics/backbone_tracer.py` - System tracing

### **Operational Scripts (NEEDED)**
8. `scripts/maintenance/glm_files_cleanup.py` - File cleanup
9. `scripts/audit/audit_env_vars.py` - Environment validation

### **Development Tools (USEFUL)**
10. `bump_version.py` - Version management
11. `create_documentation.py` - Doc generation
12. `evidence_map.py` - Evidence mapping
13. `exai_diagnose.py` - EXAI diagnostics
14. `get_strategic_guidance.py` - Strategic planning
15. `kimi_code_review.py` - Code review
16. `mcp_server_wrapper.py` - MCP wrapper
17. `mcp_tool_sweep.py` - Tool discovery
18. `metrics_server.py` - Metrics collection
19. `stress_test_exai.py` - Load testing
20. `validate_context_engineering.py` - Context validation
21. `validate_mcp_configs.py` - Config validation
22. `validate_timeout_hierarchy.py` - Timeout validation

### **WebSocket Tools (ACTIVE)**
23. `scripts/ws/ws_chat_once.py` - Single chat test
24. `scripts/ws/ws_chat_roundtrip.py` - Roundtrip test
25. `scripts/ws/ws_chat_analyze_files.py` - File analysis
26. `scripts/ws/ws_chat_review_once.py` - Code review

### **Testing Infrastructure (KEEP)**
27. `scripts/testing/run_tests.py` - Test runner
28. `scripts/testing/benchmark_performance.py` - Performance benchmarking
29. `scripts/testing/monitor_24h_stability.py` - Stability monitoring
30. `scripts/testing/retrieve_exai_conversation.py` - Conversation retrieval

---

## Scripts to Review Further

### **Potentially Redundant**
- `cleanup_phase3.py` - What phase? Is this obsolete?
- `diagnose_mcp.py` vs `exai_diagnose.py` - Duplicate functionality?
- `update_p0_8_supabase.py` - One-time migration script?

### **Archive Candidates**
- `scripts/archive/diagnostics_sep_2025/` - 6 old diagnostic scripts
- `scripts/archive/docs_cleanup_2025-07/` - 8 doc cleanup scripts
- `scripts/archive/docs_one_time/` - 2 one-time doc scripts
- `scripts/archive/testing_fixes_2025-10/` - 7 old test scripts (already archived)

---

## Next Actions

1. ✅ Archive test scripts (COMPLETE - 41 scripts archived)
2. ⏳ Review "potentially redundant" scripts
3. ⏳ Consolidate archive subdirectories
4. ⏳ Create script dependency map
5. ⏳ Document which scripts are actually used in production

---

## Production Script Usage (To Verify)

**Question:** Which scripts are actually called in production?

**Need to check:**
- Docker entrypoint
- Systemd services
- Cron jobs
- CI/CD pipelines
- Manual operations

**Method:** Search for script references in:
- Dockerfile
- docker-compose.yml
- .github/workflows/
- README.md
- docs/

---

## Status

**Cleanup Progress:** 40% complete
- ✅ Test scripts archived
- ⏳ Redundant scripts identified
- ⏳ Dependency mapping pending
- ⏳ Production usage verification pending

