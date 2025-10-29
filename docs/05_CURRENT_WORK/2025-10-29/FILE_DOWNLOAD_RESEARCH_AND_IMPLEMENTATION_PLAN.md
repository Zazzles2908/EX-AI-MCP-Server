# File Download System - Research & Implementation Plan

**Date:** 2025-10-29  
**EXAI Consultation ID:** 08fde2b0-b7d7-47ac-ba1d-e10109f0a994  
**Status:** ✅ Research Complete - Implementation Plan Ready  
**Remaining EXAI Exchanges:** 18

---

## 🎯 **EXECUTIVE SUMMARY**

This document provides comprehensive research findings and implementation plan for adding file download capabilities to the EXAI-MCP-Server system. The research was conducted using EXAI (GLM-4.6) with web search enabled to gather accurate API documentation and industry best practices.

**Key Findings:**
- ✅ Moonshot/Kimi supports full file download via OpenAI-compatible API
- ❌ Z.ai/GLM has limited/no file download support (session-bound only)
- ✅ Supabase storage can serve as persistent cache layer
- ✅ Recommended separate `smart_file_download` tool for clean architecture

---

## 📊 **PROVIDER CAPABILITY MATRIX**

| Feature | Moonshot/Kimi | Z.ai/GLM | Supabase Storage |
|---------|---------------|----------|------------------|
| File Download | ✅ Full Support | ❌ No Support | ✅ Full Support |
| Metadata Retrieval | ✅ Full Support | ⚠️ Basic Support | ✅ Full Support |
| File Formats | ✅ Multiple Formats | ⚠️ Limited Formats | ✅ All Formats |
| Session Persistence | ✅ Persistent (30+ days) | ❌ Session-bound | ✅ Permanent |
| Size Limits | ✅ Up to 512MB | ⚠️ Smaller Limits | ✅ Configurable |
| API Endpoints | ✅ OpenAI-compatible | ❌ Not Available | ✅ REST API |

---

## 🔌 **API ENDPOINTS**

### **Moonshot/Kimi API**

**File Download:**
```bash
curl -X GET "https://api.moonshot.cn/v1/files/{file_id}/content" \
  -H "Authorization: Bearer {api_key}" \
  -o "{local_filename}"
```

**File Metadata:**
```bash
curl -X GET "https://api.moonshot.cn/v1/files/{file_id}" \
  -H "Authorization: Bearer {api_key}"
```

**Response Format:**
```json
{
  "id": "file_xxx",
  "object": "file",
  "bytes": 12345,
  "created_at": 1234567890,
  "filename": "example.txt",
  "purpose": "file-extract"
}
```

### **Z.ai/GLM API**

**Status:** ❌ No persistent file download support
- Files are session-bound only
- Cannot retrieve files after session ends
- Recommendation: Use Supabase cache for GLM files

### **Supabase Storage API**

**File Download:**
```bash
curl -X GET "https://{project_ref}.supabase.co/storage/v1/object/bucket/{file_path}" \
  -H "Authorization: Bearer {supabase_key}" \
  -o "{local_filename}"
```

---

## 🏗️ **RECOMMENDED ARCHITECTURE**

### **Design Decision: Separate Tool**

**Recommendation:** Create separate `smart_file_download` tool

**Rationale:**
- ✅ Separation of concerns (upload/query vs download)
- ✅ Different error handling patterns
- ✅ Allows future expansion of download-specific features
- ✅ Maintains backward compatibility

