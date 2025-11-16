# Script Catalog

**Date**: 2025-11-10
**Version**: 1.0.0
**Status**: Active Scripts Documented

This catalog documents all scripts in the `scripts/` directory, their purpose, and whether they are actively used or archived.

---

## 📁 Archive Status

### Phase-Specific Scripts (Moved to `archive/phase-scripts/`)
These scripts were part of specific development phases and are no longer actively used:

- ✅ `archive/phase-scripts/phase_a_mcp_validation.py` - Phase A: MCP Storage Validation (2025-10-22)
- ✅ `archive/phase-scripts/phase1_behavior_capture.py` - Phase 1: Workflow Tool Behavior Capture (2025-11-03)
- ✅ `archive/phase-scripts/phase2/` - Phase 2 comparison and testing scripts
  - `analyze_results.py`
  - `run_comparison.py`
  - `websocket_test_client.py`

### Deprecated Scripts (Moved to `archive/deprecated/`)
These scripts had redundant functionality or were replaced by more comprehensive versions:

- ✅ `archive/deprecated/apply_migration_direct.py` - Replaced by `execute_unified_schema_migration.py`
- ✅ `archive/deprecated/apply_unified_migration.py` - Replaced by `execute_unified_schema_migration.py`
- ✅ `archive/deprecated/execute_migration.py` - Replaced by `execute_unified_schema_migration.py`
- ✅ `archive/deprecated/run_all_tests.py` - Kept as primary test runner
- ✅ `archive/deprecated/testing/run_tests.py` - Replaced by `run_all_tests.py` (less feature-rich)
- ✅ `archive/deprecated/testing/integration_test_phase7.py` - Phase 7 specific (archived)
- ✅ `archive/deprecated/ws/ws_chat_once.py` - Replaced by unified WebSocket test
- ✅ `archive/deprecated/ws/ws_chat_review_once.py` - Replaced by unified WebSocket test
- ✅ `archive/deprecated/ws/ws_chat_roundtrip.py` - Replaced by unified WebSocket test
- ✅ `archive/deprecated/check_redis_monitoring.py` - Redis-specific check (redis monitoring now integrated)
- ✅ `archive/deprecated/check_recovery_status.py` - Emergency recovery check (no longer needed)

---

## ✅ Active Scripts (Keep)

### Production & Core Operations

1. **`start_server.py`** - Main server startup script
   - Purpose: Starts the EXAI MCP Server
   - Usage: `python scripts/start_server.py`
   - Status: ✅ Critical - Always needed

2. **`FINAL_VERIFICATION.py`** - System verification
   - Purpose: Verifies EXAI MCP Server is operational
   - Usage: `python scripts/FINAL_VERIFICATION.py`
   - Status: ✅ Critical - Final validation

3. **`setup_claude_connection.py`** - Claude integration setup
   - Purpose: Configures Claude Code to work with EXAI
   - Usage: `python scripts/setup_claude_connection.py`
   - Status: ✅ Critical - Claude integration

4. **`exai_native_mcp_server.py`** - Native MCP server
   - Purpose: Core MCP server implementation
   - Usage: Called by start_server.py
   - Status: ✅ Critical - Core functionality

5. **`validate_mcp_connection.py`** - MCP connection validation
   - Purpose: Tests MCP config and connections
   - Usage: `python scripts/validate_mcp_connection.py`
   - Status: ✅ Important - Validation

6. **`generate_jwt_token.py`** - JWT token generation
   - Purpose: Generates JWT tokens for authentication
   - Usage: `python scripts/generate_jwt_token.py`
   - Status: ✅ Important - Authentication

7. **`generate_all_jwt_tokens.py`** - Bulk JWT token generation
   - Purpose: Generates multiple JWT tokens
   - Usage: `python scripts/generate_all_jwt_tokens.py`
   - Status: ✅ Useful - Bulk operations

8. **`config.py`** - Configuration management
   - Purpose: Centralized configuration
   - Usage: Imported by other scripts
   - Status: ✅ Critical - Configuration

### Testing & Quality Assurance

