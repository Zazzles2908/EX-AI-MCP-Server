# smart_file_query - Complete Usage Guide

**Last Updated:** 2025-10-30  
**Status:** ✅ RECOMMENDED PRIMARY INTERFACE  
**Replaces:** kimi_upload_files, kimi_chat_with_files, glm_upload_file, glm_multi_file_chat

---

## 🎯 QUICK START

### Basic File Analysis

```python
# Analyze a single file
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",
    question="Analyze this code for security issues"
)
```

### Multiple Files

```python
# Analyze multiple files
smart_file_query(
    file_path=[
        "/mnt/project/file1.py",
        "/mnt/project/file2.py",
        "/mnt/project/file3.py"
    ],
    question="Compare these implementations and identify common patterns"
)
```

### With Specific Provider

```python
# Force specific provider (Kimi recommended for files)
smart_file_query(
    file_path="/mnt/project/document.pdf",
    question="Summarize the key points from this document",
    provider="kimi"  # Always recommended for files
)
```

---

## 📚 MIGRATION FROM LEGACY TOOLS

### From kimi_upload_files + kimi_chat_with_files

**OLD PATTERN (2 steps):**
```python
# Step 1: Upload files
file_ids = kimi_upload_files(files=["file1.py", "file2.py"])

# Step 2: Chat with files
result = kimi_chat_with_files(
    prompt="Analyze these files for security vulnerabilities",
    file_ids=[f["file_id"] for f in file_ids]
)
```

**NEW PATTERN (1 step):**
```python
result = smart_file_query(
    file_path=["file1.py", "file2.py"],
    question="Analyze these files for security vulnerabilities"
)
```

**Benefits:**
- ✅ 50% less code
- ✅ 70-80% token savings (automatic deduplication)
- ✅ Single unified interface
- ✅ Better error handling

---

### From glm_upload_file + glm_multi_file_chat

**OLD PATTERN:**
```python
# Upload file
file_id = glm_upload_file(file="document.pdf")

# Chat with file
result = glm_multi_file_chat(
    files=["document.pdf"],
    prompt="Summarize this document",
    model="glm-4.5",
    temperature=0.3
)
```

**NEW PATTERN:**
```python
result = smart_file_query(
    file_path="document.pdf",
    question="Summarize this document",
    temperature=0.3
)
```

**Benefits:**
- ✅ Automatic provider selection (uses Kimi for files)
- ✅ No need to manage file IDs
- ✅ Persistent file storage (Kimi)
- ✅ Automatic fallback on failure

---

## 🔧 ADVANCED USAGE PATTERNS

### Batch Processing

```python
# Process multiple files with different questions
files = ["file1.py", "file2.py", "file3.py"]
questions = [
    "What does this file do?",
    "Are there any security issues?",
    "What are the performance characteristics?"
]

results = []
for file_path, question in zip(files, questions):
    result = smart_file_query(file_path=file_path, question=question)
    results.append(result)
```

### Custom Provider Selection

```python
# Force Kimi for large files (100MB limit)
smart_file_query(
    file_path="large_document.pdf",
    question="Analyze this document",
    provider="kimi"
)

# Auto-select based on file size (recommended)
smart_file_query(
    file_path="any_file.txt",
    question="Analyze this file",
    provider="auto"  # Default: automatically selects Kimi for files
)
```

### Error Handling

```python
try:
    result = smart_file_query(
        file_path="/path/to/file.py",
        question="Analyze this code"
    )
    
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print(f"Analysis: {result['response']}")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Streaming Responses

```python
# Request streaming for long responses
result = smart_file_query(
    file_path="large_codebase.py",
    question="Provide detailed analysis",
    stream=True  # Enable streaming if supported
)
```

---

## 💡 BEST PRACTICES

### 1. File Path Format

**✅ CORRECT:**
```python
# Linux container paths (inside Docker)
smart_file_query(file_path="/mnt/project/EX-AI-MCP-Server/src/file.py", ...)

# Windows paths (converted automatically)
smart_file_query(file_path="C:\\Project\\EX-AI-MCP-Server\\src\\file.py", ...)
```

**❌ INCORRECT:**
```python
# Relative paths (not supported)
smart_file_query(file_path="./src/file.py", ...)

# Paths outside mounted directories
smart_file_query(file_path="/external/path/file.py", ...)  # Will fail
```

---

### 2. Provider Selection

**✅ RECOMMENDED:**
```python
# Let smart_file_query choose (always Kimi for files)
smart_file_query(file_path="file.py", question="...", provider="auto")
```

**⚠️ AVOID:**
```python
# Don't force GLM for files (no file persistence)
smart_file_query(file_path="file.py", question="...", provider="glm")
```

**Why Kimi?**
- ✅ Persistent file storage across sessions
- ✅ 100MB file limit (vs GLM's 20MB)
- ✅ Better file handling capabilities
- ✅ No need to re-upload for each query

---

### 3. Question Formulation

**✅ GOOD QUESTIONS:**
```python
# Specific and actionable
"Identify security vulnerabilities in this code"
"Explain the main algorithm used in this file"
"List all functions and their purposes"
"Compare these two implementations and recommend the better approach"
```

**❌ VAGUE QUESTIONS:**
```python
# Too broad or unclear
"What is this?"
"Analyze"
"Tell me about this file"
```

---

### 4. Performance Optimization

**Deduplication Savings:**
```python
# First upload: Full file upload
result1 = smart_file_query(file_path="large_file.py", question="Question 1")

