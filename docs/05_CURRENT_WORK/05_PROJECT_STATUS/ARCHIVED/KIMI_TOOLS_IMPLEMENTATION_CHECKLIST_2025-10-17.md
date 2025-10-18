# Kimi File Tools Implementation Checklist - 2025-10-17

**Date:** 2025-10-17 (Melbourne/Australia AEDT)  
**Status:** 🚧 IN PROGRESS  
**EXAI Consultation ID:** 388a0622-02af-46f6-9254-36924d529b32  
**Confidence:** Very High

---

## 📋 COMPLETE END-TO-END CHECKLIST

### **Phase 1: Delete Old Tools**

- [ ] **DELETE:** `tools/providers/kimi/kimi_upload.py`
  - Contains `KimiUploadAndExtractTool` (lines 18-437)
  - Contains `KimiMultiFileChatTool` (lines 441-572)
  - **Action:** Remove entire file

---

### **Phase 2: Create New Tools**

- [ ] **CREATE:** `tools/providers/kimi/kimi_files.py`
  - Tool 1: `KimiUploadFilesTool` - Upload only, return file IDs
  - Tool 2: `KimiChatWithFilesTool` - Chat with file IDs
  - Tool 3: `KimiManageFilesTool` - List/delete/info operations
  - **Lines:** ~600-800 (estimated)

---

### **Phase 3: Update Tool Registry (PRIMARY)**

- [ ] **MODIFY:** `tools/registry.py`
  
  **Remove (lines 42-43):**
  ```python
  "kimi_upload_and_extract": ("tools.providers.kimi.kimi_upload", "KimiUploadAndExtractTool"),
  "kimi_multi_file_chat": ("tools.providers.kimi.kimi_upload", "KimiMultiFileChatTool"),
  ```
  
  **Add:**
  ```python
  "kimi_upload_files": ("tools.providers.kimi.kimi_files", "KimiUploadFilesTool"),
  "kimi_chat_with_files": ("tools.providers.kimi.kimi_files", "KimiChatWithFilesTool"),
  "kimi_manage_files": ("tools.providers.kimi.kimi_files", "KimiManageFilesTool"),
  ```
  
  **Remove (line 85):**
  ```python
  "kimi_upload_and_extract": "advanced",
  ```
  
  **Add:**
  ```python
  "kimi_upload_files": "advanced",
  "kimi_chat_with_files": "core",  # Core tool for file-based analysis
  "kimi_manage_files": "advanced",
  ```

---

### **Phase 4: Update Tool Registry (SECONDARY)**

- [ ] **MODIFY:** `src/bootstrap/singletons.py`
  
  **Remove (lines 148-150):**
  ```python
  kimi_tools = [
      ("kimi_multi_file_chat", ("tools.providers.kimi.kimi_upload", "KimiMultiFileChatTool")),
      ("kimi_intent_analysis", ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool")),
  ]
  ```
  
  **Replace with:**
  ```python
  kimi_tools = [
      ("kimi_upload_files", ("tools.providers.kimi.kimi_files", "KimiUploadFilesTool")),
      ("kimi_chat_with_files", ("tools.providers.kimi.kimi_files", "KimiChatWithFilesTool")),
      ("kimi_manage_files", ("tools.providers.kimi.kimi_files", "KimiManageFilesTool")),
      ("kimi_intent_analysis", ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool")),
  ]
  ```

---

### **Phase 5: Update Environment Files**

- [ ] **MODIFY:** `.env.example`
  
  **Current (line 281):**
  ```bash
  KIMI_FILES_MAX_SIZE_MB=20  # Maximum file size for Kimi uploads (MB)
  ```
  
  **Add after line 281:**
  ```bash
  # Kimi File Upload Configuration
  KIMI_FILES_PARALLEL_UPLOADS=true  # Enable parallel file uploads
  KIMI_FILES_MAX_PARALLEL=3  # Maximum concurrent uploads
  KIMI_FILES_UPLOAD_TIMEOUT_SECS=90  # Upload timeout per file
  KIMI_FILES_FETCH_TIMEOUT_SECS=25  # Content fetch timeout per file
  KIMI_FILES_MAX_COUNT=0  # Max files per batch (0=unlimited)
  KIMI_FILES_BEHAVIOR_ON_OVERSIZE=skip  # skip|fail on oversize files
  KIMI_FILES_FETCH_RETRIES=3  # Retry attempts for content fetch
  KIMI_FILES_FETCH_BACKOFF=0.8  # Backoff multiplier for retries
  KIMI_FILES_FETCH_INITIAL_DELAY=0.5  # Initial delay before retry (seconds)
  KIMI_MF_CHAT_TIMEOUT_SECS=180  # Multi-file chat total timeout
  ```

