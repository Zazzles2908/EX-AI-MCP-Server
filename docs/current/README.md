# Current Documentation

This directory contains all active, up-to-date documentation for the EX-AI MCP Server project.

---

## 📁 Directory Structure

### [architecture/](architecture/)
System architecture, design decisions, and technical specifications:
- **API Platforms** - GLM (Z.ai) and Kimi API integration documentation
- **AI Manager** - Intelligent routing and model selection
- **Classification** - Intent analysis and request classification
- **Decision Trees** - Routing logic and decision-making processes
- **Implementation Roadmap** - Technical implementation plans
- **Observability** - Monitoring, logging, and diagnostics
- **Tool Functions** - Tool architecture and implementation

**Key Files**:
- `index.md` - Architecture documentation index
- `IMPLEMENTATION_ROADMAP.md` - Comprehensive implementation roadmap
- `task-manager-implementation-checklist.md` - Task manager implementation guide

### [development/](development/)
Development guides, refactoring documentation, and implementation plans:

#### [phase2/](development/phase2/)
**Phase 2 Workflow Tools Refactoring** (COMPLETE):
- All 8 workflow tools refactored (6,377 → 5,042 lines, 20.9% reduction)
- 18 new focused modules created
- 100% test success rate
- Comprehensive completion reports and documentation

**Key Files**:
- `PHASE2_100_PERCENT_COMPLETE.md` - Final completion report
- `PHASE2_FOLLOWUP_TASKS_COMPLETE.md` - Follow-up tasks completion
- `PHASE1_COMPLETE.md` - Phase 1 workflow mixin refactoring
- `phase2_completion_reports/` - Individual tool completion reports
- `phase2_planning_docs/` - Separation plans and analysis

#### [implementation_roadmap/](development/implementation_roadmap/)
Project roadmaps and phase mapping:
- Script inventory and phase mapping
- Implementation checklists

### [tools/](tools/)
Individual tool documentation (15 tools):

**Workflow Tools**:
- `analyze.md` - Comprehensive code analysis
- `debug.md` - Root cause analysis and debugging
- `codereview.md` - Code review and quality assessment
- `thinkdeep.md` - Complex problem analysis
- `consensus.md` - Multi-model consensus gathering
- `tracer.md` - Code tracing and dependency mapping
- `precommit.md` - Pre-commit validation
- `refactor.md` - Refactoring analysis
- `secaudit.md` - Security audit
- `testgen.md` - Test generation
- `docgen.md` - Documentation generation

**Utility Tools**:
- `chat.md` - General chat and collaborative thinking
- `planner.md` - Interactive sequential planning
- `challenge.md` - Critical analysis and truth-seeking
- `listmodels.md` - Model listing
- `version.md` - Version and configuration

### [policies/](policies/)
Development guidelines and best practices:
- `AUGMENT_CODE_GUIDELINES.md` - Augment Code development guidelines

### [reviews/](reviews/)
External reviews and validation reports:
- GLM agent session logs
- WebSocket probe runs
- External validation reports

---

## 🚀 Quick Start

**New to the project?**
1. Start with [architecture/index.md](architecture/index.md)
2. Review [Phase 2 completion](development/phase2/PHASE2_100_PERCENT_COMPLETE.md)
3. Explore [tool documentation](tools/)

**Looking for specific information?**
- **Architecture** → `architecture/`
- **Refactoring work** → `development/phase2/`
- **Tool usage** → `tools/`
- **Guidelines** → `policies/`

---

## 📊 Project Status

**Phase 1** (Workflow Mixin): ✅ COMPLETE
- workflow_mixin.py refactored (1,937 → 240 lines, 87.6%)
- 5 specialized mixin modules created
- All 8 workflow tools tested and working

**Phase 2** (Workflow Tools): ✅ COMPLETE
- All 8 workflow tools refactored (20.9% average reduction)
- 18 new focused modules created
- 100% test success rate
- Zero breaking changes

**Phase 3** (Providers & Utilities): 🔄 IN PROGRESS
- Started analysis of glm.py
- 6 files targeted for refactoring

---

## 📝 Documentation Standards

All documentation in this directory follows these standards:
- **Markdown format** for all documentation files
- **Descriptive filenames** that clearly indicate content
- **Clear structure** with headers and sections
- **Up-to-date content** - regularly maintained
- **Cross-references** using relative links

---

**Last Updated**: 2025-09-30  
**Status**: Active documentation - regularly maintained

