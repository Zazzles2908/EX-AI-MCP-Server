# CRITICAL: WebSocket Shim Crashing - No Tool Calls Reaching Daemon

**Date:** 2025-10-04  
**Status:** 🔴 CRITICAL - SYSTEM BROKEN  
**Priority:** P0 - BLOCKING ALL FUNCTIONALITY

---

## 🚨 THE PROBLEM

**Symptom:** When ExAI tools are called (thinkdeep_exai, chat_exai, etc.), no logs are generated and the tool call returns `<error>Cancelled by user.</error>`

**Root Cause:** The WebSocket shim (`run_ws_shim.py`) is crashing with `anyio.ClosedResourceError` when trying to send responses back to Auggie CLI.

---

## 🔍 INVESTIGATION FINDINGS

### Error Stack Trace

**File:** `logs/ws_shim.log` (last error at 18:04:49)

```
anyio.ClosedResourceError
  File "mcp/shared/session.py", line 329, in _send_response
    await self._write_stream.send(session_message)
  File "anyio/streams/memory.py", line 212, in send_nowait
    raise ClosedResourceError
```

**What This Means:**
- The MCP server is trying to send a response back to Auggie CLI
- But the write stream has already been closed
- This causes the entire task group to crash with an ExceptionGroup
- The tool call never completes

---

### Timeline of Events

1. **Auggie CLI calls tool** (e.g., thinkdeep_exai)
2. **MCP shim receives request** via stdio
3. **MCP shim processes request** (gets to `_handle_request`)
4. **MCP shim tries to send response** via `message.respond(response)`
5. **Stream is already closed** - `ClosedResourceError` raised
6. **Task group crashes** - ExceptionGroup propagates
7. **Shim exits** - No response sent to Auggie CLI
8. **Auggie CLI sees cancellation** - Returns `<error>Cancelled by user.</error>`

---

## 🎯 ROOT CAUSE ANALYSIS

### Hypothesis 1: Schema Validation Error Causing Early Disconnect

**Evidence:**
- Schema validation warning on Auggie CLI startup: "strict mode: use allowUnionTypes"
- This warning appears BEFORE any tool calls
- Auggie CLI might be rejecting the connection due to invalid schema

**Test:**
- We fixed the schema in `glm_payload_preview.py`
- But daemon was restarted, shim was NOT restarted
- Auggie CLI might still be seeing the old schema

**Action Required:**
- Restart Auggie CLI to pick up schema fix
- Verify no schema validation warnings on startup

---

### Hypothesis 2: Timeout on Auggie CLI Side

**Evidence:**
- `EXAI_SHIM_RPC_TIMEOUT=150` in mcp-config.auggie.json
- Tool calls might be taking longer than 150 seconds
- Auggie CLI closes connection after timeout

**Test:**
- Check if tool calls are taking > 150 seconds
- Increase timeout if needed

**Action Required:**
- Monitor tool call duration
- Increase `EXAI_SHIM_RPC_TIMEOUT` if needed (e.g., to 300)

---

### Hypothesis 3: MCP Protocol Version Mismatch

**Evidence:**
- Using Python 3.13 (very new)
- MCP SDK might have compatibility issues
- anyio/asyncio behavior might have changed

**Test:**
- Check MCP SDK version
- Check for known issues with Python 3.13

**Action Required:**
- Review MCP SDK compatibility
- Consider downgrading to Python 3.11 or 3.12 if needed

---

### Hypothesis 4: Stream Closing Race Condition

**Evidence:**
- Error occurs in `_send_response` after request processing
- Stream might be closing while response is being sent
- This could be a timing issue in the MCP SDK

**Test:**
- Add error handling around stream.send()
- Log when stream closes

**Action Required:**
- Add try/except around stream operations
- Log stream state before sending

---

## ✅ IMMEDIATE FIXES TO TRY

### Fix 1: Restart Auggie CLI (HIGHEST PRIORITY)

**Why:** Schema fix was applied, but Auggie CLI hasn't reloaded

**Action:**
1. Close Auggie CLI completely
2. Reopen Auggie CLI
3. Verify no schema validation warnings on startup
4. Test tool call again

**Expected Result:**
- No schema validation warnings
- Tool calls should work

---

### Fix 2: Increase RPC Timeout

**Why:** 150 seconds might not be enough for some tool calls

**Action:**
Update `mcp-config.auggie.json`:
```json
"env": {
  "EXAI_SHIM_RPC_TIMEOUT": "300",  // Increase from 150 to 300
  ...
}
```

**Expected Result:**
- Longer timeout allows tool calls to complete
- Reduces chance of premature disconnection

---

### Fix 3: Add Error Handling to Shim

