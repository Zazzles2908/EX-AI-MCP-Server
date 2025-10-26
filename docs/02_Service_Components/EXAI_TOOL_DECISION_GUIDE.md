# EXAI Tool Decision Guide for AI Assistants (Claude)

**Date:** 2025-10-22 (Updated with Token Efficiency Guidance)
**Audience:** AI Assistants (Claude) working with EXAI-WS MCP tools
**Purpose:** Clear decision framework for choosing the right EXAI tool

---

## ⚠️ CRITICAL: TOKEN EFFICIENCY (Added 2025-10-22)

### **ALWAYS Use `files` Parameter - Never Paste Code!**

**❌ WRONG - Wastes 70-80% of tokens:**
```python
chat_EXAI-WS(
    prompt="""
    Here's the file to validate:
    ```python
    [400 lines of code pasted here]
    ```
    Please review...
    """
)
```

**✅ CORRECT - Token efficient:**
```python
# For files <5KB (most code files)
chat_EXAI-WS(
    prompt="Please validate this unified provider interface for production readiness...",
    files=["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\file_base.py"],
    model="glm-4.6",
    thinking_mode="high"
)

# For files >5KB (large files) - TWO OPTIONS:

# Option 1: Kimi Upload+Chat (2 steps)
kimi_upload_files(files=["c:\\Project\\EX-AI-MCP-Server\\large_file.py"])
kimi_chat_with_files(
    prompt="Please review this implementation...",
    file_ids=["file-xxx"],
    model="kimi-k2-0905-preview"
)

# Option 2: GLM Multi-File Chat (1 step) ⭐ NEW!
glm_multi_file_chat(
    files=["c:\\Project\\EX-AI-MCP-Server\\large_file.py"],
    prompt="Please review this implementation...",
    model="glm-4.6"
)
```

**Token Savings:** 70-80% reduction (4-6x more efficient)

**Rule:** If you're about to paste code in a prompt, STOP and use `files` parameter instead!

---

## 🎯 CRITICAL UNDERSTANDING

### Workflow Tools Architecture

**How Workflow Tools Actually Work:**
1. **Claude (you) calls tool** with step 1 + initial findings from YOUR investigation
2. **Tool auto-executes internally** (steps 2-N) - NO AI calls during this phase
3. **Tool calls expert analysis** at the end (ONE AI call for validation)
4. **Claude must investigate between steps** - the tool doesn't do investigation for you!

**Key Insight:** Workflow tools are NOT autonomous investigators. They are structured frameworks that guide YOUR investigation and provide expert validation at the end.

---

## 📊 DECISION FLOWCHART

```
User Request
    ↓
Is this about EXTERNAL information?
    ├─ YES → Use web-search or chat_EXAI-WS (with web mode)
    └─ NO → Continue
         ↓
Is this a SPECIFIC runtime error/bug?
    ├─ YES → Use debug_EXAI-WS (after YOU investigate)
    └─ NO → Continue
         ↓
Is this about CODE QUALITY/SECURITY?
    ├─ YES → Use codereview_EXAI-WS (after YOU investigate)
    └─ NO → Continue
         ↓
Is this about UNDERSTANDING code structure?
    ├─ YES → Use analyze_EXAI-WS (after YOU investigate)
    └─ NO → Continue
         ↓
Is this a GENERAL QUESTION or brainstorming?
    ├─ YES → Use chat_EXAI-WS
    └─ NO → Continue
         ↓
Is this about REFACTORING opportunities?
    ├─ YES → Use refactor_EXAI-WS (after YOU investigate)
    └─ NO → Continue
         ↓
Is this about PRE-COMMIT validation?
    ├─ YES → Use precommit_EXAI-WS (after YOU investigate git changes)
    └─ NO → Use chat_EXAI-WS for guidance
```

---

## 🛠️ TOOL SELECTION MATRIX

