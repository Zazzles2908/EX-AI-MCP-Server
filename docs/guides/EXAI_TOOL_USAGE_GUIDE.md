# EXAI TOOL USAGE GUIDE - Complete Reference

**Date:** 2025-10-04  
**Purpose:** Comprehensive guide for using all 11 EXAI tools correctly  
**Status:** ✅ VALIDATED - All examples tested and working

---

## 🎯 OVERVIEW

This guide provides **CORRECT** usage patterns for all 11 EXAI tools with working examples. Each tool has specific validation requirements that must be met to avoid errors.

**Key Principle:** EXAI tools enforce systematic investigation methodology through strict validation rules. Understanding these requirements is essential for successful usage.

---

## 📋 QUICK REFERENCE

| Tool | Step 1 Required Fields | Common Errors |
|------|----------------------|---------------|
| debug_exai | step, step_number, total_steps, next_step_required, findings | Missing findings |
| analyze_exai | step, step_number, total_steps, next_step_required, findings | Missing findings |
| codereview_exai | step, step_number, total_steps, next_step_required, findings, **relevant_files** | Missing relevant_files |
| refactor_exai | step, step_number, total_steps, next_step_required, findings | Missing findings |
| testgen_exai | step, step_number, total_steps, next_step_required, findings, **relevant_files** | Missing relevant_files |
| secaudit_exai | step, step_number, total_steps, next_step_required, findings, **relevant_files** | Missing relevant_files, security_scope (warning only) |
| precommit_exai | step, step_number, total_steps, next_step_required, findings, **path** | Missing path |
| consensus_exai | step, step_number, total_steps, next_step_required, **findings**, **models** | Missing findings or models |
| planner_exai | step, step_number, total_steps, next_step_required | None (most flexible) |
| chat_exai | prompt | None (simple interface) |
| challenge_exai | prompt | None (simple interface) |

---

## 🔍 DETAILED TOOL GUIDES

### 1. debug_exai - Step-by-Step Debugging

**Purpose:** Systematic debugging with hypothesis tracking and evidence-based analysis

**Required Fields (Step 1):**
- `step`: Description of what you're investigating
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true (for multi-step) or false (for single-step)
- `findings`: What you've discovered so far

**✅ CORRECT Usage:**
```python
debug_exai(
    step="Investigate why model='auto' resolution fails with 'Model auto is not available' error",
    step_number=1,
    total_steps=3,
    next_step_required=true,
    findings="Starting investigation. Error occurs in request_handler_model_resolution.py when 'auto' is passed as model parameter.",
    hypothesis="The _route_auto_model function may be returning 'auto' instead of a concrete model in error cases",
    confidence="exploring",
    model="auto"
)
```

**❌ INCORRECT Usage:**
```python
# Missing 'findings' field
debug_exai(
    step="Debug model resolution",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    model="auto"
)
# ERROR: Missing required 'findings' field
```

---

### 2. analyze_exai - Comprehensive Code Analysis

**Purpose:** Deep architectural analysis with strategic insights

**Required Fields (Step 1):**
- `step`: What to analyze
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true/false
- `findings`: Initial observations

**✅ CORRECT Usage:**
```python
analyze_exai(
    step="Analyze the config.py file structure and organization to assess code quality",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Beginning analysis of config.py. File contains configuration constants, environment variable handling, and helper functions.",
    confidence="medium",
    analysis_type="general",
    model="auto"
)
```

---

### 3. codereview_exai - Full Code Review

**Purpose:** Comprehensive code review with security and quality checks

**Required Fields (Step 1):**
- `step`: What to review
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true/false
- `findings`: Initial observations
- **`relevant_files`**: List of files to review (REQUIRED)

**✅ CORRECT Usage:**
```python
codereview_exai(
    step="Review the Bug #3 fix in request_handler_model_resolution.py for correctness and production readiness",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Reviewing the exception handler fix that prevents returning 'auto' as a model name",
    relevant_files=["src/server/handlers/request_handler_model_resolution.py"],
    review_type="full",
    model="auto"
)
```

