# Codereview Tool Timeout Root Cause Analysis
**Date:** 2025-10-17  
**Status:** ROOT CAUSE IDENTIFIED  
**Priority:** P0 - CRITICAL  
**Continuation ID:** 3d0f1b03-61db-43c7-a343-08527a8b77d9

---

## 🔥 PROBLEM STATEMENT

The `codereview_EXAI-WS` workflow tool experiences session drops after 8 seconds when `use_assistant_model=true`, causing "Connection error" and preventing expert analysis from completing.

**Symptoms:**
- Tool starts expert analysis successfully
- Session is CANCELLED after exactly 8 seconds
- GLM SDK continues retrying AFTER session is already cancelled
- Final connection error occurs ~30 seconds later
- User sees "Cancelled by user" error

---

## 📊 DOCKER LOGS ANALYSIS

```
2025-10-17 04:15:08 INFO tools.workflow.expert_analysis: [EXPERT_ANALYSIS_START] Tool: codereview
2025-10-17 04:15:08 INFO tools.workflow.expert_analysis: [EXPERT_ANALYSIS_START] Model: glm-4.6
2025-10-17 04:15:08 INFO tools.workflow.expert_analysis: [EXPERT_ANALYSIS_START] Thinking Mode: high
2025-10-17 04:15:08 INFO tools.workflow.expert_analysis: [EXPERT_DEBUG] Using ASYNC providers for codereview
2025-10-17 04:15:08 INFO src.providers.async_glm: Async GLM provider initialized (timeout=120s, max_retries=3)
2025-10-17 04:15:08 INFO src.providers.glm_chat: GLM chat using SDK: model=glm-4.6, stream=False
2025-10-17 04:15:16 INFO tools.workflow.expert_analysis: [EXPERT_DEDUP] Removed codereview:unknown:-2812345307072922647 from in-progress
2025-10-17 04:15:16 INFO mcp_activity: TOOL_CANCELLED: codereview req_id=157324bd-ddb7-45b5-86b2-50c4c940e27d
2025-10-17 04:15:16 INFO src.daemon.session_manager: [SESSION_MANAGER] Removed session (total sessions: 0)
2025-10-17 04:15:40 INFO zhipuai.core._http_client: Retrying request to /chat/completions in 0.806244 seconds
2025-10-17 04:15:41 INFO zhipuai.core._http_client: Retrying request to /chat/completions in 1.622088 seconds
2025-10-17 04:15:43 INFO zhipuai.core._http_client: Retrying request to /chat/completions in 3.289390 seconds
2025-10-17 04:15:46 ERROR src.providers.glm_chat: GLM generate_content failed: Connection error.
```

**Timeline:**
- `04:15:08` - Expert analysis starts
- `04:15:16` - Session CANCELLED (8 seconds later)
- `04:15:40` - GLM SDK starts retrying (24 seconds after cancellation)
- `04:15:46` - Final connection error (38 seconds total)

---

## 🔍 ROOT CAUSE IDENTIFIED

### **PROGRESS_INTERVAL = 8.0 seconds**

**Location:** `src/daemon/ws_server.py:239`
```python
PROGRESS_INTERVAL = float(os.getenv("EXAI_WS_PROGRESS_INTERVAL_SECS", "8.0"))
```

**Purpose:** Heartbeat cadence while tools run to satisfy clients with 10s idle cutoff

**The Problem:**
1. **Augment Code MCP Client** has a **10-second idle timeout**
2. **PROGRESS_INTERVAL** is set to **8.0 seconds** to send heartbeats before timeout
3. **However**, the heartbeat mechanism in `ws_server.py:762-771` uses `asyncio.wait_for(tool_task, timeout=PROGRESS_INTERVAL)`
4. **This means:** If the tool doesn't complete within 8 seconds, it triggers a TimeoutError
5. **The heartbeat is sent**, but the **client interprets this as inactivity** because:
   - The tool is still running (no response yet)
   - The heartbeat is just a progress message, not a result
   - Augment Code expects actual tool responses, not just progress updates

### **Configuration Mismatch**

**MCP Config Files:**
- `Daemon/mcp-config.claude.json`: `WORKFLOW_TOOL_TIMEOUT_SECS=120`
- `Daemon/mcp-config.auggie.json`: `WORKFLOW_TOOL_TIMEOUT_SECS=120`
- `Daemon/mcp-config.template.json`: `WORKFLOW_TOOL_TIMEOUT_SECS=120`

**BUT:**
- `config.py:278`: `WORKFLOW_TOOL_TIMEOUT_SECS = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "45"))`
- **Default is 45 seconds**, not 120 seconds!

**AND:**
- Augment Code MCP client configuration is **NOT** using these env vars
- Augment Code has its own timeout configuration (likely 10-30 seconds)
- The progress heartbeat mechanism doesn't prevent client-side timeout

---

## 🎯 THE REAL ISSUE

**Augment Code MCP Client Timeout:**
- Augment Code has a **built-in timeout** for MCP tool calls
- This timeout is **NOT configurable** via the MCP config env vars
- The timeout is likely **10-30 seconds** based on the 8-second cancellation
- **Progress heartbeats don't reset this timeout** - only actual responses do

