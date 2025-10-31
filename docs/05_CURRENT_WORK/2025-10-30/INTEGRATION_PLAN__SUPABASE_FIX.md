# Supabase Integration Fix - Implementation Plan (UPDATED)

**Date:** 2025-10-30
**Status:** 🔴 CRITICAL - Integration Required
**EXAI Consultation ID:** bbfac185-ce22-4140-9b30-b3fda4c362d9
**EXAI Recommendation:** Option B with Provider Adapters - Enhanced Generic Utilities

---

## 🎯 EXECUTIVE SUMMARY

**Problem:** Built Supabase utilities in isolation, didn't integrate with existing tools
**Impact:** Tests passed (19/19) but real integration fails (kimi_chat_with_files times out)
**Solution:** Enhanced generic utilities with provider adapters, remove ~1600 lines of redundant code
**Timeline:** 8 hours total (includes BOTH Kimi AND GLM integration)

## 🔄 UPDATED AFTER COMPREHENSIVE EXAI CONSULTATION

**Key Changes from Original Plan:**
1. ✅ Considered GLM integration (not just Kimi)
2. ✅ DELETE gateway functions (not keep them)
3. ✅ Enhanced generic utilities with provider adapters
4. ✅ Unified architecture for both providers
5. ✅ Session management for GLM's session-bound files

---

## 📊 FINAL INTEGRATION ARCHITECTURE

### Option B with Provider Adapters ✅ EXAI RECOMMENDED

**Why:**
- Eliminates redundancy (delete gateway functions)
- Centralizes logic in one place
- Maintains flexibility with provider adapters
- Simpler testing (one layer instead of two)
- Handles BOTH Kimi AND GLM with same utilities

**Final Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                    Tool Layer                            │
├─────────────────────────────────────────────────────────┤
│ kimi_upload_files │ kimi_chat_with_files │ glm_upload_file│
│ glm_multi_file_chat │ smart_file_query                │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           Enhanced Generic Utilities Layer               │
├─────────────────────────────────────────────────────────┤
│  tools/supabase_upload.py (with provider adapters)      │
│  tools/supabase_download.py (with provider adapters)    │
│  FileIdMapper (integrated)                              │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Provider SDK Layer                    │
├─────────────────────────────────────────────────────────┤
│                    Kimi SDK                              │
│                    GLM SDK                               │
└─────────────────────────────────────────────────────────┘
```

**Key Differences from Original Plan:**
- ❌ DELETE `upload_via_supabase_gateway_kimi()` and `upload_via_supabase_gateway_glm()`
- ✅ ADD provider adapters to generic utilities
- ✅ INTEGRATE FileIdMapper into utilities layer
- ✅ HANDLE GLM session management

---

## 🚀 COMPREHENSIVE IMPLEMENTATION PLAN

### Phase 1: Enhance Generic Utilities with Provider Adapters (3 hours)

**File:** `tools/supabase_upload.py`
**Status:** 🔴 CRITICAL

**Changes:**
1. Add provider adapter functions (`_kimi_upload_adapter`, `_glm_upload_adapter`)
2. Integrate FileIdMapper into upload utility
3. Handle provider-specific differences (file size limits, persistence)
4. Add session management for GLM

**New Functions:**
```python
def _kimi_upload_adapter(file_path: str, user_id: str, ...) -> Dict[str, Any]:
    """Kimi-specific upload handling (persistent files, 100MB limit)"""

def _glm_upload_adapter(file_path: str, user_id: str, ...) -> Dict[str, Any]:
    """GLM-specific upload handling (session-bound files, 20MB limit)"""

def upload_file(file_path: str, provider: str = "auto", ...) -> Dict[str, Any]:
    """Universal upload with provider detection and routing"""
```

**File:** `tools/supabase_download.py`
**Status:** 🔴 CRITICAL

**Changes:**
1. Add provider adapter functions for download
2. Handle GLM's no-download limitation
3. Integrate with cache manager

---

### Phase 2: Update Kimi Tools (2 hours)

#### Priority 2A: Fix kimi_chat_with_files Timeout (1 hour)

**File:** `tools/providers/kimi/kimi_files.py`  
**Lines:** 578-650  
**Status:** 🔴 CRITICAL

**Changes:**
```python
# Add import at top
from tools.supabase_download import SupabaseDownloadManager, CacheManager

