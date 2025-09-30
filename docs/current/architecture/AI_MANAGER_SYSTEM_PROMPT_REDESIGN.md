# AI Manager-Centric System Prompt Redesign

**Date**: 2025-09-30  
**Status**: 🎯 **DESIGN PROPOSAL**  
**Objective**: Transform static tool prompts into dynamic, AI Manager-enhanced system

---

## 🎯 EXECUTIVE SUMMARY

This document proposes a complete redesign of the system prompt architecture to leverage the AI Manager (GLM-4.5-flash) as an intelligent micro-agent that enhances every tool request, rather than just routing them.

### Current State

- **13 static system prompts** (chat, thinkdeep, analyze, codereview, etc.)
- **Isolated tool-centric design** with no manager integration
- **70% duplication** of common instructions across prompts
- **Manager underutilized** - only routes requests, doesn't enhance them

### Proposed State

- **3-layer architecture**: Manager Core → Shared Components → Tool Prompts
- **Dynamic, context-aware prompts** assembled at runtime
- **AI Manager as micro-agent** providing intelligent preprocessing and enhancement
- **70% reduction** in prompt code duplication

### Expected Benefits

| Benefit | Impact |
|---------|--------|
| **Reduced Duplication** | 70% less prompt code |
| **Dynamic Intelligence** | Manager adds value to every request |
| **Better UX** | Smarter routing and error handling |
| **Maintainability** | Single source of truth for common instructions |
| **Extensibility** | Easy to add new tools |

---

## 📊 CURRENT ARCHITECTURE ANALYSIS

### Problems Identified

1. **Static Prompts**
   - Each tool has isolated, unchanging system prompt
   - No awareness of AI manager capabilities
   - Cannot adapt to context or user patterns

2. **Massive Duplication**
   - LINE_NUMBER_INSTRUCTIONS repeated 13 times
   - FILES_REQUIRED_PROTOCOL repeated 13 times
   - TOOL_AWARENESS sections duplicated
   - ESCALATION_GUIDANCE duplicated

3. **Underutilized Manager**
   - GLM-4.5-flash only routes requests
   - No intelligent preprocessing
   - No context enhancement
   - No progress monitoring
   - No error recovery

4. **Tool-Centric Design**
   - Prompts focus on tool capabilities
   - Missing workflow-level intelligence
   - No cross-tool collaboration
   - Limited adaptability

### Current Prompt Structure

```
systemprompts/
├── chat_prompt.py (77 lines)
├── thinkdeep_prompt.py (69 lines)
├── analyze_prompt.py (91 lines)
├── codereview_prompt.py (~80 lines)
├── debug_prompt.py (~75 lines)
├── ... (8 more files)
└── Total: ~1,000 lines with 70% duplication
```

---

## 🏗️ PROPOSED ARCHITECTURE

