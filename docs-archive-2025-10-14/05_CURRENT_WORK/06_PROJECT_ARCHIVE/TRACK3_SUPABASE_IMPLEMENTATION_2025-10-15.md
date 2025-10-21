# Track 3: Supabase Integration Implementation Plan
**Date:** 2025-10-15
**Status:** Phase 1 COMPLETE ✅
**Purpose:** Implement persistent storage for files and conversation history

---

## 🎉 **PHASE 1 COMPLETE - DATABASE READY!**

**Completion Date:** 2025-10-15
**Execution Time:** ~15 minutes
**GLM-4.6 Conversation ID:** `05660144-c47c-4b0b-b2b0-83012e53dd46`

### ✅ **What Was Accomplished**

**1. Cleanup of Previous Attempts**
- Dropped 18 legacy tables from old implementations
- Verified database completely clean
- No storage buckets existed (fresh start)

**2. Fresh Schema Deployment**
- Created 4 core tables:
  - `conversations` - Conversation sessions with continuation_id
  - `messages` - Individual messages within conversations
  - `files` - File metadata and storage paths
  - `conversation_files` - Many-to-many junction table
  - `schema_version` - Schema version tracking
- Created custom types: `message_role`, `file_type`
- Created 9 performance indexes
- Created auto-update trigger for `updated_at` column

**3. Storage Buckets Created**
- `user-files` bucket (50MB file size limit, private)
- `generated-files` bucket (10MB file size limit, private)

**4. Environment Configuration**
- Updated `.env` with Supabase credentials
- Added `SUPABASE_ANON_KEY` variable
- Added `SUPABASE_SERVICE_ROLE_KEY` variable (needs manual fill)
- Updated `.env.example` with Supabase configuration template

**5. Implementation Files Created**
- `supabase/schema.sql` - Complete database schema
- `src/storage/supabase_client.py` - Storage manager implementation
- `supabase/SETUP_GUIDE.md` - Step-by-step setup instructions

### 📊 **Current State**

**Supabase Project:** Personal AI
**Project ID:** mxaazuhlqewmkweewyaz
**Region:** ap-southeast-2 (Sydney, Australia)
**Project URL:** https://mxaazuhlqewmkweewyaz.supabase.co

**Database Tables:** 5 tables
- conversations (0 rows)
- messages (0 rows)
- files (0 rows)
- conversation_files (0 rows)
- schema_version (1 row)

**Storage Buckets:** 2 buckets
- user-files (0 files)
- generated-files (0 files)

**Environment:** Configured (service role key needs manual addition)

---

## 🎯 **PHASE 2: FILE STORAGE MIGRATION - READY TO BEGIN**

**Status:** Implementation files created, awaiting service role key
**Date:** 2025-10-15

**Created Files:**
1. ✅ `scripts/testing/test_supabase_connection.py` - Connection test suite (6 tests)
2. ✅ `docs/05_CURRENT_WORK/PHASE2_FILE_STORAGE_MIGRATION_2025-10-15.md` - Implementation guide

**Prerequisites:**
- [x] Supabase Python client installed (supabase==2.22.0 in requirements.txt)
- [x] Storage manager implemented (src/storage/supabase_client.py)
- [x] Test script created (scripts/testing/test_supabase_connection.py)
- [ ] **CRITICAL:** Service role key needed in .env file

**Next Actions:**
1. **User Action Required:** Add service role key to .env file
   - Get from: https://supabase.com/dashboard/project/mxaazuhlqewmkweewyaz/settings/api
   - Add to .env: `SUPABASE_SERVICE_ROLE_KEY=your-key-here`

2. **Test Connection:** Run `python scripts/testing/test_supabase_connection.py`
   - Should pass 6/6 tests
   - Verifies environment, database, storage buckets, operations

3. **Integrate with Tools:** Update existing tools to use Supabase storage
   - chat_EXAI-WS, thinkdeep_EXAI-WS, debug_EXAI-WS, codereview_EXAI-WS

4. **Test File Operations:** Upload/download/persistence tests

**Estimated Time:** 1-2 hours (after service role key added)

**Documentation:** See `docs/05_CURRENT_WORK/PHASE2_FILE_STORAGE_MIGRATION_2025-10-15.md`

---

## 🎯 **EXECUTIVE SUMMARY**

**Objective:** Replace in-memory storage with Supabase for persistent data across container restarts

**Benefits:**
- ✅ Cross-container data persistence
- ✅ Conversation history retention
- ✅ File storage (replace local filesystem)
- ✅ Multi-client shared data access
- ✅ Foundation for distributed deployment

