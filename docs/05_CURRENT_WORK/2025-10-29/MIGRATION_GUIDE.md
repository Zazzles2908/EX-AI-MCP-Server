# Migration Guide: Old File Tools → smart_file_query

**Date:** 2025-10-29  
**Status:** ACTIVE  
**Purpose:** Guide for migrating from deprecated file upload tools to `smart_file_query`

---

## 🎯 **OVERVIEW**

As of 2025-10-29, the following file upload tools are **DEPRECATED**:

- `kimi_upload_files` → Use `smart_file_query`
- `kimi_chat_with_files` → Use `smart_file_query`
- `glm_upload_file` → Use `smart_file_query`
- `glm_multi_file_chat` → Use `smart_file_query`

**Reason:** `smart_file_query` consolidates all file operations into ONE intelligent tool with automatic deduplication, provider selection, and fallback.

---

## ⚠️ **DEPRECATION TIMELINE**

| Date | Action |
|------|--------|
| **2025-10-29** | Deprecation warnings added to old tools |
| **2025-11-12** | Old tools moved to HIDDEN tier (2 weeks) |
| **2025-12-10** | Old tools removed from codebase (6 weeks) |

**Current Status:** Deprecation warnings active, old tools still functional

---

## 🔄 **MIGRATION EXAMPLES**

### **Example 1: Upload Files (Kimi)**

**❌ OLD WAY:**
```python
# Step 1: Upload files
result = kimi_upload_files(
    files=["/mnt/project/file1.py", "/mnt/project/file2.py"],
    purpose="file-extract"
)
file_ids = [f["file_id"] for f in result]

# Step 2: Chat with files
response = kimi_chat_with_files(
    file_ids=file_ids,
    prompt="Analyze these files for security issues",
    model="kimi-k2-0905-preview"
)
```

**✅ NEW WAY:**
```python
# ONE step - upload + query
response = smart_file_query(
    file_path="/mnt/project/file1.py",
    question="Analyze this file for security issues",
    provider="auto",  # Automatic provider selection
    model="auto"      # Automatic model selection
)

# For multiple files, call multiple times (deduplication handles efficiency)
response1 = smart_file_query(file_path="/mnt/project/file1.py", question="...")
response2 = smart_file_query(file_path="/mnt/project/file2.py", question="...")
```

---

### **Example 2: Upload Files (GLM)**

**❌ OLD WAY:**
```python
# Upload single file
result = glm_upload_file(
    file="/mnt/project/file.py",
    purpose="agent"
)
file_id = result["file_id"]

# Or upload multiple files
result = glm_multi_file_chat(
    files=["/mnt/project/file1.py", "/mnt/project/file2.py"],
    prompt="Analyze these files",
    model="glm-4.6"
)
```

**✅ NEW WAY:**
```python
# ONE step - upload + query
response = smart_file_query(
    file_path="/mnt/project/file.py",
    question="Analyze this file",
    provider="auto",  # Will select GLM for small files (<20MB)
    model="auto"
)
```

---

### **Example 3: Provider-Specific Requests**

**❌ OLD WAY:**
```python
# Force Kimi
result = kimi_upload_files(files=["/mnt/project/large_doc.pdf"])
response = kimi_chat_with_files(file_ids=result[0]["file_id"], prompt="...")

# Force GLM
result = glm_upload_file(file="/mnt/project/small_file.py")
```

**✅ NEW WAY:**
```python
# Force Kimi
response = smart_file_query(
    file_path="/mnt/project/large_doc.pdf",
    question="Summarize this document",
    provider="kimi"  # Explicit provider selection
)

# Force GLM
response = smart_file_query(
    file_path="/mnt/project/small_file.py",
    question="Analyze this code",
    provider="glm"  # Explicit provider selection
)
```

---

## 🎁 **BENEFITS OF MIGRATION**

### **1. Automatic Deduplication**
```python
# OLD: Manual tracking of uploaded files
uploaded_files = {}
if file_path not in uploaded_files:
    result = kimi_upload_files(files=[file_path])
    uploaded_files[file_path] = result[0]["file_id"]

# NEW: Automatic deduplication (SHA256-based)
smart_file_query(file_path=file_path, question="...")  # Reuses existing upload
```

