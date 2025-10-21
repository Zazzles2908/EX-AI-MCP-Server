# EXAI Troubleshooting Guide

**Version:** 1.0  
**Last Updated:** 2025-01-XX (Wave 1, Epic 1.2)  
**Purpose:** Solutions to common EXAI tool issues and errors

---

## Quick Issue Index

| Issue | Severity | Solution Link |
|-------|----------|---------------|
| Web search incomplete results | 🔴 HIGH | [Issue #1](#issue-1-web-search-incomplete-results) |
| Path validation errors | 🟠 MEDIUM | [Issue #2](#issue-2-path-validation-errors) |
| Tool selection mistakes | 🟡 LOW | [Issue #3](#issue-3-wrong-tool-for-task) |
| Missing required parameters | 🟠 MEDIUM | [Issue #4](#issue-4-missing-required-parameters) |
| continuation_id confusion | 🟡 LOW | [Issue #5](#issue-5-continuation_id-confusion) |
| Model selection issues | 🟡 LOW | [Issue #6](#issue-6-model-selection-issues) |
| Confidence level mistakes | 🟡 LOW | [Issue #7](#issue-7-confidence-level-mistakes) |
| JSON formatting errors | 🟠 MEDIUM | [Issue #8](#issue-8-json-formatting-errors) |
| Workflow step errors | 🟡 LOW | [Issue #9](#issue-9-workflow-step-errors) |
| Server connection issues | 🔴 HIGH | [Issue #10](#issue-10-server-connection-issues) |
| File not found errors | 🟠 MEDIUM | [Issue #11](#issue-11-file-not-found-errors) |
| Timeout errors | 🟡 LOW | [Issue #12](#issue-12-timeout-errors) |

---

## Issue #1: Web Search Incomplete Results

### Symptom
When using `chat_EXAI-WS` with `use_websearch=true`, you get incomplete responses ending with "AGENT'S TURN: Evaluate this perspective..."

### Example Error
```json
{
  "content": "I'll help you find information about zai-sdk v0.0.4...
  
  ---
  
  AGENT'S TURN: Evaluate this perspective...",
  "metadata": {
    "tool_call_events": [{"tool_name": "web_search"}]  // Search executed but results missing
  }
}
```

### Root Cause
- Web search DOES execute (confirmed by metadata)
- Results are NOT integrated into response
- Response truncates before synthesis

### Solution
**Use `web-search` tool directly instead:**
```json
{
  "tool": "web-search",
  "query": "zai-sdk version 0.0.4 features",
  "num_results": 5
}
```

### Status
- **Severity:** 🔴 HIGH (affects all research workflows)
- **Documented in:** `docs/upgrades/international-users/exai-tool-ux-issues.md` Section 1
- **Fix planned:** Wave 2 (Epic 2.2 - CRITICAL priority)
- **Workaround:** ✅ Reliable (use web-search tool)

### Related Issues
- See `web-search-guide.md` for detailed explanation
- See Issue #3 for tool selection guidance

---

## Issue #2: Path Validation Errors

### Symptom
Error message: `All file paths must be FULL absolute paths. Invalid path: 'src/providers'`

### Example Error
```json
{
  "relevant_files": ["src/providers/glm_chat.py"]
}
// Error: All file paths must be FULL absolute paths. Invalid path: 'src/providers/glm_chat.py'
```

### Root Cause
- EXAI tools require FULL absolute paths
- Relative paths are rejected
- Current directory (`.`) is not allowed

### Solution
**Use full absolute paths:**

**Windows:**
```json
{
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]
}
```

**Linux:**
```json
{
  "relevant_files": ["/home/user/EX-AI-MCP-Server/src/providers/glm_chat.py"]
}
```

### Common Mistakes
```json
// ❌ WRONG: Relative path
{"relevant_files": ["src/providers/glm_chat.py"]}

// ❌ WRONG: Current directory
{"relevant_files": ["."]}

// ❌ WRONG: Relative with ./
{"relevant_files": ["./src/providers/glm_chat.py"]}

// ❌ WRONG: Environment variable
{"path": "%USERPROFILE%\\project"}

// ❌ WRONG: Tilde expansion
{"path": "~/project/src"}

// ✅ CORRECT: Full absolute path
{"relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]}
```

### How to Fix
1. Get workspace root: `c:\Project\EX-AI-MCP-Server`
2. Append your relative path: `src\providers\glm_chat.py`
3. Combine: `c:\Project\EX-AI-MCP-Server\src\providers\glm_chat.py`
4. Escape backslashes in JSON: `c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py`

### Status
- **Severity:** 🟠 MEDIUM (blocks usage until understood)
- **Documented in:** `docs/upgrades/international-users/exai-tool-ux-issues.md` Section 3
- **Fix planned:** Wave 2 (Epic 2.3 - better error messages)
- **Workaround:** ✅ Always use absolute paths

### Related Issues
- See `parameter-reference.md` for path requirements
- See Issue #11 for file not found errors

---

## Issue #3: Wrong Tool for Task

### Symptom
Using the wrong tool for your task type, getting irrelevant or incomplete results

### Common Mistakes

**Mistake 1: Using web-search for Internal Code**
```json
// ❌ WRONG
{
  "tool": "web-search",
  "query": "how does my glm_chat.py work"
}
// Returns: Generic information, NOT your code

// ✅ CORRECT
{
  "tool": "analyze_EXAI-WS",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]
}
```

**Mistake 2: Using analyze for External Documentation**
```json
// ❌ WRONG
{
  "tool": "analyze_EXAI-WS",
  "step": "Analyze zai-sdk v0.0.4 documentation"
}
// Error: Can't analyze external documentation

// ✅ CORRECT
{
  "tool": "web-search",
  "query": "zai-sdk version 0.0.4 documentation"
}
```

**Mistake 3: Using chat for Code Review**
```json
// ❌ WRONG
{
  "tool": "chat_EXAI-WS",
  "prompt": "Review this code for security issues: [code]"
}
// Returns: Superficial review

// ✅ CORRECT
{
  "tool": "secaudit_EXAI-WS",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\auth\\user.py"]
}
```

### Solution
**Use the decision tree in `tool-selection-guide.md`:**

| Task Type | Correct Tool |
|-----------|--------------|
| External docs | web-search |
| Internal code | analyze_EXAI-WS |
| Code review | codereview_EXAI-WS |
| Security audit | secaudit_EXAI-WS |
| Debugging | debug_EXAI-WS |
| Planning | planner_EXAI-WS |
| Testing | testgen_EXAI-WS |

### Status
- **Severity:** 🟡 LOW (doesn't block, but inefficient)
- **Solution:** See `tool-selection-guide.md`

---

## Issue #4: Missing Required Parameters

### Symptom
Error message: `Missing required parameter: 'findings'` or similar

### Example Error
```json
{
  "step": "Analyze code",
  "step_number": 1
}
// Error: Missing required parameters: total_steps, next_step_required, findings
```

### Root Cause
All workflow tools require these parameters:
- `step` (string)
- `step_number` (integer)
- `total_steps` (integer)
- `next_step_required` (boolean)
- `findings` (string)

### Solution
**Include all required parameters:**
```json
{
  "step": "Analyze provider architecture",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial assessment of provider structure"
}
```

### Quick Reference
**Minimal workflow tool call:**
```json
{
  "step": "Description of what you're doing",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "What you discovered in this step"
}
```

### Status
- **Severity:** 🟠 MEDIUM (blocks tool usage)
- **Solution:** See `parameter-reference.md` for all parameters

---

## Issue #5: continuation_id Confusion

### Symptom
Confusing messages about continuation_id: "Claude can continue this conversation for 19 more exchanges"

### Example
```json
{
  "continuation_offer": {
    "continuation_id": "abc123",
    "note": "Claude can continue this conversation for 19 more exchanges."
  }
}
```

### Why Confusing
- Message assumes "Claude" is the user
- Doesn't explain what continuation_id does
- Generic message regardless of context

### Solution
**To continue a conversation:**
1. Get `continuation_id` from previous response
2. Include it in your next request:

```json
{
  "prompt": "Follow-up question...",
  "continuation_id": "abc123"
}
```

**When to use:**
- Multi-turn conversations
- Follow-up questions
- Maintaining context

**When NOT to use:**
- New, unrelated questions
- Different topics

### Status
- **Severity:** 🟡 LOW (confusing but doesn't block)
- **Documented in:** `docs/upgrades/international-users/exai-tool-ux-issues.md` Section 2
- **Fix planned:** Wave 2 (Epic 2.3 - context-aware messaging)

---

## Issue #6: Model Selection Issues

### Symptom
Unexpected model behavior or performance

### Common Mistakes

**Mistake 1: Not Using "auto"**
```json
// ❌ SUBOPTIMAL: Hardcoded model
{"model": "glm-4.5"}

// ✅ BETTER: Let server choose
{"model": "auto"}
```

**Mistake 2: Wrong Model for Task**
```json
// ❌ WRONG: Fast model for complex analysis
{
  "model": "glm-4.5-flash",
  "thinking_mode": "max"
}
// Flash model not optimized for deep thinking

// ✅ CORRECT: Quality model for complex analysis
{
  "model": "kimi-k2-0905-preview",
  "thinking_mode": "max"
}
```

### Solution
**Use "auto" unless you have specific requirements:**
```json
{"model": "auto"}
```

**Model Selection Guide:**
- `auto` - Server selects best model (recommended)
- `kimi-k2-0905-preview` - Best for tool use, coding, agentic workflows (256K context)
- `glm-4.6` - Best for cost optimization, web search (200K context)
- `glm-4.5-flash` - Fastest, for simple tasks (128K context)

**See:** `docs/upgrades/international-users/kimi-model-selection-guide.md` for detailed model selection guidance

### Status
- **Severity:** 🟡 LOW (affects quality, not functionality)
- **Solution:** Use `"auto"` by default

---

## Issue #7: Confidence Level Mistakes

### Symptom
Skipping expert validation unintentionally or getting unnecessary validation

### Common Mistakes

**Mistake 1: Using "certain" Too Early**
```json
// ❌ WRONG: Skips expert validation
{
  "confidence": "certain"
}
// Only use when 100% confident

// ✅ CORRECT: Gets expert validation
{
  "confidence": "very_high"
}
```

**Mistake 2: Unclear Confidence Levels**
```json
// ❓ UNCLEAR: When is "high" vs "very_high"?
{"confidence": "high"}
```

### Solution
**Confidence Level Guide:**
- `exploring` - Just starting analysis
- `low` - Early investigation
- `medium` - Some evidence gathered
- `high` - Strong evidence
- `very_high` - Very strong evidence
- `almost_certain` - Nearly complete confidence
- `certain` - 100% confidence (SKIPS expert validation)

**Rule of Thumb:**
- Use `"certain"` ONLY when 100% confident
- When in doubt, use `"very_high"` or `"almost_certain"`
- Expert validation is valuable - don't skip it prematurely

### Status
- **Severity:** 🟡 LOW (affects validation quality)
- **Documented in:** `docs/upgrades/international-users/exai-tool-ux-issues.md` Section 4.3

---

## Issue #8: JSON Formatting Errors

### Symptom
Error message: `Invalid JSON` or `Unexpected token`

### Common Mistakes

**Mistake 1: Unescaped Backslashes**
```json
// ❌ WRONG: Single backslash (invalid JSON)
{"path": "c:\Project\EX-AI-MCP-Server"}

// ✅ CORRECT: Double backslash (escaped)
{"path": "c:\\Project\\EX-AI-MCP-Server"}
```

**Mistake 2: Wrong Type for Boolean**
```json
// ❌ WRONG: String instead of boolean
{"next_step_required": "true"}

// ✅ CORRECT: Boolean
{"next_step_required": true}
```

**Mistake 3: Trailing Commas**
```json
// ❌ WRONG: Trailing comma
{
  "step": "Analyze code",
  "step_number": 1,
}

// ✅ CORRECT: No trailing comma
{
  "step": "Analyze code",
  "step_number": 1
}
```

**Mistake 4: Missing Quotes**
```json
// ❌ WRONG: Unquoted string
{step: "Analyze code"}

// ✅ CORRECT: Quoted keys and values
{"step": "Analyze code"}
```

### Solution
**JSON Type Reference:**
- Strings: `"value"` (with quotes)
- Integers: `123` (no quotes)
- Booleans: `true` or `false` (lowercase, no quotes)
- Arrays: `["item1", "item2"]`
- Objects: `{"key": "value"}`

**Windows Paths:**
```json
{"path": "c:\\Project\\EX-AI-MCP-Server"}
```

### Status
- **Severity:** 🟠 MEDIUM (blocks tool usage)
- **Solution:** Validate JSON before submitting

---

## Issue #9: Workflow Step Errors

### Symptom
Error message: `step_number must be <= total_steps` or workflow confusion

### Common Mistakes

**Mistake 1: step_number > total_steps**
```json
// ❌ WRONG
{
  "step_number": 5,
  "total_steps": 3
}

// ✅ CORRECT
{
  "step_number": 3,
  "total_steps": 3
}
```

**Mistake 2: Not Incrementing step_number**
```json
// ❌ WRONG: Same step_number
// Call 1: step_number: 1
// Call 2: step_number: 1  // Should be 2

// ✅ CORRECT: Increment step_number
// Call 1: step_number: 1
// Call 2: step_number: 2
```

**Mistake 3: Starting at 0**
```json
// ❌ WRONG: step_number starts at 0
{"step_number": 0}

// ✅ CORRECT: step_number starts at 1
{"step_number": 1}
```

### Solution
**Workflow Step Rules:**
1. `step_number` starts at 1 (not 0)
2. Increment by 1 for each subsequent step
3. `step_number` must be ≤ `total_steps`
4. Can adjust `total_steps` mid-workflow if needed

### Status
- **Severity:** 🟡 LOW (easy to fix)
- **Solution:** Follow step numbering rules

---

## Issue #10: Server Connection Issues

### Symptom
Error message: `Connection refused` or `Server not responding`

### Root Cause
EX-AI-MCP-Server WebSocket daemon not running

### Solution
**Restart the server:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

**Verify server is running:**
- Check for: `server listening on 127.0.0.1:8765`
- Check for: `connection open`
- Check for: Provider configuration messages

**Test server:**
```json
{
  "tool": "version_EXAI-WS"
}
```

### Status
- **Severity:** 🔴 HIGH (blocks all tool usage)
- **Solution:** Restart server with ws_start.ps1

---

## Issue #11: File Not Found Errors

### Symptom
Error message: `File not found` or `No such file or directory`

### Common Causes
1. Incorrect file path
2. File doesn't exist
3. Typo in filename
4. Wrong directory

### Solution
**Verify file exists:**
1. Check file path is correct
2. Verify file exists at that location
3. Check for typos in filename
4. Use absolute path (not relative)

**Example:**
```json
// ❌ WRONG: File doesn't exist
{"relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\nonexistent.py"]}

// ✅ CORRECT: File exists
{"relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]}
```

### Status
- **Severity:** 🟠 MEDIUM (blocks file analysis)
- **Solution:** Verify file path and existence

---

## Issue #12: Timeout Errors

### Symptom
Error message: `Request timeout` or `Operation timed out`

### Common Causes
1. Complex analysis taking too long
2. Large files
3. Network issues (for web search)
4. Server overload

### Solution

**For Complex Analysis:**
```json
// Break into smaller steps
{
  "step": "Analyze first half of file",
  "total_steps": 2  // Split into multiple steps
}
```

**For Large Files:**
```json
// Analyze specific sections
{
  "relevant_files": ["c:\\Project\\...\\specific_function.py"]
  // Instead of entire large file
}
```

**For Web Search:**
```json
// Reduce num_results
{
  "query": "...",
  "num_results": 3  // Instead of 10
}
```

### Status
- **Severity:** 🟡 LOW (rare, workaround available)
- **Solution:** Break into smaller operations

---

## Quick Troubleshooting Checklist

### Before Calling Any Tool:
- [ ] Using correct tool for task? (See `tool-selection-guide.md`)
- [ ] All required parameters included?
- [ ] File paths are FULL absolute paths?
- [ ] JSON is valid (no syntax errors)?
- [ ] Server is running? (Test with `version_EXAI-WS`)

### For Workflow Tools:
- [ ] `step_number` starts at 1?
- [ ] `step_number` ≤ `total_steps`?
- [ ] All 5 required parameters present?
- [ ] `findings` is descriptive and specific?

### For File Operations:
- [ ] Paths are absolute (c:\\Project\\...)?
- [ ] Files exist at specified paths?
- [ ] Backslashes escaped in JSON (\\\\)?
- [ ] No relative paths (., ./, src/)?

### For Web Search:
- [ ] Using `web-search` tool (not chat_EXAI-WS)?
- [ ] Query is specific and detailed?
- [ ] `num_results` appropriate for task?

---

## Getting Help

### Documentation Resources
1. **Tool Selection:** `tool-selection-guide.md`
2. **Parameters:** `parameter-reference.md`
3. **Web Search:** `web-search-guide.md`
4. **Examples:** `query-examples.md`
5. **UX Issues:** `docs/upgrades/international-users/exai-tool-ux-issues.md`

### Common Issue Categories
- **Path Errors:** See Issue #2 and `parameter-reference.md`
- **Tool Selection:** See Issue #3 and `tool-selection-guide.md`
- **Web Search:** See Issue #1 and `web-search-guide.md`
- **Parameters:** See Issue #4 and `parameter-reference.md`
- **JSON Errors:** See Issue #8

### Still Stuck?
1. Check error message carefully
2. Review relevant documentation
3. Try the workaround if available
4. Simplify your request
5. Test with a minimal example

---

## Known Issues Summary

| Issue | Status | Fix Timeline | Workaround |
|-------|--------|--------------|------------|
| Web search incomplete | 🔴 CRITICAL | Wave 2 Week 1-2 | Use web-search tool |
| Path validation errors | 🟠 HIGH | Wave 2 Week 1-2 | Use absolute paths |
| continuation_id messaging | 🟡 MEDIUM | Wave 2 Week 2 | Ignore confusing message |
| Confidence level guidance | 🟡 MEDIUM | Wave 3 | Use "very_high" when unsure |
| Tool rigidity patterns | 🟡 LOW | Wave 3-4 | Work within constraints |

---

**Document Status:** ✅ COMPLETE (Task 1.5)  
**Validation:** Pending codereview_EXAI-WS  
**Total Issues:** 12 common issues with solutions (exceeds 10+ requirement)