### **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    smart_file_download                       │
│                                                              │
│  1. Check Supabase Cache                                    │
│  2. If MISS → Download from Provider (Kimi/GLM)            │
│  3. Verify SHA256 Hash                                      │
│  4. Store in Supabase Cache                                 │
│  5. Update Download Tracking                                │
│  6. Return Local File Path                                  │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Supabase   │    │    Kimi      │    │     GLM      │
│    Cache     │    │   Provider   │    │   Provider   │
│              │    │              │    │              │
│  • Metadata  │    │  • Download  │    │  • Session   │
│  • SHA256    │    │  • Metadata  │    │  • Limited   │
│  • Tracking  │    │  • Persist   │    │  • No DL     │
└──────────────┘    └──────────────┘    └──────────────┘
```

### **Provider Fallback Strategy**

**Priority Order:** Supabase → Kimi → GLM

```python
def resolve_file_location(file_id: str) -> Tuple[str, str]:
    """
    Returns (provider, file_id) for download
    Priority: Supabase cache → Kimi → GLM
    """
    # 1. Check Supabase cache first
    cached = supabase.table("provider_file_uploads")\
        .select("*")\
        .eq("provider_file_id", file_id)\
        .execute()
    
    if cached.data:
        return cached.data[0]["provider"], file_id
    
    # 2. Check if file_id follows Kimi pattern
    if file_id.startswith("file_") or len(file_id) > 20:
        return "kimi", file_id
    
    # 3. Default to GLM (session-bound)
    return "glm", file_id
```

---

## 💾 **SUPABASE SCHEMA DESIGN**

### **Recommended Approach: Extend Existing Table**

**Add to `provider_file_uploads` table:**
```sql
ALTER TABLE provider_file_uploads 
ADD COLUMN download_count INTEGER DEFAULT 0,
ADD COLUMN last_downloaded_at TIMESTAMP WITH TIME ZONE;
```

**Create download history table:**
```sql
CREATE TABLE file_download_history (
    id SERIAL PRIMARY KEY,
    provider_file_id VARCHAR(255) NOT NULL 
        REFERENCES provider_file_uploads(provider_file_id),
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    downloaded_by VARCHAR(100),
    destination_path VARCHAR(500)
);
```

**Benefits:**
- ✅ Maintains simplicity in main table
- ✅ Provides detailed history tracking
- ✅ Enables analytics and cleanup decisions
- ✅ Consistent with existing deduplication system

---

## 📁 **FILE PATH MANAGEMENT**

### **Docker Container Paths**

**Default Download Directory:** `/mnt/project/downloads/`

**Path Validation:**
```python
def validate_destination_path(path: str) -> str:
    """Ensure path is within allowed directories"""
    abs_path = os.path.abspath(path)
    if not abs_path.startswith("/mnt/project/"):
        raise ValueError("Downloads must be within /mnt/project/")
    return abs_path
```

**Cleanup Strategy:**
```python
# Option 1: Immediate cleanup after processing
def download_and_process(file_id: str, processor_func):
    temp_path = download_file(file_id, destination="/tmp/")
    try:
        result = processor_func(temp_path)
    finally:
        os.unlink(temp_path)  # Always cleanup
    return result

# Option 2: Configurable retention
def cleanup_old_downloads(max_age_hours=24):
    cutoff = time.time() - (max_age_hours * 3600)
    for filepath in Path(DEFAULT_DOWNLOAD_DIR).glob("*"):
        if filepath.stat().st_mtime < cutoff:
            filepath.unlink()
```

---

## 🛡️ **ERROR HANDLING STRATEGY**

### **HTTP Status Code Handling**

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 404 | File not found | Check Supabase cache → Remove from DB if expired |
| 403 | Permission denied | Re-authenticate → Retry |
| 410 | File expired | Remove from database → Fail gracefully |
| 429 | Rate limit | Queue request → Exponential backoff |
| 500 | Server error | Retry with backoff → Max 3 attempts |

**Implementation:**
```python
def handle_download_error(response: requests.Response, file_id: str):
    if response.status_code == 404:
        cached = check_supabase_cache(file_id)
        if cached:
            return download_from_supabase(file_id)
        else:
            supabase.table("provider_file_uploads")\
                .delete()\
                .eq("provider_file_id", file_id)\
                .execute()
            raise FileNotFoundError(f"File {file_id} not found")
    
    elif response.status_code == 403:
        refresh_provider_tokens()
        raise PermissionError("Authentication refreshed, retry")
    
    elif response.status_code == 410:
        supabase.table("provider_file_uploads")\
            .delete()\
            .eq("provider_file_id", file_id)\
            .execute()
        raise FileNotFoundError(f"File {file_id} expired")
    
    elif response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
        return retry_download(file_id, max_retries=3)
