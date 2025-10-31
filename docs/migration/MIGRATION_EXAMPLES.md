# Migration Examples - Deprecated Tools → smart_file_query

**Date:** 2025-10-30  
**Phase:** A2 Week 2  
**Purpose:** Concrete examples for migrating from deprecated file tools to smart_file_query

---

## 🎯 Why Migrate?

**Benefits of smart_file_query:**
- ✅ 70-80% token savings (automatic SHA256 deduplication)
- ✅ Automatic provider selection (Kimi vs GLM based on file size)
- ✅ Automatic fallback on provider failure
- ✅ Centralized Supabase tracking
- ✅ Single unified interface
- ✅ Rate limiting and audit logging (Phase A2)
- ✅ Application-aware file handling

---

## 📋 Migration Examples

### 1. kimi_upload_files → smart_file_query

**OLD PATTERN (2 steps):**
```python
# Step 1: Upload file
upload_result = kimi_upload_files(
    files=['/mnt/project/EX-AI-MCP-Server/src/file.py']
)
file_id = upload_result[0]['file_id']

# Step 2: Chat with file
result = kimi_chat_with_files(
    file_ids=[file_id],
    prompt='Analyze this code for security issues'
)
```

**NEW PATTERN (1 step):**
```python
# Single unified call
result = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file.py',
    question='Analyze this code for security issues',
    provider='auto',  # Optional: automatic selection
    model='auto'      # Optional: automatic selection
)
```

**Benefits:**
- 50% fewer API calls
- Automatic deduplication (reuses existing uploads)
- No need to manage file IDs manually
- Automatic provider selection

---

### 2. kimi_chat_with_files → smart_file_query

**OLD PATTERN:**
```python
# Assumes file already uploaded
result = kimi_chat_with_files(
    file_ids=['d41itf21ol7h6f1h6rf0'],
    prompt='What are the main functions in this file?',
    model='kimi-k2-0905-preview'
)
```

**NEW PATTERN:**
```python
# Upload + query in one call (automatic deduplication)
result = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file.py',
    question='What are the main functions in this file?',
    model='kimi-k2-0905-preview'
)
```

**Benefits:**
- No need to track file IDs
- Automatic deduplication (won't re-upload if file already exists)
- Simpler API

---

### 3. glm_upload_file → smart_file_query

**OLD PATTERN:**
```python
# Upload file to GLM
upload_result = glm_upload_file(
    file='/mnt/project/EX-AI-MCP-Server/src/small_file.py',
    purpose='agent'
)
file_id = upload_result['file_id']

# Note: GLM files expire after 24 hours and must be re-uploaded
```

**NEW PATTERN:**
```python
# Automatic provider selection (uses Kimi for persistence)
result = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/small_file.py',
    question='Analyze this code',
    provider='auto'  # Automatically selects Kimi for file persistence
)
```

**Benefits:**
- Files persist across sessions (Kimi provider)
- No 24-hour expiration
- Automatic deduplication

---

### 4. glm_multi_file_chat → smart_file_query (Multiple Files)

**OLD PATTERN:**
```python
# Upload multiple files to GLM
result = glm_multi_file_chat(
    files=[
        '/mnt/project/EX-AI-MCP-Server/src/file1.py',
        '/mnt/project/EX-AI-MCP-Server/src/file2.py'
    ],
    prompt='Compare these two files',
    model='glm-4.6'
)
```

**NEW PATTERN:**
```python
# Option 1: Upload files separately, then query
file1_result = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file1.py',
    question='Summarize this file'
)

file2_result = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file2.py',
    question='Summarize this file'
)

# Then compare in a follow-up query
comparison = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file1.py',
    question=f'Compare this file with file2.py. File2 summary: {file2_result}'
)

# Option 2: Use continuation_id for multi-turn conversation
result1 = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file1.py',
    question='Analyze this file',
    continuation_id='comparison-session'
)

result2 = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file2.py',
    question='Compare this with the previous file',
    continuation_id='comparison-session'  # Same ID maintains context
)
```

**Benefits:**
- Files persist across sessions
- Automatic deduplication
- Better context management with continuation_id

---

## 🔧 Advanced Migration Patterns

### Pattern 1: Batch File Analysis

**OLD:**
```python
for file_path in file_list:
    upload_result = kimi_upload_files(files=[file_path])
    file_id = upload_result[0]['file_id']
    result = kimi_chat_with_files(file_ids=[file_id], prompt='Analyze')
```

**NEW:**
```python
for file_path in file_list:
    result = smart_file_query(
        file_path=file_path,
        question='Analyze this code for security issues'
    )
    # Automatic deduplication - won't re-upload duplicates
```

---

### Pattern 2: Large File Handling

**OLD:**
```python
# Manual provider selection based on file size
if file_size_mb > 20:
    upload_result = kimi_upload_files(files=[file_path])
else:
    upload_result = glm_upload_file(file=file_path)
```

**NEW:**
```python
# Automatic provider selection based on file size
result = smart_file_query(
    file_path=file_path,
    question='Analyze this file',
    provider='auto'  # Automatically selects best provider
)
```

---

### Pattern 3: Error Handling with Fallback

**OLD:**
```python
try:
    upload_result = kimi_upload_files(files=[file_path])
except Exception as e:
    # Manual fallback to GLM
    upload_result = glm_upload_file(file=file_path)
```

**NEW:**
```python
# Automatic fallback built-in
result = smart_file_query(
    file_path=file_path,
    question='Analyze this file'
)
# Automatically tries Kimi first, falls back to GLM on failure
```

---

## 📊 Migration Checklist

- [ ] Identify all uses of deprecated tools in your codebase
- [ ] Replace `kimi_upload_files` + `kimi_chat_with_files` with `smart_file_query`
- [ ] Replace `glm_upload_file` with `smart_file_query`
- [ ] Replace `glm_multi_file_chat` with `smart_file_query` (use continuation_id for multi-file)
- [ ] Remove manual file ID tracking
- [ ] Remove manual provider selection logic
- [ ] Remove manual fallback error handling
- [ ] Test with existing file paths
- [ ] Verify deduplication is working (check logs for "Deduplication HIT")
- [ ] Monitor deprecation metrics in Supabase

---

## 🚀 Quick Reference

**Single File Query:**
```python
smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file.py',
    question='Analyze this code'
)
```

**With Specific Provider:**
```python
smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file.py',
    question='Analyze this code',
    provider='kimi'  # Force Kimi provider
)
```

**With Specific Model:**
```python
smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file.py',
    question='Analyze this code',
    model='kimi-k2-0905-preview'
)
```

**Multi-Turn Conversation:**
```python
# First query
result1 = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file1.py',
    question='Analyze this file',
    continuation_id='my-session'
)

# Follow-up query (maintains context)
result2 = smart_file_query(
    file_path='/mnt/project/EX-AI-MCP-Server/src/file2.py',
    question='Compare with previous file',
    continuation_id='my-session'
)
```

---

## 📝 Need Help?

- **Documentation:** See `docs/migration/SMART_FILE_QUERY_USAGE_GUIDE.md`
- **Architecture:** See `docs/05_CURRENT_WORK/2025-10-30/FILE_TOOL_ARCHITECTURE_ANALYSIS.md`
- **Issues:** Check deprecation metrics in Supabase `deprecation_summary` view

---

**Migration Timeline:** 3-month transition period (ends 2026-01-30)  
**Support:** Deprecated tools remain functional with warnings until end of transition period

