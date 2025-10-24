-- ============================================================================
-- BASELINE DATA SETUP FOR BRANCH TESTING
-- ============================================================================
-- Date: 2025-10-22
-- Purpose: Create baseline data in MAIN database before branch testing
-- Database: main (mxaazuhlqewmkweewyaz)
--
-- This script creates minimal test data to validate isolation between
-- main and branch databases during Phase D testing.
-- ============================================================================

-- ============================================================================
-- CLEANUP EXISTING TEST DATA (if any)
-- ============================================================================

-- Remove any existing test data from previous runs
DELETE FROM messages WHERE conversation_id IN (
    SELECT id FROM conversations WHERE continuation_id LIKE 'baseline-test-%'
);

DELETE FROM files WHERE metadata->>'test_type' = 'baseline';

DELETE FROM conversations WHERE continuation_id LIKE 'baseline-test-%';

-- ============================================================================
-- CREATE BASELINE CONVERSATIONS
-- ============================================================================

-- Conversation 1: Simple conversation (no messages, no files)
INSERT INTO conversations (id, session_id, continuation_id, title, metadata, created_at, updated_at)
VALUES (
    'a0000000-0000-0000-0000-000000000001'::uuid,
    'a0000000-0000-0000-0000-000000000010'::uuid,
    'baseline-test-conversation-1',
    'Baseline Test Conversation 1',
    '{"test_type": "baseline", "description": "Simple conversation for isolation testing"}'::jsonb,
    NOW(),
    NOW()
);

-- Conversation 2: Conversation with messages
INSERT INTO conversations (id, session_id, continuation_id, title, metadata, created_at, updated_at)
VALUES (
    'a0000000-0000-0000-0000-000000000002'::uuid,
    'a0000000-0000-0000-0000-000000000010'::uuid,
    'baseline-test-conversation-2',
    'Baseline Test Conversation 2',
    '{"test_type": "baseline", "description": "Conversation with messages for FK testing"}'::jsonb,
    NOW(),
    NOW()
);

-- Conversation 3: Conversation with files
INSERT INTO conversations (id, session_id, continuation_id, title, metadata, created_at, updated_at)
VALUES (
    'a0000000-0000-0000-0000-000000000003'::uuid,
    'a0000000-0000-0000-0000-000000000010'::uuid,
    'baseline-test-conversation-3',
    'Baseline Test Conversation 3',
    '{"test_type": "baseline", "description": "Conversation with files for relationship testing"}'::jsonb,
    NOW(),
    NOW()
);

-- ============================================================================
-- CREATE BASELINE MESSAGES
-- ============================================================================

-- Messages for Conversation 2
INSERT INTO messages (id, conversation_id, role, content, metadata, created_at)
VALUES 
(
    'b0000000-0000-0000-0000-000000000001'::uuid,
    'a0000000-0000-0000-0000-000000000002'::uuid,
    'user',
    'Baseline test message 1',
    '{"test_type": "baseline"}'::jsonb,
    NOW()
),
(
    'b0000000-0000-0000-0000-000000000002'::uuid,
    'a0000000-0000-0000-0000-000000000002'::uuid,
    'assistant',
    'Baseline test response 1',
    '{"test_type": "baseline"}'::jsonb,
    NOW()
),
(
    'b0000000-0000-0000-0000-000000000003'::uuid,
    'a0000000-0000-0000-0000-000000000002'::uuid,
    'user',
    'Baseline test message 2',
    '{"test_type": "baseline"}'::jsonb,
    NOW()
);

-- Messages for Conversation 3
INSERT INTO messages (id, conversation_id, role, content, metadata, created_at)
VALUES 
(
    'b0000000-0000-0000-0000-000000000004'::uuid,
    'a0000000-0000-0000-0000-000000000003'::uuid,
    'user',
    'Baseline test message with file reference',
    '{"test_type": "baseline", "has_files": true}'::jsonb,
    NOW()
),
(
    'b0000000-0000-0000-0000-000000000005'::uuid,
    'a0000000-0000-0000-0000-000000000003'::uuid,
    'assistant',
    'Baseline test response with file reference',
    '{"test_type": "baseline", "has_files": true}'::jsonb,
    NOW()
);

-- ============================================================================
-- CREATE BASELINE FILES
-- ============================================================================

-- File 1: Standalone file (not linked to conversation via conversation_files)
INSERT INTO files (id, storage_path, original_name, mime_type, size_bytes, file_type, metadata, created_at)
VALUES (
    'c0000000-0000-0000-0000-000000000001'::uuid,
    'test/baseline/file1.txt',
    'baseline_test_file_1.txt',
    'text/plain',
    1024,
    'user_upload',
    '{"test_type": "baseline", "description": "Standalone test file"}'::jsonb,
    NOW()
);

-- File 2: File linked to conversation 3
INSERT INTO files (id, storage_path, original_name, mime_type, size_bytes, file_type, metadata, created_at)
VALUES (
    'c0000000-0000-0000-0000-000000000002'::uuid,
    'test/baseline/file2.txt',
    'baseline_test_file_2.txt',
    'text/plain',
    2048,
    'user_upload',
    '{"test_type": "baseline", "description": "File linked to conversation 3"}'::jsonb,
    NOW()
);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify conversations created
SELECT 
    id, 
    continuation_id, 
    title,
    created_at
FROM conversations 
WHERE continuation_id LIKE 'baseline-test-%'
ORDER BY continuation_id;

-- Verify messages created
SELECT 
    m.id,
    m.conversation_id,
    c.continuation_id as conversation_continuation_id,
    m.role,
    m.content,
    m.created_at
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.continuation_id LIKE 'baseline-test-%'
ORDER BY m.created_at;

-- Verify files created
SELECT 
    id,
    storage_path,
    original_name,
    file_type,
    metadata->>'test_type' as test_type,
    created_at
FROM files
WHERE metadata->>'test_type' = 'baseline'
ORDER BY created_at;

-- Summary counts
SELECT 
    'conversations' as table_name,
    COUNT(*) as baseline_records
FROM conversations 
WHERE continuation_id LIKE 'baseline-test-%'
UNION ALL
SELECT 
    'messages' as table_name,
    COUNT(*) as baseline_records
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.continuation_id LIKE 'baseline-test-%'
UNION ALL
SELECT 
    'files' as table_name,
    COUNT(*) as baseline_records
FROM files
WHERE metadata->>'test_type' = 'baseline';

-- ============================================================================
-- EXPECTED RESULTS
-- ============================================================================

-- Conversations: 3 records
--   - baseline-test-conversation-1 (no messages, no files)
--   - baseline-test-conversation-2 (3 messages, no files)
--   - baseline-test-conversation-3 (2 messages, 1 file)
--
-- Messages: 5 records
--   - 3 messages for conversation-2
--   - 2 messages for conversation-3
--
-- Files: 2 records
--   - file1: Standalone
--   - file2: Linked to conversation-3

-- ============================================================================
-- CLEANUP SCRIPT (for after testing)
-- ============================================================================

-- To remove all baseline test data:
-- 
-- DELETE FROM messages WHERE conversation_id IN (
--     SELECT id FROM conversations WHERE continuation_id LIKE 'baseline-test-%'
-- );
-- 
-- DELETE FROM files WHERE metadata->>'test_type' = 'baseline';
-- 
-- DELETE FROM conversations WHERE continuation_id LIKE 'baseline-test-%';

-- ============================================================================
-- END OF BASELINE DATA SETUP
-- ============================================================================