```

---

## 🔐 **SECURITY & INTEGRITY VALIDATION**

### **SHA256-based Verification**

```python
def download_with_verification(file_id: str, destination: str) -> str:
    # 1. Get expected hash from database
    file_record = supabase.table("provider_file_uploads")\
        .select("sha256_hash")\
        .eq("provider_file_id", file_id)\
        .execute()
    
    expected_hash = file_record.data[0]["sha256_hash"] if file_record.data else None
    
    # 2. Download file
    local_path = download_from_provider(file_id, destination)
    
    # 3. Verify hash if expected
    if expected_hash:
        actual_hash = calculate_sha256(local_path)
        if actual_hash != expected_hash:
            os.unlink(local_path)  # Remove corrupted file
            raise ValueError(f"Hash mismatch for {file_id}")
    
    # 4. Update download tracking
    supabase.table("provider_file_uploads").update({
        "download_count": supabase.sql("download_count + 1"),
        "last_downloaded_at": "now()"
    }).eq("provider_file_id", file_id).execute()
    
    return local_path
```

### **Security Considerations**

1. **File Type Validation:** Verify using magic bytes
2. **Size Limits:** Enforce per-file-type limits
3. **Malware Scanning:** Optional ClamAV integration
4. **Access Control:** User-based permissions
5. **Audit Logging:** Track all download operations

---

## 💻 **CODE EXAMPLES**

### **SmartFileDownload Tool Structure**

```python
class SmartFileDownload:
    """
    Unified file download interface with automatic caching and integrity validation.

    Features:
    - Cache-first download strategy (Supabase → Provider)
    - SHA256-based integrity verification
    - Provider fallback (Kimi → Supabase)
    - Download tracking and analytics
    """

    def __init__(self, supabase_client, providers, dedup_manager):
        self.supabase = supabase_client
        self.providers = providers
        self.dedup_manager = dedup_manager
        self.default_download_dir = "/mnt/project/downloads/"

    async def execute(self, file_id: str, destination: str = None) -> str:
        """
        Download file by ID and return local path.

        Args:
            file_id: Provider file ID or Supabase file ID
            destination: Optional destination path (default: /mnt/project/downloads/)

        Returns:
            Local file path
        """
        # 1. Validate destination
        dest = destination or self.default_download_dir
        dest = self._validate_destination(dest)

        # 2. Check cache first
        cached_path = await self._check_cache(file_id)
        if cached_path:
            logger.info(f"[SMART_FILE_DOWNLOAD] Cache HIT: {file_id}")
            return cached_path

        # 3. Determine provider
        provider = await self._determine_provider(file_id)

        # 4. Download from provider
        logger.info(f"[SMART_FILE_DOWNLOAD] Cache MISS - downloading from {provider}")
        local_path = await self._download_from_provider(provider, file_id, dest)

        # 5. Verify integrity
        await self._verify_integrity(file_id, local_path)

        # 6. Update tracking
        await self._update_download_tracking(file_id, local_path)

        return local_path

    async def _check_cache(self, file_id: str) -> Optional[str]:
        """Check if file exists in Supabase cache"""
        # Implementation here
        pass

    async def _determine_provider(self, file_id: str) -> str:
        """Determine which provider has the file"""
        # Implementation here
        pass

    async def _download_from_provider(self, provider: str, file_id: str, dest: str) -> str:
        """Provider-specific download implementation"""
        if provider == "kimi":
            return await self._download_from_kimi(file_id, dest)
        elif provider == "supabase":
            return await self._download_from_supabase(file_id, dest)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _download_from_kimi(self, file_id: str, dest: str) -> str:
        """Download file from Kimi/Moonshot"""
        client = OpenAI(
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url="https://api.moonshot.cn/v1"
        )

        # Get file metadata first
        metadata = client.files.retrieve(file_id)
        filename = metadata.filename

        # Download file content
        content = client.files.content(file_id)

        # Save to destination
        local_path = os.path.join(dest, filename)
        with open(local_path, 'wb') as f:
            f.write(content.content)

        return local_path

    async def _verify_integrity(self, file_id: str, local_path: str):
        """Verify downloaded file integrity using SHA256"""
        # Get expected hash from database
        file_record = self.supabase.table("provider_file_uploads")\
            .select("sha256_hash")\
            .eq("provider_file_id", file_id)\
            .execute()

        if not file_record.data:
            logger.warning(f"No hash found for {file_id}, skipping verification")
            return

        expected_hash = file_record.data[0]["sha256_hash"]
        actual_hash = self.dedup_manager.calculate_sha256(local_path)

        if actual_hash != expected_hash:
            os.unlink(local_path)
            raise ValueError(f"Hash mismatch for {file_id}: expected {expected_hash}, got {actual_hash}")

        logger.info(f"[SMART_FILE_DOWNLOAD] Integrity verified: {file_id}")

    async def _update_download_tracking(self, file_id: str, local_path: str):
        """Update download count and history"""
        # Update main table
        self.supabase.table("provider_file_uploads").update({
            "download_count": self.supabase.sql("download_count + 1"),
            "last_downloaded_at": "now()"
        }).eq("provider_file_id", file_id).execute()

        # Record in history
        self.supabase.table("file_download_history").insert({
            "provider_file_id": file_id,
            "destination_path": local_path
        }).execute()
