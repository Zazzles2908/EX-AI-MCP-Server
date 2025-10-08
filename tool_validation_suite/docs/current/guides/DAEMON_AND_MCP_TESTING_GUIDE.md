# Daemon Testing Guide

**Last Updated:** 2025-10-05

---

## 🎯 What This Tests

The validation suite tests the **entire EX-AI-MCP-Server** through the WebSocket daemon:

```
Test → mcp_client.py → Daemon → Server → Tools → APIs
```

**Result:** Full stack validation ✅

---

## 🚀 Starting the Daemon

### Method 1: Using Script (Recommended)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

**Expected:** "Starting WS daemon on ws://127.0.0.1:8765"

### Method 2: Manual Start

```powershell
python scripts/run_ws_daemon.py
```

---

## 🧪 Running Tests

### Quick Test (30 seconds)

```powershell
python tool_validation_suite/tests/MCP_TEST_TEMPLATE.py
```

**Expected:** 3/3 tests pass

### Full Test Suite (After Regeneration)

```powershell
python tool_validation_suite/scripts/run_all_tests_simple.py
```

---

## 🔍 Verifying Daemon

### Check Daemon Logs

```powershell
Get-Content logs/ws_daemon.log -Tail 20
```

**Look for:**
- "TOOL CALL RECEIVED"
- "TOOL CALL COMPLETE"
- "Success: True"

### Check Connection

```powershell
python tool_validation_suite/utils/mcp_client.py
```

**Expected:** "✅ MCP tool call successful!"

---

## 📊 What Gets Tested

✅ MCP Protocol (WebSocket handshake)
✅ Daemon (connection, routing)
✅ Server (tool execution)
✅ Tools (actual implementations)
✅ Providers (GLM/Kimi routing)
✅ APIs (external connectivity)

---

## ⚠️ Current Status

**Infrastructure:** ✅ Ready
**Working Template:** ✅ Proven (3/3 tests pass)
**Test Scripts:** ⚠️ Need regeneration (36 files use OLD approach)

**Next:** Regenerate test scripts using `MCP_TEST_TEMPLATE.py`

---

## 🆘 Troubleshooting

**Daemon won't start:** Check port 8765 not in use
**Connection refused:** Daemon not running - start it first
**Tests timeout:** Check `logs/ws_daemon.log` for errors
**Tests fail:** Verify API keys in `.env.testing`

---

## ✅ Summary

**Purpose:** Test full EX-AI-MCP-Server stack through daemon
**Method:** WebSocket client → daemon → server → tools → APIs
**Status:** Infrastructure ready, test scripts need regeneration
