# EXAI Quick Start Guide

**Last Updated:** 2025-10-29  
**Purpose:** Get started with EXAI tools in 5 minutes

---

## 🎯 **YOUR FIRST 5 TOOLS**

These 5 tools cover 80% of all use cases:

### **1. `status` - Check System Health**
```python
status()
```
**Use when:** Starting a session, checking if system is operational

---

### **2. `planner` - Plan Your Approach**
```python
planner(
    step="Break down the task into phases",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="Initial analysis shows..."
)
```
**Use when:** Complex tasks requiring structured planning

---

### **3. `analyze` - Understand the Codebase**
```python
analyze(
    step="Analyze authentication system architecture",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Discovered JWT-based auth with Redis session storage"
)
```
**Use when:** Need to understand code structure, patterns, architecture

---

### **4. `codereview` - Review Code Changes**
```python
codereview(
    step="Review authentication changes for security issues",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Found potential SQL injection in login handler",
    relevant_files=["/mnt/project/src/auth/login.py"]
)
```
**Use when:** Reviewing code for bugs, security issues, code smells

---

### **5. `smart_file_query` - Handle All File Operations**
```python
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",
    question="Analyze this code for security issues"
)
```
**Use when:** Need to upload, query, or analyze files

**⭐ REPLACES:** kimi_upload_files, kimi_chat_with_files, glm_upload_file, glm_multi_file_chat

---

## 🚀 **QUICK DECISION TREE**

```
What do you need to do?

├─ Check system status?
│  └─ Use: status
│
├─ Plan complex task?
│  └─ Use: planner
│
├─ Understand codebase?
│  └─ Use: analyze
│
├─ Review code changes?
│  └─ Use: codereview
│
├─ Debug an issue?
│  └─ Use: debug
│
├─ Refactor code?
│  └─ Use: refactor
│
├─ Generate tests?
│  └─ Use: testgen
│
├─ Work with files?
│  └─ Use: smart_file_query
│
└─ Deep reasoning needed?
   └─ Use: thinkdeep
```

---

## 📚 **TOOL TIERS**

### **ESSENTIAL (3 tools)** - Always Available
- `status` - System status
- `chat` - Basic communication
- `planner` - Task planning

### **CORE (7 tools)** - Default Workflow
- `analyze` - Code analysis
- `codereview` - Code review
- `debug` - Debugging
- `refactor` - Refactoring
- `testgen` - Test generation
- `thinkdeep` - Deep reasoning
- `smart_file_query` - File operations

### **ADVANCED (7 tools)** - Specialized Scenarios
- `consensus` - Multi-agent coordination
- `docgen` - Documentation generation
- `secaudit` - Security auditing
- `tracer` - Code tracing
- `precommit` - Pre-commit validation
- `kimi_chat_with_tools` - Advanced Kimi features
- `glm_payload_preview` - GLM inspection

### **HIDDEN (16 tools)** - System/Diagnostic Only
- Diagnostic tools (health, version, activity, etc.)
- Deprecated file tools (use `smart_file_query` instead)

---

## 💡 **COMMON WORKFLOWS**

### **Workflow 1: Analyze New Codebase**
```python
# Step 1: Check system
status()

# Step 2: Plan approach
planner(step="Analyze codebase structure", ...)

# Step 3: Analyze code
analyze(step="Understand authentication system", ...)
```

### **Workflow 2: Debug Issue**
```python
# Step 1: Understand the problem
debug(
    step="Investigate login failure",
    hypothesis="JWT token expiration issue",
    ...
)

# Step 2: Review related code
codereview(step="Review auth token handling", ...)

# Step 3: Generate tests
testgen(step="Create tests for token expiration", ...)
```

### **Workflow 3: File Analysis**
```python
# Upload and analyze file in one step
smart_file_query(
    file_path="/mnt/project/src/config.py",
    question="Explain this configuration and identify security risks"
)
```

---

## ⚠️ **COMMON MISTAKES**

### **❌ DON'T:**
- Use old file upload tools (kimi_upload_files, glm_upload_file)
- Skip planning for complex tasks
- Use Windows paths (c:\Project\...)
- Call multiple tools when one tool can do it

### **✅ DO:**
- Use `smart_file_query` for ALL file operations
- Use `planner` for complex multi-step tasks
- Use Linux paths (/mnt/project/...)
- Start with `status` to check system health

---

## 🔗 **NEXT STEPS**

1. **Read:** `01_Tool_Decision_Tree.md` - Detailed tool selection guide
2. **Read:** `02_SDK_Integration.md` - Complete tool reference
3. **Practice:** Try the 5 essential tools above
4. **Explore:** Advanced tools when needed

---

## 📞 **NEED HELP?**

**For general questions:**
```python
chat(prompt="How do I analyze a React component for performance issues?")
```

**For complex reasoning:**
```python
thinkdeep(
    step="Evaluate best approach for implementing caching",
    findings="Need to balance performance vs complexity",
    ...
)
```

---

**Remember:** Start simple with Essential + Core tools (10 total). Advanced tools are there when you need them, but 80% of tasks can be done with the core set.

