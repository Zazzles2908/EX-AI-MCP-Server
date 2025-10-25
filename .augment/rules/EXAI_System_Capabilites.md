---
type: "agent_requested"
description: "EXAI-Systems_Capabilities"
---

# EXAI-MCP Server Capabilities Overview

**READ THIS FIRST** - Essential capabilities for AI agents working with EXAI-MCP Server

---

## 🚀 **QUICK START FOR NEW AI AGENTS**

### First 5 Minutes:
1. **Read this file** - Core capabilities overview
2. **Check `docs/AGENT_CAPABILITIES.md`** - Detailed patterns and examples
3. **Review tool descriptions** - Contextual capability hints

### Discovery Tools:
- Run `listmodels_EXAI-WS` to see available AI models
- Run `status_EXAI-WS` to check system health
- Run `provider_capabilities_EXAI-WS` to see provider features

---

## 📁 **FILE HANDLING - CRITICAL FOR TOKEN EFFICIENCY**

### Decision Matrix:

| File Size | Method | Token Savings | When to Use |
|-----------|--------|---------------|-------------|
| **<5KB** | `files` parameter | 70-80% | Quick, single-use, small files |
| **>5KB** | `kimi_upload_files` | 70-80% | Large files, persistent reference |

### Usage Examples:

**Small Files (<5KB) - Use `files` parameter:**
```python
chat_EXAI-WS(
    prompt="Analyze these configuration files",
    files=[
        "c:\\Project\\config.json",
        "c:\\Project\\.env.example"
    ],
    model="glm-4.6"
)
```

**Large Files (>5KB) - Use `kimi_upload_files`:**
```python
# Step 1: Upload files
result = kimi_upload_files(
    files=["c:\\Project\\large_document.pdf"]
)
file_ids = result['file_ids']

# Step 2: Chat with uploaded files
kimi_chat_with_files(
    prompt="Summarize this document",
    file_ids=file_ids,
    model="kimi-k2-0905-preview"
)
```

### Why This Matters:
- **Token Savings:** 70-80% reduction in token usage
- **Cost Savings:** Significant reduction in API costs
- **Performance:** Faster processing for large files
- **Persistence:** Uploaded files can be referenced across multiple conversations

---

## 🔄 **CONVERSATION CONTINUITY - MAINTAIN CONTEXT**

### The `continuation_id` Parameter

**What It Does:**
- Maintains conversation context across multiple tool calls
- Essential for multi-step workflows
- Required for referencing uploaded files
- Enables complex reasoning chains

**How to Use:**

```python
# First call - no continuation_id
response1 = chat_EXAI-WS(
    prompt="Analyze this codebase architecture",
    files=["c:\\Project\\README.md"],
    model="glm-4.6"
)

# Extract continuation_id from response
continuation_id = response1['continuation_offer']['continuation_id']

# Second call - use continuation_id to maintain context
response2 = chat_EXAI-WS(
    prompt="Now suggest improvements based on your analysis",
    continuation_id=continuation_id,  # ← Maintains context!
    model="glm-4.6"
)
```

**When to Use:**
- ✅ Multi-step analysis or debugging
- ✅ Follow-up questions about previous responses
- ✅ Referencing uploaded files across calls
- ✅ Building on previous recommendations

**When NOT to Use:**
- ❌ Independent, unrelated queries
- ❌ Starting fresh analysis
- ❌ Different topics/contexts

---

## 🤖 **MODEL SELECTION - CHOOSE THE RIGHT TOOL**

### Available Models:

**GLM Models (Z.ai):**
- `glm-4.6` - **Default for complex tasks** (high quality, balanced cost)
- `glm-4.5-flash` - **Fast, free** (simple tasks, routing, quick responses)
- `glm-4.5` - Standard model
- `glm-4.5-air` - Lightweight model

**Kimi Models (Moonshot):**
- `kimi-k2-0905-preview` - **Best for file operations** (large context, extraction)
- `kimi-k2-turbo-preview` - Fast Kimi variant
- `moonshot-v1-128k` - Large context window
- `kimi-latest` - Latest stable version

### Selection Guide:

| Task Type | Recommended Model | Why |
|-----------|-------------------|-----|
| **File Analysis** | kimi-k2-0905-preview | Large context, file extraction |
| **Complex Reasoning** | glm-4.6 | High quality, deep thinking |
| **Quick Queries** | glm-4.5-flash | Fast, free, efficient |
| **Code Review** | glm-4.6 | Detailed analysis capability |
| **Long Documents** | kimi-k2-0905-preview | Large context window |

---

## 🛠️ **WORKFLOW TOOLS - STRUCTURED ANALYSIS**

### Available Workflow Tools:

