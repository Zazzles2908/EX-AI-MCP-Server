# Legacy Scripts Archive - 2025-10-02

**Purpose:** Archive of redundant BACKUP/NEW/OLD scripts removed during agentic transformation cleanup  
**Date:** 2025-10-02  
**Branch:** docs/wave1-complete-audit  
**Related:** AGENTIC_TRANSFORMATION_ROADMAP.md

---

## Files Archived (18 total)

### Documentation (1 file)
1. `README_NEW.md` - From `docs/current/development/phase2/`
   - **Reason:** Duplicate/experimental README
   - **Current Version:** `docs/current/development/phase2/README.md`

### Provider Layer (5 files)
2. `glm_BACKUP.py` - From `src/providers/`
   - **Reason:** Backup from Phase 3 refactoring
   - **Current Version:** `src/providers/glm.py`

3. `kimi_BACKUP.py` - From `src/providers/`
   - **Reason:** Backup from Phase 3 refactoring
   - **Current Version:** `src/providers/kimi.py`

4. `registry_BACKUP.py` - From `src/providers/`
   - **Reason:** Backup from registry refactoring
   - **Current Version:** `src/providers/registry.py`

5. `registry_NEW.py` - From `src/providers/`
   - **Reason:** Experimental new registry (merged into current)
   - **Current Version:** `src/providers/registry.py`

### Server Layer (4 files)
6. `request_handler_BACKUP.py` - From `src/server/handlers/`
   - **Reason:** Backup from Phase 1.3 refactoring
   - **Current Version:** `src/server/handlers/request_handler.py`

7. `request_handler_OLD_1345_LINES.py` - From `src/server/handlers/`
   - **Reason:** Old monolithic version (1,345 lines)
   - **Current Version:** `src/server/handlers/request_handler.py` (modular)

8. `provider_config_BACKUP.py` - From `src/server/providers/`
   - **Reason:** Backup from Phase 3.4 refactoring
   - **Current Version:** `src/server/providers/provider_config.py`

9. `provider_config_OLD_290_LINES.py` - From `src/server/providers/`
   - **Reason:** Old version (290 lines)
   - **Current Version:** `src/server/providers/provider_config.py`

### Tools Layer (7 files)
10. `workflow_mixin_BACKUP.py` - From `tools/workflow/`
    - **Reason:** Backup from Phase 1 refactoring
    - **Current Version:** `tools/workflow/workflow_mixin.py`

11. `analyze_BACKUP.py` - From `tools/workflows/`
    - **Reason:** Backup from Phase 2.3 refactoring
    - **Current Version:** `tools/workflows/analyze.py`

12. `codereview_BACKUP.py` - From `tools/workflows/`
    - **Reason:** Backup from Phase 2.7 refactoring
    - **Current Version:** `tools/workflows/codereview.py`

13. `consensus_BACKUP.py` - From `tools/workflows/`
    - **Reason:** Backup from Phase 2.1 refactoring
    - **Current Version:** `tools/workflows/consensus.py`

14. `secaudit_BACKUP.py` - From `tools/workflows/`
    - **Reason:** Backup from Phase 2.4 refactoring
    - **Current Version:** `tools/workflows/secaudit.py`

15. `thinkdeep_BACKUP.py` - From `tools/workflows/`
    - **Reason:** Backup from Phase 2.2 refactoring
    - **Current Version:** `tools/workflows/thinkdeep.py`

16. `tracer_BACKUP.py` - From `tools/workflows/`
    - **Reason:** Backup from Phase 2.5 refactoring
    - **Current Version:** `tools/workflows/tracer.py`

### Utils Layer (2 files)
17. `conversation_memory_BACKUP.py` - From `utils/`
    - **Reason:** Backup from Phase 1.5 refactoring
    - **Current Version:** `utils/conversation_memory.py`

18. `conversation_memory_NEW.py` - From `utils/`
    - **Reason:** Experimental new version (merged into current)
    - **Current Version:** `utils/conversation_memory.py`

---

## Impact Assessment

**Lines of Code Removed:** ~8,000+ lines of dead code  
**Disk Space Saved:** ~350 KB  
**Codebase Clarity:** Significantly improved - no more confusion about which version is active

---

## Verification

All archived files were verified as:
1. ✅ Not imported by any active code
2. ✅ Superseded by current production versions
3. ✅ System remains fully functional after removal

**Server Status:** ✅ Running successfully  
**Tests:** ✅ All passing  
**Backward Compatibility:** ✅ 100% maintained

---

## Recovery Instructions

If any archived file is needed:
```bash
# Copy from archive back to original location
cp docs/archive/legacy-scripts/2025-10-02/<filename> <original-path>

# Example:
cp docs/archive/legacy-scripts/2025-10-02/glm_BACKUP.py src/providers/
```

---

## Next Steps

With cleanup complete, proceed to **Phase 1: Agentic Foundation**:
1. Add confidence parameters to workflow tools
2. Create PlanWorkflowTool (AI Manager)
3. Implement early termination logic
4. Update system prompts

See: `docs/AGENTIC_TRANSFORMATION_ROADMAP.md`

---

**Archive Status:** ✅ COMPLETE  
**Cleanup Status:** ✅ VERIFIED  
**Ready for:** Phase 1 Implementation

