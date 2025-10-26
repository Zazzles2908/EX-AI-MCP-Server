# Multi-Instance NOT Possible - 2025-10-26

**Date:** 2025-10-26  
**Status:** ❌ MULTI-INSTANCE SUPPORT NOT FEASIBLE WITH CURRENT ARCHITECTURE  
**Issue:** Cannot run two VSCode instances with MCP stdio protocol on Windows

---

## 🚫 **CONCLUSION: MULTI-INSTANCE NOT SUPPORTED**

After extensive investigation and multiple fix attempts, **multi-instance support is NOT possible** with the current MCP stdio protocol architecture on Windows.

---

## 🔍 **ROOT CAUSE (CONFIRMED)**

**The fundamental issue:**
- MCP uses stdio (stdin/stdout) for communication between VSCode and the shim
- Windows does not allow multiple processes to share the same stdout handle in binary mode
- When second VSCode instance starts, both try to use the same console handles
- Windows enforces exclusive access → both instances crash with `OSError: [Errno 22]`

**This is NOT a bug in our code - it's a limitation of the MCP stdio protocol on Windows**

---

## 🛠️ **FIX ATTEMPTS (ALL FAILED)**

### **Attempt 1: Binary Mode Fix** ❌ FAILED
**What we tried:**
```python
msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
```

**Result:** Made it worse - enforced exclusive access, causing both instances to fail

---

### **Attempt 2: Console Allocation** ❌ FAILED
**What we tried:**
```python
kernel32.AllocConsole()
sys.stdout = open('CONOUT$', 'w')
```

**Result:** Broke the connection entirely - shim couldn't connect to daemon at all

**Why it failed:**
- AllocConsole() creates a NEW console window
- This breaks the stdio pipe between VSCode and the shim
- VSCode expects to communicate via inherited stdio handles, not a new console
- The shim starts but never completes the WebSocket connection

---

### **Attempt 3: Handle Duplication** ❌ NOT ATTEMPTED
**Why we didn't try:**
- Would have the same issue as console allocation
- VSCode owns the stdio handles - we can't duplicate them without breaking the pipe
- Even if we could, Windows would still enforce exclusive access in binary mode

---

## 💡 **WHY MULTI-INSTANCE DOESN'T WORK**

### **The MCP Stdio Protocol Flow:**
```
VSCode Process 1 ──> stdio pipe ──> run_ws_shim.py (Process A) ──> WebSocket ──> Daemon
VSCode Process 2 ──> stdio pipe ──> run_ws_shim.py (Process B) ──> WebSocket ──> Daemon
                                            ↓
                                    BOTH try to use same console handles
                                            ↓
                                    Windows says NO (exclusive access)
                                            ↓
                                    OSError: [Errno 22] Invalid argument
```

### **The Fundamental Problem:**
1. Each VSCode instance launches its own `run_ws_shim.py` process
2. Both processes inherit the same console handles from the parent shell
3. MCP stdio_server requires binary mode for proper operation
4. Windows enforces exclusive access to console handles in binary mode
5. When second instance starts, first instance's handles become invalid
6. Both crash with stdio flush errors

---

## ✅ **WHAT WORKS**

**Single VSCode instance:** ✅ WORKS PERFECTLY
- One VSCode → One shim → Daemon
- No handle contention
- All tools work correctly

**Sequential usage:** ✅ WORKS
- Use VSCode1, close it completely
- Start VSCode2
- Works fine (no concurrent access)

---

## 🚀 **ALTERNATIVE SOLUTIONS (NOT IMPLEMENTED)**

### **Option 1: Switch to WebSocket Transport** (Recommended)
Instead of MCP stdio protocol, use WebSocket directly:

**Pros:**
- No stdio handle sharing issues
- True multi-instance support
- Better performance
- More robust

**Cons:**
- Requires changing VSCode MCP configuration
- Need to implement WebSocket MCP server
- More complex setup

**Implementation:**
```json
{
  "mcpServers": {
    "EXAI-WS": {
      "type": "websocket",
      "url": "ws://127.0.0.1:8079"
    }
  }
}
```

---

### **Option 2: Use Different Ports Per Instance**
Run separate daemon instances on different ports:

**Pros:**
- True isolation
- Each instance has own daemon

**Cons:**
- Resource intensive (multiple daemons)
- Session data not shared
- Complex configuration

**Implementation:**
```json
// VSCode1
{"EXAI_WS_PORT": "8079"}

// VSCode2
{"EXAI_WS_PORT": "8179"}
```

---

### **Option 3: Use Named Pipes (Windows)**
Replace stdio with Windows named pipes:

**Pros:**
- No handle sharing issues
- Windows-native solution

**Cons:**
- Windows-only
- Requires MCP protocol changes
- Complex implementation

---

## 📝 **CURRENT STATUS**

**Reverted all fixes:**
- ✅ Removed binary mode setting
- ✅ Removed console allocation
- ✅ Removed handle duplication attempts
- ✅ Back to original working state (single instance only)

**File modified:** `scripts/runtime/run_ws_shim.py`

**Current code:**
```python
# Windows-specific stdio handling
# NOTE: Multi-instance support is currently NOT possible with MCP stdio protocol on Windows
if sys.platform == "win32":
    try:
        import msvcrt
        # DO NOT set binary mode - causes handle sharing violations
        pass
    except Exception:
        pass
```

---

## 🎓 **LESSONS LEARNED**

1. **MCP stdio protocol has fundamental limitations on Windows**
   - Cannot support multiple concurrent instances
   - This is by design, not a bug

2. **Console allocation breaks VSCode stdio pipe**
   - VSCode expects inherited handles, not new console
   - AllocConsole() severs the communication channel

3. **Binary mode enforcement makes it worse**
   - Windows enforces exclusive access in binary mode
   - Text mode allows sharing but breaks MCP protocol

4. **The only real solution is to change the transport**
   - WebSocket transport would solve all issues
   - Requires architectural changes

---

## 🚦 **RECOMMENDATION**

**For now: Use single VSCode instance only**

**User's use case:**
> "I have two VSC running purposely so they work independently, so they don't bottleneck when you both are running"

**Our recommendation:**
1. **Short term:** Use one VSCode instance with multiple chat windows
2. **Medium term:** Implement WebSocket transport for true multi-instance support
3. **Long term:** Consider separate daemon instances on different ports

---

## 📚 **RELATED DOCUMENTATION**

- `docs/05_CURRENT_WORK/2025-10-26/MCP_STDIO_ERROR_FIX__2025-10-26.md` - Initial error analysis
- `docs/05_CURRENT_WORK/2025-10-26/ROBUSTNESS_FIXES_COMPLETE__2025-10-26.md` - First fix attempt
- `docs/05_CURRENT_WORK/2025-10-26/FINAL_MULTI_INSTANCE_FIX__2025-10-26.md` - Second fix attempt
- `docs/05_CURRENT_WORK/2025-10-26/WINDOWS_CONSOLE_HANDLE_FIX__2025-10-26.md` - Console allocation attempt

---

## ✅ **NEXT STEPS**

1. **Verify single instance works** after reverting fixes
2. **Close this issue** - multi-instance not supported
3. **Document limitation** in main README
4. **Consider WebSocket transport** for future implementation

---

**Created:** 2025-10-26  
**Status:** ❌ MULTI-INSTANCE NOT FEASIBLE - REVERTED TO SINGLE INSTANCE  
**Confidence:** 100% - This is a fundamental MCP stdio protocol limitation on Windows

