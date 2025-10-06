# Documentation Archiving Criteria
**Last Updated:** 2025-10-04  
**Purpose:** Guidelines for deciding when and how to archive documentation

---

## 🎯 WHEN TO ARCHIVE

### Automatic Archival Triggers

**Age-Based:**
- Files in `project-status/` older than 30 days
- Investigation reports after investigation is complete
- Session progress files after session ends
- Temporary analysis files after analysis is incorporated

**Status-Based:**
- Documents marked as "Complete" or "Superseded"
- Draft documents that were never finalized
- Experimental approaches that were not adopted
- Failed investigation paths (for historical reference)

**Content-Based:**
- Duplicate information (after consolidation)
- Outdated architecture docs (after update)
- Old test results (after new tests run)
- Historical snapshots (after current state documented)

### Manual Review Required

**Consider archiving if:**
- Document hasn't been accessed in 60 days
- Content is referenced by only one other document
- Information is available in a more current document
- Document is part of a completed project/investigation

**Do NOT archive if:**
- Document is actively referenced by multiple current docs
- Contains unique information not available elsewhere
- Part of ongoing investigation or project
- Required for compliance or audit purposes

---

## 📋 ARCHIVAL PROCESS

### Step 1: Review for Unique Information
**Before archiving, check:**
- [ ] Does this document contain unique information?
- [ ] Is this information available in current docs?
- [ ] Should any information be extracted and consolidated?
- [ ] Are there cross-references that need updating?

### Step 2: Extract and Consolidate
**If unique information exists:**
1. Identify the appropriate current document
2. Extract the unique information
3. Add to current document with proper context
4. Note the source in current document
5. Update last modified date

### Step 3: Create Archive Directory
**Naming convention:**
```
docs/archive/[category]-YYYY-MM-DD/
```

**Examples:**
- `docs/archive/project-status-2025-10-04/`
- `docs/archive/investigations-2025-10-04/`
- `docs/archive/session-reports-2025-10-04/`

### Step 4: Move Files
**Actions:**
1. Move file to archive directory
2. Preserve original filename
3. Do NOT modify file content
4. Keep file metadata intact

### Step 5: Update Archive Index
**Create/update `INDEX.md` in archive directory:**
```markdown
# Archive Index: [Category] - [Date]
**Archived:** YYYY-MM-DD
**Reason:** Brief explanation

## Files in This Archive

### [Filename]
- **Original Location:** docs/project-status/
- **Date Created:** YYYY-MM-DD
- **Reason for Archival:** Superseded by [current doc]
- **Unique Information:** None / Extracted to [current doc]
- **Related Current Docs:** [links]
```

### Step 6: Update Cross-References
**In current documents:**
1. Find all references to archived document
2. Update links to point to archive location
3. Add note: "(archived - see [current doc] for latest)"
4. Or remove reference if no longer relevant

### Step 7: Update Documentation Index
**In `DOCUMENTATION_INDEX.md`:**
- Remove from active sections
- Add to "Archived Documentation" section
- Or remove entirely if not useful for reference

---

## 🔍 ARCHIVAL DECISION MATRIX

| Document Type | Age | Status | Action |
|--------------|-----|--------|--------|
| Investigation Report | >30 days | Complete | Archive |
| Session Progress | >7 days | Complete | Archive |
| Bug Fix Report | >30 days | Fixed | Archive |
| Architecture Doc | Any | Superseded | Archive old, keep new |
| Test Results | >30 days | New tests run | Archive |
| Status Update | >30 days | Outdated | Archive |
| Planning Doc | Any | Project complete | Archive |
| Analysis Report | >30 days | Incorporated | Archive |

---

## 📁 ARCHIVE ORGANIZATION

### Directory Structure
```
docs/archive/
├── project-status-2025-10-04/
│   ├── INDEX.md
│   ├── [archived files]
├── investigations-2025-09-15/
│   ├── INDEX.md
│   ├── [archived files]
└── session-reports-2025-09-01/
    ├── INDEX.md
    └── [archived files]
```

### Archive Categories

**project-status-[DATE]:**
- Session progress files
- Status updates
- Temporary tracking docs

**investigations-[DATE]:**
- Completed investigation reports
- Analysis documents
- Research findings

**architecture-[DATE]:**
- Superseded architecture docs
- Old design decisions
- Deprecated specifications

**testing-[DATE]:**
- Old test results
- Superseded test plans
- Historical benchmarks

---

## ✅ ARCHIVAL CHECKLIST

### Before Archiving
- [ ] Document is eligible for archival (see criteria above)
- [ ] Reviewed for unique information
- [ ] Unique information extracted and consolidated
- [ ] Cross-references identified
- [ ] Archive directory created
- [ ] Archive INDEX.md prepared

### During Archiving
- [ ] File moved to archive directory
- [ ] Archive INDEX.md updated
- [ ] Cross-references updated in current docs
- [ ] DOCUMENTATION_INDEX.md updated
- [ ] Related documents checked for broken links

### After Archiving
- [ ] Verified file is accessible in archive
- [ ] Verified no broken links in current docs
- [ ] Verified unique information is preserved
- [ ] Committed changes to version control

---

## 🚫 DO NOT ARCHIVE

**Never archive:**
- Current architecture documentation
- Active project tracking documents
- Compliance or audit required documents
- Documents with unique information not available elsewhere
- Documents actively referenced by multiple current docs
- Legal or contractual documents

**Consult team before archiving:**
- Documents older than 1 year (may have historical value)
- Documents with significant research or analysis
- Documents that might be needed for future reference
- Documents related to ongoing or recurring issues

---

## 🔄 UNARCHIVING

**When to unarchive:**
- Information becomes relevant again
- Need to reference for new investigation
- Historical context needed for current work

**How to unarchive:**
1. Copy (don't move) from archive to appropriate location
2. Update metadata (mark as "Unarchived from [date]")
3. Review and update content if needed
4. Add to DOCUMENTATION_INDEX.md
5. Note in archive INDEX.md that file was unarchived

---

## 📊 ARCHIVAL METRICS

### Monthly Archival Report
- Number of files archived
- Categories archived
- Unique information extracted
- Archive directory size
- Oldest file in active docs

### Quarterly Archive Review
- Review all archive directories
- Consolidate similar archives
- Delete archives older than 2 years (after team review)
- Update archival criteria based on patterns

---

## 💡 TIPS

1. **Archive Early, Archive Often:** Don't let old docs clutter active areas
2. **Extract First:** Always check for unique information before archiving
3. **Index Everything:** Archive INDEX.md is critical for discoverability
4. **Preserve Context:** Note why document was archived
5. **Update Links:** Broken links frustrate users
6. **Batch Archive:** Archive similar files together for easier organization
7. **Review Regularly:** Monthly archival prevents backlog
8. **Ask If Unsure:** Better to ask than archive something important

---

**Maintained By:** Development Team  
**Last Review:** 2025-10-04  
**Next Review:** 2026-01-04

