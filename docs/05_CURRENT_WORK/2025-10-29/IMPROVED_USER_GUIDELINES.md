# Improved User Guidelines for AI Agents

**Date:** 2025-10-29  
**Purpose:** Enhanced guidelines for autonomous, effective AI agent operation

---

## 🎯 **CORE OPERATING PRINCIPLES**

### **1. Autonomous Investigation & Execution**
- **ALWAYS investigate first** using available tools (view, codebase-retrieval, Docker logs)
- **NEVER stop at first uncertainty** - use EXAI consultation to resolve ambiguity
- **NEVER ask user for clarification** when EXAI can provide the answer
- **Work persistently** through problems until fully resolved
- **Only escalate to user** when truly stuck after exhaustive investigation

### **2. EXAI Consultation Strategy**
**Two-Tier Approach:**
- **Tier 1:** Use EXAI workflow tools (debug/codereview/analyze/refactor) for structured investigation
- **Tier 2:** MANDATORY consultation with EXAI via chat_EXAI-WS to validate proposed solutions
- **Only proceed with implementation** after EXAI confirms approach is correct

**When to Consult EXAI:**
- ✅ Before implementing any fix or feature
- ✅ When choosing between multiple implementation strategies
- ✅ When uncertain about architectural decisions
- ✅ When debugging complex issues
- ✅ When validating test strategies
- ✅ After completing work (for final validation)

**How to Consult EXAI Effectively:**
- Use **GLM-4.6** with **high thinking mode** for critical analysis
- Enable **web search** for analyze/thinkdeep tools when external documentation helps
- Disable **web search** for debug/codereview tools (use codebase context)
- Pass **file paths** as parameters (let EXAI do heavy analytical work)
- Use **continuation_id** to maintain conversation context across multiple calls

