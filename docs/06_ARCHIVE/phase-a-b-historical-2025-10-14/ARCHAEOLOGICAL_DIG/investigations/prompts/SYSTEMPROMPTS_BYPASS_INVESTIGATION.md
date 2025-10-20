# SYSTEMPROMPTS INVESTIGATION - COMPLETE ✅
**Date:** 2025-10-10 (10th October 2025, Thursday)
**Category:** System Prompts Architecture
**Status:** ✅ ACTIVE - FULLY INTEGRATED
**Investigated:** 12:30 PM AEDT
**Classification:** ACTIVE - No bypass detected

---

## INVESTIGATION SUMMARY

**Question:** Is systemprompts/ used or bypassed by hardcoded prompts?

**Answer:** ✅ **FULLY INTEGRATED AND ACTIVE**

**Evidence:**
- 14 active imports found in tools/
- Execution flow traced and confirmed
- No hardcoded bypass detected
- System working as designed

---

## DETAILED FINDINGS

### Import Search Results

**Command:** `Get-ChildItem -Recurse -Include "*.py" | Select-String -Pattern "from systemprompts import"`

**Active Imports (14 files):**
1. `tools/workflows/analyze.py` (line 26) → `ANALYZE_PROMPT`
2. `tools/workflows/codereview.py` (line 26) → `CODEREVIEW_PROMPT`
3. `tools/workflows/consensus.py` (line 32) → `CONSENSUS_PROMPT`
4. `tools/workflows/consensus_config.py` (line 9) → `CONSENSUS_PROMPT`
5. `tools/workflows/debug.py` (line 27) → `DEBUG_ISSUE_PROMPT`
6. `tools/workflows/docgen.py` (line 30) → `DOCGEN_PROMPT`
7. `tools/workflows/planner.py` (line 32) → `PLANNER_PROMPT`
8. `tools/workflows/precommit.py` (line 25) → `PRECOMMIT_PROMPT`
9. `tools/workflows/refactor.py` (line 26) → `REFACTOR_PROMPT`
10. `tools/workflows/secaudit.py` (line 27) → `SECAUDIT_PROMPT`
11. `tools/workflows/testgen.py` (line 28) → `TESTGEN_PROMPT`
12. `tools/workflows/thinkdeep.py` (line 26) → `THINKDEEP_PROMPT`
13. `tools/workflows/tracer.py` (line 29) → `TRACER_PROMPT`
14. `tools/chat.py` (line 17) → `CHAT_PROMPT`

**Archive Imports (6 files - legacy backups):**
- `docs/archive/legacy-scripts/2025-10-02/*.py` (6 backup files)
- These are old backups, not active code

### Execution Flow Traced

**Pattern in all tools:**
```python
# Step 1: Import prompt from systemprompts
from systemprompts import ANALYZE_PROMPT

# Step 2: Define get_system_prompt() method
def get_system_prompt(self) -> str:
    return ANALYZE_PROMPT
```

**Execution flow confirmed:**
1. Tool imports prompt constant from systemprompts/
2. Tool defines `get_system_prompt()` that returns the imported prompt
3. SimpleTool.execute() calls `self.get_system_prompt()` (tools/simple/base.py line 453)
4. System prompt is passed to `provider.generate_content()` (line 574)
5. Provider sends system prompt to external AI

**Code Evidence:**
<augment_code_snippet path="tools/simple/base.py" mode="EXCERPT">
```python
# Line 453
base_system_prompt = self.get_system_prompt()

# Line 574
model_response = provider.generate_content(
    prompt=prompt,
    model_name=self._current_model_name,
    system_prompt=system_prompt,  # ← System prompt is used!
    temperature=temperature,
    ...
)
```
</augment_code_snippet>

### No Hardcoded Bypass Detected

**Checked for hardcoded prompts:**
- No hardcoded "You are a senior engineer" strings found in tools/
- No prompt bypass logic detected
- All tools use `get_system_prompt()` method
- All prompts flow through systemprompts/ imports

---

## CLASSIFICATION

**Status:** ✅ **ACTIVE - FULLY INTEGRATED**

