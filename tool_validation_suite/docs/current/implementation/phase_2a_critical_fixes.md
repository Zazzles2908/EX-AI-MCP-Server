# Phase 2A: Critical Silent Failure Fixes

**Date:** 2025-10-07  
**Status:** 🚧 IN PROGRESS  
**Approach:** Fix 5-7 most critical silent failures based on impact analysis

---

## 🎯 CRITICAL FAILURE ANALYSIS

### Criteria for "Critical"
1. **Data Integrity Impact** - Affects message content/truncation
2. **Execution Frequency** - Hit on every request
3. **Message Flow Proximity** - In core communication path
4. **User-Facing Impact** - Directly affects user experience

---

## 🔴 PRIORITY 1: Message Handling (CRITICAL)

### Line 532: Semaphore Release Failure
**Current Code:**
```python
try:
    _global_sem.release()
except Exception:
    pass  # ← SILENT FAILURE
```

**Impact:** CRITICAL
- Semaphore not released → Resource leak
- Backpressure system breaks
- Eventually blocks all requests
- Hit on EVERY tool call

**Fix:**
```python
try:
    _global_sem.release()
except Exception as e:
    logger.error(f"Failed to release global semaphore: {e}", exc_info=True)
    # Continue - semaphore state is corrupted but don't block response
```

---

### Line 550: Argument Injection Failure
**Current Code:**
```python
try:
    arguments = dict(arguments)
    arguments.setdefault("_session_id", session_id)
    arguments.setdefault("_call_key", call_key)
except Exception:
    pass  # ← SILENT FAILURE
```

**Impact:** CRITICAL
- Session tracking breaks
- Call deduplication fails
- Affects EVERY tool call
- Causes duplicate executions

**Fix:**
```python
try:
    arguments = dict(arguments)
    arguments.setdefault("_session_id", session_id)
    arguments.setdefault("_call_key", call_key)
except (TypeError, AttributeError) as e:
    logger.warning(f"Failed to inject session metadata into arguments: {e}")
    # Continue with original arguments - tracking will be incomplete but tool can still execute
```

---

### Line 574: Timeout Calculation Failure
**Current Code:**
```python
try:
    # Kimi timeout logic
    ...
except Exception:
    pass  # ← SILENT FAILURE
```

**Impact:** CRITICAL
- Timeout defaults to wrong value
- Can cause premature timeouts
- Affects Kimi web search calls
- User-facing failures

**Fix:**
```python
try:
    # Kimi timeout logic
    ...
except (KeyError, ValueError, TypeError) as e:
    logger.warning(f"Failed to calculate Kimi-specific timeout: {e}, using default")
    # tool_timeout already set to default value above
```

---

## 🟠 PRIORITY 2: Connection Management (HIGH)

### Line 131: PID File Cleanup Failure
**Current Code:**
```python
try:
    if PID_FILE.exists():
        PID_FILE.unlink(missing_ok=True)
except Exception:
    pass  # ← SILENT FAILURE
```

**Impact:** HIGH
- Stale PID files accumulate
- Daemon restart issues
- Port conflicts
- Affects daemon lifecycle

**Fix:**
```python
try:
    if PID_FILE.exists():
        PID_FILE.unlink(missing_ok=True)
except (OSError, PermissionError) as e:
    logger.warning(f"Failed to remove PID file {PID_FILE}: {e}")
    # Continue - stale PID file is not critical for operation
```

---

### Line 186: Cache Cleanup Failure
**Current Code:**
```python
try:
    # Expire old cache entries
    ...
except Exception:
    pass  # ← SILENT FAILURE
```

**Impact:** HIGH
- Memory leak (cache grows unbounded)
- Performance degradation over time
- Affects all requests eventually

**Fix:**
```python
try:
    # Expire old cache entries
    now = time.time()
    expired_keys = [k for k, rec in _results_cache_by_key.items() if now - rec.get("t", 0) > RESULT_TTL_SECS]
    for k in expired_keys:
        _results_cache_by_key.pop(k, None)
except (KeyError, AttributeError, TypeError) as e:
    logger.error(f"Failed to clean up results cache: {e}", exc_info=True)
    # Continue - cache cleanup failure is not critical for current request
```

---

## 🟡 PRIORITY 3: Output Normalization (MEDIUM-HIGH)

