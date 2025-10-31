# Tool Registration Architecture - Complete Guide

**Date:** 2025-10-29  
**Purpose:** Document how tool visibility works for ALL agents (VSCode, Docker, future clients)  
**Audience:** Future developers, system administrators, AI agents

---

## 🎯 **OVERVIEW**

The EXAI-WS MCP Server uses a **4-tier tool visibility system** to prevent overwhelming agents while maintaining full functionality.

**Key Principle:** Agents see 10 tools by default (Essential + Core), not all 33 tools.

---

## 📊 **4-TIER SYSTEM**

### **ESSENTIAL (3 tools)**
Always visible - basic operations every agent needs:
- `status` - System status checking
- `chat` - Basic communication interface
- `planner` - Task planning and coordination

### **CORE (7 tools)**
Default workflow tools (80% of use cases):
- `analyze` - Strategic architectural assessment
- `codereview` - Systematic code review
- `debug` - Root cause investigation
- `refactor` - Code improvement and modernization
- `testgen` - Test case generation
- `thinkdeep` - Extended hypothesis-driven reasoning
- `smart_file_query` - ⭐ UNIFIED file operations (replaces 6+ tools)

### **ADVANCED (7 tools)**
Specialized tools for complex scenarios:
- `consensus` - Multi-agent coordination
- `docgen` - Documentation generation
- `secaudit` - Security auditing
- `tracer` - Code execution tracing
- `precommit` - Pre-commit hook management
- `kimi_chat_with_tools` - Advanced Kimi capabilities
- `glm_payload_preview` - GLM payload inspection

### **HIDDEN (16 tools)**
System/diagnostic/deprecated tools (invisible to agents):
- Diagnostic: `provider_capabilities`, `listmodels`, `activity`, `version`, `health`, `toolcall_log_tail`, `test_echo`, `kimi_capture_headers`, `kimi_intent_analysis`
- Deprecated: `kimi_upload_files`, `kimi_chat_with_files`, `kimi_manage_files`, `glm_upload_file`, `glm_multi_file_chat`
- Internal: `glm_web_search`, `kimi_web_search`

---

## 🔧 **CONFIGURATION**

### **Environment Variable: LEAN_MODE**

**Location:**
- `.env` - For VSCode MCP clients (Windows host)
- `.env.docker` - For Docker container

**Syntax:**
```bash
LEAN_MODE=true   # Enable 4-tier system (10 tools visible)
LEAN_MODE=false  # Disable 4-tier system (33 tools visible)
```

**Default:** `false` (all 33 tools visible)

**Recommendation:** Always set `LEAN_MODE=true` for optimal agent experience

---

## 🏗️ **ARCHITECTURE FLOW**

### **VSCode MCP Client → Docker Daemon**

```
VSCode Extension
    ↓
run_ws_shim.py (Windows host, reads .env)
    ↓
WebSocket Connection (localhost:8079)
    ↓
WebSocket Daemon (Docker container, reads .env.docker)
    ↓
tools/registry.py (reads LEAN_MODE env var)
    ↓
Tool List (10 or 33 tools depending on LEAN_MODE)
```

### **Critical Points:**

1. **VSCode reads .env** (Windows host environment)
2. **Docker reads .env.docker** (container environment)
3. **Both must have LEAN_MODE=true** for consistency
4. **VSCode restart required** after changing .env

---

## 📝 **IMPLEMENTATION DETAILS**

### **tools/registry.py Logic:**

```python
def build_tools(self) -> None:
    disabled = {t.strip().lower() for t in os.getenv("DISABLED_TOOLS", "").split(",") if t.strip()}
    lean_mode = os.getenv("LEAN_MODE", "false").strip().lower() == "true"
    
    if lean_mode:
        lean_overrides = {t.strip().lower() for t in os.getenv("LEAN_TOOLS", "").split(",") if t.strip()}
        active = lean_overrides or set(DEFAULT_LEAN_TOOLS)  # 10 tools
    else:
        active = set(TOOL_MAP.keys())  # ALL 33 tools
    
    # Ensure utilities are always on unless STRICT_LEAN is enabled
    if os.getenv("STRICT_LEAN", "false").strip().lower() != "true":
        active.update({"version", "listmodels"})
    
    # Remove disabled
    active = {t for t in active if t not in disabled}
    
    for name in sorted(active):
        self._load_tool(name)
```

### **DEFAULT_LEAN_TOOLS Definition:**

