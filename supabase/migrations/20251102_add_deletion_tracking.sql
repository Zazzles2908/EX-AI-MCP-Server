-- Migration: Add Deletion Tracking Columns
-- Date: 2025-11-02
-- Phase: Phase 2 HIGH - Lifecycle Management
-- Purpose: Add deleted_at and deletion_reason columns for soft deletion tracking

-- ============================================================================
-- STEP 1: Add deletion tracking columns to provider_file_uploads
-- ============================================================================

-- Add nullable columns to avoid breaking existing data
ALTER TABLE provider_file_uploads 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS deletion_reason TEXT;

-- Add comment for documentation
COMMENT ON COLUMN provider_file_uploads.deleted_at IS 'Timestamp when file was soft-deleted. NULL for active files.';
COMMENT ON COLUMN provider_file_uploads.deletion_reason IS 'Reason for deletion: expired, manual, orphaned, quota_exceeded, etc.';

-- ============================================================================
-- STEP 2: Create indexes for efficient cleanup queries
-- ============================================================================

-- Partial index for deleted files (only indexes rows where deleted_at IS NOT NULL)
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_deleted_at 
ON provider_file_uploads(deleted_at) 
WHERE deleted_at IS NOT NULL;

-- Partial index for deletion reason filtering
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_deletion_reason 
ON provider_file_uploads(deletion_reason) 
WHERE deleted_at IS NOT NULL;

-- Composite index for cleanup queries (find files to delete by age)
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_cleanup 
ON provider_file_uploads(deleted_at, upload_status) 
WHERE deleted_at IS NOT NULL;

-- ============================================================================
-- STEP 3: Create helper function for soft deletion
-- ============================================================================

CREATE OR REPLACE FUNCTION soft_delete_file(
    p_file_id UUID,
    p_deletion_reason TEXT DEFAULT 'manual'
) RETURNS VOID AS $$
BEGIN
    UPDATE provider_file_uploads
    SET 
        deleted_at = NOW(),
        deletion_reason = p_deletion_reason,
        upload_status = 'deleted',
        updated_at = NOW()
    WHERE id = p_file_id
    AND deleted_at IS NULL;  -- Only delete if not already deleted
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION soft_delete_file IS 'Soft delete a file by setting deleted_at timestamp and deletion_reason';

-- ============================================================================
-- STEP 4: Create helper function for finding expired files
-- ============================================================================

CREATE OR REPLACE FUNCTION find_expired_files(
    p_retention_days INTEGER DEFAULT 30
) RETURNS TABLE (
    id UUID,
    provider TEXT,
    provider_file_id TEXT,
    filename TEXT,
    file_size_bytes INTEGER,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pfu.id,
        pfu.provider,
        pfu.provider_file_id,
        pfu.filename,
        pfu.file_size_bytes,
        pfu.last_used,
        pfu.created_at
    FROM provider_file_uploads pfu
    WHERE 
        pfu.deleted_at IS NULL  -- Not already deleted
        AND pfu.upload_status != 'uploading'  -- Not currently uploading
        AND pfu.upload_status != 'pending'  -- Not pending upload
        AND pfu.last_used < NOW() - (p_retention_days || ' days')::INTERVAL
    ORDER BY pfu.last_used ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION find_expired_files IS 'Find files that have not been used within the retention period and are eligible for deletion';

-- ============================================================================
-- STEP 5: Create helper function for finding orphaned files
-- ============================================================================

CREATE OR REPLACE FUNCTION find_orphaned_files()
RETURNS TABLE (
    id UUID,
    provider TEXT,
    provider_file_id TEXT,
    filename TEXT,
    file_size_bytes INTEGER,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pfu.id,
        pfu.provider,
        pfu.provider_file_id,
        pfu.filename,
        pfu.file_size_bytes,
        pfu.created_at
    FROM provider_file_uploads pfu
    WHERE 
        pfu.deleted_at IS NULL  -- Not already deleted
        AND pfu.upload_status = 'failed'  -- Failed uploads
        AND pfu.created_at < NOW() - INTERVAL '7 days'  -- Older than 7 days
    ORDER BY pfu.created_at ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION find_orphaned_files IS 'Find orphaned files (failed uploads older than 7 days) that should be cleaned up';

-- ============================================================================
-- STEP 6: Migration complete
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 20251102_add_deletion_tracking completed successfully';
    RAISE NOTICE 'Added columns: deleted_at, deletion_reason';
    RAISE NOTICE 'Created indexes: idx_provider_file_uploads_deleted_at, idx_provider_file_uploads_deletion_reason, idx_provider_file_uploads_cleanup';
    RAISE NOTICE 'Created functions: soft_delete_file, find_expired_files, find_orphaned_files';
END $$;

