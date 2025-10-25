---
type: "agent_requested"
description: "Guide to Function Calls with EXAI-WS MCP"
---

# EXAI-MCP Agent Capabilities Guide

**Purpose:** Quick reference for AI agents to discover and use system capabilities efficiently.

**Last Updated:** 2025-10-25

---

## 🎯 **CRITICAL WORKFLOWS (MUST KNOW)**

### **1. File Handling Patterns**

**Decision Matrix:**

| File Size | Method | Tool(s) | Token Savings | Example Use Case |
|-----------|--------|---------|---------------|------------------|
| **<5KB** | Direct embed | `chat_EXAI-WS(files=[...])` | 70-80% | Single code file analysis |
| **>5KB** | Upload workflow | `kimi_upload_files` + `kimi_chat_with_files` | 80-90% | Large documentation |
| **Multiple files** | Upload workflow | `kimi_upload_files` + `kimi_chat_with_files` | 85-95% | Batch analysis |
| **Repeated queries** | Upload once, query many | `kimi_upload_files` + multiple `kimi_chat_with_files` | 90-95% | Iterative analysis |

**Examples:**

```python
# ✅ CORRECT - Small file (<5KB)
chat_EXAI-WS(
    prompt="Review this implementation",
    files=["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\file_base.py"],
    model="glm-4.6"
)

# ✅ CORRECT - Large file (>5KB)
# Step 1: Upload
upload_result = kimi_upload_files(files=["c:\\Project\\EX-AI-MCP-Server\\large_file.py"])
# Step 2: Chat
kimi_chat_with_files(
    prompt="Review this implementation",
    file_ids=[upload_result[0]["file_id"]],
    model="kimi-k2-0905-preview"
)

# ❌ WRONG - Manually reading and embedding
view("large_file.py")  # Don't do this!
chat_EXAI-WS(prompt="Here's the code: [pasted content]")  # Wastes tokens!
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
| `kimi_upload_files` | Upload files to Kimi | `files`, `purpose` | Large files (>5KB) |
| `kimi_chat_with_files` | Chat with uploaded files | `prompt`, `file_ids`, `model` | After uploading files |
| `kimi_manage_files` | Manage uploaded files | `operation`, `file_id` | Cleanup, list files |
| `glm_upload_file` | Upload file to GLM | `file`, `purpose` | GLM-specific file handling |

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

3. **Uploading files multiple times:**
   ```python
   # ❌ WRONG
   kimi_upload_files(files=["doc.md"])
   kimi_upload_files(files=["doc.md"])  # Duplicate upload!
   ```

4. **Not using continuation_id for multi-turn:**
   ```python
   # ❌ WRONG
   chat_EXAI-WS(prompt="Explain X")
   chat_EXAI-WS(prompt="How does that relate to Y?")  # Lost context!
   ```

5. **Setting confidence="certain" prematurely:**
   ```python
   # ❌ WRONG
   debug_EXAI-WS(
       step="Initial investigation",
       confidence="certain"  # Too early!
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

3. **Reuse uploaded files:**
   ```python
   # ✅ CORRECT
   upload_result = kimi_upload_files(files=["doc.md"])
   file_id = upload_result[0]["file_id"]
   
   kimi_chat_with_files(prompt="Question 1?", file_ids=[file_id])
   kimi_chat_with_files(prompt="Question 2?", file_ids=[file_id])
   ```

4. **Use continuation_id:**
   ```python
   # ✅ CORRECT
   response1 = chat_EXAI-WS(prompt="Explain X")
   continuation_id = response1["continuation_offer"]["continuation_id"]
   
   response2 = chat_EXAI-WS(
       prompt="How does that relate to Y?",
       continuation_id=continuation_id
   )
   ```

5. **Use appropriate confidence levels:**
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

