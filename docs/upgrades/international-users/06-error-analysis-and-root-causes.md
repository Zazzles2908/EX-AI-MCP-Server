# Error Analysis: EXAI Tool Call Failures & Root Causes

**Date:** 2025-10-01  
**Purpose:** Systematic analysis of all errors encountered during EXAI tool usage  
**Goal:** Identify root causes and add fixes to implementation plan  
**Target:** Turnkey system for any GitHub user

---

## 🎯 Objective

Analyze every error encountered during EXAI tool calls to:
1. Understand WHY each error occurred
2. Identify root causes in our implementation
3. Document fixes needed for turnkey operation
4. Ensure seamless experience for future users

---

## 📋 Error Log & Analysis

### Error #1: analyze_EXAI-WS - Invalid Path Error

**Error Message:**
```
Daemon error: {'code': 'ERROR', 'message': "All file paths must be FULL absolute paths. Invalid path: '.'", 'metadata': {}}
```

**What I Did:**
```python
analyze_EXAI-WS(
    step="Conduct comprehensive research...",
    step_number=1,
    total_steps=5,
    next_step_required=true,
    findings="Starting systematic investigation...",
    model="glm-4.5",
    use_websearch=true
)
```

**Root Cause Analysis:**

1. **Missing required parameter:** I didn't provide `relevant_files` parameter
2. **Tool validation:** The analyze tool requires file paths for code analysis
3. **Default behavior:** When no files provided, tool may default to "." (current directory)
4. **Path validation:** WS daemon validates that all paths are absolute

**Why This Happened:**
- I was trying to use `analyze` for WEB RESEARCH, not CODE ANALYSIS
- The `analyze` tool is designed for analyzing CODE FILES
- I should have used `chat` tool for research instead
- Tool purpose mismatch

**Fix Required:**
1. **Documentation:** Clearly document that `analyze` is for CODE, not research
2. **Tool selection guide:** Help users choose the right tool
3. **Better error message:** "analyze requires code files. For research, use chat tool."
4. **Validation improvement:** Detect when tool is misused and suggest alternatives

**Impact:** MEDIUM - Confusing for users who don't understand tool purposes

---

### Error #2: thinkdeep_EXAI-WS - Missing 'step' Parameter

**Error Message:**
```
Input validation error: 'step' is a required property
```

**What I Did:**
```python
thinkdeep_EXAI-WS(
    prompt="**SCOPE GAP #1 IDENTIFIED:** ...",  # Used 'prompt' instead of 'step'
    model="glm-4.5",
    step_number=1,
    total_steps=4,
    next_step_required=true,
    findings="...",
    use_websearch=true
)
```

**Root Cause Analysis:**

1. **Parameter name confusion:** Used `prompt` (from chat tool) instead of `step`
2. **Inconsistent naming:** Different tools use different parameter names
3. **Schema validation:** Tool correctly rejected invalid parameter
4. **No helpful suggestion:** Error didn't suggest using `step` instead

**Why This Happened:**
- `chat` tool uses `prompt` parameter
- `thinkdeep` tool uses `step` parameter
- I mixed up the parameter names
- Inconsistent API design across tools

**Fix Required:**
1. **Standardize parameters:** Consider using `prompt` OR `step` consistently
2. **Better error messages:** "Did you mean 'step'? (thinkdeep uses 'step', not 'prompt')"
3. **Documentation:** Clear parameter reference for each tool
4. **Type hints:** Better IDE support for parameter names

**Impact:** LOW - Easy to fix once you know, but confusing initially

---

### Error #3: chat_EXAI-WS - Native Web Search Not Working

**Error Message:**
```
(No error, but unexpected behavior)
```

**What I Did:**
```python
chat_EXAI-WS(
    prompt="I need you to conduct comprehensive web research...",
    model="glm-4.5",
    use_websearch=true
)
```

**Expected Behavior:**
GLM model performs web search and returns results with sources

**Actual Behavior:**
```
"I'll help you conduct comprehensive research... Please perform a web search on 
'zai-sdk PyPI latest version' and then continue this analysis using the 
continuation_id from this response."
```

**Root Cause Analysis:**

1. **Tool schema not injected:** web_search tool not added to GLM API payload
2. **Configuration issue:** GLM_ENABLE_WEB_BROWSING=true but not working
3. **Provider implementation:** GLM chat provider not calling capabilities layer
4. **Missing integration:** Chat tool → Capabilities → Provider → API chain broken

**Why This Happened:**
- Chat tool has `use_websearch` parameter ✅
- GLMCapabilities.get_websearch_tool_schema() exists ✅
- GLM_ENABLE_WEB_BROWSING=true in .env ✅
- **BUT:** The integration between these components is broken

**Detailed Investigation Needed:**