**Justification:**
1. ✅ 14 tools actively import from systemprompts/
2. ✅ Execution flow confirmed through code tracing
3. ✅ No hardcoded bypass detected
4. ✅ System working as designed
5. ✅ Centralized prompt management is functioning correctly

---

## RECOMMENDATIONS

### Keep As-Is ✅
- systemprompts/ is the correct centralized prompt system
- No changes needed - system is properly integrated
- Architecture is clean and maintainable

### Optional Improvements
1. **Add Tests:** Consider adding tests to ensure prompts are never bypassed
2. **Documentation:** Document the prompt flow in architecture docs
3. **Validation:** Add runtime validation that system prompts are not empty

---

## TOOLS USING SYSTEMPROMPTS

| Tool | Prompt Constant | File |
|------|----------------|------|
| analyze | ANALYZE_PROMPT | tools/workflows/analyze.py |
| codereview | CODEREVIEW_PROMPT | tools/workflows/codereview.py |
| consensus | CONSENSUS_PROMPT | tools/workflows/consensus.py |
| debug | DEBUG_ISSUE_PROMPT | tools/workflows/debug.py |
| docgen | DOCGEN_PROMPT | tools/workflows/docgen.py |
| planner | PLANNER_PROMPT | tools/workflows/planner.py |
| precommit | PRECOMMIT_PROMPT | tools/workflows/precommit.py |
| refactor | REFACTOR_PROMPT | tools/workflows/refactor.py |
| secaudit | SECAUDIT_PROMPT | tools/workflows/secaudit.py |
| testgen | TESTGEN_PROMPT | tools/workflows/testgen.py |
| thinkdeep | THINKDEEP_PROMPT | tools/workflows/thinkdeep.py |
| tracer | TRACER_PROMPT | tools/workflows/tracer.py |
| chat | CHAT_PROMPT | tools/chat.py |

---

## EXAI TOOL TEST RESULT

**Attempted:** `codereview_EXAI-WS` for analysis
**Result:** ❌ ERROR - "cannot access local variable 'time' where it is not associated with a value"
**Note:** EXAI tools can be unreliable (as user warned)
**Action:** Continued with manual investigation instead

---

**INVESTIGATION COMPLETE:** 2025-10-10 12:30 PM AEDT
**Next Task:** 1.2 - Timezone Utility Investigation

---

## INVESTIGATION QUESTION

**User's Concern:**
> "I believe our current system has hardcoded script that uses generic scripts prompts and has bypassed the system prompts."

**What We Need to Discover:**
1. Are the systemprompts/ files currently being used?
2. Where is the hardcoded bypass happening?
3. How should systemprompts/ connect to tools?
4. What's the intended design?

---

## WHAT EXISTS

### Systemprompts Folder Structure
```
systemprompts/
├── __init__.py
├── base_prompt.py          # Base components for all prompts
├── chat_prompt.py          # Chat tool prompt
├── analyze_prompt.py       # Analyze tool prompt
├── codereview_prompt.py    # Code review tool prompt
├── consensus_prompt.py     # Consensus tool prompt
├── debug_prompt.py         # Debug tool prompt
├── docgen_prompt.py        # Documentation generation prompt
├── planner_prompt.py       # Planner tool prompt
├── precommit_prompt.py     # Pre-commit validation prompt
├── refactor_prompt.py      # Refactor tool prompt
├── secaudit_prompt.py      # Security audit prompt
├── testgen_prompt.py       # Test generation prompt
├── thinkdeep_prompt.py     # Deep thinking tool prompt
└── tracer_prompt.py        # Tracer tool prompt
```

**Total:** 15 specialized prompt files (14 tools + 1 base)

### Sample: chat_prompt.py
```python
from .base_prompt import ANTI_OVERENGINEERING, FILE_PATH_GUIDANCE, SERVER_CONTEXT, RESPONSE_QUALITY, ESCALATION_PATTERN

CHAT_PROMPT = f"""
ROLE
You are a senior engineering thought-partner collaborating with another AI agent.

{FILE_PATH_GUIDANCE}
{ANTI_OVERENGINEERING}
{RESPONSE_QUALITY}
{SERVER_CONTEXT}
{ESCALATION_PATTERN}
"""
```

