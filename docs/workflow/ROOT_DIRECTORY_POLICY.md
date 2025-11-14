# Root Directory Policy - ENFORCED

**Status:** ✅ MANDATORY POLICY
**Enforcement:** ALL agents must follow this without exception

---

## 🚨 Root Directory Rules

### ONLY 4 Files Allowed in Root Directory

The project root directory (`/`) **MUST** contain ONLY these 4 files:

1. **`README.md`** - Project overview, navigation hub, quick start
2. **`CLAUDE.md`** - Claude Code configuration, project rules, MCP status
3. **`CHANGELOG.md`** - Version history, release notes
4. **`CONTRIBUTING.md`** - Contribution guidelines

**NO EXCEPTIONS**

---

## ❌ ABSOLUTELY FORBIDDEN in Root

The following **MUST NOT** be created in the root directory:

### Documentation Files
- ❌ Any `.md` files except the 4 listed above
- ❌ `*.md` - Documentation, reports, guides, summaries
- ❌ `ARCHITECTURE.md`, `DESIGN.md`, `API.md`, etc.

### Code Files
- ❌ Any `.py` files
- ❌ Test scripts (`test_*.py`, `*_test.py`)
- ❌ Utility scripts (`fix_*.py`, `check_*.py`, `analyze_*.py`)

### Configuration Files
- ❌ `.json` files (`.mcp.json` is okay, but keep in `.claude/`)
- ❌ `.yaml` or `.yml` files
- ❌ `.toml` files
- ❌ `.cfg` or `.ini` files

### Temporary Files
- ❌ `*.tmp`, `*.temp`, `*_temp.md`
- ❌ `DEBUG.md`, `TODO.md`, `NOTES.md`
- ❌ Any file with "TEMP", "DEBUG", "TODO", "FIXME" in name

### Archives & Reports
- ❌ `FINAL_*.md`, `COMPLETE_*.md`, `REPORT_*.md`
- ❌ Any status reports or summaries
- ❌ `.zip`, `.tar`, `.tar.gz` files

---

## ✅ Correct File Placement

### All Documentation Goes in `documents/`

```
✅ CORRECT:
documents/
├── index.md (main hub)
├── 01-architecture-overview/
├── 02-database-integration/
├── 03-security-authentication/
├── 04-api-tools-reference/
├── 05-operations-management/
├── 06-development-guides/
├── 07-smart-routing/
├── 08-agent-workflow/  ← Agent workflow and policies
├── reports/  ← Any reports or summaries
└── [your docs here]/

❌ WRONG:
/AGENT_WORKFLOW.md (root)
/ENVIRONMENT_SETUP.md (root)
/PROJECT_SUMMARY.md (root)
/ARCHITECTURE.md (root)
```

### All Scripts Go in `scripts/`

```
✅ CORRECT:
scripts/
├── runtime/  ← Runtime scripts
├── ws/  ← WebSocket scripts
├── validation/  ← Validation scripts
├── monitoring/  ← Monitoring scripts
└── [your scripts here]/

❌ WRONG:
/test_exai_mcp.py (root)
/fix_docker.py (root)
/analyze_logs.py (root)
```

### All Tests Go in `tests/`

```
✅ CORRECT:
tests/
├── conftest.py  ← Shared fixtures
├── test_auth.py  ← Auth tests
├── test_api.py  ← API tests
└── [your tests here]/

❌ WRONG:
/test_exai_mcp.py (root)
/*_test.py (root)
```

---

## 🔍 Why This Policy Exists

### Problem: Root Directory Pollution
In the past, agents created files directly in the root:
```
Root directory before cleanup:
├── README.md ✅
├── AGENT_WORKFLOW.md ❌ (should be in documents/)
├── ENVIRONMENT_SETUP.md ❌ (should be in documents/)
├── PROJECT_SUMMARY.md ❌ (should be in documents/)
├── DOCUMENTATION_CLEANUP_SUMMARY.md ❌ (should be in documents/)
├── test_exai_mcp.py ❌ (should be in tests/)
└── ... 15+ other files
```

**Result:** Overwhelming, unprofessional, confusing for new agents

### Solution: Strict Organization
```
Root directory after cleanup:
├── README.md ✅
├── CLAUDE.md ✅
├── CHANGELOG.md ✅
└── CONTRIBUTING.md ✅

Only 4 files! Clean, professional, easy to navigate.
```

---

## 🚨 Docker Build Issue: Legacy Directories

### Problem
The Dockerfile previously had references to non-existent directories:
```dockerfile
# OLD (WRONG):
COPY systemprompts/ ./systemprompts/  # Directory doesn't exist!
COPY streaming/ ./streaming/  # Directory doesn't exist!
```

This caused:
- Agents thinking these directories should exist
- Confusion about project structure
- Root directory pollution

### Solution: Clean Dockerfile
```dockerfile
# NEW (CORRECT):
# Only copy directories that actually exist
COPY src/ ./src/
COPY tools/ ./tools/
COPY configurations/ ./configurations/
# NO references to non-existent directories!
```

**The Dockerfile now ONLY references existing directories, preventing confusion.**

---

## 📋 Agent Checklist: Before Creating Any File

Before creating ANY file, ask:

1. **Is this a documentation file?**
   - YES → Put in `documents/` (appropriate subsection)
   - NO → Continue

2. **Is this a script or code file?**
   - YES → Put in `scripts/` or `tests/`
   - NO → Continue

3. **Is this a configuration file?**
   - YES → Put in `config/` or appropriate subdirectory
   - NO → Continue

4. **Does it match one of the 4 allowed root files?**
   - YES → README.md, CLAUDE.md, CHANGELOG.md, or CONTRIBUTING.md?
   - NO → **DO NOT CREATE IN ROOT!**

**If you can't answer YES to any question, ask for clarification or review this policy.**

---

## ⚠️ Enforcement

### How This Policy is Enforced

1. **Code Review:** All PRs checked for root directory pollution
2. **Automated Checks:** Scripts verify root directory contains only 4 files
3. **Agent Training:** ALL agents must read this policy before starting
4. **Documentation:** Clear structure in `documents/` with index.md in every subdirectory

### Violations Will Be Corrected

If you create files in the root directory:
1. They will be moved to the correct location
2. You will be asked to review this policy
3. The file organization will be corrected

**It's easier to follow the policy than to fix violations!**

---

## 🎯 Summary

| File Type | Correct Location | Example |
|-----------|-----------------|---------|
| Documentation | `documents/` | `documents/08-agent-workflow/AGENT_WORKFLOW.md` |
| Scripts | `scripts/` | `scripts/validation/check_mcp.py` |
| Tests | `tests/` | `tests/test_auth.py` |
| Configuration | `config/` | `config/settings.json` |

**Remember: When in doubt, put it in `documents/` or `scripts/`, NOT in root!**

---

## 🚀 Quick Reference

### Start Here for New Agents
1. Read `documents/08-agent-workflow/AGENT_WORKFLOW.md` (MANDATORY)
2. Read this ROOT_DIRECTORY_POLICY.md
3. Check `documents/index.md` for navigation
4. Review project structure

### Need to Create a File?
1. Determine file type (doc, script, test, config)
2. Choose correct directory (documents/, scripts/, tests/, config/)
3. Follow naming conventions (descriptive, no versions)
4. Create `index.md` if new subdirectory
5. Update parent `index.md` for navigation

**Keep the root clean - only 4 files allowed!**

---

**Policy Established:** 2025-11-14
**Enforcement:** MANDATORY for all agents
**Violations:** Will be corrected immediately
**Success:** Clean, professional, navigable project structure
