# ENV RELOAD ISSUE - Python Module Caching
**Date:** 2025-10-04  
**Status:** 🔴 CRITICAL - .env changes not taking effect  
**Priority:** P0 - BLOCKING TESTING

---

## 🎯 THE PROBLEM

**Symptom:** Changed `DEFAULT_USE_ASSISTANT_MODEL=false` in `.env`, restarted daemon, but expert validation is still running (use_assistant_model=True in logs).

**Root Cause:** Python module caching prevents `.env` changes from taking effect.

---

## 🔍 TECHNICAL EXPLANATION

### How Python Module Caching Works

1. **First Import:** When `config.py` is imported, it reads environment variables:
   ```python
   # config.py line 102
   DEFAULT_USE_ASSISTANT_MODEL: bool = _parse_bool_env("DEFAULT_USE_ASSISTANT_MODEL", "true")
   ```

2. **Module Cached:** Python caches the imported module in `sys.modules`

3. **Subsequent Imports:** Future imports of `config.py` use the cached version

4. **Variables Don't Update:** Even if `.env` is reloaded, the `config.py` variables stay the same

### Why Daemon Restart Doesn't Help

The `ws_start.ps1 -Restart` script:
1. Calls `ws_stop.ps1` to kill the daemon process
2. Starts a new daemon process

**BUT:** If the daemon doesn't fully exit, or if there's a parent process that stays alive, the Python modules remain cached!

**Evidence from logs:**
```
Stopping WS daemon (PID=26596)...
WS daemon stopped (port free).
Starting WS daemon...
Stopping WS daemon (PID=26596)...  <-- SAME PID!
```

The same PID appears twice, suggesting the process wasn't actually killed.

---

## ✅ THE SOLUTION

### Option 1: Force Restart (RECOMMENDED)

Use the new `force_restart.ps1` script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\force_restart.ps1
```

**What it does:**
1. Stops daemon gracefully
2. **Kills ALL Python processes** (ensures no cached modules)
3. Waits for port to be free
4. Cleans up PID and health files
5. Starts fresh daemon

**Why it works:**
- Kills all Python processes, clearing all module caches
- Ensures completely fresh start
- New Python process loads `.env` from scratch

### Option 2: Manual Kill

```powershell
# Kill all Python processes
Get-Process python* | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Start daemon
powershell -ExecutionPolicy Bypass -File scripts\ws_start.ps1
```

### Option 3: Reboot (NUCLEAR OPTION)

If all else fails, reboot your machine. This guarantees all processes are killed and all caches are cleared.

---

## 🔬 WHY THIS HAPPENED

### The Daemon Restart Issue

Looking at the logs, the daemon restart showed the same PID twice:

```
Stopping WS daemon (PID=26596)...
WS daemon stopped (port free).
Starting WS daemon...
Stopping WS daemon (PID=26596)...  <-- SAME PID AGAIN!
```

**Possible causes:**
1. **Process didn't actually die:** `Stop-Process` might have failed silently
2. **Parent process stayed alive:** If there's a parent process, it might have kept modules cached
3. **Race condition:** New daemon started before old one fully exited
4. **PID reuse:** OS reused the same PID (unlikely but possible)

### The Config Module Issue

Even if the daemon fully restarts, `config.py` is imported at module load time:

```python
# config.py is imported by many modules
from config import DEFAULT_USE_ASSISTANT_MODEL

# This value is set ONCE when config.py is first imported
# It doesn't update even if .env is reloaded later
```

**The only way to update it:** Kill the Python process and start fresh.

---

## 📊 VERIFICATION

**After force restart, check logs for:**

```
[DEBUG_EXPERT] use_assistant_model=False  <-- Should be False now!
```

**If it's still True:**
1. Check `.env` file has `DEFAULT_USE_ASSISTANT_MODEL=false`
2. Check no other `.env` file is being loaded (e.g., `.env.production`)
3. Check no environment variable is set at system level
4. Check `config.py` line 102 for the default value

---

## 🛠️ LONG-TERM FIX

### Implement Hot Reload for Config Module

**Current state:** `_hot_reload_env()` reloads `.env` but doesn't reload `config.py`

**Proposed fix:** Add config module reload:

```python
def _hot_reload_env() -> None:
    """Hot reload environment variables from .env file."""
    load_env(override=True)
    
    # Reload config module to pick up new environment variables
    import importlib
    import config
    importlib.reload(config)
```

**Caveat:** This might break things if other modules have already imported values from `config.py`. Need careful testing.

### Alternative: Use Environment Variables Directly

Instead of caching values in `config.py`, read from environment every time:

```python
# Instead of:
DEFAULT_USE_ASSISTANT_MODEL: bool = _parse_bool_env("DEFAULT_USE_ASSISTANT_MODEL", "true")

# Do:
def get_use_assistant_model() -> bool:
    return _parse_bool_env("DEFAULT_USE_ASSISTANT_MODEL", "true")
```

**Pros:** Always reads fresh value from environment  
**Cons:** Slightly slower, requires code changes throughout codebase

---

## 📝 FILES CREATED

1. **`scripts/force_restart.ps1`** - Force restart script that kills all Python processes
2. **`docs/auggie_reports/ENV_RELOAD_ISSUE_2025-10-04.md`** - This document

---

## 🎯 IMMEDIATE ACTION REQUIRED

**Run the force restart script:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\force_restart.ps1
```

**Then test:**

```python
debug_exai(
    step="Test",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Test",
    hypothesis="Test",
    confidence="high"
)
```

**Expected:** Should complete in < 10 seconds with no expert validation

**If expert validation still runs:** Check logs for `[DEBUG_EXPERT] use_assistant_model=True/False`

---

**Created:** 2025-10-04  
**Status:** READY FOR FORCE RESTART  
**Priority:** P0 - CRITICAL

**Use the force restart script to ensure .env changes take effect!** 🚀

