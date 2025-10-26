# EXAI-MCP Agent Capabilities Guide

**Purpose:** Quick reference for AI agents to discover and use system capabilities efficiently.

**Last Updated:** 2025-10-26 (Phase 2.4 - File Deduplication Complete)

**⚠️  CRITICAL UPDATES:**
- **2025-10-26:** SHA256-based file deduplication now production-ready! Automatic duplicate detection and storage savings.
- **2025-10-25:** File size validation active! Files >5KB trigger automatic warnings suggesting kimi_upload_files workflow.

---

## 🚀 **QUICK PATTERN REFERENCE**

| Need | Pattern | Tool | Key Point |
|------|---------|------|-----------|
| Quick question | Direct chat | `chat_EXAI-WS` | Use for simple queries |
| Analyze code | **YOU investigate first** → analyze | `analyze_EXAI-WS` | Tool validates YOUR findings |
| Debug issue | **YOU investigate** → debug | `debug_EXAI-WS` | Progress confidence: exploring → certain |
| Large file | Upload workflow | `kimi_upload_files` | ✅ SHA256 deduplication automatic |
| Continue conversation | Use continuation_id | Any tool | Extract from `continuation_offer` |
| Track consultation | Log metadata | Any tool | Monitor consultation_id and tokens |

---

## 🎯 **CRITICAL WORKFLOWS (MUST KNOW)**

### **1. File Handling Patterns**

**⚠️  AUTOMATIC FILE SIZE VALIDATION (NEW - 2025-10-25):**
- Files >5KB now trigger automatic warnings in logs
- System suggests kimi_upload_files workflow for token savings
- Validation happens transparently during file processing
- No breaking changes - existing code continues to work

**Decision Matrix:**

| File Size | Method | Tool(s) | Token Savings | Deduplication | Auto-Warning | Example Use Case |
|-----------|--------|---------|---------------|---------------|--------------|------------------|
| **<5KB** | Direct embed | `chat_EXAI-WS(files=[...])` | N/A | ✅ SHA256 | ❌ No | Single code file analysis |
| **>5KB (Kimi)** | Kimi upload | `kimi_upload_files` + `kimi_chat_with_files` | 70-80% | ✅ SHA256 | ✅ Yes | Large docs with Kimi |
| **>5KB (GLM)** | GLM upload | `glm_multi_file_chat` | 70-80% | ✅ SHA256 | ✅ Yes | Large docs with GLM |
| **Multiple files** | Upload workflow | Kimi or GLM upload tools | 80-90% | ✅ SHA256 | ✅ Yes | Batch analysis |
| **Repeated queries** | Upload once, query many | Upload + multiple chats | 90-95% | ✅ SHA256 | ✅ Yes | Iterative analysis |

**🆕 Deduplication Benefits (2025-10-26):**
- **Automatic SHA256 Detection** - All uploads calculate SHA256 hashes automatically
- **Reference Counting** - Tracks how many times each file is referenced
- **Storage Savings** - Prevents duplicate storage in Supabase and AI providers
- **Performance Benefits** - Cache hits provide instant duplicate detection
- **Monitoring** - Built-in metrics track cache hit rates and storage savings

**Examples:**