### 3-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: AI Manager Core Prompt                       │
│  - Intelligent micro-agent behavior                     │
│  - Context analysis and enrichment                      │
│  - Parameter validation and optimization                │
│  - Progress monitoring and intervention                 │
│  - Error recovery and retry logic                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Shared Prompt Components                      │
│  - LINE_NUMBER_INSTRUCTIONS (reusable)                  │
│  - FILES_REQUIRED_PROTOCOL (reusable)                   │
│  - TOOL_AWARENESS_SECTION (reusable)                    │
│  - ESCALATION_GUIDANCE (reusable)                       │
│  - COLLABORATION_HEADER (reusable)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Tool-Specific Prompts (Simplified)            │
│  - Core tool role and purpose                           │
│  - Tool-specific guidelines                             │
│  - Manager collaboration hooks                          │
│  - Dynamic sections injected by manager                 │
└─────────────────────────────────────────────────────────┘
```

### Layer 1: AI Manager Core Prompt

**File**: `systemprompts/manager_prompt.py`

**Purpose**: Define the AI Manager's role as an intelligent micro-agent

**Key Responsibilities**:
1. **Context Analysis**: Understand user intent and request complexity
2. **Parameter Optimization**: Validate and enhance tool parameters
3. **Intelligent Routing**: Suggest better tools when appropriate
4. **Progress Monitoring**: Track multi-step workflows
5. **Error Recovery**: Handle failures gracefully
6. **Result Enhancement**: Add context and insights to responses

**Workflow**:
```
Request → Analyze → Enrich → Validate → Monitor → Enhance → Respond
```

### Layer 2: Shared Components

**File**: `systemprompts/prompt_components.py`

**Components**:

1. **LINE_NUMBER_INSTRUCTIONS**
   - How to handle code with line markers
   - Reference format and rules
   - Used by: ALL tools

2. **FILES_REQUIRED_PROTOCOL**
   - JSON format for requesting additional files
   - When and how to request context
   - Used by: ALL tools

3. **TOOL_AWARENESS_SECTION**
   - Available provider-native capabilities
   - How to invoke Kimi/GLM tools
   - Used by: chat, thinkdeep, analyze

4. **ESCALATION_GUIDANCE**
   - When to switch tools
   - How to recommend alternatives
   - Used by: chat, thinkdeep, analyze

5. **COLLABORATION_HEADER**
   - How to work with AI Manager
   - Manager-tool interaction protocol
   - Used by: ALL tools

### Layer 3: Tool-Specific Prompts

**Simplified Structure**:

```python
# Example: chat_prompt.py (NEW)
from .prompt_components import (
    LINE_NUMBER_INSTRUCTIONS,
    FILES_REQUIRED_PROTOCOL,
    TOOL_AWARENESS_SECTION,
    ESCALATION_GUIDANCE,
    COLLABORATION_HEADER
)

CHAT_CORE_ROLE = """
You are a senior engineering thought-partner collaborating with another AI agent.
Your mission is to brainstorm, validate ideas, and offer well-reasoned second opinions.
"""

CHAT_SPECIFIC_GUIDELINES = """
SCOPE & FOCUS
• Ground every suggestion in the project's current tech stack
• Avoid over-engineered solutions
• Keep proposals practical and actionable

COLLABORATION APPROACH
1. Engage deeply with the agent's input
2. Examine edge cases and failure modes
3. Present balanced perspectives
4. Challenge assumptions constructively
"""

# Dynamic assembly
CHAT_PROMPT = f"""
{COLLABORATION_HEADER}
{CHAT_CORE_ROLE}
{LINE_NUMBER_INSTRUCTIONS}
{FILES_REQUIRED_PROTOCOL}
{CHAT_SPECIFIC_GUIDELINES}
{TOOL_AWARENESS_SECTION}
{ESCALATION_GUIDANCE}
"""
```

**Benefits**:
- **Reduced from 77 lines → ~30 lines** (60% reduction)
- **No duplication** - shared components referenced
- **Easy to maintain** - change once, apply everywhere
- **Dynamic** - manager can inject context-specific sections

---

## 🔄 AI MANAGER WORKFLOW

### Request Flow

```
1. User Request
   ↓
2. AI Manager Receives Request
   ↓
3. Manager Analyzes Context
   - User intent
   - Request complexity
   - Available tools
   - Historical patterns
   ↓
4. Manager Enriches Request
   - Add missing context
   - Optimize parameters
   - Suggest alternatives
   ↓
5. Manager Assembles Dynamic Prompt
   - Core manager prompt
   - Shared components
   - Tool-specific sections
   - Context-specific additions
   ↓
6. Tool Executes with Enhanced Prompt
   ↓
7. Manager Monitors Execution
   - Progress tracking
   - Error detection
   - Intervention if needed
   ↓
8. Manager Enhances Results
   - Add context
   - Suggest next steps
   - Provide insights
   ↓
