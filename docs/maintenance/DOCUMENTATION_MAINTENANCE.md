# Documentation Maintenance Guide
**Last Updated:** 2025-10-04  
**Purpose:** Guidelines for maintaining clean, organized, and useful documentation

---

## 📋 DOCUMENTATION PRINCIPLES

### 1. Single Source of Truth
- Each piece of information should exist in ONE authoritative location
- Use cross-references instead of duplicating content
- Update the authoritative source, not copies

### 2. Discoverability
- All documents must be indexed in `DOCUMENTATION_INDEX.md`
- Use clear, descriptive filenames
- Include metadata (date, status, purpose) at the top of each file

### 3. Freshness
- Mark documents with last updated date
- Archive superseded documents promptly
- Review and update quarterly

### 4. Clarity
- Write for the intended audience (users, developers, contributors)
- Use clear headings and structure
- Include examples where helpful

---

## 📁 DIRECTORY STRUCTURE

### docs/ Root
**Purpose:** Essential, frequently accessed documents  
**Contents:**
- README.md - Project overview
- CURRENT_STATUS.md - Current project status
- DOCUMENTATION_INDEX.md - Complete documentation index
- QUICK_START.md - Getting started guide
- CONTRIBUTING.md - Contribution guidelines
- KIMI_DESIGN_CONTEXT.md - Design context for Kimi

**Rules:**
- Maximum 6-8 files in root
- Only essential, frequently accessed docs
- Must be current and maintained

### docs/project-status/
**Purpose:** Active project tracking and status  
**Contents:**
- ARCHITECTURE_AUDIT_CRITICAL.md - Critical issues
- FIXES_CHECKLIST.md - Fix tracking
- Current architecture flows
- Recent investigation results

**Rules:**
- Maximum 10 files
- Archive files older than 30 days
- Consolidate similar files before archiving

### docs/system-reference/
**Purpose:** System architecture and design documentation  
**Contents:**
- Architecture documentation
- Design decisions
- Technical specifications

**Rules:**
- Keep current and accurate
- Update when architecture changes
- Version control for major changes

### docs/guides/
**Purpose:** User-facing guides and tutorials  
**Contents:**
- How-to guides
- Usage examples
- Best practices

**Rules:**
- Write for end users
- Include examples
- Test examples before publishing

### docs/archive/
**Purpose:** Historical documents and superseded content  
**Contents:**
- Archived project-status files
- Old investigation reports
- Superseded documentation

**Rules:**
- Must have INDEX.md in each archive directory
- Include archival date in directory name
- Cross-reference to current docs

### docs/maintenance/
**Purpose:** Documentation maintenance and templates  
**Contents:**
- This file
- Archiving criteria
- Document templates

**Rules:**
- Keep maintenance docs current
- Update when processes change

---

## 🔄 DOCUMENT LIFECYCLE

### 1. Creation
**When creating a new document:**
1. Choose appropriate directory based on purpose
2. Use descriptive filename (no generic names like README.md in subdirs)
3. Include metadata header:
   ```markdown
   # Document Title
   **Date:** YYYY-MM-DD
   **Status:** Draft/Active/Archived
   **Purpose:** Brief description
   ```
4. Add entry to DOCUMENTATION_INDEX.md
5. Link from related documents

### 2. Maintenance
**Regular maintenance tasks:**
- **Weekly:** Update CURRENT_STATUS.md
- **Monthly:** Review project-status/ for archival candidates
- **Quarterly:** Full documentation review
- **As needed:** Update when code/architecture changes

### 3. Archival
**When to archive:**
- Document is superseded by newer version
- Investigation/project is complete
- Content is historical but may be useful for reference
- File is older than 30 days and not actively referenced

**How to archive:**
1. Review for unique information
2. Extract and consolidate into current docs
3. Create archive directory with date: `archive/category-YYYY-MM-DD/`
4. Move file to archive
5. Update archive INDEX.md
6. Update cross-references in current docs
7. Remove from DOCUMENTATION_INDEX.md or mark as archived