| Task Type | Primary Tool | When to Use | What YOU Must Do First |
|-----------|--------------|-------------|------------------------|
| **General questions** | `chat_EXAI-WS` | Brainstorming, explanations, opinions | Nothing - just ask |
| **External research** | `web-search` | Documentation, best practices | Nothing - just search |
| **Specific bug/error** | `debug_EXAI-WS` | Runtime errors, crashes, performance issues | Investigate with view/codebase-retrieval, gather evidence |
| **Code quality review** | `codereview_EXAI-WS` | Finding bugs, security issues, code smells | Read the code, identify potential issues |
| **Understanding code** | `analyze_EXAI-WS` | Architecture, patterns, structure | Explore codebase, map structure |
| **Refactoring** | `refactor_EXAI-WS` | Code smells, modernization, organization | Identify refactoring opportunities |
| **Pre-commit check** | `precommit_EXAI-WS` | Validate changes before commit | Check git diff, understand changes |
| **Security audit** | `secaudit_EXAI-WS` | OWASP Top 10, compliance, vulnerabilities | Review security-critical code |
| **Test generation** | `testgen_EXAI-WS` | Create comprehensive test suites | Understand code paths, edge cases |

---

## ⚠️ COMMON MISTAKES TO AVOID

### Mistake 1: Using Workflow Tools Without Investigation
```
❌ WRONG:
debug_EXAI-WS(
    step="Debug the authentication failure",
    step_number=1,
    findings="Starting investigation"  # NO ACTUAL FINDINGS!
)

✅ CORRECT:
1. Use view/codebase-retrieval to investigate auth code
2. Gather evidence (error messages, stack traces, code paths)
3. Form hypothesis
4. THEN call debug_EXAI-WS with actual findings:

debug_EXAI-WS(
    step="Investigate authentication failure in login endpoint",
    step_number=1,
    findings="Found that auth.py line 45 throws KeyError when 'user_id' missing from token payload. Token validation happens before user_id check. Hypothesis: Token structure changed but validation logic didn't update.",
    relevant_files=["c:\\Project\\...\\auth.py", "c:\\Project\\...\\token_validator.py"],
    hypothesis="Token structure mismatch - validation expects old format"
)
```

### Mistake 2: Using chat_EXAI-WS for Code Review
```
❌ WRONG:
chat_EXAI-WS(
    prompt="Review this code for bugs",
    files=["c:\\Project\\...\\payment.py"]
)
# Result: Generic response, not systematic review

✅ CORRECT:
1. Read the code yourself first
2. Identify potential issues
3. Use codereview_EXAI-WS with your findings:

codereview_EXAI-WS(
    step="Review payment processing for security and correctness",
    step_number=1,
    findings="Identified: 1) No input validation on amount, 2) SQL query uses string concatenation, 3) No error handling for payment gateway failures",
    relevant_files=["c:\\Project\\...\\payment.py"]
)
```

### Mistake 3: Expecting Workflow Tools to Investigate for You
```
❌ WRONG MENTAL MODEL:
"I'll call debug tool and it will investigate the bug for me"

✅ CORRECT MENTAL MODEL:
"I'll investigate the bug myself using view/codebase-retrieval, 
 then use debug tool to structure my findings and get expert validation"
```

---

## 📝 PROPER USAGE PATTERNS

### Pattern 1: Debugging Workflow
```
1. User reports bug: "Login fails with 500 error"

2. YOU investigate:
   - Use codebase-retrieval to find login code
   - Use view to read auth.py, login_handler.py
   - Check error logs
   - Trace execution path
   - Form hypothesis

3. Call debug_EXAI-WS:
   debug_EXAI-WS(
       step="Investigate 500 error in login endpoint",
       step_number=1,
       total_steps=2,
       next_step_required=true,
       findings="Error occurs in auth.py line 67 when validating JWT token. Stack trace shows KeyError: 'exp'. Token payload missing expiration field. Hypothesis: Token generation changed but validation didn't update.",
       hypothesis="Token format mismatch between generation and validation",
       relevant_files=["c:\\Project\\...\\auth.py", "c:\\Project\\...\\token_gen.py"],
       confidence="medium"
   )

4. Tool provides expert analysis and recommendations
```

