# EXAI-MCP ROOT CAUSE ANALYSIS & IMPLEMENTATION PLAN
**Date:** 2025-10-10 (10th October 2025)  
**Timezone:** AEDT (Melbourne, Australia)  
**Analyst:** Augment Agent (Claude Sonnet 4.5)  
**Scope:** 5 Critical Issues Identified from External AI Review + Terminal Output + Log Analysis

---

## EXECUTIVE SUMMARY

This document provides **root cause analysis** and **detailed implementation plans** for 5 critical issues affecting the EXAI-MCP system. Each issue includes:

1. **Root Cause Location** - Exact files and line numbers where the issue originates
2. **Script Interconnection Analysis** - How scripts call each other and where changes propagate
3. **Implementation Strategy** - Whether to modify existing scripts or create new ones
4. **Downstream Impact** - What other components will be affected
5. **Testing Requirements** - How to validate the fix

**Key Principle:** Do NOT bloat existing scripts. Create new specialized scripts when adding significant functionality. Maintain clean separation of concerns.

---

## ISSUE 1: STATIC SYSTEM PROMPTS CAUSING WEAK RESPONSES

### Problem Statement
System prompts are hardcoded as "senior engineering thought-partner" regardless of user context. This causes:
- Generic, broad responses that don't match user intent
- Missed opportunities for specialized expertise
- Poor performance on domain-specific queries

### Root Cause Location

**File:** `tools/chat.py`  
**Lines:** ~50-80 (get_system_prompt method)

```python
def get_system_prompt(self) -> str:
    return """
    ROLE
    You are a senior engineering thought-partner collaborating with another AI agent.
    """
```

**Problem:** This static prompt is used for ALL chat requests, regardless of:
- User's actual question (code review vs brainstorming vs debugging)
- Domain (frontend vs backend vs infrastructure)
- Complexity level (simple question vs complex analysis)

### Script Interconnection Analysis

**Call Chain:**
```
User → Augment IDE
  → scripts/run_ws_shim.py (MCP entry)
    → src/daemon/ws_server.py (WebSocket handler)
      → src/server/handlers/request_handler.py (SERVER_HANDLE_CALL_TOOL)
        → tools/chat.py (ChatTool.execute)
          → tools/chat.py (get_system_prompt) ← STATIC PROMPT HERE
            → tools/simple/base.py (build_standard_prompt)
              → src/providers/glm_chat.py OR src/providers/kimi.py
                → External AI API
```

**Key Insight:** The system prompt is generated ONCE per tool call, BEFORE analyzing user intent.

### Implementation Strategy

**Option A: Modify Existing (NOT RECOMMENDED - Would Bloat chat.py)**
- Add intent analysis logic to chat.py
- Add prompt template library to chat.py
- Add context extraction to chat.py
- **Result:** chat.py becomes 500+ lines, hard to maintain

**Option B: Create New Specialized Script (RECOMMENDED)**

**New File:** `src/utils/prompt_engineering.py`

**Responsibilities:**
1. Analyze user prompt to detect intent (code_review, debugging, brainstorming, etc.)
2. Extract domain context (language, framework, complexity)
3. Generate dynamic system prompt based on intent + domain
4. Provide prompt templates for different scenarios

**Modified Files:**
- `tools/chat.py` - Call prompt_engineering.py instead of hardcoded prompt
- `tools/simple/base.py` - Pass user prompt to get_system_prompt for analysis

### Detailed Implementation Plan

#### Step 1: Create Prompt Engineering Module

**File:** `src/utils/prompt_engineering.py` (NEW)

