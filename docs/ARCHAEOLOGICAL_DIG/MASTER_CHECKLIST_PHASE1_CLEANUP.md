# ARCHAEOLOGICAL DIG - PHASE 1 CLEANUP CHECKLIST
**Branch:** archaeological-dig/phase1-discovery-and-cleanup  
**Started:** 2025-10-10 6:40 PM AEDT  
**Purpose:** Execute consolidation strategy from Phase 1 investigations  
**Parent:** MASTER_CHECKLIST_PHASE1.md (Tasks 1.1-1.10 COMPLETE)

---

## 🎯 PHASE 1 CLEANUP GOAL

Execute Option 2 (Full Cleanup Before Refactoring):
1. Delete orphaned/empty directories
2. Archive planned infrastructure
3. Reorganize utils/ folder
4. Then proceed to SimpleTool refactoring

**Based on:** CONSOLIDATION_STRATEGY.md (created from Tasks 1.1-1.10)

---

## ✅ PREREQUISITES (COMPLETE)

- [x] Phase 1 Discovery Complete (Tasks 1.1-1.10) - 100%
- [x] All components classified (ACTIVE/ORPHANED/PLANNED)
- [x] Consolidation strategy created
- [x] User approval obtained for Option 2

---

## 📋 PHASE 1.A: DELETE ORPHANED DIRECTORIES

**Priority:** HIGH  
**Impact:** LOW (no code uses these)  
**Risk:** NONE (orphaned code)  
**Estimated Time:** 30 minutes

### Task 1.A.1: Verify Zero Imports ✅ COMPLETE

- [x] Verify src/conf/ has 0 imports (CONFIRMED)
- [x] Verify src/config/ has 0 imports (CONFIRMED)
- [x] Verify src/server/conversation/ is empty (CONFIRMED)
- [x] Verify tools/streaming/ is empty (CONFIRMED)

**Evidence:**
- src/conf/: 1 file (custom_models.json), 0 imports
- src/config/: Only __pycache__, 0 imports
- src/server/conversation/: EMPTY directory
- tools/streaming/: EMPTY directory (only __pycache__)

---

### Task 1.A.2: Delete Orphaned Directories ✅ COMPLETE

- [x] Delete src/conf/ (1 file, 0 imports)
- [x] Delete src/config/ (only __pycache__)
- [x] Delete src/server/conversation/ (empty directory)
- [x] Delete tools/streaming/ (empty directory)

**Commands:**
```powershell
# Delete orphaned directories
Remove-Item -Recurse -Force "src/conf"
Remove-Item -Recurse -Force "src/config"
Remove-Item -Recurse -Force "src/server/conversation"
Remove-Item -Recurse -Force "tools/streaming"
```

---

### Task 1.A.3: Verify No Breakage ✅ COMPLETE

- [x] Run server startup test
- [x] Check for import errors
- [x] Verify tools still work
- [x] Check logs for errors

**Result:** ✅ Server imports OK (no errors)

**Test Command:**
```powershell
# Test server startup
python -c "import src.server.handlers.request_handler; print('OK')"
```

---

### Task 1.A.4: Commit Changes ✅ COMPLETE

- [x] Stage deleted directories
- [x] Commit with message: "chore(cleanup): remove orphaned/empty directories (Phase 1.A)"
- [x] Push to branch

**Commit:** archaeological-dig/phase1-discovery-and-cleanup

**Commit Message:**
```
chore(cleanup): remove orphaned/empty directories (Phase 1.A)

Removed 4 orphaned/empty directories identified in Phase 1 investigation:
- src/conf/ (1 file, 0 imports)
- src/config/ (only __pycache__, 0 imports)
- src/server/conversation/ (empty directory)
- tools/streaming/ (empty directory)

Evidence: All directories had 0 imports across entire codebase.
Investigation: Tasks 1.4, 1.7, 1.9 in MASTER_CHECKLIST_PHASE1.md
Strategy: CONSOLIDATION_STRATEGY.md Phase 1.A
```

---

## 📋 PHASE 1.B: ARCHIVE PLANNED INFRASTRUCTURE

**Priority:** LOW  
**Impact:** NONE (not integrated)  
**Risk:** NONE (not used)  
**Estimated Time:** 1 hour

### Task 1.B.1: Create Archive Structure

- [ ] Create docs/archive/planned-features/ directory
- [ ] Create docs/archive/planned-features/README.md