**❌ INCORRECT Usage:**
```python
# Missing 'relevant_files' field
codereview_exai(
    step="Review code",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Starting review",
    model="auto"
)
# ERROR: Step 1 requires 'relevant_files' field to specify code files or directories to review
```

---

### 4. refactor_exai - Code Smell Detection

**Purpose:** Identify refactoring opportunities and code smells

**Required Fields (Step 1):**
- `step`: What to analyze for refactoring
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true/false
- `findings`: Initial observations

**✅ CORRECT Usage:**
```python
refactor_exai(
    step="Analyze config.py for refactoring opportunities including code smells, duplication, and organization issues",
    step_number=1,
    total_steps=2,
    next_step_required=true,
    findings="Starting refactoring analysis. Noticed repeated .strip().lower() == 'true' pattern in multiple places.",
    confidence="exploring",
    refactor_type="codesmells",
    model="auto"
)
```

---

### 5. testgen_exai - Test Generation

**Purpose:** Generate comprehensive test suites with edge case coverage

**Required Fields (Step 1):**
- `step`: What to generate tests for
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true/false
- `findings`: Initial observations
- **`relevant_files`**: Files to generate tests for (REQUIRED)

**✅ CORRECT Usage:**
```python
testgen_exai(
    step="Generate comprehensive test cases for the _parse_bool_env() helper function in config.py",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Analyzing _parse_bool_env() function. It parses boolean environment variables with default values.",
    relevant_files=["config.py"],
    confidence="high",
    model="auto"
)
```

**❌ INCORRECT Usage:**
```python
# Missing 'relevant_files' field
testgen_exai(
    step="Generate tests",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Starting test generation",
    model="auto"
)
# ERROR: Step 1 requires 'relevant_files' field to specify code files to generate tests for
```

---

### 6. secaudit_exai - Security Audit

**Purpose:** Comprehensive security assessment with OWASP compliance

**Required Fields (Step 1):**
- `step`: What to audit
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true/false
- `findings`: Initial observations
- **`relevant_files`**: Files to audit (REQUIRED)

**Optional but Recommended:**
- `security_scope`: Application context (web app, API, etc.)
- `audit_focus`: Focus area (owasp, compliance, infrastructure, dependencies)

**✅ CORRECT Usage:**
```python
secaudit_exai(
    step="Perform security audit of config.py to identify potential security vulnerabilities",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Beginning security audit. Config.py handles environment variables and API keys.",
    relevant_files=["config.py"],
    security_scope="Configuration management for MCP server handling API keys and sensitive settings",
    audit_focus="comprehensive",
    confidence="high",
    model="auto"
)
```

**⚠️ WARNING (Not Error):**
```python
# Missing 'security_scope' - generates warning but still works
secaudit_exai(
    step="Audit config.py",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    findings="Starting audit",
    relevant_files=["config.py"],
    model="auto"
)
# WARNING: Security scope not provided for security audit - defaulting to general application
```

---

### 7. precommit_exai - Pre-Commit Validation

**Purpose:** Validate changes before committing with comprehensive analysis

**Required Fields (Step 1):**
- `step`: What to validate
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true/false
- `findings`: Initial observations
- **`path`**: Git repository path (REQUIRED)

**✅ CORRECT Usage:**
```python
precommit_exai(
    step="Analyze uncommitted changes to validate they're ready for commit",
    step_number=1,
    total_steps=2,
    next_step_required=true,
    findings="Starting pre-commit analysis. Detected modified files in config.py and request_handler_model_resolution.py",
    path="C:\\Project\\EX-AI-MCP-Server",
    include_staged=true,
    include_unstaged=true,
    model="auto"
)
```

---

### 8. consensus_exai - Multi-Model Consultation

**Purpose:** Gather consensus from multiple models with structured debate

**Required Fields (Step 1):**
- `step`: Question or proposal for consensus
- `step_number`: 1
- `total_steps`: Number of models to consult
- `next_step_required`: true
- **`findings`**: Your initial analysis (REQUIRED and must be non-empty)
- **`models`**: List of models to consult (REQUIRED)

