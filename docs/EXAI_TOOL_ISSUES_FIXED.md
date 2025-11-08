# EXAI Tool Issues - Identified & Fixed

## 📋 Session Summary

This document tracks all issues I encountered while using EXAI MCP tools during this session, the errors they produced, and the solutions implemented.

---

## Issue 1: Invalid Parameter - `continuation_id`

### ❌ Error Encountered
When attempting to use EXAI chat tool with continuation_id:

```python
mcp__exai-mcp__chat(
    prompt="Continue the conversation",
    continuation_id="some_id"  # ❌ This caused the error
)
```

**Error Message:**
```
Error in chat: Provider error (GLM): Provider error (GLM): Completions.create() got an unexpected keyword argument 'continuation_id'
```

### ✅ Root Cause
- `continuation_id` is a **system-level conversation management mechanism**
- It is **returned in response metadata**, not passed as input
- The platform handles context automatically
- It is **NOT part of the tool's API**

### ✅ Solution
**Remove `continuation_id` from tool parameters**

```python
# CORRECT - Let the platform handle context
mcp__exai-mcp__chat(prompt="Your question")
# The response includes continuation_id in metadata
# Platform automatically maintains context

# Subsequent call - no continuation_id needed
mcp__exai-mcp__chat(prompt="Follow-up question")
```

### 📖 Documentation
See: `docs/development/exai-tool-usage-guide.md` - Section "Issue 1: Invalid Parameter Error - continuation_id"

---

## Issue 2: File Request Instead of Analysis

### ❌ Error Encountered
When asking EXAI to review information I provided:

**My Request:**
```
"I created a comprehensive architectural document. Please review and validate this information."
```

**EXAI Response:**
```
"Please provide the EXAI_MCP_ARCHITECTURE.md file so I can review your technical analysis."
```

### ✅ Root Cause
- EXAI's file handling is optimized for code analysis
- For conceptual review, provide information **directly in the prompt**
- File tools work best for: code files, large documents, binary files
- Not designed for: conceptual review of information you've already typed

### ✅ Solution
**Provide the content directly in the prompt**

```python
# Instead of: "Please review file X"
# Do this:
mcp__exai-mcp__chat(
    prompt="""I created an architecture document with this content:

[PASTE YOUR ACTUAL CONTENT HERE]

Please review and validate this information for technical accuracy.
"""
)
```

### 📖 Documentation
See: `docs/development/exai-tool-usage-guide.md` - Section "Issue 2: File Request Instead of Analysis"

---

## Issue 3: Parameter Validation Confusion

### ❌ Error Encountered
Uncertainty about which parameters are valid for each tool.

**Attempted Pattern:**
```python
# Wasn't sure if this was valid
mcp__exai-mcp__chat(
    prompt="Question",
    continuation_id="...",  # ❌ Invalid
    context="...",          # ❌ Invalid
    session_id="..."        # ❌ Invalid
)
```

### ✅ Root Cause
- Each tool has specific valid parameters
- Using invalid parameters causes errors
- No clear reference for what parameters each tool accepts

### ✅ Solution
**Created comprehensive parameter reference**

**Valid `chat` Parameters:**
- `prompt` (required)
- `files` (optional) - small files <5KB
- `file_ids` (optional) - uploaded file IDs
- `use_websearch` (optional)
- `stream` (optional)
- `model` (optional)
- `temperature` (optional)
- `tool_choice` (optional)
- `tools` (optional)

**Invalid Parameters:**
- `continuation_id` ❌
- `context` ❌
- `session_id` ❌
- `messages` ❌

### 📖 Documentation
See: `docs/development/exai-tool-usage-guide.md` - Section "Valid Tool Parameters Reference"

---

## Issue 4: Conversation Flow Patterns

### ❌ Error Encountered
Unclear how to maintain conversation context across multiple tool calls.

**My Approach:**
- Tried to manually pass continuation_id ❌
- Expected to need session management ❌
- Didn't understand automatic context handling ❌

### ✅ Solution
**Platform handles context automatically**

```python
# Pattern 1: Basic Q&A
response1 = mcp__exai-mcp__chat(prompt="What is X?")
response2 = mcp__exai-mcp__chat(prompt="How does X work?")
# Context maintained automatically ✅

# Pattern 2: Analysis Workflow
mcp__exai-mcp__analyze(
    step="Initial analysis",
    findings="..."
)
mcp__exai-mcp__analyze(
    step="Deeper investigation",
    findings="...",  # Builds on previous
    backtrack_from_step=1
)
```

### 📖 Documentation
See: `docs/development/exai-tool-usage-guide.md` - Section "Correct Conversation Patterns"

---

## Issue 5: File Handling Strategy

### ❌ Confusion
When to use `files` vs `file_ids` vs file paths.

**My Questions:**
- Should I use `files` or `file_ids`? 🤔
- What size threshold? 🤔
- How to handle large documents? 🤔

### ✅ Solution
**Clear file handling strategy**

**Use `files` for:**
- Small files (<5KB)
- Code files for review
- Single-use analysis
- Quick checks

```python
mcp__exai-mcp__chat(
    prompt="Review this code",
    files=["c:/Project/EX-AI-MCP-Server/src/main.py"]
)
```

**Use `file_ids` for:**
- Large files (>5KB)
- Multi-file analysis
- Complex reviews
- Persistent reference

```python
# First: Upload
file_ids = kimi_upload_files(["c:/path/to/large_doc.pdf"])

# Then: Analyze
mcp__exai-mcp__analyze(
    step="Analyze the document",
    findings="Key insights",
    file_ids=file_ids
)
```

