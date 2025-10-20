# File Categorization Plan
**Date:** 2025-10-14 (14th October 2025)  
**Purpose:** Categorize all existing markdown files for reorganization  
**Status:** IN PROGRESS

---

## 📋 Categorization Rules

### 01_ARCHITECTURE/
- System design documents
- Architecture analysis
- Dependency maps
- Design intent

### 02_API_REFERENCE/
- Provider API documentation
- Tool schemas
- Environment variables
- **CREATED:** GLM_API_REFERENCE.md, KIMI_API_REFERENCE.md, README.md

### 03_IMPLEMENTATION/
- Code implementation details
- Feature implementations
- Phase implementation summaries

### 04_TESTING/
- Test plans
- Test results
- Evidence documents

### 05_ISSUES/
- Bug investigations
- Critical issues analysis
- Known limitations

### 06_PROGRESS/
- Checklists (GOD, MASTER)
- Session summaries
- Phase summaries

### 07_ARCHIVE/
- Old/deprecated docs
- Historical investigations

---

## 📁 File Categorization

### consolidated_checklist/ Files

#### → 01_ARCHITECTURE/
- `ARCHITECTURAL_REDESIGN_PROPOSAL.md` - Architecture proposals
- `DEPENDENCY_MAP.md` - System dependencies
- `DESIGN_INTENT_SUMMARY.md` - Design intent
- `EXISTING_ARCHITECTURE_ANALYSIS.md` - Architecture analysis

#### → 02_API_REFERENCE/
- ✅ `GLM_API_REFERENCE.md` - CREATED
- ✅ `KIMI_API_REFERENCE.md` - CREATED
- ✅ `README.md` - CREATED

#### → 03_IMPLEMENTATION/
- `PHASE1_IMPLEMENTATION_SUMMARY_2025-10-14.md` - Phase 1 implementation

#### → 04_TESTING/
- `COMPREHENSIVE_VERIFICATION_REPORT.md` - Verification results
- `evidence/` - **ENTIRE DIRECTORY** (all test evidence)

#### → 05_ISSUES/
- `ARCHITECTURAL_SANITY_CHECK_2025-10-14.md` - Sanity check (investigation)
- `COMPREHENSIVE_BUG_INVESTIGATION_2025-10-14.md` - Bug investigation
- `CRITICAL_ISSUES_ANALYSIS.md` - Critical issues
- `CRITICAL_OVERLOOKED_ITEMS_ANALYSIS.md` - Overlooked items
- `FOCUSED_FIX_PLAN_2025-10-14.md` - Fix plan
- `HONEST_STATUS_UPDATE_2025-10-14.md` - Status update
- `INVESTIGATION_SUMMARY_2025-10-14.md` - Investigation summary
- `experience/` - **ENTIRE DIRECTORY** (real-world test results)

#### → 06_PROGRESS/
- `GOD_CHECKLIST_CONSOLIDATED.md` - Original GOD checklist
- `MASTER_CHECKLIST_2025-10-14.md` - Master checklist (KEEP IN consolidated_checklist/)
- `PHASE_B_CLEANUP_SUMMARY.md` - Phase B summary
- `PHASE_C_FINAL_COMPLETION_REPORT.md` - Phase C report
- `PHASE_C_OPTIMIZE_SUMMARY.md` - Phase C summary
- `README.md` - Checklist overview
- `SESSION_SUMMARY_2025-10-14_CRITICAL_FIXES.md` - Session summary
- `CONSOLIDATION_NOTES.md` - Consolidation notes
- `updates/` - **ENTIRE DIRECTORY** (if exists)

#### → 07_ARCHIVE/
- None yet (will move old docs here)

---

### docs/ Root Files

#### → 01_ARCHITECTURE/
- `architecture/` - **ENTIRE DIRECTORY**
- `system-reference/DEPENDENCY_MAP.md` (if different from consolidated_checklist version)

#### → 02_API_REFERENCE/
- ✅ Already created new structure

#### → 03_IMPLEMENTATION/
- ✅ `THINKING_MODE_CORRECTED_UNDERSTANDING.md` - CREATED (move here)

#### → 04_TESTING/
- Test-related docs from various directories

#### → 05_ISSUES/
- `known_issues/` - **ENTIRE DIRECTORY**

#### → 06_PROGRESS/
- ✅ `DOCUMENTATION_REORGANIZATION_PLAN.md` - CREATED (move here)
- ✅ `FILE_CATEGORIZATION_PLAN.md` - THIS FILE (move here)

#### → 07_ARCHIVE/
- `archive/` - **ENTIRE DIRECTORY** (already archived)
- `features/` - Old planned features
- `guides/` - **REVIEW FIRST** (may keep some)
- `maintenance/` - **REVIEW FIRST** (may keep some)
- `ux/` - **REVIEW FIRST** (may keep some)

---

## 🎯 Action Plan

