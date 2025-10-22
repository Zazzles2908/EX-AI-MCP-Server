# Supabase Integration Investigation Plan
**Date:** 2025-10-21 (Updated after MCP investigation)
**Phase:** Next Investigation Priority
**Related Docs:** SYSTEMPROMPTS_ENHANCED_ANALYSIS_2025-10-21.md
**EXAI Validation:** ✅ Completed with GLM-4.6 (High Thinking Mode)

---

## Executive Summary

This document outlines the Supabase integration strategy for the EX-AI-MCP-Server architecture based on **actual investigation** of the current Supabase setup using MCP tools.

**Project Details:**
- **Name:** Personal AI
- **Region:** ap-southeast-2 (Sydney, Australia)
- **Status:** ACTIVE_HEALTHY
- **PostgreSQL:** 17.6.1.005 (Latest stable)
- **Plan:** Supabase Pro

---

## Current Supabase State (Verified via MCP)

### ✅ What's Already Implemented

**1. Conversation Persistence (ACTIVE)**
- **conversations** table: 541 rows with continuation_id, title, metadata, session_id
- **messages** table: 2,355 rows linked to conversations
- **sessions** table: 0 rows (structure exists, not yet used)
- **conversation_files** table: 166 rows (many-to-many link)

**2. File Management (ACTIVE)**
- **files** table: 169 rows with storage_path, file_type enum
- **provider_file_uploads** table: 10 rows tracking Kimi/GLM uploads
- **file_deletion_jobs** table: 0 rows (async deletion queue ready)
- **file_metadata** table: 0 rows (EMPTY - overlaps with provider_file_uploads)

**3. Issue Tracking (ACTIVE)**
- **exai_issues** table: 11 rows
- **exai_issue_updates** table: 12 rows
- **exai_issue_checklist** table: 7 rows
- **exai_issues_tracker** table: 14 rows (comprehensive tracking)
- **exai_future_enhancements** table: 5 rows
- **exai_tool_validation** table: 18 rows
- **phase1_issues** table: 6 rows
- **issues** table: 1 row (generic)

**4. Storage Buckets (ACTIVE)**
- **user-files**: 172 objects, 50MB limit per file
- **generated-files**: 10MB limit per file
- **Image transformation**: ENABLED
- **S3 protocol**: ENABLED
- **Iceberg catalog**: DISABLED

**5. Edge Functions (DEPLOYED)**
- **gateway** (v2): API gateway for routing
- **memory** (v2): Conversation management
- **exai-chat** (v1): AI chat interface

### ⚠️ Issues Identified (EXAI Validated)

**1. Table Redundancy (HIGH PRIORITY)**
- `file_metadata` (0 rows) overlaps with `provider_file_uploads` (10 rows)
- Multiple issue tracking tables (exai_issues, exai_issues_tracker, issues, phase1_issues)
- Recommendation: **Consolidate to reduce complexity**

**2. Missing Features**
- ❌ **Realtime subscriptions**: NOT enabled (needed for live updates)
- ❌ **system_prompts table**: Prompts hard-coded in Python
- ❌ **prompt_performance table**: No metrics tracking
- ❌ **Row Level Security (RLS)**: Not configured on custom tables

**3. Missing Indexes**
- No indexes on `conversations.session_id`
- No indexes on `messages.conversation_id`
- No indexes on `files.storage_path`

### Architecture Principles (Validated)

```
User Request → Primary Processing → Response
                      ↓
                Async Supabase Recording
                (Non-blocking audit trail)
```

**Key Principle:** Supabase should NOT be in the critical path for user requests.

---

## EXAI Architectural Recommendations

### Priority 1: Critical (Week 1)

**1.1 Consolidate Overlapping Tables**

```sql
-- Consolidate file tracking
-- Migrate data from file_metadata to provider_file_uploads
UPDATE provider_file_uploads pfu
SET provider_file_ids = fm.provider_file_ids
FROM file_metadata fm
WHERE pfu.supabase_file_id = fm.file_id::text;

-- Drop empty file_metadata table
DROP TABLE IF EXISTS file_metadata;

-- Consolidate issue tracking
-- Create unified issues table
CREATE TABLE issues_unified AS
SELECT
    id, title, description, severity, category, status,
    created_at, updated_at
FROM exai_issues_tracker
UNION ALL
SELECT
    id, title, description, severity, category, status,
    created_at, updated_at
FROM exai_issues
WHERE id NOT IN (SELECT id FROM exai_issues_tracker);

-- Migrate references
-- Update foreign keys to point to issues_unified
-- Then drop redundant tables
```

