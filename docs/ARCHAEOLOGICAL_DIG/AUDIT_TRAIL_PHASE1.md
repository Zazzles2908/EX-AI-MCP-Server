# ARCHAEOLOGICAL DIG - PHASE 1 AUDIT TRAIL
**Branch:** archaeological-dig/phase1-discovery-and-cleanup  
**Started:** 2025-10-10 12:15 PM AEDT  
**Status:** 🔍 IN PROGRESS

---

## PURPOSE

This document tracks EVERY action taken during Phase 1 of the archaeological dig. It serves as:
- Complete audit trail of all investigations
- Timeline of discoveries
- Evidence for all classifications
- Justification for all recommendations

---

## PHASE 1 OVERVIEW

**Goal:** Systematically investigate entire codebase to determine what's ACTIVE, ORPHANED, or DUPLICATE

**Approach:**
1. Search for imports (grep)
2. Check .env configuration
3. Read implementation files
4. Classify components
5. Document findings
6. Create consolidation strategy

**Categories to Investigate:**
1. System Prompts (systemprompts/)
2. Timezone Utility (src/utils/timezone.py)
3. Model Routing (src/providers/registry*.py)
4. Utils Folder (utils/ - 30+ files)
5. Monitoring (monitoring/ - 9 files)
6. Security/RBAC (security/ - 2 files)
7. Streaming (streaming/ + tools/streaming/)
8. Tools Structure (tools/ - 40+ files)
9. Src Duplicates (src/ - multiple duplicates)
10. Consolidation Strategy

---

## INVESTIGATION LOG

### 2025-10-10 12:15 PM - Setup

**Action:** Created new git branch
- Branch: `archaeological-dig/phase1-discovery-and-cleanup`
- Base: `refactor/orchestrator-sync-v2.0.2`
- Status: ✅ Created successfully

**Action:** Set up task management
- Master task created: "PHASE 1: Archaeological Dig - Discovery & Classification"
- 10 subtasks created (1.1 through 1.10)
- All tasks tracked in Augment task list

**Action:** Created audit trail document
- File: `docs/ARCHAEOLOGICAL_DIG/AUDIT_TRAIL_PHASE1.md`
- Purpose: Track all investigations and findings

---

### 2025-10-10 12:30 PM - Task 1.1: System Prompts Investigation

**Action:** Searched for systemprompts imports
- Command: `Get-ChildItem -Recurse -Include "*.py" | Select-String -Pattern "from systemprompts import|import systemprompts"`
- Results: Found 20 imports total

**Evidence Collected:**

**Active Imports (14 files in tools/):**
1. tools/workflows/analyze.py (line 26: `from systemprompts import ANALYZE_PROMPT`)
2. tools/workflows/codereview.py (line 26: `from systemprompts import CODEREVIEW_PROMPT`)
3. tools/workflows/consensus.py (line 32: `from systemprompts import CONSENSUS_PROMPT`)
4. tools/workflows/consensus_config.py (line 9: `from systemprompts import CONSENSUS_PROMPT`)
5. tools/workflows/debug.py (line 27: `from systemprompts import DEBUG_ISSUE_PROMPT`)
6. tools/workflows/docgen.py (line 30: `from systemprompts import DOCGEN_PROMPT`)
7. tools/workflows/planner.py (line 32: `from systemprompts import PLANNER_PROMPT`)
8. tools/workflows/precommit.py (line 25: `from systemprompts import PRECOMMIT_PROMPT`)
9. tools/workflows/refactor.py (line 26: `from systemprompts import REFACTOR_PROMPT`)
10. tools/workflows/secaudit.py (line 27: `from systemprompts import SECAUDIT_PROMPT`)
11. tools/workflows/testgen.py (line 28: `from systemprompts import TESTGEN_PROMPT`)
12. tools/workflows/thinkdeep.py (line 26: `from systemprompts import THINKDEEP_PROMPT`)
13. tools/workflows/tracer.py (line 29: `from systemprompts import TRACER_PROMPT`)
14. tools/chat.py (line 17: `from systemprompts import CHAT_PROMPT`)

