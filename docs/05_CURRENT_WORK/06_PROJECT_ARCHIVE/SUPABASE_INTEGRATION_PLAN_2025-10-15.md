# Supabase Integration Implementation Plan

**Date**: 2025-10-15  
**Status**: Research Complete - Ready for Implementation  
**Research Method**: EXAI GLM-4.6 with web search + Supabase MCP documentation search

---

## 📋 Executive Summary

This document outlines the complete implementation plan for integrating Supabase into the EX-AI MCP Server project. The integration will replace local file storage with Supabase Storage and add conversation/chat history persistence using Supabase Database.

**Key Benefits**:
- ✅ Centralized cloud storage for files
- ✅ Persistent conversation history across sessions
- ✅ Scalable architecture for future features
- ✅ Better data organization and retrieval
- ✅ Foundation for multi-user support

---

## 🎯 Integration Goals

### 1. File Storage (Supabase Storage)
**Current State**: Files stored locally in `TEST_FILES_DIR=C:\Project`  
**Target State**: Files stored in Supabase Storage buckets

**Use Cases**:
- Kimi file uploads via `kimi_upload_and_extract` tool
- GLM file uploads (future)
- User-uploaded documents for context
- Generated artifacts and outputs

### 2. Conversation Storage (Supabase Database)
**Current State**: In-memory conversation storage (lost on restart)  
**Target State**: Persistent conversation history in Postgres

**Use Cases**:
- Conversation threads with continuation IDs
- Message history for context retrieval
- Long-term memory/context persistence
- Analytics and usage tracking

### 3. Metadata & Indexing
**Target State**: Rich metadata for files and conversations

**Features**:
- File metadata (size, type, upload date, user, tags)
- Conversation metadata (model used, tokens, duration, cost)
- Full-text search on conversations
- Relationship tracking (files ↔ conversations)

---

## 🔧 Technical Implementation

### Phase 1: Supabase Python SDK Setup

#### 1.1 Install Dependencies

```bash
pip install supabase==2.9.1
```

**Why `supabase-py`?**
- Official Python client for Supabase
- Supports both sync and async operations
- Includes Storage API, Database API, and Auth API
- Well-documented and actively maintained

#### 1.2 Environment Variables

Add to `.env.docker`:

```bash
# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # For server-side operations
SUPABASE_ANON_KEY=your-anon-key  # For client-side operations (if needed)

# Storage Configuration
SUPABASE_STORAGE_BUCKET_FILES=mcp-files  # Bucket for uploaded files
SUPABASE_STORAGE_BUCKET_AVATARS=avatars  # Bucket for user avatars (future)

# Database Configuration
SUPABASE_DB_SCHEMA=public  # Schema for tables
```

**Security Notes**:
- Use `SUPABASE_SERVICE_ROLE_KEY` for server-side operations (bypasses RLS)
- Use `SUPABASE_ANON_KEY` for client-side operations (respects RLS)
- Never commit keys to git - use `.env` files only

#### 1.3 Connection Initialization

Create `src/integrations/supabase_client.py`:

```python
"""
Supabase client initialization and connection management.
"""
import os
from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance (singleton pattern).
    
    Returns:
        Client: Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info(f"Supabase client initialized: {supabase_url}")
    
    return _supabase_client

def reset_supabase_client():
    """Reset the Supabase client (useful for testing)."""
    global _supabase_client
    _supabase_client = None
```

**Note**: The `supabase-py` SDK does NOT have native async support. All operations are synchronous. For async operations, we'll need to wrap calls in `asyncio.to_thread()`.

---

### Phase 2: File Storage Implementation

#### 2.1 Database Schema for File Metadata

Create migration: `supabase/migrations/20251015_file_storage.sql`

```sql
-- Create files table for metadata
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- File identification
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,  -- Path in Supabase Storage
    bucket_name TEXT NOT NULL DEFAULT 'mcp-files',
    
    -- File metadata
    file_size BIGINT,  -- Size in bytes
    mime_type TEXT,
    file_hash TEXT,  -- SHA-256 hash for deduplication
    
    -- Ownership and context
    user_id UUID,  -- Future: link to auth.users
    session_id TEXT,  -- MCP session that uploaded the file
    conversation_id UUID,  -- Link to conversation (if applicable)
    
    -- Additional metadata
    tags TEXT[],  -- Array of tags for categorization
    description TEXT,
    metadata JSONB  -- Flexible metadata storage
);

-- Indexes
CREATE INDEX idx_files_storage_path ON files(storage_path);
CREATE INDEX idx_files_session_id ON files(session_id);
CREATE INDEX idx_files_conversation_id ON files(conversation_id);
CREATE INDEX idx_files_created_at ON files(created_at DESC);
CREATE INDEX idx_files_tags ON files USING GIN(tags);

-- Updated timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS)
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for service role
CREATE POLICY "Service role has full access" ON files
    FOR ALL USING (true);
```

#### 2.2 Storage Bucket Setup

Create buckets via Supabase Dashboard or SQL:

```sql
-- Create storage bucket for files
INSERT INTO storage.buckets (id, name, public)
VALUES ('mcp-files', 'mcp-files', false);

-- Storage policies
CREATE POLICY "Service role can upload files" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'mcp-files');

CREATE POLICY "Service role can read files" ON storage.objects
    FOR SELECT USING (bucket_id = 'mcp-files');

CREATE POLICY "Service role can delete files" ON storage.objects
    FOR DELETE USING (bucket_id = 'mcp-files');
```

#### 2.3 File Upload Service

Create `src/integrations/supabase_storage.py`:

