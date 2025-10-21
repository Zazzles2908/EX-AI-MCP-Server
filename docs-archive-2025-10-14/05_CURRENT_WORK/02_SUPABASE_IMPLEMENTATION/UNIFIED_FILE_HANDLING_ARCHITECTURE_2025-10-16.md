# Unified File Handling Architecture Design

**Created:** 2025-10-16  
**Status:** ✅ DESIGN COMPLETE - Ready for Implementation  
**EXAI Conversation:** `a0bdb843-a6e8-46b8-962b-0ad5deca73ba`  
**Model Used:** GLM-4.6 with web search (38.8s response time)  
**Supabase Database:** Personal AI (mxaazuhlqewmkweewyaz)

---

## 🎯 **DESIGN GOALS**

1. **Unified API:** Single interface for file upload/download across all systems
2. **Docker-Compatible:** Work seamlessly in Docker container
3. **Provider-Agnostic:** Support Moonshot, GLM, and Supabase
4. **Persistent Storage:** Files persist across container restarts
5. **Efficient:** Avoid duplicate uploads, use caching
6. **Fallback Strategy:** Graceful degradation if one system fails

---

## 📊 **CURRENT STATE ANALYSIS**

### **Environment Files:**
- `.env` - Main project environment (local development)
- `.env.docker` - Docker container environment (copied to `.env` in container)
- `.env.example` - Template for new users
- `.env.supabase` - Supabase-specific configuration (if exists)

### **Docker Architecture:**
- EXAI runs in Docker container (`exai-mcp-daemon`)
- Dockerfile copies `.env.docker` to `.env` in container (line 51)
- Current volume mount: `./logs:/app/logs` (logs only)
- Container restart: `docker-compose restart exai-daemon`
- Image rebuild: `docker-compose build exai-daemon`

### **Current File Handling Systems:**
1. **Moonshot/Kimi:** `upload_file()` → file_id (K2 models can read)
2. **Z.ai/GLM:** `upload_file()` → file_id (GLM models can read)
3. **Supabase Storage:** `FileHandler` with immediate upload
4. **EXAI Tools:** Accept `files` parameter (expect local paths)

### **THE PROBLEM:**
- EXAI runs in Docker container - can't access local files (`C:\Project\file.txt`)
- Multiple file handling systems with no unified strategy
- No clear path for file persistence across providers
- Volume mounting strategy unclear

---

## 🏗️ **UNIFIED ARCHITECTURE DESIGN**

### **1. Storage Strategy**

**Primary Storage:** Supabase Storage
- Persistent across container restarts
- Centralized metadata tracking
- Single source of truth
- Eliminates duplicate file storage

**Secondary Storage:** Provider-specific storage (on-demand)
- Upload to Moonshot/GLM only when required
- Track provider file IDs in Supabase metadata
- Automatic cleanup of unused provider files

**Tertiary Storage:** Local file system volume
- Temporary cache in `/app/files`
- Backup mechanism if Supabase unavailable
- Clear separation from application code

---

### **2. Docker Volume Strategy**

**Add dedicated files volume mount:**

```yaml
# In docker-compose.yml
volumes:
  - ./logs:/app/logs
  - ./files:/app/files  # NEW: Shared files directory
```

**Benefits:**
- Local development file access
- Container persistence for temporary files
- Backup mechanism if Supabase unavailable
- Clear separation from application code

**Directory Structure:**
```
./files/
  ├── cache/          # Temporary file cache
  ├── uploads/        # User uploads (before Supabase)
  └── downloads/      # Downloaded from Supabase
```

---

### **3. Unified File Handling API**

**Create:** `src/storage/unified_file_handler.py`

```python
class UnifiedFileHandler:
    """
    Unified file handling across Supabase, Moonshot, and GLM.
    
    Features:
    - Single API for all file operations
    - Automatic provider-specific uploads on-demand
    - Caching and deduplication
    - Fallback strategies
    """
    
    def upload_file(
        self,
        file_path: str,
        purpose: str = "general",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Upload file to Supabase and return unified file ID.
        
        Args:
            file_path: Local file path or file content
            purpose: File purpose (general, chat, analysis, etc.)
            metadata: Optional metadata (tags, description, etc.)
            
        Returns:
            Unified file ID (UUID)
        """
        
    def get_file_for_provider(
        self,
        unified_file_id: str,
        provider_name: str
    ) -> str:
        """
        Get file ID for specific provider, upload if needed.
        
        Args:
            unified_file_id: Unified file ID from upload_file()
            provider_name: Provider name (moonshot, glm)
            
        Returns:
            Provider-specific file ID
        """
        
    def download_file(
        self,
        unified_file_id: str,
        local_path: Optional[str] = None
    ) -> Union[str, bytes]:
        """
        Download file from Supabase to local path or return content.
        
        Args:
            unified_file_id: Unified file ID
            local_path: Optional local path to save file
            
        Returns:
            Local file path or file content
        """
        
    def delete_file(self, unified_file_id: str) -> bool:
        """
        Delete file from Supabase and all providers.
        
        Args:
            unified_file_id: Unified file ID
            
        Returns:
            True if successful
        """
        
    def list_files(
        self,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        List files with metadata.
        
        Args:
            filters: Optional filters (purpose, date range, etc.)
            
        Returns:
            List of file metadata dictionaries
        """
```

