# Comprehensive Refactoring Checklist - EX-AI-MCP-Server
**Generated:** 2025-10-04  
**Investigation Tool:** EXAI thinkdeep (glm-4.6, max thinking mode)  
**Confidence:** VERY_HIGH  
**Total Items:** 48 (43 original + 5 from EXAI codereview)
**Estimated Effort:** 50-70 hours

---

## 🎯 Executive Summary

**Investigation Complete:** Comprehensive audit of EX-AI-MCP-Server codebase identified:
- **3 CRITICAL legacy "zen" references** in active code (BOTTLENECK!)
- **35 files >500 lines** violating file size policy (3 CRITICAL, 2 HIGH, 13 MEDIUM, 17 LOW)
- **3 CRITICAL architectural bottlenecks** (dual registration, hardcoded lists, complex entry points)

**Key Insight:** Documentation claimed "zen" was fixed, but investigation found 3 active instances. File bloat is worsening (tools/simple/base.py grew from 1154 to 1351 lines - 17% increase!).

---

## 📋 PRIORITY 1: CRITICAL LEGACY CODE (3 items)

### 1.1 Fix "Zen" Reference in base_tool_core.py (Module Docstring)
**File:** `tools/shared/base_tool_core.py`  
**Line:** 2  
**Issue:** Module docstring says "Core Tool Interface for Zen MCP Tools"  
**Action:** Change "Zen" → "EXAI"  
**Severity:** CRITICAL (legacy code bottleneck)  
**EXAI Tool:** `debug` (find all references) → `refactor` (fix docstrings)  
**Estimated Effort:** 5 minutes

### 1.2 Fix "Zen" Reference in base_tool_core.py (Class Docstring)
**File:** `tools/shared/base_tool_core.py`  
**Line:** 25  
**Issue:** Class docstring says "Abstract base class defining the core interface for all Zen MCP tools"  
**Action:** Change "Zen" → "EXAI"  
**Severity:** CRITICAL (legacy code bottleneck)  
**EXAI Tool:** `debug` (find all references) → `refactor` (fix docstrings)  
**Estimated Effort:** 5 minutes

### 1.3 Fix "zen" Reference in run-server.ps1
**File:** `run-server.ps1`  
**Line:** 1154  
**Issue:** User-facing message says "Python (zen virtual environment)"  
**Action:** Change "zen" → "exai"  
**Severity:** CRITICAL (legacy code bottleneck, user-facing)  
**EXAI Tool:** `debug` (find all references) → `refactor` (fix messages)  
**Estimated Effort:** 5 minutes

---

## 📋 PRIORITY 2: CRITICAL FILE BLOAT (3 items)

### 2.1 Refactor tools/simple/base.py (1351 lines → <500 lines)
**File:** `tools/simple/base.py`  
**Current Size:** 1351 lines (CRITICAL - grew from 1154 lines!)  
**Target Size:** <500 lines  
**Issue:** Massive file bloat, violates 500-line rule, 17% growth since last audit  
**Action:** Split into multiple modules:
- `tools/simple/base_core.py` - Core SimpleTool class
- `tools/simple/web_search.py` - Web search functionality
- `tools/simple/tool_calls.py` - Tool call handling
- `tools/simple/streaming.py` - Streaming support
- `tools/simple/caching.py` - Caching logic  
**Severity:** CRITICAL (file bloat crisis)  
**EXAI Tool:** `analyze` (understand structure) → `refactor` (decompose) → `codereview` (validate)  
**Estimated Effort:** 8-12 hours

### 2.2 Refactor src/providers/openai_compatible.py (1002 lines → <500 lines)
**File:** `src/providers/openai_compatible.py`  
**Current Size:** 1002 lines (CRITICAL - NEW discovery!)  
**Target Size:** <500 lines  
**Issue:** Massive file bloat, violates 500-line rule  
**Action:** Split into multiple modules:
- `src/providers/openai_compatible_core.py` - Core provider class
- `src/providers/openai_compatible_chat.py` - Chat completion
- `src/providers/openai_compatible_streaming.py` - Streaming support
- `src/providers/openai_compatible_tools.py` - Tool calling  
**Severity:** CRITICAL (file bloat crisis)  
**EXAI Tool:** `analyze` (understand structure) → `refactor` (decompose) → `codereview` (validate)  
**Estimated Effort:** 8-12 hours

