# 🚀 EXAI Model Selection - Quick Reference

**For:** EX-AI MCP Server Development  
**Version:** 2.1.0  
**Date:** 2025-11-04

---

## 📊 MODEL SELECTION MATRIX

| Task Type | Model | Tokens | Cost | When to Use |
|-----------|-------|--------|------|-------------|
| **Quick Query** | glm-4.5-flash | 8K | 💰 Low | Default choice, fast responses |
| **Complex Analysis** | glm-4.6 | 16K | 💰💰 Medium | Architecture, design decisions |
| **File Operations** | kimi-k2-0905-preview | 128K | 💰💰 Medium | File upload, long context |
| **Deep Debugging** | kimi-thinking-preview | 128K | 💰💰💰 High | Extended reasoning, root cause |

---

## 🎯 DECISION TREE

```
START
  │
  ├─ Has files to analyze? ──YES──> kimi-k2-0905-preview
  │                          NO
  │                          │
  ├─ Complex problem? ───────YES──> glm-4.6 or kimi-thinking-preview
  │                          NO
  │                          │
  └─ Simple query ───────────────> glm-4.5-flash (DEFAULT)
```

---

## 💡 USAGE EXAMPLES

### **glm-4.5-flash** (Default - Fast & Cheap)
```python
# Quick questions
chat_EXAI-WS(
    prompt="What's the difference between GLM and Kimi?",
    model="glm-4.5-flash"
)

# Simple explanations
chat_EXAI-WS(
    prompt="Explain how the router service works",
    model="glm-4.5-flash"
)
```

### **glm-4.6** (Complex Analysis)
```python
# Architectural decisions
chat_EXAI-WS(
    prompt="Should we use WebSocket or Supabase Realtime for event distribution?",
    model="glm-4.6",
    use_websearch=True  # Get current best practices
)

# Design patterns
chat_EXAI-WS(
    prompt="Analyze the thin orchestrator pattern in request_handler.py",
    model="glm-4.6"
)
```

### **kimi-k2-0905-preview** (File Specialist)
```python
# File analysis (small files <5KB)
chat_EXAI-WS(
    prompt="Review this code for security issues",
    files=["C:/Project/EX-AI-MCP-Server/tools/chat.py"],
    model="kimi-k2-0905-preview"
)

# Large files (>5KB) - use upload workflow
upload_result = kimi_upload_files(
    files=["C:/Project/EX-AI-MCP-Server/src/server/handlers/request_handler.py"]
)
kimi_chat_with_files(
    prompt="Analyze the request handling flow",
    file_ids=upload_result['file_ids']
)

# Multi-turn with continuation
result1 = chat_EXAI-WS(
    prompt="Analyze the authentication system",
    files=["C:/Project/EX-AI-MCP-Server/src/auth/jwt_handler.py"],
    model="kimi-k2-0905-preview"
)
result2 = chat_EXAI-WS(
    prompt="Now check for security vulnerabilities",
    continuation_id=result1['continuation_id'],
    model="kimi-k2-0905-preview"
)
```

### **kimi-thinking-preview** (Deep Reasoning)
```python
# Complex debugging
debug_EXAI-WS(
    step="Investigate WebSocket daemon deadlock",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="Daemon hangs when processing concurrent requests",
    relevant_files=["C:/Project/EX-AI-MCP-Server/src/daemon/ws_daemon.py"],
    model="kimi-thinking-preview"
)

# Multi-step problem solving
thinkdeep_EXAI-WS(
    step="Analyze the root cause of token overflow in workflow tools",
    step_number=1,
    total_steps=5,
    next_step_required=True,
    findings="Workflow tools exceed 8000 token limit when using large files",
    model="kimi-thinking-preview",
    thinking_mode="high"
)
```

---

## 🔧 BEST PRACTICES

### **1. Start Cheap, Escalate When Needed**
```python
# ✅ GOOD - Start with glm-4.5-flash
result = chat_EXAI-WS(prompt="Quick question", model="glm-4.5-flash")

# If answer is insufficient, escalate
result = chat_EXAI-WS(
    prompt="I need deeper analysis on this",
    continuation_id=result['continuation_id'],
    model="glm-4.6"  # Escalate to more powerful model
)
```

