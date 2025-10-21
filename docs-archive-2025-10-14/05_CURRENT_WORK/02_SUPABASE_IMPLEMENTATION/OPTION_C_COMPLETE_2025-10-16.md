# OPTION C: UNIFIED FILE HANDLING ARCHITECTURE - PHASE 1 COMPLETE

**Date:** 2025-10-16
**Status:** ✅ COMPLETE (Design & Schema)
**Priority:** HIGH
**Conversation ID:** `f98b3145-d803-4809-a640-c7c0cdc58970`

---

## 🎯 OBJECTIVE ACHIEVED

**Designed and prepared Phase 1 of Unified File Handling Architecture**

Completed:
- ✅ Comprehensive implementation design with EXAI (GLM-4.6 + web search)
- ✅ Database schema created in Supabase
- ✅ Three-tier storage architecture designed
- ✅ UnifiedFileHandler class specification complete
- ✅ Docker configuration planned
- ✅ Integration strategy defined

---

## ✅ DELIVERABLES

### 1. Database Schema ✅ CREATED

**Table:** `file_metadata` (Supabase)

**Schema:**
```sql
CREATE TABLE file_metadata (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    supabase_storage_path TEXT NOT NULL,
    local_cache_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    provider_file_ids JSONB DEFAULT '{}',
    upload_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    access_count INTEGER NOT NULL DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Indexes Created:**
- `idx_file_metadata_upload_date` - For upload date queries
- `idx_file_metadata_last_accessed` - For cache cleanup
- `idx_file_metadata_file_hash` - For deduplication

**Triggers Created:**
- `update_file_metadata_updated_at` - Auto-update updated_at column

**RLS:** Enabled with allow-all policy

---

### 2. Storage Infrastructure ✅ IDENTIFIED

**Existing Buckets:**
- `user-files` (52MB limit) - Will use for unified file handler
- `generated-files` (10MB limit) - For generated content

**Decision:** Use existing `user-files` bucket instead of creating new "exai-files" bucket

---

### 3. UnifiedFileHandler Class ✅ DESIGNED

**Location:** `src/storage/unified_file_handler.py` (to be created)

**Key Methods:**
```python
class UnifiedFileHandler:
    async def upload_file(file_path, metadata) -> Dict[str, Any]
    async def download_file(file_id) -> Tuple[bytes, Dict[str, Any]]
    async def get_provider_file_id(file_id, provider) -> str
    async def cleanup_cache(max_age_days, max_size_mb) -> Dict[str, int]
    async def _upload_to_provider(file_content, metadata, provider) -> str
    async def _calculate_file_hash(file_path) -> str
    async def _get_mime_type(file_path) -> str
```

**Features:**
- Three-tier storage (Supabase → Local → Memory)
- Automatic cache management
- Provider-specific file ID tracking
- SHA-256 hash for deduplication
- Async Python implementation
- Automatic cleanup of old cache files

---

### 4. Three-Tier Architecture ✅ DESIGNED

**Tier 1: Supabase Storage (Primary)**
- Persistent storage
- Accessible from anywhere
- Automatic backups
- Scalable
- Bucket: `user-files`

**Tier 2: Local Volume (Cache)**
- Fast access
- Survives container restarts
- Limited by disk space (1GB default)
- Automatic cleanup (30 days default)
- Path: `./files:/app/files`

**Tier 3: In-Memory (Fallback)**
- Fastest access
- Limited by RAM (100MB default)
- Lost on container restart
- For frequently accessed files

**Download Flow:**
1. Check memory cache → Return if found
2. Check local cache → Return if found + add to memory
3. Download from Supabase → Cache locally + add to memory

---

### 5. Docker Configuration ✅ PLANNED

**Volume Mount (to be added):**
```yaml
volumes:
  - ./files:/app/files
