# Supabase Upload Optimization - Usage Examples

**Date:** 2025-10-22  
**Phase:** C Step 4  
**EXAI Validation:** Continuation 9222d725-b6cd-44f1-8406-274e5a3b3389

---

## Overview

This document provides usage examples for the optimized `SupabaseStorageManager.upload_file()` method, demonstrating both backward-compatible usage and new features like streaming and progress tracking.

---

## Basic Usage (Backward Compatible)

### Example 1: Simple File Upload

```python
from src.storage.supabase_client import SupabaseStorageManager

# Initialize manager
storage = SupabaseStorageManager()

# Read file
with open("document.pdf", "rb") as f:
    file_data = f.read()

# Upload (backward compatible - same as before)
file_id = storage.upload_file(
    file_path="documents/report.pdf",
    file_data=file_data,
    original_name="report.pdf",
    mime_type="application/pdf",
    file_type="user_upload"
)

if file_id:
    print(f"Upload successful! File ID: {file_id}")
else:
    print("Upload failed")
```

---

## Progress Tracking

### Example 2: Upload with Progress Callback

```python
from src.storage.supabase_client import SupabaseStorageManager

def progress_callback(bytes_transferred, total_bytes, percentage):
    """Progress callback for upload tracking."""
    print(f"Upload progress: {percentage:.1f}% ({bytes_transferred}/{total_bytes} bytes)")

storage = SupabaseStorageManager()

with open("large_file.zip", "rb") as f:
    file_data = f.read()

file_id = storage.upload_file(
    file_path="archives/backup.zip",
    file_data=file_data,
    original_name="backup.zip",
    mime_type="application/zip",
    file_type="user_upload",
    progress_callback=progress_callback  # New feature!
)
```

**Output:**
```
Upload progress: 0.0% (0/10485760 bytes)
Upload progress: 100.0% (10485760/10485760 bytes)
```

---

## Streaming Upload

### Example 3: Memory-Efficient Streaming Upload

```python
from src.storage.supabase_client import SupabaseStorageManager
import io

storage = SupabaseStorageManager()

# Open file as stream (doesn't load entire file into memory)
with open("very_large_file.mp4", "rb") as file_obj:
    file_id = storage.upload_file(
        file_path="videos/presentation.mp4",
        file_obj=file_obj,  # Use file_obj instead of file_data
        original_name="presentation.mp4",
        mime_type="video/mp4",
        file_type="user_upload"
    )
```

**Benefits:**
- Memory-efficient for large files
- Doesn't load entire file into RAM
- Better for constrained environments

---

## Custom Timeout

### Example 4: Upload with Custom Timeout

```python
from src.storage.supabase_client import SupabaseStorageManager

storage = SupabaseStorageManager()

with open("large_dataset.csv", "rb") as f:
    file_data = f.read()

file_id = storage.upload_file(
    file_path="data/dataset.csv",
    file_data=file_data,
    original_name="dataset.csv",
    mime_type="text/csv",
    file_type="generated",
    timeout=600  # 10 minutes (default is 300 seconds)
)
```

---

## Error Handling

### Example 5: Robust Error Handling

```python
from src.storage.supabase_client import (
    SupabaseStorageManager,
    RetryableError,
    NonRetryableError
)
import logging

logger = logging.getLogger(__name__)
storage = SupabaseStorageManager()

def upload_with_error_handling(file_path, file_data, original_name):
    """Upload file with comprehensive error handling."""
    try:
        file_id = storage.upload_file(
            file_path=file_path,
            file_data=file_data,
            original_name=original_name,
            file_type="user_upload"
        )
        
        if file_id:
            logger.info(f"Upload successful: {file_id}")
            return file_id
        else:
            logger.error("Upload failed: No file_id returned")
            return None
            
    except NonRetryableError as e:
        # Non-retryable errors (auth, quota, etc.)
        logger.error(f"Upload failed (non-retryable): {e}")
        # Handle auth/quota issues
        return None
        
    except RetryableError as e:
        # Max retries exceeded
        logger.error(f"Upload failed (max retries): {e}")
        # Maybe queue for later retry
        return None
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Upload failed (unexpected): {e}")
        return None

# Usage
with open("document.pdf", "rb") as f:
    file_id = upload_with_error_handling(
        "documents/report.pdf",
        f.read(),
        "report.pdf"
    )
```

---

## HybridSupabaseManager Usage

### Example 6: Using HybridSupabaseManager

```python
from src.storage.hybrid_supabase_manager import HybridSupabaseManager

# Initialize hybrid manager
manager = HybridSupabaseManager()

# Upload file (automatically uses optimized SupabaseStorageManager)
result = manager.upload_file(
    bucket="user-files",
    path="documents/report.pdf",
    file_data=file_data,
    content_type="application/pdf",
    progress_callback=lambda t, total, pct: print(f"Progress: {pct:.1f}%")
)

if result.success:
    print(f"Upload successful! File ID: {result.data['file_id']}")
    print(f"Metadata: {result.metadata}")
else:
    print(f"Upload failed: {result.error}")
```

