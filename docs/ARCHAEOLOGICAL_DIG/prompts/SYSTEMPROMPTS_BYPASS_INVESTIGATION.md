# PROMPTS INVESTIGATION - FINDINGS
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Category:** System Prompts Architecture  
**Status:** 🔍 Investigation In Progress

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

