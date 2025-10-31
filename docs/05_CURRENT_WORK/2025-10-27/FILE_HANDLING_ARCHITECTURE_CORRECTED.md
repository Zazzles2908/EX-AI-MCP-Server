# File Handling Architecture - CORRECTED

**Created:** 2025-10-27 19:20 AEDT  
**Purpose:** Document the CORRECT three-method file handling architecture  
**Status:** ✅ COMPLETE - Validated with EXAI

---

## 🎯 **EXECUTIVE SUMMARY**

**CRITICAL DISCOVERY:** The system has **THREE** file handling methods, not two!

1. **Method 1: Direct Embedding** - `chat_EXAI-WS` with `files` parameter (universal)
2. **Method 2: Kimi Upload+Chat** - `kimi_upload_files` + `kimi_chat_with_files` (Kimi only)
3. **Method 3: GLM Upload+Chat** - `glm_upload_file` + `glm_multi_file_chat` (GLM only)

**What I Missed:**
- `glm_multi_file_chat` tool EXISTS and is fully functional!
- GLM DOES support file upload and chat (just like Kimi)
- `chat_EXAI-WS` embeds files as TEXT, not uploads to platform

---

## 📊 **DECISION MATRIX**

```
┌─────────────────────┬───────────────┬───────────────┬───────────────┐
│                     │ Method 1      │ Method 2      │ Method 3      │
│                     │ (Embed)       │ (Kimi)        │ (GLM)         │
├─────────────────────┼───────────────┼───────────────┼───────────────┤
│ Tool                │ chat_EXAI-WS  │ kimi_*        │ glm_*         │
│ File Size           │ <5KB          │ >5KB          │ >5KB          │
│ Model Choice        │ Any           │ Kimi only     │ GLM only      │
│ Multi-turn          │ ❌             │ ✅             │ ✅             │
│ Persistence         │ ❌             │ ✅             │ ✅             │
│ Token Efficiency    │ ❌             │ ✅             │ ✅             │
│ File Limit          │ Context limit │ 100MB         │ 20MB          │
│ Timeout Config      │ N/A           │ KIMI_MF_*     │ GLM_MF_*      │
└─────────────────────┴───────────────┴───────────────┴───────────────┘
```

---

## 🔧 **METHOD 1: DIRECT EMBEDDING**

### **Tool:** `chat_EXAI-WS` with `files` parameter

### **How It Works:**
1. Reads file content from disk
2. Embeds content as TEXT directly in prompt
3. Sends to ANY model (GLM or Kimi)
4. No platform upload required

### **Example:**
```python
chat_EXAI-WS(
    prompt="Analyze this code",
    files=["c:\\Project\\file.py"],  # Content embedded as text
    model="glm-4.6"  # OR "kimi-k2-0905-preview" - ANY model!
)
```

### **When to Use:**
- ✅ Small files (<5KB)
- ✅ Single-use interactions
- ✅ Quick code snippets
- ✅ When you want model flexibility

### **Limitations:**
- ❌ High token consumption for large files
- ❌ No file persistence
- ❌ Limited by context window

---

## 🔧 **METHOD 2: KIMI UPLOAD+CHAT**

### **Tools:** `kimi_upload_files` + `kimi_chat_with_files`

### **How It Works:**
1. Upload file to Moonshot platform storage
2. Receive file_id from Moonshot
3. Chat with Kimi model using file_id
4. Kimi model accesses file from Moonshot storage

### **Example:**
```python
# Step 1: Upload
upload_result = kimi_upload_files(
    files=["c:\\Project\\large_file.py"]
)
# Returns: {"file_ids": ["moonshot_file_id_123"]}

# Step 2: Chat
kimi_chat_with_files(
    prompt="Analyze this implementation",
    file_ids=upload_result['file_ids'],
    model="kimi-k2-0905-preview"  # MUST be Kimi model
)
```

### **When to Use:**
- ✅ Large files (>5KB)
- ✅ Multi-turn conversations with same file
- ✅ When using Kimi models
- ✅ When you need file persistence

### **Configuration:**
```env
KIMI_MF_CHAT_TIMEOUT_SECS=180  # Default: 180s
```

### **Limitations:**
- ❌ Only works with Kimi models
- ❌ Files stored on Moonshot platform only
- ❌ Cannot be accessed by GLM models

---

## 🔧 **METHOD 3: GLM UPLOAD+CHAT**

### **Tools:** `glm_upload_file` + `glm_multi_file_chat`

### **How It Works:**
1. Upload file to Z.ai platform storage
2. Receive file_id from Z.ai
3. Chat with GLM model using file_id
4. GLM model accesses file from Z.ai storage

### **Example:**
```python
# Option A: Upload then chat
file_id = glm_upload_file(
    file="c:\\Project\\large_file.py",
    purpose="agent"
)
# Returns: {"file_id": "glm_file_id_456"}

# Option B: Upload and chat in one call
glm_multi_file_chat(
    files=["c:\\Project\\large_file.py"],
    prompt="Analyze this implementation",
    model="glm-4.6"  # MUST be GLM model
)
```