### Pattern 2: Code Review Workflow
```
1. User asks: "Review the new payment feature"

2. YOU investigate:
   - Use view to read payment.py
   - Check for security issues
   - Look for error handling
   - Verify input validation
   - Check for code smells

3. Call codereview_EXAI-WS:
   codereview_EXAI-WS(
       step="Review payment processing implementation",
       step_number=1,
       total_steps=1,
       next_step_required=false,
       findings="Found 3 critical issues: 1) SQL injection risk (line 45), 2) No amount validation (line 23), 3) Hardcoded API key (line 12). Also found 2 medium issues: missing error handling, no logging.",
       relevant_files=["c:\\Project\\...\\payment.py"],
       review_type="security",
       confidence="high"
   )

4. Tool provides comprehensive review with prioritized fixes
```

### Pattern 3: General Question Workflow
```
1. User asks: "What's the best way to handle async operations in Python?"

2. YOU decide: This is a general question, not code-specific

3. Call chat_EXAI-WS:
   chat_EXAI-WS(
       prompt="What are the best practices for handling async operations in Python? I'm working on a WebSocket server that needs to handle concurrent requests efficiently.",
       model="glm-4.6",
       use_websearch=true
   )

4. Tool provides answer with web research
```

---

## 🎓 WHEN TO USE EACH TOOL

### chat_EXAI-WS
**Use for:**
- General questions and explanations
- Brainstorming and ideation
- Getting second opinions
- Discussing approaches
- Asking "how to" questions

**Don't use for:**
- Code review (use codereview_EXAI-WS)
- Debugging (use debug_EXAI-WS)
- Systematic analysis (use analyze_EXAI-WS)

### debug_EXAI-WS
**Use for:**
- Specific runtime errors
- Performance issues
- Race conditions
- Integration problems
- Mysterious crashes

**Don't use for:**
- General code review (use codereview_EXAI-WS)
- Understanding architecture (use analyze_EXAI-WS)
- Finding potential bugs without symptoms (use codereview_EXAI-WS)

### codereview_EXAI-WS
**Use for:**
- Finding bugs and security issues
- Code quality assessment
- Security audits
- Best practices validation
- Actionable feedback

**Don't use for:**
- Understanding code structure (use analyze_EXAI-WS)
- Debugging specific errors (use debug_EXAI-WS)
- General questions (use chat_EXAI-WS)

### analyze_EXAI-WS
**Use for:**
- Understanding code architecture
- Exploring unfamiliar codebases
- Identifying patterns
- Assessing design decisions
- Mapping code structure

**Don't use for:**
- Finding bugs (use codereview_EXAI-WS)
- Debugging errors (use debug_EXAI-WS)
- External documentation (use web-search)

---

## 🚨 RED FLAGS - When You're Using the Wrong Tool

1. **Tool returns generic/unhelpful response** → You probably used chat when you needed a workflow tool
2. **Tool times out or loops** → You probably didn't investigate first before calling workflow tool
3. **Tool says "no issues found" when you know there are issues** → You didn't provide enough findings
4. **Tool asks for more context repeatedly** → You're using wrong tool or didn't investigate enough
5. **You're calling the same tool multiple times with no progress** → Stop and reassess which tool to use

---

## ✅ CHECKLIST BEFORE CALLING WORKFLOW TOOLS

Before calling debug/analyze/codereview/refactor/etc:

- [ ] Have I investigated the code myself using view/codebase-retrieval?
- [ ] Do I have concrete findings to report (not just "starting investigation")?
- [ ] Have I identified relevant files with ABSOLUTE paths?
- [ ] Do I have a hypothesis or theory about what I'm investigating?
- [ ] Am I using the right tool for this task type?
- [ ] Have I set appropriate confidence level based on my investigation?

If you answered NO to any of these, DO MORE INVESTIGATION FIRST!

---

## 📚 NEXT STEPS

After reading this guide:
1. Bookmark this file for quick reference
2. When user asks you to use EXAI, consult this guide first
3. Always investigate BEFORE calling workflow tools
4. Use chat_EXAI-WS for questions, workflow tools for systematic analysis
5. Remember: YOU do the investigation, tools provide structure and validation


