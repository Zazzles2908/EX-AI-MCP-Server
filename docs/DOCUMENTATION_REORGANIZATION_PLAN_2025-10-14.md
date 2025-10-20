# Documentation Reorganization Plan
**Date:** 2025-10-14  
**Status:** 📋 Planning  
**Total Files Scanned:** ~270 markdown files

---

## 🎯 Purpose

Clean up the documentation structure to make it easy to navigate, maintain, and understand. Currently there are ~270 markdown files scattered across 10+ directories with significant overlap and redundancy.

---

## 📊 Current State Analysis

### **Directory Structure (Current)**

```
docs/
├── 01_ARCHITECTURE/          (4 files, 65 KB)
├── 02_API_REFERENCE/         (3 files, 26 KB)
├── 03_IMPLEMENTATION/        (2 files, 15 KB)
├── 04_TESTING/               (36 files, 300+ KB) ⚠️ BLOATED
├── 05_ISSUES/                (62 files, 500+ KB) ⚠️ BLOATED
├── 06_PROGRESS/              (18 files, 200+ KB) ⚠️ BLOATED
├── 07_ARCHIVE/               (2 files, 12 KB)
├── architecture/             (15 files, 150+ KB) ⚠️ DUPLICATE
├── archive/                  (150+ files, 2+ MB) ⚠️ MASSIVE
├── consolidated_checklist/   (2 files, 21 KB)
├── guides/                   (10 files, 140 KB)
├── known_issues/             (5 files, 35 KB)
├── maintenance/              (2 files, 15 KB)
├── system-reference/         (35 files, 150 KB)
├── ux/                       (1 file, 10 KB)
├── PROJECT_CONCLUSION.md     (8 KB)
├── QUICK_REFERENCE.md        (8 KB)
└── README.md                 (10 KB)
```

### **Key Problems**

1. **Duplicate Directories:**
   - `01_ARCHITECTURE/` vs `architecture/` (both contain architecture docs)
   - `07_ARCHIVE/` vs `archive/` (both contain archived content)

2. **Bloated Active Directories:**
   - `04_TESTING/` - 36 files, most are historical evidence
   - `05_ISSUES/` - 62 files, many superseded or resolved
   - `06_PROGRESS/` - 18 files, session logs and progress tracking

3. **Massive Archive:**
   - `archive/` contains 150+ files (2+ MB)
   - `archive/phase-a-b-historical-2025-10-14/` alone has 100+ files

4. **Unclear Organization:**
   - Hard to find current, actionable documentation
   - Mix of active work, historical records, and reference material
   - No clear separation between "what to read" vs "historical context"

---

## 🎯 Proposed Structure

### **New Clean Structure**

```
docs/
├── README.md                          ⭐ START HERE - Navigation hub
├── QUICK_REFERENCE.md                 ⭐ Quick lookup for common tasks
│
├── 01_GETTING_STARTED/                📘 For new users/agents
│   ├── SYSTEM_OVERVIEW.md
│   ├── INSTALLATION.md
│   └── FIRST_STEPS.md
│
├── 02_ARCHITECTURE/                   🏗️ System design & structure
│   ├── README.md
│   ├── CORE_SYSTEMS.md
│   ├── DEPENDENCY_MAP.md
│   └── DESIGN_INTENT.md
│
├── 03_API_REFERENCE/                  📚 API documentation
│   ├── README.md
│   ├── KIMI_API.md
│   ├── GLM_API.md
│   └── MCP_PROTOCOL.md
│
├── 04_GUIDES/                         📖 How-to guides
│   ├── README.md
│   ├── TOOL_USAGE.md
│   ├── WEB_SEARCH.md
│   ├── MONITORING.md
│   └── TROUBLESHOOTING.md
│
├── 05_CURRENT_WORK/                   🚧 Active development
│   ├── README.md
│   ├── MASTER_CHECKLIST.md
│   ├── IMPLEMENTATION_TRACKER.md
│   └── KNOWN_ISSUES.md
│
├── 06_ARCHIVE/                        📦 Historical reference
│   ├── README.md
│   ├── 2025-10-14_phase-a-b/         (Phase A & B work)
│   ├── 2025-10-13_testing/           (Testing evidence)
│   ├── 2025-10-12_progress/          (Progress logs)
│   └── legacy/                        (Old project status)
│
└── system-reference/                  🔧 Technical reference (keep as-is)
    └── (existing structure)
```