Let me trace the flow:
```
1. User calls chat_EXAI-WS(use_websearch=true)
   ↓
2. Chat tool receives use_websearch parameter
   ↓
3. Chat tool should call GLMCapabilities.get_websearch_tool_schema()
   ↓
4. Capabilities should return: tools=[{"type": "web_search", "web_search": {}}]
   ↓
5. Chat tool should pass tools to provider
   ↓
6. Provider should add tools to API payload
   ↓
7. GLM API should receive and use web_search tool
```

**Where is it breaking?**
- Step 3? Chat tool not calling capabilities?
- Step 5? Tools not passed to provider?
- Step 6? Provider not adding tools to payload?

**Fix Required:**
1. **Debug the integration:** Trace the actual flow with logging
2. **Add payload logging:** Log what's sent to GLM API
3. **Test with glm_payload_preview:** Verify tools are in payload
4. **Fix the broken link:** Repair the integration chain
5. **Add integration tests:** Prevent regression

**Impact:** HIGH - Core functionality broken, blocks research workflow

---

### Error #4: Tool Name Confusion (Not an Error, But a Problem)

**What I Did:**
```python
# Tried these variations:
thinkdeep_EXAI-WS(...)  # Error: Tool does not exist
thinkdeep_EXAI_WS(...)  # Error: Tool does not exist
thinkdeep(...)          # Error: Tool does not exist
```

**What Actually Works:**
```python
# From Augment environment:
# Tools are exposed WITHOUT the _EXAI-WS suffix
# But the WS daemon normalizes names
```

**Root Cause Analysis:**

1. **Naming inconsistency:** Tools have different names in different contexts
2. **WS daemon normalization:** Strips suffixes like "_EXAI-WS"
3. **Augment integration:** Exposes tools with specific naming
4. **Documentation gap:** No clear guide on which names to use where

**Why This Happened:**
- WS daemon has name normalization (line 207-235 in ws_server.py)
- Augment may expose tools differently
- No clear documentation on naming conventions
- Confusion between MCP tool names and internal names

**Fix Required:**
1. **Document tool names:** Clear guide on naming in different contexts
2. **Consistent naming:** Standardize across all interfaces
3. **Better error messages:** "Tool 'thinkdeep_EXAI-WS' not found. Did you mean 'thinkdeep'?"
4. **Alias support:** Accept multiple name variations

**Impact:** MEDIUM - Confusing for new users, wastes time

---

## 🔍 Root Cause Categories

### Category 1: Tool Purpose Misunderstanding
**Tools Affected:** analyze, thinkdeep, chat  
**Issue:** Users don't know which tool to use for which purpose  
**Fix:** Clear documentation and tool selection guide

### Category 2: Parameter Inconsistency
**Tools Affected:** All workflow tools  
**Issue:** Different tools use different parameter names (prompt vs step)  
**Fix:** Standardize parameters or document clearly

### Category 3: Integration Broken
**Tools Affected:** chat (web search)  
**Issue:** use_websearch parameter doesn't trigger actual web search  
**Fix:** Debug and repair the integration chain

### Category 4: Naming Confusion
**Tools Affected:** All EXAI tools  
**Issue:** Tool names vary by context (_EXAI-WS suffix or not)  
**Fix:** Standardize naming and document conventions

### Category 5: Error Messages Unhelpful
**Tools Affected:** All tools  
**Issue:** Errors don't suggest solutions or alternatives  
**Fix:** Improve error messages with helpful suggestions

---

## 🛠️ Fixes Needed for Turnkey System

### Fix #1: Tool Selection Guide (HIGH PRIORITY)

**Create:** `docs/guides/tool-selection-guide.md`

**Content:**
```markdown
# Which EXAI Tool Should I Use?

## For Web Research
❌ DON'T use: analyze, thinkdeep
✅ DO use: chat (once web search is fixed)
✅ WORKAROUND: Use Augment's web-search tool

## For Code Analysis
✅ DO use: analyze, codereview
❌ DON'T use: chat

## For Investigation
✅ DO use: thinkdeep, debug
✅ REQUIRES: Step-by-step workflow

## For Planning
✅ DO use: planner
✅ REQUIRES: Step-by-step workflow
```

**Impact:** Prevents tool misuse, saves time

---

### Fix #2: Parameter Reference Guide (MEDIUM PRIORITY)

**Create:** `docs/guides/parameter-reference.md`

**Content:**
```markdown
# EXAI Tool Parameters

## chat_EXAI-WS
- prompt: string (required)
- model: string (optional)
- use_websearch: boolean (optional)

## thinkdeep_EXAI-WS
- step: string (required) ← NOT 'prompt'!
- step_number: integer (required)
- findings: string (required)

## analyze_EXAI-WS
- step: string (required) ← NOT 'prompt'!
- relevant_files: array (required) ← Must be absolute paths!
```

**Impact:** Reduces parameter errors

---

### Fix #3: Fix Native Web Search (CRITICAL PRIORITY)

**Investigation Steps:**
1. Add logging to chat tool to see if use_websearch is received
2. Add logging to capabilities layer to see if get_websearch_tool_schema() is called
3. Add logging to provider to see if tools are passed
4. Use glm_payload_preview to inspect actual API payload
5. Compare working vs non-working payloads
6. Fix the broken integration point

