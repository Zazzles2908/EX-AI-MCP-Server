# NEXT AGENT PROMPT - 2025-10-04

**From:** Autonomous Phase 3 Agent (Claude Sonnet 4.5)  
**To:** Next Agent  
**Date:** 2025-10-04  
**Session Type:** Phase 3 Continuation + Testing

---

## 🎯 YOUR MISSION

Continue the autonomous Phase 3 work session. The previous agent completed **3 critical bug fixes** and **2 Phase 3 tasks**. Your job is to:

1. **Test the bug fixes** (30 minutes)
2. **Complete remaining Phase 3 tasks** (8-11 hours)
3. **Create comprehensive handover** for next agent

**Goal:** Make substantial progress so the next agent has significantly more functionality to test.

---

## 📋 QUICK START CHECKLIST

### Step 1: Read Context (5 min)
- [ ] Read `AUTONOMOUS_SESSION_2025-10-04_PHASE3_COMPLETION.md`
- [ ] Understand the 3 bug fixes applied
- [ ] Review Phase 3 status (2/9 tasks complete)

### Step 2: Restart Server (2 min)
```powershell
powershell -ExecutionPolicy Bypass -File C:\Project\EX-AI-MCP-Server\scripts\ws_start.ps1 -Restart
```

### Step 3: Test Bug Fixes (15 min)
- [ ] Test web search integration
- [ ] Test expert validation
- [ ] Verify no startup errors

### Step 4: Continue Phase 3 (8-11 hours)
- [ ] Task 3.6: Handler fragmentation audit
- [ ] Task 3.7: tools/shared/ systematic review
- [ ] Task 3.8: Provider module audit
- [ ] Task 3.9: Legacy CLAUDE_* variables documentation

### Step 5: Create Handover (30 min)
- [ ] Document all work completed
- [ ] Update markdown files
- [ ] Create prompt for next agent

---

## 🔧 BUG FIXES TO TEST

### Bug #1: Web Search Integration ✅ FIXED
**What was fixed:** Import path in `text_format_handler.py` line 108

**Test Command:**
```python
chat_exai(
    prompt="What are the latest Python async best practices in 2024?",
    use_websearch=true,
    model="glm-4.5-flash"
)
```

**Expected Result:**
- Web search executes successfully
- Returns results with sources
- No `<tool_call>web_search\nquery: ...` text

**Before Fix:**
- Returned tool_call as text instead of executing
- No search results in response

**If Test Fails:**
- Check server was restarted
- Verify `text_format_handler.py` has correct import
- Check logs for ImportError

---

### Bug #2: Expert Validation ✅ FIXED
**What was fixed:** Added `DEFAULT_USE_ASSISTANT_MODEL` config, updated thinkdeep.py

**Test Command:**
```python
thinkdeep_exai(
    step="Analyze whether Python's asyncio or threading is better for I/O-bound tasks",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Testing expert validation functionality",
    model="glm-4.5-flash",
    thinking_mode="low"
)
```

**Expected Result:**
- Returns `expert_analysis` with comprehensive insights
- NOT `expert_analysis: null`
- Expert analysis provides additional validation

**Before Fix:**
- Returned `expert_analysis: null`
- Only returned workflow scaffolding

**If Test Fails:**
- Check `config.py` has `DEFAULT_USE_ASSISTANT_MODEL = true`
- Verify `thinkdeep.py` updated with new priority order
- Check if tool-specific env override is set to false

---

### Bug #3: Model 'auto' Resolution ✅ VERIFIED
**Status:** Already fixed in previous session, just verify it works

**Test Command:**
```python
chat_exai(
    prompt="Hello, test auto model resolution",
    model="auto"
)
```

**Expected Result:**
- Routes to appropriate model (likely glm-4.5-flash)
- No error: "Model 'auto' is not available"
- Response is generated successfully

---

## 📊 PHASE 3 STATUS

### Completed Tasks ✅
- ✅ Task 3.1: Dual tool registration eliminated (14 lines)
- ✅ Task 3.2: Hardcoded tool lists removed
- ✅ Task 3.3: Entry point complexity reduced (73 lines)
- ✅ Task 3.4: Dead code removal (123 lines - browse_cache.py, search_cache.py)
- ✅ Task 3.5: systemprompts/ audit (no changes needed - already well-organized)

**Total Progress:** 5/9 tasks (56%)  
**Lines Reduced:** 210 lines

### Remaining Tasks ⏳
- ⏳ Task 3.6: Handler fragmentation audit (2-3 hours)
- ⏳ Task 3.7: tools/shared/ systematic review (2-3 hours)
- ⏳ Task 3.8: Provider module audit (3-4 hours)
- ⏳ Task 3.9: Legacy CLAUDE_* variables documentation (1 hour)

**Estimated Remaining:** 8-11 hours

---

## 🎯 YOUR TASKS IN DETAIL

### Task 3.6: Handler Fragmentation Audit (2-3 hours)

**Goal:** Analyze 8 handler modules in `src/server/handlers/` for over-fragmentation or consolidation opportunities.

**Approach:**
1. Use `analyze_exai` or `refactor_exai` to review handler modules
2. Map handler flow with `tracer_exai` if needed
3. Identify fragmentation vs cohesion
4. Create consolidation plan if opportunities found

**Files to Review:**
- `src/server/handlers/request_handler.py`
- `src/server/handlers/request_handler_execution.py`
- `src/server/handlers/request_handler_model_resolution.py`
- `src/server/handlers/request_handler_context.py`
- `src/server/handlers/request_handler_post_processing.py`
- `src/server/handlers/mcp_handlers.py`
- Other handler files in the directory

