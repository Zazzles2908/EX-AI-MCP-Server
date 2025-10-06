# IMMEDIATE REMEDIATION PLAN
## Critical Fixes to Restore System Functionality

**Date:** 2025-10-06  
**Based on:** COMPREHENSIVE_SYSTEM_AUDIT_2025-10-06.md  
**Estimated Total Time:** 70 minutes  
**Expected Outcome:** >90% test pass rate, 0% timeouts

---

## PRIORITY 1: CRITICAL FIXES (30 minutes)

### Fix #1: HTTP Client Timeout (5 minutes)

**Problem:** HTTP client has 60s timeout, workflow tools need 300s

**File:** `utils/http_client.py`

**Current (Line 26):**
```python
def __init__(
    self,
    base_url: str,
    *,
    api_key: str | None = None,
    api_key_header: str = "Authorization",
    api_key_prefix: str = "Bearer ",
    timeout: float = 60.0,  # ❌ TOO SHORT
) -> None:
```

**Fix:**
```python
def __init__(
    self,
    base_url: str,
    *,
    api_key: str | None = None,
    api_key_header: str = "Authorization",
    api_key_prefix: str = "Bearer ",
    timeout: float = 300.0,  # ✅ Match WORKFLOW_TOOL_TIMEOUT_SECS
) -> None:
```

**Validation:**
```bash
# After fix, restart daemon and run:
python tool_validation_suite/tests/core_tools/test_analyze.py
# Expected: PASS (not timeout)
```

---

### Fix #2: Document HTTP Timeout in .env.example (5 minutes)

**File:** `.env.example`

**Add after line 184:**
```bash
# -------- HTTP Client Configuration --------
# EX_HTTP_TIMEOUT_SECONDS: Global HTTP client timeout for all provider API calls
# Default: 300 seconds (matches WORKFLOW_TOOL_TIMEOUT_SECS)
# This should be >= WORKFLOW_TOOL_TIMEOUT_SECS to prevent premature timeouts
# Recommended: 300 seconds (5 minutes) for workflow tools
EX_HTTP_TIMEOUT_SECONDS=300
```

**Also update:** `.env` file with the same content

---

### Fix #3: Remove Debug Logging (10 minutes)

**Files to clean:**
1. `src/providers/glm_chat.py` (Lines 101-102, 120, 139)
2. `src/providers/glm.py` (Lines 37-38, 41)
3. `tools/workflow/expert_analysis.py` (All `[PRINT_DEBUG]` statements)

**Replace:**
```python
print(f"[GLM_CHAT_DEBUG] ...")
```

**With:**
```python
logger.debug("...")
```

**Or remove entirely if not needed**

---

### Fix #4: Fix Integration Test Encoding (10 minutes)

**Files to fix:**
- `tool_validation_suite/tests/integration/test_conversation_id_glm.py`
- `tool_validation_suite/tests/integration/test_conversation_id_isolation.py`
- `tool_validation_suite/tests/integration/test_conversation_id_kimi.py`
- `tool_validation_suite/tests/integration/test_file_upload_glm.py`
- `tool_validation_suite/tests/integration/test_file_upload_kimi.py`
- `tool_validation_suite/tests/integration/test_web_search_integration.py`

**Add at top of each file:**
```python
# -*- coding: utf-8 -*-
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

**Or replace Unicode characters:**
```python
# Before:
print("\n✅ Conversation Id Glm...")

# After:
print("\n[PASS] Conversation Id Glm...")
```

---

## PRIORITY 2: HIGH PRIORITY FIXES (30 minutes)

### Fix #5: Activate Supabase Integration (20 minutes)

**Option A: Update All Test Files (Recommended)**

**File:** `tool_validation_suite/scripts/run_all_tests_simple.py`

**Add before running tests:**
```python
from utils.supabase_client import get_supabase_client
import os

# Create test run in Supabase
supabase_client = get_supabase_client()
run_id = supabase_client.create_test_run(
    test_suite_name="Full Validation Suite",
    environment={
        "python_version": sys.version,
        "platform": sys.platform,
        "glm_api_url": os.getenv("GLM_API_URL"),
        "kimi_api_url": os.getenv("KIMI_API_URL"),
    }
)

# Pass run_id to each test via environment variable
os.environ["TEST_RUN_ID"] = run_id
```

**Update:** `tool_validation_suite/utils/test_runner.py`

**Change:**
```python
def __init__(self, run_id: Optional[str] = None):
    self.run_id = run_id or os.getenv("TEST_RUN_ID")  # ✅ Read from env
```

**Option B: Auto-create run_id in TestRunner**

**File:** `tool_validation_suite/utils/test_runner.py`

**Change:**
```python
def __init__(self, run_id: Optional[str] = None):
    if run_id is None:
        # Auto-create run_id if not provided
        from utils.supabase_client import get_supabase_client
        supabase_client = get_supabase_client()
        self.run_id = supabase_client.create_test_run(
            test_suite_name="Individual Test",
            environment={"auto_created": True}
        )
    else:
        self.run_id = run_id
```

**Validation:**
```bash
# After fix, run tests and check Supabase:
python tool_validation_suite/scripts/run_all_tests_simple.py

