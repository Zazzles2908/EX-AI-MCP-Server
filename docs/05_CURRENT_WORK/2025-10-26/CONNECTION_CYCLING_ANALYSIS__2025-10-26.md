# Connection Cycling Analysis - 2025-10-26

## 🔍 Current Observation

After updating `.env` to match `.env.docker` ping settings and toggling VSCode MCP servers:

### Connection Pattern (Last 2 Minutes)
```
19:39:38 - Both instances connect (vscode-instance-1 and vscode-instance-2) ✅
19:39:42 - vscode-instance-1 disconnects (duration: 70.18s) 
19:39:53 - Both reconnect (15 seconds later)
19:40:10 - Both reconnect (17 seconds later)
19:40:27 - Both reconnect (17 seconds later)
```

**Pattern:** Connections cycling every 15-30 seconds

---

## 📊 Comparison: Before vs After Fix

### Before Ping Timeout Fix
```
Connection duration: 10-30 seconds
Reconnection interval: 10-15 seconds
Pattern: Very frequent cycling
```

### After Ping Timeout Fix
```
Connection duration: 15-70 seconds
Reconnection interval: 15-30 seconds
Pattern: Still cycling, but slightly longer durations
```

**Improvement:** Connections last longer (70s vs 10s), but still cycling

---

## 🤔 Possible Causes

### 1. VSCode MCP Reconnection Behavior (LIKELY)
VSCode's MCP extension may periodically reconnect to ensure server health. This is **normal behavior** and doesn't indicate a problem if:
- ✅ Tools work correctly when called
- ✅ No errors in logs
- ✅ Reconnections are graceful (no crashes)

### 2. Shim Not Reading Updated .env (UNLIKELY)
The shim reads `.env` on startup via `os.getenv()`. Toggling VSCode MCP should reload the shim with new values.

**Verification needed:**
- Check shim logs for actual ping interval/timeout values
- Confirm .env is being read from correct location

### 3. WebSocket Ping/Pong Still Mismatched (POSSIBLE)
Even though we updated `.env`, there might be:
- Caching issues
- Multiple .env files being read
- Environment variable precedence issues

### 4. Network/Docker Issues (UNLIKELY)
- Docker networking instability
- Windows WSL networking issues
- Firewall interference

---

## ✅ What's Working

1. **Session IDs are respected** ✅
   - Both instances use unique session IDs (vscode-instance-1, vscode-instance-2)
   - No session ID conflicts

2. **Connections are established** ✅
   - Both instances connect successfully
   - Authentication passes
   - WebSocket handshake completes

3. **AI Auditor is running** ✅
   - Making GLM API calls
   - Processing events
   - No errors in logs

---

## ❓ What's Unknown

1. **Do tools actually work?**
   - No tool calls observed in logs yet
   - Need to test actual MCP tool execution
   - Need to verify responses come back

2. **Is cycling normal or problematic?**
   - VSCode MCP may reconnect periodically by design
   - Need to test if tools work despite reconnections
   - Need to check if reconnections cause request failures

---

## 🧪 Testing Needed

### Test 1: Simple Tool Call (System Response)
**From VSCode Instance 1:**
```
Call: listmodels_EXAI-WS-VSCode1
Expected: List of available models (GLM, Kimi)
Success criteria: Response received without errors
```

**From VSCode Instance 2:**
```
Call: listmodels_EXAI-WS-VSCode2
Expected: List of available models (GLM, Kimi)
Success criteria: Response received without errors
```

### Test 2: External AI Call (GLM)
**From VSCode Instance 1:**
```
Call: chat_EXAI-WS-VSCode1
Parameters:
  - message: "What is 2+2?"
  - model: "glm-4.5-flash"
Expected: GLM response "4" or similar
Success criteria: External AI responds correctly
```

### Test 3: External AI Call (Kimi)
**From VSCode Instance 2:**
```
Call: chat_EXAI-WS-VSCode2
Parameters:
  - message: "What is the capital of France?"
  - model: "kimi-k2-turbo-preview"
Expected: Kimi response "Paris"
Success criteria: External AI responds correctly
```

### Test 4: Sequential Execution
**Execute both calls back-to-back:**
1. Call tool from Instance 1
2. Immediately call tool from Instance 2
3. Verify second call waits for first to complete
4. Verify both complete successfully

---

## 📝 Diagnostic Commands

### Check Shim Logs
```bash
# Check if shim is reading correct ping values
Get-Content "logs/ws_shim.log" -Tail 50 | Select-String "PING"
```

### Monitor Connection Stability
```bash
# Watch for connection events in real-time
docker logs exai-mcp-daemon --follow | Select-String "Connection"
```

### Check for Errors
```bash
# Look for any errors in daemon logs
docker logs exai-mcp-daemon --tail 200 | Select-String "error|ERROR|fail|FAIL"
```

---

## 🎯 Next Steps

### Immediate (User Action Required)
1. **Test tool calls** from both VSCode instances
2. **Verify responses** come back correctly
3. **Check if reconnections** cause any request failures
4. **Report results** back to Claude

### If Tools Work Despite Cycling
- ✅ Cycling may be normal VSCode MCP behavior
- ✅ System is functional
- ✅ No further action needed

### If Tools Don't Work
- ❌ Investigate shim logs for ping values
- ❌ Check for .env reading issues
- ❌ Consider WebSocket protocol debugging
- ❌ Consult EXAI for deeper analysis

---

## 💡 Key Insight

**Connection cycling alone doesn't indicate a problem.** What matters is:
1. Can you call tools successfully?
2. Do you get responses back?
3. Are there any errors or timeouts?

If tools work correctly, the cycling is likely **normal VSCode MCP behavior** for health checking and connection management.

---

---

## 🚨 **CRITICAL FINDING (2025-10-26 19:53)**

### Only ONE Instance Connects at a Time!

**Evidence from logs:**
```
19:50:30 - vscode-instance-2 REMOVED
19:50:30 - vscode-instance-1 REMOVED
19:50:42 - vscode-instance-1 CREATED  ← Only instance-1
19:51:36 - vscode-instance-1 REMOVED
19:51:48 - vscode-instance-1 CREATED  ← Only instance-1
19:52:47 - vscode-instance-1 REMOVED
19:52:48 - vscode-instance-2 CREATED  ← Only instance-2 (after instance-1 removed!)
19:53:04 - vscode-instance-2 connects
19:53:20 - vscode-instance-2 connects
19:53:37 - vscode-instance-2 connects
```

**Pattern:** Instances take turns - when one disconnects, the other connects. They NEVER run simultaneously!

### Root Cause Investigation Needed

**Checked:**
- ✅ Session IDs are unique and working correctly
- ✅ No global lock in RequestRouter
- ✅ SESSION_MAX_CONCURRENT=10 (should allow 10 sessions)
- ✅ GLOBAL_MAX_INFLIGHT=5 (should allow 5 concurrent requests)
- ✅ Both VSCode configs are identical except session IDs
- ✅ Both connect to same port (8079) - correct

**Not Checked:**
- ❓ Is there a hidden semaphore blocking concurrent connections?
- ❓ Is VSCode itself preventing multiple MCP servers on same port?
- ❓ Is there a Windows/WSL networking issue?
- ❓ Did the container rebuild introduce a regression?

**User Report:** "Previously this was working fine until the last AI rebuilt the container"

---

**Created:** 2025-10-26
**Status:** 🚨 CRITICAL ISSUE - Only one instance can connect at a time
**Next Action:** EXAI consultation required to identify blocking mechanism
**Success Criteria:** Both instances connect and stay connected simultaneously

