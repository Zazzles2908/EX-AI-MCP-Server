# EXAI Tools - Quick Reference Cheat Sheet

## ⚠️ Critical: Avoid These Errors!

### ❌ DO NOT USE `continuation_id` as a parameter
```python
# WRONG - This causes error!
mcp__exai-mcp__chat(prompt="Hello", continuation_id="123")

# CORRECT - Platform handles context automatically
mcp__exai-mcp__chat(prompt="Hello")
```

---

## ✅ Valid Tool Parameters

### chat
```python
mcp__exai-mcp__chat(
    prompt="Your question",          # Required
    files=["c:/path/to/file.py"],   # Optional: small files <5KB
    file_ids=["uploaded_id"],       # Optional: uploaded files
    use_websearch=True,             # Optional
    stream=False,                   # Optional
    model="glm-4.6",                # Optional
    temperature=0.7                 # Optional
)
```

### status
```python
mcp__exai-mcp__status()
# No parameters needed
```

### version
```python
mcp__exai-mcp__version()
# No parameters needed
```

### analyze
```python
mcp__exai-mcp__analyze(
    step="Your step",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="What you found",
    relevant_files=["c:/path/to/file.py"],
    files_checked=["c:/path/to/file.py"],
    confidence="high"
)
```

### codereview
```python
mcp__exai-mcp__codereview(
    step="Your step",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Your findings",
    relevant_files=["c:/path/to/file.py"],
    files_checked=["c:/path/to/file.py"],
    focus_on=["security", "performance"],
    review_type="full"
)
```

### debug
```python
mcp__exai-mcp__debug(
    step="investigate",
    findings={"error": "details"},
    hypothesis="your theory",
    relevant_files=["c:/path/to/file.py"]
)
```

### thinkdeep
```python
mcp__exai-mcp__thinkdeep(
    step="reason",
    findings="insights",
    hypothesis="theory",
    problem_context="details"
)
```

---

## File Handling

### For Small Files (<5KB)
```python
mcp__exai-mcp__chat(
    prompt="Review this",
    files=["c:/Project/EX-AI-MCP-Server/src/main.py"]
)
```

### For Large Files (>5KB)
```python
# 1. Upload first
file_ids = kimi_upload_files(["c:/path/to/large_file.pdf"])

# 2. Use file_ids
mcp__exai-mcp__chat(
    prompt="Analyze this",
    file_ids=file_ids
)
```

### Path Rules
- ✅ Always use FULL ABSOLUTE paths
- ❌ Don't use relative paths ("./file.py")
- Example: `"c:/Project/EX-AI-MCP-Server/src/main.py"`

---

## Common Errors & Solutions

| Error | Cause | Fix |
|-------|-------|-----|
| `continuation_id` parameter error | Using it as input | Remove it - platform handles context |
| `file_ids` required | Not providing files | Use `files` or `file_ids` parameter |
| File not found | Relative path | Use full absolute path: `c:/path/file.py` |
| Invalid parameter 'X' | Wrong parameter name | Check tool schema |

---

## Quick Examples

### Q&A
```python
mcp__exai-mcp__chat(prompt="What is WebSocket?")
```

### Review Code
```python
mcp__exai-mcp__codereview(
    relevant_files=["c:/path/to/code.py"],
    focus_on=["style", "performance"]
)
```

### Analyze Files
```python
mcp__exai-mcp__analyze(
    step="Analyze architecture",
    findings="5-layer system",
    relevant_files=["c:/path/to/config.py"]
)
```

### Debug Issue
```python
mcp__exai-mcp__debug(
    step="Investigate error",
    findings="Error at line 42",
    hypothesis="async issue",
    relevant_files=["c:/path/to/file.py"]
)
```

---

## Best Practices

### ✅ DO
- Use valid parameters only
- Provide content directly for review
- Use full absolute paths
- Let platform handle context
- Use appropriate tools

### ❌ DON'T
- Use `continuation_id` parameter
- Ask to "provide files" for concepts
- Use relative paths
- Mix `files` and `file_ids`
- Use invalid parameters

---

## Conversation Flow

**Pattern:**
```python
# Call 1
response1 = mcp__exai-mcp__chat(prompt="Question 1")

# Call 2 - context automatically maintained
response2 = mcp__exai-mcp__chat(prompt="Question 2")

# Call 3 - still connected
response3 = mcp__exai-mcp__chat(prompt="Question 3")
```

**No need for:** continuation_id, session_id, or manual context management!

---

## 21 Tools Quick List

### Essential (3)
- status
- chat
- planner

### Core (7)
- analyze
- codereview
- debug
- refactor
- testgen
- thinkdeep
- smart_file_query

### Advanced (7)
- consensus
- docgen
- secaudit
- tracer
- precommit
- kimi_chat_with_tools
- glm_payload_preview

### Hidden (4)
- Diagnostic tools

---

## Need More Help?

- **Full Guide**: `docs/development/exai-tool-usage-guide.md`
- **Issues Fixed**: `docs/EXAI_TOOL_ISSUES_FIXED.md`
- **Architecture**: `docs/architecture/exai-mcp-architecture.md`
- **Troubleshooting**: `docs/troubleshooting/README.md`

---

**Remember: The platform handles context automatically. Just use valid parameters! ✅**