---

## 📋 Reorganization Tasks

### **Phase 1: Consolidate Active Documentation (Priority: HIGH)**

#### **Task 1.1: Merge Architecture Docs**
- [ ] Merge `01_ARCHITECTURE/` into `02_ARCHITECTURE/`
- [ ] Keep only latest versions of each doc
- [ ] Archive superseded versions to `06_ARCHIVE/2025-10-14_architecture/`

**Files to consolidate:**
- `01_ARCHITECTURE/ARCHITECTURAL_REDESIGN_PROPOSAL.md` → Archive (superseded)
- `01_ARCHITECTURE/DEPENDENCY_MAP.md` → Keep in `02_ARCHITECTURE/`
- `01_ARCHITECTURE/DESIGN_INTENT_SUMMARY.md` → Keep in `02_ARCHITECTURE/`
- `01_ARCHITECTURE/EXISTING_ARCHITECTURE_ANALYSIS.md` → Archive (analysis complete)

#### **Task 1.2: Consolidate API Reference**
- [ ] Keep `02_API_REFERENCE/` as-is (already clean)
- [ ] Add MCP protocol documentation from `05_ISSUES/MCP_FILE_HANDLING_*`

#### **Task 1.3: Create Current Work Hub**
- [ ] Create `05_CURRENT_WORK/` directory
- [ ] Move active trackers:
  - `consolidated_checklist/MASTER_CHECKLIST_2025-10-14.md` → `MASTER_CHECKLIST.md`
  - `05_ISSUES/MCP_FILE_HANDLING_IMPLEMENTATION_TRACKER_2025-10-14.md` → `MCP_IMPLEMENTATION_TRACKER.md`
  - `known_issues/` → `KNOWN_ISSUES.md` (consolidate into one file)

#### **Task 1.4: Consolidate Guides**
- [ ] Keep `04_GUIDES/` directory
- [ ] Move relevant guides from `guides/` to `04_GUIDES/`
- [ ] Remove duplicates

---

### **Phase 2: Archive Historical Content (Priority: MEDIUM)**

#### **Task 2.1: Archive Testing Evidence**
- [ ] Move `04_TESTING/evidence/` → `06_ARCHIVE/2025-10-13_testing/`
- [ ] Keep only `04_TESTING/COMPREHENSIVE_VERIFICATION_REPORT.md` (latest summary)
- [ ] Archive all other testing docs

#### **Task 2.2: Archive Progress Logs**
- [ ] Move `06_PROGRESS/` → `06_ARCHIVE/2025-10-12_progress/`
- [ ] Keep only `GOD_CHECKLIST_CONSOLIDATED.md` → Move to `05_CURRENT_WORK/`

#### **Task 2.3: Archive Resolved Issues**
- [ ] Review `05_ISSUES/` - 62 files!
- [ ] Keep only:
  - `MCP_FILE_HANDLING_EXAI_ANALYSIS_2025-10-14.md` (reference)
  - `MCP_FILE_HANDLING_IMPLEMENTATION_TRACKER_2025-10-14.md` (active)
  - `KNOWN_ISSUES.md` (consolidated)
- [ ] Archive all bug fix docs to `06_ARCHIVE/2025-10-14_bugfixes/`
- [ ] Archive all investigations to `06_ARCHIVE/2025-10-14_investigations/`