**1.2 Enable Realtime Subscriptions**

```sql
-- Enable realtime for key tables
ALTER PUBLICATION supabase_realtime ADD TABLE conversations;
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
ALTER PUBLICATION supabase_realtime ADD TABLE files;
ALTER PUBLICATION supabase_realtime ADD TABLE provider_file_uploads;
```

**Benefits:**
- Live chat updates across multiple clients
- Real-time file upload progress
- Instant issue status updates
- Multi-user collaboration support

**1.3 Add Critical Indexes**

```sql
-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_continuation_id ON conversations(continuation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_files_storage_path ON files(storage_path);
CREATE INDEX IF NOT EXISTS idx_provider_uploads_provider_file_id ON provider_file_uploads(provider_file_id);
```

### Priority 2: High (Week 2)

**2.1 Add System Prompts Tables**

```sql
CREATE TABLE system_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_name TEXT NOT NULL,
    provider TEXT NOT NULL, -- 'kimi', 'glm', 'base'
    tier INTEGER NOT NULL CHECK (tier >= 0 AND tier <= 3),
    prompt_content TEXT NOT NULL,
    version TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(tool_name, provider, version)
);

CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID REFERENCES system_prompts(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    change_description TEXT,
    changed_by TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    rollback_available BOOLEAN DEFAULT true,
    performance_metrics JSONB,
    UNIQUE(prompt_id, version)
);

CREATE TABLE prompt_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID REFERENCES system_prompts(id) ON DELETE CASCADE,
    tool_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    execution_time_ms INTEGER,
    token_count INTEGER,
    success BOOLEAN,
    error_message TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX idx_system_prompts_active ON system_prompts(tool_name, provider, is_active);
CREATE INDEX idx_prompt_performance_tool ON prompt_performance(tool_name, provider, executed_at DESC);
```

**2.2 Configure Row Level Security (RLS)**

```sql
-- Enable RLS on custom tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_prompts ENABLE ROW LEVEL SECURITY;

-- Create policies (example for conversations)
CREATE POLICY "Users can view their own conversations"
ON conversations FOR SELECT
USING (auth.uid()::text = session_id::text);

CREATE POLICY "Users can insert their own conversations"
ON conversations FOR INSERT
WITH CHECK (auth.uid()::text = session_id::text);
```

### Priority 3: Medium (Week 3)

**3.1 Add Foreign Key Constraints**

```sql
-- Add missing foreign keys
ALTER TABLE messages
ADD CONSTRAINT fk_messages_conversation
FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;

ALTER TABLE conversation_files
ADD CONSTRAINT fk_conv_files_conv
FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_conv_files_file
FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE;

ALTER TABLE provider_file_uploads
ADD CONSTRAINT fk_provider_uploads_file
FOREIGN KEY (supabase_file_id) REFERENCES files(id) ON DELETE SET NULL;
```

**3.2 Optimize Edge Functions**

Based on the 3 deployed edge functions, here's the recommended usage:

**gateway (v2) - API Gateway**
```typescript
// Route requests to appropriate services
export default async function(req: Request) {
  const url = new URL(req.url);

  if (url.pathname.startsWith('/chat')) {
    return await handleChat(req);
  }
  if (url.pathname.startsWith('/files')) {
    return await handleFiles(req);
  }
  if (url.pathname.startsWith('/issues')) {
    return await handleIssues(req);
  }

  return new Response('Not Found', { status: 404 });
}
```

**memory (v2) - Conversation Management**
```typescript
// Handle conversation persistence and retrieval
export default async function(req: Request) {
  const { method } = req;

  if (method === 'GET') {
    const { continuation_id } = await req.json();
    return await getConversation(continuation_id);
  }

  if (method === 'POST') {
    const { conversation_id, role, content } = await req.json();
    return await saveMessage(conversation_id, role, content);
  }

  return new Response('Method Not Allowed', { status: 405 });
}
```

**exai-chat (v1) - AI Chat Interface**
```typescript
// Direct AI model integration
export default async function(req: Request) {
  const { message, model, conversation_id } = await req.json();

  // Save user message
  await saveMessage(conversation_id, 'user', message);

  // Get AI response (call EX-AI-MCP-Server)
  const response = await getAIResponse(message, model);

  // Save AI response
  await saveMessage(conversation_id, 'assistant', response);

  return new Response(JSON.stringify({ response }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```

---

## Investigation Areas (Updated)

---

### 2. Schema Design for System Prompts

**Objective:** Design Supabase schema to support system prompts architecture

**Proposed Tables:**

