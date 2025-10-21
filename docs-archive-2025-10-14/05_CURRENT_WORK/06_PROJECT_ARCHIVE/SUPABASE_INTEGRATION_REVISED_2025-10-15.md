# Supabase Integration - REVISED PLAN - 2025-10-15

**Date**: 2025-10-15  
**Status**: ✅ READY TO IMPLEMENT  
**Approach**: Use EXISTING Supabase database + Supabase MCP tools

---

## 🎯 Critical Discovery

**User already has a Supabase project!**
- **Project ID**: `mxaazuhlqewmkweewyaz`
- **Region**: `ap-southeast-2` (Sydney, Australia)
- **Status**: ACTIVE_HEALTHY
- **Database**: PostgreSQL 17.6.1

**Existing Schema**:
- ✅ `exai_sessions` - Chat sessions (id, user_id, title, created_at, updated_at, metadata)
- ✅ `exai_messages` - Chat messages (id, session_id, role, content, tool_name, tool_args, tool_result, tokens, cost, model, provider, metadata)
- ✅ `conversations` - Legacy conversation table (partitioned, with embeddings)
- ✅ `users`, `core_memory`, `week_memory`, `slips` - Memory system tables
- ✅ `test_runs`, `test_results`, `watcher_insights` - Testing infrastructure

---

## ❌ What NOT To Do

1. ❌ **DO NOT** create new `conversations` or `messages` tables
2. ❌ **DO NOT** create duplicate schemas
3. ❌ **DO NOT** ignore existing data
4. ❌ **DO NOT** create a new Supabase project

---

## ✅ What TO Do

### Phase 1: Add File Storage (NEW)

**Create `files` table** to track uploaded files:

```sql
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- File identification
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,  -- Path in Supabase Storage
    bucket_name TEXT NOT NULL DEFAULT 'mcp-files',
    
    -- File metadata
    file_size BIGINT,
    mime_type TEXT,
    file_hash TEXT,  -- SHA-256 for deduplication
    
    -- Link to sessions
    session_id UUID REFERENCES exai_sessions(id) ON DELETE CASCADE,
    
    -- Additional metadata
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_files_storage_path ON files(storage_path);
CREATE INDEX idx_files_session_id ON files(session_id);
CREATE INDEX idx_files_created_at ON files(created_at DESC);
CREATE INDEX idx_files_tags ON files USING GIN(tags);
CREATE INDEX idx_files_file_hash ON files(file_hash);

-- Updated timestamp trigger
CREATE TRIGGER update_files_updated_at 
    BEFORE UPDATE ON files
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role has full access to files" 
    ON files FOR ALL USING (true);
```

### Phase 2: Extend `exai_sessions` for MCP Continuity

**Add `continuation_id` column** to support MCP thread continuity:

```sql
-- Add continuation_id column
ALTER TABLE exai_sessions 
ADD COLUMN IF NOT EXISTS continuation_id TEXT UNIQUE;

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_exai_sessions_continuation_id 
ON exai_sessions(continuation_id);

-- Add comment
COMMENT ON COLUMN exai_sessions.continuation_id IS 'MCP continuation ID for thread continuity';
```

### Phase 3: Create Storage Bucket

Use Supabase MCP or Dashboard to create bucket:

```python
# Via Supabase MCP (if available)
# Or via Dashboard: Storage → New Bucket → "mcp-files" (private)
```

### Phase 4: Python Integration Service

**Create `src/integrations/supabase_service.py`**:

