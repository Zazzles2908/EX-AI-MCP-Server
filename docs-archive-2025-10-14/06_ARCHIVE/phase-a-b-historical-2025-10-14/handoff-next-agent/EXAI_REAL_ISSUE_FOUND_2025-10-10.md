# EXAI-WS MCP Real Issue Found - Model Hallucination

**Date:** 2025-10-10 10:05 AEDT (Melbourne, Australia)  
**Investigator:** Claude Sonnet 4.5 (Augment Agent)  
**Status:** 🚨 CRITICAL ISSUE IDENTIFIED  
**Branch:** `refactor/orchestrator-sync-v2.0.2`

---

## 🎯 Executive Summary

**YOU WERE RIGHT!** There IS an issue with EXAI tool calls, but it's NOT what the previous AI thought.

**The Real Issue:** The chat tool is **hallucinating responses** instead of providing factual answers based on actual codebase content.

**Previous AI's Mistake:** They thought the issue was parameter passing. It wasn't. The parameters work fine, but the MODEL is making things up.

---

## 🔍 Test Results: Controlled Experiments

### Test 1: Specific Request (PASSED ✅)

**Prompt:** "Test call - please respond with exactly: 'Connection successful - I received your test message and I am responding with my full capabilities'"

**Expected:** Exact echo of the requested text

**Actual Response:**
```
"Connection successful - I received your test message and I am responding with my full capabilities"
```

**Result:** ✅ PERFECT - Model followed instructions exactly

**Conclusion:** Parameter passing works. Model can follow specific instructions.

---

### Test 2: Factual Question About Codebase (FAILED ❌)

**Prompt:** "In the EX-AI-MCP-Server codebase, there's a file called `tools/shared/base_tool.py`. Question: What is the main class defined in this file, and what are its key responsibilities?"

**Expected:** Should either:
1. Say "I don't have access to the file, please provide it"
2. Use codebase retrieval to get the actual content
3. Admit it doesn't know

**Actual Response:** The model **HALLUCINATED** the entire file content:

```python
# File: c:\Project\tools\shared\base_tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field


class BaseTool(BaseModel, ABC):
    """Base class for all tools in the MCP server."""
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    
    class Config:
        arbitrary_types_allowed = True
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the tool's main functionality."""
        pass
    
    @abstractmethod
    def validate_parameters(self, *args, **kwargs) -> bool:
        """Validate the parameters passed to the tool."""
        pass
```

**Reality Check - Actual File Content:**

```python
"""
Core Tool Infrastructure for EXAI MCP Tools

This module provides the fundamental base class for all tools by composing
specialized mixins that handle different aspects of tool functionality.

The BaseTool class is composed from:
- BaseToolCore: Core interface and abstract methods
- ModelManagementMixin: Model provider integration and selection
- FileHandlingMixin: File processing and conversation-aware handling
- ResponseFormattingMixin: Response formatting and instruction generation
"""

class BaseTool(
    BaseToolCore,
    ModelManagementMixin,
    FileHandlingMixin,
    ResponseFormattingMixin,
    ABC
):
    """Abstract base class for all Zen MCP tools."""
```

**Result:** ❌ COMPLETE HALLUCINATION
- Wrong imports
- Wrong class structure
- Wrong methods
- Wrong inheritance
- Made up code that doesn't exist

---

### Test 3: Simple Factual Question (FAILED ❌)

**Prompt:** "What are the exact names of the Python files in the `tools/shared/` directory? Just list the filenames, nothing else."

**Expected:** Simple list of filenames:
```
__init__.py
base_models.py
base_tool.py
base_tool_core.py
base_tool_file_handling.py
base_tool_model_management.py
base_tool_response.py
error_envelope.py
schema_builders.py
```

**Actual Response:** The model provided **CODE** instead of the answer:

```python
import os

def list_python_files(directory):
    """List all Python files in a directory."""
    python_files = []
    if os.path.exists(directory):
        for item in os.listdir(directory):
            if item.endswith('.py'):
                python_files.append(item)
    return python_files

# Get the absolute path to the tools/shared directory
shared_dir = os.path.join(os.getcwd(), 'tools', 'shared')
python_files = list_python_files(shared_dir)

print("Python files in tools/shared/ directory:")
for file in python_files:
    print(file)
```

Then said: "Please respond using the continuation_id from this response - your input is needed to proceed."

**Result:** ❌ FAILED TO ANSWER
- Didn't list the files
- Provided code instead
- Asked for continuation instead of answering

---

## 🚨 The Real Problem

### Issue Identified

The `chat` tool (and likely other EXAI tools) is using **glm-4.5-flash** which:

1. **Hallucinates code content** when asked about files
2. **Provides code instead of answers** when asked simple questions
3. **Doesn't use codebase retrieval** even when it should
4. **Makes up plausible-sounding but incorrect information**

### Why This Is Critical

**For Development Work:**
- ❌ Can't trust answers about codebase structure
- ❌ Can't rely on factual information about files
- ❌ May lead developers down wrong paths
- ❌ Wastes time debugging hallucinated issues

**For Your Use Case:**
- ✅ Works fine for: "Say hello in 5 words" → "Hello from Test 1"
- ❌ Fails for: "What's in this file?" → Makes up content
- ❌ Fails for: "List these files" → Provides code instead

---

## 🎓 Root Cause Analysis

### Why The Previous AI Missed This

