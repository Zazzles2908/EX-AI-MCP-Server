# Unified File Manager Migration Plan
**Created:** 2025-11-02  
**Status:** Week 1 Critical Task 3  
**Priority:** HIGH  
**Estimated Effort:** 1 hour planning + 2-3 hours execution

---

## Executive Summary

This document outlines the migration strategy for deprecating the legacy `src/storage/unified_file_manager.py` in favor of the new `src/file_management/unified_manager.py` implemented in PHASE 1.

**Key Differences:**
- **Legacy:** 530 lines, basic file upload/download, minimal error handling
- **New:** Comprehensive file lifecycle management, Redis locking, Prometheus metrics, soft deletion, deduplication

**Migration Timeline:** 2-3 weeks (phased rollout with backward compatibility)

---

## Current State Analysis

### Legacy File Manager (`src/storage/unified_file_manager.py`)

**Location:** `src/storage/unified_file_manager.py` (530 lines)

**Capabilities:**
- Basic file upload to Kimi/GLM
- File download from providers
- Simple provider selection logic
- Minimal error handling
- No lifecycle management
- No metrics collection
- No file locking

**Known Issues:**
- No deduplication (uploads same file multiple times)
- No cleanup (files accumulate indefinitely)
- No metrics (no visibility into operations)
- No locking (race conditions possible)
- No soft deletion (hard deletes only)

### New File Manager (`src/file_management/unified_manager.py`)

**Location:** `src/file_management/unified_manager.py`

**Capabilities:**
- SHA256-based deduplication
- Redis-based file locking (prevents race conditions)
- 7 Prometheus metrics (upload attempts, bytes, duration, etc.)
- Soft deletion with audit trail
- Automatic lifecycle management (30-day retention)
- Comprehensive error handling
- Provider fallback chain
- Supabase integration for tracking

**Advantages:**
- 70-80% reduction in duplicate uploads
- Complete audit trail
- Real-time metrics
- Automatic cleanup
- Production-ready error handling

---

## Migration Strategy

### Phase 1: Backward Compatibility Layer (Week 1)

**Goal:** Ensure zero breaking changes for existing code

**Actions:**
1. Create compatibility wrapper in `src/storage/unified_file_manager.py`
2. Wrapper delegates all calls to new `src/file_management/unified_manager.py`
3. Add deprecation warnings to all legacy methods
4. Update imports to use new manager internally

**Example Wrapper:**
```python
# src/storage/unified_file_manager.py (legacy - deprecated)
import warnings
from src.file_management.unified_manager import UnifiedFileManager as NewManager

class UnifiedFileManager:
    """DEPRECATED: Use src.file_management.unified_manager.UnifiedFileManager instead."""
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "src.storage.unified_file_manager is deprecated. "
            "Use src.file_management.unified_manager instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._new_manager = NewManager(*args, **kwargs)
    
    def upload_file(self, *args, **kwargs):
        return self._new_manager.upload_file(*args, **kwargs)
    
    # ... delegate all other methods
```

**Testing:**
- Run all existing tests with wrapper
- Verify no breaking changes
- Monitor deprecation warnings in logs

### Phase 2: Import Migration (Week 2)

**Goal:** Update all imports to use new manager

**Actions:**
1. Find all imports of legacy manager:
   ```bash
   grep -r "from src.storage.unified_file_manager import" .
   grep -r "from src.storage import unified_file_manager" .
   ```

2. Update imports systematically:
   ```python
   # OLD
   from src.storage.unified_file_manager import UnifiedFileManager
   
   # NEW
   from src.file_management.unified_manager import UnifiedFileManager
   ```

3. Update all affected files (see Import Mapping section below)

4. Run comprehensive test suite after each batch of changes

**Testing:**
- Unit tests for each updated module
- Integration tests for file upload/download flows
- End-to-end tests with real API calls

### Phase 3: Legacy Removal (Week 3)

**Goal:** Remove legacy code and cleanup

**Actions:**
1. Verify no remaining imports of legacy manager
2. Delete `src/storage/unified_file_manager.py`
3. Update documentation to reference new manager
4. Remove backward compatibility layer
5. Final validation with full test suite

**Rollback Plan:**
- Keep legacy file in git history
- Can restore from commit if issues found
- Backward compatibility layer can be re-enabled if needed