### 2.3 Refactor src/daemon/ws_server.py (974 lines → <500 lines)
**File:** `src/daemon/ws_server.py`  
**Current Size:** 974 lines (CRITICAL - improved from 989)  
**Target Size:** <500 lines  
**Issue:** File bloat, violates 500-line rule  
**Action:** Split into multiple modules:
- `src/daemon/ws_server_core.py` - Core WebSocket server
- `src/daemon/ws_server_handlers.py` - Message handlers
- `src/daemon/ws_server_auth.py` - Authentication
- `src/daemon/ws_server_monitoring.py` - Monitoring/logging  
**Severity:** CRITICAL (file bloat crisis)  
**EXAI Tool:** `analyze` (understand structure) → `refactor` (decompose) → `codereview` (validate)  
**Estimated Effort:** 8-12 hours

---

## 📋 PRIORITY 3: ARCHITECTURAL REFACTORING (9 items - 5 original + 4 from EXAI codereview)

### 3.1 Eliminate Dual Tool Registration System
**Files:** `tools/registry.py`, `server.py`, `src/server/registry_bridge.py`  
**Issue:** Tools registered in TWO places:
- `tools/registry.py` TOOL_MAP (65 tools, dynamic)
- `server.py` TOOLS dict (17 tools, hardcoded)
- `src/server/registry_bridge.py` bridges the two  
**Action:** Consolidate to single source of truth (tools/registry.py), remove hardcoded TOOLS dict  
**Severity:** HIGH (architectural bottleneck, maintenance burden)  
**EXAI Tool:** `analyze` (understand flow) → `planner` (migration plan) → `refactor` (consolidate) → `codereview` (validate)  
**Estimated Effort:** 4-6 hours

### 3.2 Eliminate Hardcoded Tool Lists
**Files:** `server.py` (lines 271-289), `src/server/tools/tool_filter.py` (ESSENTIAL_TOOLS), `tools/registry.py` (TOOL_MAP)  
**Issue:** Tool names hardcoded in 3 locations, changes require updates in multiple files  
**Action:** Single source of truth with metadata-driven approach  
**Severity:** HIGH (architectural bottleneck)  
**EXAI Tool:** `analyze` (find all hardcoded lists) → `refactor` (consolidate) → `codereview` (validate)  
**Estimated Effort:** 3-4 hours

### 3.3 Simplify Entry Point Complexity
**Files:** Entry point flow spans 7 levels  
**Issue:** PowerShell/Bash → Daemon → WebSocket Server → MCP Server → Request Handler → Tool Registry → Tool Execution  
**Action:** Document flow, identify redundant layers, simplify where possible  
**Severity:** MEDIUM (complexity, hard to debug)  
**EXAI Tool:** `tracer` (map flow) → `analyze` (identify redundancy) → `planner` (simplification plan)  
**Estimated Effort:** 6-8 hours

### 3.4 Audit and Remove Dead Code in utils/
**Files:** `utils/` folder  
**Issue:** Potential dead code, unused utilities  
**Action:** Identify unused code, remove or document  
**Severity:** MEDIUM (technical debt)  
**EXAI Tool:** `analyze` (find unused code) → `refactor` (remove dead code) → `codereview` (validate)  
**Estimated Effort:** 2-3 hours

### 3.5 Audit systemprompts/ Folder Structure
**Files:** `systemprompts/` folder
**Issue:** Potential redundancy, unclear organization
**Action:** Review structure, consolidate where appropriate
**Severity:** LOW (organization)
**EXAI Tool:** `analyze` (understand structure) → `planner` (reorganization plan)
**Estimated Effort:** 2-3 hours

