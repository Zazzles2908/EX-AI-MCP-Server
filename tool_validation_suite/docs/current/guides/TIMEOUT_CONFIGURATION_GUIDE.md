# Timeout Configuration Guide

**Last Updated:** 2025-10-07  
**Status:** Active Reference

---

## 📋 Overview

This guide explains the EX-AI-MCP-Server timeout configuration system, including the coordinated hierarchy, auto-calculated values, and how to properly configure timeouts.

---

## 🎯 Key Concepts

### 1. Timeout Hierarchy

The system uses a **coordinated timeout hierarchy** to ensure proper error propagation:

```
HTTP Client → Tool Level → Daemon Level → Shim Level → Client Level
```

**Rule:** Each outer timeout = 1.5x inner timeout (50% buffer)

### 2. Two Types of Timeouts

#### ✅ Configurable (Environment Variables)
These can be set in `.env` file:
- `EX_HTTP_TIMEOUT_SECONDS` - HTTP client timeout (foundation)
- `SIMPLE_TOOL_TIMEOUT_SECS` - Simple tool timeout
- `WORKFLOW_TOOL_TIMEOUT_SECS` - Workflow tool timeout (most important)
- `EXPERT_ANALYSIS_TIMEOUT_SECS` - Expert analysis timeout
- `GLM_TIMEOUT_SECS` - GLM provider timeout
- `KIMI_TIMEOUT_SECS` - Kimi provider timeout
- `KIMI_WEB_SEARCH_TIMEOUT_SECS` - Kimi web search timeout

#### ⚙️ Auto-Calculated (NOT Environment Variables)
These are calculated by `TimeoutConfig` class in `config.py`:
- **Daemon timeout** = 1.5x `WORKFLOW_TOOL_TIMEOUT_SECS`
- **Shim timeout** = 2.0x `WORKFLOW_TOOL_TIMEOUT_SECS`
- **Client timeout** = 2.5x `WORKFLOW_TOOL_TIMEOUT_SECS`

**CRITICAL:** You CANNOT override daemon/shim/client timeouts via environment variables. They are always auto-calculated.

---

## 📊 Default Configuration

### Current Defaults (from .env)

```bash
# HTTP Client (Foundation)
EX_HTTP_TIMEOUT_SECONDS=300

# Tool-level timeouts
SIMPLE_TOOL_TIMEOUT_SECS=60
WORKFLOW_TOOL_TIMEOUT_SECS=300
EXPERT_ANALYSIS_TIMEOUT_SECS=180

# Provider-specific timeouts
GLM_TIMEOUT_SECS=90
KIMI_TIMEOUT_SECS=120
KIMI_WEB_SEARCH_TIMEOUT_SECS=150
```

### Auto-Calculated Infrastructure Timeouts

Based on `WORKFLOW_TOOL_TIMEOUT_SECS=300`:

```
Daemon timeout:  450s (1.5x 300)
Shim timeout:    600s (2.0x 300)
Client timeout:  750s (2.5x 300)
```

---

## 🔧 How to Change Timeouts

### Scenario 1: Increase Workflow Tool Timeout

**Problem:** Workflow tools (analyze, debug, codereview) are timing out.

**Solution:**
1. Edit `.env` file
2. Increase `WORKFLOW_TOOL_TIMEOUT_SECS`:
   ```bash
   WORKFLOW_TOOL_TIMEOUT_SECS=600  # Changed from 300
   ```
3. Restart the server
4. Infrastructure timeouts auto-adjust:
   - Daemon: 900s (1.5x 600)
   - Shim: 1200s (2.0x 600)
   - Client: 1500s (2.5x 600)

### Scenario 2: Increase HTTP Client Timeout

**Problem:** HTTP requests are timing out before workflow completes.

**Solution:**
1. Edit `.env` file
2. Ensure `EX_HTTP_TIMEOUT_SECONDS` >= `WORKFLOW_TOOL_TIMEOUT_SECS`:
   ```bash
   EX_HTTP_TIMEOUT_SECONDS=600  # Must be >= workflow timeout
   WORKFLOW_TOOL_TIMEOUT_SECS=600
   ```
3. Restart the server

**Note:** This was the root cause of the "SDK hanging" issue (was 60s, needed 300s).

### Scenario 3: Increase Provider Timeout

**Problem:** Kimi API calls are timing out.

**Solution:**
1. Edit `.env` file
2. Increase `KIMI_TIMEOUT_SECS`:
   ```bash
   KIMI_TIMEOUT_SECS=180  # Changed from 120
   ```
3. Restart the server

---

## ⚠️ Common Mistakes

### ❌ WRONG: Trying to Set Daemon Timeout in .env

```bash
# This does NOT work - daemon timeout is auto-calculated
EXAI_WS_DAEMON_TIMEOUT=900
```

### ✅ CORRECT: Change Workflow Timeout Instead