```python
# ✅ CORRECT - Small file (<5KB)
chat_EXAI-WS(
    prompt="Review this implementation",
    files=["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\file_base.py"],
    model="glm-4.6"
)
# No warning - file is under 5KB threshold

# ✅ CORRECT - Large file (>5KB) with Kimi upload workflow
# Step 1: Upload
upload_result = kimi_upload_files(files=["c:\\Project\\EX-AI-MCP-Server\\large_file.py"])
# Step 2: Chat
kimi_chat_with_files(
    prompt="Review this implementation",
    file_ids=[upload_result[0]["file_id"]],
    model="kimi-k2-0905-preview"
)
# Saves 70-80% tokens compared to direct embedding

# ✅ CORRECT - Large file (>5KB) with GLM upload workflow
glm_multi_file_chat(
    files=["c:\\Project\\EX-AI-MCP-Server\\large_file.py"],
    prompt="Review this implementation",
    model="glm-4.6"
)
# Saves 70-80% tokens compared to direct embedding

# ⚠️  SUBOPTIMAL - Large file with direct embedding (still works but wasteful)
chat_EXAI-WS(
    prompt="Review this implementation",
    files=["c:\\Project\\EX-AI-MCP-Server\\large_file.py"],  # >5KB
    model="glm-4.6"
)
# System will log warning: "⚠️  FILE SIZE WARNING: 1 file(s) exceed 5KB threshold"
# Recommendation: Use kimi_upload_files workflow for 70-80% token savings

# ❌ WRONG - Manually reading and embedding
view("large_file.py")  # Don't do this!
chat_EXAI-WS(prompt="Here's the code: [pasted content]")  # Wastes tokens!
```

**Deduplication Best Practices (NEW - 2025-10-26):**

✅ **DO:**
- Let the system handle deduplication automatically
- Upload the same file multiple times - system will detect duplicates
- Monitor deduplication metrics with `get_dedup_metrics()`
- Use async upload for files >100MB

❌ **DON'T:**
- Manually check for duplicates before uploading
- Implement client-side deduplication (system handles it)
- Worry about uploading the same file to different providers

---

## 🎯 **EXAI TOOL USAGE PHILOSOPHY**

### **Core Principle: "YOU Investigate First"**

EXAI workflow tools follow a specific pattern where **YOU (the agent) must investigate first**, then call the tool with your findings. This ensures:

1. **Efficiency** - Tools don't waste time investigating what you already know
2. **Quality** - Expert analysis validates YOUR findings, not discovers them
3. **Transparency** - Clear separation between investigation and validation
4. **Cost** - Single AI call at the end for validation, not during investigation

### **Pattern Breakdown:**

```
Step 1: YOU investigate (using view, codebase-retrieval, etc.)
Step 2: YOU call workflow tool with YOUR findings
Step 3: Tool auto-executes internally (no AI calls)
Step 4: Tool calls expert analysis at END (one AI call)
Step 5: You receive comprehensive analysis with recommendations
```

### **Example - Proper Usage:**

```python
# Step 1: YOU investigate first
view(path="src/server.py", type="file")
codebase-retrieval(information_request="How is authentication handled?")

# Step 2: Call workflow tool with YOUR findings
debug_EXAI-WS(
    step="Investigating authentication bug",
    findings="Found that JWT validation is missing expiry check in validate_token()",
    hypothesis="Authentication bypass due to missing token expiration validation",
    relevant_files=["c:\\Project\\src\\auth.py"],
    confidence="exploring"  # Start with exploring, not certain
)
```

### **Example - Improper Usage:**

```python
# ❌ WRONG - Expecting tool to investigate for you
debug_EXAI-WS(
    step="Investigate authentication bug",
    findings="Please investigate the auth system",  # Tool won't investigate!
    confidence="exploring"
)
```

### **Confidence Level Progression**

**Understanding the Journey:**

1. **"exploring"** - Initial investigation phase
   - Use when: Starting analysis, forming hypotheses
   - Indicates: "I'm investigating, not yet certain"
   - Example: "Exploring potential causes of the memory leak"

2. **"low"** - Early evidence gathering
   - Use when: Found initial clues, need more validation
   - Indicates: "I have some leads but need confirmation"
   - Example: "Low confidence: Possible race condition in session manager"

3. **"medium"** - Building evidence
   - Use when: Multiple data points support conclusion
   - Indicates: "Evidence suggests this direction"
   - Example: "Medium confidence: Pattern indicates database connection leak"

4. **"high"** - Strong evidence gathered
   - Use when: Substantial evidence supports conclusion
   - Indicates: "Evidence strongly suggests this is the issue"
   - Example: "High confidence: Missing null check in user service"