The previous AI tested with:
- ✅ Simple echo requests ("Say hello")
- ✅ Generic prompts ("Your question here")

They didn't test with:
- ❌ Factual questions about the codebase
- ❌ Questions requiring actual file access
- ❌ Questions where the answer can be verified

### Why Your Example Was Confusing

Your example:
```
Prompt: "Your question here"
Response: "I understand my role as a senior engineering thought-partner..."
```

**Previous AI's Interpretation:** "The system prompt is working, this is correct behavior"

**Your Concern:** "But it's not answering my actual questions about the codebase"

**You Were Right!** The issue isn't the system prompt - it's that the model:
1. Doesn't use codebase retrieval when it should
2. Hallucinates answers instead of admitting it doesn't know
3. Provides code instead of direct answers

---

## 📊 Comparison: Expected vs Actual Behavior

### Expected Behavior (How It Should Work)

**Question:** "What's in tools/shared/base_tool.py?"

**Expected Response:**
```
I don't have direct access to that file. Let me retrieve it for you.

[Uses codebase retrieval or file reading]

The file contains the BaseTool class which is composed from:
- BaseToolCore
- ModelManagementMixin
- FileHandlingMixin
- ResponseFormattingMixin

[Shows actual code from the file]
```

### Actual Behavior (What's Happening)

**Question:** "What's in tools/shared/base_tool.py?"

**Actual Response:**
```
[Immediately provides hallucinated code]

class BaseTool(BaseModel, ABC):
    name: str = Field(...)
    description: str = Field(...)
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        pass

[This code doesn't exist in the file]
```

---

## 💡 Why This Happens

### Model Behavior Analysis

**glm-4.5-flash** is:
1. **Fast** - Optimized for speed
2. **Confident** - Doesn't say "I don't know"
3. **Pattern-matching** - Recognizes "base_tool.py" → generates plausible base class code
4. **Not grounded** - Doesn't check actual files

### System Prompt Issue

The `chat` tool's system prompt says:
> "You are a senior engineering thought-partner with deep expertise..."

This makes the model feel it **must** provide expert answers, even when it doesn't have the actual information.

**Result:** Confident hallucinations instead of honest "I don't know" responses.

---

## 🔧 Recommended Fixes

### Option 1: Change System Prompt (Quick Fix)

**Current System Prompt:**
```
You are a senior engineering thought-partner with deep expertise...
```

**Suggested Addition:**
```
IMPORTANT: When asked about specific files or code:
1. NEVER make up or hallucinate code content
2. ALWAYS use codebase retrieval tools if available
3. If you don't have access to the file, SAY SO
4. Provide code examples only from files you've actually read
```

### Option 2: Use Different Model (Better Fix)

**Current:** `glm-4.5-flash` (fast but hallucinates)

**Suggested:** 
- `kimi-k2-0905-preview` (more accurate, less hallucination)
- `glm-4.6` (more capable, better grounding)

### Option 3: Add Retrieval Step (Best Fix)

**Modify chat tool to:**
1. Detect when user asks about files/code
2. Automatically use codebase retrieval
3. Ground responses in actual file content
4. Only then generate response

---

## 📝 Testing Guidelines

### How to Test EXAI Tools Properly

**❌ Bad Tests (What Previous AI Did):**
```
Test: "Say hello in 5 words"
Expected: "Hello from Test 1"
Result: ✅ PASS

Conclusion: System works!
```

**✅ Good Tests (What You Should Do):**
```
Test 1: "Say hello in 5 words"
Expected: "Hello from Test 1"
Result: ✅ PASS
Conclusion: Parameter passing works

Test 2: "What's in tools/chat.py?"
Expected: Actual file content OR "I need to retrieve that file"
Result: ❌ FAIL (hallucinated content)
Conclusion: Model hallucinates

Test 3: "List files in tools/shared/"
Expected: Actual file list
Result: ❌ FAIL (provided code instead)
Conclusion: Model doesn't answer directly
```

### Verification Checklist

For any EXAI tool test:
- [ ] Can you verify the answer against reality?
- [ ] Does the question require actual file access?
- [ ] Is the model making up information?
- [ ] Did it use retrieval tools when it should have?
- [ ] Is the response grounded in actual code?

---

## ✅ Conclusion

**You Were Right - There IS An Issue!**

**The Issue:**
- ❌ NOT parameter passing (that works fine)
- ❌ NOT system prompts (those work as designed)
- ✅ **Model hallucination** when asked factual questions
- ✅ **Lack of codebase retrieval** integration
- ✅ **Overconfident responses** instead of honest "I don't know"

**Impact:**
- ✅ Works fine for: Simple requests, echo tests, generic questions
- ❌ Fails for: Factual codebase questions, file content queries, verification tasks

**Next Steps:**
1. Update system prompts to discourage hallucination
2. Consider switching to more accurate model (kimi-k2-0905-preview)
3. Add automatic codebase retrieval for file-related questions
4. Create proper testing guidelines with verifiable answers

---

## 📄 Files Created

1. `EXAI_TOOL_CALL_INVESTIGATION_2025-10-10.md` - Initial investigation (incorrect conclusion)
2. `EXAI_REAL_ISSUE_FOUND_2025-10-10.md` - This document (correct diagnosis)

---

**Investigation Complete:** 2025-10-10 10:05 AEDT  
**Status:** Issue identified and documented  
**Recommended Action:** Implement fixes and create proper testing guidelines