async def _run_async(self, **kwargs) -> Dict[str, Any]:
    file_ids = kwargs.get("file_ids") or []
    
    # Initialize download manager
    download_manager = SupabaseDownloadManager(...)
    
    for file_id in file_ids:
        try:
            # First try Supabase download
            local_path = await download_manager.download_file(file_id)
            with open(local_path, 'r') as f:
                content = f.read()
            
            # Use Supabase content directly
            file_messages.append({
                "role": "system",
                "content": f"File content:\\n{content}"
            })
            
        except Exception as e:
            # Fallback to Kimi API only if Supabase fails
            logger.warning(f"Supabase download failed for {file_id}, trying Kimi API")
            response = await content_method(file_id=file_id)
```

**Testing:**
```bash
python -c "from tools.providers.kimi.kimi_files import KimiChatWithFilesTool; tool = KimiChatWithFilesTool(); tool.execute(file_ids=['test_id'], prompt='test')"
```

---

### Priority 2: Update kimi_upload_files (2 hours)

**File:** `tools/providers/kimi/kimi_files.py`  
**Lines:** 261-320  
**Status:** 🔴 HIGH

**Changes:**
```python
def _run(self, **kwargs) -> List[Dict[str, Any]]:
    files = kwargs.get("files") or []
    purpose = kwargs.get("purpose") or "file-extract"
    
    # ... existing validation ...
    
    # Use Supabase utilities instead of direct upload
    from tools.supabase_upload import SupabaseUploadManager
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    client = create_client(url, service_key)
    
    upload_manager = SupabaseUploadManager(client)
    
    # Get dev user ID
    result = client.rpc('get_dev_user_id').execute()
    user_id = result.data
    
    results = []
    for file_path in files:
        try:
            # Upload to Supabase
            upload_result = upload_manager.upload_file(
                file_path=file_path,
                user_id=user_id,
                filename=Path(file_path).name,
                bucket="user-files",
                tags=["kimi", purpose]
            )
            
            results.append({
                "filename": Path(file_path).name,
                "file_id": upload_result['file_id'],
                "size_bytes": upload_result['file_size'],
                "upload_timestamp": upload_result['created_at']
            })
            
        except Exception as e:
            logger.error(f"Upload failed for {file_path}: {e}")
            raise
            
    return results
```

---

### Priority 3: Update smart_file_query (2 hours)

**File:** `tools/smart_file_query.py`  
**Lines:** 79-96  
**Status:** 🔴 HIGH

**Changes:**
```python
def __init__(self):
    super().__init__()
    
    # Replace old managers with new utilities
    from tools.supabase_upload import SupabaseUploadManager
    from tools.supabase_download import SupabaseDownloadManager, CacheManager
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    self.supabase_client = create_client(url, service_key)
    
    self.upload_manager = SupabaseUploadManager(self.supabase_client)
    
    cache_manager = CacheManager(
        cache_dir=os.path.join(os.path.dirname(__file__), '../cache'),
        max_size=100 * 1024 * 1024,  # 100MB
        ttl=3600  # 1 hour
    )
    self.download_manager = SupabaseDownloadManager(
        supabase_client=self.supabase_client,
        cache_manager=cache_manager,
        default_bucket="user-files"
    )
    
    # Remove old tool initialization
    # self.kimi_upload = None
    # self.kimi_chat = None
```

---

### Priority 4: Create File ID Mapper (1 hour)

**File:** `tools/file_id_mapper.py` (NEW)  
**Status:** 🟡 MEDIUM

**Implementation:**
```python
"""
File ID Mapper - Maps between Supabase file_ids and provider file_ids
"""

import logging
from typing import Optional
from supabase import Client

logger = logging.getLogger(__name__)