5. **"very_high"** - Near certainty
   - Use when: Overwhelming evidence, minimal doubt
   - Indicates: "Almost certain this is the issue"
   - Example: "Very high confidence: Buffer overflow confirmed in parse_config()"

6. **"certain"** - Definitive conclusion
   - Use when: Evidence is conclusive, no reasonable doubt
   - Indicates: "This is definitively the issue"
   - Example: "Certain: Root cause verified with test case at line 142"

**Progression Example:**

```python
# Initial investigation
debug_EXAI-WS(step="Initial investigation", confidence="exploring")

# After finding evidence
debug_EXAI-WS(step="Found evidence in logs", confidence="low")

# After confirming pattern
debug_EXAI-WS(step="Pattern confirmed across multiple instances", confidence="medium")

# After substantial validation
debug_EXAI-WS(step="Validated with test cases", confidence="high")

# After definitive proof
debug_EXAI-WS(step="Root cause verified and fix tested", confidence="certain")
```

---

### **2. Tool Escalation Patterns**

**When to Use Which Tool:**

```
General Questions → chat_EXAI-WS
    ↓ (need structured analysis)
Code Analysis → analyze_EXAI-WS
    ↓ (found issues)
Code Review → codereview_EXAI-WS
    ↓ (found bugs)
Debugging → debug_EXAI-WS
    ↓ (need deep reasoning)
Deep Analysis → thinkdeep_EXAI-WS
```

**Decision Tree:**

- **Quick question or brainstorming?** → `chat_EXAI-WS`
- **Need to understand architecture?** → `analyze_EXAI-WS`
- **Need to review code quality?** → `codereview_EXAI-WS`
- **Need to find root cause of bug?** → `debug_EXAI-WS`
- **Need deep reasoning or complex analysis?** → `thinkdeep_EXAI-WS`
- **Need to plan implementation?** → `planner_EXAI-WS`
- **Need multiple perspectives?** → `consensus_EXAI-WS`

---

### **3. Conversation Continuation**

**Use `continuation_id` for multi-turn conversations:**

```python
# First call
response1 = chat_EXAI-WS(
    prompt="Explain the provider architecture",
    model="glm-4.6"
)
continuation_id = response1["continuation_offer"]["continuation_id"]

# Follow-up call (uses conversation history automatically)
response2 = chat_EXAI-WS(
    prompt="How does this relate to the session manager?",
    continuation_id=continuation_id,
    model="glm-4.6"
)
```

**Benefits:**
- ✅ Conversation history automatically embedded
- ✅ No need to repeat context
- ✅ More coherent multi-turn discussions

### **Continuation ID Lifecycle Management**

**Continuation ID Rules:**

1. **Creation** - Offered in response when conversation can continue
2. **Extraction** - Extract from `response['continuation_offer']['continuation_id']`
3. **Usage** - Pass to next call to maintain context
4. **Scope** - Valid for the specific conversation chain only
5. **Expiration** - Varies by provider (typically 30-60 minutes)

**Critical Rules:**

✅ **DO:**
- Extract continuation_id immediately after receiving response
- Use continuation_id for follow-up questions in same context
- Maintain continuation_id across multiple related calls
- Handle missing continuation_offer gracefully

❌ **DON'T:**
- Reuse continuation_id across different conversations
- Assume continuation_id will always be present
- Store continuation_id for long-term use
- Share continuation_id between different agents

**Tracking Pattern:**

```python
# Recommended tracking pattern
class ConversationTracker:
    def __init__(self):
        self.current_continuation_id = None
        self.conversation_history = []

    def make_call(self, prompt, **kwargs):
        # Add continuation_id if available
        if self.current_continuation_id:
            kwargs['continuation_id'] = self.current_continuation_id

        # Make the call
        response = chat_EXAI-WS(prompt=prompt, **kwargs)

        # Update continuation_id
        if 'continuation_offer' in response:
            self.current_continuation_id = response['continuation_offer']['continuation_id']

        # Track the conversation
        self.conversation_history.append({
            'prompt': prompt,
            'response': response,
            'continuation_id': self.current_continuation_id
        })

        return response
```

