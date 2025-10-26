# EXAI-MCP Server Capabilities Overview

**READ THIS FIRST** - Essential capabilities for AI agents working with EXAI-MCP Server

**Last Updated:** 2025-10-26 (Phase 2.4 - File Deduplication Complete)

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

**🆕 CRITICAL UPDATES:**
- **2025-10-26:** SHA256-based file deduplication production-ready! Automatic duplicate detection and storage savings.
- **2025-10-25:** Automatic file size validation active! Files >5KB trigger warnings suggesting kimi_upload_files workflow.

### Decision Matrix:

| File Size | Method | Token Savings | Deduplication | Auto-Warning | When to Use |
|-----------|--------|---------------|---------------|--------------|-------------|
| **<5KB** | `files` parameter | N/A | ✅ SHA256 | ❌ No | Quick, single-use, small files |
| **>5KB (Kimi)** | `kimi_upload_files` | 70-80% | ✅ SHA256 | ✅ Yes | Large files with Kimi models |
| **>5KB (GLM)** | `glm_multi_file_chat` | 70-80% | ✅ SHA256 | ✅ Yes | Large files with GLM models |

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

**Large Files (>5KB) - Use Upload Workflow:**

**Option A: Kimi Upload (for Kimi models):**
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

**Option B: GLM Upload (for GLM models):**
```python
# Upload and chat in one call
glm_multi_file_chat(
    files=["c:\\Project\\large_document.pdf"],
    prompt="Summarize this document",
    model="glm-4.6"
)
```

### Why This Matters:
- **Token Savings:** 70-80% reduction in token usage
- **Cost Savings:** Significant reduction in API costs
- **Performance:** Faster processing for large files
- **Persistence:** Uploaded files can be referenced across multiple conversations
- **Deduplication:** SHA256-based duplicate detection prevents redundant storage
- **Storage Savings:** Automatic reference counting and cleanup

### Deduplication Benefits (NEW - 2025-10-26):
- **Automatic SHA256 Detection** - All uploads calculate hashes automatically
- **Reference Counting** - Tracks file usage across providers
- **Storage Savings** - Prevents duplicate storage in Supabase and AI providers
- **Cache Performance** - Instant duplicate detection via in-memory cache
- **Monitoring** - Built-in metrics track cache hit rates and storage savings

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

**⚠️ CRITICAL: "YOU Investigate First" Pattern**

1. **YOU investigate first** using view/codebase-retrieval tools
2. **YOU call workflow tool** with your findings
3. **Tool auto-executes** internally (no AI calls during steps 2-N)
4. **Tool calls expert analysis** at END (one AI call for validation)
5. **You receive** comprehensive analysis with recommendations

**Why This Matters:**
- ✅ **Efficiency** - Tools validate YOUR findings, not discover them
- ✅ **Quality** - Expert analysis validates your investigation
- ✅ **Cost** - Single AI call at end, not during investigation
- ✅ **Transparency** - Clear separation between investigation and validation

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
    confidence="exploring"  # Start with exploring, progress to certain
)
```

**Common Mistake:**
```python
# ❌ WRONG - Expecting tool to investigate for you
debug_EXAI-WS(
    step="Investigate authentication bug",
    findings="Please investigate the auth system",  # Tool won't investigate!
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
- **Investigate first, then use workflow tools** (critical!)
- Enable web search for documentation/best practices
- Let system handle file deduplication automatically
- Progress confidence levels appropriately (exploring → certain)
- Extract and track continuation_id from responses

### ❌ DON'T:
- Paste large code snippets in prompts (use files parameter)
- **Call workflow tools expecting them to investigate for you** (critical!)
- Use continuation_id for unrelated queries
- Reuse continuation_id across different conversation topics
- Assume all models have same context window
- Enable web search for code analysis tasks
- Manually check for duplicate files (system handles it)
- Set confidence="certain" prematurely in workflow tools

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
- Small files (<5KB): Use `files` parameter in `chat_EXAI-WS`
- Large files with Kimi (>5KB): Use `kimi_upload_files` + `kimi_chat_with_files`
- Large files with GLM (>5KB): Use `glm_multi_file_chat`
- File management: Use `kimi_manage_files` (Kimi) or `glm_upload_file` (GLM)

**Conversation:**
- Continuation: Use `continuation_id` from previous response
- Multi-turn: Maintain continuation_id across calls
- Context: Automatically embedded when continuation_id provided

---

**Last Updated:** 2025-10-25  
**Purpose:** Quick capability overview for AI agents  
**Next Steps:** Read `docs/AGENT_CAPABILITIES.md` for detailed patterns