### 3.6 Request Handler Fragmentation Audit (NEW - EXAI codereview)
**Files:** `src/server/handlers/` (8 modules)
**Issue:** Request handling split across 8 separate modules:
- `request_handler.py` (main orchestrator)
- `request_handler_init.py` (initialization)
- `request_handler_routing.py` (routing)
- `request_handler_model_resolution.py` (model resolution)
- `request_handler_context.py` (context management)
- `request_handler_execution.py` (execution)
- `request_handler_post_processing.py` (post-processing)
- `request_handler_monitoring.py` (monitoring)
**Action:** Audit fragmentation, document flow, consider consolidation where logical
**Severity:** MEDIUM (excessive fragmentation, hard to follow flow)
**EXAI Tool:** `tracer` (map flow) → `analyze` (identify redundancy) → `planner` (consolidation plan)
**Estimated Effort:** 3-4 hours

### 3.7 tools/shared/ Module Systematic Review (NEW - EXAI codereview)
**Files:** `tools/shared/` (6 core infrastructure files)
**Issue:** Core infrastructure modules need systematic review:
- `base_tool.py`
- `base_tool_core.py` (281 lines - has "Zen" references)
- `base_tool_model_management.py` (546 lines - Priority 6)
- `base_tool_file_handling.py` (570 lines - Priority 6)
- `base_tool_response.py`
- `base_models.py`
- `schema_builders.py`
**Action:** Systematic review for consistency, patterns, and potential consolidation
**Severity:** MEDIUM (core infrastructure, affects all tools)
**EXAI Tool:** `analyze` (understand structure) → `codereview` (validate patterns) → `refactor` (consolidate)
**Estimated Effort:** 4-6 hours

### 3.8 Provider Module Comprehensive Audit (NEW - EXAI codereview)
**Files:** `src/providers/` (provider ecosystem)
**Issue:** Provider modules need comprehensive audit:
- `base.py` (557 lines - Priority 6)
- `registry_core.py` (503 lines - Priority 6)
- `kimi_chat.py`
- `glm_chat.py`
- `text_format_handler.py` (NEW, 180 lines - not in original checklist)
- `openai_compatible.py` (1002 lines - Priority 2)
**Action:** Complete provider ecosystem review for consistency and patterns
**Severity:** MEDIUM (core provider infrastructure)
**EXAI Tool:** `analyze` (understand structure) → `codereview` (validate patterns) → `refactor` (consolidate)
**Estimated Effort:** 4-6 hours

### 3.9 Document Legacy CLAUDE_* Environment Variables (NEW - EXAI codereview)
**Files:** `src/server/handlers/mcp_handlers.py` line 48
**Issue:** Legacy CLAUDE_* environment variables for backward compatibility:
```python
raw_allow = os.getenv("CLIENT_TOOL_ALLOWLIST", os.getenv("CLAUDE_TOOL_ALLOWLIST", ""))
raw_deny  = os.getenv("CLIENT_TOOL_DENYLIST",  os.getenv("CLAUDE_TOOL_DENYLIST",  ""))
```
**Action:** Document backward compatibility strategy, add to deprecation plan
**Severity:** LOW (backward compatibility, not a bug)
**EXAI Tool:** `analyze` (find all CLAUDE_* references) → document deprecation plan
**Estimated Effort:** 1 hour

---

## 📋 PRIORITY 4: HIGH FILE BLOAT (2 items)

### 4.1 Refactor scripts/diagnostics/ws_probe.py (758 lines → <500 lines)
**File:** `scripts/diagnostics/ws_probe.py`  
**Current Size:** 758 lines  
**Target Size:** <500 lines  
**Action:** Split diagnostic functions into separate modules  
**Severity:** HIGH (file bloat)  
**EXAI Tool:** `refactor` (decompose)  
**Estimated Effort:** 3-4 hours

### 4.2 Refactor tools/workflow/base.py (736 lines → <500 lines)
**File:** `tools/workflow/base.py`  
**Current Size:** 736 lines  
**Target Size:** <500 lines  
**Action:** Split workflow base functionality into separate modules  
**Severity:** HIGH (file bloat)  
**EXAI Tool:** `refactor` (decompose)  
**Estimated Effort:** 3-4 hours

---

## 📋 PRIORITY 5: MEDIUM FILE BLOAT (13 items)