---

## 🔍 **TRANSPARENCY & VISIBILITY**

### **Tracking EXAI Consultations**

**Why Track?**
- Debug conversation issues
- Analyze tool usage patterns
- Monitor token consumption
- Identify optimization opportunities

### **Built-in Tracking Features:**

1. **Continuation ID Tracking** - Each consultation offers continuation_id for chain tracking
2. **Response Metadata** - Includes model used, token counts, timing
3. **Activity Logs** - Access via `activity_EXAI-WS` tool
4. **Deduplication Metrics** - Track cache hit rates and storage savings

### **Tracking Best Practices:**

```python
# Track consultation metadata
response = chat_EXAI-WS(prompt="Analyze this code", files=["file.py"])

# Extract tracking information
model_used = response.get('metadata', {}).get('model_used')
continuation_id = response.get('continuation_offer', {}).get('continuation_id')

# Log for visibility
logger.info(f"EXAI Consultation: Model={model_used}, ContinuationID={continuation_id}")
```

### **Metrics to Monitor:**

1. **Token Efficiency** - Files uploaded vs tokens saved
2. **Deduplication Rate** - Cache hit percentage
3. **Tool Usage Patterns** - Which tools used most frequently
4. **Response Quality** - Confidence level progression
5. **Conversation Length** - Average calls per consultation

### **Visibility Tools:**

```python
# Check system activity
activity_EXAI-WS(lines=50, filter="EXAI", source="all")

# Monitor deduplication
from utils.file.deduplication import get_dedup_metrics
metrics = get_dedup_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']}%")
print(f"Storage saved: {metrics['storage_saved_bytes']:,} bytes")

# Track consultation chains
def track_consultation_chain(initial_prompt):
    continuation_id = None
    call_count = 0

    while True:
        call_count += 1
        response = chat_EXAI-WS(
            prompt=initial_prompt if call_count == 1 else input("Next prompt: "),
            continuation_id=continuation_id
        )

        print(f"Call {call_count}: {response['metadata']['model_used']}")

        if 'continuation_offer' in response:
            continuation_id = response['continuation_offer']['continuation_id']
        else:
            break

    return call_count
```

---

## 🛠️ **TOOL CAPABILITIES MATRIX**

### **Simple Tools (No Workflow)**

| Tool | Primary Use | Key Parameters | When to Use |
|------|-------------|----------------|-------------|
| `chat_EXAI-WS` | General chat, brainstorming | `prompt`, `files`, `images`, `continuation_id` | Quick questions, small files |
| `challenge_EXAI-WS` | Critical analysis | `prompt` | When user challenges your response |
| `activity_EXAI-WS` | View MCP activity logs | `lines`, `filter`, `source` | Debugging MCP issues |

### **Workflow Tools (Multi-Step)**

| Tool | Primary Use | Key Parameters | Confidence Levels |
|------|-------------|----------------|-------------------|
| `analyze_EXAI-WS` | Code analysis | `step`, `findings`, `relevant_files`, `confidence` | exploring → certain |
| `codereview_EXAI-WS` | Code review | `step`, `findings`, `issues_found`, `confidence` | exploring → certain |
| `debug_EXAI-WS` | Debugging | `step`, `findings`, `hypothesis`, `confidence` | exploring → certain |
| `refactor_EXAI-WS` | Refactoring analysis | `step`, `findings`, `refactor_type`, `confidence` | exploring → certain |
| `testgen_EXAI-WS` | Test generation | `step`, `findings`, `relevant_files`, `confidence` | exploring → certain |
| `secaudit_EXAI-WS` | Security audit | `step`, `findings`, `audit_focus`, `confidence` | exploring → certain |
| `planner_EXAI-WS` | Planning | `step`, `step_number`, `total_steps`, `next_step_required` | N/A |
| `consensus_EXAI-WS` | Multi-model consensus | `step`, `models`, `findings` | N/A |
| `thinkdeep_EXAI-WS` | Deep reasoning | `step`, `findings`, `confidence` | exploring → certain |

