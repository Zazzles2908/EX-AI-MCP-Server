# Stage 3: Environment Variable Audit Results

**Date:** 2025-10-09 12:30 PM  
**Status:** ✅ COMPLETE

---

## Executive Summary

Comprehensive audit of all `os.getenv()` calls across the codebase revealed:

- **89 missing environment variables** with hardcoded defaults not in .env
- **26 variables in .env** but not found in Python code (may be used dynamically)
- **178 unique environment variables** used across the codebase
- **78 variables currently in .env**

**Critical Finding:** Many important configuration options are hardcoded and not exposed in .env file, making them difficult to configure without code changes.

---

## Audit Methodology

1. Created audit script: `scripts/audit/audit_env_vars.py`
2. Scanned all Python files in `src/`, `tools/`, `scripts/` directories
3. Extracted all `os.getenv()` calls with regex pattern matching
4. Compared against variables in .env file
5. Filtered for variables with non-None defaults (likely intentional configuration)

---

## Key Findings by Category

### High Priority (Should Add to .env)

**Model Configuration:**
- `GLM_SPEED_MODEL=glm-4.5-flash` (used in 7 locations)
- `GLM_QUALITY_MODEL=glm-4.5` (used in 5 locations)
- `KIMI_QUALITY_MODEL=kimi-thinking-preview` (used in 4 locations)
- `CUSTOM_MODEL_NAME=llama3.2`
- `FAST_MODEL_DEFAULT=glm-4.5-flash`
- `LONG_MODEL_DEFAULT=kimi-k2-0711-preview`

**Timeout Configuration:**
- `KIMI_CHAT_TOOL_TIMEOUT_SECS=180`
- `KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS=300`
- `FILE_UPLOAD_TIMEOUT_SECS=120`
- `GLM_WEBSEARCH_TIMEOUT_SECS=30`
- `THINKDEEP_EXPERT_TIMEOUT_SECS=25`
- `FALLBACK_ATTEMPT_TIMEOUT_SECS=60`

**Feature Flags:**
- `ENABLE_INTELLIGENT_SELECTION=true`
- `ENABLE_CONSENSUS_AUTOMODE=true`
- `HIDDEN_MODEL_ROUTER_ENABLED=true`
- `THINK_ROUTING_ENABLED=true`
- `ROUTER_PREFLIGHT_CHAT=true`
- `EX_WEBSEARCH_DEFAULT_ON=true`
- `FALLBACK_ON_FAILURE=true`

**File Handling:**
- `KIMI_FILES_MAX_COUNT=0` (unlimited)
- `KIMI_FILES_BEHAVIOR_ON_OVERSIZE=skip`
- `KIMI_FILES_UPLOAD_TIMEOUT_SECS=90`
- `KIMI_FILES_FETCH_TIMEOUT_SECS=25`
- `FILECACHE_ENABLED=true`

### Medium Priority (Nice to Have)

**Monitoring & Diagnostics:**
- `EX_HEARTBEAT_SECONDS=10`
- `HEARTBEAT_INTERVAL=30`
- `EX_WATCHDOG_WARN_SECONDS=30`
- `EX_WATCHDOG_ERROR_SECONDS=90`
- `ROUTER_DIAGNOSTICS_ENABLED=false`

**Retry & Circuit Breaker:**
- `RETRY_ATTEMPTS=2`
- `RETRY_BACKOFF_BASE=0.5`
- `RETRY_BACKOFF_MAX=4.0`
- `COST_AWARE_ROUTING_ENABLED=false`
- `FREE_TIER_PREFERENCE_ENABLED=false`

**WebSocket Daemon:**
- `EXAI_WS_AUTOSTART=true`
- `EXAI_WS_CONNECT_TIMEOUT=10`
- `EXAI_WS_HANDSHAKE_TIMEOUT=15`
- `EXAI_SHIM_ACK_GRACE_SECS=120`

### Low Priority (Advanced/Experimental)

**Activity Tool:**
- `ACTIVITY_SINCE_UNTIL_ENABLED=false`
- `ACTIVITY_STRUCTURED_OUTPUT_ENABLED=false`