```python
"""
Supabase integration service using Supabase MCP tools.

This service provides file storage and session management
using the EXISTING Supabase database schema.
"""

import asyncio
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for Supabase file storage and session management."""
    
    def __init__(self, project_id: str = "mxaazuhlqewmkweewyaz"):
        """Initialize with existing project ID."""
        self.project_id = project_id
        self.bucket_name = "mcp-files"
    
    async def upload_file(
        self,
        file_path: str,
        session_id: str,
        storage_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Supabase Storage and record in files table.
        
        Args:
            file_path: Local path to file
            session_id: UUID of exai_session
            storage_path: Path in storage (auto-generated if None)
            tags: List of tags
            metadata: Additional metadata
        
        Returns:
            Dict with file_id, storage_path, public_url
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Calculate file hash
        file_hash = await self._calculate_file_hash(file_path)
        
        # Generate storage path if not provided
        if storage_path is None:
            file_ext = file_path_obj.suffix
            storage_path = f"{session_id}/{file_hash}{file_ext}"
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # TODO: Upload to Supabase Storage via MCP
        # For now, this is a placeholder - will use Supabase MCP tools
        
        # Record in database via execute_sql
        file_metadata = {
            "filename": file_path_obj.name,
            "storage_path": storage_path,
            "bucket_name": self.bucket_name,
            "file_size": file_path_obj.stat().st_size,
            "mime_type": mime_type,
            "file_hash": file_hash,
            "session_id": session_id,
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        # TODO: Insert via Supabase MCP execute_sql
        
        return {
            "storage_path": storage_path,
            "filename": file_path_obj.name,
            "file_size": file_metadata["file_size"],
            "mime_type": mime_type,
            "file_hash": file_hash
        }
    
    async def create_session(
        self,
        user_id: str,
        continuation_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new exai_session with continuation_id.
        
        Args:
            user_id: User identifier
            continuation_id: MCP continuation ID
            title: Session title
            metadata: Additional metadata
        
        Returns:
            Session UUID
        """
        # TODO: Insert via Supabase MCP execute_sql
        pass
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict] = None,
        tool_result: Optional[Dict] = None,
        model_used: Optional[str] = None,
        provider_used: Optional[str] = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
        latency_ms: int = 0,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add message to exai_messages table.
        
        Args:
            session_id: UUID of exai_session
            role: user/assistant/system
            content: Message content
            tool_name: Tool name if tool call
            tool_args: Tool arguments
            tool_result: Tool result
            model_used: Model name
            provider_used: Provider name
            tokens_in: Input tokens
            tokens_out: Output tokens
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            metadata: Additional metadata
        
        Returns:
            Message UUID
        """
        # TODO: Insert via Supabase MCP execute_sql
        pass
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        def _hash():
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        
        return await asyncio.to_thread(_hash)


__all__ = ["SupabaseService"]
```

---

## 📋 Implementation Steps

### Step 1: Run Database Migrations ✅

Use Supabase MCP `apply_migration` tool:

```python
# Migration 1: Create files table
apply_migration(
    project_id="mxaazuhlqewmkweewyaz",
    name="add_files_table",
    query="""<SQL from Phase 1>"""
)

# Migration 2: Add continuation_id to exai_sessions
apply_migration(
    project_id="mxaazuhlqewmkweewyaz",
    name="add_continuation_id_to_sessions",
    query="""<SQL from Phase 2>"""
)
```

### Step 2: Create Storage Bucket ✅

Via Supabase Dashboard or API:
- Bucket name: `mcp-files`
- Public: No (private)
- File size limit: 50MB

### Step 3: Implement Python Service ✅

Create `src/integrations/supabase_service.py` with methods to:
- Upload files via Supabase MCP
- Create sessions with continuation_id
- Add messages to exai_messages
- Query conversation history

### Step 4: Integrate with Existing Tools ✅

Update Kimi upload tools to use Supabase:
- Replace local file storage with Supabase Storage
- Link uploaded files to sessions
- Track file metadata in database

### Step 5: Test End-to-End ✅

- Upload file via Kimi tool
- Verify file in Supabase Storage
- Verify metadata in files table
- Verify link to session
- Test file retrieval

---

## 🔧 Using Supabase MCP Tools

### Execute SQL

```python
from supabase_mcp import execute_sql

result = execute_sql(
    project_id="mxaazuhlqewmkweewyaz",
    query="SELECT * FROM exai_sessions LIMIT 10"
)
```

### Apply Migration

```python
from supabase_mcp import apply_migration

apply_migration(
    project_id="mxaazuhlqewmkweewyaz",
    name="add_files_table",
    query="CREATE TABLE files (...)"
)
```

### List Tables

```python
from supabase_mcp import list_tables

tables = list_tables(
    project_id="mxaazuhlqewmkweewyaz",
    schemas=["public"]
)
```

---

## 🎯 Next Steps

1. ✅ Run migrations to add `files` table and `continuation_id` column
2. ✅ Create `mcp-files` storage bucket
3. ✅ Implement `SupabaseService` class
4. ✅ Update Kimi upload tools to use Supabase
5. ✅ Test file upload/download
6. ✅ Update conversation tools to use exai_sessions/exai_messages
7. ✅ Remove local `TEST_FILES_DIR` dependency

---

**Advantages of This Approach**:
- ✅ Works with existing schema
- ✅ No data migration needed
- ✅ Uses Supabase MCP for direct database access
- ✅ Maintains backward compatibility
- ✅ Leverages existing conversation tracking
- ✅ Adds file storage capability cleanly