### **File Handling Tools**

| Tool | Primary Use | Key Parameters | When to Use |
|------|-------------|----------------|-------------|
| `kimi_upload_files` | Upload files to Kimi | `files`, `purpose` | Large files (>5KB) with Kimi models |
| `kimi_chat_with_files` | Chat with uploaded files | `prompt`, `file_ids`, `model` | After uploading to Kimi |
| `kimi_manage_files` | Manage uploaded files | `operation`, `file_id` | Cleanup, list Kimi files |
| `glm_upload_file` | Upload file to GLM | `file`, `purpose` | GLM-specific file upload |
| `glm_multi_file_chat` | Upload and chat with GLM | `files`, `prompt`, `model` | Large files (>5KB) with GLM models |

### **Utility Tools**

| Tool | Primary Use | Key Parameters | When to Use |
|------|-------------|----------------|-------------|
| `status_EXAI-WS` | System status | `doctor`, `probe` | Check system health |
| `health_EXAI-WS` | Provider health | `tail_lines` | Check provider status |
| `listmodels_EXAI-WS` | List available models | None | Discover available models |
| `version_EXAI-WS` | Server version | None | Check server version |

---

## ⚠️ **COMMON ANTI-PATTERNS**

### **❌ DON'T DO THIS:**

1. **Manually reading files and embedding in prompts:**
   ```python
   # ❌ WRONG
   content = view("file.py")
   chat_EXAI-WS(prompt=f"Review this code: {content}")
   ```

2. **Using chat_EXAI-WS for files >5KB:**
   ```python
   # ❌ WRONG
   chat_EXAI-WS(files=["large_file.py"])  # File is 50KB
   ```

3. **Manually checking for duplicates (system handles it):**
   ```python
   # ❌ WRONG - Manual deduplication
   existing_files = kimi_manage_files(operation="list")
   if "doc.pdf" not in existing_files:
       kimi_upload_files(files=["doc.pdf"])
   ```

4. **Not using continuation_id for multi-turn:**
   ```python
   # ❌ WRONG
   chat_EXAI-WS(prompt="Explain X")
   chat_EXAI-WS(prompt="How does that relate to Y?")  # Lost context!
   ```

5. **Reusing continuation_id across different contexts:**
   ```python
   # ❌ WRONG - Reusing across different topics
   response1 = chat_EXAI-WS(prompt="Analyze React code")
   continuation_id = response1['continuation_offer']['continuation_id']

   # Different topic - shouldn't reuse!
   response2 = chat_EXAI-WS(
       prompt="Explain Python decorators",
       continuation_id=continuation_id  # Wrong context!
   )
   ```

6. **Setting confidence="certain" prematurely:**
   ```python
   # ❌ WRONG
   debug_EXAI-WS(
       step="Initial investigation",
       confidence="certain"  # Too early!
   )
   ```

7. **Expecting workflow tools to investigate for you:**
   ```python
   # ❌ WRONG - Investigation reversal
   analyze_EXAI-WS(
       step="Please analyze the codebase architecture",
       findings="Need you to investigate"  # Tool won't investigate!
   )
   ```

### **✅ DO THIS INSTEAD:**

1. **Use files parameter for small files:**
   ```python
   # ✅ CORRECT
   chat_EXAI-WS(
       prompt="Review this code",
       files=["c:\\Project\\EX-AI-MCP-Server\\file.py"]
   )
   ```