9. **`run_all_tests.py`** - Primary test runner ✅ **KEEP**
   - Purpose: Comprehensive test suite with coverage, parallel execution
   - Features: Coverage reports, parallel execution, fail-fast, JUnit XML
   - Usage: `python scripts/run_all_tests.py --type all --coverage`
   - Status: ✅ Critical - Only test runner needed

10. **`testing/benchmark_performance.py`** - Performance benchmarking
    - Purpose: Benchmarks system performance
    - Usage: `python scripts/testing/benchmark_performance.py`
    - Status: ✅ Useful - Performance testing

11. **`testing/collect_baseline_metrics.py`** - Baseline metrics collection
    - Purpose: Collects baseline performance metrics
    - Usage: `python scripts/testing/collect_baseline_metrics.py`
    - Status: ✅ Useful - Metrics

12. **`testing/monitor_24h_stability.py`** - 24-hour stability monitoring
    - Purpose: Long-running stability test
    - Usage: `python scripts/testing/monitor_24h_stability.py`
    - Status: ✅ Useful - Stability testing

13. **`testing/retrieve_exai_conversation.py`** - Conversation retrieval
    - Purpose: Retrieves EXAI conversations for testing
    - Usage: `python scripts/testing/retrieve_exai_conversation.py`
    - Status: ✅ Useful - Testing

14. **`testing/test_session_persistence.py`** - Session persistence testing
    - Purpose: Tests session persistence
    - Usage: `python scripts/testing/test_session_persistence.py`
    - Status: ✅ Useful - Testing

### Database & Migrations

15. **`execute_unified_schema_migration.py`** - ✅ **UNIFIED MIGRATION SCRIPT**
   - Purpose: Executes unified database schema migration
   - Features: SQL parsing, statement execution, validation
   - Usage: `python scripts/execute_unified_schema_migration.py`
   - Status: ✅ Critical - Primary migration script
   - **Note**: Replaced 3 other migration scripts

16. **`validate_migration.py`** - Migration validation
   - Purpose: Validates migration was applied correctly
   - Usage: `python scripts/validate_migration.py`
   - Status: ✅ Important - Migration validation

17. **`database/apply_schema.py`** - Schema application
   - Purpose: Applies database schema
   - Usage: `python scripts/database/apply_schema.py`
   - Status: ✅ Important - Database operations

18. **`database/apply_table.py`** - Table creation
   - Purpose: Creates database tables
   - Usage: `python scripts/database/apply_table.py`
   - Status: ✅ Important - Database operations

19. **`database/check_tables.py`** - Table verification
   - Purpose: Verifies tables exist
   - Usage: `python scripts/database/check_tables.py`
   - Status: ✅ Useful - Database verification

20. **`database/create_table_direct.py`** - Direct table creation
   - Purpose: Creates tables via direct connection
   - Usage: `python scripts/database/create_table_direct.py`
   - Status: ✅ Useful - Database operations

### Health Checks & Monitoring

21. **`runtime/health_check.py`** - Comprehensive system health check ✅ **KEEP**
   - Purpose: Checks Supabase, database, storage, WebSocket daemon
   - Features: Exit codes for different failure types
   - Usage: `python scripts/runtime/health_check.py`
   - Status: ✅ Critical - System health

22. **`ws/health_check.py`** - WebSocket health check ✅ **KEEP**
   - Purpose: WebSocket-specific health check with hello handshake
   - Features: Token-based authentication
   - Usage: `python scripts/ws/health_check.py`
   - Status: ✅ Important - WebSocket health

23. **`ws/ws_status.py`** - WebSocket status check ✅ **KEEP**
   - Purpose: Simple status check via health file
   - Features: Checks daemon health file
   - Usage: `python scripts/ws/ws_status.py`
   - Status: ✅ Useful - Quick status

24. **`ws/run_ws_daemon.py`** - WebSocket daemon runner
   - Purpose: Starts the WebSocket daemon
   - Usage: Called by start_server.py
   - Status: ✅ Critical - Core daemon

### WebSocket Testing