#### **Task 2.4: Consolidate Archives**
- [ ] Merge `07_ARCHIVE/` into `06_ARCHIVE/`
- [ ] Merge `archive/` into `06_ARCHIVE/`
- [ ] Create clear subdirectories by date/topic

---

### **Phase 3: Create Navigation & Index (Priority: HIGH)**

#### **Task 3.1: Update Root README**
- [ ] Rewrite `docs/README.md` as navigation hub
- [ ] Clear sections: Getting Started, Architecture, Guides, Current Work
- [ ] Link to all major documents
- [ ] Add "What to read first" section

#### **Task 3.2: Create Directory READMEs**
- [ ] `02_ARCHITECTURE/README.md` - Architecture overview
- [ ] `03_API_REFERENCE/README.md` - API index
- [ ] `04_GUIDES/README.md` - Guide index
- [ ] `05_CURRENT_WORK/README.md` - Current status
- [ ] `06_ARCHIVE/README.md` - Archive index

#### **Task 3.3: Update QUICK_REFERENCE**
- [ ] Consolidate quick reference info
- [ ] Add links to detailed docs
- [ ] Keep it under 200 lines

---

## 📊 File Count Reduction Target

### **Before:**
- Total files: ~270
- Active docs: ~120
- Archive: ~150

### **After (Target):**
- Total files: ~100
- Active docs: ~30 (easy to navigate)
- Archive: ~70 (organized by date/topic)

**Reduction: ~170 files (63% reduction)**

---

## ✅ Success Criteria

1. **Easy Navigation:**
   - New agent can find what they need in < 2 minutes
   - Clear separation between active work and historical context

2. **No Duplicates:**
   - Each piece of information exists in exactly one place
   - Clear versioning for documents that evolve

3. **Clean Structure:**
   - Max 6 top-level directories
   - Each directory has clear purpose
   - README in every directory

4. **Preserved History:**
   - All historical docs archived (not deleted)
   - Clear dating and organization
   - Easy to reference when needed

---

## 🚀 Execution Plan

### **Step 1: Backup**
- [ ] Create backup of entire `docs/` directory
- [ ] Commit current state to git

### **Step 2: Execute Phase 1** (Active Docs)
- [ ] Consolidate architecture
- [ ] Consolidate API reference
- [ ] Create current work hub
- [ ] Consolidate guides

### **Step 3: Execute Phase 2** (Archive)
- [ ] Archive testing evidence
- [ ] Archive progress logs
- [ ] Archive resolved issues
- [ ] Consolidate archive directories

### **Step 4: Execute Phase 3** (Navigation)
- [ ] Update root README
- [ ] Create directory READMEs
- [ ] Update QUICK_REFERENCE

### **Step 5: Validation**
- [ ] Test navigation (can you find key docs quickly?)
- [ ] Verify no broken links
- [ ] Confirm all files accounted for

---

## 📝 Notes

### **Files to Keep (Active)**
1. `02_ARCHITECTURE/DEPENDENCY_MAP.md`
2. `02_ARCHITECTURE/DESIGN_INTENT.md`
3. `03_API_REFERENCE/KIMI_API_REFERENCE.md`
4. `03_API_REFERENCE/GLM_API_REFERENCE.md`
5. `05_CURRENT_WORK/MASTER_CHECKLIST.md`
6. `05_CURRENT_WORK/MCP_IMPLEMENTATION_TRACKER.md`
7. `05_CURRENT_WORK/KNOWN_ISSUES.md`
8. `04_GUIDES/` (all guides)
9. `system-reference/` (all reference docs)

### **Files to Archive**
- All `04_TESTING/evidence/` → `06_ARCHIVE/2025-10-13_testing/`
- All `06_PROGRESS/` → `06_ARCHIVE/2025-10-12_progress/`
- Most of `05_ISSUES/` → `06_ARCHIVE/2025-10-14_issues/`
- All `archive/` → `06_ARCHIVE/legacy/`

---

**Next Action:** Get user approval, then execute Phase 1