```bash
# This works - daemon timeout auto-adjusts to 900s (1.5x 600)
WORKFLOW_TOOL_TIMEOUT_SECS=600
```

---

## 🔍 Validation

The `TimeoutConfig` class includes validation to ensure the hierarchy is correct:

```python
from config import TimeoutConfig

# Validate timeout hierarchy
TimeoutConfig.validate_hierarchy()  # Raises ValueError if invalid

# Get summary of all timeouts
summary = TimeoutConfig.get_summary()
print(summary)
```

**Output:**
```python
{
    "tool_timeouts": {
        "simple": 60,
        "workflow": 300,
        "expert_analysis": 180
    },
    "infrastructure_timeouts": {
        "daemon": 450,
        "shim": 600,
        "client": 750
    },
    "ratios": {
        "daemon_to_tool": 1.5,
        "shim_to_tool": 2.0,
        "client_to_tool": 2.5
    }
}
```

---

## 📁 Related Files

- **`.env`** - Environment variable configuration
- **`.env.example`** - Template with documentation
- **`config.py`** - `TimeoutConfig` class (lines 240-360)
- **`src/daemon/daemon.py`** - Uses `TimeoutConfig.get_daemon_timeout()`
- **`src/daemon/shim.py`** - Uses `TimeoutConfig.get_shim_timeout()`

---

## 🎯 Best Practices

1. **Always start with WORKFLOW_TOOL_TIMEOUT_SECS**
   - This is the foundation for infrastructure timeouts
   - Daemon, shim, and client timeouts auto-adjust

2. **Ensure HTTP timeout >= workflow timeout**
   - HTTP client is the foundation
   - Must be at least as long as the longest tool timeout

3. **Use validation during development**
   - Call `TimeoutConfig.validate_hierarchy()` in tests
   - Ensures timeout hierarchy is always correct

4. **Document timeout changes**
   - Add comments in .env explaining why timeouts were changed
   - Reference issue numbers or investigation documents

5. **Test after changing timeouts**
   - Run workflow tools to ensure they complete
   - Check logs for timeout warnings

---

## 🐛 Troubleshooting

### Problem: "SDK hanging" or "Request timed out"

**Diagnosis:**
1. Check if `EX_HTTP_TIMEOUT_SECONDS` < `WORKFLOW_TOOL_TIMEOUT_SECS`
2. Check if workflow is taking longer than timeout

**Solution:**
1. Increase `WORKFLOW_TOOL_TIMEOUT_SECS` in .env
2. Ensure `EX_HTTP_TIMEOUT_SECONDS` >= `WORKFLOW_TOOL_TIMEOUT_SECS`
3. Restart server

### Problem: "Timeout hierarchy validation failed"

**Diagnosis:**
The `TimeoutConfig.validate_hierarchy()` check failed.

**Solution:**
1. Check that `WORKFLOW_TOOL_TIMEOUT_SECS` is set correctly
2. Ensure no manual overrides of auto-calculated timeouts
3. Restart server to reload configuration

---

## 📚 Historical Context

### Why Auto-Calculated Timeouts?

**Problem (Before):**
- Daemon and shim timeouts were environment variables
- Users could set them incorrectly (e.g., daemon < workflow)
- Led to confusing timeout behavior and hanging

**Solution (Current):**
- Daemon, shim, and client timeouts are auto-calculated
- Always maintain correct hierarchy (1.5x, 2x, 2.5x)
- Users only need to configure `WORKFLOW_TOOL_TIMEOUT_SECS`

**Reference:** See `tool_validation_suite/docs/current/NEW_FINDINGS_FROM_AUDIT_2025-10-07.md` for full investigation.

---

## ✅ Quick Reference

| Timeout | Type | Default | How to Change |
|---------|------|---------|---------------|
| HTTP Client | Env Var | 300s | Set `EX_HTTP_TIMEOUT_SECONDS` in .env |
| Simple Tool | Env Var | 60s | Set `SIMPLE_TOOL_TIMEOUT_SECS` in .env |
| Workflow Tool | Env Var | 300s | Set `WORKFLOW_TOOL_TIMEOUT_SECS` in .env |
| Expert Analysis | Env Var | 180s | Set `EXPERT_ANALYSIS_TIMEOUT_SECS` in .env |
| Daemon | Auto-Calc | 450s | Change `WORKFLOW_TOOL_TIMEOUT_SECS` (1.5x) |
| Shim | Auto-Calc | 600s | Change `WORKFLOW_TOOL_TIMEOUT_SECS` (2.0x) |
| Client | Auto-Calc | 750s | Change `WORKFLOW_TOOL_TIMEOUT_SECS` (2.5x) |

---

**Need Help?** See `docs/current/NEW_FINDINGS_FROM_AUDIT_2025-10-07.md` for detailed investigation of timeout hierarchy design.

