# External Agent Integration Guide - EXAI-MCP System

**Date:** 2025-10-29  
**Purpose:** Complete guide for external Claude applications and AI agents using EXAI-MCP

---

## 🚀 **QUICK START**

### **Prerequisites**
- Access to EXAI-MCP server (default: localhost:8079 for VSCode)
- Understanding of MCP (Model Context Protocol)
- Basic knowledge of tool calling patterns

### **First Steps**
1. Connect to EXAI-MCP server via WebSocket
2. List available tools using MCP protocol
3. Start with `chat_EXAI-WS` for simple queries
4. Progress to workflow tools for complex tasks

---

## 🛠️ **AVAILABLE TOOLS**

### **Essential Tools** (Always Available)
- **status_EXAI-WS** - Check system health and provider status
- **chat_EXAI-WS** - General chat and brainstorming
- **planner_EXAI-WS** - Task planning and breakdown

### **Core Workflow Tools** (Recommended)
- **analyze_EXAI-WS** - Code analysis and architectural assessment
- **codereview_EXAI-WS** - Code review with expert validation
- **debug_EXAI-WS** - Debugging and root cause analysis
- **refactor_EXAI-WS** - Refactoring opportunities analysis
- **testgen_EXAI-WS** - Test generation
- **thinkdeep_EXAI-WS** - Deep reasoning and complex problem analysis
- **smart_file_query** - Unified file operations (RECOMMENDED)

### **Advanced Tools** (Optional)
- **consensus_EXAI-WS** - Multi-model consensus
- **docgen_EXAI-WS** - Documentation generation
- **secaudit_EXAI-WS** - Security audit
- **tracer_EXAI-WS** - Code tracing
- **precommit_EXAI-WS** - Pre-commit validation

---

## 📁 **FILE HANDLING**

### **CRITICAL: Path Requirements**

**✅ ACCESSIBLE PATHS:**
- `/mnt/project/EX-AI-MCP-Server/*` (main project)
- `/mnt/project/Personal_AI_Agent/*` (AI agent project)

**❌ NOT ACCESSIBLE:**
- `/mnt/project/Mum/*`
- `/mnt/project/Documents/*`
- `c:\Users\...` (Windows paths)
- Any other paths

**💡 TIP:** If you need to analyze external files, they must be copied into an accessible directory first.

### **Recommended: Use smart_file_query**

```python
# BEST PRACTICE - Use smart_file_query for ALL file operations
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",
    question="Analyze this code for security issues",
    provider="auto"  # Automatic provider selection
)
```

**Benefits:**
- Automatic SHA256-based deduplication
- Intelligent provider selection (Kimi vs GLM)
- Automatic fallback on failure
- Centralized Supabase tracking
- Single unified interface

### **Legacy File Handling** (Still Available)

**Small Files (<5KB):**
```python
chat_EXAI-WS(
    prompt="Review this code",
    files=["c:\\Project\\EX-AI-MCP-Server\\file.py"],  # Windows paths OK for chat
    model="glm-4.6"
)
```

**Large Files (>5KB):**
```python
# Step 1: Upload (use Linux container paths!)
upload_result = kimi_upload_files(
    files=["/mnt/project/EX-AI-MCP-Server/large_file.py"]
)

# Step 2: Chat
kimi_chat_with_files(
    prompt="Review this code",
    file_ids=[upload_result[0]["file_id"]],
    model="kimi-k2-0905-preview"
)
```

---

## ⚠️ **CIRCUIT BREAKER BEHAVIOR**

### **What is the Circuit Breaker?**
A safety mechanism that prevents infinite loops when workflow tools aren't making progress.

### **When Does It Trigger?**
- **Exploring/Low confidence:** 3 consecutive steps with no progress
- **Medium confidence:** 5 consecutive steps with no progress
- **High/Very High/Certain:** Never triggers (stable confidence is good)

### **How to Avoid Circuit Breaker:**

**1. Increase Confidence When Making Progress:**
```python
# ❌ DON'T: Stay at 'medium' when you're actually making progress
debug_EXAI-WS(
    step="Found root cause and implemented fix",
    confidence="medium"  # Too low!
)

# ✅ DO: Increase confidence when you have strong evidence
debug_EXAI-WS(
    step="Found root cause and implemented fix",
    confidence="high"  # Appropriate!
)
```

**2. Provide More Context:**
```python
# ✅ DO: Include relevant files and specific details
debug_EXAI-WS(
    step="Investigating authentication bug",
    relevant_files=["/mnt/project/EX-AI-MCP-Server/src/auth.py"],
    findings="JWT validation missing expiry check on line 42",
    hypothesis="Authentication bypass due to missing token expiration",
    confidence="high"
)
```

**3. Break Tasks Into Smaller Steps:**
```python
# ❌ DON'T: Try to solve everything in one step
debug_EXAI-WS(
    step="Fix all authentication issues",
    confidence="medium"
)

# ✅ DO: Focus on specific, achievable goals
debug_EXAI-WS(
    step="Identify root cause of JWT validation failure",
    confidence="high"
)
```

**4. Use chat_EXAI-WS for Manual Guidance:**
```python
# If workflow tools aren't working, switch to chat
chat_EXAI-WS(
    prompt="I'm stuck debugging this authentication issue. Can you help me understand the JWT validation flow?",
    files=["/mnt/project/EX-AI-MCP-Server/src/auth.py"],
    model="glm-4.6"
)
```

**5. Increase Thinking Mode:**
```python
# For complex problems, use higher thinking modes
debug_EXAI-WS(
    step="Analyzing complex race condition",
    thinking_mode="high",  # or "max" for very complex issues
    confidence="medium"
)
```

