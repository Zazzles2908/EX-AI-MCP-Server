# Phase 2: File Storage Migration - Implementation Guide
**Date:** 2025-10-15  
**Status:** Ready to Begin  
**Prerequisites:** Phase 1 Complete ✅  
**GLM-4.6 Conversation ID:** `05660144-c47c-4b0b-b2b0-83012e53dd46`

---

## 📋 **PHASE 2 OVERVIEW**

**Goal:** Migrate file storage from local filesystem (TEST_FILES_DIR) to Supabase Storage

**Estimated Time:** 1-2 hours  
**Complexity:** Medium  
**Impact:** Enables persistent file storage across container restarts

---

## ✅ **PREREQUISITES CHECKLIST**

Before starting Phase 2, ensure:

- [x] Phase 1 complete (database schema deployed)
- [x] Supabase project active and healthy
- [x] Storage buckets created (user-files, generated-files)
- [x] Supabase Python client installed (supabase==2.22.0)
- [x] Storage manager implemented (src/storage/supabase_client.py)
- [ ] **CRITICAL:** Service role key added to .env file

---

## 🔐 **STEP 1: ADD SERVICE ROLE KEY**

**Action Required:** Manual configuration

### Get Service Role Key:

1. Go to https://supabase.com/dashboard/project/mxaazuhlqewmkweewyaz/settings/api
2. Scroll to "Project API keys" section
3. Find "service_role" key
4. Click "Reveal" to show the key
5. Copy the full key (starts with `eyJ...`)

### Update .env File:

```bash
# Open .env file and update this line:
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**Why it's needed:**
- Service role key bypasses Row Level Security (RLS)
- Required for server-side file operations
- Enables storage bucket access
- Allows database writes from storage manager

**Security Note:**
- Never commit service role key to git
- Keep it in .env file only (already in .gitignore)
- Never expose to client-side code

---

## 🧪 **STEP 2: TEST SUPABASE CONNECTION**

**Test Script:** `scripts/testing/test_supabase_connection.py`

### Run Connection Test:

```bash
# From project root
python scripts/testing/test_supabase_connection.py
```

### Expected Output:

```
================================================================================
SUPABASE CONNECTION TEST SUITE
================================================================================

================================================================================
TEST 1: Environment Variables
================================================================================
SUPABASE_URL: ✅ SET
SUPABASE_ANON_KEY: ✅ SET
SUPABASE_SERVICE_ROLE_KEY: ✅ SET

✅ All environment variables are set!

================================================================================
TEST 2: Storage Manager Initialization
================================================================================
✅ Storage manager initialized successfully!
   URL: https://mxaazuhlqewmkweewyaz.supabase.co
   Enabled: True

================================================================================
TEST 3: Database Connection
================================================================================
✅ Database connection successful!
   Schema version: 1
   Description: Initial schema: conversations, messages, files, conversation_files
   Applied at: 2025-10-15T22:33:34.781Z

================================================================================
TEST 4: Table Structure
================================================================================
✅ Table 'conversations' exists (rows: 0)
✅ Table 'messages' exists (rows: 0)
✅ Table 'files' exists (rows: 0)
✅ Table 'conversation_files' exists (rows: 0)

✅ All required tables exist!

================================================================================
TEST 5: Storage Buckets
================================================================================
✅ Bucket 'user-files' exists
   Public: False
   File size limit: 50.0 MB
✅ Bucket 'generated-files' exists
   Public: False
   File size limit: 10.0 MB

✅ All required storage buckets exist!

================================================================================
TEST 6: Conversation Operations
================================================================================
✅ Created test conversation: <uuid>
✅ Created test message: <uuid>
✅ Retrieved conversation history: 1 messages
✅ Cleaned up test data

================================================================================
TEST SUMMARY
================================================================================
Environment Variables: ✅ PASS
Storage Manager Init: ✅ PASS
Database Connection: ✅ PASS
Table Structure: ✅ PASS
Storage Buckets: ✅ PASS
Conversation Operations: ✅ PASS

Total: 6/6 tests passed

🎉 All tests passed! Supabase integration is ready!
```

### If Tests Fail:

**Missing Service Role Key:**
```
❌ SUPABASE_SERVICE_ROLE_KEY: MISSING
  → Get from: https://supabase.com/dashboard/project/mxaazuhlqewmkweewyaz/settings/api
```
→ Add service role key to .env file and rerun test

**Database Connection Failed:**
```
❌ Database connection failed: <error>
```
→ Check SUPABASE_URL is correct
→ Verify project is active in Supabase dashboard
→ Check network connectivity

**Tables Missing:**
```
❌ Table 'conversations' missing or inaccessible
```
→ Rerun Phase 1 schema deployment
→ Check Supabase dashboard SQL editor for errors

---

## 🔧 **STEP 3: INTEGRATE WITH EXISTING TOOLS**

### Tools to Update:

1. **chat_EXAI-WS** - File upload support
2. **thinkdeep_EXAI-WS** - File context support
3. **debug_EXAI-WS** - File attachment support
4. **codereview_EXAI-WS** - File review support

### Integration Pattern:

```python
from src.storage.supabase_client import get_storage_manager

