# 🟣 Track 3: Store - READY TO START
**Goal:** Files & conversations survive container restarts  
**Status:** ⏳ NOT STARTED  
**Estimated Time:** 4 hours  
**Priority:** MEDIUM (quality of life improvement)

---

## 🎯 Single Goal

**Make file uploads and chat history persist across Docker container restarts.**

Current problem:
- File uploads stored in container (lost on restart)
- Chat history in memory (lost on restart)
- Users lose context after container rebuild

Target state:
- Files uploaded to Supabase Storage
- Chat history saved to Supabase Database
- Everything survives container restarts

---

## 📋 Implementation Plan

### Use Existing Supabase Project
**Project:** `mxaazuhlqewmkweewyaz`  
**No new infrastructure needed!**

---

### Phase 1: File Upload to Supabase (90 min)

#### Step 1: Create Storage Bucket (5 min)
1. Open Supabase Dashboard
2. Navigate to Storage
3. Create new bucket: `mcp-files` (private)
4. Set permissions: Authenticated users only

#### Step 2: Wire File Upload (60 min)

**File to modify:** `src/tools/kimi_upload_and_extract.py`

**Current flow:**
```python
# Upload to Kimi API
file_id = kimi_api.upload(file_path)

# Save locally
local_path = save_to_temp(file_content)

# Return local path
return {"file_path": local_path}
```

**New flow:**
```python
# Upload to Kimi API (keep existing)
file_id = kimi_api.upload(file_path)

# Upload to Supabase Storage
storage_path = supabase_service.upload_file(
    bucket="mcp-files",
    file_path=file_path,
    file_content=file_content
)

# Return Supabase path
return {"file_path": storage_path, "kimi_file_id": file_id}
```

#### Step 3: Test File Upload (25 min)
```bash
# Upload file
kimi_upload_and_extract_EXAI-WS with file="test.txt"

# Restart container
docker-compose restart

# Verify file still accessible
# Check Supabase Dashboard → Storage → mcp-files
```

---

### Phase 2: Chat History to Supabase (90 min)

#### Step 1: Create Database Tables (10 min)

**SQL Schema:**
```sql
-- Sessions table
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  continuation_id TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  user_id TEXT,  -- For future multi-user support
  metadata JSONB
);

-- Messages table
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL,  -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_sessions_continuation ON chat_sessions(continuation_id);
CREATE INDEX idx_messages_session ON chat_messages(session_id);
CREATE INDEX idx_messages_created ON chat_messages(created_at);
```

#### Step 2: Wire Chat History (60 min)

**File to modify:** `src/tools/chat.py`

**Current flow:**
```python
# Call model
response = await model.chat(prompt)

# Return response
return {"content": response}
```

**New flow:**
```python
# Create or get session
if continuation_id:
    session = supabase_service.get_session(continuation_id)
else:
    session = supabase_service.create_session()

# Save user message
supabase_service.add_message(
    session_id=session.id,
    role="user",
    content=prompt
)

# Call model
response = await model.chat(prompt)

# Save assistant message
supabase_service.add_message(
    session_id=session.id,
    role="assistant",
    content=response
)

# Return response with continuation_id
return {
    "content": response,
    "continuation_id": session.continuation_id
}
```

#### Step 3: Test Chat History (20 min)
```bash
# Start chat
chat_EXAI-WS with prompt="Hello"
# Note continuation_id from response

# Continue chat
chat_EXAI-WS with prompt="Remember me?" continuation_id="<id>"

# Restart container
docker-compose restart

# Continue chat again (should load history)
chat_EXAI-WS with prompt="What did I say?" continuation_id="<id>"
```

---

### Phase 3: Supabase Service Implementation (60 min)

**Create new file:** `utils/infrastructure/supabase_service.py`

```python
from supabase import create_client, Client
import os

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(url, key)
    
    # File operations
    def upload_file(self, bucket: str, file_path: str, file_content: bytes) -> str:
        """Upload file to Supabase Storage"""
        result = self.client.storage.from_(bucket).upload(
            path=file_path,
            file=file_content
        )
        return result.path
    
    def download_file(self, bucket: str, file_path: str) -> bytes:
        """Download file from Supabase Storage"""
        return self.client.storage.from_(bucket).download(file_path)
    
    # Session operations
    def create_session(self, continuation_id: str = None) -> dict:
        """Create new chat session"""
        if not continuation_id:
            continuation_id = str(uuid.uuid4())
        
        result = self.client.table("chat_sessions").insert({
            "continuation_id": continuation_id
        }).execute()
        return result.data[0]
    
    def get_session(self, continuation_id: str) -> dict:
        """Get existing session"""
        result = self.client.table("chat_sessions").select("*").eq(
            "continuation_id", continuation_id
        ).execute()
        return result.data[0] if result.data else None
    
    # Message operations
    def add_message(self, session_id: str, role: str, content: str) -> dict:
        """Add message to session"""
        result = self.client.table("chat_messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content
        }).execute()
        return result.data[0]
    
    def get_messages(self, session_id: str) -> list:
        """Get all messages for session"""
        result = self.client.table("chat_messages").select("*").eq(
            "session_id", session_id
        ).order("created_at").execute()
        return result.data

# Singleton instance
supabase_service = SupabaseService()
```