#### `system_prompts`
```sql
CREATE TABLE system_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_name TEXT NOT NULL,
    provider TEXT NOT NULL, -- 'kimi', 'glm', 'base'
    tier INTEGER NOT NULL, -- 0, 1, 2, 3
    prompt_content TEXT NOT NULL,
    version TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    metadata JSONB,
    UNIQUE(tool_name, provider, version)
);

CREATE INDEX idx_system_prompts_active ON system_prompts(tool_name, provider, is_active);
CREATE INDEX idx_system_prompts_version ON system_prompts(version);
```

#### `prompt_versions`
```sql
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID REFERENCES system_prompts(id),
    version TEXT NOT NULL,
    change_description TEXT,
    changed_by TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    rollback_available BOOLEAN DEFAULT true,
    performance_metrics JSONB
);
```

#### `prompt_performance`
```sql
CREATE TABLE prompt_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID REFERENCES system_prompts(id),
    tool_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    execution_time_ms INTEGER,
    token_count INTEGER,
    success BOOLEAN,
    error_message TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_prompt_performance_tool ON prompt_performance(tool_name, provider, executed_at);
```

#### `conversation_history`
```sql
CREATE TABLE conversation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    continuation_id TEXT UNIQUE NOT NULL,
    tool_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    messages JSONB NOT NULL, -- Array of message objects
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_conversation_continuation ON conversation_history(continuation_id);
CREATE INDEX idx_conversation_active ON conversation_history(is_active, expires_at);
```

#### `file_metadata`
```sql
CREATE TABLE file_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    moonshot_file_id TEXT UNIQUE,
    supabase_storage_path TEXT,
    original_filename TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type TEXT,
    uploaded_by TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0,
    is_orphaned BOOLEAN DEFAULT false,
    metadata JSONB
);

CREATE INDEX idx_file_moonshot ON file_metadata(moonshot_file_id);
CREATE INDEX idx_file_orphaned ON file_metadata(is_orphaned);
```

---

### 3. Integration Patterns

**Pattern 1: Prompt Versioning & Rollback**

```python
class SupabasePromptManager:
    async def store_prompt_version(
        self, 
        tool_name: str, 
        provider: str, 
        prompt: str, 
        version: str
    ):
        """Store a new prompt version in Supabase."""
        await self.supabase.table('system_prompts').insert({
            'tool_name': tool_name,
            'provider': provider,
            'prompt_content': prompt,
            'version': version,
            'is_active': True
        })
    
    async def get_active_prompt(self, tool_name: str, provider: str) -> str:
        """Retrieve the active prompt for a tool/provider."""
        result = await self.supabase.table('system_prompts')\
            .select('prompt_content')\
            .eq('tool_name', tool_name)\
            .eq('provider', provider)\
            .eq('is_active', True)\
            .single()
        
        return result['prompt_content']
    
    async def rollback_to_version(
        self, 
        tool_name: str, 
        provider: str, 
        version: str
    ):
        """Rollback to a specific prompt version."""
        # Deactivate current version
        await self.supabase.table('system_prompts')\
            .update({'is_active': False})\
            .eq('tool_name', tool_name)\
            .eq('provider', provider)\
            .eq('is_active', True)
        
        # Activate target version
        await self.supabase.table('system_prompts')\
            .update({'is_active': True})\
            .eq('tool_name', tool_name)\
            .eq('provider', provider)\
            .eq('version', version)
```

**Pattern 2: Conversation Persistence**

```python
class SupabaseConversationManager:
    async def store_conversation(
        self, 
        continuation_id: str, 
        tool_name: str,
        messages: list
    ):
        """Store conversation for later retrieval."""
        await self.supabase.table('conversation_history').upsert({
            'continuation_id': continuation_id,
            'tool_name': tool_name,
            'messages': messages,
            'updated_at': 'NOW()'
        })
    
    async def retrieve_conversation(self, continuation_id: str) -> dict:
        """Retrieve conversation by continuation ID."""
        result = await self.supabase.table('conversation_history')\
            .select('*')\
            .eq('continuation_id', continuation_id)\
            .single()
        
        return result
    
    async def cleanup_expired_conversations(self):
        """Remove expired conversations."""
        await self.supabase.table('conversation_history')\
            .delete()\
            .lt('expires_at', 'NOW()')
```

**Pattern 3: File Synchronization**

