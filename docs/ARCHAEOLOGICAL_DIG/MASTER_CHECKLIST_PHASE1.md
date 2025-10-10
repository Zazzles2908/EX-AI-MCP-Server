# ARCHAEOLOGICAL DIG - PHASE 1 MASTER CHECKLIST
**Branch:** archaeological-dig/phase1-discovery-and-cleanup  
**Started:** 2025-10-10 12:15 PM AEDT  
**Purpose:** Physical checklist to mark off completed items

---

## 🎯 PHASE 1 GOAL

Systematically investigate entire codebase to determine what's ACTIVE, ORPHANED, or DUPLICATE.

---

## ✅ SETUP (COMPLETE)

- [x] Create git branch: `archaeological-dig/phase1-discovery-and-cleanup`
- [x] Set up task management (10 tasks)
- [x] Create audit trail: `AUDIT_TRAIL_PHASE1.md`
- [x] Create master checklist: `MASTER_CHECKLIST_PHASE1.md` (this file)

---

## 📋 INVESTIGATION TASKS

### Task 1.1: System Prompts Investigation

**Goal:** Determine if systemprompts/ is used or bypassed

- [ ] Search for imports: `grep -r "from systemprompts import" .`
- [ ] Search for imports: `grep -r "import systemprompts" .`
- [ ] Check tools/ for systemprompts imports
- [ ] Check for hardcoded prompt strings in tools/
- [ ] Read systemprompts/__init__.py
- [ ] Classify: ACTIVE / BYPASSED / ORPHANED
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update prompts/SYSTEMPROMPTS_BYPASS_INVESTIGATION.md
- [ ] Mark task 1.1 complete in task manager

**Classification:** (To be filled)  
**Evidence:** (To be filled)

---

### Task 1.2: Timezone Utility Investigation

**Goal:** Determine if src/utils/timezone.py is used

- [ ] Search for imports: `grep -r "from src.utils.timezone import" .`
- [ ] Search for imports: `grep -r "import src.utils.timezone" .`
- [ ] Search for imports: `grep -r "from utils.timezone import" .`
- [ ] Check if logs use timezone.py
- [ ] Check if tools use timezone.py
- [ ] Classify: ACTIVE / ORPHANED
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update timezone/TIMEZONE_DETECTION_STRATEGY.md
- [ ] Mark task 1.2 complete in task manager

**Classification:** (To be filled)  
**Evidence:** (To be filled)

---

### Task 1.3: Model Routing Investigation

**Goal:** Understand registry system and routing failure

- [ ] Read logs/provider_registry_snapshot.json
- [ ] Check if file exists
- [ ] Document registered models
- [ ] Document routing rules
- [ ] Search for imports: `grep -r "from src.providers.registry import" .`
- [ ] Read src/providers/registry.py
- [ ] Read src/providers/registry_config.py
- [ ] Read src/providers/registry_core.py
- [ ] Read src/providers/registry_selection.py
- [ ] Identify why kimi-latest-128k was selected
- [ ] Classify: ACTIVE / BROKEN
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update routing/MODEL_ROUTING_REGISTRY_ANALYSIS.md
- [ ] Mark task 1.3 complete in task manager

**Classification:** (To be filled)  
**Evidence:** (To be filled)

---

### Task 1.4: Utils Folder Audit

**Goal:** Classify all 30+ scripts in utils/

- [ ] List all files in utils/
- [ ] For EACH file, search for imports
- [ ] Classify each as: ACTIVE / ORPHANED / DUPLICATE
- [ ] Group by category (file, conversation, token, etc.)
- [ ] Identify duplicates
- [ ] Recommend reorganization
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update utilities/UTILS_FOLDER_CHAOS_AUDIT.md
- [ ] Mark task 1.4 complete in task manager

**Files to Check:** (30+ files)  
**Classification:** (To be filled per file)  
**Evidence:** (To be filled)

---

### Task 1.5: Monitoring Infrastructure Investigation

**Goal:** Determine if monitoring/ is active or planned

- [ ] Search for imports: `grep -r "from monitoring import" .`
- [ ] Search for imports: `grep -r "import monitoring" .`
- [ ] Check .env for MONITORING_ENABLED
- [ ] Check .env for HEALTH_CHECK_INTERVAL
- [ ] Check .env for METRICS_SINK
- [ ] Read monitoring/monitoring_integration_plan.md
- [ ] Classify: ACTIVE / PLANNED / ORPHANED
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update monitoring/MONITORING_INFRASTRUCTURE_ANALYSIS.md
- [ ] Mark task 1.5 complete in task manager

**Classification:** (To be filled)  
**Evidence:** (To be filled)

---

### Task 1.6: Security/RBAC Investigation

**Goal:** Determine if security/ is active or planned

- [ ] Search for imports: `grep -r "from security import" .`
- [ ] Search for imports: `grep -r "import security" .`
- [ ] Check .env for RBAC_ENABLED
- [ ] Check .env for AUTH_ENABLED
- [ ] Read security/rbac.py
- [ ] Read security/rbac_config.py
- [ ] Classify: ACTIVE / PLANNED / ORPHANED
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update security/SECURITY_RBAC_IMPLEMENTATION.md
- [ ] Mark task 1.6 complete in task manager

