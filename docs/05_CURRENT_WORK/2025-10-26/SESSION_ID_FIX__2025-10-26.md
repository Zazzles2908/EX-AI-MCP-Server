# Multi-Instance Session ID Fix - 2025-10-26

## 🎯 Root Cause Identified

**Problem:** Daemon was ignoring client-provided session IDs and generating random ones instead.

### Evidence

**Client sends unique session IDs:**
```python
# VSCode1: EXAI_SESSION_ID="vscode-instance-1"
# VSCode2: EXAI_SESSION_ID="vscode-instance-2"

await _ws.send(json.dumps({
    "op": "hello",
    "session_id": SESSION_ID,  # Unique per instance
    "token": EXAI_WS_TOKEN,
}))
```

**Daemon IGNORED them:**
```python
# src/daemon/ws/connection_manager.py:289 (BEFORE)
session_id = secrets.token_urlsafe(32)  # Always random!
sess = await session_manager.ensure(session_id)
```

**Result:**
- Both instances got random session IDs
- Session identity was lost
- Caused disconnection issues when second instance connected

---

## ✅ Solution Implemented

### Use Client's Session ID with Validation

**File:** `src/daemon/ws/connection_manager.py` (lines 286-311)

```python
# MULTI-INSTANCE FIX (2025-10-26): Use client's session_id if provided and valid
client_session_id = hello.get("session_id")

def _is_valid_session_id(sid: str) -> bool:
    """Validate client-provided session ID format and length"""
    if not sid or not isinstance(sid, str):
        return False
    # Allow reasonable length (3-64 chars) and safe characters
    return (3 <= len(sid) <= 64 and 
            sid.replace("-", "").replace("_", "").isalnum())

if client_session_id and _is_valid_session_id(client_session_id):
    session_id = client_session_id
    logger.info(f"[SESSION] Using client-provided session ID: {session_id}")
else:
    # Fallback to random if invalid or not provided
    session_id = secrets.token_urlsafe(32)
    if client_session_id:
        logger.warning(f"[SESSION] Client provided invalid session ID, using random")
    else:
        logger.debug(f"[SESSION] No client session ID provided, using random")

sess = await session_manager.ensure(session_id)
```

---

## 🔒 Security Considerations

### Validation Rules
- **Length:** 3-64 characters
- **Characters:** Alphanumeric, dash (-), underscore (_) only
- **Type:** Must be string
- **Fallback:** Random secure token if invalid

### Why This Is Safe
1. **Input validation** prevents injection attacks
2. **Length limits** prevent DoS via huge session IDs
3. **Character whitelist** prevents special character exploits
4. **Fallback to secure random** maintains security when client doesn't provide ID

---

## 📊 Expected Behavior

### Before Fix
```
VSCode1 connects → Daemon assigns random ID: "xK9mP2..."
VSCode2 connects → Daemon assigns random ID: "7nQ4vL..."
Both disconnect due to session conflicts
```

### After Fix
```
VSCode1 connects → Daemon uses: "vscode-instance-1" ✅
VSCode2 connects → Daemon uses: "vscode-instance-2" ✅
Both maintain unique session identities ✅
Sequential execution via existing semaphore system ✅
```

---

## 🧪 Testing Instructions

### Step 1: Restart Both VSCode Instances
1. Close both VSCode windows completely
2. Open VSCode Instance 1 (uses `mcp-config.augmentcode.vscode1.json`)
3. Open VSCode Instance 2 (uses `mcp-config.augmentcode.vscode2.json`)
4. Reload both windows (Developer: Reload Window)

### Step 2: Verify Connections
Check MCP panel in both instances:
- ✅ Both should show green dots
- ✅ Both should show "EXAI-WS-VSCode1" and "EXAI-WS-VSCode2" respectively

### Step 3: Check Daemon Logs
```bash
docker logs exai-mcp-daemon --tail 50 | grep SESSION
```

**Expected output:**
```
INFO [SESSION] Using client-provided session ID: vscode-instance-1
INFO [SESSION] Using client-provided session ID: vscode-instance-2
```

### Step 4: Test Sequential Execution
1. Call a tool from VSCode1 (e.g., `chat_EXAI-WS-VSCode1`)
2. Immediately call a tool from VSCode2 (e.g., `chat_EXAI-WS-VSCode2`)
3. Second call should queue and execute after first completes

---

## 🔍 EXAI Consultation Summary

**Continuation ID:** `2d389cde-ccbb-4363-bd75-22362ee82bc5`

### EXAI's Analysis
1. **Confirmed root cause:** Daemon ignoring client session IDs
2. **Recommended fix:** Use client's session ID with validation
3. **Security guidance:** Validate format, length, and characters
4. **Additional considerations:**
   - Session collision handling (already handled by `session_manager.ensure()`)
   - Session cleanup (already implemented)
   - Backward compatibility (fallback to random maintains compatibility)

### Key Insights
- Session identity loss was causing reconnection issues
- VSCode instances expected to maintain their identities
- Random session IDs defeated the purpose of unique configuration
- Validation ensures security while enabling multi-instance support

---

## 📝 Related Files

### Configuration Files
- `Daemon/mcp-config.augmentcode.vscode1.json` - VSCode1 config (session: vscode-instance-1)
- `Daemon/mcp-config.augmentcode.vscode2.json` - VSCode2 config (session: vscode-instance-2)

### Code Files Modified
- `src/daemon/ws/connection_manager.py` - Session ID handling (lines 286-311)

### Previous Attempts
- `docs/05_CURRENT_WORK/2025-10-26/WINDOWS_CONSOLE_HANDLE_FIX__2025-10-26.md` - Console allocation (failed)
- `docs/05_CURRENT_WORK/2025-10-26/MULTI_INSTANCE_SEQUENTIAL_FIX__2025-10-26.md` - Handle isolation (partial success)

---

## ✅ Status

**Implementation:** COMPLETE  
**Testing:** PENDING USER VERIFICATION  
**Docker Container:** RESTARTED (exai-mcp-daemon)

**Next Steps:**
1. User tests both VSCode instances
2. Verify both connect successfully
3. Verify sequential execution works
4. Monitor logs for session ID usage

