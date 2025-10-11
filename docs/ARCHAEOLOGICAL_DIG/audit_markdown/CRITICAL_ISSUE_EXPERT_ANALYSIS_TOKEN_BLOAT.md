# CRITICAL ISSUE: Expert Analysis Token Bloat

**Date:** 2025-10-11 (11th October 2025, Friday)  
**Severity:** 🔴 CRITICAL  
**Status:** 🚨 BLOCKING PHASE 2 COMPLETION  
**Discovered During:** Task 2.G.4 (WorkflowTool Testing)

---

## 🚨 ISSUE SUMMARY

Expert analysis in WorkflowTools is sending **1.28 MILLION input tokens** for a simple question, causing:
- **Extreme costs:** $0.77 per call (should be ~$0.01)
- **Slow performance:** 63 seconds for simple analysis (should be ~5-10s)
- **Poor user experience:** Long waits for basic questions

---

## 📊 EVIDENCE

### Test Case
**Tool:** thinkdeep  
**Question:** "Should we implement a circuit breaker pattern for the GLM and Kimi API calls?"  
**Expected tokens:** ~500-1000 input tokens  
**Actual tokens:** 1,279,891 input tokens (1.28M!)  

### GLM API Usage Data
```
2025-10-10  1bd7...93e9  inference  std  glm-4.6  INPUT  0.0006kToken  
1,279,891 tokens  $0.7679346  Paid
```

### Server Logs
```
2025-10-11 18:26:04 WARNING tools.workflow.expert_analysis: 🔥 [EXPERT_ANALYSIS_START]
Tool: thinkdeep
Model: glm-4.6
Thinking Mode: low
Temperature: 0.7
Prompt Length: 293 chars  ← MISLEADING! Actual tokens: 1.28M
```

### Timeline
- **18:26:04** - Expert analysis started
- **18:26:11** - Progress: 5% | Elapsed: 7.0s | ETA: 119.0s
- **18:26:12** - Cancelled by user (seemed hung)
- **18:27:07** - GLM API actually returned (63 seconds total)

---

## 🔍 ROOT CAUSE ANALYSIS

### Hypothesis 1: File Inclusion Gone Wrong
**Log evidence:**
```
[EXPERT_ANALYSIS_DEBUG] File inclusion disabled (EXPERT_ANALYSIS_INCLUDE_FILES=false)
```

File inclusion is supposedly disabled, but 1.28M tokens suggests files ARE being included.

**Possible causes:**
1. `EXPERT_ANALYSIS_INCLUDE_FILES=false` not being respected
2. Files being included through a different code path
3. Conversation history including massive file contents

### Hypothesis 2: Conversation History Bloat
**Possible causes:**
1. Entire conversation history being sent (including all previous file contents)
2. Thread context reconstruction including too much data
3. No token limit on conversation history

### Hypothesis 3: Hidden Context Injection
**Possible causes:**
1. System prompts including large amounts of data
2. Tool definitions being sent with every call
3. Provider-specific context being added

---

## 🎯 IMPACT ASSESSMENT

### Cost Impact
**Current state:**
- Simple thinkdeep call: $0.77
- If testing all 12 WorkflowTools: ~$9.24
- If used in production (100 calls/day): $77/day = $2,310/month

**Expected state:**
- Simple thinkdeep call: ~$0.01
- Testing all 12 WorkflowTools: ~$0.12
- Production (100 calls/day): $1/day = $30/month

**Cost multiplier:** 77x too expensive!

### Performance Impact
- **Current:** 63 seconds for simple analysis
- **Expected:** 5-10 seconds
- **Slowdown:** 6-12x slower than expected

### User Experience Impact
- Users wait over 1 minute for simple questions
- Appears to be "hanging" (I cancelled after 8 seconds)
- Unpredictable costs for users

---

## 🔧 INVESTIGATION NEEDED

### Immediate Actions
1. **Check actual prompt being sent to GLM**
   - Add logging to show full prompt before API call
   - Count actual tokens in prompt
   - Identify what's consuming 1.28M tokens

2. **Verify EXPERT_ANALYSIS_INCLUDE_FILES flag**
   - Check if flag is being respected
   - Search for other file inclusion code paths
   - Verify conversation history doesn't include files

3. **Review conversation history handling**
   - Check if thread context is being included
   - Verify conversation history token limits
   - Check for hidden context injection

### Code Locations to Investigate
- `tools/workflow/expert_analysis.py` - Expert analysis implementation
- `utils/conversation/history.py` - Conversation history formatting
- `src/server/context/thread_context.py` - Thread context reconstruction
- `src/providers/glm_chat.py` - GLM provider implementation

---

## 🚫 BLOCKING ISSUES

This issue **BLOCKS** the following Phase 2 Cleanup tasks:

- ❌ **Task 2.G.4:** Test All WorkflowTools (can't afford to test 12 tools at $0.77 each)
- ❌ **Task 2.G.5:** Cross-Provider Testing (same issue likely affects Kimi)
- ❌ **Task 2.G.6:** Performance Regression Testing (this IS a performance regression)
- ❌ **Task 2.G.7:** Upload Documentation for AI QA (would consume massive tokens)
- ❌ **Task 2.H:** Expert Validation & Summary (same issue)

**Cannot proceed with Phase 2 Cleanup until this is resolved.**

---

## 📝 RECOMMENDED ACTIONS

### Option A: Fix Immediately (RECOMMENDED)
1. Investigate root cause (1-2 hours)
2. Fix token bloat issue (1-2 hours)
3. Test fix with thinkdeep (15 minutes)
4. Resume Task 2.G.4 testing

**Total time:** 2-4 hours  
**Benefit:** Proper testing, reasonable costs, better performance

### Option B: Disable Expert Analysis Temporarily
1. Set `use_assistant_model=false` for all WorkflowTool tests
2. Complete Task 2.G.4 without expert analysis
3. Fix token bloat issue later

**Total time:** 15 minutes to resume testing  
**Drawback:** Incomplete testing, issue persists

### Option C: Skip WorkflowTool Testing
1. Mark Task 2.G.4 as "DEFERRED - Token bloat issue"
2. Proceed to Task 2.G.5 (Cross-Provider Testing)
3. Fix token bloat issue in Phase 3

**Total time:** Immediate  
**Drawback:** Incomplete Phase 2 Cleanup, issue persists

---

## 🎯 DECISION REQUIRED

**User decision needed:**
- **Option A:** Fix token bloat now (2-4 hours) - Thorough approach
- **Option B:** Disable expert analysis temporarily - Quick workaround
- **Option C:** Skip WorkflowTool testing - Defer to Phase 3

**My recommendation:** Option A - Fix the issue now. This is a critical bug that affects all WorkflowTools and will cause problems in production if not addressed.

---

## 🔗 RELATED DOCUMENTS

- `docs/ARCHAEOLOGICAL_DIG/MASTER_CHECKLIST_PHASE2_CLEANUP.md` - Task 2.G.4 checklist
- `tools/workflow/expert_analysis.py` - Expert analysis implementation
- `logs/ws_daemon.log` - Server logs showing the issue

---

**STATUS:** 🚨 CRITICAL ISSUE - BLOCKING PHASE 2 COMPLETION - USER DECISION REQUIRED

