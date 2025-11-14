# Agent Workflow & Standards

**MANDATORY READING FOR ALL AGENTS**

This section contains the **definitive workflow, standards, and policies** that ALL agents must follow when working on this project.

---

## 📋 Essential Documents (Read in Order)

### 1. **AGENT_WORKFLOW.md** ⭐ MANDATORY FIRST READ
**The single most important document** - Defines the mandatory workflow, file organization rules, testing standards, and quality gates that all agents must follow.

**Contains:**
- Mandatory workflow for all tasks
- File organization requirements (NO files in root!)
- Testing standards (80%+ coverage)
- Quality gates before task completion
- Code quality requirements
- Error handling standards

### 2. **ENVIRONMENT_SETUP.md**
Comprehensive guide to environment file management (5 different .env files).

**Contains:**
- Purpose of each .env file
- Security guidelines
- Docker vs local development
- API key rotation procedures
- Environment variable validation

### 3. **ENVIRONMENT_FILES_README.md**
Quick reference table for environment files.

**Contains:**
- At-a-glance reference
- Which files are git-ignored
- When to use each file
- Security status

### 4. **PROJECT_ORGANIZATION_SUMMARY.md**
Complete project organization guide.

**Contains:**
- Directory structure explanation
- Role of each project component
- Three-tier architecture explanation
- How components interact
- Clear navigation paths

---

## 🚨 Critical Rules

### Root Directory Policy
**ONLY 4 files allowed in root directory:**
1. `README.md` - Project overview and navigation
2. `CLAUDE.md` - Claude Code configuration and rules
3. `CHANGELOG.md` - Version history
4. `CONTRIBUTING.md` - Contribution guidelines

**❌ ABSOLUTELY FORBIDDEN in root:**
- Any `.md` files (except the 4 listed above)
- Any `.py` test scripts
- Any configuration files (`.json`, `.yaml`, etc.)
- Any documentation files
- Any temporary files

**✅ ALL documentation must go in `documents/`**
**✅ ALL scripts must go in `scripts/`**

### Documentation Organization
**Every subdirectory in `documents/` must have `index.md`**

**Structure:**
```
documents/
├── index.md (main hub)
├── 01-architecture-overview/
├── 02-database-integration/
├── 03-security-authentication/
├── 04-api-tools-reference/
├── 05-operations-management/
├── 06-development-guides/
├── 07-smart-routing/
└── 08-agent-workflow/ (this section)
```

---

## 📝 Workflow Summary

### Before Starting ANY Task:
1. **Read** `documents/08-agent-workflow/AGENT_WORKFLOW.md`
2. **Read** `documents/index.md` (documentation hub)
3. **Read** `documents/integration-strategy-checklist.md`
4. Check `CLAUDE.md` for project-specific rules

### During Development:
1. **Follow file organization** - documents/ for docs, scripts/ for scripts
2. **Write tests first** (TDD preferred) - 80%+ coverage required
3. **Use proper error handling** - specific exceptions, logging, actionable messages
4. **Document public APIs** - type hints, docstrings, examples
5. **Update documentation** - maintain accuracy, add examples

### Before Marking Task Complete:
1. All files in correct directories (NO root pollution!)
2. 80%+ test coverage achieved
3. Tests passing locally
4. Documentation updated
5. README.md reflects changes (if needed)
6. CHANGELOG.md updated (if needed)
7. No TODO/FIXME comments remaining
8. Followed AGENT_WORKFLOW.md completely

---

## 🔧 File Naming Conventions

### Markdown Files
- Use descriptive names: `USER_AUTHENTICATION.md` NOT `doc1.md`
- No version numbers: Don't use `FINAL_v2.md`, `COMPLETE.md`
- No duplicates: Each topic should have ONE definitive document
- All lowercase with underscores: `api_reference_guide.md`

### Python Files
- Test files: `test_<module_name>.py`
- Modules: `<module_name>.py` (one class/module per file)
- Scripts: Descriptive names in `scripts/` directory
- No bare except clauses
- Full type hints on public APIs

---

## 🚀 Quick Start for New Agents

### Step 1: Read Mandatory Documents
```bash
# MUST READ THESE IN ORDER:
documents/08-agent-workflow/AGENT_WORKFLOW.md          # ← START HERE
documents/index.md                                     # Documentation hub
documents/integration-strategy-checklist.md            # Master checklist
CLAUDE.md                                              # Project rules
```

### Step 2: Understand Organization
- **Root**: Only 4 files (README, CLAUDE, CHANGELOG, CONTRIBUTING)
- **documents/**: ALL documentation (7 sections + agent workflow)
- **scripts/**: ALL scripts and operational code
- **src/**: Core application source code
- **tests/**: All test files

### Step 3: Check System Status
```bash
# Verify system is operational
curl http://127.0.0.1:3002/health
docker-compose ps

# Check MCP connections
# (See AGENT_WORKFLOW.md for detailed instructions)
```

---

## ⚠️ Common Mistakes to Avoid

### File Placement
❌ **WRONG**: Creating `NEW_FEATURE.md` in root
✅ **RIGHT**: Creating `documents/04-api-tools-reference/new-feature.md`

❌ **WRONG**: Scattered documentation
✅ **RIGHT**: Organized in `documents/` hierarchy

❌ **WRONG**: Test scripts in root
✅ **RIGHT**: Test files in `tests/` directory

### Test Coverage
❌ **WRONG**: Writing code without tests
✅ **RIGHT**: 80%+ coverage for all modules, TDD preferred

❌ **WRONG**: Making real HTTP calls in tests
✅ **RIGHT**: Mocking all external dependencies

### Documentation
❌ **WRONG**: README.md with scattered links
✅ **RIGHT**: Clear navigation with logical sections

❌ **WRONG**: No index.md files in subdirectories
✅ **RIGHT**: Every subdirectory has navigation index.md

---

## 📚 Section Navigation

### Official Documentation Sections
- **01-architecture-overview/** - System architecture and design
- **02-database-integration/** - Database setup and integration
- **03-security-authentication/** - Security and authentication
- **04-api-tools-reference/** - API and tools reference
- **05-operations-management/** - Deployment and operations
- **06-development-guides/** - Development guidelines
- **07-smart-routing/** - Smart routing analysis

### Agent-Specific Section
- **08-agent-workflow/** - This section (MANDATORY for all agents)

---

## 🎯 Success Criteria

### Every Task Must:
- [ ] Follow AGENT_WORKFLOW.md completely
- [ ] Keep root directory clean (only 4 files)
- [ ] Place all documentation in `documents/`
- [ ] Place all scripts in `scripts/`
- [ ] Achieve 80%+ test coverage
- [ ] Pass all tests locally
- [ ] Document public APIs with type hints
- [ ] Use proper error handling (no bare except!)
- [ ] Update documentation as needed
- [ ] Remove all TODO/FIXME comments
- [ ] Follow code quality standards (Linux/Kubernetes patterns)

---

## 🆘 Getting Help

### Documentation
1. Start at `documents/index.md`
2. Check relevant section based on your task
3. Review `documents/integration-strategy-checklist.md`

### System Issues
1. Check `documents/05-operations-management/`
2. Review troubleshooting guides
3. Check logs in `logs/` directory

### Workflow Questions
1. Re-read `documents/08-agent-workflow/AGENT_WORKFLOW.md`
2. Check this index.md for quick answers
3. Review PROJECT_ORGANIZATION_SUMMARY.md

---

**Status:** ✅ Complete - Mandatory for all agents
**Last Updated:** 2025-11-14
**Enforcement:** All agents must follow these standards
