# Documentation Reorganization Plan
**Date:** 2025-10-14 (14th October 2025)  
**Purpose:** Reorganize scattered documentation into clear categories  
**Status:** PROPOSED

---

## Current Problems

1. **Scattered Files:** 50+ markdown files across multiple directories
2. **Unclear Categories:** Files named by date/topic, not by purpose
3. **Duplicate Content:** Multiple investigation files covering same topics
4. **Hard to Navigate:** No clear entry point or structure

---

## Proposed Structure

```
docs/
├── README.md                          # Navigation guide to all documentation
│
├── 01_ARCHITECTURE/                   # System design and architecture
│   ├── SYSTEM_OVERVIEW.md            # High-level system architecture
│   ├── TOOLS_ARCHITECTURE.md         # 3-layer tool architecture
│   ├── ROUTING_ARCHITECTURE.md       # Model routing and selection
│   ├── PROVIDER_ARCHITECTURE.md      # GLM and Kimi provider design
│   └── DEPENDENCY_MAP.md             # System dependencies
│
├── 02_API_REFERENCE/                  # Provider API documentation
│   ├── GLM_API_REFERENCE.md          # GLM/ZhipuAI API details
│   ├── KIMI_API_REFERENCE.md         # Kimi/Moonshot API details
│   ├── TOOL_SCHEMAS.md               # MCP tool input/output schemas
│   └── ENVIRONMENT_VARIABLES.md      # All env vars with descriptions
│
├── 03_IMPLEMENTATION/                 # Code implementation details
│   ├── THINKING_MODE_IMPLEMENTATION.md    # How thinking mode works
│   ├── WEB_SEARCH_IMPLEMENTATION.md       # Web search for both providers
│   ├── FILE_UPLOAD_IMPLEMENTATION.md      # File handling
│   ├── STREAMING_IMPLEMENTATION.md        # Streaming responses
│   └── CACHING_IMPLEMENTATION.md          # Semantic caching
│
├── 04_TESTING/                        # Test plans, results, evidence
│   ├── TEST_STRATEGY.md              # Overall testing approach
│   ├── UNIT_TESTS.md                 # Unit test documentation
│   ├── INTEGRATION_TESTS.md          # Integration test documentation
│   ├── REAL_WORLD_TESTS.md           # Real-world usage test results
│   └── evidence/                      # Test evidence and results
│       ├── K2_CONSISTENCY_TEST.md
│       ├── THINKING_MODE_TEST.md
│       └── ...
│
├── 05_ISSUES/                         # Bug reports and investigations
│   ├── CRITICAL_BUGS_2025-10-14.md   # 8 critical bugs from real-world testing
│   ├── GOD_CHECKLIST_ISSUES.md       # 4 remaining GOD checklist issues
│   ├── KNOWN_LIMITATIONS.md          # Known limitations and workarounds
│   └── investigations/                # Detailed bug investigations
│       ├── K2_CONSISTENCY_INVESTIGATION.md
│       ├── THINKING_MODE_INVESTIGATION.md
│       └── ...
│
├── 06_PROGRESS/                       # Session summaries and checklists
│   ├── MASTER_CHECKLIST.md           # Current master checklist
│   ├── GOD_CHECKLIST_ORIGINAL.md     # Original GOD checklist (reference)
│   ├── PHASE_SUMMARIES/              # Phase completion summaries
│   │   ├── PHASE_A_STABILIZE.md
│   │   ├── PHASE_B_CLEANUP.md
│   │   └── ...
│   └── SESSION_LOGS/                  # Daily session summaries
│       ├── 2025-10-14_CRITICAL_FIXES.md
│       └── ...
│
├── 07_ARCHIVE/                        # Old/deprecated documentation
│   ├── ARCHAEOLOGICAL_DIG/           # Historical investigation docs
│   ├── planned-features/             # Old planned features
│   └── deprecated/                    # Deprecated documentation
│
└── consolidated_checklist/            # KEEP AS-IS (active work)
    ├── MASTER_CHECKLIST_2025-10-14.md
    ├── ARCHITECTURAL_SANITY_CHECK_2025-10-14.md
    └── ...
```

---

## Migration Plan

### Phase 1: Create New Structure (30 minutes)
- [ ] Create new directory structure
- [ ] Create README.md with navigation guide
- [ ] Create placeholder files in each category

### Phase 2: Categorize Existing Files (2 hours)
- [ ] Review all existing markdown files
- [ ] Assign each file to a category
- [ ] Identify duplicates for consolidation

### Phase 3: Consolidate Content (4 hours)
- [ ] Merge duplicate investigation files
- [ ] Consolidate API documentation
- [ ] Consolidate architecture documentation
- [ ] Update cross-references

### Phase 4: Move Files (1 hour)
- [ ] Move files to new locations
- [ ] Update internal links
- [ ] Verify no broken references

### Phase 5: Cleanup (1 hour)
- [ ] Archive old files
- [ ] Remove duplicates
- [ ] Update main README

---

## File Categorization