**✅ CORRECT Usage:**
```python
consensus_exai(
    step="Should we add more comprehensive error handling to the _parse_bool_env() function?",
    step_number=1,
    total_steps=2,
    next_step_required=true,
    findings="Initial analysis: The _parse_bool_env() function currently uses simple string comparison. Adding error handling could improve robustness but might add complexity. Need consensus on whether the benefits outweigh the costs.",
    models=[
        {"model": "glm-4.5-flash", "stance": "for"},
        {"model": "kimi-k2-0905-preview", "stance": "against"}
    ],
    model="auto"
)
```

**❌ INCORRECT Usage:**
```python
# Missing 'findings' or empty findings
consensus_exai(
    step="Should we add error handling?",
    step_number=1,
    total_steps=2,
    next_step_required=true,
    models=[{"model": "glm-4.5-flash"}],
    model="auto"
)
# ERROR: Step 1 requires non-empty 'findings'
```

---

### 9. planner_exai - Step-by-Step Planning

**Purpose:** Break down complex tasks through systematic planning

**Required Fields (Step 1):**
- `step`: Task or problem to plan
- `step_number`: 1
- `total_steps`: Estimated total steps
- `next_step_required`: true/false

**✅ CORRECT Usage:**
```python
planner_exai(
    step="Create a plan for implementing custom model aliases in the config system",
    step_number=1,
    total_steps=1,
    next_step_required=false,
    model="auto"
)
```

---

### 10. chat_exai - General Conversation

**Purpose:** General conversation, brainstorming, quick questions

**Required Fields:**
- `prompt`: Your message or question

**✅ CORRECT Usage:**
```python
chat_exai(
    prompt="What are the latest Python async/await best practices in 2025?",
    use_websearch=true,
    model="auto"
)
```

---

### 11. challenge_exai - Critical Thinking

**Purpose:** Prevent reflexive agreement and encourage critical analysis

**Required Fields:**
- `prompt`: Statement or question to challenge

**✅ CORRECT Usage:**
```python
challenge_exai(
    prompt="I think the Bug #3 fix might not handle all edge cases. What if there's a different exception type?"
)
```

---

## 🚨 COMMON ERRORS AND SOLUTIONS

### Error 1: Missing 'findings' field
**Error Message:** `Missing required 'findings' field` or `Step 1 requires non-empty 'findings'`

**Solution:** Always provide a `findings` field with your initial observations:
```python
findings="Starting investigation. Initial observations: ..."
```

### Error 2: Missing 'relevant_files' field
**Error Message:** `Step 1 requires 'relevant_files' field to specify code files...`

**Affected Tools:** codereview_exai, testgen_exai, secaudit_exai

**Solution:** Always provide a list of files to analyze:
```python
relevant_files=["path/to/file.py"]
```

### Error 3: Missing 'path' field
**Error Message:** `Step 1 requires 'path' field to specify git repository location`

**Affected Tools:** precommit_exai

**Solution:** Provide the repository path:
```python
path="C:\\Project\\EX-AI-MCP-Server"
```

### Error 4: Missing 'models' field
**Error Message:** `Step 1 requires 'models' to specify which models to consult`

**Affected Tools:** consensus_exai

**Solution:** Provide a list of models with optional stances:
```python
models=[{"model": "glm-4.5-flash", "stance": "neutral"}]
```

---

## ✅ VALIDATION CHECKLIST

Before calling any EXAI tool, verify:

- [ ] All required fields are provided
- [ ] `findings` is non-empty (if required)
- [ ] `relevant_files` contains valid file paths (if required)
- [ ] `path` points to a valid directory (if required)
- [ ] `models` list is not empty (if required)
- [ ] `step_number` starts at 1
- [ ] `total_steps` is >= `step_number`

---

## 📚 ADDITIONAL RESOURCES

- **Tool Selection Guide:** `docs/guides/tool-selection-guide.md`
- **Effectiveness Matrix:** `docs/auggie_reports/EXAI_TOOLS_EFFECTIVENESS_MATRIX_2025-10-04.md`
- **Integration Test Results:** `docs/auggie_reports/INTEGRATION_TEST_RESULTS_2025-10-04.md`

---

**Last Updated:** 2025-10-04  
**Status:** ✅ VALIDATED - All examples tested and working  
**Confidence:** VERY HIGH

