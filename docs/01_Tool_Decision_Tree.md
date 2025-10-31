# EXAI Tool Decision Tree

**Last Updated:** 2025-10-29  
**Purpose:** Comprehensive guide for selecting the right tool for any task

---

## 🎯 **QUICK REFERENCE**

### **File Operations → `smart_file_query`**
```
smart_file_query
├── Upload files
├── Query content
├── Chat with files
├── Manage files
└── Automatic deduplication
```

### **Code Workflows**
```
Code Analysis → analyze
Code Review → codereview
Debugging → debug
Refactoring → refactor
Test Generation → testgen
```

### **Advanced Scenarios**
```
Security Audit → secaudit
Documentation → docgen
Code Tracing → tracer
Multi-Agent → consensus
Pre-Commit → precommit
```

---

## 📊 **DETAILED DECISION TREE**

### **1. FILE OPERATIONS**

**Question:** Do you need to work with files?

```
YES → Use smart_file_query
│
├─ Upload file?
│  └─ smart_file_query(file_path="...", question="...")
│
├─ Query file content?
│  └─ smart_file_query(file_path="...", question="...")
│
├─ Chat with multiple files?
│  └─ Call smart_file_query multiple times
│
└─ Manage files (list/delete)?
   └─ Use kimi_manage_files (advanced)

⚠️ DEPRECATED TOOLS (DO NOT USE):
   ❌ kimi_upload_files → Use smart_file_query
   ❌ kimi_chat_with_files → Use smart_file_query
   ❌ glm_upload_file → Use smart_file_query
   ❌ glm_multi_file_chat → Use smart_file_query
```

---

### **2. CODE ANALYSIS**

**Question:** Do you need to understand code structure/architecture?

```
YES → Use analyze
│
├─ Understand architecture?
│  └─ analyze(analysis_type="architecture", ...)
│
├─ Assess performance?
│  └─ analyze(analysis_type="performance", ...)
│
├─ Check security?
│  └─ analyze(analysis_type="security", ...)
│
├─ Evaluate code quality?
│  └─ analyze(analysis_type="quality", ...)
│
└─ General analysis?
   └─ analyze(analysis_type="general", ...)
```

---

### **3. CODE REVIEW**

**Question:** Do you need to review code for issues?

```
YES → Use codereview
│
├─ Full review (bugs + security + performance)?
│  └─ codereview(review_type="full", ...)
│
├─ Security-focused review?
│  └─ codereview(review_type="security", ...)
│
├─ Performance-focused review?
│  └─ codereview(review_type="performance", ...)
│
└─ Quick review?
   └─ codereview(review_type="quick", ...)
```

---

### **4. DEBUGGING**

**Question:** Do you need to find root cause of an issue?

```
YES → Use debug
│
├─ Complex bug (multi-step investigation)?
│  └─ debug(
│       step="Investigate login failure",
│       hypothesis="JWT token expiration",
│       confidence="exploring",
│       ...
│     )
│
├─ Simple bug (quick fix)?
│  └─ debug(
│       step="Fix null pointer exception",
│       confidence="high",
│       ...
│     )
│
└─ Performance issue?
   └─ debug(
        step="Investigate slow query",
        hypothesis="Missing database index",
        ...
      )
```

---

### **5. REFACTORING**

**Question:** Do you need to improve code quality?

```
YES → Use refactor
│
├─ Identify code smells?
│  └─ refactor(refactor_type="codesmells", ...)
│
├─ Decompose large functions/classes?
│  └─ refactor(refactor_type="decompose", ...)
│
├─ Modernize legacy code?
│  └─ refactor(refactor_type="modernize", ...)
│
└─ Reorganize code structure?
   └─ refactor(refactor_type="organization", ...)
```

---

### **6. TEST GENERATION**

**Question:** Do you need to generate tests?

```
YES → Use testgen
│
├─ Unit tests for specific function?
│  └─ testgen(
│       step="Generate tests for User.login()",
│       ...
│     )
│
├─ Integration tests?
│  └─ testgen(
│       step="Generate integration tests for payment flow",
│       ...
│     )
│
└─ Edge case tests?
   └─ testgen(
        step="Generate edge case tests for input validation",
        ...
      )
```

---

### **7. PLANNING & REASONING**

**Question:** Do you need to plan or reason through a problem?

```
Simple planning?
└─ Use planner
   └─ planner(
        step="Break down task into phases",
        step_number=1,
        total_steps=3,
        ...
      )

Deep reasoning needed?
└─ Use thinkdeep
   └─ thinkdeep(
        step="Evaluate caching strategies",
        findings="Need to balance performance vs complexity",
        ...
      )

General question?
└─ Use chat
   └─ chat(prompt="How do I implement OAuth2?")
```

---

### **8. ADVANCED SCENARIOS**

**Question:** Do you need specialized functionality?