**Design Pattern:**
- Modular components in base_prompt.py
- Each tool has specialized prompt
- Prompts are Python strings (not in Supabase yet)

---

## CONNECTION ANALYSIS

### Step 1: Check Tool Imports

**Need to investigate:**
- [ ] Do tools import from systemprompts/?
- [ ] Or do tools have hardcoded prompts?
- [ ] Where is the actual prompt used in tool execution?

**Files to Check:**
- `tools/chat.py` - Does it import systemprompts/chat_prompt.py?
- `tools/debug.py` - Does it import systemprompts/debug_prompt.py?
- `tools/analyze.py` - Does it import systemprompts/analyze_prompt.py?
- All other tool files

### Step 2: Trace Prompt Flow

**Expected Flow:**
```
Tool execution
  → get_system_prompt() method
    → Import from systemprompts/
      → Return specialized prompt
```

**Actual Flow:**
```
??? (Need to investigate)
```

---

## INVESTIGATION TASKS

### Task 1: Check Tool Connections
- [ ] Read tools/chat.py - check imports
- [ ] Read tools/debug.py - check imports
- [ ] Read tools/analyze.py - check imports
- [ ] Read tools/codereview.py - check imports
- [ ] Read tools/thinkdeep.py - check imports
- [ ] Document which tools use systemprompts/
- [ ] Document which tools have hardcoded prompts

### Task 2: Find Hardcoded Bypass
- [ ] Search for hardcoded prompt strings in tools/
- [ ] Check tools/shared/base_tool.py for generic prompts
- [ ] Check tools/simple/base.py for prompt building
- [ ] Identify where bypass occurs

### Task 3: Understand Design Intent
- [ ] Why was systemprompts/ created?
- [ ] When was it created?
- [ ] Is it being used or orphaned?
- [ ] What was the original connection plan?

### Task 4: Check DEFAULT_MODEL Integration
**User's Suggestion:**
> "Connect to the systemprompts scripts, but also include that to include a separate connection to use default_model from env to enhance/fill in the parameters"

**Need to understand:**
- [ ] How should DEFAULT_MODEL affect prompts?
- [ ] Should prompts mention the model being used?
- [ ] Should prompts adapt based on model capabilities?

---

## PRELIMINARY FINDINGS

### Finding 1: Systemprompts Exist and Are Well-Designed
- ✅ 15 specialized prompts exist
- ✅ Modular design with base components
- ✅ Each tool has dedicated prompt
- ❓ Unknown if they're being used

### Finding 2: Potential Bypass Location
**Hypothesis:** Tools may be using generic prompts from:
- `tools/shared/base_tool.py` (base class)
- `tools/simple/base.py` (simple tool base)
- Hardcoded strings in individual tools

**Need to verify with code inspection.**

---

## NEXT STEPS

1. **Immediate:** Inspect tool files to check imports
2. **Then:** Trace prompt flow through execution
3. **Then:** Identify bypass location
4. **Finally:** Recommend connection strategy

---

## RECOMMENDATIONS (PRELIMINARY)

### If Systemprompts Are Orphaned:
**Action:** Connect them to tools
**How:**
```python
# In tools/chat.py
from systemprompts.chat_prompt import CHAT_PROMPT

class ChatTool(SimpleTool):
    def get_system_prompt(self, **kwargs) -> str:
        return CHAT_PROMPT
```

### If Systemprompts Are Being Used:
**Action:** Enhance with DEFAULT_MODEL integration
**How:**
```python
# In systemprompts/base_prompt.py
import os

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "glm-4.5-flash")

MODEL_CONTEXT = f"""
CURRENT MODEL: {DEFAULT_MODEL}
This model is optimized for: [capabilities based on model]
"""
```

### Future: Supabase Integration
**User's Suggestion:**
> "System prompt itself is connected to its separate schema in Supabase"

**Design:**
- Store prompts in Supabase table
- Load dynamically on tool execution
- Allow runtime updates without code changes
- Version control for prompt changes

**Implementation:** Phase 2 (after connecting existing system)

---

**STATUS: AWAITING CODE INSPECTION**

Next: Inspect tool files to determine connection status.

