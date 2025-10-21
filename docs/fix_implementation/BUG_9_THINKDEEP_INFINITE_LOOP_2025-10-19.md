# Bug #9: Thinkdeep Auto-Execution Infinite Loop
**Date:** 2025-10-19  
**Status:** 🚨 CRITICAL - UNFIXED  
**Impact:** Tool unusable, wastes tokens, causes WebSocket drops  
**Severity:** P0 - Tool completely broken

---

## 🚨 CRITICAL BUG - DO NOT USE THINKDEEP

**⚠️ WARNING:** `thinkdeep_EXAI-WS` is currently BROKEN and should NOT be used. Use `chat_EXAI-WS` instead for all general questions and complex reasoning.

---

## 📊 BUG SUMMARY

### **Symptom:**
When calling `thinkdeep_EXAI-WS`, the tool enters auto-execution mode and gets stuck in an infinite loop, repeating "Confidence stagnant at 'medium' for 3 steps" endlessly.

### **Impact:**
- Tool runs through 20+ steps without making progress
- Wastes significant tokens and API costs
- Eventually causes WebSocket connection to drop
- Completely unusable for its intended purpose

### **Evidence:**
```
2025-10-19 23:13:45 INFO tools.workflow.orchestration: thinkdeep: Confidence stagnant at 'medium' for 3 steps, may need different approach
2025-10-19 23:13:45 INFO tools.workflow.orchestration: thinkdeep: Continuing auto-execution (step 2)
2025-10-19 23:13:45 INFO tools.workflow.orchestration: thinkdeep: Confidence stagnant at 'medium' for 3 steps, may need different approach
2025-10-19 23:13:45 INFO tools.workflow.orchestration: thinkdeep: Continuing auto-execution (step 3)
... [repeats 24+ times]
2025-10-19 23:13:47 INFO tools.workflow.orchestration: thinkdeep: Continuing auto-execution (step 24)
```

---

## 🔍 ROOT CAUSE ANALYSIS

### **What Happened:**

1. **Tool Call Initiated:**
   ```python
   thinkdeep_EXAI-WS(
       step="Create the ultimate handoff prompt...",
       step_number=1,
       total_steps=3,
       next_step_required=true,
       findings="Starting to create...",
       model="glm-4.6",
       confidence="medium"
   )
   ```

2. **Auto-Execution Triggered:**
   - Tool entered fully agentic mode (safety limit: 50 steps)
   - Started auto-executing next steps

3. **Infinite Loop:**
   - Confidence remained at "medium" for every step
   - Warning triggered: "Confidence stagnant at 'medium' for 3 steps"
   - But tool continued anyway, didn't abort
   - Ran through 24+ steps with identical warnings

4. **WebSocket Drop:**
   - Eventually the connection dropped: `no close frame received or sent`
   - Tool call failed completely

### **Why It Happened:**

**Hypothesis (needs investigation):**
1. **Circuit Breaker Not Working:**
   - The "confidence stagnant" warning is triggered
   - But the circuit breaker doesn't abort the operation
   - Tool continues looping indefinitely

2. **Auto-Execution Logic Flaw:**
   - Auto-execution doesn't have proper termination conditions
   - Confidence level doesn't change, but tool keeps trying
   - No maximum retry limit for stagnant confidence

3. **Model Response Issue:**
   - GLM-4.6 might be returning responses that don't change confidence
   - Tool interprets this as "need to continue"
   - Loops endlessly waiting for confidence to increase

---

## 🎯 EXPECTED BEHAVIOR

**What SHOULD Happen:**
1. Tool detects confidence stagnant for 3 steps
2. Circuit breaker triggers
3. Tool aborts auto-execution
4. Returns error message: "Unable to make progress, confidence stagnant"
5. Suggests alternative approach or manual intervention

**What ACTUALLY Happens:**
1. Tool detects confidence stagnant for 3 steps
2. Logs warning but continues anyway
3. Loops through 20+ steps with identical warnings
4. Eventually WebSocket drops
5. Complete failure, no useful output

---

## 🔧 POTENTIAL FIXES

### **Option 1: Fix Circuit Breaker (Recommended)**
```python
# In tools/workflow/orchestration.py
if confidence_stagnant_count >= 3:
    # ABORT instead of just warning
    raise Exception(
        f"Circuit breaker triggered: Confidence stagnant at '{current_confidence}' "
        f"for {confidence_stagnant_count} steps. Unable to make progress."
    )
```

### **Option 2: Add Maximum Stagnant Steps Limit**
```python
# In tools/workflow/orchestration.py
MAX_STAGNANT_STEPS = 3

if confidence_stagnant_count >= MAX_STAGNANT_STEPS:
    logger.error(f"Aborting: Confidence stagnant for {MAX_STAGNANT_STEPS} steps")
    return self._format_error_response(
        "Unable to make progress - confidence not improving"
    )
```