```python
"""
Dynamic prompt engineering for context-aware system instructions.
Analyzes user intent and generates specialized system prompts.
"""

from typing import Dict, Optional
import re

class PromptEngineer:
    """Generates dynamic system prompts based on user intent and context."""
    
    INTENT_PATTERNS = {
        "code_review": [
            r"review\s+(?:this|the|my)\s+code",
            r"what(?:'s| is)\s+wrong\s+with",
            r"check\s+(?:this|the)\s+code",
            r"code\s+quality",
        ],
        "debugging": [
            r"debug",
            r"why\s+(?:is|does|doesn't)",
            r"error|exception|bug",
            r"not\s+working",
        ],
        "architecture": [
            r"architect",
            r"design\s+pattern",
            r"how\s+should\s+I\s+structure",
            r"best\s+way\s+to\s+organize",
        ],
        "explanation": [
            r"explain|what\s+is|how\s+does",
            r"understand",
            r"learn\s+about",
        ],
        "brainstorming": [
            r"ideas?\s+for",
            r"suggest|recommend",
            r"what\s+are\s+(?:some|the)\s+options",
        ],
    }
    
    DOMAIN_PATTERNS = {
        "frontend": ["react", "vue", "angular", "css", "html", "ui", "ux"],
        "backend": ["api", "server", "database", "sql", "rest", "graphql"],
        "devops": ["docker", "kubernetes", "ci/cd", "deploy", "infrastructure"],
        "security": ["auth", "security", "vulnerability", "encryption"],
    }
    
    def analyze_intent(self, user_prompt: str) -> str:
        """Detect primary intent from user prompt."""
        prompt_lower = user_prompt.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    return intent
        
        return "general"
    
    def detect_domain(self, user_prompt: str) -> Optional[str]:
        """Detect technical domain from user prompt."""
        prompt_lower = user_prompt.lower()
        
        for domain, keywords in self.DOMAIN_PATTERNS.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return domain
        
        return None
    
    def generate_system_prompt(
        self,
        user_prompt: str,
        base_role: str = "engineering thought-partner",
        include_websearch_instructions: bool = False
    ) -> str:
        """Generate dynamic system prompt based on user intent and domain."""
        
        intent = self.analyze_intent(user_prompt)
        domain = self.detect_domain(user_prompt)
        
        # Build specialized role description
        role_parts = [f"You are a {base_role}"]
        
        if intent == "code_review":
            role_parts.append("specializing in code quality analysis and best practices")
        elif intent == "debugging":
            role_parts.append("with deep expertise in root cause analysis and systematic debugging")
        elif intent == "architecture":
            role_parts.append("with extensive experience in software architecture and design patterns")
        elif intent == "explanation":
            role_parts.append("skilled at clear, pedagogical explanations of technical concepts")
        elif intent == "brainstorming":
            role_parts.append("experienced in creative problem-solving and solution design")
        
        if domain:
            role_parts.append(f"with specialized knowledge in {domain} development")
        
        role_description = " ".join(role_parts) + "."
        
        # Build context-specific instructions
        instructions = []
        
        if intent == "code_review":
            instructions.extend([
                "Focus on:",
                "- Code quality, readability, and maintainability",
                "- Potential bugs, edge cases, and error handling",
                "- Performance implications and optimization opportunities",
                "- Security vulnerabilities and best practices",
                "- Adherence to language/framework conventions",
            ])
        elif intent == "debugging":
            instructions.extend([
                "Approach systematically:",
                "1. Understand the expected vs actual behavior",
                "2. Identify potential root causes",
                "3. Suggest specific debugging steps",
                "4. Provide concrete fixes with explanations",
            ])
        elif intent == "architecture":
            instructions.extend([
                "Consider:",
                "- Scalability and performance characteristics",
                "- Maintainability and code organization",
                "- Trade-offs between different approaches",
                "- Industry best practices and patterns",
                "- Future extensibility requirements",
            ])
        
        # Combine into final prompt
        prompt_parts = [
            "ROLE",
            role_description,
            "",
        ]
        
        if instructions:
            prompt_parts.extend(instructions)
            prompt_parts.append("")
        
        # Add standard collaboration guidelines
        prompt_parts.extend([
            "COLLABORATION APPROACH",
            "1. Engage deeply - extend, refine alternatives when well-justified",
            "2. Examine edge cases, failure modes, unintended consequences",
            "3. Present balanced perspectives with trade-offs",
            "4. Challenge assumptions constructively",
            "5. Provide concrete examples and actionable next steps",
            "",
            "RESPONSE QUALITY",
            "• Be concise and technically precise",
            "• Provide concrete examples and actionable next steps",
            "• Reference specific files, line numbers, and code when applicable",
            "• Balance depth with clarity - avoid unnecessary verbosity",
        ])
        
        return "\n".join(prompt_parts)


# Singleton instance
_prompt_engineer = None

def get_prompt_engineer() -> PromptEngineer:
    """Get or create singleton PromptEngineer instance."""
    global _prompt_engineer
    if _prompt_engineer is None:
        _prompt_engineer = PromptEngineer()
    return _prompt_engineer
```

#### Step 2: Modify Chat Tool

**File:** `tools/chat.py`  
**Modification:** Replace static get_system_prompt with dynamic version