def handle_file_upload(file_path: str, continuation_id: str):
    """Upload file to Supabase and link to conversation."""
    manager = get_storage_manager()
    
    if not manager.is_enabled():
        # Fallback to local storage
        return handle_local_file(file_path)
    
    # Read file
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    # Upload to Supabase
    file_id = manager.upload_file(
        file_path=f"uploads/{continuation_id}/{os.path.basename(file_path)}",
        file_data=file_data,
        original_name=os.path.basename(file_path),
        mime_type=get_mime_type(file_path),
        file_type="user_upload"
    )
    
    # Link to conversation
    conversation_id = manager.get_conversation_by_continuation_id(continuation_id)
    if conversation_id and file_id:
        manager.link_file_to_conversation(conversation_id, file_id)
    
    return file_id
```

---

## 📊 **STEP 4: MIGRATION STRATEGY**

### Current State:
- Files stored in TEST_FILES_DIR (local filesystem)
- Lost on container restart
- No persistence across deployments

### Target State:
- Files stored in Supabase Storage buckets
- Persistent across container restarts
- Accessible from any deployment

### Migration Approach:

**Option A: Gradual Migration (Recommended)**
1. Keep TEST_FILES_DIR for backward compatibility
2. Add Supabase storage as primary storage
3. Fallback to local if Supabase unavailable
4. Gradually phase out local storage

**Option B: Hard Cutover**
1. Disable TEST_FILES_DIR
2. Use Supabase storage exclusively
3. Faster but riskier

**Recommendation:** Option A (gradual migration with fallback)

---

## 🎯 **STEP 5: IMPLEMENTATION TASKS**

### Task 5.1: Update File Upload Logic
- [ ] Modify file upload handlers to use Supabase
- [ ] Add fallback to local storage
- [ ] Test file upload with various file types
- [ ] Verify file metadata stored correctly

### Task 5.2: Update File Download Logic
- [ ] Modify file download handlers to use Supabase
- [ ] Add caching for frequently accessed files
- [ ] Test file download performance
- [ ] Verify file integrity after download

### Task 5.3: Update File Listing Logic
- [ ] Modify file listing to query Supabase
- [ ] Add pagination for large file lists
- [ ] Test file search functionality
- [ ] Verify file metadata display

### Task 5.4: Add File Cleanup Logic
- [ ] Implement file deletion from Supabase
- [ ] Add orphan file cleanup (files not linked to conversations)
- [ ] Add file expiration logic (optional)
- [ ] Test cleanup operations

---

## 🧪 **STEP 6: TESTING**

### Test Cases:

1. **File Upload Test**
   - Upload small file (< 1MB)
   - Upload medium file (1-10MB)
   - Upload large file (10-50MB)
   - Upload file with special characters in name
   - Upload file with no extension

2. **File Download Test**
   - Download recently uploaded file
   - Download file from different conversation
   - Download non-existent file (error handling)

3. **File Persistence Test**
   - Upload file
   - Restart container
   - Verify file still accessible

4. **File Cleanup Test**
   - Upload file
   - Delete conversation
   - Verify file deleted (CASCADE)

---

## 📈 **SUCCESS CRITERIA**

Phase 2 is complete when:

- [x] Service role key configured
- [ ] Connection test passes (6/6 tests)
- [ ] Files upload to Supabase successfully
- [ ] Files download from Supabase successfully
- [ ] Files persist across container restarts
- [ ] File metadata stored correctly in database
- [ ] Fallback to local storage works when Supabase unavailable
- [ ] All existing tools support Supabase file storage

---

## 🚀 **NEXT STEPS AFTER PHASE 2**

Once Phase 2 is complete, proceed to:

**Phase 3: Conversation Persistence**
- Integrate conversation service with daemon
- Update daemon to persist conversations
- Test persistence across container restarts
- Migrate from in-memory storage to Supabase

---

## 📝 **NOTES**

- Supabase free tier: 1GB storage, 2GB bandwidth/month
- File size limits: user-files (50MB), generated-files (10MB)
- Storage paths: `uploads/{continuation_id}/{filename}`
- File types: user_upload, generated, cache

---

## 🔗 **REFERENCES**

- Supabase Storage Docs: https://supabase.com/docs/guides/storage
- Supabase Python Client: https://supabase.com/docs/reference/python/introduction
- Storage Manager: `src/storage/supabase_client.py`
- Test Script: `scripts/testing/test_supabase_connection.py`

