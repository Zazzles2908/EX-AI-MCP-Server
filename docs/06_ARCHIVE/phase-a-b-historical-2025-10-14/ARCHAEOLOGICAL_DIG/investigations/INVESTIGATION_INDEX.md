# ARCHAEOLOGICAL DIG - INVESTIGATIONS CATALOG
**Last Updated:** 2025-10-12 11:45 AM AEDT

---

## 📚 INVESTIGATION OVERVIEW

This folder contains topic-based deep-dive investigations conducted during Phase 1 of the Archaeological Dig.

Each investigation determined whether a component is **ACTIVE**, **ORPHANED**, **DUPLICATE**, or **PLANNED**.

---

## 🔍 INVESTIGATIONS

### 1. [System Prompts](prompts/) ✅ ACTIVE - FULLY INTEGRATED

**Investigation:** SYSTEMPROMPTS_BYPASS_INVESTIGATION.md

**Question:** Is systemprompts/ used or bypassed?

**Finding:** ✅ ACTIVE - Fully integrated
- 14 active imports in tools/ (workflows + chat)
- Execution flow confirmed: import → get_system_prompt() → provider.generate_content()
- No hardcoded bypass detected
- System working as designed

**Recommendation:** ✅ KEEP - No changes needed

---

### 2. [Timezone Utility](timezone/) ✅ ACTIVE - IN USE

**Investigation:** TIMEZONE_DETECTION_STRATEGY.md

**Question:** Is src/utils/timezone.py used?

**Finding:** ✅ ACTIVE - In use
- 2 active imports found
- Used by provider_diagnostics.py for Melbourne timestamps
- Test script exists (scripts/test_timezone.py)
- Adds timestamps to logs/provider_registry_snapshot.json

**Recommendation:** ✅ KEEP - Active and working

**Bonus:** Fixed EXAI codereview error (removed redundant `import time` in expert_analysis.py)

---

### 3. [Model Routing](routing/) ✅ ACTIVE - WORKING AS DESIGNED

**Investigation:** MODEL_ROUTING_REGISTRY_ANALYSIS.md

**Question:** How does model routing work? Why was kimi-latest-128k selected?

**Finding:** ✅ ACTIVE - Working correctly
- 2 providers registered (KIMI, GLM)
- 22 models available
- Clean 3-module architecture (1,079 lines)
- Environment-driven preference system via KIMI_PREFERRED_MODELS/GLM_PREFERRED_MODELS
- kimi-latest-128k selected because KIMI_PREFERRED_MODELS not set (correct behavior)

**Recommendation:** ✅ KEEP - Add KIMI_PREFERRED_MODELS to .env

---

### 4. [Utilities Folder](utilities/) ✅ ACTIVE - NEEDS REORGANIZATION

**Investigation:** UTILS_FOLDER_CHAOS_AUDIT.md

**Question:** Which of the 37 files in utils/ are active?

**Finding:** ✅ ACTIVE - Needs reorganization
- 25 files confirmed ACTIVE (68%)
- 12 files need verification (32%)
- 0 files orphaned
- Top imports: progress.py (24), observability.py (18), conversation_memory.py (15)

**Recommendation:** ✅ KEEP ALL - Reorganize into folders:
- file/ (file utilities)
- conversation/ (conversation management)
- model/ (model utilities)
- config/ (configuration)
- infrastructure/ (observability, health, metrics)

---

### 5. [Monitoring Infrastructure](monitoring/) ⚠️ PLANNED - NOT ACTIVE

**Investigation:** MONITORING_INFRASTRUCTURE_ANALYSIS.md

**Question:** Is monitoring/ active or planned?

**Finding:** ⚠️ PLANNED - Not active
- 0 imports across entire codebase
- No .env configuration (MONITORING_ENABLED, HEALTH_CHECK_INTERVAL, METRICS_SINK missing)
- 9 files exist (8 Python + 1 markdown plan)
- __pycache__ exists (tested but not integrated)
- Redundant with utils/observability.py, utils/health.py, utils/metrics.py

**Recommendation:** 🗑️ DELETE or ARCHIVE - Redundant with existing utils

---

### 6. [Security/RBAC](security/) ⚠️ PLANNED - NOT ACTIVE

**Investigation:** SECURITY_RBAC_IMPLEMENTATION.md

**Question:** Is security/ active or planned?

**Finding:** ⚠️ PLANNED - Not active
- 0 imports across entire codebase
- No .env configuration (RBAC_ENABLED, AUTH_ENABLED missing)
- 2 files exist (rbac.py, rbac_config.py)
- __pycache__ exists (tested but not integrated)
- Single-user system, RBAC not needed

**Recommendation:** 🗑️ DELETE or ARCHIVE - Not needed for single-user system

---

### 7. [Streaming](streaming/) ⚠️ MIXED

**Investigation:** STREAMING_ADAPTER_ARCHITECTURE.md

**Question:** What's the relationship between streaming/ and tools/streaming/?

**Finding:** ⚠️ MIXED
- streaming/: 1 file (streaming_adapter.py), 0 imports, PLANNED
- tools/streaming/: EMPTY directory (only __pycache__)
- No .env configuration (STREAMING_ENABLED missing)

**Recommendation:**
- 🗑️ DELETE tools/streaming/ (empty)
- 🤔 KEEP or DELETE streaming/ (not integrated, decide based on future plans)

---

### 8. [Message Bus](message_bus/) 📋 PLANNED - DESIGN DOCUMENT

**Investigation:** SUPABASE_MESSAGE_BUS_DESIGN.md

**Question:** What is the message bus design?

**Finding:** 📋 PLANNED - Design document only
- Supabase-based message bus design
- Not yet implemented
- Future architecture for system communication

**Recommendation:** 🤔 KEEP - Future architecture design

---

## 📊 INVESTIGATION SUMMARY

**Total Investigations:** 8

**Classification Results:**
- ✅ ACTIVE: 4 (System Prompts, Timezone, Model Routing, Utils)
- ⚠️ PLANNED: 3 (Monitoring, Security, Streaming)
- 📋 DESIGN: 1 (Message Bus)
- 🗑️ ORPHANED: 0

**Cleanup Recommendations:**
- DELETE: monitoring/, security/, tools/streaming/
- REORGANIZE: utils/ (37 files → 6 folders)
- KEEP: systemprompts/, src/utils/timezone.py, model routing, utils/

---

## 🎯 KEY INSIGHTS

### Active Systems Working Well:
1. System prompts fully integrated (14 imports)
2. Timezone utility in use (Melbourne timestamps)
3. Model routing working as designed (environment-driven)
4. Utils folder active but needs organization

### Planned Systems Not Integrated:
1. Monitoring (redundant with existing utils)
2. Security/RBAC (not needed for single-user)
3. Streaming (not integrated)

### No Orphaned Code in Investigations:
- All investigated components are either ACTIVE or PLANNED
- No dead code found in these areas
- Orphaned code found elsewhere (src/conf/, src/config/, etc.)

---

## 🔗 RELATED DOCUMENTATION

**Phase Documentation:**
- [phases/01_PHASE1_DISCOVERY_CLASSIFICATION.md](../phases/01_PHASE1_DISCOVERY_CLASSIFICATION.md)

**Architecture:**
- [architecture/](../architecture/) - System architecture documentation

**Summary:**
- [summary/ARCHAEOLOGICAL_DIG_STATUS_CONSOLIDATED.md](../summary/ARCHAEOLOGICAL_DIG_STATUS_CONSOLIDATED.md)

---

**Last Updated:** 2025-10-12 11:45 AM AEDT  
**Maintained By:** Archaeological Dig reorganization process