```

**Environment Variables (to be added):**
```bash
# File Handling Configuration
SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_key>
FILE_CACHE_DIR=/app/files
FILE_STORAGE_BUCKET=user-files
MAX_MEMORY_CACHE_SIZE=104857600  # 100MB
MAX_CACHE_SIZE_MB=1000
MAX_CACHE_AGE_DAYS=30
```

---

### 6. Integration Strategy ✅ DEFINED

**MCP Server Integration:**
```python
# Initialize file handler
file_handler = UnifiedFileHandler(
    supabase_url=os.environ.get("SUPABASE_URL"),
    supabase_key=os.environ.get("SUPABASE_SERVICE_KEY"),
    local_cache_dir=os.environ.get("FILE_CACHE_DIR", "./files"),
    bucket_name=os.environ.get("FILE_STORAGE_BUCKET", "user-files"),
    max_memory_cache_size=int(os.environ.get("MAX_MEMORY_CACHE_SIZE", 104857600))
)

# Endpoints to create
async def handle_file_upload(request)
async def handle_file_download(request)
async def handle_provider_file_id(request)
```

---

## 📊 IMPLEMENTATION STATUS

**Phase 1 Progress:** 40% (Design & Schema Complete)

| Component | Status | Progress |
|-----------|--------|----------|
| Database Schema | ✅ CREATED | 100% |
| Storage Bucket | ✅ IDENTIFIED | 100% |
| UnifiedFileHandler Design | ✅ COMPLETE | 100% |
| Docker Config Design | ✅ COMPLETE | 100% |
| MCP Integration Design | ✅ COMPLETE | 100% |
| **Implementation** | ⏳ PENDING | 0% |
| **Testing** | ⏳ PENDING | 0% |

---

## 🎯 NEXT STEPS (Implementation)

### Immediate Actions (Week 1 Remaining):
1. **Create UnifiedFileHandler class** ⏳ NEXT
   - Implement `src/storage/unified_file_handler.py`
   - Add all methods as designed
   - Add error handling and logging

2. **Update Docker configuration** ⏳ PENDING
   - Add volume mount to docker-compose.yml
   - Add environment variables to .env.docker
   - Add environment variables to .env.example
   - Create ./files directory

3. **Integrate with MCP server** ⏳ PENDING
   - Initialize UnifiedFileHandler in server startup
   - Create file upload/download endpoints
   - Add provider file ID endpoint

4. **Testing & Validation** ⏳ PENDING
   - Test file upload to Supabase
   - Test three-tier fallback
   - Test provider file ID generation
   - Test cache cleanup

---

## 📝 DEPENDENCIES

**Python Packages (to be installed):**
```bash
pip install supabase-py aiofiles python-magic
```

**Supabase Setup:**
- ✅ Storage bucket: `user-files` (existing)
- ✅ Database table: `file_metadata` (created)
- ⏳ Service role key configuration

**Docker:**
- ⏳ Volume mount: `./files:/app/files`
- ⏳ Environment variables configured

---

## 🔍 EXAI RESEARCH SUMMARY

**Model Used:** GLM-4.6 with web search enabled
**Conversation ID:** `f98b3145-d803-4809-a640-c7c0cdc58970`

**Research Conducted:**
- Supabase Storage Python API documentation
- Async Python file handling best practices
- Three-tier caching strategies
- Provider file upload patterns

**Key Findings:**
- Supabase-py library supports async operations
- Storage API provides upload/download with retry logic
- File metadata tracking essential for multi-provider support
- Cache cleanup prevents disk space issues
- SHA-256 hashing enables deduplication

---

## 📋 LESSONS LEARNED

**Design Decisions:**
1. Use existing `user-files` bucket instead of creating new bucket
2. Three-tier architecture provides optimal performance/reliability balance
3. Provider file IDs stored in JSONB for flexibility
4. Automatic cache cleanup prevents disk space issues
5. SHA-256 hashing enables file deduplication

**Implementation Best Practices:**
1. Async Python for non-blocking file operations
2. Comprehensive error handling at each tier
3. Automatic fallback between storage tiers
4. Metadata tracking for analytics and debugging
5. RLS enabled for future security enhancements

---

**Document Status:** COMPLETE (Design Phase)  
**Next Action:** Implement UnifiedFileHandler class  
**Owner:** EXAI Development Team  
**Implementation Status:** 🏗️ READY FOR IMPLEMENTATION

