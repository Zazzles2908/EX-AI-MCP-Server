# Tool Consolidation Report

**Date:** 2025-11-09
**Status:** MEDIUM-TERM TASK 1

## Analysis

Identified 16 overlapping files in `tools/workflows/`:

### Files to Consolidate

1. **analyze** workflow:
   - `analyze.py` (29KB - main tool)
   - `analyze_config.py` (4.5KB - config)
   - `analyze_models.py` (5.4KB - request model)

2. **codereview** workflow:
   - `codereview.py` (30KB)
   - `codereview_config.py` (6.8KB)
   - `codereview_models.py` (4KB)

3. **refactor** workflow:
   - `refactor.py` (30KB)
   - `refactor_config.py` (6.6KB)
   - `refactor_models.py` (3.3KB)

4. **consensus** workflow:
   - `consensus.py` (30KB)
   - `consensus_config.py` (7.6KB)
   - `consensus_schema.py` (4.3KB)
   - `consensus_validation.py` (3.3KB)

5. **secaudit** workflow:
   - `secaudit.py` (38KB)
   - `secaudit_config.py` (6.6KB)
   - `secaudit_models.py` (3.3KB)

6. **precommit** workflow:
   - `precommit.py` (30KB)
   - `precommit_config.py` (6.6KB)
   - `precommit_models.py` (3.3KB)

7. **tracer** workflow:
   - `tracer.py` (30KB)
   - `tracer_config.py` (3.3KB)
   - `tracer_models.py` (3.3KB)

8. **thinkdeep** workflow:
   - `thinkdeep.py` (30KB)
   - `thinkdeep_config.py` (6.6KB)
   - `thinkdeep_models.py` (3.3KB)

## Consolidation Strategy

**Current Structure:**
```
tool_name/
  ├── tool_name.py (main class)
  ├── tool_name_config.py (field descriptions)
  └── tool_name_models.py (request model)
```

**Recommended Structure:**
```
tool_name/
  └── tool_name.py (all-in-one)
    - Request model as nested class or top-level class
    - Config constants at module level
    - Main tool class
```

## Benefits

1. **Reduced Complexity:** 25 files → 8 files (68% reduction)
2. **Better Maintainability:** Changes in one place
3. **Easier Understanding:** Complete tool in single file
4. **Faster Development:** No need to jump between files
5. **Better IDE Support:** Complete tool view

## Implementation

For each tool:
1. Read base file + config + models
2. Merge into single file
3. Update imports
4. Test functionality
5. Delete old files

## Recommendation

**PRIORITY: MEDIUM** - Not blocking, but improves maintainability significantly.

**NEXT STEPS:**
1. Create consolidation script
2. Test consolidated versions
3. Update imports across codebase
4. Delete redundant files
5. Update documentation

---

**Note:** This consolidation will be performed as part of ongoing maintenance.