**README Content:**
```markdown
# Planned Features Archive

This directory contains infrastructure that was developed but never integrated into the main system.

## Why Archived?

These features were planned and partially implemented, but:
- Never integrated into the main codebase (0 imports)
- No .env configuration exists
- Functionality is redundant with existing systems

## Contents

1. **monitoring/** - Monitoring infrastructure (redundant with utils/observability.py)
2. **security/** - RBAC system (single-user system, not needed)
3. **streaming/** - Streaming adapter (not integrated)

## Future Use

These can be:
- Deleted if not needed
- Integrated if requirements change
- Used as reference for future implementations
```

---

### Task 1.B.2: Move Monitoring Infrastructure

- [ ] Move monitoring/ to docs/archive/planned-features/monitoring/
- [ ] Add README explaining why archived
- [ ] Document redundancy with utils/observability.py

**Evidence:**
- 9 files (8 Python + 1 markdown)
- 0 imports across entire codebase
- No .env configuration
- Redundant with utils/observability.py (18 imports), utils/health.py (1 import), utils/metrics.py

---

### Task 1.B.3: Move Security/RBAC Infrastructure

- [ ] Move security/ to docs/archive/planned-features/security/
- [ ] Add README explaining why archived
- [ ] Document single-user system design

**Evidence:**
- 2 files (rbac.py, rbac_config.py)
- 0 imports across entire codebase
- No .env configuration (RBAC_ENABLED, AUTH_ENABLED missing)
- Single-user system (RBAC not needed)

---

### Task 1.B.4: Move Streaming Infrastructure

- [ ] Move streaming/ to docs/archive/planned-features/streaming/
- [ ] Add README explaining why archived
- [ ] Document non-integration

**Evidence:**
- 1 file (streaming_adapter.py)
- 0 imports across entire codebase
- No .env configuration (STREAMING_ENABLED missing)
- Not integrated into system

---

### Task 1.B.5: Verify No Breakage

- [ ] Run server startup test
- [ ] Check for import errors
- [ ] Verify tools still work
- [ ] Check logs for errors

---

### Task 1.B.6: Commit Changes

- [ ] Stage archived directories
- [ ] Commit with message: "chore(cleanup): archive planned infrastructure (Phase 1.B)"
- [ ] Push to branch

**Commit Message:**
```
chore(cleanup): archive planned infrastructure (Phase 1.B)

Moved 3 planned but unintegrated systems to archive:
- monitoring/ → docs/archive/planned-features/monitoring/
- security/ → docs/archive/planned-features/security/
- streaming/ → docs/archive/planned-features/streaming/

Evidence: All systems had 0 imports and no .env configuration.
Reason: Redundant with existing systems or not needed for single-user design.
Investigation: Tasks 1.5, 1.6, 1.7 in MASTER_CHECKLIST_PHASE1.md
Strategy: CONSOLIDATION_STRATEGY.md Phase 1.B
```

---

## 📋 PHASE 1.C: REORGANIZE UTILS/ FOLDER

**Priority:** MEDIUM  
**Impact:** HIGH (improves maintainability)  
**Risk:** MEDIUM (requires updating imports across codebase)  
**Estimated Time:** 5 hours

### Task 1.C.1: Create Folder Structure

- [ ] Create utils/file/ directory
- [ ] Create utils/conversation/ directory
- [ ] Create utils/model/ directory
- [ ] Create utils/config/ directory
- [ ] Create utils/progress/ directory
- [ ] Create utils/infrastructure/ directory

---

### Task 1.C.2: Move File Utilities (9 files)

- [ ] Move file_utils.py → utils/file/operations.py
- [ ] Move file_utils_reading.py → utils/file/operations.py (merge)
- [ ] Move file_utils_expansion.py → utils/file/expansion.py
- [ ] Move file_utils_helpers.py → utils/file/helpers.py
- [ ] Move file_utils_json.py → utils/file/json.py
- [ ] Move file_utils_security.py → utils/file/security.py
- [ ] Move file_utils_tokens.py → utils/file/tokens.py
- [ ] Move file_cache.py → utils/file/cache.py
- [ ] Move file_types.py → utils/file/types.py
- [ ] Create utils/file/__init__.py (re-export all)

---

### Task 1.C.3: Move Conversation Utilities (4 files)

- [ ] Move conversation_memory.py → utils/conversation/memory.py
- [ ] Move conversation_history.py → utils/conversation/history.py
- [ ] Move conversation_models.py → utils/conversation/models.py
- [ ] Move conversation_threads.py → utils/conversation/threads.py
- [ ] Create utils/conversation/__init__.py (re-export all)

---

### Task 1.C.4: Move Model Utilities (4 files)