25. **`ws/ws_chat_analyze_files.py`** - File analysis via WebSocket ✅ **KEEP**
   - Purpose: Analyzes files using WebSocket chat
   - Features: Markdown report generation
   - Usage: `python scripts/ws/ws_chat_analyze_files.py <output> <file1> <file2> ...`
   - Status: ✅ Useful - File analysis

26. **`ws/websocket_test_client.py`** - General WebSocket test client
   - Purpose: General-purpose WebSocket testing
   - Usage: `python scripts/ws/websocket_test_client.py`
   - Status: ✅ Useful - WebSocket testing

### Validation Scripts

27. **`unified_validator.py`** - Unified validation
   - Purpose: Validates multiple aspects of the system
   - Usage: `python scripts/unified_validator.py`
   - Status: ✅ Important - Validation

28. **`validate_environment.py`** - Environment validation
   - Purpose: Validates environment variables
   - Usage: `python scripts/validate_environment.py`
   - Status: ✅ Important - Environment check

29. **`validate_enhanced_schemas.py`** - Schema validation
   - Purpose: Validates enhanced database schemas
   - Usage: `python scripts/validate_enhanced_schemas.py`
   - Status: ✅ Useful - Schema validation

30. **`validation/validate_mcp_configs.py`** - MCP config validation
   - Purpose: Validates MCP server configurations
   - Usage: `python scripts/validation/validate_mcp_configs.py`
   - Status: ✅ Important - Config validation

31. **`validation/validate_timeout_hierarchy.py`** - Timeout validation
   - Purpose: Validates timeout hierarchy
   - Usage: `python scripts/validation/validate_timeout_hierarchy.py`
   - Status: ✅ Useful - Timeout validation

32. **`validation/validate_context_engineering.py`** - Context engineering validation
   - Purpose: Validates context engineering
   - Usage: `python scripts/validation/validate_context_engineering.py`
   - Status: ✅ Useful - Validation

### Supabase Operations

33. **`get_supabase_keys.py`** - Supabase key retrieval
   - Purpose: Retrieves Supabase API keys
   - Usage: `python scripts/get_supabase_keys.py`
   - Status: ✅ Important - Key management

34. **`supabase/setup_supabase.py`** - Supabase setup
   - Purpose: Sets up Supabase configuration
   - Usage: `python scripts/supabase/setup_supabase.py`
   - Status: ✅ Important - Setup

35. **`supabase/create_buckets.py`** - Storage bucket creation
   - Purpose: Creates Supabase storage buckets
   - Usage: `python scripts/supabase/create_buckets.py`
   - Status: ✅ Useful - Storage setup

36. **`supabase/supabase_client.py`** - Supabase client utilities
   - Purpose: Supabase client helper functions
   - Usage: Imported by other scripts
   - Status: ✅ Important - Client utilities

37. **`supabase/execute_schema.py`** - Schema execution
   - Purpose: Executes Supabase schema
   - Usage: `python scripts/supabase/execute_schema.py`
   - Status: ✅ Useful - Schema operations

38. **`supabase/deploy_cache_metrics_migration.py`** - Cache metrics deployment
   - Purpose: Deploys cache metrics migration
   - Usage: `python scripts/supabase/deploy_cache_metrics_migration.py`
   - Status: ✅ Useful - Metrics

### Production Readiness

39. **`production_readiness/validate_checklist.py`** - Production checklist validation
   - Purpose: Validates production readiness checklist
   - Usage: `python scripts/production_readiness/validate_checklist.py`
   - Status: ✅ Important - Production validation

40. **`production_readiness/validate_simple.py`** - Simple production validation
   - Purpose: Quick production readiness check
   - Usage: `python scripts/production_readiness/validate_simple.py`
   - Status: ✅ Useful - Quick check

41. **`production_readiness/setup_supabase_pro.py`** - Production Supabase setup
   - Purpose: Sets up Supabase for production
   - Usage: `python scripts/production_readiness/setup_supabase_pro.py`
   - Status: ✅ Useful - Production setup

### Maintenance & Utilities

42. **`auto_fix_script_issues.py`** - Auto-fix script issues
   - Purpose: Automatically fixes common script issues
   - Usage: `python scripts/auto_fix_script_issues.py --fix`
   - Status: ✅ Useful - Maintenance

