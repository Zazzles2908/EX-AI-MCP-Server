# Architecture Documentation

**Purpose:** Central repository for EX-AI-MCP-Server architecture documentation  
**Last Updated:** 2025-01-08

---

## Directory Structure

```
docs/architecture/
├── README.md (this file)
├── releases/           # Version-specific release documentation
├── investigations/     # Deep-dive investigations and audits
└── core-systems/       # Core system architecture documentation
```

---

## 📁 Releases

**Location:** `releases/`

Version-specific documentation for major releases and refactoring efforts.

### v2.0.1 - Polish & Harden
- **File:** `POLISH_AND_HARDEN_v2.0.1.md`
- **Date:** 2025-01-08
- **Summary:** Production-grade polish with tool count hygiene, logging clarity, env documentation, requirements pinning, health JSON improvements, and README badges
- **Impact:** Zero breaking changes - only logs, docs, env order, and JSON format

### v2.0.2 - Orchestrator Sync
- **Files:**
  - `ORCHESTRATOR_SYNC_ANALYSIS_v2.0.2.md` - Investigation findings
  - `ORCHESTRATOR_SYNC_TASKS_v2.0.2.md` - Detailed task list
  - `ORCHESTRATOR_SYNC_COMPLETE_v2.0.2.md` - Completion summary
- **Date:** 2025-01-08
- **Summary:** Hardened registry_bridge to delegate to singleton pattern, preventing second ToolRegistry instance creation
- **Impact:** Zero breaking changes - ensures TOOLS is SERVER_TOOLS identity check always passes

### v2.0.2+ - Spring-Clean Orchestrator Helpers
- **File:** `SPRING_CLEAN_COMPLETE_v2.0.2+.md`
- **Date:** 2025-01-08
- **Summary:** Hardened 4 orchestrator helper files (mcp_handlers, request_handler_init, request_handler_routing, schema_audit) with idempotent guards and architecture notes
- **Impact:** Zero breaking changes - only guards + documentation

---

## 🔍 Investigations

**Location:** `investigations/`

Deep-dive investigations, audits, and analysis reports.

### System Audit 2025-01-08
- **File:** `SYSTEM_AUDIT_2025-01-08.md`
- **Date:** 2025-01-08
- **Summary:** Comprehensive system audit covering package updates, dependency verification, and system readiness
- **Key Findings:** All packages up-to-date, 29 tools registered, system production-ready

---

## 🏗️ Core Systems

**Location:** `core-systems/`

Architecture documentation for core system components.

### Twin Entry Points Safety
- **File:** `TWIN_ENTRY_POINTS_SAFETY.md`
- **Summary:** Documents the dual entry point architecture (server.py and ws_server.py) and how singleton pattern ensures they share the same tools dict
- **Key Concept:** Identity check `TOOLS is SERVER_TOOLS` must always be True

### Service Split
- **File:** `service-split.md`
- **Summary:** Documents the separation between MCP server and WebSocket daemon
- **Architecture:** Explains how both entry points bootstrap the same singleton system

### Backbone X-Ray
- **Directory:** `backbone-xray/`
- **Summary:** Comprehensive analysis of three core subsystems (singletons, providers, request_handler)
- **Files:**
  - `README.md` - Executive summary
  - `ENV_FORENSICS.md` - Why environment flags are false/true
  - `singletons.md` - Singleton initialization system deep-dive
  - `providers.md` - AI provider abstraction deep-dive
  - `request_handler.md` - MCP request pipeline deep-dive
- **Key Findings:** All three subsystems are production-ready with minimal/zero dead code

---

## 📊 Quick Reference

### System Health Checks

```bash
# Identity check (must be True)
python -c "from server import TOOLS; from src.daemon.ws_server import SERVER_TOOLS; print('SAME OBJECT:', TOOLS is SERVER_TOOLS)"

# Tool count (should be 29)
python -c "from server import TOOLS; print('Tool count:', len(TOOLS))"

# Provider status
python -c "from src.providers.registry import ModelProviderRegistry; r = ModelProviderRegistry(); print('Providers:', list(r._providers.keys()))"
```

### Analysis Tools

```bash
# Python backbone tracer
python backbone_tracer.py singletons
python backbone_tracer.py providers
python backbone_tracer.py request_handler

# PowerShell component tracer
powershell -File trace-component.ps1 singletons
```

---

## 🎯 Key Architecture Principles

### 1. Singleton Pattern
- **Purpose:** Ensure single initialization across entry points
- **Implementation:** Module-level flags + idempotent functions
- **Validation:** Identity check (TOOLS is SERVER_TOOLS)
- **Files:** `src/bootstrap/singletons.py`, `src/server/registry_bridge.py`

### 2. Provider Abstraction
- **Purpose:** Unified interface for multiple AI providers
- **Implementation:** Base class + provider-specific implementations
- **Features:** Fallback, health monitoring, cost-aware selection
- **Files:** `src/providers/`, `src/server/providers/`

### 3. Request Pipeline
- **Purpose:** Process MCP tool calls through modular stages
- **Implementation:** 7-stage pipeline with single orchestrator
- **Stages:** Init → Routing → Model Resolution → Context → Monitoring → Execution → Post-Processing
- **Files:** `src/server/handlers/request_handler*.py`

---

## 🔄 Version History

| Version | Date | Summary | Breaking Changes |
|---------|------|---------|------------------|
| v2.0.2+ | 2025-01-08 | Spring-clean orchestrator helpers | None |
| v2.0.2 | 2025-01-08 | Orchestrator sync - harden registry_bridge | None |
| v2.0.1 | 2025-01-08 | Polish & harden - production-grade improvements | None |

---

## 📚 Related Documentation

### System Reference
- `docs/system-reference/` - Definitive design intent baseline
- `docs/System_layout/` - Provider-specific documentation

### Known Issues
- `docs/known_issues/` - Documented bugs and workarounds

### Archive
- `docs/archive/` - Legacy documentation and backup scripts

---

## 🚀 Next Steps

### For New Developers
1. Read `core-systems/backbone-xray/README.md` for system overview
2. Review `releases/` for recent changes
3. Check `investigations/` for deep-dive analysis

### For Maintainers
1. Update release docs when shipping new versions
2. Run analysis tools periodically to detect drift
3. Keep core-systems docs current with architecture changes

---

## 📝 Documentation Standards

### File Naming
- **Releases:** `{TITLE}_v{VERSION}.md` (e.g., `POLISH_AND_HARDEN_v2.0.1.md`)
- **Investigations:** `{TITLE}_{DATE}.md` (e.g., `SYSTEM_AUDIT_2025-01-08.md`)
- **Core Systems:** `{COMPONENT}.md` (e.g., `singletons.md`)

### Content Structure
- Executive summary at top
- Clear sections with headers
- Code examples where relevant
- Troubleshooting guide
- Related documentation links

### Maintenance
- Update README.md when adding new docs
- Archive old docs when superseded
- Keep version history current

---

**Maintainer:** EX-AI-MCP-Server Team  
**Last Review:** 2025-01-08  
**Status:** 🟢 Current