---

## 📝 DOCUMENT TEMPLATES

### Status Document Template
```markdown
# [Feature/Issue] Status
**Date:** YYYY-MM-DD
**Status:** In Progress/Complete/Blocked
**Priority:** High/Medium/Low

## Summary
Brief overview

## Current State
What's done

## Next Steps
What's needed

## Issues
Any blockers
```

### Investigation Report Template
```markdown
# [Topic] Investigation
**Date:** YYYY-MM-DD
**Investigator:** Name
**Status:** Complete/In Progress

## Objective
What we're investigating

## Findings
What we discovered

## Recommendations
What should be done

## Next Steps
Follow-up actions
```

### Architecture Document Template
```markdown
# [Component] Architecture
**Date:** YYYY-MM-DD
**Status:** Current/Proposed/Deprecated

## Overview
High-level description

## Components
Detailed breakdown

## Flows
How it works

## Decisions
Why it's designed this way
```

---

## 🔍 QUALITY CHECKS

### Before Committing Documentation
- [ ] Filename is descriptive and follows conventions
- [ ] Metadata header is complete
- [ ] Content is clear and well-structured
- [ ] Links are valid and working
- [ ] Added to DOCUMENTATION_INDEX.md
- [ ] Cross-references updated
- [ ] Spell-checked and proofread

### Monthly Review Checklist
- [ ] Review all docs in project-status/
- [ ] Archive files older than 30 days
- [ ] Update CURRENT_STATUS.md
- [ ] Check for broken links
- [ ] Consolidate duplicate information
- [ ] Update DOCUMENTATION_INDEX.md

### Quarterly Review Checklist
- [ ] Full documentation audit
- [ ] Update all architecture docs
- [ ] Review and update guides
- [ ] Clean up archive directories
- [ ] Update this maintenance guide
- [ ] Verify all templates are current

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue: Too Many Files in project-status/
**Solution:** Archive files older than 30 days, consolidate similar files

### Issue: Duplicate Information
**Solution:** Identify authoritative source, update it, remove duplicates, add cross-references

### Issue: Broken Links
**Solution:** Use relative paths, update links when moving files, run link checker

### Issue: Outdated Information
**Solution:** Mark with "OUTDATED" banner, update or archive, set review schedule

### Issue: Can't Find Information
**Solution:** Improve DOCUMENTATION_INDEX.md, add search tips, consolidate scattered info

---

## 📊 METRICS

### Documentation Health Indicators
- **File Count:** project-status/ should have <10 files
- **Age:** 80% of docs should be <30 days old
- **Links:** 100% of links should be valid
- **Index:** 100% of docs should be in DOCUMENTATION_INDEX.md
- **Metadata:** 100% of docs should have complete metadata

### Review Schedule
- **Daily:** Update CURRENT_STATUS.md as needed
- **Weekly:** Quick scan of project-status/
- **Monthly:** Full project-status/ review and archival
- **Quarterly:** Complete documentation audit

---

## 🎯 BEST PRACTICES

1. **Write for Your Audience:** Users need guides, developers need architecture docs
2. **Be Concise:** Shorter is better, link to details
3. **Use Examples:** Show, don't just tell
4. **Keep It Current:** Outdated docs are worse than no docs
5. **Link Generously:** Help readers find related information
6. **Archive Promptly:** Don't let old docs clutter active areas
7. **Index Everything:** If it's not in the index, it doesn't exist
8. **Version Control:** Use git for tracking changes
9. **Review Regularly:** Set calendar reminders
10. **Ask for Feedback:** Docs are for readers, not writers

---

## 📞 QUESTIONS?

If you have questions about documentation:
1. Check this guide first
2. Check DOCUMENTATION_INDEX.md
3. Ask in team chat
4. Update this guide with the answer

---

**Maintained By:** Development Team  
**Last Review:** 2025-10-04  
**Next Review:** 2026-01-04

