# Branch Testing Execution Plan

**Date:** 2025-10-22  
**Branch:** phase-d-testing (yhcyohwsqqmnfyijbxpk)  
**Parent:** main (your-project-id)  
**Test Suite:** `tests/branch_testing_suite.sql` (22 tests)

---

## Pre-Execution Checklist

### Branch Status Verification
- [ ] Branch status: `ACTIVE_HEALTHY` or `FUNCTIONS_DEPLOYED`
- [ ] Branch project_ref accessible: `yhcyohwsqqmnfyijbxpk`
- [ ] Parent database accessible: `your-project-id`

### Environment Setup
- [ ] Supabase MCP tools available
- [ ] Both project refs configured
- [ ] Test suite file ready: `tests/branch_testing_suite.sql`

---

## Test Data Plan

### Baseline Data (Create in MAIN before testing)
**Purpose:** Establish baseline for isolation testing

**Tables to populate:**
1. **conversations** (3 records)
   - conversation-main-1: Normal conversation
   - conversation-main-2: Conversation with messages
   - conversation-main-3: Conversation with files

2. **messages** (5 records)
   - 3 messages for conversation-main-2
   - 2 messages for conversation-main-3

3. **files** (2 records)
   - file-main-1: Linked to conversation-main-3
   - file-main-2: Standalone file

### Test Data (Create in BRANCH during testing)
**Purpose:** Validate isolation and schema modifications

**Phase 2 - Data Isolation:**
- conversation-branch-1: Test conversation (should NOT appear in main)
- message-branch-1: Test message (should NOT appear in main)
- file-branch-1: Test file (should NOT appear in main)

**Phase 3 - Schema Modifications:**
- test_table_branch: New table (should NOT appear in main)
- idx_test_branch: New index (should NOT appear in main)

**Phase 4 - Performance:**
- 100 test messages: Bulk insert for performance testing
- Query execution time baseline

---

## Test Execution Order

### Phase 1: Connectivity & Schema Validation (4 tests)
**Estimated Time:** 1 minute  
**Run On:** Branch database

**Tests:**
1. Database connection verification
2. Extensions availability (uuid-ossp, vector)
3. Tables exist (all public tables)
4. Indexes exist (all idx_* indexes)

**Success Criteria:**
- All queries return expected results
- No connection errors
- Schema matches main database

**Failure Handling:**
- If connection fails: Check branch status, verify project_ref
- If schema mismatch: Document differences, investigate migration state

---

### Phase 2: Data Isolation Testing (4 tests)
**Estimated Time:** 2 minutes  
**Run On:** Branch database, verify on Main

**Tests:**
5. Create test conversation in branch
6. Verify conversation exists in branch
7. Verify conversation does NOT exist in main
8. Create test message and file in branch

**Success Criteria:**
- Data created successfully in branch
- Data isolated from main (no cross-contamination)
- Foreign key relationships work correctly

**Failure Handling:**
- If data appears in main: CRITICAL - isolation broken, stop testing
- If FK violations: Check schema consistency

---

### Phase 3: Schema Modification Testing (4 tests)
**Estimated Time:** 2 minutes  
**Run On:** Branch database, verify on Main

**Tests:**
9. Create test table in branch
10. Verify table exists in branch
11. Verify table does NOT exist in main
12. Add index to test table in branch

**Success Criteria:**
- Schema changes successful in branch
- Schema changes isolated from main
- No impact on main database operations

**Failure Handling:**
- If schema changes appear in main: CRITICAL - isolation broken, stop testing
- If DDL fails: Check permissions, document error

---

### Phase 4: Performance Baseline (2 tests)
**Estimated Time:** 3 minutes  
**Run On:** Branch database

**Tests:**
13. Bulk insert 100 messages
14. Query performance measurement

**Success Criteria:**
- Bulk insert completes successfully
- Query performance within 10% of main baseline
- No memory/connection issues

**Failure Handling:**
- If performance >10% degradation: Document, investigate bottleneck
- If timeout: Reduce test data size, retry

---

### Phase 5: Data Integrity Validation (2 tests)
**Estimated Time:** 1 minute  
**Run On:** Branch database

**Tests:**
15. Foreign key constraint validation
16. Unique constraint validation

**Success Criteria:**
- Constraints enforced correctly
- Violations detected and rejected
- Data integrity maintained

**Failure Handling:**
- If constraints not enforced: CRITICAL - data integrity issue
- Document any unexpected behavior

---

### Phase 6: Cleanup Verification (1 test)
**Estimated Time:** 1 minute  
**Run On:** Branch database

**Tests:**
17. Delete test data
18. Verify cleanup successful

**Success Criteria:**
- All test data removed
- No orphaned records
- Database clean for next test