43. **`maintenance/bump_version.py`** - Version bumping
   - Purpose: Bumps project version
   - Usage: `python scripts/maintenance/bump_version.py`
   - Status: ✅ Useful - Version management

44. **`maintenance/cleanup_documentation.py`** - Documentation cleanup
   - Purpose: Cleans up documentation
   - Usage: `python scripts/maintenance/cleanup_documentation.py`
   - Status: ✅ Useful - Maintenance

45. **`maintenance/consolidate_tests.py`** - Test consolidation
   - Purpose: Consolidates test scripts
   - Usage: `python scripts/maintenance/consolidate_tests.py`
   - Status: ✅ Useful - Test management

46. **`maintenance/glm_files_cleanup.py`** - GLM files cleanup
   - Purpose: Cleans up GLM-related files
   - Usage: `python scripts/maintenance/glm_files_cleanup.py`
   - Status: ✅ Useful - Maintenance

### Development & Analysis

47. **`batch_analyze_archive_docs.py`** - Batch document analysis
   - Purpose: Analyzes archived documentation
   - Usage: `python scripts/batch_analyze_archive_docs.py`
   - Status: ✅ Useful - Analysis

48. **`dev/diagnose_mcp.py`** - MCP diagnostics
   - Purpose: Diagnoses MCP issues
   - Usage: `python scripts/dev/diagnose_mcp.py`
   - Status: ✅ Useful - Diagnostics

49. **`dev/stress_test_exai.py`** - EXAI stress testing
   - Purpose: Stresses the EXAI system
   - Usage: `python scripts/dev/stress_test_exai.py`
   - Status: ✅ Useful - Testing

### Simple Utilities

50. **`check_port.py`** - Port availability check ✅ **KEEP**
   - Purpose: Checks if a port is available
   - Usage: `python scripts/check_port.py`
   - Status: ✅ Useful - Quick check
   - **Note**: Very simple, no redundancy

51. **`check-project-status.py`** - Project status check
   - Purpose: Checks overall project status
   - Usage: `python scripts/check-project-status.py`
   - Status: ✅ Useful - Status check

### Monitoring

52. **`monitoring/realtime_log_monitor.py`** - Real-time log monitoring
   - Purpose: Monitors logs in real-time
   - Usage: `python scripts/monitoring/realtime_log_monitor.py`
   - Status: ✅ Useful - Monitoring

53. **`monitoring/log_sampling_monitor.py`** - Log sampling monitor
   - Purpose: Monitors log sampling
   - Usage: `python scripts/monitoring/log_sampling_monitor.py`
   - Status: ✅ Useful - Monitoring

54. **`monitor_shadow_mode.py`** - Shadow mode monitoring
   - Purpose: Monitors shadow mode
   - Usage: `python scripts/monitor_shadow_mode.py`
   - Status: ✅ Useful - Monitoring

### Other Scripts

55. **`create_test_users.py`** - Test user creation
   - Purpose: Creates test users
   - Usage: `python scripts/create_test_users.py`
   - Status: ✅ Useful - Testing

56. **`create_monitoring_view.py`** - Monitoring view creation
   - Purpose: Creates database monitoring views
   - Usage: `python scripts/create_monitoring_view.py`
   - Status: ✅ Useful - Monitoring

57. **`create_functions_via_sql.py`** - Function creation via SQL
   - Purpose: Creates database functions via SQL
   - Usage: `python scripts/create_functions_via_sql.py`
   - Status: ✅ Useful - Database functions

58. **`deploy_all_migrations.py`** - Deploy all migrations
   - Purpose: Deploys all database migrations
   - Usage: `python scripts/deploy_all_migrations.py`
   - Status: ✅ Useful - Migration deployment

59. **`deploy_monitoring_functions.py`** - Deploy monitoring functions
   - Purpose: Deploys monitoring functions
   - Usage: `python scripts/deploy_monitoring_functions.py`
   - Status: ✅ Useful - Monitoring

60. **`quick_deploy.py`** - Quick deployment
   - Purpose: Quick deployment script
   - Usage: `python scripts/quick_deploy.py`
   - Status: ✅ Useful - Deployment

