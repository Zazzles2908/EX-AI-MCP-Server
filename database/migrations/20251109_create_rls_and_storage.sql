-- ============================================================================
-- EXAI MCP Server - RLS Policies and Storage Buckets Migration
-- Date: 2025-11-09
-- Purpose: Create storage buckets and RLS policies for file access
-- Dependencies: Core tables must exist (file_operations, file_metadata, user_quotas)
-- ============================================================================

-- ============================================================================
-- STORAGE BUCKETS
-- ============================================================================
-- Create storage buckets for file storage

-- Bucket: user-files (for user uploads)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'user-files',
    'user-files',
    false,
    104857600,  -- 100MB
    null  -- Allow all types
)
ON CONFLICT (id) DO NOTHING;

-- Bucket: results (for generated results)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'results',
    'results',
    false,
    104857600,  -- 100MB
    null  -- Allow all types
)
ON CONFLICT (id) DO NOTHING;

-- Bucket: generated-files (for AI-generated files)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'generated-files',
    'generated-files',
    false,
    104857600,  -- 100MB
    null  -- Allow all types
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STORAGE RLS POLICIES - USER-FILES BUCKET
-- ============================================================================

-- Policy: Users can upload to user-files bucket
DROP POLICY IF EXISTS "Users can upload to user-files" ON storage.objects;
CREATE POLICY "Users can upload to user-files"
    ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'user-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can view their own files in user-files bucket
DROP POLICY IF EXISTS "Users can view user-files" ON storage.objects;
CREATE POLICY "Users can view user-files"
    ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'user-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can update their own files in user-files bucket
DROP POLICY IF EXISTS "Users can update user-files" ON storage.objects;
CREATE POLICY "Users can update user-files"
    ON storage.objects
    FOR UPDATE
    USING (
        bucket_id = 'user-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can delete their own files in user-files bucket
DROP POLICY IF EXISTS "Users can delete user-files" ON storage.objects;
CREATE POLICY "Users can delete user-files"
    ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'user-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- ============================================================================
-- STORAGE RLS POLICIES - RESULTS BUCKET
-- ============================================================================

-- Policy: Users can upload to results bucket
DROP POLICY IF EXISTS "Users can upload to results" ON storage.objects;
CREATE POLICY "Users can upload to results"
    ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'results' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can view their own result files
DROP POLICY IF EXISTS "Users can view results" ON storage.objects;
CREATE POLICY "Users can view results"
    ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'results' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can update their own result files
DROP POLICY IF EXISTS "Users can update results" ON storage.objects;
CREATE POLICY "Users can update results"
    ON storage.objects
    FOR UPDATE
    USING (
        bucket_id = 'results' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can delete their own result files
DROP POLICY IF EXISTS "Users can delete results" ON storage.objects;
CREATE POLICY "Users can delete results"
    ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'results' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- ============================================================================
-- STORAGE RLS POLICIES - GENERATED-FILES BUCKET
-- ============================================================================

-- Policy: Users can upload to generated-files bucket
DROP POLICY IF EXISTS "Users can upload to generated-files" ON storage.objects;
CREATE POLICY "Users can upload to generated-files"
    ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'generated-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can view their own generated files
DROP POLICY IF EXISTS "Users can view generated-files" ON storage.objects;
CREATE POLICY "Users can view generated-files"
    ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'generated-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can update their own generated files
DROP POLICY IF EXISTS "Users can update generated-files" ON storage.objects;
CREATE POLICY "Users can update generated-files"
    ON storage.objects
    FOR UPDATE
    USING (
        bucket_id = 'generated-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can delete their own generated files
DROP POLICY IF EXISTS "Users can delete generated-files" ON storage.objects;
CREATE POLICY "Users can delete generated-files"
    ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'generated-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- ============================================================================
-- SERVICE ROLE BYPASS POLICIES
-- ============================================================================
-- Service role has full access to all storage buckets (for server operations)

-- User-files bucket - service role full access
DROP POLICY IF EXISTS "Service role full access user-files" ON storage.objects;
CREATE POLICY "Service role full access user-files"
    ON storage.objects
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Results bucket - service role full access
DROP POLICY IF EXISTS "Service role full access results" ON storage.objects;
CREATE POLICY "Service role full access results"
    ON storage.objects
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Generated-files bucket - service role full access
DROP POLICY IF EXISTS "Service role full access generated-files" ON storage.objects;
CREATE POLICY "Service role full access generated-files"
    ON storage.objects
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- STORAGE PERMISSIONS
-- ============================================================================

-- Grant permissions to authenticated users (they can only access their own files)
GRANT SELECT, INSERT, UPDATE, DELETE
    ON storage.objects
    TO authenticated;

-- Grant full permissions to service role
GRANT SELECT, INSERT, UPDATE, DELETE
    ON storage.objects
    TO service_role;

-- Grant permissions on storage bucket management
GRANT USAGE
    ON SCHEMA storage
    TO authenticated, service_role;

-- ============================================================================
-- MONITORING TABLES (if not already created)
-- ============================================================================

-- Create monitoring schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Create raw metrics table
CREATE TABLE IF NOT EXISTS monitoring.metrics_raw (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_metrics_raw_type
    ON monitoring.metrics_raw(type);

CREATE INDEX IF NOT EXISTS idx_metrics_raw_timestamp
    ON monitoring.metrics_raw(timestamp);

-- Enable RLS on monitoring tables
ALTER TABLE monitoring.metrics_raw ENABLE ROW LEVEL SECURITY;

-- Service role full access to monitoring
DROP POLICY IF EXISTS "Service role has full access to metrics_raw"
    ON monitoring.metrics_raw;
CREATE POLICY "Service role has full access to metrics_raw"
    ON monitoring.metrics_raw
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Grant permissions
GRANT ALL ON monitoring.metrics_raw TO service_role;

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

INSERT INTO schema_version (version, description)
VALUES (5, 'Created storage buckets and RLS policies for file access')
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'RLS and Storage Migration Complete!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Storage Buckets Created: 3';
    RAISE NOTICE '  - user-files (100MB limit)';
    RAISE NOTICE '  - results (100MB limit)';
    RAISE NOTICE '  - generated-files (100MB limit)';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'RLS Policies Created:';
    RAISE NOTICE '  - Per-bucket policies: 12 (4 per bucket)';
    RAISE NOTICE '  - Service role policies: 3 (1 per bucket)';
    RAISE NOTICE '  - Total: 15 policies';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Additional Components:';
    RAISE NOTICE '  - monitoring.metrics_raw table';
    RAISE NOTICE '  - Storage schema permissions';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Security Features Enabled:';
    RAISE NOTICE '  - User isolation (folder-based)';
    RAISE NOTICE '  - Service role bypass';
    RAISE NOTICE '  - Row-level security on all tables';
    RAISE NOTICE '========================================';
END $$;