```python
from src.utils.prompt_engineering import get_prompt_engineer

class ChatTool(SimpleTool):
    """Chat tool with dynamic system prompts."""
    
    def get_system_prompt(self, user_prompt: str = "", **kwargs) -> str:
        """Generate dynamic system prompt based on user intent."""
        
        # Get prompt engineer
        engineer = get_prompt_engineer()
        
        # Generate context-aware prompt
        return engineer.generate_system_prompt(
            user_prompt=user_prompt,
            base_role="senior engineering thought-partner",
            include_websearch_instructions=kwargs.get("use_websearch", False)
        )
```

#### Step 3: Update Base Tool Interface

**File:** `tools/shared/base_tool_core.py`  
**Modification:** Update get_system_prompt signature to accept user_prompt

```python
from abc import ABC, abstractmethod

class BaseToolCore(ABC):
    """Core base class for all tools."""
    
    @abstractmethod
    def get_system_prompt(self, user_prompt: str = "", **kwargs) -> str:
        """
        Generate system prompt for this tool.
        
        Args:
            user_prompt: The user's actual prompt (for context-aware generation)
            **kwargs: Additional context (files, model, etc.)
        
        Returns:
            System prompt string
        """
        pass
```

#### Step 4: Update Prompt Building Logic

**File:** `tools/simple/base.py`  
**Lines:** ~966-1017 (build_standard_prompt method)

```python
def build_standard_prompt(self, arguments: dict) -> str:
    """Build complete prompt with dynamic system instructions."""
    
    # Extract user prompt for intent analysis
    user_prompt = arguments.get("prompt", "")
    
    # Get dynamic system prompt (passes user_prompt for analysis)
    system_prompt = self.get_system_prompt(
        user_prompt=user_prompt,
        use_websearch=arguments.get("use_websearch", False),
        files=arguments.get("files", []),
        model=arguments.get("model", "auto")
    )
    
    # ... rest of prompt building logic
```

### Downstream Impact Analysis

**Files That Will Change:**
1. `src/utils/prompt_engineering.py` - NEW (no impact)
2. `tools/chat.py` - Modified (get_system_prompt method)
3. `tools/shared/base_tool_core.py` - Modified (method signature)
4. `tools/simple/base.py` - Modified (pass user_prompt to get_system_prompt)

**Files That Need Updates (All Tools):**
- `tools/debug.py` - Update get_system_prompt signature
- `tools/analyze.py` - Update get_system_prompt signature
- `tools/codereview.py` - Update get_system_prompt signature
- `tools/thinkdeep.py` - Update get_system_prompt signature
- All other tool files that override get_system_prompt

**Breaking Changes:** None (default parameter makes it backward compatible)

### Testing Requirements

**Test 1: Intent Detection**
```python
# Test file: tests/test_prompt_engineering.py
from src.utils.prompt_engineering import get_prompt_engineer

def test_code_review_intent():
    engineer = get_prompt_engineer()
    prompt = "Please review this code for bugs"
    intent = engineer.analyze_intent(prompt)
    assert intent == "code_review"

def test_debugging_intent():
    engineer = get_prompt_engineer()
    prompt = "Why is my function not working?"
    intent = engineer.analyze_intent(prompt)
    assert intent == "debugging"
```

**Test 2: Dynamic Prompt Generation**
```python
def test_dynamic_prompt_code_review():
    engineer = get_prompt_engineer()
    prompt = "Review this React component for performance issues"
    
    system_prompt = engineer.generate_system_prompt(prompt)
    
    # Should mention code review
    assert "code quality" in system_prompt.lower()
    # Should mention frontend domain
    assert "frontend" in system_prompt.lower()
```

**Test 3: End-to-End Chat Tool**
```bash
# Manual test via chat tool
# Prompt 1: "Review this code: def foo(): pass"
# Expected: System prompt should mention code review, quality analysis

# Prompt 2: "Why is my API returning 500 errors?"
# Expected: System prompt should mention debugging, root cause analysis

# Prompt 3: "Explain how React hooks work"
# Expected: System prompt should mention explanation, pedagogical approach
```

### Implementation Checklist

- [ ] Create `src/utils/prompt_engineering.py` with PromptEngineer class
- [ ] Add intent detection patterns (code_review, debugging, architecture, etc.)
- [ ] Add domain detection patterns (frontend, backend, devops, security)
- [ ] Implement generate_system_prompt method
- [ ] Update `tools/shared/base_tool_core.py` - add user_prompt parameter to get_system_prompt
- [ ] Update `tools/simple/base.py` - pass user_prompt to get_system_prompt
- [ ] Update `tools/chat.py` - use PromptEngineer instead of static prompt
- [ ] Update all other tools to match new signature (backward compatible)
- [ ] Write unit tests for intent detection
- [ ] Write unit tests for domain detection
- [ ] Write unit tests for prompt generation
- [ ] Write integration tests for chat tool
- [ ] Manual testing with various prompt types
- [ ] Document new prompt engineering system in docs/