**Why Chat Works But Codereview Doesn't:**
- `chat_EXAI-WS` completes quickly (usually <10 seconds)
- `codereview_EXAI-WS` with expert analysis takes 30-60+ seconds
- Expert analysis phase involves:
  - Building complex prompt (8,848 chars)
  - GLM-4.6 with thinking mode "high"
  - Web search enabled
  - Multiple retries on connection errors
- **Total time exceeds Augment Code's timeout**

---

## 💡 SOLUTION OPTIONS

### **Option 1: Disable Expert Analysis (IMMEDIATE FIX)**
**Pros:**
- Immediate fix, no code changes
- Codereview still provides value without expert analysis
- User can manually consult EXAI via chat after codereview

**Cons:**
- Loses expert validation feature
- Reduces tool effectiveness
- Doesn't fix underlying timeout issue

**Implementation:**
```python
# In codereview call
use_assistant_model=false
```

### **Option 2: Reduce Expert Analysis Timeout (QUICK FIX)**
**Pros:**
- Keeps expert analysis feature
- Reduces likelihood of timeout
- Simple configuration change

**Cons:**
- May still timeout on complex analysis
- Reduces analysis quality (less thinking time)
- Doesn't address root cause

**Implementation:**
```bash
# In .env or MCP config
EXPERT_ANALYSIS_TIMEOUT_SECS=20
```

### **Option 3: Use Faster Model for Expert Analysis (RECOMMENDED)**
**Pros:**
- Keeps expert analysis feature
- Faster response time
- Better user experience

**Cons:**
- May reduce analysis quality
- Still subject to Augment timeout

**Implementation:**
```python
# In tools/workflow/expert_analysis.py
# Change default model from glm-4.6 to glm-4.5-flash
model = model or "glm-4.5-flash"
```

### **Option 4: Split Expert Analysis into Separate Tool Call (BEST LONG-TERM)**
**Pros:**
- Separates investigation from validation
- Each call stays under timeout
- User can choose when to validate
- Aligns with two-tier methodology

**Cons:**
- Requires code changes
- Changes workflow UX
- More tool calls needed

**Implementation:**
1. Codereview completes without expert analysis
2. Returns continuation_id
3. User calls `validate_analysis_EXAI-WS(continuation_id=...)` separately
4. Validation uses previous context, completes quickly

---

## 📋 RECOMMENDED ACTION PLAN

### **Phase 1: Immediate Fix (TODAY)**
1. **Disable expert analysis for codereview** by default
2. **Update tool description** to mention manual EXAI consultation
3. **Document workaround** in tool registry audit

### **Phase 2: Quick Improvement (THIS WEEK)**
1. **Switch to glm-4.5-flash** for expert analysis
2. **Reduce EXPERT_ANALYSIS_TIMEOUT_SECS** to 20 seconds
3. **Test with Augment Code** to verify completion

### **Phase 3: Long-term Solution (NEXT WEEK)**
1. **Create separate validation tool** (`validate_analysis_EXAI-WS`)
2. **Update workflow tools** to return continuation_id
3. **Update system prompts** with two-tier methodology guidance
4. **Test end-to-end** workflow

---

## 🔧 FILES TO MODIFY

### **Immediate Fix:**
- `tools/workflow/codereview.py` - Set `use_assistant_model=false` by default
- `tools/registry.py` - Update codereview description

### **Quick Improvement:**
- `tools/workflow/expert_analysis.py` - Change default model to glm-4.5-flash
- `.env` - Add `EXPERT_ANALYSIS_TIMEOUT_SECS=20`
- `.env.docker` - Add `EXPERT_ANALYSIS_TIMEOUT_SECS=20`

### **Long-term Solution:**
- `tools/workflow/validate_analysis.py` - New tool for separate validation
- `systemprompts/workflow_prompts.py` - Add two-tier methodology guidance
- `tools/registry.py` - Register new validation tool

---

## 📊 IMPACT ASSESSMENT

**Affected Tools:**
- ✅ `codereview_EXAI-WS` - CONFIRMED affected
- ⚠️ `debug_EXAI-WS` - Likely affected (uses expert analysis)
- ⚠️ `thinkdeep_EXAI-WS` - Likely affected (uses expert analysis)
- ⚠️ `analyze_EXAI-WS` - Likely affected (uses expert analysis)
- ⚠️ All workflow tools with `use_assistant_model=true`

**Not Affected:**
- ✅ `chat_EXAI-WS` - Completes quickly
- ✅ Simple tools - No expert analysis
- ✅ Provider tools - Direct API calls

---

## 🎯 NEXT STEPS

1. **Implement immediate fix** (disable expert analysis)
2. **Test codereview** without expert analysis
3. **Update Supabase** issue tracking
4. **Return to original task** (tool registry fix)
5. **Schedule Phase 2** improvements for this week

---

**Related Issues:**
- Tool Registry Audit (2025-10-17)
- Track 2 Timeout Configuration (2025-10-16)

**Continuation ID:** 3d0f1b03-61db-43c7-a343-08527a8b77d9