---

## Import Mapping

### Files Using Legacy Manager

**To be determined via codebase search:**
```bash
# Find all imports
grep -r "from src.storage.unified_file_manager" . --include="*.py"
grep -r "import src.storage.unified_file_manager" . --include="*.py"
```

**Expected locations:**
- `tools/providers/*/file_operations.py` - Provider-specific file tools
- `src/file_management/providers/*_provider.py` - Provider implementations
- `scripts/ws/run_ws_daemon.py` - Main daemon startup
- Various test files in `tests/`

**Update Pattern:**
```python
# Before
from src.storage.unified_file_manager import UnifiedFileManager

# After
from src.file_management.unified_manager import UnifiedFileManager
```

---

## Testing Strategy

### Unit Tests
- Test backward compatibility wrapper
- Test all new manager methods
- Test error handling and edge cases

### Integration Tests
- Test file upload/download flows
- Test deduplication logic
- Test lifecycle management
- Test metrics collection

### End-to-End Tests
- Test with real Kimi/GLM API calls
- Test with large files (near 512MB limit)
- Test concurrent uploads (Redis locking)
- Test cleanup after 30 days

### Performance Tests
- Benchmark upload speed (old vs new)
- Measure deduplication effectiveness
- Monitor metrics overhead
- Test Redis locking performance

---

## Rollback Plan

### If Issues Found in Phase 1
- Remove compatibility wrapper
- Revert to direct use of legacy manager
- Document issues for future retry

### If Issues Found in Phase 2
- Revert import changes
- Re-enable backward compatibility layer
- Fix issues in new manager
- Retry migration

### If Issues Found in Phase 3
- Restore legacy file from git history
- Re-enable backward compatibility layer
- Revert import changes if needed
- Document root cause

---

## Success Criteria

### Phase 1 Complete
- ✅ Backward compatibility wrapper implemented
- ✅ All existing tests pass
- ✅ Deprecation warnings logged
- ✅ No breaking changes

### Phase 2 Complete
- ✅ All imports updated to new manager
- ✅ All tests pass with new imports
- ✅ No deprecation warnings in logs
- ✅ Metrics showing new manager usage

### Phase 3 Complete
- ✅ Legacy file deleted
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Production deployment successful

---

## Timeline

| Phase | Duration | Start Date | End Date | Status |
|-------|----------|------------|----------|--------|
| Phase 1: Backward Compatibility | 2-3 days | TBD | TBD | NOT STARTED |
| Phase 2: Import Migration | 5-7 days | TBD | TBD | NOT STARTED |
| Phase 3: Legacy Removal | 2-3 days | TBD | TBD | NOT STARTED |
| **Total** | **2-3 weeks** | **TBD** | **TBD** | **NOT STARTED** |

---

## Risk Assessment

### High Risk
- **Breaking changes:** Mitigated by backward compatibility layer
- **Data loss:** Mitigated by soft deletion and audit trail
- **Performance degradation:** Mitigated by benchmarking and monitoring

### Medium Risk
- **Import errors:** Mitigated by systematic testing
- **Redis dependency:** Mitigated by fallback to non-locking mode
- **Metrics overhead:** Mitigated by performance testing

### Low Risk
- **Documentation gaps:** Mitigated by comprehensive docs
- **Test coverage:** Mitigated by extensive test suite

---

## Next Steps

1. **Immediate (Week 1):**
   - Implement backward compatibility wrapper
   - Run full test suite
   - Monitor deprecation warnings

2. **Short-term (Week 2):**
   - Find all legacy imports
   - Update imports systematically
   - Run tests after each batch

3. **Medium-term (Week 3):**
   - Delete legacy file
   - Update documentation
   - Final validation

---

## References

- **New Manager:** `src/file_management/unified_manager.py`
- **Legacy Manager:** `src/storage/unified_file_manager.py`
- **PHASE 1 Implementation:** `docs/05_CURRENT_WORK/2025-11-02/PHASE2_HIGH_IMPLEMENTATION_PROGRESS.md`
- **Master Plan:** `docs/05_CURRENT_WORK/2025-11-02/NEW_MASTER_IMPLEMENTATION_PLAN.md`