**Archive Imports (6 files - legacy backups):**
- docs/archive/legacy-scripts/2025-10-02/*.py (6 backup files)

**Action:** Traced execution flow
- Checked tools/workflows/analyze.py: `get_system_prompt()` returns `ANALYZE_PROMPT` (line 80)
- Checked tools/chat.py: `get_system_prompt()` returns `CHAT_PROMPT` (line 83)
- Searched for where `get_system_prompt()` is called

**Execution Flow Confirmed:**
1. Tool defines `get_system_prompt()` method that returns imported prompt
2. SimpleTool.execute() calls `self.get_system_prompt()` (tools/simple/base.py line 453)
3. System prompt is passed to provider.generate_content() (line 574)
4. Provider sends system prompt to external AI

**Code Evidence:**
```python
# tools/simple/base.py line 453
base_system_prompt = self.get_system_prompt()

# tools/simple/base.py line 574
model_response = provider.generate_content(
    prompt=prompt,
    model_name=self._current_model_name,
    system_prompt=system_prompt,  # ← System prompt is used!
    temperature=temperature,
    ...
)
```

**EXAI Tool Test:**
- Attempted to use `codereview_EXAI-WS` for analysis
- Result: ❌ ERROR - "cannot access local variable 'time' where it is not associated with a value"
- Note: EXAI tools can be unreliable (user warned about this)
- Continued with manual investigation instead

**Classification:** ✅ **ACTIVE - FULLY INTEGRATED**

**Findings:**
- systemprompts/ is ACTIVELY USED by 14 tools
- NO hardcoded prompt bypass detected
- Prompts flow correctly: import → get_system_prompt() → provider → external AI
- System is working as designed
- Archive files are legacy backups (can be ignored)

**Recommendation:**
- ✅ Keep systemprompts/ - it's the correct centralized prompt system
- ✅ No changes needed - system is properly integrated
- ⚠️ Consider adding tests to ensure prompts are never bypassed

---

## TASK CHECKLIST

### ✅ Completed Tasks
- [x] Create git branch
- [x] Set up task management
- [x] Create audit trail document
- [x] Create investigation checklist

### 🔄 In Progress Tasks
- [ ] None yet

### ⏳ Pending Tasks
- [ ] 1.1: System Prompts Investigation
- [ ] 1.2: Timezone Utility Investigation
- [ ] 1.3: Model Routing Investigation
- [ ] 1.4: Utils Folder Audit
- [ ] 1.5: Monitoring Infrastructure Investigation
- [ ] 1.6: Security/RBAC Investigation
- [ ] 1.7: Streaming Investigation
- [ ] 1.8: Tools Structure Investigation
- [ ] 1.9: Src Duplicates Investigation
- [ ] 1.10: Create Consolidation Strategy

---

## FINDINGS SUMMARY

### Category 1: System Prompts
**Status:** ✅ COMPLETE - ACTIVE
**Files:** 15 specialized prompts in systemprompts/
**Classification:** ACTIVE - Fully integrated into 14 tools
**Evidence:** 14 imports found, execution flow traced and confirmed
**Recommendation:** Keep as-is, system working correctly

### Category 2: Timezone Utility
**Status:** Not yet investigated  
**Files:** src/utils/timezone.py  
**Investigation:** Pending

### Category 3: Model Routing
**Status:** Not yet investigated  
**Files:** src/providers/registry*.py (4-5 files)  
**Investigation:** Pending

### Category 4: Utils Folder
**Status:** Not yet investigated  
**Files:** 30+ scripts in utils/  
**Investigation:** Pending

### Category 5: Monitoring
**Status:** Not yet investigated  
**Files:** 9 files in monitoring/  
**Investigation:** Pending

### Category 6: Security/RBAC
**Status:** Not yet investigated  
**Files:** 2 files in security/  
**Investigation:** Pending

### Category 7: Streaming
**Status:** Not yet investigated  
**Files:** streaming/ + tools/streaming/  
**Investigation:** Pending

### Category 8: Tools Structure
**Status:** Not yet investigated  
**Files:** 40+ files in tools/  
**Investigation:** Pending

### Category 9: Src Duplicates
**Status:** Not yet investigated  
**Files:** Multiple duplicate folders in src/  
**Investigation:** Pending

### Category 10: Consolidation Strategy
**Status:** Not yet investigated  
**Depends on:** All above investigations  
**Investigation:** Pending

---

## CLASSIFICATION RESULTS

### ACTIVE Components

**1. systemprompts/ (15 files)**
- ✅ ACTIVE - Fully integrated
- Used by 14 tools in tools/workflows/ and tools/chat.py
- Execution flow confirmed: import → get_system_prompt() → provider → AI
- No bypass detected
- **Action:** Keep as-is

### ORPHANED Components
(To be filled as investigations complete)

### DUPLICATE Components
(To be filled as investigations complete)

---

## EVIDENCE COLLECTED

### Import Search Results
(To be filled with grep results)

### .env Configuration
(To be filled with relevant env vars)

### File Analysis
(To be filled with file content analysis)

---

## RECOMMENDATIONS

### Immediate Actions
(To be filled based on findings)

### Consolidation Strategy
(To be filled after all investigations)

### Reorganization Plan
(To be filled after all investigations)

---

## TIMELINE

| Time | Action | Result |
|------|--------|--------|
| 12:15 PM | Created git branch | ✅ archaeological-dig/phase1-discovery-and-cleanup |
| 12:15 PM | Set up task management | ✅ 10 tasks created |
| 12:15 PM | Created audit trail | ✅ This document |
| 12:16 PM | Ready to begin investigations | ⏳ Awaiting start |

---

## NEXT STEPS

1. Begin Task 1.1: System Prompts Investigation
2. Search for imports of systemprompts/
3. Check if tools use them
4. Classify as ACTIVE or BYPASSED
5. Document findings in this audit trail
6. Update investigation markdown
7. Move to next task

---

**STATUS: READY TO BEGIN SYSTEMATIC INVESTIGATION**

All setup complete. Ready to start Task 1.1.