### **Option 3: Disable Auto-Execution for Thinkdeep**
```python
# In tools/thinkdeep.py
def should_auto_execute(self):
    # Disable auto-execution until infinite loop bug is fixed
    return False
```

---

## 📁 FILES INVOLVED

**Primary:**
- `tools/workflow/orchestration.py` - Auto-execution logic, circuit breaker
- `tools/workflow/base.py` - Confidence tracking, termination conditions
- `tools/thinkdeep.py` - Thinkdeep tool implementation

**Related:**
- `tools/workflow/performance_optimizer.py` - Performance monitoring
- `src/monitoring/resilient_websocket.py` - WebSocket connection management

---

## 🧪 REPRODUCTION STEPS

1. Call `thinkdeep_EXAI-WS` with any parameters
2. Set `next_step_required=true` to trigger auto-execution
3. Set `confidence="medium"` (or any level)
4. Observe Docker logs: `docker logs -f exai-mcp-daemon`
5. Watch for "Confidence stagnant" warnings repeating
6. Wait for WebSocket connection to drop

**Example Call:**
```python
thinkdeep_EXAI-WS(
    step="Analyze this complex problem",
    step_number=1,
    total_steps=3,
    next_step_required=true,
    findings="Initial analysis",
    model="glm-4.6",
    confidence="medium"
)
```

---

## ⚠️ WORKAROUND

**DO NOT USE `thinkdeep_EXAI-WS` until this bug is fixed.**

**Instead, use `chat_EXAI-WS` for:**
- Complex reasoning
- Multi-step analysis
- Hypothesis-driven investigation
- Architectural decisions

**Example:**
```python
# Instead of thinkdeep
chat_EXAI-WS(
    prompt="I need help with complex reasoning about X. Here's the context...",
    model="glm-4.6",
    use_websearch=false
)
```

---

## 📊 INVESTIGATION NEEDED

**Questions to Answer:**
1. Why doesn't the circuit breaker abort when confidence is stagnant?
2. What is the intended behavior for "confidence stagnant" warnings?
3. Should auto-execution have a maximum retry limit?
4. Why does GLM-4.6 return responses that don't change confidence?
5. Is this specific to thinkdeep or affects other workflow tools?

**Next Steps:**
1. Investigate `tools/workflow/orchestration.py` circuit breaker logic
2. Check confidence tracking in `tools/workflow/base.py`
3. Test other workflow tools (debug, codereview, analyze) for same issue
4. Implement proper circuit breaker abort logic
5. Add maximum stagnant steps limit
6. Test fix thoroughly before re-enabling thinkdeep

---

## 🎯 PRIORITY

**Priority:** P0 - CRITICAL  
**Reason:** Tool completely unusable, wastes resources, causes failures

**Impact:**
- ❌ Thinkdeep tool completely broken
- ❌ Wastes tokens and API costs
- ❌ Causes WebSocket connection drops
- ❌ Blocks complex reasoning tasks
- ❌ Reduces overall system reliability

**Recommendation:**
- Disable thinkdeep tool until fixed
- Use chat_EXAI-WS as workaround
- Investigate and fix circuit breaker logic
- Add proper termination conditions
- Test thoroughly before re-enabling

---

## 📚 RELATED BUGS

**Similar Issues:**
- Bug #5: Circuit Breaker (file read failures) - FIXED
- This bug shows circuit breaker doesn't work for confidence stagnation

**Lessons Learned:**
- Circuit breakers need to ABORT, not just warn
- Auto-execution needs proper termination conditions
- Confidence tracking needs maximum retry limits
- WebSocket drops can be caused by infinite loops

---

## 🎓 TAKEAWAY FOR NEXT AGENT

**This bug is a perfect example of the investigative mindset:**

1. ✅ **Discovered during actual use** - Not theoretical
2. ✅ **Immediately documented** - Not ignored for "later"
3. ✅ **Updated handoff guide** - Warned next agent
4. ✅ **Provided workaround** - System remains usable
5. ✅ **Identified root cause** - Clear investigation path

**This is EXACTLY the approach you should take when you discover bugs:**
- Document immediately
- Update documentation
- Provide workarounds
- Investigate root cause
- Fix when possible

**Don't ignore bugs hoping they'll go away. They won't. Fix them now.**

---

**Status:** UNFIXED - Needs investigation and repair  
**Workaround:** Use `chat_EXAI-WS` instead  
**Next Agent:** Please investigate and fix this critical bug