**Expert Analysis:**
- `EXAI_WS_EXPERT_MICROSTEP=false`
- `EXAI_WS_EXPERT_SOFT_DEADLINE_SECS=0`
- `EXPERT_FALLBACK_ON_RATELIMIT=true`

**Synthesis & Router:**
- `SYNTHESIS_ENABLED=false`
- `SYNTHESIS_MODEL=glm-4.5-flash`
- `ROUTER_SENTINEL_MODELS=glm-4.5-flash,auto`

---

## Variables in .env But Not Found in Code

These 26 variables are in .env but not found in Python code scans:

```
CIRCUIT_BREAKER_ENABLED
CIRCUIT_BREAKER_FAILURE_THRESHOLD
CIRCUIT_BREAKER_RECOVERY_TIMEOUT_SECS
ENVIRONMENT
EXAI_WS_INFLIGHT_TTL_SECS
EXAI_WS_MAX_BYTES
EXPERT_ANALYSIS_TIMEOUT_SECS
EX_HTTP_TIMEOUT_SECONDS
FALLBACK_TO_WEBSOCKET
GLM_TIMEOUT_SECS
KIMI_TIMEOUT_SECS
MESSAGE_BUS_*
ROUTER_ENABLED
SIMPLE_TOOL_TIMEOUT_SECS
SUPABASE_*
WORKFLOW_TOOL_TIMEOUT_SECS
ZHIPUAI_BASE_URL
```

**Note:** These may be:
1. Used dynamically (string interpolation)
2. Used in non-Python files (PowerShell scripts, configs)
3. Legacy variables no longer used
4. Reserved for future features

---

## Recommendations

### Immediate Actions (High Priority)

1. **Add Model Configuration Variables**
   - Add GLM_SPEED_MODEL, GLM_QUALITY_MODEL, KIMI_QUALITY_MODEL
   - Ensures consistent model selection across codebase

2. **Add Timeout Configuration Variables**
   - Add all timeout variables to .env
   - Allows tuning without code changes

3. **Add Feature Flag Variables**
   - Add ENABLE_INTELLIGENT_SELECTION, HIDDEN_MODEL_ROUTER_ENABLED, etc.
   - Makes features discoverable and configurable

### Staged Approach

**Phase 1: Critical Variables (Now)**
- Model configuration (6 variables)
- Core timeouts (6 variables)
- Essential feature flags (5 variables)
- Total: ~17 variables

**Phase 2: Important Variables (Next)**
- File handling configuration (8 variables)
- Monitoring & diagnostics (8 variables)
- WebSocket daemon (4 variables)
- Total: ~20 variables

**Phase 3: Advanced Variables (Future)**
- Retry & circuit breaker (7 variables)
- Activity tool (2 variables)
- Expert analysis (3 variables)
- Synthesis & router (3 variables)
- Total: ~15 variables

**Phase 4: Cleanup (Future)**
- Review 26 variables in .env but not in code
- Remove truly unused variables
- Document dynamic/non-Python usage

---

## Next Steps

1. ✅ **Audit Complete** - Script created and run successfully
2. ⏳ **Prioritize Variables** - Categorized into High/Medium/Low priority
3. ⏳ **Add to .env** - Staged approach (Phase 1-4)
4. ⏳ **Update .env.example** - Keep in sync with .env
5. ⏳ **Document Defaults** - Add comments explaining each variable
6. ⏳ **Test Configuration** - Verify all variables work as expected

---

## Audit Script

Created: `scripts/audit/audit_env_vars.py`

**Usage:**
```bash
python scripts/audit/audit_env_vars.py
```

**Features:**
- Scans all Python files for os.getenv() calls
- Extracts variable names and defaults
- Compares against .env file
- Reports missing variables with locations
- Shows variables in .env but not in code

---

## Conclusion

This audit revealed significant configuration debt:
- **89 missing variables** means many settings are hardcoded
- **User's concern was valid** - not everything is in .env
- **Staged approach recommended** - don't add all 89 at once
- **Focus on high-impact variables first** - models, timeouts, feature flags

**Impact:** Improves configurability, reduces code changes for tuning, makes system more maintainable.

