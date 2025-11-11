# Hybrid Router - Completion Action Plan

> **Goal:** Complete the migration to achieve promised 76% code reduction
> **Current State:** Partially complete (new system added, old not removed)
> **Required Actions:** 7 steps to true completion

---

## Step-by-Step Completion Plan

### Step 1: Remove Legacy Files
**Files to delete:**
```bash
# Remove the two legacy routing files
rm src/providers/capability_router.py
rm src/providers/registry_selection.py

# Verify deletion
git status
# Should show: deleted: src/providers/capability_router.py
#             deleted: src/providers/registry_selection.py
```

**Why:** These 986 lines must be removed to achieve code reduction.

---

### Step 2: Remove Imports from registry_core.py
**File:** `src/providers/registry_core.py`

**Lines to remove (around lines 576, 585, 592, 603, 616):**
```python
# REMOVE THESE LINES:
from src.providers.registry_selection import get_preferred_fallback_model
from src.providers.registry_selection import get_best_provider_for_category
from src.providers.registry_selection import _get_allowed_models_for_provider
from src.providers.registry_selection import _auggie_fallback_chain
from src.providers.registry_selection import call_with_fallback as _call_with_fallback
```

**Why:** These imports reference deleted files. Must be removed.

---

### Step 3: Remove _Registry Wrapper
**File:** `tools/simple/base.py`

**Lines to remove (around lines 32-39):**
```python
# REMOVE THIS ENTIRE CLASS:
class _Registry:
    @staticmethod
    def call_with_fallback(category, call_fn, hints=None):
        """Execute call_fn with fallback logic."""
        registry_instance = get_registry_instance()
        from src.providers.registry_selection import call_with_fallback as _call_with_fallback
        return _call_with_fallback(registry_instance, category, call_fn, hints)
```

**Why:** This wrapper calls the deleted module. Not needed with hybrid router.

---

### Step 4: Remove Registry Selection Import
**File:** `tools/simple/base.py`

**Line to remove (around line 38):**
```python
# REMOVE THIS LINE:
from src.providers.registry_selection import call_with_fallback as _call_with_fallback
```

**Why:** No longer needed with hybrid router.

---

### Step 5: Fix Config Import Error
**Issue:** `ImportError: cannot import name 'CONTEXT_ENGINEERING' from 'config'`

**Root Cause:** Missing in `src/config/__init__.py`

**Fix Options:**

**Option A:** Add to `src/config/__init__.py`:
```python
# Add this line
CONTEXT_ENGINEERING = os.getenv("CONTEXT_ENGINEERING", "false").lower() == "true"
```

**Option B:** Remove import from `utils/conversation/memory.py`
- Find the import: `from config import CONTEXT_ENGINEERING`
- Either add the constant or remove the dependency

**Why:** Blocking test execution. Must be resolved to validate changes.

---

### Step 6: Run Tests & Verify
```bash
# Run the hybrid router test
python test_hybrid_simple.py

# Expected: All tests pass
# [TEST 1] Routing Cache System - [OK]
# [TEST 2] RouterService - [OK]
# [TEST 3] SimpleTool Integration - [OK]
# [TEST 4] File Structure - [OK]

# If errors, fix before proceeding
```

**Why:** Validate that removal didn't break functionality.

---

### Step 7: Count Lines & Verify Reduction
```bash
# Count current total lines in routing system
echo "=== LEGACY SYSTEM (should be 0) ==="
wc -l src/providers/capability_router.py 2>/dev/null || echo "0 (DELETED)"
wc -l src/providers/registry_selection.py 2>/dev/null || echo "0 (DELETED)"

echo -e "\n=== NEW SYSTEM ==="
wc -l src/router/service.py
wc -l src/router/minimax_m2_router.py
wc -l src/router/hybrid_router.py
wc -l tools/simple/base.py | grep -v "total"

echo -e "\n=== TOTALS ==="
OLD_LINES=0  # After deletion
NEW_LINES=$(($(wc -l < src/router/service.py) + $(wc -l < src/router/minimax_m2_router.py) + $(wc -l < src/router/hybrid_router.py)))
SIMPLETOOL_ADDED=107  # Lines added to base.py
TOTAL=$((NEW_LINES + SIMPLETOOL_ADDED))

echo "Old system: $OLD_LINES lines"
echo "New system: $TOTAL lines"
echo "Reduction: $(echo "scale=1; (($OLD_LINES - $TOTAL) / $OLD_LINES) * 100" | bc)%"
```

**Expected Result:**
- Old system: 0 lines
- New system: ~600 lines
- Reduction: 76%

---

## Verification Checklist

After completing all 7 steps:

- [ ] `capability_router.py` deleted
- [ ] `registry_selection.py` deleted
- [ ] All imports removed from `registry_core.py`
- [ ] `_Registry` class removed from `base.py`
- [ ] Import removed from `base.py`
- [ ] Config import error fixed
- [ ] Tests pass: `python test_hybrid_simple.py`
- [ ] Line count shows 76% reduction
- [ ] No runtime errors
- [ ] All 29 tools still work

---

## Rollback Plan (If Needed)

If something breaks:

```bash
# Restore files from git
git checkout HEAD -- src/providers/capability_router.py
git checkout HEAD -- src/providers/registry_selection.py

# Restore imports
git checkout HEAD -- src/providers/registry_core.py
git checkout HEAD -- tools/simple/base.py

# Restore config
git checkout HEAD -- src/config/__init__.py
```

**Note:** This returns to pre-completion state (both systems running).

---

## Success Metrics

**After completion, we should see:**

| Metric | Current | Target | Status |
|--------|---------|--------|---------|
| Old system lines | 986 | 0 | ❌ |
| New system lines | ~1,700 | ~600 | ❌ |
| Total reduction | +120 | -1,938 | ❌ |
| Reduction % | -7% | 76% | ❌ |
| Tests | Failing | Passing | ❌ |

**After completion:**

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Old files | Deleted | `ls src/providers/capability_router.py` (should error) |
| Old imports | Removed | `grep "registry_selection" src/providers/registry_core.py` (should be empty) |
| Tests | Passing | `python test_hybrid_simple.py` (all OK) |
| Line count | ~600 | Count lines as in Step 7 |
| Reduction | 76% | Calculate: (old - new) / old * 100 |

---

## Estimated Time

- **Step 1-3:** File deletion and cleanup - 30 minutes
- **Step 4:** Import removal - 5 minutes
- **Step 5:** Config fix - 15-30 minutes (depending on approach)
- **Step 6-7:** Testing and verification - 30 minutes

**Total: 1.5 - 2 hours**

**With debugging: 2-4 hours**

---

## Final Result

After completing all steps:

✅ **True 76% code reduction achieved**
✅ **Clean architecture (single routing system)**
✅ **All tests passing**
✅ **Production ready**
✅ **Claims match reality**

**Current state: Good components, incomplete migration**
**Post-completion: Clean, efficient, production-ready system**

---

## Next Actions

1. **Review this plan** with team
2. **Assign completion task** to developer
3. **Execute steps 1-7**
4. **Verify metrics**
5. **Mark as complete** only after all steps pass

**Ready to complete the migration and deliver on the promise!**
