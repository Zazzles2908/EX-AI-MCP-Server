-- ============================================================================
-- DATABASE BRANCHING POC - TEST SUITE
-- ============================================================================
-- Date: 2025-10-22
-- Purpose: Comprehensive test suite for validating database branching
-- Branch: poc-test-branch (fvdzrllnzrglsladcpay)
-- Main: mxaazuhlqewmkweewyaz
--
-- EXAI Consultation ID: 9222d725-b6cd-44f1-8406-274e5a3b3389
-- ============================================================================

-- ============================================================================
-- PHASE 1: CONNECTIVITY & SCHEMA VALIDATION
-- ============================================================================

-- Test 1: Verify database connection
SELECT current_database(), current_user, version();

-- Test 2: Verify extensions are available
SELECT extname, extversion 
FROM pg_extension 
WHERE extname IN ('uuid-ossp', 'vector')
ORDER BY extname;

-- Test 3: Verify tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Test 4: Verify indexes exist
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- ============================================================================
-- PHASE 2: DATA ISOLATION TESTING
-- ============================================================================

-- Test 5: Create test conversation (branch only)
INSERT INTO conversations (id, session_id, continuation_id, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'poc-test-session',
    'poc-test-continuation',
    NOW(),
    NOW()
)
RETURNING id, session_id, continuation_id;

-- Test 6: Create test messages (branch only)
-- Note: Replace <conversation_id> with actual ID from Test 5
INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES (
    gen_random_uuid(),
    '<conversation_id>',
    'user',
    'Test message in POC branch - should not appear in main',
    NOW()
)
RETURNING id, conversation_id, content;

-- Test 7: Create test file metadata (branch only)
INSERT INTO files (
    id, 
    storage_path, 
    original_name, 
    file_type, 
    size_bytes,
    created_at
)
VALUES (
    gen_random_uuid(),
    'poc-test/test-file.txt',
    'test-file.txt',
    'user_upload',
    1024,
    NOW()
)
RETURNING id, storage_path, original_name;

-- Test 8: Query test data (should exist in branch)
SELECT COUNT(*) as test_conversations
FROM conversations 
WHERE session_id = 'poc-test-session';

SELECT COUNT(*) as test_messages
FROM messages 
WHERE content LIKE '%POC branch%';

SELECT COUNT(*) as test_files
FROM files 
WHERE storage_path LIKE 'poc-test/%';

-- ============================================================================
-- PHASE 3: SCHEMA MODIFICATION TESTING
-- ============================================================================

-- Test 9: Create test table (branch only)
CREATE TABLE IF NOT EXISTS poc_test_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_data TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Test 10: Insert test data into test table
INSERT INTO poc_test_table (test_data)
VALUES 
    ('Test data 1'),
    ('Test data 2'),
    ('Test data 3')
RETURNING id, test_data;

-- Test 11: Create test index
CREATE INDEX IF NOT EXISTS idx_poc_test_created_at 
ON poc_test_table(created_at);

-- Test 12: Verify test table exists
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name = 'poc_test_table'
ORDER BY ordinal_position;

-- ============================================================================
-- PHASE 4: PERFORMANCE BASELINE
-- ============================================================================

-- Test 13: Measure query performance
EXPLAIN ANALYZE
SELECT c.id, c.session_id, COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, c.session_id
LIMIT 100;

-- Test 14: Measure index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC
LIMIT 20;

-- ============================================================================
-- PHASE 5: DATA INTEGRITY VALIDATION
-- ============================================================================

-- Test 15: Verify foreign key constraints
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- Test 16: Verify unique constraints
SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'UNIQUE'
ORDER BY tc.table_name;

-- ============================================================================
-- PHASE 6: CLEANUP VERIFICATION QUERIES
-- ============================================================================

-- Test 17: Count test data before cleanup
SELECT 
    (SELECT COUNT(*) FROM conversations WHERE session_id = 'poc-test-session') as test_conversations,
    (SELECT COUNT(*) FROM messages WHERE content LIKE '%POC branch%') as test_messages,
    (SELECT COUNT(*) FROM files WHERE storage_path LIKE 'poc-test/%') as test_files,
    (SELECT COUNT(*) FROM poc_test_table) as test_table_rows;

-- ============================================================================
-- CLEANUP OPERATIONS (Run after testing complete)
-- ============================================================================

-- Cleanup 1: Delete test messages
DELETE FROM messages 
WHERE content LIKE '%POC branch%';

-- Cleanup 2: Delete test files
DELETE FROM files 
WHERE storage_path LIKE 'poc-test/%';

-- Cleanup 3: Delete test conversations
DELETE FROM conversations 
WHERE session_id = 'poc-test-session';

-- Cleanup 4: Drop test table
DROP TABLE IF EXISTS poc_test_table;

-- Cleanup 5: Drop test index (if table not dropped)
DROP INDEX IF EXISTS idx_poc_test_created_at;

-- ============================================================================
-- VALIDATION QUERIES (Run on MAIN branch for comparison)
-- ============================================================================

-- Validation 1: Verify test data does NOT exist in main
SELECT COUNT(*) as should_be_zero
FROM conversations 
WHERE session_id = 'poc-test-session';

-- Validation 2: Verify test table does NOT exist in main
SELECT COUNT(*) as should_be_zero
FROM information_schema.tables
WHERE table_name = 'poc_test_table';

-- Validation 3: Verify test messages do NOT exist in main
SELECT COUNT(*) as should_be_zero
FROM messages 
WHERE content LIKE '%POC branch%';

-- ============================================================================
-- MERGE CONFLICT TESTING (Advanced)
-- ============================================================================

-- Conflict Test 1: Create conflicting schema change in branch
ALTER TABLE files ADD COLUMN IF NOT EXISTS branch_test_column TEXT;

-- Conflict Test 2: Verify column exists in branch
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'files' AND column_name = 'branch_test_column';

-- Conflict Test 3: Create different schema change in main (run on main)
-- ALTER TABLE files ADD COLUMN IF NOT EXISTS main_test_column TEXT;

-- ============================================================================
-- PERFORMANCE COMPARISON QUERIES
-- ============================================================================

-- Performance 1: Compare table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Performance 2: Compare index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;

-- ============================================================================
-- NOTES
-- ============================================================================

-- 1. Run Phase 1-4 tests in BRANCH first
-- 2. Run Validation queries in MAIN to verify isolation
-- 3. Run Performance comparison on both BRANCH and MAIN
-- 4. Run Cleanup operations in BRANCH after testing
-- 5. Verify cleanup with Validation queries
-- 6. Delete branch after all testing complete

-- ============================================================================
-- EXPECTED RESULTS
-- ============================================================================

-- Phase 1: All connectivity and schema tests should pass
-- Phase 2: Test data should exist in branch, NOT in main
-- Phase 3: Schema modifications should exist in branch, NOT in main
-- Phase 4: Performance should be comparable between branch and main
-- Phase 5: All constraints should be preserved in branch
-- Phase 6: Cleanup should remove all test data from branch

-- ============================================================================
-- SUCCESS CRITERIA
-- ============================================================================

-- ✅ Branch can connect and query successfully
-- ✅ Schema is identical to main (before modifications)
-- ✅ Data operations work in branch
-- ✅ Schema modifications work in branch
-- ✅ Changes in branch do NOT affect main
-- ✅ Performance is comparable to main
-- ✅ Cleanup removes all test artifacts
-- ✅ Branch can be safely deleted

-- ============================================================================
-- END OF TEST SUITE
-- ============================================================================