### **2. Intelligent Provider Selection**
```python
# OLD: Manual provider selection based on file size
if file_size < 20_000_000:
    result = glm_upload_file(file=file_path)
else:
    result = kimi_upload_files(files=[file_path])

# NEW: Automatic provider selection
smart_file_query(file_path=file_path, question="...")  # Selects best provider
```

### **3. Automatic Fallback**
```python
# OLD: Manual fallback handling
try:
    result = glm_upload_file(file=file_path)
except Exception:
    result = kimi_upload_files(files=[file_path])  # Fallback to Kimi

# NEW: Automatic fallback
smart_file_query(file_path=file_path, question="...")  # Fallback built-in
```

### **4. Unified Interface**
```python
# OLD: Different APIs for different providers
kimi_result = kimi_upload_files(files=[...])  # Returns list of dicts
glm_result = glm_upload_file(file=...)        # Returns single dict

# NEW: Consistent API
result = smart_file_query(file_path=..., question=...)  # Always same format
```

---

## 📋 **MIGRATION CHECKLIST**

### **For Agents:**
- [ ] Replace all `kimi_upload_files` calls with `smart_file_query`
- [ ] Replace all `kimi_chat_with_files` calls with `smart_file_query`
- [ ] Replace all `glm_upload_file` calls with `smart_file_query`
- [ ] Replace all `glm_multi_file_chat` calls with `smart_file_query`
- [ ] Remove manual deduplication logic (smart_file_query handles it)
- [ ] Remove manual provider selection logic (smart_file_query handles it)
- [ ] Remove manual fallback logic (smart_file_query handles it)

### **For Developers:**
- [ ] Update documentation to reference `smart_file_query`
- [ ] Update examples to use `smart_file_query`
- [ ] Update tests to use `smart_file_query`
- [ ] Remove references to deprecated tools from guides

---

## ⚠️ **BREAKING CHANGES**

### **None!**

The migration is **100% backward compatible**:
- Old tools still work (with deprecation warnings)
- No code breaks during migration period
- Gradual migration is safe

---

## 🔧 **TROUBLESHOOTING**

### **Issue: "File already uploaded" error**

**Cause:** Deduplication detected existing upload

**Solution:** This is expected behavior! `smart_file_query` reuses existing uploads for efficiency.

---

### **Issue: "Provider selection failed"**

**Cause:** File size exceeds all provider limits (>100MB)

**Solution:** Split large files or compress before uploading

---

### **Issue: "Path validation failed"**

**Cause:** Using Windows paths or relative paths

**Solution:** Use Linux container paths: `/mnt/project/...`

```python
# ❌ WRONG
smart_file_query(file_path="c:\\Project\\file.py", ...)
smart_file_query(file_path="./file.py", ...)

# ✅ CORRECT
smart_file_query(file_path="/mnt/project/EX-AI-MCP-Server/file.py", ...)
```

---

## 📊 **MIGRATION PROGRESS TRACKING**

Track your migration progress:

| Component | Old Tools Used | Migrated to smart_file_query | Status |
|-----------|----------------|------------------------------|--------|
| Tool A | ✅ | ✅ | Complete |
| Tool B | ✅ | ⏳ | In Progress |
| Tool C | ✅ | ❌ | Not Started |

---

## 🔗 **ADDITIONAL RESOURCES**

- **Quick Start Guide:** `docs/00_Quick_Start_Guide.md`
- **Tool Decision Tree:** `docs/01_Tool_Decision_Tree.md`
- **Implementation Report:** `docs/05_CURRENT_WORK/2025-10-29/IMPLEMENTATION_COMPLETE_REPORT.md`
- **Tool Categorization:** `docs/01_Core_Architecture/02_SDK_Integration.md`

---

## 💡 **NEED HELP?**

**For migration questions:**
```python
chat(prompt="How do I migrate from kimi_upload_files to smart_file_query?")
```

**For technical issues:**
```python
debug(
    step="Investigate smart_file_query migration issue",
    hypothesis="Path format incorrect",
    ...
)
```

---

**Migration is simple, safe, and provides immediate benefits. Start today!** ✅