```python
# Derive DEFAULT_LEAN_TOOLS dynamically from TOOL_VISIBILITY
# Includes ESSENTIAL + CORE tools (10 total) for optimal agent experience
DEFAULT_LEAN_TOOLS = {
    name for name, vis in TOOL_VISIBILITY.items() 
    if vis in ("essential", "core")
}
```

---

## 🔄 **RESTART REQUIREMENTS**

### **When LEAN_MODE Changes:**

**VSCode MCP Clients:**
1. Update `.env` file
2. **Restart VSCode completely** (or toggle MCP extension)
3. Verify tool count in VSCode MCP panel

**Docker Container:**
1. Update `.env.docker` file
2. Rebuild Docker container: `docker-compose down && docker-compose up -d --build`
3. Verify tool count via WebSocket connection

**Why Restart?**
- Environment variables are read at startup
- Existing connections maintain original configuration
- No hot-reload mechanism for LEAN_MODE

---

## 🧪 **TESTING & VALIDATION**

### **Verify Tool Count:**

**VSCode:**
1. Open VSCode MCP panel
2. Count visible tools
3. Expected: 10 tools (Essential + Core) when LEAN_MODE=true

**Docker:**
1. Check container logs: `docker logs exai-mcp-daemon`
2. Look for tool registration messages
3. Expected: "Loaded 10 tools" when LEAN_MODE=true

**Direct API:**
```bash
# Connect to WebSocket daemon
wscat -c ws://localhost:8079

# Send list_tools request
{"op": "list_tools"}

# Count tools in response
# Expected: 10 tools when LEAN_MODE=true
```

### **Test Scenarios:**

1. **LEAN_MODE=true** → Verify 10 tools visible
2. **LEAN_MODE=false** → Verify 33 tools visible
3. **LEAN_MODE missing** → Verify 33 tools visible (default)
4. **LEAN_TOOLS override** → Verify custom tool set

---

## 🚨 **TROUBLESHOOTING**

### **Problem: VSCode still shows 33 tools**

**Cause:** VSCode not restarted after .env change

**Solution:**
1. Close VSCode completely
2. Reopen VSCode
3. Verify tool count

### **Problem: Docker shows 33 tools**

**Cause:** .env.docker not updated or container not rebuilt

**Solution:**
1. Verify `LEAN_MODE=true` in .env.docker
2. Rebuild container: `docker-compose down && docker-compose up -d --build`
3. Check container logs

### **Problem: Inconsistent tool counts**

**Cause:** .env and .env.docker have different LEAN_MODE values

**Solution:**
1. Ensure both files have `LEAN_MODE=true`
2. Restart VSCode
3. Rebuild Docker container

---

## 📚 **RELATED DOCUMENTATION**

- `docs/00_Quick_Start_Guide.md` - 5-minute getting started guide
- `docs/01_Tool_Decision_Tree.md` - Comprehensive tool selection guide
- `docs/01_Core_Architecture/02_SDK_Integration.md` - Complete tool reference
- `docs/05_CURRENT_WORK/2025-10-29/PHASE_4_COMPLETE_REPORT.md` - Implementation details

---

## 🔮 **FUTURE ENHANCEMENTS**

### **Potential Improvements:**

1. **Hot-Reload:** Allow LEAN_MODE changes without restart
2. **Per-Client Configuration:** Different tool sets for different clients
3. **Dynamic Tool Loading:** Load tools on-demand based on usage
4. **Tool Usage Analytics:** Track which tools are actually used
5. **Configuration Validation:** Startup warnings for conflicting settings

### **Backward Compatibility:**

- LEAN_MODE defaults to `false` (all tools visible)
- Existing deployments continue working without changes
- Gradual migration path to 4-tier system

---

## ✅ **SUMMARY**

**For Future Agents:**
1. Read `docs/00_Quick_Start_Guide.md` first
2. Use 10 default tools (Essential + Core)
3. Refer to `docs/01_Tool_Decision_Tree.md` for tool selection
4. No need to understand LEAN_MODE internals

**For System Administrators:**
1. Set `LEAN_MODE=true` in both `.env` and `.env.docker`
2. Restart VSCode and rebuild Docker container
3. Verify 10 tools visible in all clients
4. Monitor tool usage and adjust as needed

**For Developers:**
1. Understand 4-tier system (Essential/Core/Advanced/Hidden)
2. Add new tools to appropriate tier in `tools/registry.py`
3. Update `DEFAULT_LEAN_TOOLS` if adding Essential/Core tools
4. Test with both `LEAN_MODE=true` and `LEAN_MODE=false`

---

**The 4-tier tool visibility system is now fully operational and documented.** ✅