### **Circuit Breaker Error Message:**
```
🔧 TROUBLESHOOTING FOR EXTERNAL AGENTS:
  1. Increase confidence level in your next call (e.g., 'high' instead of 'medium')
  2. Provide more specific context or relevant files
  3. Break task into smaller, more focused steps
  4. Use chat_EXAI-WS for manual guidance instead of workflow tools
  5. Increase thinking_mode for deeper analysis (e.g., 'high' or 'max')

💡 TIP: If you're making progress, set confidence='high' to bypass circuit breaker.
```

---

## 🎯 **CONFIDENCE LEVELS GUIDE**

| Level | When to Use | Circuit Breaker |
|-------|-------------|-----------------|
| **exploring** | Just starting, forming initial hypotheses | Triggers after 3 steps |
| **low** | Early investigation, limited evidence | Triggers after 3 steps |
| **medium** | Some solid evidence, partial understanding | Triggers after 5 steps |
| **high** | Strong evidence, clear understanding | Never triggers |
| **very_high** | Comprehensive understanding, ready to conclude | Never triggers |
| **almost_certain** | Near complete confidence | Never triggers |
| **certain** | Complete confidence, analysis is conclusive | Never triggers |

**💡 PROGRESSION TIP:** Start at 'exploring' or 'low', progress to 'medium' once you have solid evidence, then use 'high' or 'very_high' when you have clear answers.

---

## 🔄 **CONVERSATION CONTINUITY**

### **Use continuation_id for Multi-Turn Conversations:**

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
- ✅ Works across different tools

---

## 🤖 **MODEL SELECTION**

### **GLM Models (Z.ai)**
| Model | Speed | Cost | Use Case |
|-------|-------|------|----------|
| `glm-4.5-flash` | ⚡⚡⚡ | FREE | Quick queries, simple tasks |
| `glm-4.5` | ⚡⚡ | PAID | Standard tasks |
| `glm-4.6` | ⚡ | PAID | Complex reasoning, code review |

### **Kimi Models (Moonshot)**
| Model | Speed | Cost | Context | Use Case |
|-------|-------|------|---------|----------|
| `kimi-k2-turbo-preview` | ⚡⚡ | PAID | 128k | Fast responses |
| `kimi-k2-0905-preview` | ⚡ | PAID | 200k+ | Large context, file analysis |

### **Model Selection Decision Tree:**
- **Quick question?** → `glm-4.5-flash` (FREE)
- **Complex reasoning?** → `glm-4.6`
- **Large files/context?** → `kimi-k2-0905-preview`
- **Cost-sensitive?** → `glm-4.5-flash` (FREE)

---

## ❌ **COMMON MISTAKES TO AVOID**

### **1. Using Windows Paths for File Uploads**
```python
# ❌ WRONG
kimi_upload_files(files=["c:\\Project\\EX-AI-MCP-Server\\file.py"])

# ✅ CORRECT
kimi_upload_files(files=["/mnt/project/EX-AI-MCP-Server/file.py"])
```

### **2. Staying at Low Confidence When Making Progress**
```python
# ❌ WRONG
debug_EXAI-WS(
    step="Found root cause and implemented fix",
    confidence="medium"  # Circuit breaker will trigger!
)

# ✅ CORRECT
debug_EXAI-WS(
    step="Found root cause and implemented fix",
    confidence="high"  # Appropriate confidence level
)
```

### **3. Not Using continuation_id for Multi-Turn**
```python
# ❌ WRONG
chat_EXAI-WS(prompt="Explain X")
chat_EXAI-WS(prompt="How does that relate to Y?")  # Lost context!

# ✅ CORRECT
response1 = chat_EXAI-WS(prompt="Explain X")
continuation_id = response1["continuation_offer"]["continuation_id"]
chat_EXAI-WS(prompt="How does that relate to Y?", continuation_id=continuation_id)
```

### **4. Manually Reading Files and Embedding in Prompts**
```python
# ❌ WRONG
content = view("file.py")
chat_EXAI-WS(prompt=f"Review this code: {content}")  # Wastes tokens!

# ✅ CORRECT
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/file.py",
    question="Review this code"
)
```

---

## 🆘 **TROUBLESHOOTING**

### **Error: FileNotFoundError**
**Cause:** File path is outside accessible directories

**Solution:**
1. Check if file is in `/mnt/project/EX-AI-MCP-Server/` or `/mnt/project/Personal_AI_Agent/`
2. If not, copy file to accessible directory
3. Use correct Linux container path format

### **Error: Circuit Breaker Triggered**
**Cause:** Confidence stagnant for too many steps

**Solution:**
1. Increase confidence level if making progress
2. Provide more specific context
3. Break task into smaller steps
4. Switch to chat_EXAI-WS for manual guidance

### **Error: AI Auditor Processing Event**
**Cause:** Internal monitoring system issue (now fixed)

**Solution:**
- This error has been fixed in the latest version
- If you still see it, report to system administrator

---

## 📚 **ADDITIONAL RESOURCES**

- **Tool Descriptions:** Check individual tool schemas for detailed parameters
- **Model List:** Run `listmodels_EXAI-WS` to see all available models
- **System Status:** Run `status_EXAI-WS` to check system health
- **File Handling Analysis:** See `docs/05_CURRENT_WORK/2025-10-29/EXTERNAL_AGENT_ISSUES_AND_FIXES.md`

---

## ✅ **SUCCESS CHECKLIST**

Before using EXAI-MCP, ensure you:
- [ ] Understand accessible file paths
- [ ] Know how to use smart_file_query
- [ ] Understand circuit breaker behavior
- [ ] Know when to increase confidence levels
- [ ] Can use continuation_id for multi-turn conversations
- [ ] Have selected appropriate model for your task
- [ ] Know how to avoid common mistakes

---

**For Support:** Check Docker logs or contact system administrator

**Last Updated:** 2025-10-29

