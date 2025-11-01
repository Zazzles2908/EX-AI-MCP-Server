# File Upload System - Bottleneck Analysis & Refactoring Plan

## Executive Summary

The file upload system has critical performance bottlenecks that block the async event loop and prevent concurrent operations. This document outlines the specific issues and provides a refactoring strategy.

## Critical Bottlenecks Identified

### 1. Synchronous File Operations in Async Context

**Location**: `tools/providers/kimi/kimi_files.py:91-92`, `tools/providers/glm/glm_files.py:81-82`

```python
# BLOCKING - Entire file loaded into memory
with open(pth, 'rb') as f:
    file_data = f.read()  # Blocks event loop!
```

**Impact**: 
- Blocks entire async event loop
- Memory spike for large files
- No concurrent operations possible during read

**Fix**: Use `aiofiles` for async file operations

### 2. No Streaming Upload Support

**Issue**: Files are fully loaded before upload, causing:
- Memory exhaustion on large files (>50MB)
- Timeout on slow connections
- No backpressure handling

**Fix**: Implement chunked streaming uploads

### 3. Blocking Supabase Calls

**Location**: `tools/providers/kimi/kimi_files.py:96-102`

```python
# BLOCKING - Synchronous Supabase call
supabase_file_id = storage.upload_file(...)  # Blocks!
```

**Impact**: Database operations block event loop

**Fix**: Use async Supabase client or thread pool executor

### 4. Sequential Processing

**Issue**: File operations processed one-at-a-time instead of parallel

**Fix**: Use `asyncio.gather()` for concurrent uploads

### 5. No Connection Pooling

**Issue**: New HTTP connections created for each upload

**Fix**: Implement async HTTP session pooling

## Refactoring Strategy

### Phase 1: Async File Operations (Priority: CRITICAL)

Replace synchronous file reads with `aiofiles`:

```python
import aiofiles

async def read_file_async(file_path: str) -> bytes:
    async with aiofiles.open(file_path, 'rb') as f:
        return await f.read()
```

### Phase 2: Streaming Uploads (Priority: HIGH)

Implement chunked uploads:

```python
async def upload_file_streaming(file_path: str, chunk_size: int = 8192):
    async with aiofiles.open(file_path, 'rb') as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            yield chunk
```

### Phase 3: Async HTTP Client (Priority: HIGH)

Use `aiohttp` for connection pooling:

```python
import aiohttp

async def upload_with_session(file_path: str, url: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=await read_file_async(file_path)) as resp:
            return await resp.json()
```

### Phase 4: Concurrent Operations (Priority: MEDIUM)

Use `asyncio.gather()` for parallel uploads:

```python
async def upload_multiple_files(file_paths: list[str]):
    tasks = [upload_file_async(path) for path in file_paths]
    return await asyncio.gather(*tasks)
```

### Phase 5: Semaphore-Based Throttling (Priority: MEDIUM)

Prevent resource exhaustion:

```python
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent uploads

async def throttled_upload(file_path: str):
    async with semaphore:
        return await upload_file_async(file_path)
```

## Implementation Priority

1. **CRITICAL** (Week 1): Async file operations + streaming
2. **HIGH** (Week 1): Async HTTP client + connection pooling
3. **MEDIUM** (Week 2): Concurrent operations + throttling
4. **LOW** (Week 2): Monitoring + metrics

## Expected Performance Improvements

- **Memory**: 80-90% reduction for large files (streaming)
- **Throughput**: 5-10x improvement (concurrent operations)
- **Latency**: 30-50% reduction (connection pooling)
- **Timeout Rate**: 95% reduction (proper async handling)

## Files to Refactor

1. `tools/file_upload_optimizer.py` - Add async methods
2. `tools/smart_file_query.py` - Use async operations
3. `tools/providers/kimi/kimi_files.py` - Async file + Supabase
4. `tools/providers/glm/glm_files.py` - Async file + Supabase
5. `tools/providers/kimi/kimi_chat.py` - Async query operations
6. `tools/providers/glm/glm_chat.py` - Async query operations

## Dependencies to Add

```
aiofiles>=23.2.0
aiohttp>=3.9.0
```

## Testing Strategy

1. Unit tests for async functions
2. Concurrent upload tests (10+ simultaneous)
3. Large file tests (50MB+)
4. Memory profiling before/after
5. Timeout reduction verification

## Success Criteria

- [ ] All file operations are async
- [ ] Streaming uploads working for files >10MB
- [ ] 5+ concurrent uploads without blocking
- [ ] Memory usage <100MB for 50MB file upload
- [ ] Timeout rate <1%
- [ ] All tests passing

