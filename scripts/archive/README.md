# Archived Scripts

This directory contains scripts that have been moved from active use due to redundancy, completion of their purpose, or being phase-specific.

## Directory Structure

### `phase-scripts/`
Scripts that were created for specific development phases and are no longer actively used:

- **`phase_a_mcp_validation.py`** (2025-10-22)
  - Purpose: Phase A - MCP Storage Validation
  - Reason archived: Phase-specific validation, superseded by comprehensive validation

- **`phase1_behavior_capture.py`** (2025-11-03)
  - Purpose: Phase 1 - Workflow Tool Behavior Capture
  - Reason archived: Phase-specific analysis, documentation complete

- **`phase2/`** (Directory)
  - Purpose: Phase 2 - Comparison and testing scripts
  - Contains: `analyze_results.py`, `run_comparison.py`, `websocket_test_client.py`
  - Reason archived: Phase-specific testing, analysis complete

### `deprecated/`
Scripts that had redundant functionality and were replaced by more comprehensive versions:

- **`apply_migration_direct.py`**
  - Was: Basic migration using psycopg2 or supabase client
  - Replaced by: `execute_unified_schema_migration.py` (more comprehensive)

- **`apply_unified_migration.py`**
  - Was: Unified migration script
  - Replaced by: `execute_unified_schema_migration.py` (more features)

- **`execute_migration.py`**
  - Was: Simple migration executor
  - Replaced by: `execute_unified_schema_migration.py` (better validation)

- **`testing/run_tests.py`**
  - Was: Basic test runner
  - Replaced by: `run_all_tests.py` (more features: coverage, parallel, etc.)

- **`testing/integration_test_phase7.py`** (also in phase-scripts/)
  - Was: Phase 7 integration test
  - Reason archived: Phase-specific, no longer needed

- **`ws/ws_chat_once.py`**
  - Was: Simple WebSocket chat test
  - Replaced by: More specialized scripts (kept file analyzer)

- **`ws/ws_chat_review_once.py`**
  - Was: WebSocket chat review test
  - Replaced by: More specialized scripts

- **`ws/ws_chat_roundtrip.py`**
  - Was: WebSocket roundtrip test
  - Replaced by: More specialized scripts

- **`check_redis_monitoring.py`**
  - Was: Redis monitoring check
  - Reason archived: Redis monitoring now integrated elsewhere

- **`check_recovery_status.py`**
  - Was: Emergency database recovery check
  - Reason archived: No longer needed, system stable

## Why These Were Archived

1. **Redundancy**: Multiple scripts doing the same thing
2. **Phase-Specific**: Created for a specific development phase
3. **Superseded**: Replaced by more comprehensive versions
4. **Inactive**: No longer actively used in current development

## Restoration

If you need to restore any of these scripts:
```bash
# From scripts/archive/phase-scripts/
cp archive/phase-scripts/phase_a_mcp_validation.py ./

# From scripts/archive/deprecated/
cp archive/deprecated/apply_migration_direct.py ./
```

## Consolidation Results

- **Before**: 95+ scripts in `scripts/`
- **After**: 72 active scripts in `scripts/`
- **Archived**: 17 scripts
- **Reduced by**: ~18%

For detailed information about active scripts, see `SCRIPT_CATALOG.md`.

---

**Note**: These scripts are kept for historical reference and can be restored if needed.