### Step 1: Move Architecture Files
```powershell
# Move to 01_ARCHITECTURE/
Move-Item "docs\consolidated_checklist\ARCHITECTURAL_REDESIGN_PROPOSAL.md" "docs\01_ARCHITECTURE\"
Move-Item "docs\consolidated_checklist\DEPENDENCY_MAP.md" "docs\01_ARCHITECTURE\"
Move-Item "docs\consolidated_checklist\DESIGN_INTENT_SUMMARY.md" "docs\01_ARCHITECTURE\"
Move-Item "docs\consolidated_checklist\EXISTING_ARCHITECTURE_ANALYSIS.md" "docs\01_ARCHITECTURE\"
Move-Item "docs\architecture" "docs\01_ARCHITECTURE\legacy_architecture" -Recurse
```

### Step 2: Move Implementation Files
```powershell
# Move to 03_IMPLEMENTATION/
Move-Item "docs\consolidated_checklist\PHASE1_IMPLEMENTATION_SUMMARY_2025-10-14.md" "docs\03_IMPLEMENTATION\"
Move-Item "docs\THINKING_MODE_CORRECTED_UNDERSTANDING.md" "docs\03_IMPLEMENTATION\"
```

### Step 3: Move Testing Files
```powershell
# Move to 04_TESTING/
Move-Item "docs\consolidated_checklist\COMPREHENSIVE_VERIFICATION_REPORT.md" "docs\04_TESTING\"
Move-Item "docs\consolidated_checklist\evidence" "docs\04_TESTING\" -Recurse
```

### Step 4: Move Issues Files
```powershell
# Move to 05_ISSUES/
Move-Item "docs\consolidated_checklist\ARCHITECTURAL_SANITY_CHECK_2025-10-14.md" "docs\05_ISSUES\investigations\"
Move-Item "docs\consolidated_checklist\COMPREHENSIVE_BUG_INVESTIGATION_2025-10-14.md" "docs\05_ISSUES\investigations\"
Move-Item "docs\consolidated_checklist\CRITICAL_ISSUES_ANALYSIS.md" "docs\05_ISSUES\"
Move-Item "docs\consolidated_checklist\CRITICAL_OVERLOOKED_ITEMS_ANALYSIS.md" "docs\05_ISSUES\"
Move-Item "docs\consolidated_checklist\FOCUSED_FIX_PLAN_2025-10-14.md" "docs\05_ISSUES\"
Move-Item "docs\consolidated_checklist\HONEST_STATUS_UPDATE_2025-10-14.md" "docs\05_ISSUES\"
Move-Item "docs\consolidated_checklist\INVESTIGATION_SUMMARY_2025-10-14.md" "docs\05_ISSUES\investigations\"
Move-Item "docs\consolidated_checklist\experience" "docs\05_ISSUES\" -Recurse
Move-Item "docs\known_issues" "docs\05_ISSUES\legacy_known_issues" -Recurse
```

### Step 5: Move Progress Files
```powershell
# Move to 06_PROGRESS/
Move-Item "docs\consolidated_checklist\GOD_CHECKLIST_CONSOLIDATED.md" "docs\06_PROGRESS\"
Move-Item "docs\consolidated_checklist\PHASE_B_CLEANUP_SUMMARY.md" "docs\06_PROGRESS\PHASE_SUMMARIES\"
Move-Item "docs\consolidated_checklist\PHASE_C_FINAL_COMPLETION_REPORT.md" "docs\06_PROGRESS\PHASE_SUMMARIES\"
Move-Item "docs\consolidated_checklist\PHASE_C_OPTIMIZE_SUMMARY.md" "docs\06_PROGRESS\PHASE_SUMMARIES\"
Move-Item "docs\consolidated_checklist\SESSION_SUMMARY_2025-10-14_CRITICAL_FIXES.md" "docs\06_PROGRESS\SESSION_LOGS\"
Move-Item "docs\consolidated_checklist\CONSOLIDATION_NOTES.md" "docs\06_PROGRESS\"
Move-Item "docs\DOCUMENTATION_REORGANIZATION_PLAN.md" "docs\06_PROGRESS\"
Move-Item "docs\FILE_CATEGORIZATION_PLAN.md" "docs\06_PROGRESS\"
```

### Step 6: Archive Old Directories
```powershell
# Move to 07_ARCHIVE/
Move-Item "docs\features" "docs\07_ARCHIVE\" -Recurse
# Keep guides/, maintenance/, system-reference/ for now (review first)
```

### Step 7: Keep in consolidated_checklist/
```
# These stay in consolidated_checklist/ (active work)
- MASTER_CHECKLIST_2025-10-14.md
- README.md
```

---

## 📊 Summary

### Files to Move: ~40 files
### Directories to Move: ~5 directories
### Files to Keep in Place: 2 files
### New Files Created: 5 files

### Estimated Time: 2-3 hours

---

## ✅ Completed

- [x] Created new directory structure (01-07)
- [x] Created 02_API_REFERENCE/ with GLM and Kimi docs
- [x] Created THINKING_MODE_CORRECTED_UNDERSTANDING.md
- [x] Created this categorization plan

---

## 🎯 Next Steps

1. Execute file moves (Steps 1-7)
2. Update internal links in moved files
3. Create consolidated documents (merge duplicates)
4. Update main README
5. Verify no broken references

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Status:** IN PROGRESS - Ready to execute moves