**Failure Handling:**
- If cleanup fails: Manual cleanup required
- Document any residual data

---

### Phase 7: Merge Conflict Testing (3 tests)
**Estimated Time:** 5 minutes  
**Run On:** Branch and Main

**Tests:**
19. Create conflicting schema change in branch
20. Attempt merge operation
21. Verify conflict detection

**Success Criteria:**
- Conflicts detected correctly
- Merge blocked when conflicts exist
- Clear error messages provided

**Failure Handling:**
- If conflicts not detected: CRITICAL - merge safety issue
- If merge succeeds with conflicts: CRITICAL - data corruption risk

---

### Phase 8: Performance Comparison (2 tests)
**Estimated Time:** 2 minutes  
**Run On:** Branch and Main

**Tests:**
22. Compare table sizes (branch vs main)
23. Compare index sizes (branch vs main)

**Success Criteria:**
- Size differences documented
- No unexpected bloat
- Performance metrics within acceptable range

**Failure Handling:**
- If excessive bloat: Investigate, document
- If performance issues: Identify bottleneck

---

## Success Criteria Summary

### Functional Requirements
- [ ] 22/22 tests passing
- [ ] Data isolation confirmed (no cross-contamination)
- [ ] Schema isolation confirmed (no cross-contamination)
- [ ] Merge conflict detection working

### Performance Requirements
- [ ] Query performance within 10% of main baseline
- [ ] Bulk operations complete successfully
- [ ] No memory/connection issues

### Safety Requirements
- [ ] No data corruption
- [ ] No schema corruption
- [ ] Rollback procedures validated

---

## Monitoring During Execution

### Branch Status Checks
**Frequency:** Every 5 minutes during testing

```sql
-- Check branch status
SELECT name, status, updated_at 
FROM branches 
WHERE name = 'phase-d-testing';
```

**Expected Status:** `ACTIVE_HEALTHY` or `FUNCTIONS_DEPLOYED`  
**Alert If:** Status changes to `UNHEALTHY`, `FAILED`, or `MIGRATIONS_FAILED`

### Connection Health
**Frequency:** Before each phase

```sql
-- Verify connection
SELECT current_database(), current_user, pg_backend_pid();
```

**Expected:** Successful response with branch database name  
**Alert If:** Connection timeout, authentication error

---

## Rollback Procedures

### If Critical Issue Detected
1. **Stop all testing immediately**
2. **Document the issue** (error messages, state, data)
3. **Delete the branch** to prevent further issues
4. **Investigate root cause** before retrying

### Branch Deletion Command
```bash
# Via Supabase MCP
delete_branch_supabase-mcp-full(branch_id="edca6df5-2dc0-4618-a415-35e311fa20c1")
```

### Data Cleanup (if needed)
```sql
-- Clean up any test data in main (if isolation failed)
DELETE FROM conversations WHERE continuation_id LIKE 'poc-test-%';
DELETE FROM messages WHERE conversation_id IN (
    SELECT id FROM conversations WHERE continuation_id LIKE 'poc-test-%'
);
DELETE FROM files WHERE metadata->>'test' = 'true';
```

---

## Post-Execution Tasks

### Documentation
- [ ] Update `docs/STEP5_DATABASE_BRANCHING_POC.md` with results
- [ ] Document any issues or unexpected behavior
- [ ] Update success criteria status

### Cleanup
- [ ] Delete test branch (if no longer needed)
- [ ] Remove test data from main (if any)
- [ ] Archive test results

### Next Steps
- [ ] Proceed to Task 3: Integration Testing
- [ ] Proceed to Task 4: Performance Benchmarking
- [ ] Update Phase D planning document

---

## Estimated Total Time

| Phase | Time | Cumulative |
|-------|------|------------|
| Phase 1: Connectivity | 1 min | 1 min |
| Phase 2: Data Isolation | 2 min | 3 min |
| Phase 3: Schema Modification | 2 min | 5 min |
| Phase 4: Performance | 3 min | 8 min |
| Phase 5: Data Integrity | 1 min | 9 min |
| Phase 6: Cleanup | 1 min | 10 min |
| Phase 7: Merge Conflicts | 5 min | 15 min |
| Phase 8: Performance Comparison | 2 min | 17 min |

**Total Estimated Time:** 17 minutes  
**Buffer for Issues:** +8 minutes  
**Total with Buffer:** 25 minutes

---

## Notes

- All tests are idempotent where possible
- Test data uses unique identifiers to avoid conflicts
- Performance baselines may vary based on system load
- Branch creation time not included in estimates
- Assumes no critical issues requiring investigation

---

**Ready to execute once branch status is `ACTIVE_HEALTHY` or `FUNCTIONS_DEPLOYED`!** 🚀

