# Documentation Index

**Last Updated:** 2025-10-03  
**Organization:** Hierarchical by purpose

---

## 📁 **ROOT LEVEL**

Essential files kept at root for easy access:

- **README.md** - Main documentation entry point
- **KIMI_DESIGN_CONTEXT.md** - Design context used by Kimi review scripts

---

## 📊 **REVIEWS**

### **reviews/kimi/current/** (19 files)
Current Kimi code review results:
- `KIMI_RAW_BATCH_1.md` through `KIMI_RAW_BATCH_14.md` - Raw review responses
- `KIMI_CODE_REVIEW_src.json` - Consolidated review results
- `KIMI_FRESH_REVIEW_IN_PROGRESS.md` - Fresh review progress
- `KIMI_FRESH_REVIEW_ANALYSIS.md` - Validity analysis of findings
- `KIMI_REVIEW_PROGRESS.md` - Issue tracking and fix progress
- `KIMI_REVALIDATION_ANALYSIS.md` - Re-review analysis

### **reviews/kimi/completed/** (7 files)
Historical Kimi review documentation:
- `KIMI_CODE_REVIEW_STARTED.md` - Initial review kickoff
- `KIMI_CODE_REVIEW_SUCCESS.md` - First successful review
- `KIMI_CODE_REVIEW_FINAL_SUCCESS.md` - Final review completion
- `KIMI_CODE_REVIEW_FIX_SUMMARY.md` - Summary of fixes applied
- `KIMI_CODE_REVIEW_WHERE_IS_THE_DATA.md` - Data location investigation
- `KIMI_INVESTIGATION_COMPLETE.md` - Investigation results
- `PRE_KIMI_VALIDATION_COMPLETE.md` - Pre-review validation

### **reviews/code-review/** (2 files)
General code review documentation:
- `CODE_REVIEW_ACTION_PLAN.md` - Action plan for code review
- `CRITICAL_ISSUES_FOUND.md` - Critical issues documentation

---

## 📈 **PROJECT STATUS**

### **project-status/summaries/** (5 files)
Project completion and milestone summaries:
- `ARCHIVE_COMPLETE_SUMMARY.md` - Archive completion summary
- `FINAL_RESTRUCTURE_SUMMARY.md` - Final restructure summary
- `REVIEW_COMPLETE_SUMMARY.md` - Review completion summary
- `USER_WAS_RIGHT_SUMMARY.md` - User feedback validation
- `EXAI_RESPONSE_SUMMARY.md` - EXAI analysis summary

### **project-status/progress/** (1 file)
In-progress tracking:
- `REVIEW_IN_PROGRESS.md` - Current review progress

### **project-status/readiness/** (3 files)
Readiness and handover documentation:
- `READY_FOR_RESTART.md` - Server restart readiness
- `READY_TO_TEST.md` - Testing readiness
- `HANDOVER_TO_NEXT_AGENT.md` - Agent handover documentation

---

## 🔧 **TECHNICAL**

### **technical/plans/** (3 files)
Technical implementation plans:
- `MOONSHOT_API_FIX_PLAN.md` - Moonshot API fix plan
- `MOONSHOT_MODEL_STRATEGY.md` - Model selection strategy
- `AUTOMATED_CLEANUP_IMPLEMENTED.md` - Cleanup automation plan

### **technical/analyses/** (1 file)
Technical analysis documentation:
- `SCRIPT_RUN_RESULTS.md` - Script execution results and analysis

### **technical/fixes/** (2 files)
Fix implementation documentation:
- `ERROR_RECOVERY_COMPLETE.md` - Error recovery implementation
- `LANGUAGE_FIX_SUMMARY.md` - Language-related fixes

---

## 📚 **GUIDES**

User and developer guides (5 files):
- `parameter-reference.md` - Parameter reference guide
- `query-examples.md` - Query examples
- `tool-selection-guide.md` - Tool selection guide
- `troubleshooting.md` - Troubleshooting guide
- `web-search-guide.md` - Web search guide

---

## 🏗️ **SYSTEM REFERENCE**

System architecture and reference documentation (8 files + subdirs):
- `README.md` - System reference overview
- `01-system-overview.md` - System overview
- `02-provider-architecture.md` - Provider architecture
- `03-tool-ecosystem.md` - Tool ecosystem
- `04-features-and-capabilities.md` - Features and capabilities
- `05-api-endpoints-reference.md` - API endpoints reference
- `06-deployment-guide.md` - Deployment guide
- `07-upgrade-roadmap.md` - Upgrade roadmap

**Subdirectories:**
- `api/` - API documentation
- `features/` - Feature documentation
- `providers/` - Provider-specific documentation
- `tools/` - Tool-specific documentation

---

## 🎨 **UX**

User experience documentation (1 file):
- `improvement-strategy.md` - UX improvement strategy

---

## 📦 **ARCHIVE**

Historical and superseded documentation:
- `ARCHIVE-LOG.md` - Archive log
- `DOCUMENTATION_REORGANIZATION_PLAN.md` - Previous reorganization plan
- `DOCUMENTATION_REORGANIZATION_STATUS.md` - Previous reorganization status
- `README.md` - Archive overview
- `abacus/` - Abacus-related archives
- `cleanup_backup_20251003_082921/` - Cleanup backup
- `exai_streamlined_implementation_guide.md` - EXAI implementation guide
- `legacy-scripts/` - Legacy scripts
- `misc/` - Miscellaneous archives
- `old-system-reference-20251003/` - Old system reference
- `old-tool-ecosystem/` - Old tool ecosystem
- `superseded/` - Superseded documentation
- `superseded-20251003/` - Superseded documentation (dated)
- `sweep_reports/` - Sweep reports
- `upgrades/` - Upgrade documentation

---

## 🗂️ **OLDRUN**

Previous Kimi review run data (14 files):
- `KIMI_CODE_REVIEW_src.json` - Previous review results
- `KIMI_RAW_BATCH_1.md` through `KIMI_RAW_BATCH_14.md` - Previous raw responses

---

## 🔍 **NAVIGATION TIPS**

### **Finding Documentation:**

1. **Current Kimi Review Results** → `reviews/kimi/current/`
2. **Project Status** → `project-status/summaries/`
3. **Technical Plans** → `technical/plans/`
4. **User Guides** → `guides/`
5. **System Architecture** → `system-reference/`
6. **Historical Data** → `archive/` or `Oldrun/`

### **Common Tasks:**

- **Check review progress** → `reviews/kimi/current/KIMI_REVIEW_PROGRESS.md`
- **Understand system** → `system-reference/01-system-overview.md`
- **Learn tools** → `guides/tool-selection-guide.md`
- **Find API docs** → `system-reference/05-api-endpoints-reference.md`
- **Review fixes** → `technical/fixes/`

---

## 📝 **MAINTENANCE**

### **Adding New Documentation:**

1. **Review Results** → `reviews/kimi/current/`
2. **Project Summaries** → `project-status/summaries/`
3. **Technical Plans** → `technical/plans/`
4. **Guides** → `guides/`
5. **System Reference** → `system-reference/`

### **Archiving Old Documentation:**

1. Move completed reviews to `reviews/kimi/completed/`
2. Move superseded docs to `archive/superseded/`
3. Update this index

### **Organization Script:**

Use `scripts/organize_docs.py` to reorganize documentation:

```bash
# Dry-run (preview changes)
python scripts/organize_docs.py

# Execute (actually move files)
python scripts/organize_docs.py --execute
```

---

**Total Files Organized:** 43 files  
**Organization Date:** 2025-10-03  
**Organization Script:** `scripts/organize_docs.py`

