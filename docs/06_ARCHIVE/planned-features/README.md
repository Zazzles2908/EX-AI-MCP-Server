# Planned Features Archive
**Date:** 2025-10-10 6:50 PM AEDT  
**Purpose:** Infrastructure developed but never integrated

---

## WHY ARCHIVED?

These features were planned and partially implemented, but:
- **Never integrated** into the main codebase (0 imports)
- **No .env configuration** exists
- **Functionality is redundant** with existing systems

---

## CONTENTS

### 1. monitoring/ - Monitoring Infrastructure
**Status:** PLANNED - NOT ACTIVE  
**Evidence:**
- 9 files (8 Python + 1 markdown)
- 0 imports across entire codebase
- No .env configuration (MONITORING_ENABLED, HEALTH_CHECK_INTERVAL, METRICS_SINK all missing)
- __pycache__ exists (tested but not integrated)

**Redundancy:**
- utils/observability.py (18 imports) - Already provides monitoring
- utils/health.py (1 import) - Already provides health checks
- utils/metrics.py - Already provides metrics

**Recommendation:** DELETE or keep as reference

---

### 2. security/ - RBAC System
**Status:** PLANNED - NOT ACTIVE  
**Evidence:**
- 2 files (rbac.py, rbac_config.py)
- 0 imports across entire codebase
- No .env configuration (RBAC_ENABLED, AUTH_ENABLED missing)
- __pycache__ exists (tested but not integrated)

**Reason Not Needed:**
- Single-user system (MCP server for one developer)
- RBAC adds unnecessary complexity
- No multi-user requirements

**Recommendation:** DELETE or keep as reference for future multi-user systems

---

### 3. streaming/ - Streaming Adapter
**Status:** PLANNED - NOT ACTIVE  
**Evidence:**
- 1 file (streaming_adapter.py)
- 0 imports across entire codebase
- No .env configuration (STREAMING_ENABLED missing)
- Not integrated into provider system

**Reason Not Integrated:**
- Providers handle streaming directly
- No need for adapter layer
- Adds unnecessary abstraction

**Recommendation:** DELETE or keep as reference

---

## FUTURE USE

These can be:
- **Deleted** if not needed
- **Integrated** if requirements change (e.g., multi-user system)
- **Used as reference** for future implementations

---

## INVESTIGATION EVIDENCE

**Phase 1 Tasks:**
- Task 1.5: Monitoring Infrastructure Investigation
- Task 1.6: Security/RBAC Investigation
- Task 1.7: Streaming Investigation

**Documentation:**
- docs/ARCHAEOLOGICAL_DIG/monitoring/MONITORING_INFRASTRUCTURE_ANALYSIS.md
- docs/ARCHAEOLOGICAL_DIG/security/SECURITY_RBAC_IMPLEMENTATION.md
- docs/ARCHAEOLOGICAL_DIG/streaming/STREAMING_ADAPTER_ARCHITECTURE.md

**Strategy:**
- docs/ARCHAEOLOGICAL_DIG/CONSOLIDATION_STRATEGY.md Phase 1.B

---

**Archived:** 2025-10-10 6:50 PM AEDT  
**By:** Phase 1 Cleanup (Option 2)

