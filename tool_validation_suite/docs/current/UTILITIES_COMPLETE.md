# Utilities Reference

**Last Updated:** 2025-10-05
**Status:** 11 utilities available

---

## 🚀 Primary Utilities (Use These)

### 1. MCP Client (`utils/mcp_client.py`) ⭐ **NEW**

**Purpose:** Call MCP tools through WebSocket daemon (tests full stack)

**Features:**
- ✅ WebSocket connection to daemon (ws://127.0.0.1:8765)
- ✅ MCP protocol implementation (hello handshake, tool calls)
- ✅ Progress message handling
- ✅ Full stack testing (MCP → daemon → server → tools → APIs)

**Key Methods:**
- `call_tool(tool_name, arguments)` - Call any MCP tool
- `connect()` - Connect to daemon
- `disconnect()` - Close connection

**Example:**
```python
from utils.mcp_client import MCPClient

mcp_client = MCPClient()
result = mcp_client.call_tool(
    tool_name="chat",
    arguments={"prompt": "Hello", "model": "glm-4.5-flash"}
)
```

---

### 2. Prompt Counter (`utils/prompt_counter.py`)

**Purpose:** Track API calls, tokens, and costs

**Key Methods:**
- `record_prompt()` - Record API call
- `get_summary()` - Get statistics
- `save()` / `load()` - Persist data

---

### 3. Test Runner (`utils/test_runner.py`)
**Purpose:** Orchestrate test execution

**Key Methods:**
- `run_test()` - Run single test
- `run_batch()` - Run multiple tests

---

### 4. Response Validator (`utils/response_validator.py`)

**Purpose:** Validate tool responses

**Key Methods:**
- `validate_response()` - Validate response
- `validate_batch()` - Validate multiple

---

### 5. Result Collector (`utils/result_collector.py`)

**Purpose:** Collect test results

**Key Methods:**
- `add_result()` - Add result
- `get_summary()` - Get summary
- `print_summary()` - Print report

---

## 📦 Supporting Utilities

### 6. Conversation Tracker (`utils/conversation_tracker.py`)
- Manage conversation IDs with platform isolation

### 7. File Uploader (`utils/file_uploader.py`)
- Upload files to Kimi/GLM APIs

### 8. Performance Monitor (`utils/performance_monitor.py`)
- Monitor CPU, memory, response times

### 9. Report Generator (`utils/report_generator.py`)
- Generate test reports

### 10. GLM Watcher (`utils/glm_watcher.py`)
- Independent test observation

---

## ⚠️ Legacy Utilities (Deprecated)

### API Client (`utils/api_client.py`) ❌ **DEPRECATED**

**Purpose:** Direct API calls (bypasses MCP server)

**Status:** Legacy - use `mcp_client.py` instead

**Why Deprecated:**
- Bypasses MCP server, daemon, and tools
- Only tests external APIs
- Doesn't validate full stack

**Migration:**
```python
# OLD (deprecated):
from utils.api_client import APIClient
response = api_client.call_kimi(...)

# NEW (correct):
from utils.mcp_client import MCPClient
result = mcp_client.call_tool(tool_name="chat", arguments={...})
```

---

## 📊 Summary

**Total Utilities:** 11
**Primary (Use These):** 5 (mcp_client, prompt_counter, test_runner, response_validator, result_collector)
**Supporting:** 5 (conversation_tracker, file_uploader, performance_monitor, report_generator, glm_watcher)
**Deprecated:** 1 (api_client)

**Recommendation:** Use `mcp_client.py` for all new tests