### Line 249: Tool Name Normalization Failure
**Current Code:**
```python
try:
    # Strip EXAI-WS suffix
    ...
except Exception:
    pass  # ← SILENT FAILURE
return name
```

**Impact:** MEDIUM-HIGH
- Tool names not normalized
- Affects tool lookup
- Metrics/logging inconsistent
- Hit on every tool call

**Fix:**
```python
try:
    for suf in ("_EXAI-WS", "-EXAI-WS", "_EXAI_WS", "-EXAI_WS"):
        if name.endswith(suf):
            return name[: -len(suf)]
except (AttributeError, TypeError) as e:
    logger.warning(f"Failed to normalize tool name '{name}': {e}")
    # Return original name - normalization is cosmetic
return name
```

---

### Line 635: JSONL Metrics Logging Failure
**Current Code:**
```python
try:
    _jsonl_path.write_text(..., mode="a")
except Exception:
    pass  # ← SILENT FAILURE
```

**Impact:** MEDIUM-HIGH
- Observability blind spots
- Debugging impossible
- Performance metrics lost
- Affects ALL tool calls

**Fix:**
```python
try:
    _jsonl_path.write_text(json.dumps({
        "t": time.time(), "op": "call_tool", "lat": latency,
        "sess": session_id, "name": name, "prov": prov_key or ""
    }) + "\n", mode="a")
except (OSError, PermissionError, IOError) as e:
    logger.error(f"Failed to write JSONL metrics: {e}")
    # Continue - metrics logging failure should not block response
```

---

## 📊 SUMMARY

### Fixes Planned (7 Critical)
1. ✅ Line 532: Semaphore release (CRITICAL - resource leak)
2. ✅ Line 550: Argument injection (CRITICAL - tracking breaks)
3. ✅ Line 574: Timeout calculation (CRITICAL - user-facing)
4. ✅ Line 131: PID file cleanup (HIGH - daemon lifecycle)
5. ✅ Line 186: Cache cleanup (HIGH - memory leak)
6. ✅ Line 249: Tool name normalization (MEDIUM-HIGH - consistency)
7. ✅ Line 635: JSONL metrics (MEDIUM-HIGH - observability)

### Impact Assessment
- **Resource Leaks Fixed:** 2 (semaphore, cache)
- **User-Facing Issues Fixed:** 1 (timeout calculation)
- **Observability Improved:** 1 (JSONL metrics)
- **System Stability Improved:** 3 (PID cleanup, tracking, normalization)

### Remaining Silent Failures
- **Total:** 43 (50 - 7 fixed)
- **Will be addressed in Phase 2C** based on message bus audit trail

---

## 🔧 IMPLEMENTATION APPROACH

### Step 1: Create Backup
```bash
cp src/daemon/ws_server.py src/daemon/ws_server.py.backup
```

### Step 2: Fix Each Critical Failure
- Replace bare `except Exception: pass` with specific exception types
- Add comprehensive logging with `exc_info=True` for critical errors
- Add comments explaining why we continue despite error
- Preserve original behavior (don't change control flow)

### Step 3: Test Each Fix
- Run validation suite
- Test error scenarios
- Verify logging works
- Check no regressions

### Step 4: Document Changes
- Update this tracking document
- Add to master plan progress tracker
- Note any issues encountered

---

## 📝 TESTING CHECKLIST

### Before Fixes
- [ ] Run validation suite (baseline)
- [ ] Check current error rate
- [ ] Review current logs

### After Each Fix
- [ ] Verify specific exception types are correct
- [ ] Test error scenario (trigger the exception)
- [ ] Verify logging appears in logs
- [ ] Verify system continues to function
- [ ] Run validation suite (no regressions)

### After All Fixes
- [ ] Full validation suite run
- [ ] Load testing (if available)
- [ ] Review all new log entries
- [ ] Document any unexpected behavior

---

## 🎓 LESSONS LEARNED

### Best Practices Applied
1. **Specific Exception Types** - Catch only what you expect
2. **Comprehensive Logging** - Always log with exc_info=True
3. **Explain Continuations** - Comment why we continue despite error
4. **Preserve Behavior** - Don't change control flow, just add visibility

### Anti-Patterns Avoided
1. **Bare except** - Never use `except Exception: pass`
2. **Silent failures** - Always log errors
3. **Hiding bugs** - Make errors visible for debugging

---

**Status:** Ready to implement fixes  
**Next:** Create backup and begin systematic fixes  
**Estimated Time:** 2-3 hours