- [ ] **MODIFY:** `.env` (user's file)
  - Add any missing env vars from above
  - Keep existing values

---

### **Phase 6: Create Supabase Migration**

- [ ] **CREATE:** `supabase/migrations/YYYYMMDDHHMMSS_create_kimi_file_uploads.sql`
  
  ```sql
  -- Kimi File Uploads Tracking Table
  CREATE TABLE IF NOT EXISTS kimi_file_uploads (
      id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
      file_id TEXT NOT NULL,  -- Moonshot file ID
      filename TEXT NOT NULL,
      sha256 TEXT NOT NULL,
      provider TEXT NOT NULL DEFAULT 'KIMI',
      file_size_bytes BIGINT,
      upload_timestamp TIMESTAMPTZ DEFAULT NOW(),
      last_used TIMESTAMPTZ DEFAULT NOW(),
      purpose TEXT DEFAULT 'file-extract',
      UNIQUE(sha256, provider)
  );
  
  -- Indexes for performance
  CREATE INDEX IF NOT EXISTS idx_kimi_file_uploads_file_id 
      ON kimi_file_uploads(file_id);
  CREATE INDEX IF NOT EXISTS idx_kimi_file_uploads_sha256 
      ON kimi_file_uploads(sha256);
  CREATE INDEX IF NOT EXISTS idx_kimi_file_uploads_last_used 
      ON kimi_file_uploads(last_used);
  
  -- Comments
  COMMENT ON TABLE kimi_file_uploads IS 'Tracks files uploaded to Moonshot/Kimi for reuse and cleanup';
  COMMENT ON COLUMN kimi_file_uploads.file_id IS 'Moonshot-assigned file ID';
  COMMENT ON COLUMN kimi_file_uploads.sha256 IS 'SHA256 hash for deduplication';
  COMMENT ON COLUMN kimi_file_uploads.last_used IS 'Last time file was referenced in chat';
  ```

---

### **Phase 7: Update Documentation**

- [ ] **MODIFY:** `docs/05_CURRENT_WORK/05_PROJECT_STATUS/KIMI_TOOL_USAGE_LESSONS_2025-10-17.md`
  - Update tool names
  - Update usage examples
  - Mark old patterns as deprecated

- [ ] **MODIFY:** `docs/03_API_REFERENCE/02_API_REFERENCE/KIMI_API_REFERENCE.md`
  - Remove old tool documentation
  - Add new tool documentation
  - Update examples

---

## 🎯 Implementation Order

**Step 1:** Create new tools file
**Step 2:** Update both tool registries
**Step 3:** Delete old tools file
**Step 4:** Update environment files
**Step 5:** Create Supabase migration
**Step 6:** Update documentation
**Step 7:** Test with Docker restart

---

## ✅ Verification Checklist

After implementation, verify:

- [ ] Old tools file deleted
- [ ] New tools file created with all three tools
- [ ] Tool registry (primary) updated
- [ ] Tool registry (secondary) updated
- [ ] .env.example updated with all env vars
- [ ] .env updated (user's file)
- [ ] Supabase migration created
- [ ] Documentation updated
- [ ] Docker container restarts successfully
- [ ] New tools appear in tool list
- [ ] Old tools do NOT appear in tool list
- [ ] Can upload files and get file IDs
- [ ] Can chat with uploaded file IDs
- [ ] Can list/delete files

---

## 🚨 Critical Notes

1. **No Deprecation** - Old tools removed completely, no warnings
2. **Two Registries** - Must update BOTH `tools/registry.py` AND `src/bootstrap/singletons.py`
3. **Env Vars** - Many already exist in code, just need documentation
4. **Supabase** - Migration must be run before using new tools
5. **Testing** - Must restart Docker + toggle Augment settings

---

**Status:** Ready for implementation! 🚀