```python
"""
Supabase Storage service for file uploads and management.
"""
import asyncio
import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """Service for managing file uploads to Supabase Storage."""
    
    def __init__(self, bucket_name: str = None):
        self.client = get_supabase_client()
        self.bucket_name = bucket_name or os.getenv("SUPABASE_STORAGE_BUCKET_FILES", "mcp-files")
    
    async def upload_file(
        self,
        file_path: str,
        storage_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to Supabase Storage and record metadata.
        
        Args:
            file_path: Local path to file
            storage_path: Path in storage (auto-generated if None)
            metadata: Additional metadata
            session_id: MCP session ID
            conversation_id: Conversation ID (if applicable)
        
        Returns:
            Dict with file metadata including storage_path and file_id
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate storage path if not provided
        if storage_path is None:
            file_hash = await self._calculate_file_hash(file_path)
            file_ext = file_path_obj.suffix
            storage_path = f"{session_id or 'uploads'}/{file_hash}{file_ext}"
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Upload to Supabase Storage (sync operation wrapped in async)
        upload_result = await asyncio.to_thread(
            self.client.storage.from_(self.bucket_name).upload,
            path=storage_path,
            file=file_content,
            file_options={"content-type": mime_type or "application/octet-stream"}
        )
        
        # Record metadata in database
        file_metadata = {
            "filename": file_path_obj.name,
            "storage_path": storage_path,
            "bucket_name": self.bucket_name,
            "file_size": file_path_obj.stat().st_size,
            "mime_type": mime_type,
            "file_hash": await self._calculate_file_hash(file_path),
            "session_id": session_id,
            "conversation_id": conversation_id,
            "metadata": metadata or {}
        }
        
        db_result = await asyncio.to_thread(
            self.client.table("files").insert(file_metadata).execute
        )
        
        logger.info(f"File uploaded: {storage_path} (ID: {db_result.data[0]['id']})")
        
        return {
            "file_id": db_result.data[0]["id"],
            "storage_path": storage_path,
            "public_url": self._get_public_url(storage_path),
            **file_metadata
        }
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        def _hash():
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        
        return await asyncio.to_thread(_hash)
    
    def _get_public_url(self, storage_path: str) -> str:
        """Get public URL for file (if bucket is public)."""
        return self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
```

---

### Phase 3: Conversation Storage Implementation

#### 3.1 Database Schema for Conversations

Create migration: `supabase/migrations/20251015_conversations.sql`

```sql
-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Conversation identification
    continuation_id TEXT UNIQUE NOT NULL,  -- MCP continuation ID
    session_id TEXT,  -- MCP session ID
    
    -- Conversation metadata
    title TEXT,  -- Auto-generated or user-provided
    summary TEXT,  -- Auto-generated summary
    model_used TEXT,  -- Primary model used
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0,
    
    -- Status
    status TEXT DEFAULT 'active',  -- active, archived, deleted
    
    -- Additional metadata
    tags TEXT[],
    metadata JSONB
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Relationship
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role TEXT NOT NULL,  -- user, assistant, system, tool
    content TEXT NOT NULL,
    
    -- Message metadata
    model_used TEXT,
    tokens INTEGER,
    cost DECIMAL(10, 4),
    duration_ms INTEGER,
    
    -- Additional metadata
    metadata JSONB
);

-- Indexes
CREATE INDEX idx_conversations_continuation_id ON conversations(continuation_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Full-text search on messages
CREATE INDEX idx_messages_content_fts ON messages USING GIN(to_tsvector('english', content));

-- Updated timestamp trigger for conversations
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role has full access to conversations" ON conversations
    FOR ALL USING (true);

CREATE POLICY "Service role has full access to messages" ON messages
    FOR ALL USING (true);
```

---

## 📊 Migration Strategy

### Step 1: Parallel Operation (Week 1)
- Keep existing local file storage
- Add Supabase storage alongside
- Log all operations to both systems
- Compare results for validation

### Step 2: Gradual Cutover (Week 2)
- Make Supabase primary storage
- Keep local storage as backup
- Monitor for issues

### Step 3: Full Migration (Week 3)
- Remove local storage dependency
- Migrate existing files to Supabase
- Update all documentation

---

## 🔐 Security Considerations

1. **API Keys**: Use service role key for server-side, anon key for client-side
2. **RLS Policies**: Implement Row Level Security for multi-user support
3. **File Validation**: Validate file types and sizes before upload
4. **Rate Limiting**: Implement rate limiting on uploads
5. **Encryption**: Files encrypted at rest by Supabase

---

## 📈 Implementation Status

### ✅ Completed (2025-10-15)

1. ✅ **Research complete** - This document created with comprehensive plan
2. ✅ **Phase 1: SDK Setup** - `src/integrations/supabase_client.py` created
3. ✅ **Phase 2: File Storage** - `src/integrations/supabase_storage.py` created
4. ✅ **Database Migrations** - SQL migrations created:
   - `supabase/migrations/20251015_file_storage.sql`
   - `supabase/migrations/20251015_conversations.sql`

### ⏭️ Next Steps

1. ⏭️ Create Supabase project and get credentials
2. ⏭️ Add environment variables to `.env.docker`
3. ⏭️ Run database migrations
4. ⏭️ Create storage buckets
5. ⏭️ Test file upload/download
6. ⏭️ Implement conversation storage service
7. ⏭️ Integrate with existing tools
8. ⏭️ Migration of existing data
9. ⏭️ Documentation updates

---

**Research Sources**:
- Supabase Python SDK Documentation
- Supabase Storage API Documentation
- Supabase Database Documentation
- GLM-4.6 Web Search Results

**Implementation Files Created**:
- `src/integrations/supabase_client.py` - Client initialization
- `src/integrations/supabase_storage.py` - File storage service
- `supabase/migrations/20251015_file_storage.sql` - Files table schema
- `supabase/migrations/20251015_conversations.sql` - Conversations schema

