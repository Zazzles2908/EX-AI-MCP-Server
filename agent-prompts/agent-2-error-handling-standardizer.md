# AGENT 2: ERROR HANDLING STANDARDIZER
## Self-Aware Parallel Execution Agent

**⚠️ CRITICAL: 3 other agents are working simultaneously in separate terminals!**
- Agent 1: Performance optimization (COMPLETES FIRST - you wait for this!)
- Agent 3: Testing infrastructure
- Agent 4: Architecture modernization

**Your work MUST NOT interfere with their work!**

## Agent Identity & Mission

**You are:** Error Handling Standardization Specialist
**Your Goal:** Standardize error handling across the entire codebase using the existing framework
**Priority:** P0 (Critical)
**Execution Order:** SECOND (After Agent 1 completes)

## Context: What You Need to Know

### The Problem
The EX-AI MCP Server has a **well-designed error handling framework** in `src/daemon/error_handling.py` that is **severely underutilized**:
- Framework has 12 error codes and 7 custom exception classes
- **1,497 exception patterns** across 276 files NOT using the framework
- **5,722 logging operations** with inconsistent patterns
- Many files still use `raise Exception()` instead of MCPError classes

### Your Analysis Reports
Read these files for complete context:
- `docs/development/error-handling-standardization-report.md` - Full analysis
- `docs/development/multi-agent-execution-plan.md` - Coordination plan

## Your Files (Safe to Modify)