**Note:** `HybridSupabaseManager.upload_file()` now delegates to the optimized `SupabaseStorageManager`, so you get all the benefits (retry logic, progress tracking, etc.) automatically!

---

## Configuration

### Environment Variables

Configure upload behavior in `.env.docker`:

```env
# Maximum retry attempts for failed uploads
SUPABASE_MAX_RETRIES=3

# Upload timeout in seconds (5 minutes)
SUPABASE_UPLOAD_TIMEOUT=300

# Chunk size for streaming uploads (8KB)
SUPABASE_CHUNK_SIZE=8192

# Progress callback throttle interval (seconds)
SUPABASE_PROGRESS_INTERVAL=0.5
```

### Adjusting Configuration

```python
import os

# Increase timeout for very large files
os.environ["SUPABASE_UPLOAD_TIMEOUT"] = "900"  # 15 minutes

# Increase retries for unreliable networks
os.environ["SUPABASE_MAX_RETRIES"] = "5"

# Reduce progress update frequency
os.environ["SUPABASE_PROGRESS_INTERVAL"] = "1.0"  # 1 second
```

---

## Advanced Usage

### Example 7: Upload with All Features

```python
from src.storage.supabase_client import SupabaseStorageManager
import logging

logger = logging.getLogger(__name__)
storage = SupabaseStorageManager()

def advanced_upload(file_path, original_name, mime_type):
    """Upload with all optimization features."""
    
    # Progress tracking
    def progress_callback(transferred, total, percentage):
        logger.info(f"Upload: {percentage:.1f}% ({transferred}/{total} bytes)")
    
    # Open file as stream
    with open(file_path, "rb") as file_obj:
        try:
            file_id = storage.upload_file(
                file_path=f"uploads/{original_name}",
                file_obj=file_obj,              # Streaming
                original_name=original_name,
                mime_type=mime_type,
                file_type="user_upload",
                progress_callback=progress_callback,  # Progress tracking
                timeout=600                     # Custom timeout
            )
            
            if file_id:
                logger.info(f"✅ Upload successful: {file_id}")
                return file_id
            else:
                logger.error("❌ Upload failed: No file_id returned")
                return None
                
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return None

# Usage
file_id = advanced_upload(
    "/path/to/large_file.mp4",
    "presentation.mp4",
    "video/mp4"
)
```

---

## Migration Guide

### Migrating from Old Upload Code

**Before (Old Code):**
```python
# Old upload without retry or progress
client = get_supabase_client()
result = client.storage.from_("user-files").upload(
    path="file.pdf",
    file=file_data
)
```

**After (Optimized):**
```python
# New upload with retry and progress
storage = SupabaseStorageManager()
file_id = storage.upload_file(
    file_path="file.pdf",
    file_data=file_data,
    original_name="file.pdf",
    progress_callback=lambda t, total, pct: print(f"{pct:.1f}%")
)
```

**Benefits:**
- ✅ Automatic retry on network failures
- ✅ Progress tracking
- ✅ Better error handling
- ✅ Deduplication (checks for existing files)
- ✅ Metadata tracking in database

---

## Testing

### Example 8: Unit Test with Mock

```python
import pytest
from unittest.mock import Mock, patch
from src.storage.supabase_client import SupabaseStorageManager

def test_upload_with_progress():
    """Test upload with progress callback."""
    progress_updates = []
    
    def progress_callback(transferred, total, percentage):
        progress_updates.append((transferred, total, percentage))
    
    with patch('src.storage.supabase_client.create_client'):
        storage = SupabaseStorageManager()
        storage._enabled = True
        
        # Mock client
        mock_client = Mock()
        storage.get_client = Mock(return_value=mock_client)
        
        # Mock responses
        mock_client.storage.from_.return_value.upload.return_value = {"path": "test.txt"}
        mock_client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
        
        # Upload
        file_id = storage.upload_file(
            file_path="test.txt",
            file_data=b"test content",
            original_name="test.txt",
            progress_callback=progress_callback
        )
        
        assert file_id == "test-id"
        assert len(progress_updates) >= 1  # At least one progress update
```

---

## Troubleshooting

### Common Issues

**Issue 1: Upload Timeout**
```python
# Solution: Increase timeout
file_id = storage.upload_file(
    ...,
    timeout=900  # 15 minutes
)
```

**Issue 2: Progress Callback Not Called**
```python
# Check that callback is provided and file size > 0
def debug_callback(t, total, pct):
    print(f"DEBUG: {t}/{total} = {pct}%")

file_id = storage.upload_file(
    ...,
    progress_callback=debug_callback
)
```

**Issue 3: NonRetryableError (Auth)**
```python
# Check environment variables
import os
print(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))  # Should be set
print(os.getenv("SUPABASE_URL"))  # Should be set
```

---

## References

- **Architecture:** `docs/HYBRID_SUPABASE_ARCHITECTURE.md`
- **Implementation:** `src/storage/supabase_client.py`
- **Tests:** `tests/test_supabase_upload_optimization.py`
- **Migration:** `supabase/migrations/001_phase_c_setup.sql`
- **EXAI Validation:** Continuation ID `9222d725-b6cd-44f1-8406-274e5a3b3389`