**Files to Investigate:**
- `tools/chat.py` - Does it call capabilities?
- `src/providers/capabilities.py` - Is get_websearch_tool_schema() called?
- `src/providers/glm_chat.py` - Are tools added to payload?
- `src/server/handlers/request_handler_execution.py` - Any middleware?

**Impact:** CRITICAL - Enables core functionality

---

### Fix #4: Improve Error Messages (MEDIUM PRIORITY)

**Examples of Better Errors:**

**Before:**
```
Input validation error: 'step' is a required property
```

**After:**
```
Input validation error: 'step' is a required property
Hint: thinkdeep uses 'step' parameter, not 'prompt'. 
Did you mean to use the chat tool instead?
```

**Before:**
```
All file paths must be FULL absolute paths. Invalid path: '.'
```

**After:**
```
All file paths must be FULL absolute paths. Invalid path: '.'
Hint: analyze requires code files for analysis. 
Example: relevant_files=["c:\\Project\\file.py"]
For web research, use the chat tool instead.
```

**Impact:** Better user experience, faster problem resolution

---

### Fix #5: Tool Name Standardization (LOW PRIORITY)

**Options:**

**Option A:** Always use base names (no suffix)
```python
chat(...)
thinkdeep(...)
analyze(...)
```

**Option B:** Always use full names (with suffix)
```python
chat_EXAI-WS(...)
thinkdeep_EXAI-WS(...)
analyze_EXAI-WS(...)
```

**Option C:** Accept both (recommended)
```python
# Both work:
chat(...) 
chat_EXAI-WS(...)
```

**Recommendation:** Option C with clear documentation

**Impact:** Reduces confusion, improves consistency

---

## 📊 Priority Matrix

| Fix | Priority | Impact | Effort | Status |
|-----|----------|--------|--------|--------|
| Fix native web search | 🔴 CRITICAL | HIGH | HIGH | Not started |
| Tool selection guide | 🟡 HIGH | MEDIUM | LOW | Not started |
| Parameter reference | 🟡 MEDIUM | MEDIUM | LOW | Not started |
| Better error messages | 🟡 MEDIUM | MEDIUM | MEDIUM | Not started |
| Name standardization | 🟢 LOW | LOW | LOW | Not started |

---

## 🎯 Implementation Checklist

### Phase 1: Documentation (Quick Wins)
- [ ] Create tool selection guide
- [ ] Create parameter reference guide
- [ ] Document tool naming conventions
- [ ] Add examples for each tool
- [ ] Update README with guides

### Phase 2: Fix Web Search (Critical)
- [ ] Add logging to trace integration flow
- [ ] Test with glm_payload_preview
- [ ] Identify broken integration point
- [ ] Fix the integration
- [ ] Add integration tests
- [ ] Verify web search works

### Phase 3: Improve Error Messages
- [ ] Identify common error patterns
- [ ] Add helpful hints to errors
- [ ] Suggest alternatives when tool misused
- [ ] Test error messages with users

### Phase 4: Standardization
- [ ] Standardize parameter names (if possible)
- [ ] Support multiple tool name variations
- [ ] Update all documentation
- [ ] Add migration guide

---

## 🔄 For Turnkey System

### What Users Need to Know

**1. Tool Selection**
- Clear guide on which tool for which purpose
- Examples of correct usage
- Common mistakes to avoid

**2. Parameter Usage**
- Reference for each tool's parameters
- Required vs optional parameters
- Type requirements (string, array, etc.)

**3. File Paths**
- Always use absolute paths
- Example: `c:\\Project\\EX-AI-MCP-Server\\file.py`
- Not: `./file.py` or `file.py`

**4. Web Search**
- Current status (working or not)
- Workaround if not working
- How to verify it's working

**5. Workflow Tools**
- Understand step-by-step nature
- Don't expect autonomous operation
- Investigation required between steps

---

## 📝 Summary

### Errors Encountered: 4
1. ❌ Invalid path error (analyze tool)
2. ❌ Missing 'step' parameter (thinkdeep tool)
3. ❌ Web search not working (chat tool)
4. ⚠️ Tool name confusion (all tools)

### Root Causes: 5
1. Tool purpose misunderstanding
2. Parameter inconsistency
3. Integration broken (web search)
4. Naming confusion
5. Unhelpful error messages

### Fixes Required: 5
1. 🔴 Fix native web search (CRITICAL)
2. 🟡 Tool selection guide (HIGH)
3. 🟡 Parameter reference (MEDIUM)
4. 🟡 Better error messages (MEDIUM)
5. 🟢 Name standardization (LOW)

### For Turnkey System:
- ✅ Clear documentation
- ✅ Working web search
- ✅ Helpful error messages
- ✅ Consistent naming
- ✅ Good examples

---

**Status:** Analysis complete, fixes identified  
**Next:** Add to implementation plan  
**Goal:** Seamless experience for GitHub users