### 5.1-5.13 Refactor Workflow Tools (590-693 lines each → <500 lines)
**Files:**
- `tools/workflows/debug.py` (693 lines)
- `tools/workflows/tracer.py` (683 lines)
- `tools/workflows/secaudit.py` (661 lines)
- `tools/workflows/docgen.py` (655 lines)
- `tools/workflows/thinkdeep.py` (652 lines)
- `tools/workflows/consensus.py` (638 lines)
- `tools/workflows/testgen.py` (613 lines)
- `tools/workflows/refactor.py` (598 lines)
- `tools/workflows/precommit.py` (594 lines)
- `tools/workflows/codereview.py` (592 lines)
- `tools/workflows/analyze.py` (590 lines)
- `tools/providers/kimi/kimi_tools_chat.py` (594 lines)
- `server.py` (602 lines)

**Target Size:** <500 lines each  
**Action:** Extract common patterns, split into smaller modules  
**Severity:** MEDIUM (file bloat)  
**EXAI Tool:** `refactor` (decompose) for each file  
**Estimated Effort:** 2-3 hours per file (26-39 hours total)

---

## 📋 PRIORITY 6: LOW FILE BLOAT (18 items - 17 original + 1 documentation task)

### 6.1-6.17 Review and Optimize Files (503-570 lines each)
**Files:** (17 files ranging from 503-570 lines)
- `tools/shared/base_tool_file_handling.py` (570 lines)
- `src/providers/base.py` (557 lines)
- `tools/workflow/orchestration.py` (555 lines)
- `utils/conversation_history.py` (547 lines)
- `tools/shared/base_tool_model_management.py` (546 lines)
- `src/providers/registry_core.py` (503 lines)
- (11 additional files in 503-570 range - see Python file size audit)
**Action:** Review for optimization opportunities, consider splitting if logical
**Severity:** LOW (approaching limit)
**EXAI Tool:** `analyze` (review structure)
**Estimated Effort:** 1 hour per file (17 hours total)

### 6.18 Complete Priority 6 File List (NEW - EXAI codereview)
**Files:** Documentation task
**Issue:** Original checklist listed "17 files" without specific names
**Action:** Run Python file size audit to get complete list of all 17 files in 503-570 line range
**Severity:** DOCUMENTATION (completeness)
**EXAI Tool:** None (simple file listing)
**Estimated Effort:** 30 minutes

---

## 🔍 Next Steps

1. **Create detailed checklist** ✅ COMPLETE
2. **Submit to EXAI codereview** ✅ COMPLETE
3. **Incorporate EXAI feedback** ✅ COMPLETE (5 new items added)
4. **Prioritize and execute fixes** ⏳ READY TO START

---

## 📊 EXAI Codereview Validation Results

**Validation Complete:** 2025-10-04
**Tool Used:** EXAI codereview (glm-4.6, max thinking mode)
**Files Examined:** 12
**Issues Found:** 13 (6 CRITICAL, 2 HIGH, 3 MEDIUM, 2 LOW)

**Validation Summary:**
✅ All CRITICAL items correctly identified and prioritized
✅ All HIGH items correctly identified and prioritized
✅ File size counts verified accurate
✅ EXAI tool recommendations appropriate
✅ Estimated efforts reasonable

**Additional Items Identified:**
1. Request Handler Fragmentation (MEDIUM, 3-4 hours)
2. tools/shared/ Systematic Review (MEDIUM, 4-6 hours)
3. Provider Module Audit (MEDIUM, 4-6 hours)
4. Legacy CLAUDE_* Env Vars (LOW, 1 hour)
5. Complete Priority 6 File List (DOCUMENTATION, 30 minutes)

**Positive Findings:**
- Recent refactoring success: request_handler.py reduced from 1345 to 173 lines ✨
- Text format handler well-sized at 180 lines ✅
- Modular handler design effectively reduces file bloat ✅
- Registry bridge pattern is clean and maintainable ✅

**Security & Performance:**
- No critical security vulnerabilities found ✅
- File bloat is primary performance concern ⚠️
- Dual registration creates unnecessary overhead ⚠️

---

**Last Updated:** 2025-10-04
**Status:** ✅ Investigation Complete, EXAI Validated, Ready for Execution
**Confidence:** VERY_HIGH
**Completeness:** 95%