# Then query Supabase:
SELECT COUNT(*) FROM test_results;  -- Should be > 0
SELECT COUNT(*) FROM watcher_insights;  -- Should be > 0
```

---

### Fix #6: Fix test_self-check.py Syntax Error (5 minutes)

**File:** `tool_validation_suite/tests/advanced_tools/test_self-check.py`

**Problem:** Likely invalid Python syntax (hyphen in filename or code)

**Fix:**
1. Rename file to `test_selfcheck.py` (remove hyphen)
2. Or fix syntax error in the file

**Validation:**
```bash
python tool_validation_suite/tests/advanced_tools/test_selfcheck.py
# Expected: PASS or FAIL (not syntax error)
```

---

### Fix #7: Add Timeout Hierarchy Validation (5 minutes)

**File:** `src/config/timeouts.py` (or create if doesn't exist)

**Add:**
```python
import os
import logging

logger = logging.getLogger(__name__)

def validate_timeout_hierarchy():
    """Validate that timeouts follow the required hierarchy."""
    
    # Get configured timeouts
    http_timeout = float(os.getenv("EX_HTTP_TIMEOUT_SECONDS", "300"))
    workflow_timeout = float(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "300"))
    daemon_timeout = float(os.getenv("EXAI_WS_CALL_TIMEOUT", str(workflow_timeout * 1.5)))
    
    # Validate hierarchy
    errors = []
    
    if http_timeout < workflow_timeout:
        errors.append(
            f"HTTP timeout ({http_timeout}s) must be >= workflow timeout ({workflow_timeout}s)"
        )
    
    if daemon_timeout < workflow_timeout * 1.5:
        errors.append(
            f"Daemon timeout ({daemon_timeout}s) should be >= 1.5x workflow timeout ({workflow_timeout * 1.5}s)"
        )
    
    if errors:
        for error in errors:
            logger.error(f"[TIMEOUT_VALIDATION] {error}")
        raise ValueError(f"Timeout hierarchy validation failed: {'; '.join(errors)}")
    
    logger.info(f"[TIMEOUT_VALIDATION] Hierarchy valid: HTTP={http_timeout}s, Workflow={workflow_timeout}s, Daemon={daemon_timeout}s")

# Call at startup
validate_timeout_hierarchy()
```

**Import in:** `server.py` or `ws_daemon.py`

---

## PRIORITY 3: VERIFICATION (10 minutes)

### Step 1: Restart Daemon

```bash
# Kill existing daemon
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *ws_daemon*"

# Start fresh daemon
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### Step 2: Run Single Workflow Test

```bash
python tool_validation_suite/tests/core_tools/test_analyze.py
```

**Expected:**
- ✅ PASS or FAIL (not TIMEOUT)
- ✅ Completes in <300s
- ✅ Data saved to Supabase

### Step 3: Run Full Test Suite

```bash
python tool_validation_suite/scripts/run_all_tests_simple.py
```

**Expected:**
- ✅ Pass rate: >90% (>33/37)
- ✅ Timeout rate: 0% (0/37)
- ✅ Integration tests: >80% pass (>4/6)
- ✅ Total time: <20 minutes
- ✅ Supabase data: 37 test results

### Step 4: Verify Supabase Data

```bash
# Check Supabase has data
python -c "
from tool_validation_suite.utils.supabase_client import get_supabase_client
client = get_supabase_client()
# Query test results
print('Test results:', client.supabase.table('test_results').select('*').execute())
"
```

**Expected:**
- ✅ test_results table has 37 rows
- ✅ watcher_insights table has data
- ✅ test_runs table has 1 new run

---

## SUCCESS CRITERIA

### Before Fixes:
- ❌ Pass Rate: 62.2% (23/37)
- ❌ Timeout Rate: 18.9% (7/37)
- ❌ Integration Tests: 0% (0/6)
- ❌ Supabase Data: 0 rows
- ❌ Test Duration: 61 minutes

### After Fixes:
- ✅ Pass Rate: >90% (>33/37)
- ✅ Timeout Rate: 0% (0/37)
- ✅ Integration Tests: >80% (>4/6)
- ✅ Supabase Data: 37+ rows
- ✅ Test Duration: <20 minutes

---

## ROLLBACK PLAN

If fixes cause issues:

1. **Revert HTTP timeout:**
   ```bash
   git checkout HEAD -- utils/http_client.py
   ```

2. **Revert debug logging removal:**
   ```bash
   git checkout HEAD -- src/providers/glm_chat.py src/providers/glm.py
   ```

3. **Revert Supabase changes:**
   ```bash
   git checkout HEAD -- tool_validation_suite/utils/test_runner.py
   ```

4. **Restart daemon:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
   ```

---

## NEXT STEPS AFTER FIXES

1. **Commit fixes:**
   ```bash
   git add -A
   git commit -m "fix: Critical timeout and integration fixes - HTTP timeout 300s, Supabase activation, encoding fixes"
   ```

2. **Run full validation:**
   ```bash
   python tool_validation_suite/scripts/run_all_tests_simple.py
   ```

3. **Document results:**
   - Update `tool_validation_suite/docs/current/INDEX.md`
   - Create `FIXES_VALIDATION_REPORT.md`

4. **Plan next improvements:**
   - Add CI/CD
   - Add unit tests for providers
   - Refactor workarounds
   - Improve documentation

---

**Status:** Ready for implementation  
**Risk Level:** LOW (changes are minimal and targeted)  
**Estimated Success Rate:** 95%  
**Blocking Issues:** None

