-- Add TTL support to files table
-- Issue: No TTL on files table → unbounded growth (11GB cached PNGs)
-- Fix: Add expires_at column for automatic cleanup

-- Add expires_at column to files table
ALTER TABLE files
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;

-- Create index on expires_at for efficient cleanup queries
CREATE INDEX IF NOT EXISTS idx_files_expires_at ON files(expires_at);

-- Set default expires_at for cache files (24 hours from creation)
-- This will be set via trigger or application logic
COMMENT ON COLUMN files.expires_at IS 'File expiration time for cleanup. 24h TTL for cache files.';

-- Cleanup function to remove expired files
CREATE OR REPLACE FUNCTION cleanup_expired_files()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete expired cache files
    DELETE FROM files
    WHERE expires_at < NOW()
    AND file_type = 'cache';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Log cleanup
    RAISE NOTICE 'Cleaned up % expired cache files', deleted_count;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Schedule automatic cleanup (can be called by cron or application)
SELECT cleanup_expired_files();

-- Create index on file_type and expires_at for compound queries
CREATE INDEX IF NOT EXISTS idx_files_type_expires_at
ON files(file_type, expires_at);

COMMENT ON FUNCTION cleanup_expired_files() IS 'Removes expired cache files from files table';