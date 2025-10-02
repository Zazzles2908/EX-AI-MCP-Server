# Documentation Reorganization Plan

**Date**: 2025-09-30  
**Status**: READY FOR EXECUTION  
**Scope**: Complete docs/ directory restructuring

---

## 🎯 Objectives

1. **Separate Active from Archived**: Clear distinction between current and historical docs
2. **Logical Grouping**: Related documentation organized together
3. **Easy Navigation**: Clear structure with index files
4. **Preserve History**: Archive valuable historical context
5. **Remove Clutter**: Eliminate truly obsolete content

---

## 📊 Current State Analysis

### Existing Structure
```
docs/
├── System_layout/          # Architecture docs (CURRENT)
├── augmentcode_phase2/     # Phase 2 refactoring docs (CURRENT)
├── external_review/        # External reviews (CURRENT)
├── tools/                  # Tool documentation (CURRENT)
├── policies/               # Guidelines (CURRENT)
├── implementation_roadmap/ # Roadmap docs (CURRENT)
├── abacus/                 # Abacus-related (UNCLEAR)
├── superseeded/            # Already archived (KEEP)
├── sweep_reports/          # Sweep reports (ARCHIVE)
└── mcp_tool_sweep_report.md # Root-level file (RELOCATE)
```

### Issues Identified
- ✅ Root-level markdown files (should be in subdirectories)
- ✅ `sweep_reports/` should be archived
- ✅ `abacus/` unclear purpose - needs review
- ✅ No clear entry point (README.md)
- ✅ Multiple overlapping directories

---

## 🎯 Proposed Structure

```
docs/
├── README.md                    # Main navigation guide (NEW)
├── DOCUMENTATION_REORGANIZATION_PLAN.md (this file)
├── DOCUMENTATION_REORGANIZATION_COMPLETE.md (after execution)
│
├── current/                     # All active documentation (NEW)
│   ├── README.md               # Current docs index
│   ├── architecture/           # System architecture
│   │   └── (move from System_layout/)
│   ├── development/            # Development guides
│   │   ├── phase1/            # Phase 1 refactoring
│   │   ├── phase2/            # Phase 2 refactoring
│   │   └── implementation_roadmap/
│   ├── tools/                  # Tool documentation (keep as-is)
│   ├── policies/               # Guidelines (keep as-is)
│   └── reviews/                # External reviews
│       └── (move from external_review/)
│
└── archive/                     # Historical documentation (EXPANDED)
    ├── README.md               # Archive index
    ├── superseded/             # (existing, keep)
    ├── sweep_reports/          # (move from root)
    ├── abacus/                 # (move from root if obsolete)
    └── misc/                   # Other archived content
```

---

## 📋 File Categorization

### CURRENT (Keep Active)
**System_layout/** → `current/architecture/`
- All architecture documentation
- Implementation roadmaps
- Decision trees
- API platform docs

**augmentcode_phase2/** → `current/development/phase2/`
- All Phase 2 refactoring documentation
- Completion reports
- Planning docs
- Evidence and analysis

**tools/** → `current/tools/` (no change)
- Tool documentation (analyze, debug, etc.)
- Keep as-is

**policies/** → `current/policies/` (no change)
- AUGMENT_CODE_GUIDELINES.md
- Keep as-is

**external_review/** → `current/reviews/`
- External review sessions
- Validation reports

**implementation_roadmap/** → `current/development/implementation_roadmap/`
- Script inventory
- Phase mapping

### ARCHIVE (Move to archive/)
**sweep_reports/** → `archive/sweep_reports/`
- Historical sweep reports
- No longer actively referenced

**abacus/** → `archive/abacus/` (if obsolete)
- Review contents first
- Archive if not actively used

**mcp_tool_sweep_report.md** → `archive/sweep_reports/`
- Root-level file, should be with other sweep reports

**superseeded/** → `archive/superseded/` (rename for consistency)
- Already archived content
- Keep structure

---

## 🔧 Execution Steps

### Step 1: Create New Structure
```bash
mkdir -p docs/current/architecture
mkdir -p docs/current/development/phase1
mkdir -p docs/current/development/phase2
mkdir -p docs/current/development/implementation_roadmap
mkdir -p docs/current/reviews
mkdir -p docs/archive/sweep_reports
mkdir -p docs/archive/abacus
mkdir -p docs/archive/misc
```

### Step 2: Move Current Documentation
```bash
# Architecture
mv docs/System_layout/* docs/current/architecture/

# Phase 2 Development
mv docs/augmentcode_phase2/* docs/current/development/phase2/

# Reviews
mv docs/external_review/* docs/current/reviews/

# Implementation Roadmap
mv docs/implementation_roadmap/* docs/current/development/implementation_roadmap/

# Tools and Policies (already in good locations, just move to current/)
mv docs/tools docs/current/
mv docs/policies docs/current/
```

### Step 3: Archive Historical Content
```bash
# Sweep reports
mv docs/sweep_reports/* docs/archive/sweep_reports/
mv docs/mcp_tool_sweep_report.md docs/archive/sweep_reports/

# Abacus (if obsolete)
mv docs/abacus/* docs/archive/abacus/

# Rename superseded for consistency
mv docs/superseeded docs/archive/superseded
```

### Step 4: Clean Up Empty Directories
```bash
rmdir docs/System_layout
rmdir docs/augmentcode_phase2
rmdir docs/external_review
rmdir docs/implementation_roadmap
rmdir docs/sweep_reports
rmdir docs/abacus
```

### Step 5: Create Navigation Files
- Create `docs/README.md` (main index)
- Create `docs/current/README.md` (current docs index)
- Create `docs/archive/README.md` (archive index)

---

## 📝 Navigation Structure

### docs/README.md
```markdown
# EX-AI MCP Server Documentation

## Current Documentation
- [Architecture](current/architecture/) - System architecture and design
- [Development](current/development/) - Development guides and refactoring docs
- [Tools](current/tools/) - Tool documentation
- [Policies](current/policies/) - Development guidelines
- [Reviews](current/reviews/) - External reviews and validation

## Archive
- [Historical Documentation](archive/) - Archived and superseded content

## Quick Links
- [Phase 2 Refactoring Complete](current/development/phase2/PHASE2_100_PERCENT_COMPLETE.md)
- [System Architecture](current/architecture/index.md)
- [Tool Documentation](current/tools/)
```

---

## ✅ Success Criteria

- ✅ Clear separation of current vs. archived documentation
- ✅ Logical grouping of related content
- ✅ Easy navigation with README files
- ✅ No broken internal links
- ✅ All valuable content preserved
- ✅ Obsolete content properly archived

---

## 🎯 Benefits

1. **Clarity**: Clear distinction between active and historical docs
2. **Discoverability**: Easy to find relevant documentation
3. **Maintainability**: Logical structure easier to maintain
4. **Scalability**: Room for future documentation growth
5. **Professionalism**: Clean, organized documentation structure

---

## ⚠️ Considerations

1. **Internal Links**: Will need to update after reorganization
2. **External References**: Check if any external tools reference doc paths
3. **Git History**: Moves will be tracked in git history
4. **Backup**: Ensure git commit before reorganization

---

**Status**: READY FOR EXECUTION  
**Estimated Time**: 15-20 minutes  
**Risk Level**: LOW (all moves, no deletions)

