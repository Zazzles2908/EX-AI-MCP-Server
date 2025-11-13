-- Migration: Add provider_file_uploads table for Moonshot/Kimi file tracking
-- Created: 2025-10-17
-- Purpose: Track file uploads to AI providers (Kimi, GLM) with bidirectional sync

-- Create provider_file_uploads table
CREATE TABLE IF NOT EXISTS provider_file_uploads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  provider TEXT NOT NULL CHECK (provider IN ('kimi', 'glm')),
  provider_file_id TEXT NOT NULL,
  sha256 TEXT,
  filename TEXT,
  file_size_bytes INTEGER,
  last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  upload_status TEXT DEFAULT 'completed' CHECK (upload_status IN ('pending', 'completed', 'failed', 'deleted')),
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(provider, provider_file_id)
);

-- Create index for efficient cleanup queries
CREATE INDEX IF NOT EXISTS idx_provider_uploads_last_used 
ON provider_file_uploads(last_used) 
WHERE upload_status = 'completed';

-- Create index for provider lookups
CREATE INDEX IF NOT EXISTS idx_provider_uploads_provider 
ON provider_file_uploads(provider);

-- Create index for SHA256 deduplication
CREATE INDEX IF NOT EXISTS idx_provider_uploads_sha256 
ON provider_file_uploads(sha256) 
WHERE sha256 IS NOT NULL;

-- Create file_deletion_jobs table for async deletion
CREATE TABLE IF NOT EXISTS file_deletion_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  provider TEXT NOT NULL,
  provider_file_id TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  attempts INTEGER DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for job processing
CREATE INDEX IF NOT EXISTS idx_deletion_jobs_status 
ON file_deletion_jobs(status, created_at) 
WHERE status IN ('pending', 'processing');

-- Add updated_at trigger for provider_file_uploads
CREATE OR REPLACE FUNCTION update_provider_file_uploads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_provider_file_uploads_updated_at
BEFORE UPDATE ON provider_file_uploads
FOR EACH ROW
EXECUTE FUNCTION update_provider_file_uploads_updated_at();

-- Add updated_at trigger for file_deletion_jobs
CREATE OR REPLACE FUNCTION update_file_deletion_jobs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_file_deletion_jobs_updated_at
BEFORE UPDATE ON file_deletion_jobs
FOR EACH ROW
EXECUTE FUNCTION update_file_deletion_jobs_updated_at();

-- Add comment for documentation
COMMENT ON TABLE provider_file_uploads IS 'Tracks file uploads to AI providers (Kimi, GLM) for bidirectional sync and cleanup';
COMMENT ON TABLE file_deletion_jobs IS 'Async deletion job queue for provider file cleanup';