**Classification:** (To be filled)  
**Evidence:** (To be filled)

---

### Task 1.7: Streaming Investigation

**Goal:** Determine streaming status and relationship

- [ ] Search for imports: `grep -r "from streaming import" .`
- [ ] Search for imports: `grep -r "import streaming" .`
- [ ] Check .env for STREAMING_ENABLED
- [ ] List files in tools/streaming/
- [ ] Compare streaming/ vs tools/streaming/
- [ ] Determine relationship
- [ ] Classify: ACTIVE / DUPLICATE / ORPHANED
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update streaming/STREAMING_ADAPTER_ARCHITECTURE.md
- [ ] Mark task 1.7 complete in task manager

**Classification:** (To be filled)  
**Evidence:** (To be filled)

---

### Task 1.8: Tools Structure Investigation

**Goal:** Understand tools/ organization and duplicates

- [ ] Read tools/workflow/base.py
- [ ] Read tools/workflows/analyze.py (example)
- [ ] Understand workflow/ vs workflows/ relationship
- [ ] List files in tools/streaming/
- [ ] Compare with streaming/
- [ ] List files in tools/providers/
- [ ] Compare with src/providers/
- [ ] Classify duplicates
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update tools/TOOLS_FOLDER_STRUCTURE_ANALYSIS.md
- [ ] Mark task 1.8 complete in task manager

**Classification:** (To be filled)  
**Evidence:** (To be filled)

---

### Task 1.9: Src Duplicates Investigation

**Goal:** Investigate all duplicate folders in src/

- [ ] Check contents of src/config/
- [ ] Compare src/conf/ vs src/config/
- [ ] Search for imports of each
- [ ] Classify: ACTIVE / DUPLICATE / ORPHANED
- [ ] Check contents of src/server/conversation/
- [ ] Compare src/conversation/ vs src/server/conversation/
- [ ] Search for imports of each
- [ ] Classify: ACTIVE / DUPLICATE / ORPHANED
- [ ] Check contents of src/server/providers/
- [ ] Compare src/providers/ vs src/server/providers/
- [ ] Search for imports of each
- [ ] Classify: ACTIVE / DUPLICATE / ORPHANED
- [ ] Check contents of src/server/utils/
- [ ] Compare src/utils/ vs src/server/utils/ vs utils/
- [ ] Search for imports of each
- [ ] Classify: ACTIVE / DUPLICATE / ORPHANED
- [ ] Document findings in AUDIT_TRAIL_PHASE1.md
- [ ] Update src_structure/SRC_FOLDER_DUPLICATION_ANALYSIS.md
- [ ] Mark task 1.9 complete in task manager

**Classification:** (To be filled per duplicate)  
**Evidence:** (To be filled)

---

### Task 1.10: Create Consolidation Strategy

**Goal:** Based on all findings, create detailed plan

- [ ] Review all classification results
- [ ] Identify all ORPHANED code (to remove)
- [ ] Identify all DUPLICATES (to consolidate)
- [ ] Identify all DISCONNECTED systems (to connect)
- [ ] Create consolidation strategy for each duplicate
- [ ] Create reorganization plan for utils/
- [ ] Create connection plan for disconnected systems
- [ ] Prioritize by impact
- [ ] Break into phases
- [ ] Create detailed implementation checklist
- [ ] Document in AUDIT_TRAIL_PHASE1.md
- [ ] Create new markdown: CONSOLIDATION_STRATEGY.md
- [ ] Get user approval
- [ ] Mark task 1.10 complete in task manager

**Strategy:** (To be filled)  
**Phases:** (To be filled)

---

## 📊 PROGRESS TRACKER

### Overall Progress
- Setup: 4/4 (100%) ✅
- Investigations: 0/9 (0%) ⏳
- Consolidation Strategy: 0/1 (0%) ⏳
- **Total: 4/14 (29%)**

### Time Estimates
- Task 1.1: ~15 minutes
- Task 1.2: ~10 minutes
- Task 1.3: ~30 minutes
- Task 1.4: ~60 minutes (30+ files)
- Task 1.5: ~15 minutes
- Task 1.6: ~15 minutes
- Task 1.7: ~20 minutes
- Task 1.8: ~30 minutes
- Task 1.9: ~45 minutes
- Task 1.10: ~60 minutes
- **Total: ~5 hours**

---

## 🎯 SUCCESS CRITERIA

### Phase 1 Complete When:
- [ ] All 9 investigations complete
- [ ] All components classified (ACTIVE/ORPHANED/DUPLICATE)
- [ ] All findings documented in AUDIT_TRAIL_PHASE1.md
- [ ] All investigation markdowns updated
- [ ] Consolidation strategy created
- [ ] User approval obtained

---

## 📝 NOTES

- Use grep for import searches (fast, accurate)
- Document ALL evidence (no assumptions)
- Update audit trail after EACH task
- Mark checklist items as completed
- Update task manager after each task

---

**STATUS: READY TO BEGIN TASK 1.1**

Next: System Prompts Investigation