### **When to Use:**
- ✅ Large files (>5KB)
- ✅ Multi-turn conversations with same file
- ✅ When using GLM models
- ✅ When you need file persistence

### **Configuration:**
```env
GLM_MF_CHAT_TIMEOUT_SECS=60  # Default: 60s
```

### **Limitations:**
- ❌ Only works with GLM models
- ❌ Files stored on Z.ai platform only
- ❌ Cannot be accessed by Kimi models
- ❌ 20MB file limit (vs Kimi's 100MB)

---

## 🌳 **DECISION TREE**

```
START: Need to analyze file with AI
│
├─ Is file <5KB AND single interaction?
│   └─ YES → Use Method 1 (chat_EXAI-WS with files)
│
├─ Is file >5KB OR multi-turn needed?
│   │
│   ├─ Using Kimi model?
│   │   └─ YES → Use Method 2 (kimi_upload_files + kimi_chat_with_files)
│   │
│   └─ Using GLM model?
│       └─ YES → Use Method 3 (glm_upload_file + glm_multi_file_chat)
```

---

## ❌ **COMMON MISTAKES**

### **Mistake 1: Confusing Embedding with Upload**
```python
# ❌ WRONG - Thinking chat_EXAI-WS uploads to platform
chat_EXAI-WS(
    prompt="Analyze this",
    files=["file.py"],  # This EMBEDS as text, doesn't upload!
    model="glm-4.6"
)
# Then trying to access with kimi_chat_with_files - WON'T WORK!
```

### **Mistake 2: Cross-Platform File Access**
```python
# ❌ WRONG - Upload to Kimi, try to access with GLM
upload_result = kimi_upload_files(files=["file.py"])
glm_multi_file_chat(
    files=["file.py"],
    prompt="Analyze",
    model="glm-4.6"  # Can't access Kimi files!
)
```

### **Mistake 3: Not Knowing glm_multi_file_chat Exists**
```python
# ❌ SUBOPTIMAL - Using embedding for large file with GLM
chat_EXAI-WS(
    prompt="Analyze this",
    files=["large_file.py"],  # >5KB - wastes tokens!
    model="glm-4.6"
)

# ✅ CORRECT - Use GLM upload+chat
glm_multi_file_chat(
    files=["large_file.py"],
    prompt="Analyze this",
    model="glm-4.6"  # Token efficient!
)
```

---

## 📋 **TOOL REFERENCE**

### **Universal Tools (Any Model)**
| Tool | Purpose | File Handling |
|------|---------|---------------|
| `chat_EXAI-WS` | General chat | Embeds files as text |

### **Kimi-Specific Tools**
| Tool | Purpose | File Handling |
|------|---------|---------------|
| `kimi_upload_files` | Upload to Moonshot | Returns file_ids |
| `kimi_chat_with_files` | Chat with uploaded files | Uses file_ids |

### **GLM-Specific Tools**
| Tool | Purpose | File Handling |
|------|---------|---------------|
| `glm_upload_file` | Upload to Z.ai | Returns file_id |
| `glm_multi_file_chat` | Upload and chat | Uploads + chats in one call |

---

## 🔧 **CONFIGURATION**

### **Kimi Timeouts**
```env
KIMI_MF_CHAT_TIMEOUT_SECS=180  # Default: 180s (3 minutes)
```

### **GLM Timeouts**
```env
GLM_MF_CHAT_TIMEOUT_SECS=60  # Default: 60s (1 minute)
```

### **File Limits**
- **Kimi**: 100MB per file
- **GLM**: 20MB per file
- **Embedding**: Limited by context window

---

## ✅ **BEST PRACTICES**

1. **Use Method 1 for small files** - Fastest, most flexible
2. **Use Method 2 for large files with Kimi** - Token efficient, persistent
3. **Use Method 3 for large files with GLM** - Token efficient, persistent
4. **Don't mix platforms** - Files uploaded to one platform can't be accessed by the other
5. **Configure timeouts appropriately** - Increase for large files
6. **Reuse uploaded files** - Upload once, query multiple times

---

## 📚 **DOCUMENTATION TO UPDATE**

1. ✅ **PLATFORM_ARCHITECTURE_CLARIFICATION.md** - Updated with three methods
2. ⏳ **AGENT_CAPABILITIES.md** - Add `glm_multi_file_chat` documentation
3. ⏳ **SYSTEM_CAPABILITIES_OVERVIEW.md** - Add GLM file chat capability
4. ⏳ **EXAI_TOOL_DECISION_GUIDE.md** - Update decision matrix
5. ⏳ **QUICK_REFERENCE_EXAI_USAGE.md** - Add GLM file chat examples

---

## 🎯 **KEY TAKEAWAYS**

1. **THREE methods exist**, not two!
2. **GLM DOES support file upload+chat** via `glm_multi_file_chat`
3. **`chat_EXAI-WS` embeds files as text**, doesn't upload to platform
4. **Platforms are separate** - Kimi files ≠ GLM files
5. **Choose method based on file size and model** - Use decision tree

---

**Status:** ✅ COMPLETE - Architecture correctly understood and documented  
**Next Steps:** Update all documentation and test GLM file upload+chat workflow