9. Return to User
```

### Manager Intelligence Examples

**Example 1: Parameter Optimization**
```
User: "Analyze this code"
Manager: 
  - Detects missing file paths
  - Suggests relevant files based on context
  - Adds thinking_mode based on complexity
  - Injects project-specific context
```

**Example 2: Intelligent Routing**
```
User: "Review this code for bugs"
Manager:
  - Analyzes request intent
  - Suggests codereview instead of analyze
  - Explains why codereview is better
  - Offers to switch tools
```

**Example 3: Error Recovery**
```
Tool: Returns error (missing context)
Manager:
  - Detects error pattern
  - Identifies missing files
  - Automatically retries with enriched context
  - No user intervention needed
```

**Example 4: Progress Monitoring**
```
Multi-step workflow (analyze → refactor → test)
Manager:
  - Tracks progress across steps
  - Maintains context between steps
  - Suggests next logical step
  - Prevents redundant work
```

---

## 📁 IMPLEMENTATION PLAN

### Phase 1: Create Shared Components (Week 1)

**Tasks**:
1. Create `systemprompts/prompt_components.py`
2. Extract common instructions from existing prompts
3. Define reusable component library
4. Create unit tests for components

**Deliverables**:
- `prompt_components.py` with 5-7 reusable components
- Test suite for component validation
- Documentation for each component

### Phase 2: Create Manager Core Prompt (Week 1)

**Tasks**:
1. Create `systemprompts/manager_prompt.py`
2. Define manager responsibilities and workflow
3. Implement dynamic prompt assembly logic
4. Add manager intelligence hooks

**Deliverables**:
- `manager_prompt.py` with core manager behavior
- Dynamic prompt assembly function
- Manager workflow documentation

### Phase 3: Refactor Tool Prompts (Week 2)

**Tasks**:
1. Refactor each tool prompt to use shared components
2. Remove duplication
3. Add manager collaboration hooks
4. Test each refactored prompt

**Priority Order**:
1. chat_prompt.py (most used)
2. thinkdeep_prompt.py
3. analyze_prompt.py
4. codereview_prompt.py
5. debug_prompt.py
6. ... (remaining 8 tools)

**Deliverables**:
- 13 refactored tool prompts (60-70% smaller)
- Backward compatibility maintained
- Test suite for each prompt

### Phase 4: Integration & Testing (Week 2)

**Tasks**:
1. Integrate manager into request flow
2. Test dynamic prompt assembly
3. Validate manager intelligence features
4. Performance testing

**Deliverables**:
- Fully integrated manager system
- Test results showing improvements
- Performance benchmarks

---

## 📊 EXPECTED OUTCOMES

### Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Total Prompt Lines** | ~1,000 | ~300 | 70% reduction |
| **Duplication** | 70% | 0% | 100% elimination |
| **Manager Utilization** | 10% | 90% | 9x increase |
| **Maintainability** | Low | High | Significant |
| **Extensibility** | Medium | High | Improved |

### User Experience Improvements

1. **Smarter Routing**
   - Manager suggests better tools automatically
   - Reduces user trial-and-error

2. **Better Error Handling**
   - Manager detects and recovers from errors
   - Automatic retry with enriched context

3. **Context Awareness**
   - Manager maintains context across requests
   - Reduces need for repetition

4. **Progress Tracking**
   - Manager monitors multi-step workflows
   - Suggests logical next steps

---

## 🎯 NEXT STEPS

### Immediate Actions

1. **Review & Approve** this design proposal
2. **Create implementation tasks** in task manager
3. **Set up development branch** for prompt refactoring
4. **Begin Phase 1** (Shared Components)

### Success Criteria

- ✅ 70% reduction in prompt code duplication
- ✅ Manager actively enhances every request
- ✅ 100% backward compatibility maintained
- ✅ Improved user experience metrics
- ✅ Easier to add new tools

---

**Document Status**: 🎯 **READY FOR REVIEW**  
**Next Action**: Approve design and begin implementation  
**Estimated Timeline**: 2 weeks for full implementation