```python
class SupabaseFileSync:
    async def sync_moonshot_file(
        self, 
        moonshot_file_id: str, 
        filename: str,
        file_size: int
    ):
        """Sync Moonshot file with Supabase metadata."""
        await self.supabase.table('file_metadata').insert({
            'moonshot_file_id': moonshot_file_id,
            'original_filename': filename,
            'file_size_bytes': file_size,
            'uploaded_at': 'NOW()'
        })
    
    async def delete_file_bidirectional(self, moonshot_file_id: str):
        """Delete file from both Moonshot and Supabase."""
        # Delete from Moonshot
        await self.moonshot_client.delete_file(moonshot_file_id)
        
        # Delete from Supabase
        await self.supabase.table('file_metadata')\
            .delete()\
            .eq('moonshot_file_id', moonshot_file_id)
    
    async def identify_orphaned_files(self) -> list:
        """Find files in Supabase not in Moonshot."""
        supabase_files = await self.supabase.table('file_metadata')\
            .select('moonshot_file_id')
        
        moonshot_files = await self.moonshot_client.list_files()
        moonshot_ids = {f['id'] for f in moonshot_files}
        
        orphaned = [
            f['moonshot_file_id'] 
            for f in supabase_files 
            if f['moonshot_file_id'] not in moonshot_ids
        ]
        
        return orphaned
```

---

## Implementation Checklist (Updated)

### Phase 1: Critical Fixes (Week 1)
- [x] Investigate current Supabase setup via MCP
- [x] Validate findings with EXAI
- [ ] Consolidate overlapping tables
  - [ ] Migrate data from file_metadata to provider_file_uploads
  - [ ] Drop file_metadata table
  - [ ] Consolidate issue tracking tables
  - [ ] Update foreign key references
- [ ] Enable Realtime subscriptions
  - [ ] Enable on conversations table
  - [ ] Enable on messages table
  - [ ] Enable on files table
  - [ ] Enable on provider_file_uploads table
- [ ] Add critical indexes
  - [ ] conversations.session_id
  - [ ] conversations.continuation_id
  - [ ] messages.conversation_id
  - [ ] messages.created_at
  - [ ] files.storage_path
  - [ ] provider_file_uploads.provider_file_id

### Phase 2: System Prompts Migration (Week 2)
- [ ] Create system_prompts table
- [ ] Create prompt_versions table
- [ ] Create prompt_performance table
- [ ] Add indexes for performance
- [ ] Migrate existing prompts from Python to database
  - [ ] debug_prompt.py → database
  - [ ] analyze_prompt.py → database
  - [ ] codereview_prompt.py → database
  - [ ] chat_prompt.py → database
  - [ ] All other prompts → database
- [ ] Update tools to read prompts from database
- [ ] Test prompt versioning and rollback

### Phase 3: Security & Optimization (Week 3)
- [ ] Configure Row Level Security (RLS)
  - [ ] Enable RLS on conversations
  - [ ] Enable RLS on messages
  - [ ] Enable RLS on files
  - [ ] Enable RLS on system_prompts
  - [ ] Create appropriate policies
- [ ] Add missing foreign key constraints
  - [ ] messages → conversations
  - [ ] conversation_files → conversations
  - [ ] conversation_files → files
  - [ ] provider_file_uploads → files
- [ ] Optimize edge functions
  - [ ] Update gateway function
  - [ ] Update memory function
  - [ ] Update exai-chat function
- [ ] Test performance under load

### Phase 4: Testing & Validation (Week 4)
- [ ] Test Realtime subscriptions
- [ ] Test prompt versioning and rollback
- [ ] Test conversation persistence and retrieval
- [ ] Test file synchronization
- [ ] Validate non-blocking async recording
- [ ] Test failure scenarios and recovery
- [ ] Measure performance improvements

---

## Success Criteria

1. ✅ **Non-Blocking:** Supabase operations do NOT add latency to user requests
2. ✅ **Reliable:** 99.9% success rate for async recording
3. ✅ **Performant:** <100ms for conversation retrieval
4. ✅ **Scalable:** Handles 1000+ conversations without degradation
5. ✅ **Maintainable:** Clear schema, documented patterns, easy to extend

---

## Next Steps

1. Use Supabase MCP tools to explore current schema
2. Create investigation script to test MCP capabilities
3. Design and implement schema based on findings
4. Develop integration patterns incrementally
5. Test and validate each pattern independently
6. Document lessons learned and best practices

---

**Related Documents:**
- SYSTEMPROMPTS_ENHANCED_ANALYSIS_2025-10-21.md
- KNOWN_ISSUES_INVESTIGATION_ROADMAP_2025-10-21.md (Next)
- MASTER_CHECKLIST_FOR_NEXT_AGENT_2025-10-21.md (Final)

