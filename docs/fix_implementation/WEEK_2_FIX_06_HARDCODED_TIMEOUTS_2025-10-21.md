# Week 2 Fix #6: Hardcoded Timeouts

**Date:** 2025-10-21  
**Status:** ✅ COMPLETE  
**Priority:** HIGH  
**Category:** Configuration Management

---

## 🎯 Problem Statement

Several timeout values were hardcoded in the codebase instead of being configurable via environment variables. This made it difficult to:
- Tune timeouts for different environments (dev/prod)
- Adjust timeouts without code changes
- Maintain consistent timeout configuration
- Debug timeout-related issues

---

## 🔍 Hardcoded Timeouts Found

### 1. Port Listening Check (ws_server.py:285)
```python
# BEFORE:
with socket.create_connection((host, port), timeout=0.25):
```

### 2. Semaphore Health Check Interval (ws_server.py:1661)
```python
# BEFORE:
await asyncio.wait_for(stop_event.wait(), timeout=30.0)  # Check every 30 seconds
```

### 3. Health Writer Session Lock Timeout (ws_server.py:1680)
```python
# BEFORE:
sess_ids = await asyncio.wait_for(_sessions.list_ids(), timeout=2.0)
```

### 4. Health Writer Interval (ws_server.py:1731)
```python
# BEFORE:
await asyncio.wait_for(stop_event.wait(), timeout=10.0)
```

### 5. WebSocket Close Timeout (ws_server.py:1889)
```python
# BEFORE:
close_timeout=1.0,
```

---

## ✅ Solution Implemented

### 1. Added Environment Variables (.env.docker & .env.example)

```bash
# Connection timeouts
EXAI_WS_CLOSE_TIMEOUT=1.0  # WebSocket close timeout (seconds)

# Health monitoring intervals
EXAI_SEMAPHORE_HEALTH_CHECK_INTERVAL=30  # Semaphore health check interval (seconds)
EXAI_HEALTH_WRITER_INTERVAL=10  # Health file update interval (seconds)
EXAI_HEALTH_WRITER_SESSION_LOCK_TIMEOUT=2.0  # Timeout for session lock acquisition (seconds)
EXAI_PORT_CHECK_TIMEOUT=0.25  # Port listening check timeout (seconds)
```

### 2. Updated Code to Use Environment Variables

#### Port Listening Check
```python
# AFTER:
def _is_port_listening(host: str, port: int) -> bool:
    """Check if a port is listening. Week 2 Fix #6 (2025-10-21): Centralized timeout."""
    timeout = float(os.getenv("EXAI_PORT_CHECK_TIMEOUT", "0.25"))
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False
```

#### Semaphore Health Check
```python
# AFTER:
async def _periodic_semaphore_health(stop_event):
    """
    Periodic semaphore health monitoring.
    Week 2 Fix #6 (2025-10-21): Centralized timeout configuration.
    """
    interval = float(os.getenv("EXAI_SEMAPHORE_HEALTH_CHECK_INTERVAL", "30"))
    while not stop_event.is_set():
        await _check_semaphore_health()
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue
```

#### Health Writer Session Lock
```python
# AFTER:
session_lock_timeout = float(os.getenv("EXAI_HEALTH_WRITER_SESSION_LOCK_TIMEOUT", "2.0"))
try:
    sess_ids = await asyncio.wait_for(_sessions.list_ids(), timeout=session_lock_timeout)
except asyncio.TimeoutError:
    logger.warning(f"Health writer timeout getting session IDs (lock held >{session_lock_timeout}s), using empty list")
    sess_ids = []
```

#### Health Writer Interval
```python
# AFTER:
health_interval = float(os.getenv("EXAI_HEALTH_WRITER_INTERVAL", "10"))
try:
    await asyncio.wait_for(stop_event.wait(), timeout=health_interval)
except asyncio.TimeoutError:
    continue
```

#### WebSocket Close Timeout
```python
# AFTER:
close_timeout=float(os.getenv("EXAI_WS_CLOSE_TIMEOUT", "1.0")),  # Week 2 Fix #6 (2025-10-21)
```

---

## 📊 Configuration Hierarchy

