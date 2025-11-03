# NEXT AGENT PROMPT - PHASE 2 HIGH PRIORITY IMPLEMENTATION

**Date:** 2025-11-01  
**Task:** Implement Phase 2 HIGH priority tasks  
**Estimated Time:** 2-3 hours  
**Estimated Lines of Code:** ~2,300 lines (1,500 new, 500 modified, 300 removed)

---

## 🚨 CRITICAL: READ THESE FILES FIRST

**MANDATORY READING (in this exact order):**

1. **`docs/05_CURRENT_WORK/2025-11-02/PHASE2_IMPLEMENTATION_PLAN__HANDOVER.md`** (1,556 lines)
   - Complete implementation plan with EXAI recommendations
   - Full code templates for all new files
   - Step-by-step implementation sequence
   - Validation workflow (exact sequence)
   - **CRITICAL:** Section 13 - EXAI Validation Feedback & Critical Updates

2. **`docs/05_CURRENT_WORK/2025-11-02/COMPREHENSIVE_MASTER_CHECKLIST__FINAL.md`** (Part 1)
   - Master tracking sheet for all project work
   - Phase 0 (SECURITY CRITICAL) - ✅ COMPLETE
   - Phase 1 (URGENT) - ✅ COMPLETE
   - Phase 2 (HIGH) - 🔄 PLANNING COMPLETE

3. **`docs/05_CURRENT_WORK/2025-11-02/COMPREHENSIVE_MASTER_CHECKLIST__PART2.md`** (Part 2)
   - Architecture and script changes documentation
   - System impact documentation

4. **`docs/05_CURRENT_WORK/2025-11-02/COMPREHENSIVE_MASTER_CHECKLIST__PART3.md`** (Part 3)
   - Implementation code examples
   - Batch details and completion timestamps

---

## 📋 YOUR TASK

Implement Phase 2 HIGH priority tasks following the **EXACT** implementation plan in the handover document:

### Tasks to Complete (5 total):
1. **Task 3.1:** Reduce configuration complexity
   - Create `config/base.py` with base configuration classes
   - Create `config/file_management.py` with file upload configuration
   - Refactor `config/operations.py` to use base classes

2. **Task 3.2:** Consolidate configuration files
   - Reduce `.env.docker` from 776 lines to <200 lines
   - Move non-sensitive env vars to Python config classes
   - Keep only API keys and secrets in .env

3. **Task 4.1:** Add comprehensive monitoring
   - Create `src/monitoring/file_metrics.py` with Prometheus metrics
   - Instrument `src/file_management/unified_manager.py` for metrics collection
   - Add metrics: upload_attempts, upload_bytes, upload_duration, active_uploads, deduplication_hits, circuit_breaker_trips

4. **Task 4.2:** Implement lifecycle management
   - Create `src/file_management/lifecycle_manager.py` with periodic cleanup
   - Implement retention policy (30 days default)
   - Integrate with `src/monitoring/persistence/graceful_shutdown.py`

5. **Additional:** Remove all dead code
   - Delete `config/timeouts.py`, `config/migration.py`, `config/file_handling.py`
   - Consolidate duplicate configurations
   - Update all imports

---

## 🔧 IMPLEMENTATION WORKFLOW

### ⚠️ CRITICAL: Follow this EXACT sequence

**DO NOT deviate from the plan without consulting EXAI first.**

### Step 1: Read and Understand
1. Read the handover document thoroughly (all 1,556 lines)
2. Pay special attention to Section 13 (EXAI Validation Feedback)
3. Review the configuration migration mapping table (23 environment variables)
4. Understand the implementation sequence with testing checkpoints

### Step 2: Consult EXAI BEFORE Starting
**MANDATORY:** Consult EXAI to validate your understanding before writing any code.

**EXAI Parameters:**
- Continuation ID: `fa6820a0-d18b-49da-846f-ee5d5db2ae8b` (18 turns remaining)
- Model: `glm-4.6`
- Thinking mode: `max`
- Web search: `true`
- Tool: `chat_EXAI-WS-VSCode1` (NOT `chat_EXAI-WS-VSCode2`)

