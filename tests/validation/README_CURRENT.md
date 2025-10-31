# 🧪 Tool Validation Suite - README

**Purpose:** Test the entire EX-AI-MCP-Server stack end-to-end
**Status:** ⚠️ Infrastructure Ready - Test Scripts Need Regeneration
**Last Updated:** 2025-10-05

---

## 🎯 What This Suite Does

Tests the **complete EX-AI-MCP-Server stack** through the WebSocket daemon:

```
Test Script
    ↓
utils/mcp_client.py (WebSocket client)
    ↓
WebSocket Daemon (ws://127.0.0.1:8765)
    ↓
src/daemon/ws_server.py
    ↓
server.py (MCP server)
    ↓
tools/workflows/*.py (30 tools)
    ↓
src/providers/ (GLM/Kimi routing)
    ↓
External APIs
```

**Result:** Full stack validation - tests ALL 7 layers ✅

---

## ✅ What's Working

**Infrastructure (100%):**
- ✅ `utils/mcp_client.py` - WebSocket client
- ✅ `utils/test_runner.py` - Test orchestration
- ✅ All 11 utilities functional

**Working Template:**
- ✅ `tests/MCP_TEST_TEMPLATE.py` - Proven working (3/3 tests pass)

**Daemon:**
- ✅ Running on ws://127.0.0.1:8765
- ✅ Tool calls executing successfully

---

## ⚠️ What Needs Fixing

**Test Scripts (36 files):**
- ❌ All use OLD approach (`api_client.py` - direct API calls)
- ❌ Bypass MCP server entirely
- ✅ Need regeneration using `MCP_TEST_TEMPLATE.py`

**Impact:** Suite doesn't test full stack currently

---

## 🚀 Quick Start

### 1. Start Daemon
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### 2. Run Working Template
```powershell
python tool_validation_suite/tests/MCP_TEST_TEMPLATE.py
```

**Expected:** 3/3 tests pass ✅

### 3. Verify Daemon
```powershell
Get-Content logs/ws_daemon.log -Tail 20
```

**Look for:** "TOOL CALL COMPLETE" with "Success: True"

---

## 📚 Documentation

**Root Files (Read These):**
1. `README_CURRENT.md` ← You are here
2. `START_HERE.md` - Quick start guide
3. `tests/MCP_TEST_TEMPLATE.py` - Working code example

**Technical Docs:**
- `docs/current/` - Essential technical documentation
- `docs/archive/` - Historical/outdated files

---

## 🔧 Next Steps (Critical)

### 1. Regenerate Test Scripts (2-4 hours)

**Why:** Current 36 test scripts bypass MCP server

**How:**
- Use `tests/MCP_TEST_TEMPLATE.py` as reference
- Replace `api_client.call_kimi/call_glm` with `mcp_client.call_tool`
- Update all 36 test files

### 2. Run Full Test Suite (1-2 hours)

**Command:**
```powershell
python tool_validation_suite/scripts/run_all_tests_simple.py
```

**Expected:** 90%+ pass rate

---

## 💡 OLD vs NEW Approach

**OLD (Wrong):**
```python
from utils.api_client import APIClient
response = api_client.call_kimi(...)  # Bypasses MCP server
```

**NEW (Correct):**
```python
from utils.mcp_client import MCPClient
result = mcp_client.call_tool(tool_name="chat", arguments={...})  # Tests full stack
```

---

## 🆘 Troubleshooting

**Connection refused:** Start daemon first
**Tests timeout:** Check `logs/ws_daemon.log`
**Need help:** See `docs/current/` for technical docs

---

**Status:** Infrastructure ready, test scripts need regeneration
**Next:** Regenerate 36 test scripts using MCP template