**Estimated Effort:** 4-6 hours
- Phase 1: Foundation Setup (1-2 hours)
- Phase 2: File Storage Migration (1-2 hours)
- Phase 3: Conversation Persistence (1-2 hours)

**GLM-4.6 Strategic Validation:** ✅ Recommended as next phase

---

## 📊 **CURRENT STATE ANALYSIS**

### In-Memory Storage (Current)

**Conversation Storage:**
- Location: Daemon memory
- Persistence: Lost on container restart
- Sharing: Single container only
- Scalability: Limited to container memory

**File Storage:**
- Location: `TEST_FILES_DIR` (local filesystem)
- Persistence: Container-dependent
- Sharing: Single container only
- Scalability: Limited to container disk

### Supabase Storage (Target)

**Conversation Storage:**
- Location: Supabase PostgreSQL
- Persistence: Permanent
- Sharing: Multi-container/multi-client
- Scalability: Cloud-scale

**File Storage:**
- Location: Supabase Storage buckets
- Persistence: Permanent
- Sharing: Multi-container/multi-client
- Scalability: Cloud-scale

---

## 🗄️ **DATABASE SCHEMA DESIGN**

### Tables

#### 1. Conversations Table
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  continuation_id TEXT UNIQUE NOT NULL,
  title TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  INDEX idx_continuation_id (continuation_id)
);
```

**Purpose:** Track conversation sessions  
**Key Fields:**
- `continuation_id`: Unique conversation identifier
- `title`: Auto-generated or user-provided title
- `metadata`: Tool usage, model info, etc.

#### 2. Messages Table
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  INDEX idx_conversation_id (conversation_id),
  INDEX idx_timestamp (timestamp)
);
```

**Purpose:** Store individual messages within conversations  
**Key Fields:**
- `conversation_id`: Foreign key to conversations
- `role`: Message sender (user/assistant/system)
- `content`: Message text
- `metadata`: Model used, tokens, etc.

#### 3. Files Table
```sql
CREATE TABLE files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  storage_path TEXT NOT NULL UNIQUE,
  original_name TEXT NOT NULL,
  mime_type TEXT,
  size_bytes INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  INDEX idx_storage_path (storage_path)
);
```

**Purpose:** Track uploaded files and metadata  
**Key Fields:**
- `storage_path`: Path in Supabase Storage
- `original_name`: User's original filename
- `size_bytes`: File size for quota management

#### 4. Conversation_Files Junction Table
```sql
CREATE TABLE conversation_files (
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  file_id UUID REFERENCES files(id) ON DELETE CASCADE,
  attached_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (conversation_id, file_id)
);
```

**Purpose:** Link files to conversations (many-to-many)

---

### Storage Buckets

#### 1. User Files Bucket
```
Name: user-files
Public: false
File size limit: 50MB
Allowed MIME types: text/*, application/pdf, image/*
```

**Purpose:** Store user-uploaded files for context

#### 2. Generated Files Bucket
```
Name: generated-files
Public: false
File size limit: 10MB
Allowed MIME types: text/*, application/json
```

**Purpose:** Store AI-generated files (code, docs, etc.)

---

## 🔧 **IMPLEMENTATION PHASES**

### Phase 1: Foundation Setup (1-2 hours)

#### Step 1.1: Supabase Project Setup
```bash
# Create Supabase project (via web UI)
# Note: Project URL and anon key

# Install Supabase client
pip install supabase
```

#### Step 1.2: Environment Configuration
```bash
# Add to .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Add to .env.example (without actual keys)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

#### Step 1.3: Create Database Schema
```python
# scripts/supabase/setup_schema.py
import os
from supabase import create_client, Client

