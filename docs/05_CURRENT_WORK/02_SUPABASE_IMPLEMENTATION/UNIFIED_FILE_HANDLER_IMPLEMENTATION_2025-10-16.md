# UNIFIED FILE HANDLER IMPLEMENTATION - PHASE 1

**Date:** 2025-10-16
**Status:** ⏳ IN PROGRESS
**Priority:** HIGH
**Related Architecture:** UNIFIED_FILE_HANDLING_ARCHITECTURE_2025-10-16.md
**Conversation ID:** `f98b3145-d803-4809-a640-c7c0cdc58970`

---

## 🎯 OBJECTIVE

**Implement Phase 1 (Week 1) of Unified File Handling Architecture**

Create a unified file handling system with:
- Supabase Storage as primary backend
- Local volume as cache layer
- In-memory as fallback layer
- Provider-specific file ID management (Kimi, GLM)

---

## ✅ IMPLEMENTATION PLAN

### 1. Core Components ✅ DESIGNED

**UnifiedFileHandler Class** (`src/storage/unified_file_handler.py`)
- Three-tier storage architecture
- Async Python implementation
- Automatic cache management
- Provider integration support

**Key Methods:**
- `upload_file(file_path, metadata)` - Upload to Supabase + cache locally
- `download_file(file_id)` - Download with three-tier fallback
- `get_provider_file_id(file_id, provider)` - Get/create provider-specific file ID
- `cleanup_cache(max_age_days, max_size_mb)` - Automatic cache cleanup

---

### 2. Database Schema ✅ DESIGNED

**Table:** `file_metadata`

**Columns:**
- `file_id` (UUID, PRIMARY KEY) - Unique file identifier
- `original_filename` (TEXT) - Original filename
- `file_size` (BIGINT) - File size in bytes
- `mime_type` (TEXT) - MIME type
- `supabase_storage_path` (TEXT) - Path in Supabase Storage
- `local_cache_path` (TEXT) - Path in local cache
- `file_hash` (TEXT) - SHA-256 hash for deduplication
- `provider_file_ids` (JSONB) - Provider-specific file IDs {kimi: "file-xxx", glm: "file-yyy"}
- `upload_date` (TIMESTAMPTZ) - Upload timestamp
- `last_accessed` (TIMESTAMPTZ) - Last access timestamp
- `access_count` (INTEGER) - Access counter
- `metadata` (JSONB) - Additional metadata
- `created_at` (TIMESTAMPTZ) - Creation timestamp
- `updated_at` (TIMESTAMPTZ) - Last update timestamp

**Indexes:**
- `idx_file_metadata_upload_date` - For upload date queries
- `idx_file_metadata_last_accessed` - For cache cleanup
- `idx_file_metadata_file_hash` - For deduplication

**Triggers:**
- `update_file_metadata_updated_at` - Auto-update updated_at column

**RLS:** Enabled with allow-all policy (to be refined later)

---

### 3. Docker Configuration ✅ DESIGNED

**Volume Mount:**
```yaml
volumes:
  - ./files:/app/files
```

**Environment Variables:**
```bash
SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_key>
FILE_CACHE_DIR=/app/files
MAX_MEMORY_CACHE_SIZE=104857600  # 100MB
MAX_CACHE_SIZE_MB=1000
MAX_CACHE_AGE_DAYS=30
```

---

### 4. Three-Tier Fallback Strategy ✅ DESIGNED

**Tier 1: Supabase Storage (Primary)**
- Persistent storage
- Accessible from anywhere
- Automatic backups
- Scalable

**Tier 2: Local Volume (Cache)**
- Fast access
- Survives container restarts
- Limited by disk space
- Automatic cleanup

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

## 📋 IMPLEMENTATION TASKS

### Task 1: Create Database Schema ⏳ NEXT
- [ ] Create `file_metadata` table in Supabase
- [ ] Create indexes for performance
- [ ] Create auto-update trigger
- [ ] Enable RLS with allow-all policy
- [ ] Test schema with sample data

### Task 2: Create Supabase Storage Bucket ⏳ PENDING
- [ ] Create "exai-files" bucket in Supabase
- [ ] Configure bucket permissions
- [ ] Test upload/download functionality
- [ ] Configure CORS if needed

### Task 3: Implement UnifiedFileHandler Class ⏳ PENDING
- [ ] Create `src/storage/unified_file_handler.py`
- [ ] Implement `__init__()` method
- [ ] Implement `upload_file()` method
- [ ] Implement `download_file()` method
- [ ] Implement `get_provider_file_id()` method
- [ ] Implement `cleanup_cache()` method
- [ ] Implement helper methods (_calculate_file_hash, _get_mime_type)

### Task 4: Update Docker Configuration ⏳ PENDING
- [ ] Add volume mount to docker-compose.yml
- [ ] Add environment variables to .env.docker
- [ ] Add environment variables to .env.example
- [ ] Create ./files directory
- [ ] Test volume mount

### Task 5: Integration with MCP Server ⏳ PENDING
- [ ] Initialize UnifiedFileHandler in server startup
- [ ] Create file upload endpoint
- [ ] Create file download endpoint
- [ ] Create provider file ID endpoint
- [ ] Add error handling
- [ ] Add logging

### Task 6: Testing & Validation ⏳ PENDING
- [ ] Test file upload to Supabase
- [ ] Test file download with three-tier fallback
- [ ] Test provider file ID generation
- [ ] Test cache cleanup
- [ ] Test error handling
- [ ] Performance testing

---

## 🔧 DEPENDENCIES

**Python Packages:**
- `supabase-py` - Supabase Python client
- `aiofiles` - Async file operations
- `python-magic` or `mimetypes` - MIME type detection

**Supabase Setup:**
- Storage bucket: "exai-files"
- Database table: "file_metadata"
- Service role key for admin operations

**Docker:**
- Volume mount: `./files:/app/files`
- Environment variables configured

---

## 📊 PROGRESS TRACKING

**Overall Progress:** 20% (Design Complete)

| Component | Status | Progress |
|-----------|--------|----------|
| Database Schema | ✅ DESIGNED | 100% |
| Storage Bucket | ⏳ PENDING | 0% |
| UnifiedFileHandler | ✅ DESIGNED | 100% |
| Docker Config | ✅ DESIGNED | 100% |
| MCP Integration | ⏳ PENDING | 0% |
| Testing | ⏳ PENDING | 0% |

---

## 🎯 NEXT STEPS

**Immediate Actions:**
1. Create database schema in Supabase (Task 1)
2. Create Supabase Storage bucket (Task 2)
3. Implement UnifiedFileHandler class (Task 3)

**Follow-up Actions:**
4. Update Docker configuration (Task 4)
5. Integrate with MCP server (Task 5)
6. Test and validate (Task 6)

---

**Document Status:** IN PROGRESS  
**Next Action:** Create database schema in Supabase  
**Owner:** EXAI Development Team  
**Implementation Status:** 🏗️ PHASE 1 - WEEK 1 IN PROGRESS