- [ ] Move model_context.py → utils/model/context.py
- [ ] Move model_restrictions.py → utils/model/restrictions.py
- [ ] Move token_estimator.py → utils/model/token_estimator.py
- [ ] Move token_utils.py → utils/model/token_utils.py
- [ ] Create utils/model/__init__.py (re-export all)

---

### Task 1.C.5: Move Config Utilities (3 files)

- [ ] Move config_bootstrap.py → utils/config/bootstrap.py
- [ ] Move config_helpers.py → utils/config/helpers.py
- [ ] Move security_config.py → utils/config/security.py
- [ ] Create utils/config/__init__.py (re-export all)

---

### Task 1.C.6: Move Progress Utilities (1 file)

- [ ] Move progress_messages.py → utils/progress/messages.py
- [ ] Create utils/progress/__init__.py (re-export all)

---

### Task 1.C.7: Move Infrastructure Utilities (8 files)

- [ ] Move health.py → utils/infrastructure/health.py
- [ ] Move metrics.py → utils/infrastructure/metrics.py
- [ ] Move instrumentation.py → utils/infrastructure/instrumentation.py
- [ ] Move lru_cache_ttl.py → utils/infrastructure/lru_cache_ttl.py
- [ ] Move storage_backend.py → utils/infrastructure/storage_backend.py
- [ ] Move costs.py → utils/infrastructure/costs.py
- [ ] Move docs_validator.py → utils/infrastructure/docs_validator.py
- [ ] Move error_handling.py → utils/infrastructure/error_handling.py
- [ ] Create utils/infrastructure/__init__.py (re-export all)

---

### Task 1.C.8: Update Root utils/__init__.py

- [ ] Re-export commonly used utilities from subfolders
- [ ] Maintain backward compatibility
- [ ] Keep high-traffic files at root (progress.py, observability.py, cache.py, etc.)

---

### Task 1.C.9: Update Imports Across Codebase

- [ ] Search and replace: `from utils.file_utils import` → `from utils.file import`
- [ ] Search and replace: `from utils.conversation_memory import` → `from utils.conversation import`
- [ ] Search and replace: `from utils.model_context import` → `from utils.model import`
- [ ] Update all other imports systematically

---

### Task 1.C.10: Test Everything

- [ ] Run all tests
- [ ] Verify no import errors
- [ ] Test all workflow tools
- [ ] Test all simple tools
- [ ] Check logs for errors

---

### Task 1.C.11: Commit Changes

- [ ] Stage reorganized utils/
- [ ] Commit with message: "refactor(utils): reorganize into folders (Phase 1.C)"
- [ ] Push to branch

**Commit Message:**
```
refactor(utils): reorganize into folders (Phase 1.C)

Reorganized 37 files in utils/ into logical folders:
- utils/file/ (9 files) - File operations
- utils/conversation/ (4 files) - Conversation management
- utils/model/ (4 files) - Model utilities
- utils/config/ (3 files) - Configuration
- utils/progress/ (1 file) - Progress messages
- utils/infrastructure/ (8 files) - Infrastructure utilities

High-traffic files remain at root for easy imports:
- progress.py (24 imports)
- observability.py (18 imports)
- cache.py, client_info.py, tool_events.py, http_client.py, logging_unified.py

Backward compatibility maintained via __init__.py re-exports.

Investigation: Task 1.4 in MASTER_CHECKLIST_PHASE1.md
Strategy: CONSOLIDATION_STRATEGY.md Phase 1.C
```

---

## 📊 PROGRESS TRACKER

### Overall Progress
- Phase 1.A: 0/4 tasks (0%) ⏳
- Phase 1.B: 0/6 tasks (0%) ⏳
- Phase 1.C: 0/11 tasks (0%) ⏳
- **Total: 0/21 tasks (0%)**

### Time Estimates
- Phase 1.A: 30 minutes
- Phase 1.B: 1 hour
- Phase 1.C: 5 hours
- **Total: 6.5 hours**

---

## 🎯 SUCCESS CRITERIA

### Phase 1 Cleanup Complete When:
- [ ] All orphaned directories deleted (Phase 1.A)
- [ ] All planned infrastructure archived (Phase 1.B)
- [ ] Utils/ folder reorganized (Phase 1.C)
- [ ] All tests passing
- [ ] No import errors
- [ ] Changes committed and pushed
- [ ] Ready to proceed to SimpleTool refactoring

---

**STATUS: READY TO BEGIN PHASE 1.A**

Next: Delete orphaned directories (30 minutes)

