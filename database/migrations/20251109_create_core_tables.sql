-- ============================================================================
-- EXAI MCP Server - Core Tables Migration
-- Date: 2025-11-09
-- Purpose: Create missing core tables required by the application
-- Dependencies: None (can be applied independently)
-- ============================================================================

-- ============================================================================
-- FILE OPERATIONS TABLE
-- ============================================================================
-- Tracks all file operations (upload, download, process, delete, generate)
-- Referenced in: RLS policies, file_operations_logger, and audit trail
CREATE TABLE IF NOT EXISTS public.file_operations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_id UUID REFERENCES storage.objects(id) ON DELETE CASCADE,
    operation_type TEXT NOT NULL CHECK (operation_type IN ('upload', 'download', 'process', 'delete', 'generate')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_file_operations_user_id
    ON public.file_operations(user_id);

CREATE INDEX IF NOT EXISTS idx_file_operations_file_id
    ON public.file_operations(file_id);

CREATE INDEX IF NOT EXISTS idx_file_operations_status
    ON public.file_operations(status);

CREATE INDEX IF NOT EXISTS idx_file_operations_operation_type
    ON public.file_operations(operation_type);

CREATE INDEX IF NOT EXISTS idx_file_operations_created_at
    ON public.file_operations(created_at DESC);

-- ============================================================================
-- FILE METADATA TABLE
-- ============================================================================
-- Stores metadata about files for quick lookups and analytics
-- Referenced in: RLS policies, file registry, and lifecycle manager
CREATE TABLE IF NOT EXISTS public.file_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    file_id UUID REFERENCES storage.objects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    content_type TEXT,
    bucket_id TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256_hash TEXT,
    tags TEXT[] DEFAULT '{}',
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_file_metadata_user_id
    ON public.file_metadata(user_id);

CREATE INDEX IF NOT EXISTS idx_file_metadata_file_id
    ON public.file_metadata(file_id);

CREATE INDEX IF NOT EXISTS idx_file_metadata_bucket_id
    ON public.file_metadata(bucket_id);

CREATE INDEX IF NOT EXISTS idx_file_metadata_sha256_hash
    ON public.file_metadata(sha256_hash);

CREATE INDEX IF NOT EXISTS idx_file_metadata_tags
    ON public.file_metadata USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_file_metadata_created_at
    ON public.file_metadata(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_file_metadata_last_accessed
    ON public.file_metadata(last_accessed DESC NULLS LAST);

-- ============================================================================
-- TRIGGER FUNCTIONS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_file_operations_updated_at
    ON public.file_operations;
CREATE TRIGGER update_file_operations_updated_at
    BEFORE UPDATE ON public.file_operations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_file_metadata_updated_at
    ON public.file_metadata;
CREATE TRIGGER update_file_metadata_updated_at
    BEFORE UPDATE ON public.file_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FILE ACCESS TRACKING FUNCTION
-- ============================================================================

-- Function to increment file access count
CREATE OR REPLACE FUNCTION increment_file_access_count(p_file_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.file_metadata
    SET
        access_count = access_count + 1,
        last_accessed = NOW(),
        updated_at = NOW()
    WHERE file_id = p_file_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS
ALTER TABLE public.file_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_metadata ENABLE ROW LEVEL SECURITY;

-- FILE_OPERATIONS Policies
DROP POLICY IF EXISTS "Users can view their own file operations" ON public.file_operations;
CREATE POLICY "Users can view their own file operations"
    ON public.file_operations
    FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own file operations" ON public.file_operations;
CREATE POLICY "Users can insert their own file operations"
    ON public.file_operations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own file operations" ON public.file_operations;
CREATE POLICY "Users can update their own file operations"
    ON public.file_operations
    FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own file operations" ON public.file_operations;
CREATE POLICY "Users can delete their own file operations"
    ON public.file_operations
    FOR DELETE
    USING (auth.uid() = user_id);

-- FILE_METADATA Policies
DROP POLICY IF EXISTS "Users can view their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can view their own file metadata"
    ON public.file_metadata
    FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can insert their own file metadata"
    ON public.file_metadata
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can update their own file metadata"
    ON public.file_metadata
    FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own file metadata" ON public.file_metadata;
CREATE POLICY "Users can delete their own file metadata"
    ON public.file_metadata
    FOR DELETE
    USING (auth.uid() = user_id);

-- Service role bypass policies
DROP POLICY IF EXISTS "Service role full access file_operations" ON public.file_operations;
CREATE POLICY "Service role full access file_operations"
    ON public.file_operations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Service role full access file_metadata" ON public.file_metadata;
CREATE POLICY "Service role full access file_metadata"
    ON public.file_metadata
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.file_operations TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.file_metadata TO authenticated;

-- Grant to service role
GRANT ALL ON public.file_operations TO service_role;
GRANT ALL ON public.file_metadata TO service_role;

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION update_updated_at_column() TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION increment_file_access_count(UUID) TO authenticated, service_role;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE public.file_operations IS
    'Tracks all file operations across the system (upload, download, process, delete, generate)';

COMMENT ON TABLE public.file_metadata IS
    'Stores metadata about files for quick lookups and analytics';

COMMENT ON COLUMN public.file_metadata.sha256_hash IS
    'SHA256 hash for content-based deduplication';

COMMENT ON COLUMN public.file_metadata.tags IS
    'Array of tags for categorization and filtering';

COMMENT ON COLUMN public.file_metadata.access_count IS
    'Number of times the file has been accessed';

COMMENT ON FUNCTION increment_file_access_count(UUID) IS
    'Increments the access count and updates last_accessed timestamp for a file';

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

INSERT INTO schema_version (version, description)
VALUES (4, 'Created core tables: file_operations, file_metadata with RLS policies')
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Core Tables Migration Complete!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables Created:';
    RAISE NOTICE '  - file_operations (file operation tracking)';
    RAISE NOTICE '  - file_metadata (file metadata and analytics)';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Indexes Created: 12';
    RAISE NOTICE 'Triggers Created: 2 (updated_at)';
    RAISE NOTICE 'Functions Created: 2 (increment_access, update_updated_at)';
    RAISE NOTICE 'RLS Policies Created: 8 (4 per table)';
    RAISE NOTICE 'Service Role Policies: 2 (full access)';
    RAISE NOTICE '========================================';
END $$;
