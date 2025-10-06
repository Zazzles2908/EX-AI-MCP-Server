# ExAI Function Test Plan

**Date:** 2025-10-04  
**Status:** 🔄 IN PROGRESS  
**Priority:** HIGH

---

## 🎯 OBJECTIVE

Systematically test each ExAI function to verify:
1. Operational effectiveness (not placeholder implementations)
2. Response authenticity and quality
3. Performance metrics
4. Integration with provider layer
5. Web search functionality where applicable

---

## 📋 TEST MATRIX

### Simple Tools (7 tools)

| Tool | Status | Test Type | Expected Duration | Notes |
|------|--------|-----------|-------------------|-------|
| chat_exai | ⏳ Pending | Basic + Web Search | < 30s | Test with and without web search |
| challenge_exai | ⏳ Pending | Basic | < 20s | Test critical analysis |
| activity_exai | ⏳ Pending | Log Analysis | < 10s | Test log filtering |
| listmodels_exai | ⏳ Pending | Registry Check | < 5s | Verify hidden tools |
| version_exai | ⏳ Pending | System Info | < 5s | Basic system check |

### Workflow Tools (9 tools)

| Tool | Status | Test Type | Expected Duration | Notes |
|------|--------|-----------|-------------------|-------|
| debug_exai | ⏳ Pending | 2-step workflow | < 30s total | Test pause enforcement |
| thinkdeep_exai | ⏳ Pending | Single-step analysis | < 30s | **CRITICAL: Verify 240s issue fixed** |
| analyze_exai | ⏳ Pending | Code analysis | < 30s | Test with real code |
| codereview_exai | ⏳ Pending | Code review | < 30s | Test with real code |
| testgen_exai | ⏳ Pending | Test generation | < 30s | Test with real code |
| consensus_exai | ⏳ Pending | Multi-model consensus | < 60s | Test with 2 models |
| planner_exai | ⏳ Pending | Planning workflow | < 30s | Test step-by-step planning |
| precommit_exai | ⏳ Pending | Git analysis | < 30s | Test with git changes |
| refactor_exai | ⏳ Pending | Refactoring analysis | < 30s | Test with real code |
| secaudit_exai | ⏳ Pending | Security audit | < 30s | Test with real code |
| tracer_exai | ⏳ Pending | Code tracing | < 30s | Test with real code |
| docgen_exai | ⏳ Pending | Documentation generation | < 30s | Test with real code |

---

## 🧪 TEST SCENARIOS

### Test 1: chat_exai (Basic)
**Purpose:** Verify basic chat functionality without web search

**Test Case:**
```python
chat_exai(
    prompt="Explain the difference between async and sync programming in Python",
    use_websearch=false,
    model="glm-4.5-flash"
)
```

**Expected Result:**
- Duration: < 20 seconds
- Response: Comprehensive explanation of async vs sync
- No web search results
- Real content (not placeholder)

**Success Criteria:**
- ✅ Response is relevant and accurate
- ✅ No web search was performed
- ✅ Duration within expected range
- ✅ No errors or timeouts

---

### Test 2: chat_exai (Web Search)
**Purpose:** Verify web search integration

**Test Case:**
```python
chat_exai(
    prompt="What are the latest features in Python 3.13?",
    use_websearch=true,
    model="glm-4.5-flash"
)
```

**Expected Result:**
- Duration: < 30 seconds
- Response: Information about Python 3.13 features from web search
- Web search results included
- Real content from recent sources

**Success Criteria:**
- ✅ Web search was performed
- ✅ Response includes current information
- ✅ Search results are relevant
- ✅ Duration within expected range
- ✅ No errors or timeouts

---

### Test 3: thinkdeep_exai (CRITICAL)
**Purpose:** Verify 240s performance issue is fixed

**Test Case:**
```python
thinkdeep_exai(
    step="Analyze the current state of the EX-AI-MCP-Server project",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Project analysis in progress",
    confidence="high",
    model="glm-4.5-flash"
)
```

**Expected Result:**
- Duration: < 30 seconds (NOT 240+ seconds)
- Response: Comprehensive analysis
- Expert validation: DISABLED (no expert_analysis in response)
- Real content (not placeholder)

**Success Criteria:**
- ✅ Duration < 30 seconds (CRITICAL)
- ✅ No expert validation performed
- ✅ Response is comprehensive
- ✅ No errors or timeouts

**CRITICAL:** This test verifies the Auggie CLI restart fixed the 240s delay issue.

---

### Test 4: debug_exai (2-step workflow)
**Purpose:** Verify workflow pause enforcement