# Subsequent queries: Uses cached file (70-80% token savings!)
result2 = smart_file_query(file_path="large_file.py", question="Question 2")
result3 = smart_file_query(file_path="large_file.py", question="Question 3")
```

**Batch Similar Files:**
```python
# More efficient than individual queries
smart_file_query(
    file_path=["file1.py", "file2.py", "file3.py"],
    question="Find common patterns across these files"
)
```

---

## 🔍 TROUBLESHOOTING

### Issue: "File not found"

**Cause:** File path is outside mounted directories  
**Solution:** Ensure file is in `/mnt/project/EX-AI-MCP-Server/` or `/mnt/project/Personal_AI_Agent/`

```python
# ✅ CORRECT
smart_file_query(file_path="/mnt/project/EX-AI-MCP-Server/src/file.py", ...)

# ❌ WRONG
smart_file_query(file_path="/external/path/file.py", ...)
```

---

### Issue: "File too large"

**Cause:** File exceeds provider limits  
**Solution:** Use Kimi (100MB limit) or split file

```python
# Force Kimi for large files
smart_file_query(
    file_path="large_file.pdf",
    question="...",
    provider="kimi"  # 100MB limit
)
```

---

### Issue: "Provider error"

**Cause:** Provider API failure  
**Solution:** smart_file_query automatically falls back to alternative provider

```python
# Automatic fallback is built-in
result = smart_file_query(file_path="file.py", question="...")

# Check which provider was used
print(f"Provider used: {result.get('provider')}")
```

---

### Issue: "Timeout"

**Cause:** Large file or complex analysis  
**Solution:** Break into smaller queries or increase timeout

```python
# Break into smaller questions
result1 = smart_file_query(file_path="large_file.py", question="List all functions")
result2 = smart_file_query(file_path="large_file.py", question="Analyze function X")
```

---

## 📊 COMPARISON: Legacy vs smart_file_query

| Feature | Legacy Tools | smart_file_query |
|---------|-------------|------------------|
| **Steps Required** | 2 (upload + query) | 1 (unified) |
| **Token Savings** | None | 70-80% (deduplication) |
| **Provider Selection** | Manual | Automatic |
| **Error Handling** | Basic | Advanced with fallback |
| **File Persistence** | Depends on provider | Always persistent (Kimi) |
| **Max File Size** | 20MB (GLM) | 100MB (Kimi) |
| **Code Complexity** | High | Low |
| **Maintenance** | Multiple tools | Single interface |

---

## 🎓 REAL-WORLD EXAMPLES

### Example 1: Code Review

```python
# Review a pull request
files = [
    "/mnt/project/src/feature.py",
    "/mnt/project/tests/test_feature.py"
]

result = smart_file_query(
    file_path=files,
    question="""
    Review this code for:
    1. Security vulnerabilities
    2. Performance issues
    3. Code quality and best practices
    4. Test coverage
    """
)
```

### Example 2: Documentation Generation

```python
# Generate documentation for a module
result = smart_file_query(
    file_path="/mnt/project/src/module.py",
    question="""
    Generate comprehensive documentation including:
    - Module overview
    - Function descriptions
    - Parameter explanations
    - Return value descriptions
    - Usage examples
    """
)
```

### Example 3: Refactoring Suggestions

```python
# Get refactoring recommendations
result = smart_file_query(
    file_path="/mnt/project/src/legacy_code.py",
    question="""
    Analyze this code and suggest refactoring opportunities:
    - Code smells
    - Decomposition possibilities
    - Modernization opportunities
    - Performance optimizations
    """
)
```

---

## 🚀 NEXT STEPS

1. **Try it now:** Replace your next legacy tool call with smart_file_query
2. **Measure savings:** Track token usage before/after migration
3. **Share feedback:** Report any issues or suggestions
4. **Explore advanced features:** Experiment with batch processing and custom providers

---

## 📝 ADDITIONAL RESOURCES

- **Architecture Analysis:** `docs/05_CURRENT_WORK/2025-10-30/FILE_TOOL_ARCHITECTURE_ANALYSIS.md`
- **Phase A1 Report:** `docs/05_CURRENT_WORK/2025-10-30/PHASE_A1_FINAL_REPORT.md`
- **Phase A2 Plan:** `docs/05_CURRENT_WORK/2025-10-30/PHASE_A2_IMPLEMENTATION_PLAN.md`
- **Migration Examples:** `docs/migration/migration_examples.py` (coming soon)

---

**Questions or Issues?**  
Consult EXAI for assistance or refer to the comprehensive architecture documentation.

**Document Status:** ✅ COMPLETE  
**Last Reviewed:** 2025-10-30