### Existing Timeout Configuration (Already Centralized)
✅ **TimeoutConfig class** (config.py) - Coordinated hierarchy
- `SIMPLE_TOOL_TIMEOUT_SECS=30`
- `WORKFLOW_TOOL_TIMEOUT_SECS=180`
- `EXPERT_ANALYSIS_TIMEOUT_SECS=180`
- `GLM_TIMEOUT_SECS=120`
- `KIMI_TIMEOUT_SECS=240`
- Auto-calculated: Daemon (270s), Shim (360s), Client (450s)

### New Timeout Configuration (Week 2 Fix #6)
✅ **Health & Monitoring Timeouts** - Now centralized
- `EXAI_WS_CLOSE_TIMEOUT=1.0`
- `EXAI_SEMAPHORE_HEALTH_CHECK_INTERVAL=30`
- `EXAI_HEALTH_WRITER_INTERVAL=10`
- `EXAI_HEALTH_WRITER_SESSION_LOCK_TIMEOUT=2.0`
- `EXAI_PORT_CHECK_TIMEOUT=0.25`

---

## 🎯 Benefits

### 1. **Configurability**
- All timeouts now adjustable via environment variables
- No code changes required for timeout tuning
- Different values for dev/staging/prod environments

### 2. **Maintainability**
- Single source of truth for timeout configuration
- Clear documentation of all timeout values
- Easier to understand timeout relationships

### 3. **Debuggability**
- Can increase timeouts for debugging without code changes
- Can reduce timeouts for faster failure detection in tests
- Timeout values visible in configuration files

### 4. **Consistency**
- All timeouts follow same pattern (environment variable with default)
- Consistent naming convention (`EXAI_*_TIMEOUT` or `EXAI_*_INTERVAL`)
- Clear comments explaining purpose of each timeout

---

## 📝 Files Modified

1. **`.env.docker`** - Added 5 new timeout configuration variables
2. **`.env.example`** - Added 5 new timeout configuration variables
3. **`src/daemon/ws_server.py`** - Updated 5 hardcoded timeouts to use environment variables

---

## ✅ Validation

### Manual Testing
```bash
# Test with custom timeouts
docker exec exai-mcp-daemon env | grep EXAI_

# Verify defaults are used when not set
docker exec exai-mcp-daemon python -c "import os; print(os.getenv('EXAI_PORT_CHECK_TIMEOUT', '0.25'))"
```

### Configuration Verification
```bash
# Check .env.docker has all new variables
grep "EXAI_.*TIMEOUT\|EXAI_.*_INTERVAL" .env.docker

# Check .env.example matches
grep "EXAI_.*TIMEOUT\|EXAI_.*_INTERVAL" .env.example
```

---

## 🔮 Future Enhancements

### Short-Term
- [ ] Add timeout validation on startup
- [ ] Log timeout values at startup for debugging
- [ ] Add timeout metrics to monitoring dashboard

### Long-Term
- [ ] Create timeout configuration guide
- [ ] Add timeout tuning recommendations for different workloads
- [ ] Implement dynamic timeout adjustment based on load

---

## 📚 Related Documentation

- **[Timeout Configuration Guide](../../tool_validation_suite/docs/current/guides/TIMEOUT_CONFIGURATION_GUIDE.md)** - Comprehensive timeout hierarchy
- **[Week 1 Completion](WEEK_1_COMPLETION_SUMMARY_2025-10-21.md)** - Previous fixes
- **[Monitoring Enhancements](MONITORING_ENHANCEMENTS_2025-10-21.md)** - Related monitoring improvements

---

## 🎓 Lessons Learned

### 1. **Hardcoded Values Are Technical Debt**
Even "reasonable" hardcoded values (like 30 seconds) should be configurable. What works in development may not work in production.

### 2. **Default Values Are Important**
All environment variables should have sensible defaults. The system should work out-of-the-box without configuration.

### 3. **Documentation Is Critical**
Each timeout should have a comment explaining its purpose. Future developers need to understand why a timeout exists and what it controls.

### 4. **Naming Conventions Matter**
Consistent naming (`EXAI_*_TIMEOUT`, `EXAI_*_INTERVAL`) makes configuration easier to understand and maintain.

---

**Status:** ✅ COMPLETE - All hardcoded timeouts centralized and configurable

