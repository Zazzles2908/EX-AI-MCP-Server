# Python Script Issues - Identified & Fixed

## 📋 Session Summary

This document tracks all issues found in Python scripts in the `scripts/` directory during this session, analyzed using EXAI MCP tools.

**Total Issues Found:** 15+
**Critical Security Issues:** 2
**Configuration Issues:** 8
**Code Quality Issues:** 5

---

## 🔴 CRITICAL SECURITY ISSUES

### Issue 1: Hardcoded JWT Token in Plain Text

**File:** `scripts/setup_claude_connection.py`
**Line:** 27
**Severity:** CRITICAL

```python
EXAI_JWT_TOKEN_CLAUDE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjUwNzMsImV4cCI6MTc5MzY2MTA3M30.hVzyioI0JRDgGnbVIq7NYZOsPiiOYjjuRXwAPBVtFn0"
```

**Problem:** JWT token is hardcoded in plain text directly in the source code.

**Risk:**
- Credentials exposed to anyone with code access
- Unauthorized API access
- Security breach potential

**Fix:**
```python
EXAI_JWT_TOKEN_CLAUDE = os.getenv("EXAI_JWT_TOKEN_CLAUDE")
if not EXAI_JWT_TOKEN_CLAUDE:
    raise ValueError("EXAI_JWT_TOKEN_CLAUDE environment variable is required")
```

---

### Issue 2: JWT Tokens Printed to Console

**File:** `scripts/generate_all_jwt_tokens.py`
**Lines:** 121-127
**Severity:** HIGH

```python
# Display tokens
for name, info in tokens.items():
    print(f"## {name}")
    print(f"User ID: {info['user_id']}")
    print(f"Config: {info['config_file']}")
    print(f"Token:")  # ⚠️ DANGEROUS
    print(info['token'])  # ⚠️ TOKEN EXPOSED
    print()
```

**Problem:** JWT tokens are printed to console without redaction.

**Risk:**
- Token exposure in logs
- Token exposure in screenshots
- Unauthorized access

**Fix:**
```python
# Display tokens
for name, info in tokens.items():
    print(f"## {name}")
    print(f"User ID: {info['user_id']}")
    print(f"Config: {info['config_file']}")
    print("Token: [REDACTED - stored in configuration files]")
    # Or write to secure file instead:
    # write_token_to_file(name, info['token'])
    print()
```

---

## 🟡 CONFIGURATION ISSUES

### Issue 3: Inconsistent Default Ports

**Problem:** Multiple scripts use different hardcoded default ports:
- `8079` (Docker internal port)
- `8765` (legacy/default)
- `8710` (incorrect)
- `3000` (correct host port)

**All should use:** `3000` (the corrected configuration)

### Issue 3a: Port 8079 in validate_environment.py

**File:** `scripts/validate_environment.py`
**Line:** 104
**Current:**
```python
ws_port = os.getenv("EXAI_WS_PORT", "8079")
```
**Should be:**
```python
ws_port = os.getenv("EXAI_WS_PORT", "3000")
```

### Issue 3b: Port 8079 in exai_native_mcp_server.py

**File:** `scripts/exai_native_mcp_server.py`
**Line:** 38
**Current:**
```python
EXAI_WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
```
**Should be:**
```python
EXAI_WS_PORT = int(os.getenv("EXAI_WS_PORT", "3000"))
```

### Issue 3c: Port 8079 in setup_claude_connection.py

**File:** `scripts/setup_claude_connection.py`
**Lines:** 53, 102
**Current:**
```python
"EXAI_WS_PORT": "8079",
```
**Should be:**
```python
"EXAI_WS_PORT": "3000",
```

### Issue 3d: Port 8765 in ws_chat_once.py

**File:** `scripts/ws/ws_chat_once.py`
**Line:** 9
**Current:**
```python
HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1"); PORT = int(os.getenv("EXAI_WS_PORT", "8765"));
```
**Should be:**
```python
HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1"); PORT = int(os.getenv("EXAI_WS_PORT", "3000"));
```

### Issue 3e: Port 8710 in ws_chat_review_once.py

**File:** `scripts/ws/ws_chat_review_once.py`
**Line:** 7
**Current:**
```python
PORT = int(os.getenv("EXAI_WS_PORT", "8710"))
```
**Should be:**
```python
PORT = int(os.getenv("EXAI_WS_PORT", "3000"))
```

### Issue 3f: Port 8765 in ws_chat_analyze_files.py

**File:** `scripts/ws/ws_chat_analyze_files.py`
**Line:** 29
**Current:**
```python
PORT = int(os.getenv("EXAI_WS_PORT", "8765"))
```
**Should be:**
```python
PORT = int(os.getenv("EXAI_WS_PORT", "3000"))
```

### Issue 3g: Port 8765 in ws_chat_roundtrip.py

**File:** `scripts/ws/ws_chat_roundtrip.py`
**Line:** 22
**Current:**
```python
PORT = int(os.getenv("EXAI_WS_PORT", "8765"))
```
**Should be:**
```python
PORT = int(os.getenv("EXAI_WS_PORT", "3000"))
```

### Issue 3h: Port Validation in setup_claude_connection.py

**File:** `scripts/setup_claude_connection.py`
**Line:** 122
**Current:**
```python
result = sock.connect_ex(('127.0.0.1', 8079))
```
**Should be:**
```python
result = sock.connect_ex(('127.0.0.1', 3000))
```