```

---

## 🎯 **USE CASES**

### **Use Case 1: Download AI-Generated File**

**Scenario:** User asks AI to generate a Python script, wants to download it locally

```python
# User request: "Download the generated script to my project"
result = await smart_file_download.execute(
    file_id="file_abc123",
    destination="/mnt/project/EX-AI-MCP-Server/scripts/"
)
# Returns: "/mnt/project/EX-AI-MCP-Server/scripts/generated_script.py"
```

### **Use Case 2: Retrieve Previously Uploaded File**

**Scenario:** User uploaded a file weeks ago, wants to retrieve it

```python
# User request: "Download the file I uploaded last week"
result = await smart_file_download.execute(
    file_id="file_xyz789"
)
# Returns: "/mnt/project/downloads/my_document.pdf"
```

### **Use Case 3: Batch Download Multiple Files**

**Scenario:** User wants to download multiple files at once

```python
# User request: "Download all files from this conversation"
file_ids = ["file_1", "file_2", "file_3"]
results = await asyncio.gather(*[
    smart_file_download.execute(file_id)
    for file_id in file_ids
])
# Returns: ["/mnt/project/downloads/file1.txt", ...]
```

### **Use Case 4: Download with Integrity Verification**

**Scenario:** Critical file download requiring integrity check

```python
# Automatic integrity verification
try:
    result = await smart_file_download.execute(file_id="file_critical")
    # File verified automatically via SHA256
except ValueError as e:
    # Hash mismatch - file corrupted
    logger.error(f"Download failed: {e}")
```

---

## ⚠️ **RISK ASSESSMENT**

### **High Risk Items**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GLM session dependency causes file loss | High | High | Immediate Supabase backup for GLM files |
| Large file downloads impact performance | High | Medium | Streaming downloads, progress tracking |
| Rate limiting affects batch operations | Medium | High | Request queuing, exponential backoff |

### **Medium Risk Items**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| File integrity corruption during transfer | Medium | Low | Multi-layer integrity validation |
| Cache synchronization issues | Medium | Medium | Atomic cache operations |
| Provider API changes | Medium | Low | Provider abstraction layer |

### **Low Risk Items**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Disk space exhaustion | Low | Low | Cleanup policies, monitoring |
| Network timeouts | Low | Medium | Retry logic, timeout configuration |
| File permission issues | Low | Low | Proper permission handling |

---

## 🔄 **INTEGRATION WITH EXISTING SYSTEM**

### **Deduplication Integration**

**Download deduplication:**
```python
def deduplicate_download(file_id: str, destination: str) -> str:
    """Check if file already exists locally with same hash"""
    file_record = supabase.table("provider_file_uploads")\
        .select("sha256_hash")\
        .eq("provider_file_id", file_id)\
        .execute()

    if not file_record.data:
        return download_with_verification(file_id, destination)

    expected_hash = file_record.data[0]["sha256_hash"]

    # Check if file already exists in download directory
    for existing_file in Path(DEFAULT_DOWNLOAD_DIR).glob("*"):
        if calculate_sha256(existing_file) == expected_hash:
            # File already exists with same content
            logger.info(f"[DEDUP] Found existing file: {existing_file}")
            return str(existing_file)

    # No local match, download normally
    return download_with_verification(file_id, destination)
