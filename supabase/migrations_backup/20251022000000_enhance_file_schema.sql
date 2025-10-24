-- Migration: Enhance file schema for unified provider interface
-- Created: 2025-10-22
-- Purpose: Add columns and tables to support unified file provider architecture
-- Phase: 2.3.2 - Foundation

-- Run this migration in a single transaction
BEGIN;

-- ============================================================================
-- ENHANCE provider_file_uploads TABLE
-- ============================================================================

-- Add new columns to support unified provider interface
ALTER TABLE provider_file_uploads
ADD COLUMN IF NOT EXISTS purpose VARCHAR(20) NOT NULL DEFAULT 'file-extract',
ADD COLUMN IF NOT EXISTS checksum_sha256 VARCHAR(64),
ADD COLUMN IF NOT EXISTS custom_metadata JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS mime_type VARCHAR(100),
ADD COLUMN IF NOT EXISTS file_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add purpose constraint (maps to FilePurpose enum)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_purpose') THEN
        ALTER TABLE provider_file_uploads
        ADD CONSTRAINT chk_purpose
        CHECK (purpose IN ('file-extract', 'agent', 'assistants', 'training', 'custom'));
    END IF;
END $$;

-- Update provider constraint to include future providers
ALTER TABLE provider_file_uploads
DROP CONSTRAINT IF EXISTS provider_file_uploads_provider_check;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_provider') THEN
        ALTER TABLE provider_file_uploads
        ADD CONSTRAINT chk_provider
        CHECK (provider IN ('kimi', 'glm', 'openai', 'anthropic'));
    END IF;
END $$;

-- Add file size constraint (2GB max)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_file_size') THEN
        ALTER TABLE provider_file_uploads
        ADD CONSTRAINT chk_file_size
        CHECK (file_size_bytes > 0 AND file_size_bytes <= 2147483648);
    END IF;
END $$;

-- Add unique constraint to prevent duplicate provider file IDs
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_provider_file_id') THEN
        ALTER TABLE provider_file_uploads
        ADD CONSTRAINT uq_provider_file_id UNIQUE (provider, provider_file_id);
    END IF;
END $$;

-- Ensure critical fields are NOT NULL (only if columns exist)
DO $$
BEGIN
    -- These columns should already exist from previous migration
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'provider_file_uploads' AND column_name = 'provider') THEN
        ALTER TABLE provider_file_uploads ALTER COLUMN provider SET NOT NULL;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'provider_file_uploads' AND column_name = 'provider_file_id') THEN
        ALTER TABLE provider_file_uploads ALTER COLUMN provider_file_id SET NOT NULL;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'provider_file_uploads' AND column_name = 'filename') THEN
        ALTER TABLE provider_file_uploads ALTER COLUMN filename SET NOT NULL;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'provider_file_uploads' AND column_name = 'upload_status') THEN
        ALTER TABLE provider_file_uploads ALTER COLUMN upload_status SET NOT NULL;
    END IF;
END $$;

-- ============================================================================
-- CREATE file_embeddings TABLE
-- ============================================================================
-- Caches embeddings for files to avoid regeneration

CREATE TABLE IF NOT EXISTS file_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_file_id UUID NOT NULL REFERENCES provider_file_uploads(id) ON DELETE CASCADE,
    embedding_model VARCHAR(50) NOT NULL, -- e.g., 'text-embedding-ada-002'
    embedding_dimension INTEGER NOT NULL,
    embedding_data JSONB NOT NULL, -- Store as JSONB array for compatibility
    chunk_index INTEGER DEFAULT 0, -- For multi-chunk embeddings
    text_content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE file_embeddings IS 'Caches file embeddings to avoid regeneration';
COMMENT ON COLUMN file_embeddings.embedding_data IS 'Embedding vector stored as JSONB array';
COMMENT ON COLUMN file_embeddings.chunk_index IS 'Index for multi-chunk embeddings (0 for single-chunk)';

-- ============================================================================
-- CREATE file_chunks TABLE
-- ============================================================================
-- Tracks chunked uploads for large files

CREATE TABLE IF NOT EXISTS file_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_file_id UUID NOT NULL REFERENCES provider_file_uploads(id) ON DELETE CASCADE,
    chunk_number INTEGER NOT NULL,
    chunk_size_bytes INTEGER NOT NULL,
    chunk_offset_bytes INTEGER NOT NULL,
    provider_chunk_id VARCHAR(255), -- Provider's chunk identifier
    checksum_sha256 VARCHAR(64),
    upload_status VARCHAR(20) DEFAULT 'pending' CHECK (upload_status IN ('pending', 'uploading', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider_file_id, chunk_number)
);