class FileIdMapper:
    """Maps between Supabase file_ids and provider file_ids"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    def store_mapping(self, supabase_id: str, provider_id: str, provider: str) -> bool:
        """Store mapping in database"""
        try:
            self.client.table('file_id_mappings').insert({
                'supabase_file_id': supabase_id,
                'provider_file_id': provider_id,
                'provider': provider
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to store mapping: {e}")
            return False
    
    def get_provider_id(self, supabase_id: str, provider: str) -> Optional[str]:
        """Get provider file_id from Supabase ID"""
        try:
            result = self.client.table('file_id_mappings').select('provider_file_id').eq(
                'supabase_file_id', supabase_id
            ).eq('provider', provider).execute()
            
            if result.data:
                return result.data[0]['provider_file_id']
            return None
        except Exception as e:
            logger.error(f"Failed to get provider ID: {e}")
            return None
    
    def get_supabase_id(self, provider_id: str, provider: str) -> Optional[str]:
        """Get Supabase ID from provider file_id"""
        try:
            result = self.client.table('file_id_mappings').select('supabase_file_id').eq(
                'provider_file_id', provider_id
            ).eq('provider', provider).execute()
            
            if result.data:
                return result.data[0]['supabase_file_id']
            return None
        except Exception as e:
            logger.error(f"Failed to get Supabase ID: {e}")
            return None
```

**Database Schema:**
```sql
CREATE TABLE file_id_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supabase_file_id TEXT NOT NULL,
    provider_file_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(supabase_file_id, provider),
    UNIQUE(provider_file_id, provider)
);

CREATE INDEX idx_file_id_mappings_supabase ON file_id_mappings(supabase_file_id);
CREATE INDEX idx_file_id_mappings_provider ON file_id_mappings(provider_file_id, provider);
```

---

### Priority 5: Remove Redundant Code (1 hour)

**Files to Modify/Delete:**

1. **`src/providers/kimi_files.py`**
   - Remove old `upload_file()` method
   - Keep only minimal provider-specific logic

2. **`src/providers/glm_files.py`**
   - Remove old `upload_file()` method
   - Keep only minimal provider-specific logic

3. **`tools/smart_file_download.py`**
   - Mark as deprecated
   - Add deprecation warning pointing to `supabase_download.py`

4. **`tools/providers/kimi/kimi_files.py`**
   - Remove `upload_via_supabase_gateway_kimi()` (duplicate logic)
   - Keep only tool interface

5. **`tools/providers/glm/glm_files.py`**
   - Remove `upload_via_supabase_gateway_glm()` (duplicate logic)
   - Keep only tool interface

**Estimated Code Removal:** ~1600 lines

---

### Priority 6: Integration Testing (2 hours)

**File:** `tests/integration/test_supabase_full_workflow.py` (NEW)

**Tests:**
```python
async def test_kimi_upload_to_chat_workflow():
    """Test: kimi_upload_files → kimi_chat_with_files"""
    
async def test_smart_query_with_supabase():
    """Test: smart_file_query using Supabase utilities"""
    
async def test_timeout_handling():
    """Test: Proper timeout handling with Supabase"""
    
async def test_fallback_mechanisms():
    """Test: Fallback when Supabase unavailable"""
    
async def test_file_id_mapping():
    """Test: File ID mapping between Supabase and providers"""
```

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] Priority 1: Fix kimi_chat_with_files timeout (30 min)
- [ ] Priority 2: Update kimi_upload_files (2 hours)
- [ ] Priority 3: Update smart_file_query (2 hours)
- [ ] Priority 4: Create File ID Mapper (1 hour)
- [ ] Priority 5: Remove redundant code (1 hour)
- [ ] Priority 6: Integration testing (2 hours)
- [ ] Update documentation
- [ ] EXAI validation of changes

**Total Time:** 6 hours

---

## 🎯 SUCCESS CRITERIA

1. ✅ kimi_chat_with_files no longer times out
2. ✅ All file operations use Supabase utilities
3. ✅ ~1600 lines of redundant code removed
4. ✅ Integration tests passing
5. ✅ EXAI validation complete
6. ✅ Documentation updated

---

**Status:** 🔴 READY TO IMPLEMENT  
**Next Step:** Begin Priority 1 - Fix kimi_chat_with_files timeout