**Prompt:**
```
I'm about to implement Phase 2 HIGH priority tasks based on the handover document. Here's my understanding:

1. Configuration consolidation:
   - Create config/base.py with BaseConfig class (get_bool, get_int, get_float, get_str, get_list methods)
   - Create config/file_management.py with FileManagementConfig class (file sizes, extensions, timeouts, retention)
   - Refactor config/operations.py to inherit from BaseConfig
   - Update src/core/env_config.py to import new config modules
   - Reduce .env.docker from 776 lines to <200 lines using migration mapping table

2. Monitoring enhancement:
   - Create src/monitoring/file_metrics.py with 6 Prometheus metrics
   - Add init_file_metrics() function for initialization
   - Instrument src/file_management/unified_manager.py (upload_file and delete_file methods)
   - Record metrics at correct points (start, completion, deduplication, circuit breaker trips)

3. Lifecycle management:
   - Create src/file_management/lifecycle_manager.py with FileLifecycleManager class
   - Implement periodic cleanup task (asyncio.create_task)
   - Query Supabase for expired files (created_at < cutoff_date, status='active', NOT status='uploading')
   - Delete from provider using unified_manager.delete_file()
   - Mark as deleted in Supabase
   - Integrate with graceful_shutdown.py

4. Dead code removal:
   - Delete config/timeouts.py, config/migration.py, config/file_handling.py
   - Update all imports
   - Consolidate duplicate timeout configurations into operations.py

5. Critical updates from EXAI validation:
   - Fix type hints in config/base.py (List[str] instead of list)
   - Fix null check in lifecycle_manager.py (if not result or not result.data)
   - Add init_file_metrics() to file_metrics.py
   - Add race condition prevention (exclude status='uploading' from cleanup)
   - Add configuration validation methods
   - Verify database schema (file_uploads table has deleted_at and deletion_reason columns)

Is this understanding correct? Any potential issues I should be aware of before starting?
```

### Step 3: Implement Following Handover Document
Follow the implementation sequence in Section 6 of the handover document:

**PHASE 1: Configuration Foundation (30 minutes)**
- Create config/base.py → TEST IMMEDIATELY
- Create config/file_management.py → TEST IMMEDIATELY
- Refactor config/operations.py → TEST IMMEDIATELY
- Update src/core/env_config.py → TEST IMMEDIATELY
- CHECKPOINT: Run all configuration tests

**PHASE 2: Monitoring Enhancement (30 minutes)**
- Create src/monitoring/file_metrics.py → TEST IMMEDIATELY
- Add init_file_metrics() to server startup → TEST IMMEDIATELY
- Instrument unified_manager.py → TEST WITH SAMPLE UPLOAD
- CHECKPOINT: Verify metrics in Prometheus endpoint

**PHASE 3: Lifecycle Management (45 minutes)**
- Verify database schema (file_uploads table)
- Create src/file_management/lifecycle_manager.py → TEST IMMEDIATELY
- Integrate with graceful_shutdown.py → TEST SHUTDOWN
- Update server startup → TEST LIFECYCLE START/STOP
- CHECKPOINT: Manually trigger cleanup (dry run)

**PHASE 4: Configuration Cleanup (30 minutes)**
- Backup .env.docker
- Reduce .env.docker using migration table
- TEST: Verify all configs still load
- Delete dead code files
- CHECKPOINT: Full system test

**PHASE 5: Docker Validation (15 minutes)**
- Docker rebuild
- Verify container starts without errors
- Run end-to-end tests
- CHECKPOINT: All tests pass

### Step 4: Consult EXAI During Implementation (if stuck)
If you encounter any issues:

**Prompt:**
```
I'm implementing [specific component] and encountered [specific issue]. Here's what I've tried:
- [attempt 1]
- [attempt 2]

Error message: [error]

What's the root cause and how should I fix it?
```

### Step 5: Execute Validation Workflow (EXACT SEQUENCE)

**CRITICAL:** Follow this EXACT sequence for validation.

#### 5.1 Docker Rebuild
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
timeout /t 10 /nobreak
```

#### 5.2 Create Completion Markdown
Create file: `docs/05_CURRENT_WORK/2025-11-02/HIGH_TASKS_IMPLEMENTATION_COMPLETE.md`

**Required Content:**
- Summary of all 5 tasks completed
- List of ALL files created (full absolute paths)
- List of ALL files modified (full absolute paths)
- List of ALL files deleted (full absolute paths)
- Implementation details and features
- **Note:** Docker logs are PENDING (will be collected after EXAI Round 1)

#### 5.3 EXAI Validation Round 1 (Initial Review)
**Upload to EXAI:**
- Completion markdown
- ALL newly created files
- ALL modified files

**EXAI Parameters:**
- Model: `glm-4.6`
- Thinking mode: `max`
- Web search: `true`
- Continuation ID: `fa6820a0-d18b-49da-846f-ee5d5db2ae8b`

**Prompt:**
```
Phase 2 HIGH priority tasks implementation complete. Please review the implementation and validate that all objectives have been achieved:

1. Configuration consolidation (Tasks 3.1 & 3.2):
   - .env.docker reduced from 776 lines to <200 lines
   - New config modules created (base.py, file_management.py)
   - Existing configs refactored to use base classes

2. Comprehensive monitoring (Task 4.1):
   - file_metrics.py created with Prometheus metrics
   - unified_manager.py instrumented for metrics collection
   - Metrics: upload_attempts, upload_bytes, upload_duration, active_uploads, deduplication_hits, circuit_breaker_trips

3. Lifecycle management (Task 4.2):
   - lifecycle_manager.py created with periodic cleanup
   - Retention policy (30 days) implemented
   - Integration with graceful shutdown manager

4. Dead code removal:
   - Deleted: config/timeouts.py, config/migration.py, config/file_handling.py
   - Consolidated duplicate configurations