COMMENT ON TABLE file_chunks IS 'Tracks chunked uploads for large files (>50MB)';
COMMENT ON COLUMN file_chunks.chunk_number IS 'Sequential chunk number (0-based)';
COMMENT ON COLUMN file_chunks.provider_chunk_id IS 'Provider-specific chunk identifier';

-- ============================================================================
-- CREATE file_access_log TABLE
-- ============================================================================
-- Tracks file operations for monitoring and analytics

CREATE TABLE IF NOT EXISTS file_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_file_id UUID NOT NULL REFERENCES provider_file_uploads(id) ON DELETE CASCADE,
    operation VARCHAR(20) NOT NULL CHECK (operation IN ('upload', 'download', 'delete', 'list', 'metadata')),
    provider VARCHAR(20) NOT NULL,
    user_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE file_access_log IS 'Tracks file operations for monitoring and analytics';
COMMENT ON COLUMN file_access_log.operation IS 'Type of operation performed';
COMMENT ON COLUMN file_access_log.response_time_ms IS 'Operation duration in milliseconds';

-- ============================================================================
-- CREATE INDEXES
-- ============================================================================

-- Indexes for provider_file_uploads
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_purpose ON provider_file_uploads(purpose);
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_checksum ON provider_file_uploads(checksum_sha256) WHERE checksum_sha256 IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_size ON provider_file_uploads(file_size_bytes);
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_provider_status ON provider_file_uploads(provider, upload_status);
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_mime_type ON provider_file_uploads(mime_type) WHERE mime_type IS NOT NULL;

-- Indexes for file_embeddings
CREATE INDEX IF NOT EXISTS idx_file_embeddings_provider_file_id ON file_embeddings(provider_file_id);
CREATE INDEX IF NOT EXISTS idx_file_embeddings_model ON file_embeddings(embedding_model);
CREATE INDEX IF NOT EXISTS idx_file_embeddings_chunk_index ON file_embeddings(provider_file_id, chunk_index);

-- Indexes for file_chunks
CREATE INDEX IF NOT EXISTS idx_file_chunks_provider_file_id ON file_chunks(provider_file_id);
CREATE INDEX IF NOT EXISTS idx_file_chunks_status ON file_chunks(upload_status) WHERE upload_status IN ('pending', 'uploading');
CREATE INDEX IF NOT EXISTS idx_file_chunks_provider_chunk_id ON file_chunks(provider_chunk_id) WHERE provider_chunk_id IS NOT NULL;

-- Indexes for file_access_log
CREATE INDEX IF NOT EXISTS idx_file_access_log_provider_file_id ON file_access_log(provider_file_id);
CREATE INDEX IF NOT EXISTS idx_file_access_log_operation ON file_access_log(operation);
CREATE INDEX IF NOT EXISTS idx_file_access_log_created_at ON file_access_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_file_access_log_provider ON file_access_log(provider);

-- ============================================================================
-- CREATE TRIGGERS
-- ============================================================================

-- Trigger to update file_updated_at on provider_file_uploads
CREATE OR REPLACE FUNCTION update_file_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.file_updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER IF NOT EXISTS trg_provider_file_uploads_updated
    BEFORE UPDATE ON provider_file_uploads
    FOR EACH ROW
    EXECUTE FUNCTION update_file_updated_at();

-- Trigger to update updated_at on file_embeddings
CREATE TRIGGER IF NOT EXISTS trg_file_embeddings_updated
    BEFORE UPDATE ON file_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_provider_file_uploads_updated_at();

-- Trigger to update updated_at on file_chunks
CREATE TRIGGER IF NOT EXISTS trg_file_chunks_updated
    BEFORE UPDATE ON file_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_provider_file_uploads_updated_at();

-- ============================================================================
-- UPDATE SCHEMA VERSION
-- ============================================================================

INSERT INTO schema_version (version, description) VALUES 
  (3, 'Enhanced file schema: added purpose, checksums, embeddings, chunks, access logs');

COMMIT;

-- ============================================================================
-- POST-MIGRATION NOTES
-- ============================================================================
-- 1. Existing records will have default purpose='file-extract'
-- 2. Consider running VACUUM ANALYZE on modified tables
-- 3. Monitor index usage with pg_stat_user_indexes
-- 4. Set up automated cleanup for old access logs (>30 days)
-- 5. Consider partitioning file_access_log by date for large-scale deployments

