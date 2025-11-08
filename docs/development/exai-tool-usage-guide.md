# EXAI MCP Tools - Correct Usage Guide

## ⚠️ Common Issues Encountered & Solutions

This guide documents the issues I encountered while using EXAI MCP tools and provides the correct patterns to avoid these problems.

---

## Issue 1: Invalid Parameter Error - `continuation_id`

### ❌ Error Encountered
```python
mcp__exai-mcp__chat(
    continuation_id="some_id",
    prompt="Continue the conversation"
)
# Result: Provider error (GLM): Completions.create() got an unexpected keyword argument 'continuation_id'
```

### ✅ Solution
**`continuation_id` is NOT a tool parameter** - it's a system-level conversation mechanism handled automatically by the platform.

**Correct Usage:**
```python
# Initial call - no continuation_id needed
mcp__exai-mcp__chat(
    prompt="Your question here"
)

# The response includes a continuation_id in metadata
# The system automatically maintains context
# Just make another call without continuation_id
mcp__exai-mcp__chat(
    prompt="Follow-up question"
)
```

### Why This Error Occurred
- `continuation_id` is part of the **platform's conversation management**, not the tool's API
- It's **returned in the response metadata**, not passed as input
- The platform handles context automatically
- DO NOT pass it as a parameter to any tool

---

## Issue 2: File Request Instead of Analysis

### ❌ Error Encountered
I asked EXAI to review information I provided:
```
"Please review the EXAI MCP ARCHITECTURE.md file I created"
```
EXAI responded: *"Please provide the EXAI_MCP_ARCHITECTURE.md file so I can review"*

### ✅ Solution
**Provide the information directly in the prompt** rather than asking EXAI to "provide" or access files.

**Correct Pattern:**
```python
# Instead of asking to "provide files"
# Provide the content directly
mcp__exai-mcp__chat(
    prompt="""I created an architecture document with this content:

[PASTE YOUR CONTENT HERE]

Please review and validate this information.
"""
)
```

### Why This Error Occurred
- EXAI's file handling is optimized for code analysis, not general content review
- For conceptual analysis, provide information directly in the prompt
- File tools are best for: code files, large documents, binary files
- Not for: conceptual review of information you've already typed

---

## Issue 3: Invalid Parameters for Chat Tool

### ❌ Valid Parameters for `chat` Tool
Based on the tool schema, these are the **valid** parameters:
- `prompt` (required)
- `files` (optional) - small files <5KB
- `file_ids` (optional) - uploaded file IDs
- `use_websearch` (optional)
- `stream` (optional)
- `model` (optional - auto-selected if not specified)
- `temperature` (optional)
- `tool_choice` (optional)
- `tools` (optional)

### ❌ Invalid Parameters
These will cause errors:
- `continuation_id` ❌ (handled automatically)
- `context` ❌ (part of prompt)
- `session_id` ❌ (not used in this implementation)
- `messages` ❌ (not the right format)

---

## Valid Tool Parameters Reference

### chat
```python
mcp__exai-mcp__chat(
    prompt="Your question or message",
    files=["c:/path/to/small_file.py"],  # Optional: small files <5KB
    file_ids=["uploaded_file_id"],       # Optional: large files
    use_websearch=True,                  # Optional: enable web search
    stream=False,                        # Optional: streaming responses
    model="glm-4.6",                     # Optional: specific model
    temperature=0.7                      # Optional: creativity level
)
```

### status
```python
mcp__exai-mcp__status(
    # No parameters typically required
)
```

### version
```python
mcp__exai-mcp__version(
    # No parameters typically required
)
```

### analyze
```python
mcp__exai-mcp__analyze(
    step="Your analysis step",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="What you discovered",
    relevant_files=["c:/path/to/file.py"],  # Required: files to analyze
    files_checked=["c:/path/to/file.py"],   # Required: all files examined
    confidence="high",
    model="glm-4.6"
)
```

### codereview
```python
mcp__exai-mcp__codereview(
    step="Your review step",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Your findings",
    relevant_files=["c:/path/to/file.py"],
    files_checked=["c:/path/to/file.py"],
    focus_on=["security", "performance"],
    review_type="full",  # "full", "security", "performance", "quick"
    severity_filter="all",
    standards="Your coding standards"
)
```

### debug
```python
mcp__exai-mcp__debug(
    step="Your debugging step",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Current findings",
    hypothesis="Your theory about the bug",
    relevant_files=["c:/path/to/file.py"],
    files_checked=["c:/path/to/file.py"],
    model="glm-4.6"
)
```

### thinkdeep
```python
mcp__exai-mcp__thinkdeep(
    step="Your reasoning step",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Your findings",
    hypothesis="Your current theory",
    problem_context="Detailed context of the problem",
    relevant_files=["c:/path/to/file.py"],
    focus_areas=["architecture", "performance"],
    model="glm-4.6"
)
```

---

## Correct Conversation Patterns

### Pattern 1: Basic Q&A
```python
# Initial question
response1 = mcp__exai-mcp__chat(
    prompt="What is the EXAI MCP Server?"
)

# Follow-up (automatically maintains context)
response2 = mcp__exai-mcp__chat(
    prompt="How does the WebSocket shim work?"
)
# No continuation_id needed - context is maintained
```