**Questions to Answer:**
- Are handlers appropriately separated by concern?
- Is there duplication across handlers?
- Are any handlers too small/fragmented?
- Would consolidation improve maintainability?

---

### Task 3.7: tools/shared/ Systematic Review (2-3 hours)

**Goal:** Review all 6 core shared tool files for patterns and inconsistencies.

**Approach:**
1. Use `codereview_exai` to review each file
2. Identify patterns and anti-patterns
3. Create consolidation recommendations
4. Document findings

**Files to Review:**
- `tools/shared/base_tool.py`
- `tools/shared/base_tool_core.py`
- `tools/shared/base_tool_model_management.py`
- `tools/shared/base_models.py`
- `tools/shared/error_envelope.py`
- `tools/shared/schema_builder.py`

**Questions to Answer:**
- Are there consistent patterns across files?
- Is there code duplication?
- Are abstractions appropriate?
- Would refactoring improve clarity?

---

### Task 3.8: Provider Module Audit (3-4 hours)

**Goal:** Comprehensive audit of `src/providers/` ecosystem.

**Approach:**
1. Use `analyze_exai` to review provider ecosystem
2. Identify patterns and inconsistencies
3. Create consolidation plan
4. Document findings

**Areas to Review:**
- Provider implementations (glm_chat.py, kimi_chat.py, etc.)
- Provider registry and selection
- Provider capabilities
- Provider-specific utilities

**Questions to Answer:**
- Are providers consistently structured?
- Is there duplication across providers?
- Are capabilities properly abstracted?
- Would consolidation improve maintainability?

---

### Task 3.9: Legacy CLAUDE_* Variables Documentation (1 hour)

**Goal:** Document and create deprecation plan for legacy CLAUDE_* environment variables.

**Approach:**
1. Search codebase for all CLAUDE_* references
2. Document current usage
3. Create deprecation plan
4. Provide migration guide

**Files to Check:**
- `src/server/handlers/mcp_handlers.py` line 48
- Any other files with CLAUDE_* references

**Deliverables:**
- List of all CLAUDE_* variables
- Current usage documentation
- Deprecation timeline
- Migration guide for users

---

## 🛠️ RECOMMENDED TOOLS

### For Analysis Tasks
- `analyze_exai` - Strategic architectural assessment
- `refactor_exai` - Refactoring opportunities analysis
- `codereview_exai` - Systematic code review

### For Investigation
- `tracer_exai` - Call flow and dependency mapping
- `debug_exai` - Root cause analysis if issues found

### For Documentation
- `chat_exai` - Brainstorming and validation
- Standard file tools - Reading and writing

---

## 📝 HANDOVER REQUIREMENTS

When you complete your work, create:

1. **Session Summary Document**
   - What you accomplished
   - What you tested
   - What you found
   - What remains

2. **Updated Phase 3 Status**
   - Tasks completed
   - Lines reduced
   - Issues found
   - Recommendations

3. **Next Agent Prompt**
   - Clear instructions
   - Context summary
   - Action items
   - Testing procedures

---

## ⚠️ CRITICAL WARNINGS

### DO NOT Remove These Files
- ❌ `utils/file_cache.py` - ACTIVELY USED by GLM and Kimi
- ❌ Any file without thorough verification

### ALWAYS Before Making Changes
1. Search entire codebase for usage
2. Verify no indirect dependencies
3. Test server startup after changes
4. Document all modifications

### If You Find Issues
1. Document the issue clearly
2. Identify root cause
3. Propose fix with rationale
4. Test fix thoroughly
5. Document in handover

---

## 💡 TIPS FOR SUCCESS

### Use EXAI Tools Effectively
- Start with `analyze_exai` for high-level understanding
- Use `refactor_exai` for specific refactoring opportunities
- Use `codereview_exai` for detailed code review
- Use `tracer_exai` when you need to understand call flows

### Work Systematically
1. Read and understand before changing
2. Document findings as you go
3. Test after each significant change
4. Create clear handover documentation

### Focus on Value
- Prioritize high-impact changes
- Don't over-engineer solutions
- Maintain backward compatibility
- Document trade-offs clearly

---

## 📚 REFERENCE DOCUMENTS

**Must Read:**
- `docs/auggie_reports/AUTONOMOUS_SESSION_2025-10-04_PHASE3_COMPLETION.md`
- `docs/auggie_reports/phase3_architectural_refactoring_summary.md`

**Helpful Context:**
- `docs/auggie_reports/HANDOVER_TO_USER_2025-10-04.md`
- `docs/auggie_reports/CRITICAL_BUGS_FIXED_2025-10-04.md`

**Phase 3 Details:**
- `docs/auggie_reports/PHASE_3_TASK_3.4_ANALYSIS_REPORT.md`
- `docs/auggie_reports/PHASE_3_TASK_3.3_IMPLEMENTATION_REPORT.md`

---

## 🚀 READY TO START?

1. Read `AUTONOMOUS_SESSION_2025-10-04_PHASE3_COMPLETION.md`
2. Restart the server
3. Test the 3 bug fixes
4. Continue with Phase 3 tasks
5. Create comprehensive handover

**Remember:** The goal is to make substantial progress so the next agent has significantly more functionality to test. Focus on completing multiple tasks in this session.

**Good luck!** 🎉

---

**Questions?** Review the reference documents or use `chat_exai` to brainstorm approaches.

**Stuck?** Document what you tried, what didn't work, and pass it to the next agent with clear context.

**Success?** Document everything clearly so the next agent can build on your work!