```

### **Smart File Query Integration**

**Unified file operations:**
```python
# Upload + Query (existing)
smart_file_query(file_path="/path/to/file.py", question="Analyze this code")

# Download (new)
smart_file_download(file_id="file_abc123", destination="/path/to/save/")

# Future: Unified manager
smart_file_manager(
    operation="upload",
    file_path="/path/to/file.py",
    question="Analyze this code"
)

smart_file_manager(
    operation="download",
    file_id="file_abc123",
    destination="/path/to/save/"
)
```

---

## 📈 **SUCCESS METRICS**

### **Performance Metrics**

- **Download Speed:** Target <5 seconds for files <10MB
- **Cache Hit Rate:** Target >70% for repeated downloads
- **Integrity Verification:** 100% success rate
- **Error Recovery:** <5% failure rate with retry logic

### **Operational Metrics**

- **Download Count:** Track total downloads per day/week/month
- **Provider Distribution:** Monitor Kimi vs Supabase downloads
- **Storage Usage:** Track Supabase cache size growth
- **Cleanup Efficiency:** Monitor automatic cleanup effectiveness

---

## 🚀 **NEXT STEPS**

### **Immediate Actions**

1. **EXAI Validation:** Get final approval on architecture and implementation plan
2. **Schema Updates:** Apply Supabase schema changes
3. **Tool Skeleton:** Create `smart_file_download` tool structure
4. **Provider Clients:** Implement Kimi download client

### **Follow-up Tasks**

1. Update tool registry with new download tool
2. Update documentation with download examples
3. Create test suite for download functionality
4. Integrate with monitoring dashboard

---

## 📚 **REFERENCES**

### **API Documentation**

- **Moonshot/Kimi API:** https://platform.moonshot.cn/docs
- **OpenAI Files API:** https://platform.openai.com/docs/api-reference/files
- **Supabase Storage:** https://supabase.com/docs/guides/storage
- **Z.ai/GLM API:** https://open.bigmodel.cn/dev/api

### **Best Practices**

- File download caching strategies
- SHA256 integrity verification
- Exponential backoff retry logic
- File deduplication patterns

---

**Status:** ✅ Research Complete - Ready for Implementation
**EXAI Consultation:** Available for 18 more exchanges
**Next:** Get user approval and begin Phase 1 implementation

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Basic Download Functionality (Week 1-2)**

**Tasks:**
- [ ] Create `smart_file_download` tool skeleton
- [ ] Implement Kimi provider download client
- [ ] Implement Supabase storage download client
- [ ] Basic error handling and retry logic
- [ ] Integration with existing file tracking system

**Deliverables:**
- Working download from Kimi provider
- Working download from Supabase storage
- Basic error handling

### **Phase 2: Caching Layer (Week 3-4)**

**Tasks:**
- [ ] Extend Supabase schema (add download tracking columns)
- [ ] Create `file_download_history` table
- [ ] Implement SHA256-based integrity validation
- [ ] Implement cache-first download strategy
- [ ] Add download deduplication logic

**Deliverables:**
- Supabase cache integration
- Integrity validation working
- Download tracking operational

### **Phase 3: Advanced Features (Week 5-6)**

**Tasks:**
- [ ] Implement file path validation
- [ ] Add cleanup strategies (immediate + retention-based)
- [ ] Implement provider fallback logic
- [ ] Add comprehensive error handling for all status codes
- [ ] Create download history analytics

**Deliverables:**
- Complete error handling
- File cleanup working
- Analytics dashboard integration

### **Phase 4: Testing & Documentation (Week 7-8)**

**Tasks:**
- [ ] Comprehensive testing with 10+ file types
- [ ] Test all error scenarios
- [ ] Performance optimization
- [ ] Update tool schemas and documentation
- [ ] EXAI validation of complete implementation

**Deliverables:**
- Test suite passing
- Documentation complete
- EXAI-validated implementation

---


