-- Migration: Add supabase_file_id column to provider_file_uploads table
-- Date: 2025-10-18
-- Purpose: Link Moonshot file_id with Supabase Storage file_id for proper file retrieval

-- Add column with default NULL to avoid breaking existing records
ALTER TABLE provider_file_uploads 
ADD COLUMN IF NOT EXISTS supabase_file_id TEXT DEFAULT NULL;

-- Add index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_supabase_file_id 
ON provider_file_uploads(supabase_file_id);

-- Add comment for documentation
COMMENT ON COLUMN provider_file_uploads.supabase_file_id IS 'UUID of the file in Supabase Storage (files table). NULL if upload to Supabase failed or was skipped.';

-- Update schema version
INSERT INTO schema_version (version, description) VALUES 
  (2, 'Add supabase_file_id column to provider_file_uploads for storage integration');