**Estimated Effort:** 6-8 hours  
**Risk Level:** Medium (touches many files, but backward compatible)  
**Priority:** HIGH (directly impacts response quality)

---

## ISSUE 2: MODEL TRAINING DATE AWARENESS

### Problem Statement
Models default to their training cutoff dates instead of current date/time. When asked "what's today's date", they respond with their training date (e.g., "April 2024" for GLM-4.5-flash).

### Root Cause Location

**File:** `tools/simple/base.py`  
**Lines:** ~966-1017 (build_standard_prompt method)

**Current Code:**
```python
def build_standard_prompt(self, arguments: dict) -> str:
    system_prompt = self.get_system_prompt()
    user_content = arguments.get("prompt", "")
    
    # NO DATE/TIME INJECTION HERE
    
    return f"{system_prompt}\n\n=== USER REQUEST ===\n{user_content}\n=== END REQUEST ==="
```

**Problem:** Current date/time is NEVER injected into the prompt or system context.

### Script Interconnection Analysis

**Call Chain:**
```
User asks "What's today's date?"
  → tools/chat.py (execute)
    → tools/simple/base.py (build_standard_prompt) ← SHOULD INJECT DATE HERE
      → src/providers/glm_chat.py (build_payload)
        → GLM API
          → Model responds with training date (WRONG!)
```

**Key Insight:** The model has NO WAY to know the current date unless we explicitly tell it.

### Implementation Strategy

**Option A: Inject in System Prompt (RECOMMENDED)**
- Add current date/time to system prompt
- Models see it as part of their instructions
- Works for all providers (GLM, Kimi, etc.)

**Option B: Add as Metadata Field**
- Pass date/time in request metadata
- Requires provider-specific handling
- More complex, less reliable

**Decision:** Use Option A - inject in system prompt

### Detailed Implementation Plan

#### Step 1: Create Timestamp Utility

**File:** `src/utils/timestamp_utils.py` (NEW)

```python
"""
Timestamp utilities for EXAI-MCP system.
Provides current date/time in multiple formats and timezones.
"""

from datetime import datetime, timezone
import pytz

# Melbourne timezone
MELBOURNE_TZ = pytz.timezone("Australia/Melbourne")

def get_current_timestamps() -> dict:
    """
    Get current timestamps in multiple formats.
    
    Returns:
        dict with keys:
            - unix: Unix epoch timestamp (float)
            - utc_iso: UTC ISO8601 string
            - aedt_human: Melbourne human-readable string
            - date_only: YYYY-MM-DD format
    """
    now_utc = datetime.now(timezone.utc)
    now_melbourne = now_utc.astimezone(MELBOURNE_TZ)
    
    return {
        "unix": now_utc.timestamp(),
        "utc_iso": now_utc.isoformat(),
        "aedt_human": now_melbourne.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "date_only": now_melbourne.strftime("%Y-%m-%d"),
    }

def format_date_for_prompt() -> str:
    """
    Format current date/time for injection into AI prompts.
    
    Returns:
        Human-readable string like:
        "Current date: 2025-10-10 (10th October 2025, Thursday)
         Current time: 14:30:25 AEDT (Melbourne, Australia)"
    """
    now_melbourne = datetime.now(timezone.utc).astimezone(MELBOURNE_TZ)
    
    # Get day suffix (1st, 2nd, 3rd, 4th, etc.)
    day = now_melbourne.day
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    
    date_str = now_melbourne.strftime(f"%Y-%m-%d ({day}{suffix} %B %Y, %A)")
    time_str = now_melbourne.strftime("%H:%M:%S %Z (%Z timezone, Melbourne, Australia)")
    
    return f"Current date: {date_str}\nCurrent time: {time_str}"
```

#### Step 2: Inject Date into System Prompts

**File:** `tools/simple/base.py`  
**Modification:** Add date/time to all system prompts