---

## 🟢 CODE QUALITY ISSUES

### Issue 4: Unused Imports

**Files:**
- `scripts/ws/ws_chat_once.py` line 6: `from pathlib import Path`
- `scripts/ws/ws_chat_review_once.py` line 6: `from pathlib import Path`
- `scripts/validate_environment.py` line 6: `from pathlib import Path` (not used)

**Fix:** Remove unused imports

### Issue 5: Missing Environment Variable Validation

**Multiple scripts lack validation for required environment variables:**

**Scripts Affected:**
- `scripts/ws/ws_chat_once.py`
- `scripts/ws/ws_chat_review_once.py`
- `scripts/ws/ws_chat_analyze_files.py`
- `scripts/ws/ws_chat_roundtrip.py`
- `scripts/validate_environment.py`
- `scripts/exai_native_mcp_server.py`

**Fix:** Add validation at startup
```python
required_vars = ["EXAI_WS_HOST", "EXAI_WS_PORT", "EXAI_WS_TOKEN"]
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)
```

### Issue 6: Hardcoded WebSocket Timeouts

**File:** Multiple scripts
**Problem:** Timeouts hardcoded without config option

**Examples:**
- `scripts/ws/ws_chat_once.py` line 32: `timeout: float = 180.0`
- `scripts/ws/ws_chat_review_once.py` line 69: `timeout: float = 120.0`
- `scripts/ws/ws_chat_analyze_files.py` line 110: `timeout: float = 180.0`

**Fix:** Make configurable
```python
WS_TIMEOUT = float(os.getenv("WS_TIMEOUT", "180.0"))
```

### Issue 7: Poor Error Handling for JSON Parsing ✅ FIXED

**Files:**
- `scripts/ws/ws_chat_once.py` (lines 59, 74)
- `scripts/ws/ws_chat_analyze_files.py` (lines 129, 162)
- `scripts/ws/ws_chat_roundtrip.py` (lines 89, 108)

**Problem:** JSON parsing without try-except blocks - potential crash points if malformed WebSocket messages received.

**Fix Applied:**
```python
try:
    msg = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"[ERROR] Failed to parse server response: {e}")
    print(f"[DEBUG] Raw response: {raw[:200]}...")
    return False, f"JSON parse error: {e}", None, None
```

**Status:** ✅ FIXED - All json.loads() calls now have proper error handling with JSONDecodeError捕获, logging, and graceful error reporting.

### Issue 8: Inconsistent Exit Patterns

**Files:**
- `scripts/ws/ws_chat_once.py` line 66: `raise SystemExit(asyncio.run(main()))`
- `scripts/ws/ws_chat_review_once.py` line 69: `asyncio.run(main())`
- `scripts/ws/ws_chat_roundtrip.py` line 124: `raise SystemExit(asyncio.run(main()))`

**Problem:** Mix of `raise SystemExit` and `asyncio.run(main())`

**Fix:** Use consistent pattern
```python
if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

---

## 📊 Summary by File

| File | Issues Found | Critical | Config | Quality |
|------|-------------|----------|--------|---------|
| `setup_claude_connection.py` | 4 | 1 (JWT token) | 3 (ports) | 0 |
| `generate_all_jwt_tokens.py` | 1 | 1 (token exposure) | 0 | 0 |
| `validate_environment.py` | 3 | 0 | 1 (port) | 2 (imports, exit) |
| `exai_native_mcp_server.py` | 1 | 0 | 1 (port) | 0 |
| `ws/ws_chat_once.py` | 4 | 0 | 1 (port) | 3 (imports, timeout, exit) |
| `ws/ws_chat_review_once.py` | 3 | 0 | 1 (port) | 2 (imports, timeout) |
| `ws/ws_chat_analyze_files.py` | 2 | 0 | 1 (port) | 1 (timeout) |
| `ws/ws_chat_roundtrip.py` | 2 | 0 | 1 (port) | 1 (exit) |

---

## 🛠️ Fix Priority

### Priority 1 (Immediate - Security)
1. Remove hardcoded JWT token from `setup_claude_connection.py`
2. Fix JWT token printing in `generate_all_jwt_tokens.py`

### Priority 2 (High - Configuration)
3. Update all port references from 8079/8765/8710 to 3000
4. Update port validation in `setup_claude_connection.py`

### Priority 3 (Medium - Quality)
5. Remove unused imports across all scripts
6. Add environment variable validation
7. Make timeouts configurable
8. Standardize exit patterns

---

## ✅ Verification

All issues were identified using EXAI MCP tools:
- ✅ Analyzed 8+ Python scripts
- ✅ Found 15+ issues
- ✅ Categorized by severity
- ✅ Provided specific fix recommendations
- ✅ Documented with line numbers

**Tools Used:**
- `mcp__exai-mcp__codereview` - Code quality analysis
- Focused on security, configuration, and error handling

---

## 🎯 Next Steps

1. **Fix critical security issues** (JWT token exposure)
2. **Standardize port configuration** (all to 3000)
3. **Add environment variable validation** to all scripts
4. **Create a script validation test** to prevent future issues
5. **Update documentation** with correct configuration values

---

**Documentation Created:** 2025-11-08
**Analysis Method:** EXAI MCP Code Review Tools
**Files Analyzed:** 8 Python scripts in `scripts/` directory
**Status:** All issues identified and documented
