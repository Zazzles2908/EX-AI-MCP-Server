# P1 Priority Fixes Implementation Plan

**Date:** 2025-10-17  
**Status:** Ready for Implementation  
**EXAI Continuation ID:** 09a350a8-c97f-43f5-9def-2a686778b359

---

## Overview

This document outlines the complete implementation plan for all 3 P1 priority fixes identified by EXAI analysis. All code has been provided by EXAI (GLM-4.6 with web search) and is ready for implementation.

---

## Priority 1: Semaphore Leak Prevention

### Status: ✅ SemaphoreGuard Class Added (Line 113)

**What's Done:**
- Added `SemaphoreGuard` context manager class to `src/daemon/ws_server.py`
- Provides guaranteed semaphore cleanup even on exceptions
- Tracks acquisition state to prevent double-release
- Includes debug logging for semaphore operations

**What's Remaining:**
- Refactor semaphore acquisition code (lines 557-600)
- Create `_execute_tool_with_semaphores()` helper function
- Delete old finally block (lines 948-966)
- Replace manual acquire/release with context managers

**Impact:**
- Eliminates all semaphore leak risks
- Prevents deadlocks under high load
- Improves system stability

---

## Priority 2: Race Condition in Cache Operations

### Status: ⏳ Ready to Implement

**Changes Required:**

1. **Add AtomicCache class** (after SemaphoreGuard, line 165)
   - Thread-safe cache operations using `asyncio.Lock`
   - Atomic get/set/pop/contains operations
   - TTL-based cleanup support

2. **Replace global cache variables** (around line 200)
   ```python
   # OLD:
   _inflight_by_key: dict[str, asyncio.Event] = {}
   _inflight_meta_by_key: dict[str, dict] = {}
   
   # NEW:
   _inflight_cache = AtomicCache()
   _inflight_meta_cache = AtomicCache()
   ```

3. **Add atomic helper functions:**
   - `_check_and_set_inflight()` - Atomic duplicate detection
   - `_cleanup_inflight()` - Atomic cache cleanup
   - `_store_result_by_key()` - Atomic result storage
   - `_get_cached_by_key()` - Atomic result retrieval

4. **Update all cache access points** (lines 530-540, 830-840, 300-320)

**Impact:**
- Eliminates race conditions in duplicate detection
- Prevents cache corruption under concurrent access
- Improves reliability of request coalescing

---

## Priority 3: Additional Improvements

### Status: ⏳ Ready to Implement

**3.1 Timeout Hierarchy Validation** (Add at startup in main_async, line 670)
- Validates daemon timeout > tool timeout
- Warns if ratio is too low (<1.3x)
- Prevents timeout configuration errors

**3.2 Semaphore Health Monitoring** (Add after line 950)
- Periodic health checks every 30 seconds
- Detects semaphore leaks automatically
- Logs warnings for any discrepancies

**3.3 Connection Pool Optimization** (Add at line 950)
- Tracks connection metadata
- Cleans up stale connections (>5 minutes inactive)
- Provides health monitoring

**Impact:**
- Catches configuration errors early
- Proactive leak detection
- Better connection management

---

## Implementation Order

### Phase 1: Add New Classes and Functions (Low Risk)
1. ✅ Add `SemaphoreGuard` class (DONE)
2. Add `AtomicCache` class
3. Add atomic helper functions
4. Add timeout validation
5. Add semaphore health monitoring
6. Add connection pool

### Phase 2: Refactor Existing Code (High Risk - Requires Testing)
1. Replace global cache variables
2. Update all cache access points
3. Refactor semaphore acquisition code
4. Create `_execute_tool_with_semaphores()` function
5. Delete old finally block

### Phase 3: Testing and Validation
1. Rebuild Docker container
2. Check Docker logs for errors
3. Test with actual EXAI tool calls
4. Verify no semaphore leaks
5. Verify no race conditions
6. Update architecture documentation

---

## Risk Assessment

**Low Risk:**
- Adding new classes (SemaphoreGuard, AtomicCache)
- Adding helper functions
- Adding monitoring code

**Medium Risk:**
- Replacing global cache variables
- Updating cache access points

**High Risk:**
- Refactoring semaphore acquisition (core concurrency control)
- Deleting finally block (cleanup logic)

**Mitigation:**
- Implement in phases
- Test after each phase
- Keep Docker logs open for monitoring
- Have rollback plan ready

---

## Files to Modify

1. `src/daemon/ws_server.py` - Main implementation file
2. `.env` - Verify timeout configuration
3. `.env.docker` - Verify timeout configuration
4. `docs/02_ARCHITECTURE/SYSTEM_ARCHITECTURE_ANALYSIS.md` - Update with results

---

## Success Criteria

✅ **All fixes implemented without errors**
✅ **Docker container builds successfully**
✅ **No errors in Docker logs**
✅ **EXAI tools work correctly**
✅ **No semaphore leaks detected**
✅ **No race condition warnings**
✅ **Timeout hierarchy validated on startup**

---

## Next Steps

**USER APPROVAL REQUIRED:**

The implementation is complex and touches core concurrency control code. Before proceeding:

1. Review this implementation plan
2. Confirm you want to proceed with all 3 priorities
3. Approve the phased implementation approach

**Once approved, I will:**
1. Implement Phase 1 (add new classes/functions)
2. Rebuild and test
3. Implement Phase 2 (refactor existing code)
4. Rebuild and test
5. Update documentation
6. Provide final summary

---

**Ready to proceed?**

