# K2 Consultation Guide - How to Work with Kimi K2 Model
**Date:** 2025-11-03  
**Purpose:** Enable effective collaboration with K2 for complex problem-solving  
**Audience:** Next agent continuing production readiness work

---

## 🚀 Quick Start Checklist

Before calling K2, ensure you have:
- ✅ **Current date specified** in prompt (e.g., "Today is November 3, 2025")
- ✅ **Model explicitly set** to `kimi-k2-0905-preview`
- ✅ **Continuation ID** saved from previous exchanges (if continuing conversation)
- ✅ **Absolute file paths** ready (never relative paths)
- ✅ **Clear question** formulated (avoid vague requests)
- ✅ **Web search enabled** if current information needed (`use_websearch=true`)

---

## 🎯 When to Use K2 vs Other Models

### Use K2 For:
- ✅ Strategic architectural decisions
- ✅ Complex debugging requiring deep reasoning
- ✅ Multi-step problem analysis
- ✅ Code review with security/performance implications
- ✅ System design validation
- ✅ Root cause analysis of systemic issues

### Use GLM-4.6 For:
- ✅ Quick code generation
- ✅ Simple refactoring
- ✅ Documentation writing
- ✅ Straightforward bug fixes

### Use GLM-4.5-flash For:
- ✅ Simple queries
- ✅ Formatting tasks
- ✅ Basic information retrieval

---

## 🔧 K2 Model Selection & Configuration

### Essential Parameters

```python
chat_EXAI-WS(
    prompt="Your detailed question here",
    model="kimi-k2-0905-preview",  # ALWAYS specify explicitly
    use_websearch=True,  # Enable for current information
    continuation_id="3a894585-2fea-4e02-b5de-9b81ad5999e0",  # For multi-turn
    files=["c:\\Project\\file.py"]  # Absolute paths only
)
```

### Critical Configuration Notes

1. **Always Include Current Date**
   ```
   "Today is November 3, 2025 (Melbourne, Victoria, Australia timezone)"
   ```
   This forces K2 to use current information instead of training data.

2. **Model Selection**
   - Use `kimi-k2-0905-preview` (NOT `kimi-latest`)
   - K2 has superior reasoning capabilities
   - Worth the extra latency for complex problems

3. **Web Search**
   - Enable when you need current documentation
   - Enable when researching framework updates
   - Disable for internal codebase analysis (saves overhead)

4. **Continuation ID**
   - Save from each response: `continuation_offer.continuation_id`
   - Reuse for follow-up questions (maintains context)
   - Track remaining exchanges (typically 15 total)

---

## 📁 File Handling Mastery

### Absolute Paths Only

❌ **WRONG:**
```python
files=["tools/workflow/base.py"]  # Relative path - WILL FAIL
```

✅ **CORRECT:**
```python
files=["c:\\Project\\EX-AI-MCP-Server\\tools\\workflow\\base.py"]
```

### Two File Attachment Approaches

#### Approach 1: Direct Embedding (Small Files <5KB)
```python
chat_EXAI-WS(
    prompt="Analyze this script",
    files=["c:\\Project\\script.py"],  # Embedded directly
    model="kimi-k2-0905-preview"
)
```

#### Approach 2: Upload First (Large Files >5KB)
```python
# Step 1: Upload
upload_result = kimi_upload_files(
    files=["c:\\Project\\large_file.py"]
)

# Step 2: Reference in chat
kimi_chat_with_files(
    prompt="Analyze this large file",
    file_ids=upload_result['file_ids']
)
```

### Smart Attachment Strategy

**DON'T preload everything:**
```python
# ❌ BAD: Wastes context window
files=[
    "c:\\Project\\file1.py",
    "c:\\Project\\file2.py",
    "c:\\Project\\file3.py",
    # ... 20 more files
]
```

**DO let K2 request what it needs:**
```python
# ✅ GOOD: K2 will ask for specific files
prompt="""
We're debugging file upload failures. 
What specific files should I provide for analysis?
"""
```

---

## 💬 Effective Prompting Patterns

### Pattern 1: Diagnostic Approach

```
Today is November 3, 2025.

We're seeing [SPECIFIC SYMPTOM] in the Docker logs.

Symptoms:
- [Concrete observation 1]
- [Concrete observation 2]

What we've tried:
- [Action 1] → [Result]
- [Action 2] → [Result]

Question: What should we investigate next to isolate the root cause?

Attached files:
- docker_logs_latest.txt (last 1000 lines)
- relevant_script.py (suspected issue)
```

### Pattern 2: Script Request

```
Today is November 3, 2025.

We need a script to [SPECIFIC ACTION] that handles:
- [Edge case 1]
- [Edge case 2]
- [Error condition 3]

Requirements:
- Must work in Docker container (Linux)
- Must handle Supabase connection failures gracefully
- Must log to structured format

Can you provide the implementation?
```

### Pattern 3: Analysis Request

```
Today is November 3, 2025.

Please analyze the attached [FILE/LOG] and identify:
1. [Specific pattern to look for]
2. [Specific issue to diagnose]
3. [Specific recommendation needed]

Context:
- [Background information]
- [Current system state]

Attached: [file_name.ext]
```

### Pattern 4: Continuation

```
Today is November 3, 2025.

Continuing from our previous discussion about [TOPIC]...

You recommended [ACTION]. We implemented it and observed:
- [Result 1]
- [Result 2]

New question: [FOLLOW-UP QUESTION]
```

---

## 🔄 Continuation Workflow

### Saving Continuation ID

```python
result = chat_EXAI-WS(
    prompt="Initial question",
    model="kimi-k2-0905-preview"
)

# Save this for next call
continuation_id = result['continuation_offer']['continuation_id']
remaining_turns = result['continuation_offer']['remaining_turns']
```