### 01_ARCHITECTURE/
**Move Here:**
- `TOOLS_FOLDER_STRUCTURE_ANALYSIS.md`
- `EXISTING_ARCHITECTURE_ANALYSIS.md`
- `DEPENDENCY_MAP.md`
- `DESIGN_INTENT_SUMMARY.md`

**Consolidate Into:**
- `SYSTEM_OVERVIEW.md` (merge multiple architecture docs)
- `ROUTING_ARCHITECTURE.md` (from routing analysis sections)

### 02_API_REFERENCE/
**Create New:**
- `GLM_API_REFERENCE.md` (from API docs you provided)
- `KIMI_API_REFERENCE.md` (from Moonshot docs)
- `ENVIRONMENT_VARIABLES.md` (from .env.example with descriptions)

### 03_IMPLEMENTATION/
**Move Here:**
- `PHASE1_IMPLEMENTATION_SUMMARY_2025-10-14.md`

**Create New:**
- `THINKING_MODE_IMPLEMENTATION.md` (consolidate thinking mode docs)
- `WEB_SEARCH_IMPLEMENTATION.md` (consolidate web search docs)

### 04_TESTING/
**Move Here:**
- All files in `consolidated_checklist/evidence/`
- Test scripts documentation

### 05_ISSUES/
**Move Here:**
- `COMPREHENSIVE_BUG_INVESTIGATION_2025-10-14.md`
- `CRITICAL_ISSUES_ANALYSIS.md`
- `HONEST_STATUS_UPDATE_2025-10-14.md`

**Consolidate Into:**
- `CRITICAL_BUGS_2025-10-14.md` (8 bugs from real-world testing)
- `GOD_CHECKLIST_ISSUES.md` (4 remaining issues)

### 06_PROGRESS/
**Move Here:**
- `MASTER_CHECKLIST_2025-10-14.md`
- `GOD_CHECKLIST_CONSOLIDATED.md`
- All session summaries

### 07_ARCHIVE/
**Move Here:**
- `ARCHAEOLOGICAL_DIG/` (entire directory)
- `planned-features/` (entire directory)
- Old investigation files after consolidation

---

## Navigation Guide (README.md)

```markdown
# EX-AI-MCP-Server Documentation

## Quick Start
- **New to the project?** Start with [System Overview](01_ARCHITECTURE/SYSTEM_OVERVIEW.md)
- **Looking for API docs?** See [API Reference](02_API_REFERENCE/)
- **Need to fix a bug?** Check [Issues](05_ISSUES/)
- **Want to see progress?** View [Master Checklist](06_PROGRESS/MASTER_CHECKLIST.md)

## Documentation Structure

### 01_ARCHITECTURE/
System design, architecture diagrams, and dependency maps.

### 02_API_REFERENCE/
Provider API documentation, tool schemas, and environment variables.

### 03_IMPLEMENTATION/
Code implementation details for key features.

### 04_TESTING/
Test plans, results, and evidence.

### 05_ISSUES/
Bug reports, investigations, and known limitations.

### 06_PROGRESS/
Session summaries, checklists, and phase completion reports.

### 07_ARCHIVE/
Historical documentation and deprecated content.

## Key Documents

- **Master Checklist:** [06_PROGRESS/MASTER_CHECKLIST.md](06_PROGRESS/MASTER_CHECKLIST.md)
- **System Overview:** [01_ARCHITECTURE/SYSTEM_OVERVIEW.md](01_ARCHITECTURE/SYSTEM_OVERVIEW.md)
- **Critical Bugs:** [05_ISSUES/CRITICAL_BUGS_2025-10-14.md](05_ISSUES/CRITICAL_BUGS_2025-10-14.md)
- **GLM API Reference:** [02_API_REFERENCE/GLM_API_REFERENCE.md](02_API_REFERENCE/GLM_API_REFERENCE.md)
- **Kimi API Reference:** [02_API_REFERENCE/KIMI_API_REFERENCE.md](02_API_REFERENCE/KIMI_API_REFERENCE.md)
```

---

## Benefits

1. **Clear Navigation:** Easy to find relevant documentation
2. **No Duplicates:** Consolidated content in single locations
3. **Logical Grouping:** Related docs grouped by purpose
4. **Easy Maintenance:** Clear where new docs should go
5. **Better Onboarding:** New developers can navigate easily

---

## Timeline

- **Phase 1:** 30 minutes (create structure)
- **Phase 2:** 2 hours (categorize files)
- **Phase 3:** 4 hours (consolidate content)
- **Phase 4:** 1 hour (move files)
- **Phase 5:** 1 hour (cleanup)

**Total:** ~8-9 hours (1 full day)

---

## Next Steps

1. **Get Approval:** User reviews and approves this plan
2. **Execute Phase 1:** Create new directory structure
3. **Execute Phase 2-5:** Categorize, consolidate, move, cleanup
4. **Update Master Checklist:** Reflect documentation reorganization

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Status:** PROPOSED - Awaiting user approval