### Pattern 2: Review Specific Content
```python
# Instead of: "Please review file X"
# Do this:
content = "PASTE THE ACTUAL CONTENT HERE"
mcp__exai-mcp__codereview(
    step="Review the provided code",
    findings="The code does Y which is good because Z",
    relevant_files=[],
    files_checked=[],
    focus_on=["readability", "performance"]
)
```

### Pattern 3: File Analysis
```python
# For small files
mcp__exai-mcp__chat(
    prompt="Review this code",
    files=["c:/Project/EX-AI-MCP-Server/run_ws_shim.py"]
)

# For large files or multi-turn analysis
file_ids = kimi_upload_files(["c:/path/to/large_doc.pdf"])
mcp__exai-mcp__analyze(
    step="Analyze the uploaded document",
    findings="Key findings from document",
    relevant_files=[],
    files_checked=[],
    file_ids=file_ids
)
```

---

## Best Practices Summary

### ✅ DO
1. **Use valid parameters** only (check tool schema)
2. **Provide content directly** for conceptual review
3. **Use full absolute paths** for files
4. **Let the system handle context** automatically
5. **Use appropriate tools** for the task (chat vs analyze vs debug)
6. **Keep files under 5KB** for `files` parameter
7. **Use `file_ids`** for large files or uploaded content

### ❌ DON'T
1. **Don't pass `continuation_id`** as a parameter
2. **Don't ask to "provide files"** for conceptual review
3. **Don't use relative paths** ("../file.py")
4. **Don't mix `files` and `file_ids`** in the same call
5. **Don't use invalid parameters** (check the schema)
6. **Don't over-engineer** simple tasks
7. **Don't create wrapper abstractions** unnecessarily

---

## File Handling Strategy

### When to Use `files` vs `file_ids`

#### Use `files` for:
- Small files (<5KB)
- Code files for review
- Single-use analysis
- Quick checks

```python
mcp__exai-mcp__chat(
    prompt="Explain this function",
    files=["c:/Project/EX-AI-MCP-Server/src/main.py"]
)
```

#### Use `file_ids` for:
- Large files (>5KB)
- Multi-file analysis
- Complex reviews
- Persistent reference

```python
# First: Upload
file_ids = kimi_upload_files(["c:/path/to/large_document.pdf"])

# Then: Analyze
mcp__exai-mcp__analyze(
    step="Analyze the document",
    findings="Key insights",
    file_ids=file_ids
)
```

---

## Workflow Recommendations

### For Quick Questions
```python
mcp__exai-mcp__chat(prompt="Your question")
```

### For Code Review
```python
mcp__exai-mcp__codereview(
    step="Review the code",
    relevant_files=["c:/path/to/file.py"],
    focus_on=["style", "performance"],
    review_type="full"
)
```

### For Debugging
```python
mcp__exai-mcp__debug(
    step="Investigate the error",
    findings="Error occurs at line 42",
    hypothesis="可能是异步操作的问题",
    relevant_files=["c:/path/to/file.py"]
)
```

### For Analysis
```python
mcp__exai-mcp__analyze(
    step="Analyze architecture",
    findings="5-layer architecture identified",
    confidence="high",
    relevant_files=["c:/path/to/config.py"]
)
```

### For Deep Thinking
```python
mcp__exai-mcp__thinkdeep(
    step="Reason through the problem",
    findings="Current state analysis",
    hypothesis="Proposed solution",
    problem_context="Detailed problem description"
)
```

---

## Error Messages & Solutions

### Error: "Provider error (GLM): Completions.create() got an unexpected keyword argument 'continuation_id'"
**Solution:** Remove `continuation_id` from parameters. Context is maintained automatically.

### Error: "File required" or "file_ids required"
**Solution:** Use `files` parameter for small files, `file_ids` for uploaded files.

### Error: "Invalid parameter 'X'"
**Solution:** Check the tool schema and use only valid parameters.

### Error: "File not found" or path errors
**Solution:** Use full absolute paths like `"c:/Project/file.py"` not `"./file.py"`.

---

## Quick Reference Card

### Essential Commands
```python
# Chat
chat("Your question")

# Review
codereview(
    relevant_files=["c:/path/to/file.py"],
    focus_on=["style"]
)

# Analyze
analyze(
    findings="Analysis results",
    relevant_files=["c:/path/to/file.py"]
)

# Debug
debug(
    step="investigate",
    findings="Current findings",
    relevant_files=["c:/path/to/file.py"]
)

# Think Deep
thinkdeep(
    step="reason",
    findings="Insights",
    problem_context="Context"
)
```

### File Parameters
```python
# Small files
files=["c:/path/to/small_file.py"]

# Large files
file_ids=["uploaded_file_id"]
```

### Optional Parameters
```python
use_websearch=True      # Enable web search
stream=False            # Streaming responses
model="glm-4.6"         # Specific model
temperature=0.7         # Creativity level
```

---

## Conclusion

By following these patterns, you can avoid the common issues:
1. ✅ No more `continuation_id` errors
2. ✅ No more file request confusion
3. ✅ No more invalid parameter errors
4. ✅ Effective use of all 21 EXAI tools
5. ✅ Smooth conversation flow

**Remember:** The platform handles context automatically. Just use the right tool with the right parameters!