### **3. Task Management (MANDATORY)**
- **ALWAYS use task manager tools** at the beginning and end of tasks
- **Break down complex work** into smaller, trackable tasks
- **Update task status** as you progress (NOT_STARTED → IN_PROGRESS → COMPLETE)
- **Mark tasks COMPLETE immediately** after finishing (don't batch updates)
- **Use tasks for planning** - if you don't track it, you'll forget it

---

## 📁 **FILE & PATH HANDLING**

### **Docker Environment Context (CRITICAL)**
- **EXAI runs in Docker** (Linux) while user operates in Windows
- **Accessible paths:**
  - `/mnt/project/EX-AI-MCP-Server/*` (main project)
  - `/mnt/project/Personal_AI_Agent/*` (AI agent project)
- **NOT accessible:** Any other paths (e.g., `/mnt/project/Mum/*`, `c:\Users\...`)

### **File Upload Strategy**
**Use smart_file_query for ALL file operations:**
```python
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",
    question="Analyze this code",
    provider="auto"  # Automatic provider selection
)
```

**Benefits:**
- Automatic SHA256-based deduplication
- Intelligent provider selection (Kimi vs GLM)
- Automatic fallback on failure
- Centralized Supabase tracking

**Legacy Tools (still available but prefer smart_file_query):**
- `<5KB`: Use `files` parameter in chat_EXAI-WS
- `>5KB`: Use kimi_upload_files + kimi_chat_with_files

---

## 🔧 **CODE QUALITY & ARCHITECTURE**

### **Script Size Limits**
- **Target:** Keep scripts under 500 lines
- **If exceeding:** Break into smaller, focused modules
- **Rationale:** Maintainability, readability, testability

### **Configuration Management**
- **NEVER hardcode** timeouts, credentials, or configuration
- **ALWAYS use** centralized .env configuration
- **Validate** that env vars activate their intended functionality
- **Document** all configuration options

### **Dependency Management**
- **ALWAYS use package managers** (npm, pip, cargo, etc.)
- **NEVER manually edit** package.json, requirements.txt, etc.
- **Add to requirements.txt** when manually installing packages
- **Validate changes** using EXAI consultation + Docker log review

---

## 📚 **DOCUMENTATION PRACTICES**

### **Markdown Files**
- **ALWAYS use unique names** (include date or context)
- **Update existing files** rather than creating new ones
- **ALL documentation** goes in `docs/05_CURRENT_WORK/` directory
- **Only create new files** when explicitly needed

### **Documentation Consolidation**
- **Prefer updating** existing documentation over creating new files
- **Maintain** MASTER_PLAN__TESTING_AND_CLEANUP.md as master tracking sheet
- **Include** EXAI consultation summaries in handover documents

---

## 🔄 **WORKFLOW & VALIDATION**

### **Systematic Workflow**
1. **Investigation** → Use view/codebase-retrieval/Docker logs
2. **EXAI Consultation** → Validate approach before implementation
3. **Implementation** → Execute with comprehensive testing
4. **Validation** → EXAI review + Docker log analysis
5. **Documentation** → Update relevant markdown files
6. **Git Operations** → Commit, push (NEVER to main directly)

### **Testing Requirements**
- **Complete entire test phases** comprehensively (not just one tool)
- **Active log monitoring** during test execution
- **EXAI creates test strategy** → EXAI QA approval → run tests → EXAI analyzes output
- **Integration tests** + performance benchmarks + monitoring dashboard integration

### **Validation Checklist**
- ✅ Code compiles without errors
- ✅ Docker container builds successfully
- ✅ All services running
- ✅ No import errors
- ✅ End-to-end tests pass
- ✅ EXAI validation completed
- ✅ Documentation updated

---

## 🐙 **GIT & VERSION CONTROL**

### **Branch Management**
- **Use gh-mcp tools** exclusively for all git operations
- **ALWAYS include path parameter:** `{"path": "c:\\Project\\EX-AI-MCP-Server"}`
- **NEVER push to main** directly
- **Current branch:** Continue on existing branch unless instructed otherwise

### **Commit Strategy**
- **Use gh_branch_push_gh-mcp** for commits
- **Descriptive commit messages** following conventional commits
- **Test before committing** (run validation suite)

### **Merge Strategy**
- **Use gh_branch_merge_to_main_gh-mcp** for merging
- **Test with dryRun=true** first
- **Get user approval** before actual merge

---

## 🚀 **AUTONOMOUS EXECUTION**

### **Authorization Levels**
**User authorizes autonomous execution for:**
- ✅ Technical decisions (with EXAI validation)
- ✅ Bug fixes (with EXAI validation)
- ✅ Feature implementation (with EXAI validation)
- ✅ Testing and validation
- ✅ Documentation updates

**User approval required for:**
- ❌ Phase transitions
- ❌ Breaking changes
- ❌ Code pushes/merges to main
- ❌ Dependency installations
- ❌ Deployment

### **Decision-Making Process**
1. **Investigate** all options thoroughly
2. **Consult EXAI** for best implementation strategy
3. **Choose** the most robust and effective approach
4. **Implement** with comprehensive testing
5. **Validate** with EXAI before proceeding

### **When Uncertain**
- **DON'T:** Stop and ask user
- **DO:** Consult EXAI with high thinking mode
- **DO:** Use web search for external documentation
- **DO:** Investigate Docker logs for runtime behavior
- **DO:** Use codebase-retrieval for architectural context

---

## 🎯 **SUCCESS CRITERIA**

**You're operating effectively if:**
- ✅ You investigate thoroughly before asking questions
- ✅ You consult EXAI for validation before implementation
- ✅ You use task manager tools consistently
- ✅ You complete work comprehensively (not partially)
- ✅ You update documentation as you go
- ✅ You validate changes with EXAI + Docker logs
- ✅ You work autonomously through problems
- ✅ You only escalate when truly stuck

**Red flags:**
- ❌ Asking user for clarification without investigating first
- ❌ Implementing without EXAI validation
- ❌ Not using task manager tools
- ❌ Stopping after first finding (incomplete work)
- ❌ Creating new documentation files unnecessarily
- ❌ Not validating changes before reporting complete

---

## 📖 **QUICK REFERENCE**

### **Essential Tools**
- **Investigation:** view, codebase-retrieval, Docker logs
- **EXAI Consultation:** chat_EXAI-WS, debug_EXAI-WS, analyze_EXAI-WS, codereview_EXAI-WS
- **File Operations:** smart_file_query
- **Task Management:** add_tasks, update_tasks, view_tasklist
- **Git Operations:** gh_branch_push_gh-mcp, gh_branch_merge_to_main_gh-mcp

### **Model Selection**
- **Complex reasoning:** glm-4.6
- **Quick queries:** glm-4.5-flash
- **Large files:** kimi-k2-0905-preview
- **File operations:** kimi-k2-0905-preview

### **Thinking Modes**
- **Critical analysis:** high or max
- **Standard work:** medium
- **Simple queries:** low or minimal

---

**Remember:** You're not just executing tasks - you're solving problems autonomously with EXAI as your expert consultant. Work persistently, validate thoroughly, and only escalate when truly necessary.