### Using Continuation ID

```python
result = chat_EXAI-WS(
    prompt="Follow-up question",
    continuation_id="3a894585-2fea-4e02-b5de-9b81ad5999e0",
    model="kimi-k2-0905-preview"
)
```

### Tracking Exchange Count

- K2 typically allows **15 total exchanges** per conversation
- Each call decrements the counter
- When you hit 0, start a new conversation
- **Handover strategy:** Create markdown summary before running out

---

## 🎓 Advanced Techniques

### Multi-File Analysis

```python
# Upload related files separately
chat_EXAI-WS(
    prompt="""
    Analyze the interaction between these components:
    1. base_workflow.py - Base class
    2. refactor.py - Implementation
    3. orchestration.py - Caller
    
    What's the data flow and where could failures occur?
    """,
    files=[
        "c:\\Project\\tools\\workflows\\base_workflow.py",
        "c:\\Project\\tools\\workflows\\refactor.py",
        "c:\\Project\\tools\\workflow\\orchestration.py"
    ],
    model="kimi-k2-0905-preview"
)
```

### Log Interrogation

```python
chat_EXAI-WS(
    prompt="""
    Today is November 3, 2025.
    
    Please create a Python script that:
    1. Parses Docker logs for Supabase connection errors
    2. Extracts timestamps, error codes, and stack traces
    3. Groups errors by type
    4. Outputs structured JSON
    
    The script should handle malformed log lines gracefully.
    """,
    files=["c:\\Project\\docker_logs_latest.txt"],
    model="kimi-k2-0905-preview"
)
```

### Database Query Generation

```python
chat_EXAI-WS(
    prompt="""
    Today is November 3, 2025.
    
    We need a Supabase query to:
    1. Find all messages in last 24 hours
    2. Filter by tool_name='refactor'
    3. Check if content_length > 100 bytes
    4. Group by conversation_id
    
    Include proper error handling for connection failures.
    """,
    model="kimi-k2-0905-preview",
    use_websearch=True  # Get current Supabase API docs
)
```

---

## ⚠️ Critical Warnings

### 1. Never Use Relative Paths
```python
# ❌ WILL FAIL
files=["tools/workflow/base.py"]

# ✅ CORRECT
files=["c:\\Project\\EX-AI-MCP-Server\\tools\\workflow\\base.py"]
```

### 2. Don't Burn Exchanges on Preamble
```python
# ❌ WASTES EXCHANGE
prompt="Hi K2! Hope you're doing well. I have a question about..."

# ✅ GET TO THE POINT
prompt="Today is November 3, 2025. We're seeing upload failures. What should we check?"
```

### 3. Avoid Context Overload
```python
# ❌ TOO MUCH
prompt="""
Here's our entire codebase structure...
[500 lines of file listings]
Now, can you help with a small bug?
"""

# ✅ TARGETED
prompt="""
We have a bug in file upload. 
What specific files should I provide for diagnosis?
"""
```

### 4. Track Your Continuation ID
```python
# ❌ LOSES CONTEXT
# Calling without continuation_id after previous exchange

# ✅ MAINTAINS CONTEXT
continuation_id = "3a894585-2fea-4e02-b5de-9b81ad5999e0"
```

### 5. Specify Model Explicitly
```python
# ❌ MIGHT GET WRONG MODEL
chat_EXAI-WS(prompt="Complex analysis")

# ✅ GUARANTEED K2
chat_EXAI-WS(
    prompt="Complex analysis",
    model="kimi-k2-0905-preview"
)
```

---

## 📊 Current K2 Conversation Status

**Continuation ID:** `3a894585-2fea-4e02-b5de-9b81ad5999e0`  
**Exchanges Remaining:** 14 (as of 2025-11-03)  
**Topic:** Production readiness validation & systemic issue analysis

---

## 🎯 Best Practices Summary

1. **Always include current date** in prompt
2. **Use absolute paths** for all files
3. **Let K2 request** what it needs (don't preload)
4. **Track continuation_id** for multi-turn conversations
5. **Be specific** in questions (avoid vague requests)
6. **Enable web search** when researching current information
7. **Save K2's recommendations** to markdown for handover
8. **Validate K2's suggestions** with actual testing

---

## 📝 Example: Complete K2 Consultation

```python
result = chat_EXAI-WS(
    prompt="""
    Today is November 3, 2025 (Melbourne, Victoria, Australia timezone).
    
    We're investigating file upload failures in smart_file_query tool.
    
    Symptoms:
    - Kimi provider returns no file_id (100% failure rate)
    - GLM provider also fails
    - No error messages in logs
    
    What we've tried:
    - Verified file paths are absolute
    - Checked file sizes (<5KB)
    - Tested with different file types
    
    Question: What diagnostic script should we create to capture 
    the actual HTTP response from Kimi/GLM upload APIs?
    
    Attached files:
    - smart_file_query.py (current implementation)
    - docker_logs_latest.txt (last 1000 lines)
    """,
    files=[
        "c:\\Project\\EX-AI-MCP-Server\\tools\\simple\\smart_file_query.py",
        "c:\\Project\\EX-AI-MCP-Server\\docker_logs_latest.txt"
    ],
    model="kimi-k2-0905-preview",
    use_websearch=True,
    continuation_id="3a894585-2fea-4e02-b5de-9b81ad5999e0"
)

# Save for next exchange
next_continuation_id = result['continuation_offer']['continuation_id']
remaining = result['continuation_offer']['remaining_turns']
print(f"Continuation ID: {next_continuation_id}")
print(f"Remaining exchanges: {remaining}")
```

---

**Remember:** K2 is your strategic partner, not just an information retrieval tool. Use it for complex reasoning, architectural decisions, and systematic problem-solving.