```python
from src.utils.timestamp_utils import format_date_for_prompt

def build_standard_prompt(self, arguments: dict) -> str:
    """Build complete prompt with current date/time awareness."""
    
    # Get base system prompt
    user_prompt = arguments.get("prompt", "")
    system_prompt = self.get_system_prompt(user_prompt=user_prompt, **arguments)
    
    # Inject current date/time
    date_context = format_date_for_prompt()
    enhanced_system_prompt = f"{system_prompt}\n\n=== CURRENT DATE/TIME ===\n{date_context}\n=== END DATE/TIME ===\n"
    
    # Build user content
    user_content = arguments.get("prompt", "")
    
    # Combine
    return f"{enhanced_system_prompt}\n\n=== USER REQUEST ===\n{user_content}\n=== END REQUEST ==="
```

#### Step 3: Add Date to Request Metadata

**File:** `src/server/handlers/request_handler.py`  
**Lines:** ~73-109 (SERVER_HANDLE_CALL_TOOL)

```python
from src.utils.timestamp_utils import get_current_timestamps

async def SERVER_HANDLE_CALL_TOOL(name: str, arguments: dict, req_id=None):
    """Main entry point for tool execution with timestamp injection."""
    
    # Generate request_id if not provided
    if req_id is None:
        req_id = str(uuid.uuid4())
    
    # Inject timestamp metadata
    timestamps = get_current_timestamps()
    if "_request_metadata" not in arguments:
        arguments["_request_metadata"] = {}
    
    arguments["_request_metadata"].update({
        "request_id": req_id,
        "timestamp_unix": timestamps["unix"],
        "timestamp_utc": timestamps["utc_iso"],
        "timestamp_aedt": timestamps["aedt_human"],
        "current_date": timestamps["date_only"],
    })
    
    # Also add as top-level for easy access
    arguments["_today"] = timestamps["date_only"]
    arguments["_current_time"] = timestamps["aedt_human"]
    
    # Execute tool
    tool_obj = get_tool(name)
    result = await execute_tool_with_context(tool_obj, arguments, req_id)
    
    return result
```

### Downstream Impact Analysis

**Files That Will Change:**
1. `src/utils/timestamp_utils.py` - NEW (no impact)
2. `tools/simple/base.py` - Modified (inject date in prompts)
3. `src/server/handlers/request_handler.py` - Modified (add metadata)

**Files That Benefit:**
- ALL tools automatically get current date awareness
- ALL logs will have proper timestamps
- ALL provider calls will include date context

**Breaking Changes:** None (purely additive)

### Testing Requirements

**Test 1: Timestamp Utility**
```python
# Test file: tests/test_timestamp_utils.py
from src.utils.timestamp_utils import get_current_timestamps, format_date_for_prompt

def test_timestamp_formats():
    ts = get_current_timestamps()
    assert "unix" in ts
    assert "utc_iso" in ts
    assert "aedt_human" in ts
    assert "date_only" in ts
    assert ts["date_only"] == "2025-10-10"  # Today

def test_prompt_formatting():
    formatted = format_date_for_prompt()
    assert "2025-10-10" in formatted
    assert "AEDT" in formatted
    assert "Melbourne" in formatted
```

**Test 2: Date Injection in Prompts**
```bash
# Manual test via chat tool
# Prompt: "What's today's date?"
# Expected: Model responds "2025-10-10" or "10th October 2025"
# NOT: "April 2024" (training date)

# Prompt: "What day of the week is it?"
# Expected: Model responds with correct day (e.g., "Thursday")
```

**Test 3: Metadata Injection**
```python
# Test file: tests/test_request_handler.py
async def test_timestamp_metadata_injection():
    arguments = {"prompt": "test"}
    await SERVER_HANDLE_CALL_TOOL("chat", arguments)
    
    assert "_request_metadata" in arguments
    assert "timestamp_unix" in arguments["_request_metadata"]
    assert "_today" in arguments
    assert arguments["_today"] == "2025-10-10"
```

### Implementation Checklist

- [ ] Create `src/utils/timestamp_utils.py` with timestamp functions
- [ ] Add pytz dependency to requirements.txt (if not already present)
- [ ] Update `tools/simple/base.py` - inject date in build_standard_prompt
- [ ] Update `src/server/handlers/request_handler.py` - add metadata
- [ ] Write unit tests for timestamp utilities
- [ ] Write integration tests for date injection
- [ ] Manual testing: "What's today's date?"
- [ ] Manual testing: "What day of the week is it?"
- [ ] Verify logs show correct timestamps
- [ ] Document timestamp injection in docs/

**Estimated Effort:** 3-4 hours  
**Risk Level:** LOW (purely additive, no breaking changes)  
**Priority:** HIGH (critical for model accuracy)

---

*[Continued in next file due to 300-line limit]*