Please validate:
- No import errors
- All modules integrate correctly
- Configuration loads properly
- Metrics are defined correctly
- Lifecycle manager logic is sound
- No obvious bugs or issues

Docker logs will be provided in Round 2 for runtime validation.
```

#### 5.4 Collect Docker Logs
```bash
docker logs exai-mcp-daemon --tail 1000 > docs\05_CURRENT_WORK\2025-11-02\docker_logs_high.txt
```

#### 5.5 EXAI Validation Round 2 (Comprehensive Review)
**Upload to EXAI:**
- Completion markdown
- ALL files (created + modified)
- Docker logs (`docker_logs_high.txt`)

**Prompt:**
```
Comprehensive review of Phase 2 HIGH priority implementation with Docker logs.

Please verify:
1. Container started successfully (no import errors in logs)
2. All modules loaded correctly
3. No runtime errors
4. Configuration system working (values loaded from new config modules)
5. Metrics system initialized (Prometheus metrics registered)
6. Lifecycle manager started successfully
7. No warnings or errors in logs
8. System is stable and production-ready

If any issues are found, provide specific recommendations for fixes.
```

#### 5.6 Implement EXAI Findings (if any)
If EXAI identifies issues:
1. Implement fixes immediately
2. Rebuild Docker: `docker-compose down && docker-compose build --no-cache && docker-compose up -d`
3. Repeat validation workflow from Step 5.2
4. Continue until EXAI confirms all objectives achieved

#### 5.7 Update Master Checklists
Update all 3 master checklist files:
- `COMPREHENSIVE_MASTER_CHECKLIST__FINAL.md` (Part 1) - Mark Phase 2 tasks complete
- `COMPREHENSIVE_MASTER_CHECKLIST__PART2.md` (Part 2) - Document script changes and system impact
- `COMPREHENSIVE_MASTER_CHECKLIST__PART3.md` (Part 3) - Document batches and completion timestamps

---

## ⚠️ CRITICAL REMINDERS

1. **ALWAYS use absolute file paths** (c:\Project\EX-AI-MCP-Server\...)
2. **ALWAYS consult EXAI before major decisions**
3. **ALWAYS follow the validation workflow in exact sequence**
4. **NEVER skip steps or deviate from the plan without EXAI approval**
5. **Track ALL changes in completion markdown**
6. **Test incrementally after each phase** (don't wait until the end)
7. **Backup .env.docker before modifying** (cp .env.docker .env.docker.backup.$(date +%Y%m%d_%H%M%S))
8. **Verify database schema before implementing lifecycle manager**
9. **Use configuration migration mapping table** (Section 13.1 of handover document)
10. **Apply all EXAI validation feedback** (Section 13 of handover document)

---

## ✅ SUCCESS CRITERIA

Phase 2 implementation is COMPLETE when:

- [ ] All 4 new files created and tested
- [ ] All 5 existing files modified correctly
- [ ] All 3 dead code files deleted
- [ ] .env.docker reduced from 776 lines to <200 lines
- [ ] All configuration loads correctly
- [ ] No import errors
- [ ] Metrics recorded during file operations
- [ ] Prometheus endpoint shows new metrics
- [ ] Lifecycle manager starts and stops correctly
- [ ] Periodic cleanup task runs successfully
- [ ] Docker rebuild successful (no errors)
- [ ] EXAI Round 1 validation passed
- [ ] Docker logs collected (1000 lines)
- [ ] EXAI Round 2 validation passed
- [ ] All 3 master checklists updated
- [ ] System production-ready

---

## 📚 QUICK REFERENCE

### File Paths (Absolute)
- Handover doc: `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\PHASE2_IMPLEMENTATION_PLAN__HANDOVER.md`
- Master checklist (Part 1): `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\COMPREHENSIVE_MASTER_CHECKLIST__FINAL.md`
- Completion markdown: `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\HIGH_TASKS_IMPLEMENTATION_COMPLETE.md`
- Docker logs: `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\docker_logs_high.txt`

### Key Commands
```bash
# Docker rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
timeout /t 10 /nobreak

# Collect logs
docker logs exai-mcp-daemon --tail 1000 > docs\05_CURRENT_WORK\2025-11-02\docker_logs_high.txt

# Backup .env.docker
cp .env.docker .env.docker.backup.$(date +%Y%m%d_%H%M%S)

# Test imports
python -c "from config.base import BaseConfig; print('OK')"
python -c "from config.file_management import FileManagementConfig; print('OK')"
python -c "from src.monitoring.file_metrics import record_upload_attempt; print('OK')"
python -c "from src.file_management.lifecycle_manager import FileLifecycleManager; print('OK')"
```

### EXAI Consultation
- Continuation ID: `fa6820a0-d18b-49da-846f-ee5d5db2ae8b`
- Turns remaining: 18
- Model: `glm-4.6`
- Thinking mode: `max`
- Web search: `true`
- Tool: `chat_EXAI-WS-VSCode1`

---

**BEGIN BY:** Reading the handover document and confirming your understanding with EXAI using the prompt provided in Step 2 above.

**GOOD LUCK!** 🚀
