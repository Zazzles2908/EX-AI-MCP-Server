-- Migration: Add SHA256 column to files table for deduplication
-- Date: 2025-10-22
-- Purpose: Enable file deduplication across providers using content hashing

-- Add sha256 column to files table (nullable for backward compatibility)
ALTER TABLE files ADD COLUMN IF NOT EXISTS sha256 TEXT;

-- Create unique index on sha256 (only for non-null values)
-- This allows existing files to have NULL sha256 while enforcing uniqueness for new files
CREATE UNIQUE INDEX IF NOT EXISTS idx_files_sha256 
ON files(sha256) 
WHERE sha256 IS NOT NULL;

-- Add comment to document the column
COMMENT ON COLUMN files.sha256 IS 'SHA256 hash of file content for deduplication. NULL for legacy files, required for new uploads.';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_files_sha256_lookup 
ON files(sha256) 
WHERE sha256 IS NOT NULL;

-- Add provider_file_id column if it doesn't exist (for provider-specific IDs)
ALTER TABLE files ADD COLUMN IF NOT EXISTS provider_file_id TEXT;

-- Add provider column if it doesn't exist
ALTER TABLE files ADD COLUMN IF NOT EXISTS provider TEXT;

-- Create index on provider for faster provider-specific queries
CREATE INDEX IF NOT EXISTS idx_files_provider 
ON files(provider) 
WHERE provider IS NOT NULL;

-- Add accessed_at column for tracking file access
ALTER TABLE files ADD COLUMN IF NOT EXISTS accessed_at TIMESTAMPTZ;

-- Add metadata column for provider-specific metadata
ALTER TABLE files ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Create index on metadata for faster JSONB queries
CREATE INDEX IF NOT EXISTS idx_files_metadata 
ON files USING GIN (metadata);

-- Migration complete
-- Next steps:
-- 1. Run backfill script to calculate SHA256 for existing files
-- 2. Update application code to use UnifiedFileManager
-- 3. Monitor for duplicate uploads