---

## 🔧 Configuration

### Environment Variables (.env.docker)

```bash
# Supabase Configuration (NEW - to be added)
SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co
SUPABASE_KEY=<your-service-role-key>  # Get from Supabase Dashboard
SUPABASE_STORAGE_BUCKET=mcp-files
```

### Dependencies

**Add to requirements.txt:**
```
supabase>=2.0.0
```

**Install:**
```bash
pip install supabase
```

---

## 🧪 Testing Checklist

### File Upload Test (30 min)
- [ ] Upload file via `kimi_upload_and_extract_EXAI-WS`
- [ ] Verify file in Supabase Dashboard → Storage → mcp-files
- [ ] Restart container
- [ ] Verify file still accessible
- [ ] Download file and verify content

### Chat History Test (30 min)
- [ ] Start chat with `chat_EXAI-WS`
- [ ] Note continuation_id
- [ ] Continue chat with same continuation_id
- [ ] Verify messages in Supabase Dashboard → Database → chat_messages
- [ ] Restart container
- [ ] Continue chat with same continuation_id
- [ ] Verify history loads correctly

### Edge Cases (30 min)
- [ ] Upload large file (>10MB)
- [ ] Long chat session (>100 messages)
- [ ] Multiple concurrent sessions
- [ ] Invalid continuation_id (should create new session)

---

## 📊 Success Criteria

### Must Have
- [ ] Files uploaded to Supabase Storage
- [ ] Files survive container restarts
- [ ] Chat history saved to Supabase Database
- [ ] Chat history survives container restarts
- [ ] Continuation_id works across restarts

### Nice to Have
- [ ] File versioning
- [ ] Chat history search
- [ ] Session expiration (auto-cleanup old sessions)
- [ ] Multi-user support (user_id column)

---

## 🚫 What NOT to Do

| Task | Reason | Action |
|------|--------|--------|
| Perfect schema | Ship working first | ❌ Add indexes later |
| Multi-user auth | Future feature | ❌ Add user_id column only |
| File versioning | Not needed yet | ❌ Simple upload/download |
| Complex search | YAGNI | ❌ Basic queries only |

---

## 🔄 Rollback Plan

If Supabase integration causes issues:

1. **Disable Supabase**
   ```bash
   # In .env.docker
   USE_SUPABASE=false  # Add this flag
   ```

2. **Fallback to local storage**
   ```python
   if os.getenv("USE_SUPABASE") == "true":
       storage_path = supabase_service.upload_file(...)
   else:
       storage_path = save_to_temp(...)  # Old behavior
   ```

3. **Restart container**
   ```bash
   docker-compose restart
   ```

---

## 📝 Known Issues

### From Previous Planning
1. **Supabase credentials** need to be added to `.env.docker`
   - Get from Supabase Dashboard → Settings → API
   - Use service role key (not anon key)

2. **File size limits** in Supabase Storage
   - Free tier: 1GB total storage
   - Max file size: 50MB per file
   - Workaround: Implement file size check before upload

3. **Database connection pooling**
   - Supabase client handles this automatically
   - No manual configuration needed

---

## 🚀 Next Steps

### Immediate (This Week)
1. [ ] Create Supabase storage bucket
2. [ ] Create database tables
3. [ ] Implement `supabase_service.py`
4. [ ] Wire file upload
5. [ ] Wire chat history
6. [ ] Test end-to-end

### Future Enhancements
- [ ] File versioning
- [ ] Session expiration
- [ ] Multi-user support
- [ ] Search functionality

---

## 📚 Related Documentation

- **Track 1:** `TRACK_1_STABILIZE_STATUS.md` (COMPLETE)
- **Track 2:** `TRACK_2_SCALE_PLAN.md` (NOT STARTED)
- **Supabase Plan:** `SUPABASE_INTEGRATION_REVISED_2025-10-15.md` (to be archived)

---

**Track 3 Status:** ⏳ READY TO START - Begin with Phase 1 file upload