```
Security audit?
└─ Use secaudit
   └─ secaudit(
        audit_focus="owasp",
        threat_level="high",
        ...
      )

Documentation generation?
└─ Use docgen
   └─ docgen(
        step="Generate API documentation",
        ...
      )

Code tracing?
└─ Use tracer
   └─ tracer(
        trace_mode="precision",
        target_description="Trace User.login() execution",
        ...
      )

Multi-agent coordination?
└─ Use consensus
   └─ consensus(
        step="Evaluate database migration proposal",
        models=[{"model": "glm-4.6"}, {"model": "kimi-k2-0905-preview"}],
        ...
      )

Pre-commit validation?
└─ Use precommit
   └─ precommit(
        step="Validate changes before commit",
        path="/mnt/project/EX-AI-MCP-Server",
        ...
      )
```

---

## 🔄 **WORKFLOW COMBINATIONS**

### **Workflow 1: New Feature Development**
```
1. planner → Plan feature implementation
2. analyze → Understand existing codebase
3. codereview → Review implementation
4. testgen → Generate tests
5. precommit → Validate before commit
```

### **Workflow 2: Bug Investigation**
```
1. debug → Find root cause
2. codereview → Review affected code
3. testgen → Create regression tests
4. precommit → Validate fix
```

### **Workflow 3: Code Quality Improvement**
```
1. analyze → Assess current state
2. refactor → Identify improvements
3. codereview → Validate changes
4. testgen → Ensure coverage
```

### **Workflow 4: Security Audit**
```
1. secaudit → Comprehensive security scan
2. analyze → Understand security posture
3. codereview → Review vulnerable code
4. testgen → Create security tests
```

---

## 📋 **TOOL SELECTION MATRIX**

| Task Type | Primary Tool | Secondary Tool | Advanced Tool |
|-----------|-------------|----------------|---------------|
| **File Operations** | smart_file_query | - | kimi_manage_files |
| **Code Analysis** | analyze | thinkdeep | tracer |
| **Code Review** | codereview | analyze | secaudit |
| **Debugging** | debug | tracer | thinkdeep |
| **Refactoring** | refactor | analyze | codereview |
| **Testing** | testgen | codereview | - |
| **Planning** | planner | thinkdeep | consensus |
| **Security** | secaudit | codereview | analyze |
| **Documentation** | docgen | analyze | - |
| **Pre-Commit** | precommit | codereview | testgen |

---

## ⚠️ **ANTI-PATTERNS**

### **❌ DON'T DO THIS:**

**1. Using old file upload tools**
```python
# ❌ WRONG
kimi_upload_files(files=["file.py"])
kimi_chat_with_files(file_ids=["..."], prompt="...")

# ✅ CORRECT
smart_file_query(file_path="/mnt/project/file.py", question="...")
```

**2. Skipping planning for complex tasks**
```python
# ❌ WRONG - Jump straight to implementation
analyze(step="Implement entire authentication system", ...)

# ✅ CORRECT - Plan first
planner(step="Break down authentication implementation", ...)
```

**3. Using wrong tool for the job**
```python
# ❌ WRONG - Using analyze for code review
analyze(step="Review code for bugs", ...)

# ✅ CORRECT - Use codereview
codereview(step="Review code for bugs", ...)
```

**4. Not using continuation_id for multi-turn**
```python
# ❌ WRONG - Lose context between calls
debug(step="Investigate issue", ...)
debug(step="Continue investigation", ...)  # Lost context!

# ✅ CORRECT - Maintain context
debug(step="Investigate issue", continuation_id="abc123", ...)
debug(step="Continue investigation", continuation_id="abc123", ...)
```

---

## 💡 **PRO TIPS**

### **1. Start Simple**
- Begin with Essential + Core tools (10 total)
- Only use Advanced tools when specifically needed
- Don't overcomplicate with too many tools

### **2. Use Continuation IDs**
- Maintain context across multiple tool calls
- Reuse same ID for related operations
- Create new ID for new topics

### **3. Leverage smart_file_query**
- ONE tool for ALL file operations
- Automatic deduplication
- Intelligent provider selection
- No need to manage uploads manually

### **4. Set Confidence Appropriately**
- Start at "exploring" or "low"
- Progress to "medium" with evidence
- Use "high" or "very_high" when confident
- Only use "certain" when 100% sure

### **5. Use Web Search Selectively**
- Enable for analyze and thinkdeep (benefits from external docs)
- Disable for debug and codereview (adds overhead)
- Default: use_websearch=true for research, false for code work

---

## 🔗 **NEXT STEPS**

1. **Read:** `00_Quick_Start_Guide.md` - Get started in 5 minutes
2. **Read:** `02_SDK_Integration.md` - Complete tool reference
3. **Practice:** Try the workflows above
4. **Explore:** Advanced tools when needed

---

**Remember:** The right tool makes the job easier. When in doubt, start with the Core tools - they cover 80% of use cases.