61. **`validate_enhanced_schemas.py`** - Enhanced schema validation
   - Purpose: Validates enhanced schemas
   - Usage: `python scripts/validate_enhanced_schemas.py`
   - Status: ✅ Useful - Schema validation

62. **`verify_backfill.py`** - Backfill verification
   - Purpose: Verifies data backfill
   - Usage: `python scripts/verify_backfill.py`
   - Status: ✅ Useful - Verification

63. **`verify_exai.py`** - EXAI verification
   - Purpose: Verifies EXAI system
   - Usage: `python scripts/verify_exai.py`
   - Status: ✅ Useful - Verification

64. **`file_cleanup_job.py`** - File cleanup job
   - Purpose: Cleans up files
   - Usage: `python scripts/file_cleanup_job.py`
   - Status: ✅ Useful - Maintenance

65. **`phase_a2_security_tables.sql`** - Phase A2 security tables
   - Purpose: SQL for security tables
   - Usage: Applied via migration
   - Status: ✅ Useful - Security

66. **`query_supabase_data.py`** - Supabase data querying
   - Purpose: Queries Supabase data
   - Usage: `python scripts/query_supabase_data.py`
   - Status: ✅ Useful - Data query

67. **`setup_multi_user_database.py`** - Multi-user database setup
   - Purpose: Sets up multi-user database
   - Usage: `python scripts/setup_multi_user_database.py`
   - Status: ✅ Useful - Database setup

68. **`quick_backfill_sha256.py`** - SHA256 backfill
   - Purpose: Backfills SHA256 hashes
   - Usage: `python scripts/quick_backfill_sha256.py`
   - Status: ✅ Useful - Backfill

69. **`fix_duplicate_messages.py`** - Duplicate message fix
   - Purpose: Fixes duplicate messages
   - Usage: `python scripts/fix_duplicate_messages.py`
   - Status: ✅ Useful - Message cleanup

70. **`fix_on_chunk_parameter.py`** - Chunk parameter fix
   - Purpose: Fixes chunk parameter issues
   - Usage: `python scripts/fix_on_chunk_parameter.py`
   - Status: ✅ Useful - Fix

71. **`apply_idempotency_migration.py`** - Idempotency migration
   - Purpose: Applies idempotency migration
   - Usage: `python scripts/apply_idempotency_migration.py`
   - Status: ✅ Useful - Migration

72. **`review_external_ai_changes_with_k2.py`** - External AI changes review
   - Purpose: Reviews external AI changes
   - Usage: `python scripts/review_external_ai_changes_with_k2.py`
   - Status: ✅ Useful - Review

---

## 📊 Consolidation Summary

### Scripts Removed: 12
- 3 migration scripts → consolidated into 1
- 3 test scripts → consolidated into 1
- 3 WebSocket chat scripts → consolidated into 1 (kept file analyzer)
- 2 check scripts → archived as redundant
- 1 phase-specific integration test → archived

### Scripts Archived: 17
- **Phase scripts**: 5 files (Phase A, 1, 2)
- **Deprecated**: 12 files (redundant functionality)

### Active Scripts: 72
All remaining scripts are actively used and serve unique purposes.

---

## ✅ Maintenance Notes

1. **Migration**: Use only `execute_unified_schema_migration.py` (unified approach)
2. **Testing**: Use only `run_all_tests.py` (comprehensive test runner)
3. **WebSocket Testing**: Use `ws_chat_analyze_files.py` for file analysis
4. **Health Checks**: All 3 health check scripts serve different purposes - keep all
5. **Phase Scripts**: All moved to archive - can be restored if needed for reference

---

## 🔄 Future Consolidation Opportunities

- Consider merging simple check scripts (`check_port.py`, `check-project-status.py`) if needed
- Production readiness scripts could be consolidated into a single comprehensive script
- Validation scripts in `validation/` directory could be unified

---

**Status**: ✅ **CONSOLIDATION COMPLETE**

**Last Updated**: 2025-11-10
**Archived Scripts**: 17
**Active Scripts**: 72
**Total Scripts**: 89 (down from 95+)