### **2. Use Continuation IDs**
```python
# ✅ GOOD - Maintain context across calls
id1 = chat_EXAI-WS(prompt="Analyze X", model="glm-4.6")['continuation_id']
id2 = chat_EXAI-WS(prompt="Now Y", continuation_id=id1, model="glm-4.6")['continuation_id']
id3 = chat_EXAI-WS(prompt="Finally Z", continuation_id=id2, model="glm-4.6")['continuation_id']

# ❌ BAD - Lose context, waste tokens
chat_EXAI-WS(prompt="Analyze X", model="glm-4.6")
chat_EXAI-WS(prompt="Now Y", model="glm-4.6")  # No context from previous call
chat_EXAI-WS(prompt="Finally Z", model="glm-4.6")  # No context from previous calls
```

### **3. File Size Awareness**
```python
# Files <5KB - Embed directly
chat_EXAI-WS(
    prompt="Review this",
    files=["small_file.py"],  # <5KB
    model="kimi-k2-0905-preview"
)

# Files >5KB - Upload first (70-80% token savings)
upload = kimi_upload_files(files=["large_file.py"])  # >5KB
kimi_chat_with_files(prompt="Review this", file_ids=upload['file_ids'])
```

### **4. Web Search When Needed**
```python
# ✅ GOOD - Specify current date for latest info
chat_EXAI-WS(
    prompt="Today is November 4, 2025. What are the latest MCP protocol updates?",
    use_websearch=True,
    model="glm-4.6"
)

# ❌ BAD - Model uses outdated training data
chat_EXAI-WS(
    prompt="What are the latest MCP protocol updates?",
    use_websearch=False,  # Will use old knowledge
    model="glm-4.6"
)
```

---

## 💰 COST OPTIMIZATION

### **Token Usage Comparison**

| Scenario | Method | Tokens | Cost |
|----------|--------|--------|------|
| Small file (<5KB) | Embed in prompt | ~5K | 💰 Low |
| Large file (50KB) | Embed in prompt | ~50K | 💰💰💰 High |
| Large file (50KB) | kimi_upload_files | ~10K | 💰 Low |
| **Savings** | **Upload vs Embed** | **80%** | **80%** |

### **Model Cost Comparison**

| Model | Cost/1K Tokens | Relative Cost |
|-------|----------------|---------------|
| glm-4.5-flash | $0.001 | 1x (baseline) |
| glm-4.6 | $0.003 | 3x |
| kimi-k2-0905-preview | $0.002 | 2x |
| kimi-thinking-preview | $0.005 | 5x |

**Recommendation:** Default to glm-4.5-flash, escalate only when necessary.

---

## 🎯 WORKFLOW TOOL RECOMMENDATIONS

| Tool | Recommended Model | Reason |
|------|-------------------|--------|
| **chat** | glm-4.5-flash | Quick queries, general discussion |
| **analyze** | glm-4.6 | Architectural assessment |
| **codereview** | kimi-k2-0905-preview | File-based review, long context |
| **debug** | kimi-thinking-preview | Extended reasoning, root cause |
| **thinkdeep** | kimi-thinking-preview | Multi-step analysis |
| **testgen** | glm-4.6 | Test strategy planning |
| **refactor** | glm-4.6 | Refactoring strategy |
| **secaudit** | kimi-k2-0905-preview | Security review with files |
| **precommit** | kimi-k2-0905-preview | Change validation with files |

---

## 📝 QUICK TIPS

1. **Default to glm-4.5-flash** - Fast and cheap for most queries
2. **Use continuation_id** - Maintain context, save tokens
3. **Upload large files** - 70-80% token savings
4. **Enable web search** - Get current information when needed
5. **Absolute paths always** - Never clip or shorten file paths
6. **Escalate when stuck** - glm-4.5-flash → glm-4.6 → kimi-thinking-preview
7. **Kimi for files** - File persistence across conversations
8. **GLM for speed** - Faster responses, lower latency

---

## 🔗 RELATED DOCS

- **Full Guide:** `.claude/EXAI_MCP_CONFIGURATION_GUIDE.md`
- **Summary:** `.claude/CONFIGURATION_UPDATE_SUMMARY.md`
- **Settings:** `.claude/settings.local.json`
- **EXAI Tools:** `docs/02_Service_Components/EXAI_TOOL_DECISION_GUIDE.md`

---

**Last Updated:** 2025-11-04  
**Version:** 2.1.0  
**Project:** EX-AI MCP Server v2.3