### Primary Framework (Already exists):
- `src/daemon/error_handling.py` (DO NOT MODIFY - it's perfect!)

### Provider Files to Update:
- `src/providers/glm*.py` (GLM provider errors)
- `src/providers/kimi*.py` (Kimi provider errors)
- `src/providers/openai*.py` (OpenAI provider errors)

### Core System Files to Update:
- `src/daemon/ws/tool_executor.py` (Tool execution errors)
- `src/daemon/ws/request_router.py` (WebSocket errors)
- `src/daemon/monitoring_endpoint.py` (if Agent 1 refactored it, update the new modules)
- `src/server/handlers/*.py` (Request handlers)

### Configuration:
- Any config files that generate errors

## Forbidden Areas (DO NOT TOUCH!)

❌ **NEVER MODIFY:**
- `tools/` directory (tool implementations)
- `src/auth/` directory (security-critical, handled separately)
- `src/security/` directory (security-critical, handled separately)
- `tests/` directory (Agent 3 owns this)
- `docs/` directory (documentation)
- `src/bootstrap/` directory (Agent 4 owns this)
- `src/daemon/error_handling.py` (DON'T CHANGE - framework is perfect!)

## Your Work Sequence

### Phase 1: Wait for Agent 1 ✅
**Before you start, verify Agent 1 completed:**
```bash
# Check if monitoring_endpoint.py was refactored
ls -la src/daemon/monitoring/
# Should show: monitoring/ directory with multiple files
```

### Step 1: Audit Current State
```bash
# Find all files NOT importing error_handling.py
find src/ -name "*.py" -type f -exec grep -L "from src.daemon.error_handling" {} \;

# Count direct exception usage
grep -r "raise Exception" src/ --include="*.py" | wc -l
# Target: Reduce to 0

# Count direct logging usage in error paths
grep -r "logger.error" src/ --include="*.py" | wc -l
# Target: Reduce significantly
```

### Step 2: Update Provider Integrations

**GLM Provider (`src/providers/glm*.py`):**
- Replace `raise Exception("GLM error: ...")` with `raise ProviderError("GLM", e)`
- Replace `logger.error(msg)` with `log_error(ErrorCode.PROVIDER_ERROR, msg, request_id)`
- Ensure all GLM errors use proper error codes

**Kimi Provider (`src/providers/kimi*.py`):**
- Replace `raise Exception("Kimi error: ...")` with `raise ProviderError("Kimi", e)`
- Replace `logger.error(msg)` with `log_error(ErrorCode.PROVIDER_ERROR, msg, request_id)`
- Ensure all Kimi errors use proper error codes

**OpenAI Provider (`src/providers/openai*.py`):**
- Same pattern as GLM and Kimi
- Use ProviderError class

### Step 3: Update Tool Executor
**File:** `src/daemon/ws/tool_executor.py`
- Replace generic exceptions with `ToolExecutionError`
- Use `log_error()` for all error logging
- Ensure request_id correlation

### Step 4: Update WebSocket Handlers
**File:** `src/daemon/ws/request_router.py`
- Replace manual error dict creation with `create_error_response()`
- Use `create_tool_error_response()` for tool errors
- Ensure consistent op="call_tool_res" format

### Step 5: Update HTTP Endpoints
**Files:** `src/server/handlers/*.py`
- Replace `return {"error": str(e)}` with `create_error_response()`
- Use proper error codes for HTTP status codes
- Add request_id to all error responses

### Step 6: Update Monitoring (if refactored)
**Files:** `src/daemon/monitoring/*.py` (if Agent 1 completed)
- Ensure monitoring errors use standardized format
- Use `log_error()` for monitoring issues
- Do NOT modify monitoring_endpoint.py directly (Agent 1 owns that)

## Validation: How to Verify Success

### Run These Checks:

1. **Import check:**
   ```bash
   # Find files that should import but don't
   find src/ -name "*.py" -type f -exec grep -L "from src.daemon.error_handling" {} \; | grep -E "(provider|daemon|server)"
   # Should show: 0 files
   ```

2. **Direct exception check:**
   ```bash
   # Find remaining direct exceptions
   grep -r "raise Exception" src/ --include="*.py" | grep -v "#"
   # Should show: 0 instances (or very few in non-critical code)
   ```

3. **Direct logging check:**
   ```bash
   # Find remaining direct error logging
   grep -r "logger.error" src/daemon/ --include="*.py"
   # Should show: Minimal instances, all justified
   ```

4. **Error response check:**
   ```bash
   # Find manual error dicts
   grep -r '"error".*"message"' src/daemon/ --include="*.py"
   # Should show: 0 instances
   ```

5. **Framework usage check:**
   ```bash
   # Verify framework is being used
   python -c "
   from src.daemon.error_handling import MCPError, ToolNotFoundError, ProviderError
   print('✅ Framework classes importable')
   "
   ```

6. **Provider error check:**
   ```bash
   # Test a provider error
   python -c "
   from src.providers.glm_provider import GLMProvider
   # Verify it uses proper error handling
   "
   ```

7. **Test suite:**
   ```bash
   pytest tests/ -k "error" -v
   # Should pass all error-related tests
   ```

## What Success Looks Like

✅ **Before:**
- 1,497 exception patterns not using framework
- 5,722 logging operations with inconsistencies
- Direct `raise Exception` in provider files
- Manual error dict creation

✅ **After:**
- 0 exception patterns not using framework
- All logging uses `log_error()` utility
- All providers use `ProviderError` class
- All error responses use `create_error_response()`
- All WebSocket errors use `create_tool_error_response()`
- Request ID correlation on all errors

## Code Templates

### Template 1: Provider Error
```python
# ❌ BEFORE
try:
    result = glm_api.call()
except Exception as e:
    raise Exception(f"GLM error: {e}")

# ✅ AFTER
try:
    result = glm_api.call()
except Exception as e:
    raise ProviderError("GLM", e) from e
```

### Template 2: Error Logging
```python
# ❌ BEFORE
logger.error(f"Error processing request: {e}")

# ✅ AFTER
log_error(ErrorCode.TOOL_EXECUTION_ERROR, f"Error processing request: {e}", request_id)
```

### Template 3: Error Response
```python
# ❌ BEFORE
return {"error": {"code": "ERROR", "message": str(e)}}

# ✅ AFTER
return create_error_response(
    code=ErrorCode.TOOL_EXECUTION_ERROR,
    message=str(e),
    request_id=request_id
)
```

## Risk Mitigation

**If you break something:**
1. Don't panic
2. Run: `git diff` to see your changes
3. Test: `python -c "import src.daemon.error_handling"`
4. If broken: `git checkout -- <file>` and try again

**If Agent 1 is still working:**
- Wait! Do NOT start until Agent 1 completes
- Verify: `ls -la src/daemon/monitoring/`
- If monitoring/ exists, Agent 1 is done

**If Agent 3 breaks your tests:**
- They shouldn't - you're not touching tests/
- If they do, they'll fix it

**If Agent 4 changes bootstrap:**
- They might - but bootstrap doesn't use error_handling.py much
- You'll handle it if conflicts arise

## Parallel Agent Awareness

**Agents working simultaneously:**
- Agent 1: Performance (WAIT FOR THIS FIRST!)
- Agent 3: Testing infrastructure (they work on tests/, you work on src/)
- Agent 4: Architecture (they work on bootstrap/, you avoid that)

**Your coordination with them:**
- Wait for Agent 1 to complete performance refactoring
- Work completely independently from Agent 3 and 4
- No file overlap with any agent

**What each agent is doing:**
- Agent 1: Decomposing monitoring_endpoint.py
- Agent 3: Setting up test coverage and CI/CD
- Agent 4: Removing singletons in bootstrap/

## Estimated Time

- **Effort:** 8-12 hours
- **Start:** After Agent 1 validates
- **Parallel with:** Agents 3 and 4

## Start Checklist

Before you begin:
- [ ] Agent 1 has completed (check: `ls src/daemon/monitoring/`)
- [ ] You've read error-handling-standardization-report.md
- [ ] You understand the framework in `src/daemon/error_handling.py`
- [ ] You know your forbidden areas

## Start Now

Verify you can start:
```bash
# Check if Agent 1 is done
ls -la src/daemon/monitoring/ 2>/dev/null && echo "✅ Agent 1 complete - you can start!" || echo "⏳ Wait for Agent 1"

# Check framework exists
python -c "from src.daemon.error_handling import MCPError; print('✅ Framework ready')"

# Find first file to fix
find src/providers/ -name "*.py" -type f | head -1
```

**Go!** Make error handling consistent across the entire codebase! 🛡️
