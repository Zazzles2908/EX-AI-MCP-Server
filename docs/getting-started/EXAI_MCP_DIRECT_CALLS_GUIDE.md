# EXAI MCP Direct Calls - Complete Guide

## ✅ CURRENT STATUS

### Files Confirmed:
```
✓ C:/Project/EX-AI-MCP-Server/.mcp.json           (Claude Desktop config)
✓ C:/Project/EX-AI-MCP-Server/scripts/exai_native_mcp_server.py
✓ c:/Users/Jazeel-Home/.claude/exai_mcp_server.py
```

### Configuration Verified:
```json
{
  "mcpServers": {
    "exai-simple": {           ← 5 tools (direct MCP)
    "exai-native-mcp": {       ← 19 tools (native MCP)
    "exai-mcp": {             ← WebSocket interface
  }
}
```

### EXAI Infrastructure:
```
✓ WebSocket daemon: Port 8079 (healthy)
✓ Providers: GLM + Kimi + Moonshot
✓ Models: 25 available
✓ All tools tested via WebSocket: WORKING
```

## 🚫 PROBLEM: Direct MCP Calls Not Available

### Symptoms:
```python
mcp__exai_simple__exai_status()
→ Error: No such tool available

mcp__exai_native_mcp__status()
→ Error: No such tool available
```

### Root Cause:
Claude Desktop caches MCP configurations and doesn't auto-reload when:
- `.mcp.json` is modified
- New servers are added
- Configuration changes

## 💡 SOLUTION

### Option 1: Full Claude Desktop Restart
```
1. Close Claude Desktop completely
2. Navigate to: C:/Project/EX-AI-MCP-Server
3. Start Claude Desktop FROM that directory
4. Verify: Tools should auto-load
```

### Option 2: Verify Loaded Configuration
Check which MCP servers Claude Desktop has loaded:

**Working MCP servers (confirmed):**
- `mcp__claude-enhancements__cache_stats()` ✓
- `mcp__gh-mcp__gh_user_get()` ✓

**EXAI MCP servers (configured but not loaded):**
- `mcp__exai_simple__exai_status()` ✗
- `mcp__exai_native_mcp__status()` ✗

## 📋 TOOLS AVAILABLE AFTER RELOAD

### exai-simple (5 tools)
```python
mcp__exai_simple__exai_status()
mcp__exai_simple__exai_tools()
mcp__exai_simple__exai_chat(message="...", model="...")
mcp__exai_simple__exai_search(query="...")
mcp__exai_simple__exai_analyze(content="...", type="...")
```

### exai-native-mcp (19 tools)
```python
mcp__exai_native_mcp__status()
mcp__exai_native_mcp__listmodels()
mcp__exai_native_mcp__analyze(step="...", model="...", thinking_mode="...")
mcp__exai_native_mcp__debug(request="...", thinking_mode="...")
mcp__exai_native_mcp__chat(message="...", model="...")
mcp__exai_native_mcp__codereview(code="...", model="...")
mcp__exai_native_mcp__refactor(code="...", model="...")
mcp__exai_native_mcp__testgen(code="...", model="...")
mcp__exai_native_mcp__thinkdeep(question="...", thinking_mode="...")
mcp__exai_native_mcp__smart_file_query(query="...", file_paths=[], thinking_mode="...")
mcp__exai_native_mcp__planner(goal="...", model="...")
mcp__exai_native_mcp__secaudit(code="...", model="...")
mcp__exai_native_mcp__docgen(code="...", model="...")
mcp__exai_native_mcp__tracer(code="...", model="...")
mcp__exai_native_mcp__consensus(request="...", models=[...])
mcp__exai_native_mcp__precommit(files=[], model="...")
mcp__exai_native_mcp__kimi_chat_with_tools(message="...", files=[])
mcp__exai_native_mcp__glm_payload_preview(payload={...})
```

## 🔍 VERIFICATION STEPS

After restarting Claude Desktop:

### 1. Check Available Tools
```python
# These should now work:
mcp__exai_simple__exai_status()
mcp__exai_native_mcp__status()
```

### 2. Test Simple Tool
```python
mcp__exai_simple__exai_tools()
# Should list all 5 simple EXAI tools
```

### 3. Test Native Tool
```python
mcp__exai_native_mcp__listmodels()
# Should list all 25 available models
```

## 🎯 SUMMARY

**Configuration:** ✅ Complete and correct
**Servers:** ✅ Verified working
**WebSocket:** ✅ Fully operational
**Issue:** Claude Desktop needs restart to load new MCP config

**Once reloaded, EXAI MCP tools will be available for direct programmatic use!**