2. **Use upload workflow for large files:**
   ```python
   # ✅ CORRECT
   upload_result = kimi_upload_files(files=["large_file.py"])
   kimi_chat_with_files(
       prompt="Review this code",
       file_ids=[upload_result[0]["file_id"]]
   )
   ```

3. **Let system handle deduplication:**
   ```python
   # ✅ CORRECT - System detects duplicates automatically
   kimi_upload_files(files=["doc.pdf"])  # Upload freely
   kimi_upload_files(files=["doc.pdf"])  # System deduplicates automatically
   ```

4. **Use continuation_id for related queries:**
   ```python
   # ✅ CORRECT
   response1 = chat_EXAI-WS(prompt="Explain X")
   continuation_id = response1["continuation_offer"]["continuation_id"]

   response2 = chat_EXAI-WS(
       prompt="How does that relate to Y?",
       continuation_id=continuation_id
   )
   ```

5. **Create new continuation_id for different topics:**
   ```python
   # ✅ CORRECT - Fresh start for new topic
   response1 = chat_EXAI-WS(prompt="Analyze React code")
   # ... conversation about React ...

   # New topic - start fresh
   response2 = chat_EXAI-WS(prompt="Explain Python decorators")
   ```

6. **Use appropriate confidence levels:**
   ```python
   # ✅ CORRECT
   debug_EXAI-WS(
       step="Initial investigation",
       confidence="exploring"  # Start low
   )
   # ... investigate more ...
   debug_EXAI-WS(
       step="Root cause identified",
       confidence="certain"  # Only when truly certain
   )
   ```

7. **Investigate first, then use workflow tools:**
   ```python
   # ✅ CORRECT - YOU investigate first
   view(path="src/main.py")
   codebase-retrieval(information_request="How is routing handled?")

   analyze_EXAI-WS(
       step="Architecture analysis",
       findings="Found modular structure with clear separation of concerns"
   )
   ```

---

## 🎯 **MODEL SELECTION GUIDE**

### **GLM Models (ZhipuAI)**

| Model | Speed | Cost | Use Case |
|-------|-------|------|----------|
| `glm-4.5-flash` | ⚡⚡⚡ | FREE | Background tasks, AI Auditor, simple queries |
| `glm-4.5` | ⚡⚡ | PAID | Standard tasks |
| `glm-4.6` | ⚡ | PAID | Complex reasoning, code review |

### **Kimi Models (Moonshot)**

| Model | Speed | Cost | Context | Use Case |
|-------|-------|------|---------|----------|
| `kimi-k2-turbo-preview` | ⚡⚡ | PAID | 128k | Fast responses |
| `kimi-k2-0905-preview` | ⚡ | PAID | 200k+ | Large context, file analysis |

### **Model Selection Decision Tree:**

- **Background task (AI Auditor)?** → `glm-4.5-flash` (FREE)
- **Quick question?** → `glm-4.5-flash` or `kimi-k2-turbo-preview`
- **Complex reasoning?** → `glm-4.6`
- **Large files/context?** → `kimi-k2-0905-preview`
- **Cost-sensitive?** → `glm-4.5-flash` (FREE)

---

## 📚 **RELATED DOCUMENTATION**

- **Tool Implementations:** `tools/` directory
- **Best Practices:** `docs/02_Service_Components/EXAI_TOOL_DECISION_GUIDE.md`
- **Quick Reference:** `docs/fix_implementation/QUICK_REFERENCE_EXAI_USAGE.md`
- **File Handling Analysis:** `docs/05_CURRENT_WORK/2025-10-25/EXAI_FILE_HANDLING_ANALYSIS__2025-10-25.md`
- **Capability Discovery:** `docs/05_CURRENT_WORK/2025-10-25/CAPABILITY_DISCOVERY_INVESTIGATION__2025-10-25.md`

---

**For AI Agents:** Read this file FIRST before starting any task. It will save you time and tokens!

**For Humans:** This file documents how AI agents should use the EXAI-MCP system efficiently.