**Investigation & Analysis:**
- `debug_EXAI-WS` - Root cause analysis, bug investigation
- `analyze_EXAI-WS` - Code analysis, architectural assessment
- `codereview_EXAI-WS` - Code review with expert validation
- `thinkdeep_EXAI-WS` - Complex problem analysis

**Code Quality:**
- `refactor_EXAI-WS` - Refactoring opportunities
- `secaudit_EXAI-WS` - Security audit (OWASP Top 10)
- `testgen_EXAI-WS` - Test generation
- `docgen_EXAI-WS` - Documentation generation

**Planning & Validation:**
- `planner_EXAI-WS` - Task planning and breakdown
- `precommit_EXAI-WS` - Pre-commit validation
- `consensus_EXAI-WS` - Multi-model consensus
- `tracer_EXAI-WS` - Code tracing and flow analysis

### How Workflow Tools Work:

1. **YOU investigate first** using view/codebase-retrieval tools
2. **YOU call workflow tool** with your findings
3. **Tool auto-executes** internally (no AI calls during steps 2-N)
4. **Tool calls expert analysis** at END (one AI call for validation)
5. **You receive** comprehensive analysis with recommendations

**Example:**
```python
# Step 1: YOU investigate
view(path="src/server.py", type="file")
codebase-retrieval(information_request="How is authentication handled?")

# Step 2: Call workflow tool with YOUR findings
debug_EXAI-WS(
    step="Investigating authentication bug",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Found that JWT validation is missing expiry check",
    hypothesis="Authentication bypass due to missing token expiration validation",
    relevant_files=["c:\\Project\\src\\auth.py"],
    confidence="high"
)
```

---

## 🌐 **WEB SEARCH - CURRENT INFORMATION**

### When to Enable:

**Use `use_websearch=True` for:**
- ✅ Current documentation lookup
- ✅ Best practices research
- ✅ Framework/library information
- ✅ Industry standards
- ✅ Recent changes/updates

**Use `use_websearch=False` for:**
- ❌ Code analysis (use codebase context)
- ❌ Internal system knowledge
- ❌ Fast responses needed
- ❌ Token efficiency critical

### Example:

```python
chat_EXAI-WS(
    prompt="What are the latest best practices for React 19 server components?",
    use_websearch=True,  # ← Enable for current information
    model="glm-4.6"
)
```

---

## 💡 **COMMON PATTERNS & ANTI-PATTERNS**

### ✅ DO:
- Upload files instead of pasting content in prompts
- Use continuation_id for multi-step workflows
- Choose appropriate model for task type
- Investigate first, then use workflow tools
- Enable web search for documentation/best practices

### ❌ DON'T:
- Paste large code snippets in prompts (use files parameter)
- Call workflow tools expecting them to investigate for you
- Use continuation_id for unrelated queries
- Assume all models have same context window
- Enable web search for code analysis tasks

---

## 📚 **DETAILED DOCUMENTATION**

For comprehensive patterns, examples, and advanced usage:

**Primary Reference:**
- `docs/AGENT_CAPABILITIES.md` - Complete capability guide (300 lines)

**Architecture & Decisions:**
- `docs/05_CURRENT_WORK/2025-10-24/ARCHITECTURE_DECISIONS_AND_CORRECTIONS__2025-10-24.md`

**Testing & Validation:**
- `docs/05_CURRENT_WORK/MASTER_PLAN__TESTING_AND_CLEANUP.md`

**Recent Achievements:**
- `docs/05_CURRENT_WORK/2025-10-25/WEBSOCKET_FIX_VALIDATED__PHASE_0_COMPLETE__2025-10-25.md`

---

## 🎯 **SUCCESS METRICS**

**You're using capabilities effectively if:**
- ✅ You discover file upload patterns within 5 minutes
- ✅ You understand continuation_id usage without trial/error
- ✅ You select appropriate models for different tasks
- ✅ You use workflow tools correctly (investigate first)
- ✅ You achieve 70-80% token savings with file uploads

---

## 🔗 **QUICK REFERENCE LINKS**

**Tool Documentation:**
- All EXAI tools: Check tool descriptions in schema
- Model list: Run `listmodels_EXAI-WS`
- System status: Run `status_EXAI-WS`

**File Handling:**
- Small files: Use `files` parameter in `chat_EXAI-WS`
- Large files: Use `kimi_upload_files` + `kimi_chat_with_files`
- File management: Use `kimi_manage_files`

**Conversation:**
- Continuation: Use `continuation_id` from previous response
- Multi-turn: Maintain continuation_id across calls
- Context: Automatically embedded when continuation_id provided

---

**Last Updated:** 2025-10-25  
**Purpose:** Quick capability overview for AI agents  
**Next Steps:** Read `docs/AGENT_CAPABILITIES.md` for detailed patterns