---

### **4. File Upload Workflow**

```
User → EXAI Tool → UnifiedFileHandler.upload_file()
                                    ↓
                        Upload to Supabase Storage
                                    ↓
                        Store metadata in database
                                    ↓
                        Return unified_file_id to user
```

**When provider needs the file:**
```
Provider → UnifiedFileHandler.get_file_for_provider()
                                    ↓
                        Check if already uploaded to provider
                                    ↓
            If yes: Return provider file ID
            If no: Upload to provider → Store ID → Return ID
```

---

### **5. Caching Strategy**

**Two-Level Caching:**
1. **Local Cache:** Temporary files in `/app/files/cache`
2. **Provider Cache:** Track provider file IDs in Supabase metadata

**Cache Invalidation:**
- TTL-based (24 hours default)
- LRU eviction when cache size exceeds limit
- Manual cleanup via admin API

---

### **6. Supabase Metadata Schema**

```sql
CREATE TABLE files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filename TEXT NOT NULL,
  storage_path TEXT NOT NULL,  -- supabase://bucket/path
  sha256 TEXT NOT NULL UNIQUE,
  size_bytes BIGINT NOT NULL,
  mime_type TEXT NOT NULL,
  purpose TEXT NOT NULL DEFAULT 'general',
  provider_ids JSONB DEFAULT '{}',  -- {"moonshot": "file_abc", "glm": "file_def"}
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed TIMESTAMPTZ DEFAULT NOW(),
  access_count INTEGER DEFAULT 0,
  created_by TEXT,
  conversation_id TEXT
);

CREATE INDEX idx_files_sha256 ON files(sha256);
CREATE INDEX idx_files_conversation ON files(conversation_id);
CREATE INDEX idx_files_created_at ON files(created_at DESC);
```

---

### **7. Environment Configuration**

**Add to `.env.example` (and all environment files):**

```bash
# ============================================================================
# UNIFIED FILE HANDLING CONFIGURATION
# ============================================================================
# Primary storage backend (supabase, local, dual)
FILE_STORAGE_BACKEND=supabase

# Upload files to Supabase immediately when received
UPLOAD_FILES_IMMEDIATELY=true

# Enable local file cache in /app/files
ENABLE_FILE_CACHE=true
FILE_CACHE_DIR=/app/files/cache
FILE_CACHE_MAX_SIZE_MB=500
FILE_CACHE_TTL_HOURS=24

# Auto-cleanup provider files after TTL
AUTO_CLEANUP_PROVIDER_FILES=true
PROVIDER_FILE_TTL_HOURS=72

# Fallback to local storage if Supabase fails
ENABLE_FILE_FALLBACK=true

# Supabase Storage bucket name
SUPABASE_FILES_BUCKET=user-files
```

---

### **8. Container Restart vs Rebuild Guidelines**

**Restart Needed For:**
- Configuration changes (.env files)
- Volume mount changes
- Cache clearing
- Environment variable updates

**Rebuild Needed For:**
- Code changes to file handling logic
- New Python dependencies
- Dockerfile changes
- Base image updates

**Commands:**
```bash
# Restart container (config changes)
docker-compose restart exai-daemon

# Rebuild and restart (code changes)
docker-compose build exai-daemon
docker-compose up -d exai-daemon
```

---

### **9. Fallback Strategy**

**Three-Tier Fallback System:**
1. **Primary:** Supabase Storage (persistent, cloud-based)
2. **Secondary:** Local file system volume (`/app/files`)
3. **Tertiary:** In-memory storage (temporary, lost on restart)

**Fallback Logic:**
```python
try:
    # Try Supabase
    file_id = upload_to_supabase(file_path)
except SupabaseError:
    try:
        # Fallback to local volume
        file_id = save_to_local_volume(file_path)
    except IOError:
        # Last resort: in-memory
        file_id = save_to_memory(file_path)
```

---

### **10. Security Considerations**

1. **File Integrity:** SHA256 hashing for verification
2. **Access Control:** File ownership and permissions
3. **Path Sanitization:** Prevent directory traversal attacks
4. **Rate Limiting:** Prevent abuse via upload limits
5. **Size Limits:** Enforce maximum file sizes
6. **Virus Scanning:** Optional integration with antivirus APIs

---

## 🚀 **IMPLEMENTATION PLAN**

**Phase 1: Core Infrastructure (Week 1)**
1. Create `UnifiedFileHandler` class
2. Implement Supabase Storage integration
3. Add local volume support
4. Create database schema

**Phase 2: Provider Integration (Week 2)**
5. Update Moonshot provider to use unified handler
6. Update GLM provider to use unified handler
7. Implement provider file ID caching

**Phase 3: Tool Integration (Week 3)**
8. Update EXAI tools to use unified file IDs
9. Implement file download/retrieval
10. Add error handling and fallbacks

**Phase 4: Testing & Migration (Week 4)**
11. Comprehensive testing (unit, integration, e2e)
12. Migration script for existing files
13. Documentation and examples

---

**Status:** ✅ Design complete, ready for implementation  
**Next Steps:** Begin Phase 1 implementation