**Test Case (Step 1):**
```python
debug_exai(
    step="Investigate why thinkdeep_exai was taking 240+ seconds",
    step_number=1,
    total_steps=2,
    next_step_required=true,
    findings="Initial investigation started",
    hypothesis="Configuration issue with expert validation",
    confidence="exploring",
    model="glm-4.5-flash"
)
```

**Expected Result (Step 1):**
- Duration: < 15 seconds
- Status: WORKFLOW_PAUSED
- Response: Investigation plan
- No expert validation

**Test Case (Step 2):**
```python
debug_exai(
    step="Analyze .env configuration and verify settings",
    step_number=2,
    total_steps=2,
    next_step_required=false,
    findings="Configuration verified, expert validation disabled",
    hypothesis="Auggie CLI needs restart to pick up new config",
    confidence="high",
    model="glm-4.5-flash"
)
```

**Expected Result (Step 2):**
- Duration: < 15 seconds
- Status: COMPLETE
- Response: Analysis complete
- No expert validation

**Success Criteria:**
- ✅ Step 1 pauses correctly
- ✅ Step 2 completes correctly
- ✅ Total duration < 30 seconds
- ✅ No expert validation performed
- ✅ No errors or timeouts

---

### Test 5: listmodels_exai
**Purpose:** Verify tool registry cleanup

**Test Case:**
```python
listmodels_exai()
```

**Expected Result:**
- Duration: < 5 seconds
- Response: List of available models and tools
- Hidden tools NOT visible:
  - ❌ glm_web_search
  - ❌ kimi_upload_and_extract
  - ❌ kimi_chat_with_tools
- Public tools visible:
  - ✅ chat_exai
  - ✅ debug_exai
  - ✅ thinkdeep_exai
  - ✅ All other ExAI tools

**Success Criteria:**
- ✅ Internal tools are hidden
- ✅ Public tools are visible
- ✅ Response is complete
- ✅ No errors

---

### Test 6: analyze_exai
**Purpose:** Verify code analysis functionality

**Test Case:**
```python
analyze_exai(
    step="Analyze the SimpleTool architecture and its benefits",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="SimpleTool provides clean separation of concerns",
    relevant_files=["c:\\Project\\EX-AI-MCP-Server\\tools\\simple\\base.py"],
    confidence="high",
    model="glm-4.5-flash"
)
```

**Expected Result:**
- Duration: < 30 seconds
- Response: Comprehensive code analysis
- No expert validation
- Real insights about SimpleTool architecture

**Success Criteria:**
- ✅ Analysis is comprehensive
- ✅ Insights are accurate
- ✅ Duration within expected range
- ✅ No errors or timeouts

---

### Test 7: codereview_exai
**Purpose:** Verify code review functionality

**Test Case:**
```python
codereview_exai(
    step="Review the tool registry cleanup changes in server.py",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Tool registry cleanup successfully hides internal tools",
    relevant_files=["c:\\Project\\EX-AI-MCP-Server\\server.py"],
    confidence="high",
    model="glm-4.5-flash"
)
```

**Expected Result:**
- Duration: < 30 seconds
- Response: Code review with feedback
- No expert validation
- Real code review insights

**Success Criteria:**
- ✅ Review is comprehensive
- ✅ Feedback is actionable
- ✅ Duration within expected range
- ✅ No errors or timeouts

---

## 📊 PERFORMANCE TARGETS

**With Expert Validation Disabled:**
- Simple tools: < 30 seconds
- Workflow tools (per step): < 30 seconds
- Workflow tools (total): < 60 seconds for 2-step workflows

**With Expert Validation Enabled (Future):**
- Final workflow step: 90-120 seconds (single expert call)
- NOT 240+ seconds (duplicate calls)

---

## 🚨 CRITICAL ISSUES TO VERIFY

1. **Thinkdeep 240s Delay:**
   - ❓ Is it fixed after Auggie CLI restart?
   - ❓ Does it complete in < 30 seconds?
   - ❓ Is expert validation disabled?

2. **Web Search Integration:**
   - ❓ Does chat_exai use web search when use_websearch=true?
   - ❓ Are search results included in response?
   - ❓ Is glm_web_search hidden from registry?

3. **Tool Registry Cleanup:**
   - ❓ Are internal tools hidden?
   - ❓ Are public tools visible?
   - ❓ Does listmodels_exai show correct tools?

---

## 📝 TEST EXECUTION LOG

**Test Results will be documented here as tests are executed.**

---

**Created:** 2025-10-04  
**Status:** IN PROGRESS  
**Priority:** HIGH

**Note:** Tests should be executed AFTER Auggie CLI restart to verify performance fixes.