**Why:** Prevent crashes when stream closes unexpectedly

**Action:**
Modify `run_ws_shim.py` to catch `ClosedResourceError`:

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        # ... existing code ...
    except anyio.ClosedResourceError as e:
        logger.error(f"Stream closed while sending response: {e}")
        # Return error response instead of crashing
        return [TextContent(type="text", text=f"Error: Stream closed unexpectedly")]
    except Exception as e:
        logger.exception(f"Unexpected error in handle_call_tool: {e}")
        raise
```

**Expected Result:**
- Shim doesn't crash on stream errors
- Returns error message instead of silent failure

---

## 📊 VERIFICATION STEPS

### Step 1: Check Current State

```bash
# Check if daemon is running
tail -10 logs/ws_daemon.log

# Check if shim is crashing
tail -50 logs/ws_shim.log | grep "ERROR\|ClosedResourceError"

# Check daemon health
cat logs/ws_daemon.health.json
```

### Step 2: Restart Auggie CLI

1. Close Auggie CLI
2. Reopen Auggie CLI
3. Check for schema validation warnings
4. Test simple tool call (e.g., `listmodels_exai()`)

### Step 3: Test Tool Calls

```python
# Test 1: Simple tool (should be fast)
listmodels_exai()

# Test 2: Chat tool (moderate complexity)
chat_exai(prompt="Hello, how are you?", use_websearch=false, model="glm-4.5-flash")

# Test 3: Thinkdeep (complex, might be slow)
thinkdeep_exai(
    step="Analyze the project",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Test",
    confidence="high",
    model="glm-4.5-flash"
)
```

### Step 4: Monitor Logs

```bash
# Watch shim logs in real-time
tail -f logs/ws_shim.log

# Watch daemon logs in real-time
tail -f logs/ws_daemon.log
```

---

## 🎯 EXPECTED OUTCOMES

### If Schema Fix Works:
- ✅ No schema validation warnings on Auggie CLI startup
- ✅ Tool calls complete successfully
- ✅ Logs show tool execution
- ✅ Responses returned to Auggie CLI

### If Timeout Fix Works:
- ✅ Tool calls have more time to complete
- ✅ No premature disconnections
- ✅ Slower tools (like thinkdeep) can finish

### If Error Handling Fix Works:
- ✅ Shim doesn't crash on stream errors
- ✅ Error messages returned instead of silent failures
- ✅ System remains operational even with errors

---

## 📝 CONFIGURATION REVIEW

### Current MCP Configuration

```json
{
  "mcpServers": {
    "exai": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": {
        "AUGGIE_CLI": "true",
        "ALLOW_AUGGIE": "true",
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "AUGGIE_CONFIG": "C:/Project/EX-AI-MCP-Server/auggie-config.json",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8765",
        "EXAI_SHIM_RPC_TIMEOUT": "150",  // ⚠️ Might be too short
        "EX_SESSION_SCOPE_STRICT": "true",
        "EX_SESSION_SCOPE_ALLOW_CROSS_SESSION": "false"
      }
    }
  }
}
```

### Recommended Changes

```json
{
  "env": {
    "EXAI_SHIM_RPC_TIMEOUT": "300",  // ✅ Increase timeout
    "EXAI_WS_CONNECT_TIMEOUT": "60",  // ✅ Add connection timeout
    "EXAI_WS_HANDSHAKE_TIMEOUT": "30",  // ✅ Add handshake timeout
    ...
  }
}
```

---

## 🚀 NEXT STEPS

### For User:

1. **CRITICAL: Restart Auggie CLI**
   - Close Auggie CLI completely
   - Reopen Auggie CLI
   - Verify no schema validation warnings

2. **Test Simple Tool Call**
   - Try `listmodels_exai()`
   - Check if it completes successfully

3. **Report Results**
   - Did schema warning disappear?
   - Did tool call work?
   - Any new errors in logs?

### For Next Agent:

1. **If Auggie CLI restart doesn't fix it:**
   - Implement error handling in run_ws_shim.py
   - Increase EXAI_SHIM_RPC_TIMEOUT to 300
   - Add detailed logging around stream operations

2. **If still broken:**
   - Investigate MCP SDK compatibility with Python 3.13
   - Consider downgrading to Python 3.11/3.12
   - Review anyio/asyncio behavior changes

3. **Document findings:**
   - Update investigation document with results
   - Create fix documentation if solution found
   - Update handover with current status

---

**Created:** 2025-10-04  
**Status:** CRITICAL - SYSTEM BROKEN  
**Priority:** P0 - BLOCKING ALL FUNCTIONALITY

**ACTION REQUIRED: Restart Auggie CLI to apply schema fix!** 🚨