### 📖 Documentation
See: `docs/development/exai-tool-usage-guide.md` - Section "File Handling Strategy"

---

## Issue 6: Path Format Confusion

### ❌ Error Example
Using relative paths that don't work:

```python
# ❌ WRONG
mcp__exai-mcp__chat(
    prompt="Review this",
    files=["./src/main.py"]
)

# ❌ WRONG
mcp__exai-mcp__chat(
    prompt="Review this",
    files=["src/main.py"]
)
```

### ✅ Solution
**Always use full absolute paths**

```python
# ✅ CORRECT
mcp__exai-mcp__chat(
    prompt="Review this",
    files=["c:/Project/EX-AI-MCP-Server/src/main.py"]
)
```

### 📖 Documentation
See: `docs/development/exai-tool-usage-guide.md` - Section "Error: 'File not found' or path errors"

---

## Best Practices Discovered

### ✅ DO
1. Use valid parameters only
2. Provide content directly for conceptual review
3. Use full absolute paths for files
4. Let the system handle context automatically
5. Use appropriate tools for the task
6. Keep files under 5KB for `files` parameter
7. Use `file_ids` for large files

### ❌ DON'T
1. Pass `continuation_id` as a parameter
2. Ask to "provide files" for conceptual review
3. Use relative paths
4. Mix `files` and `file_ids` in same call
5. Use invalid parameters
6. Over-engineer simple tasks
7. Create unnecessary wrapper abstractions

---

## Quick Reference - Correct Patterns

### Basic Chat
```python
# ✅ CORRECT
mcp__exai-mcp__chat(prompt="Your question")
```

### Chat with Files
```python
# ✅ CORRECT - Small files
mcp__exai-mcp__chat(
    prompt="Review this",
    files=["c:/path/to/file.py"]
)

# ✅ CORRECT - Large files
file_ids = kimi_upload_files(["c:/path/to/large.pdf"])
mcp__exai-mcp__chat(
    prompt="Analyze this",
    file_ids=file_ids
)
```

### Analysis Workflow
```python
# ✅ CORRECT
mcp__exai-mcp__analyze(
    step="Initial analysis",
    findings="What you discovered",
    relevant_files=["c:/path/to/file.py"],
    confidence="high"
)
```

### Code Review
```python
# ✅ CORRECT
mcp__exai-mcp__codereview(
    step="Review the code",
    relevant_files=["c:/path/to/file.py"],
    focus_on=["security", "performance"],
    review_type="full"
)
```

### Debugging
```python
# ✅ CORRECT
mcp__exai-mcp__debug(
    step="Investigate issue",
    findings="Current findings",
    hypothesis="Theory about the bug",
    relevant_files=["c:/path/to/file.py"]
)
```

---

## Files Created to Document Solutions

### 1. `docs/development/exai-tool-usage-guide.md` (16KB)
Comprehensive guide covering:
- All 6 issues encountered
- Correct usage patterns for all 21 tools
- Valid/invalid parameters
- File handling strategy
- Best practices
- Quick reference

### 2. `docs/EXAI_TOOL_ISSUES_FIXED.md` (this file)
Session summary documenting:
- Each issue encountered
- Error messages
- Root causes
- Solutions implemented
- Documentation created

### 3. Updated `docs/README.md`
Added links to the usage guide:
- Highlighted in development section
- Marked as required reading for developers
- ⚠️ Warning icon to draw attention

---

## Impact of Fixes

### Before Fixes
- ❌ Unclear tool usage patterns
- ❌ Frequent parameter errors
- ❌ Confusion about conversation context
- ❌ File handling issues
- ❌ No reference documentation

### After Fixes
- ✅ Clear parameter reference for all 21 tools
- ✅ Comprehensive usage guide with examples
- ✅ Correct patterns documented
- ✅ File handling strategy defined
- ✅ Best practices established
- ✅ Quick reference available

---

## Verification

### Tested Patterns That Work
1. ✅ Basic chat without continuation_id
2. ✅ Chat with small files using absolute paths
3. ✅ Analysis workflow with step-by-step progression
4. ✅ Code review with focus areas
5. ✅ Debugging with findings and hypothesis
6. ✅ File upload and analysis with file_ids

### Documented Patterns
- All 21 EXAI tools have parameter reference
- File handling strategy is clear
- Conversation flow is documented
- Error patterns are identified
- Best practices are established

---

## Next Steps

### For Users
1. **Read**: `docs/development/exai-tool-usage-guide.md`
2. **Bookmark**: Quick reference section
3. **Test**: Try basic chat pattern
4. **Explore**: Use different tools with correct parameters

### For Developers
1. **Integrate**: Use the guide for tool development
2. **Reference**: When building wrappers or integrations
3. **Contribute**: Add to the guide if you discover more patterns

### For Documentation
1. **Maintain**: Keep the usage guide updated
2. **Expand**: Add examples as tools evolve
3. **Improve**: Based on user feedback

---

## Summary

**Total Issues Identified:** 6
**Total Solutions Documented:** 6
**Documentation Created:** 2 new files (16KB total)
**Navigation Updated:** 1 file (docs/README.md)

**Result:** A comprehensive reference for correct EXAI tool usage that prevents common errors and enables effective use of all 21 tools.

---

**Key Takeaway:** The platform handles context automatically. Just use the right tool with valid parameters - no need to manage continuation_id or session state manually! ✅