def setup_database():
    """Create all tables and indexes"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    # Execute SQL from schema file
    with open("scripts/supabase/schema.sql", "r") as f:
        schema_sql = f.read()
    
    # Execute schema creation
    # Note: Use Supabase dashboard SQL editor for initial setup
    print("Schema created successfully")
```

#### Step 1.4: Create Storage Buckets
```python
# scripts/supabase/setup_storage.py
def setup_storage():
    """Create storage buckets"""
    supabase.storage.create_bucket("user-files", {
        "public": False,
        "file_size_limit": 52428800,  # 50MB
        "allowed_mime_types": ["text/*", "application/pdf", "image/*"]
    })
    
    supabase.storage.create_bucket("generated-files", {
        "public": False,
        "file_size_limit": 10485760,  # 10MB
        "allowed_mime_types": ["text/*", "application/json"]
    })
```

---

### Phase 2: File Storage Migration (1-2 hours)

#### Step 2.1: Create File Service
```python
# src/services/file_service.py
from supabase import Client
import os
from typing import Optional

class FileService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def upload_file(
        self,
        file_path: str,
        bucket: str = "user-files"
    ) -> dict:
        """Upload file to Supabase Storage"""
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        # Generate unique storage path
        storage_path = f"{uuid.uuid4()}/{os.path.basename(file_path)}"
        
        # Upload to storage
        result = self.supabase.storage.from_(bucket).upload(
            storage_path,
            file_data
        )
        
        # Save metadata to database
        file_record = {
            "storage_path": storage_path,
            "original_name": os.path.basename(file_path),
            "mime_type": self._get_mime_type(file_path),
            "size_bytes": len(file_data)
        }
        
        db_result = self.supabase.table("files").insert(file_record).execute()
        
        return db_result.data[0]
    
    async def download_file(self, file_id: str) -> bytes:
        """Download file from Supabase Storage"""
        # Get file metadata
        file_record = self.supabase.table("files").select("*").eq("id", file_id).execute()
        
        if not file_record.data:
            raise FileNotFoundError(f"File {file_id} not found")
        
        storage_path = file_record.data[0]["storage_path"]
        
        # Download from storage
        result = self.supabase.storage.from_("user-files").download(storage_path)
        
        return result
```

#### Step 2.2: Update Tools to Use File Service
```python
# tools/chat.py - Update file handling
async def handle_files(self, files: list[str]) -> list[dict]:
    """Upload files and return file IDs"""
    file_service = FileService(self.supabase)
    
    uploaded_files = []
    for file_path in files:
        file_record = await file_service.upload_file(file_path)
        uploaded_files.append(file_record)
    
    return uploaded_files
```

---

### Phase 3: Conversation Persistence (1-2 hours)

#### Step 3.1: Create Conversation Service
```python
# src/services/conversation_service.py
class ConversationService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def create_conversation(
        self,
        continuation_id: str,
        title: Optional[str] = None
    ) -> dict:
        """Create new conversation"""
        conversation = {
            "continuation_id": continuation_id,
            "title": title or f"Conversation {continuation_id[:8]}"
        }
        
        result = self.supabase.table("conversations").insert(conversation).execute()
        return result.data[0]
    
    async def add_message(
        self,
        continuation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """Add message to conversation"""
        # Get or create conversation
        conv = await self.get_or_create_conversation(continuation_id)
        
        message = {
            "conversation_id": conv["id"],
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        result = self.supabase.table("messages").insert(message).execute()
        return result.data[0]
    
    async def get_conversation_history(
        self,
        continuation_id: str,
        limit: int = 100
    ) -> list[dict]:
        """Get conversation message history"""
        # Get conversation
        conv_result = self.supabase.table("conversations").select("id").eq(
            "continuation_id", continuation_id
        ).execute()
        
        if not conv_result.data:
            return []
        
        conv_id = conv_result.data[0]["id"]
        
        # Get messages
        messages = self.supabase.table("messages").select("*").eq(
            "conversation_id", conv_id
        ).order("timestamp").limit(limit).execute()
        
        return messages.data
```

---

## ✅ **SUCCESS CRITERIA**

### Functional Requirements
- [ ] Files persist across container restarts
- [ ] Conversations persist across container restarts
- [ ] Multiple clients can access shared conversations
- [ ] File upload/download works correctly
- [ ] Conversation history retrieval works correctly

### Performance Requirements
- [ ] File upload < 2 seconds for 10MB files
- [ ] Conversation retrieval < 100ms
- [ ] Message insertion < 50ms
- [ ] No memory leaks from connection pooling

### Security Requirements
- [ ] Row-level security policies configured
- [ ] API keys stored securely in .env
- [ ] File access restricted to authenticated users
- [ ] No sensitive data in logs

---

## 🎯 **NEXT STEPS**

1. **Create Supabase project** (via web UI)
2. **Set up environment variables** (.env configuration)
3. **Execute Phase 1** (Foundation Setup)
4. **Execute Phase 2** (File Storage Migration)
5. **Execute Phase 3** (Conversation Persistence)
6. **Test and validate** (Success criteria verification)

**Estimated Total Time:** 4-6 hours

---

**Status:** Ready to begin - GLM-4.6 validated strategy

