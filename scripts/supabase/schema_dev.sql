-- Supabase Universal File Hub - Database Schema (Development Version)
-- Date: 2025-10-30
-- EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9
-- Modified for single-user development environment (no auth.users dependency)

-- ============================================================================
-- USERS TABLE (Development - replaces auth.users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert development user
INSERT INTO public.users (email) 
VALUES ('dev@localhost')
ON CONFLICT (email) DO NOTHING;

-- Function to get dev user ID
CREATE OR REPLACE FUNCTION get_dev_user_id()
RETURNS UUID AS $$
    SELECT id FROM public.users WHERE email = 'dev@localhost' LIMIT 1;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- FILE OPERATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.file_operations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  file_id UUID,
  operation_type TEXT NOT NULL CHECK (operation_type IN ('upload', 'download', 'process', 'delete', 'generate')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  metadata JSONB DEFAULT '{}',
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE public.file_operations IS 'Tracks all file operations for audit and monitoring';
COMMENT ON COLUMN public.file_operations.operation_type IS 'Type of operation: upload, download, process, delete, generate';
COMMENT ON COLUMN public.file_operations.status IS 'Current status: pending, processing, completed, failed';
COMMENT ON COLUMN public.file_operations.metadata IS 'Additional operation metadata (JSON)';

-- ============================================================================
-- FILE METADATA TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.file_metadata (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  file_id TEXT,
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
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

COMMENT ON TABLE public.file_metadata IS 'Metadata about files for quick lookups and analytics';
COMMENT ON COLUMN public.file_metadata.sha256_hash IS 'SHA256 hash for deduplication';
COMMENT ON COLUMN public.file_metadata.tags IS 'Array of tags for categorization';
COMMENT ON COLUMN public.file_metadata.access_count IS 'Number of times file has been accessed';

-- ============================================================================
-- FILE ID MAPPINGS TABLE (Provider Integration)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.file_id_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_file_id TEXT NOT NULL,
    provider_file_id TEXT,
    provider TEXT NOT NULL CHECK (provider IN ('kimi', 'glm')),
    user_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,
    session_info JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(supabase_file_id, provider),
    UNIQUE(provider_file_id, provider)
);

COMMENT ON TABLE public.file_id_mappings IS 'Maps Supabase file IDs to provider-specific file IDs';
COMMENT ON COLUMN public.file_id_mappings.supabase_file_id IS 'Supabase storage path (file ID)';
COMMENT ON COLUMN public.file_id_mappings.provider_file_id IS 'Provider-specific file ID (Kimi or GLM)';
COMMENT ON COLUMN public.file_id_mappings.provider IS 'Provider name (kimi or glm)';
COMMENT ON COLUMN public.file_id_mappings.status IS 'Upload status for retry logic';
COMMENT ON COLUMN public.file_id_mappings.session_info IS 'Session information (primarily for GLM)';

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_file_operations_user_id ON public.file_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_file_operations_file_id ON public.file_operations(file_id);
CREATE INDEX IF NOT EXISTS idx_file_operations_status ON public.file_operations(status);
CREATE INDEX IF NOT EXISTS idx_file_operations_operation_type ON public.file_operations(operation_type);
CREATE INDEX IF NOT EXISTS idx_file_operations_created_at ON public.file_operations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_file_metadata_user_id ON public.file_metadata(user_id);
CREATE INDEX IF NOT EXISTS idx_file_metadata_file_id ON public.file_metadata(file_id);
CREATE INDEX IF NOT EXISTS idx_file_metadata_bucket_id ON public.file_metadata(bucket_id);
CREATE INDEX IF NOT EXISTS idx_file_metadata_sha256_hash ON public.file_metadata(sha256_hash);
CREATE INDEX IF NOT EXISTS idx_file_metadata_tags ON public.file_metadata USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_file_metadata_created_at ON public.file_metadata(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_file_metadata_last_accessed ON public.file_metadata(last_accessed DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_file_id_mappings_supabase ON public.file_id_mappings(supabase_file_id);
CREATE INDEX IF NOT EXISTS idx_file_id_mappings_provider ON public.file_id_mappings(provider_file_id, provider);
CREATE INDEX IF NOT EXISTS idx_file_id_mappings_user ON public.file_id_mappings(user_id);
CREATE INDEX IF NOT EXISTS idx_file_id_mappings_status ON public.file_id_mappings(status) WHERE status = 'failed';

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_file_operations_updated_at ON public.file_operations;
CREATE TRIGGER update_file_operations_updated_at 
  BEFORE UPDATE ON public.file_operations 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_file_metadata_updated_at ON public.file_metadata;
CREATE TRIGGER update_file_metadata_updated_at 
  BEFORE UPDATE ON public.file_metadata 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION increment_file_access_count(p_file_id TEXT)
RETURNS VOID AS $$
BEGIN
  UPDATE public.file_metadata
  SET 
    access_count = access_count + 1,
    last_accessed = NOW()
  WHERE file_id = p_file_id;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION get_file_statistics(p_user_id UUID)
RETURNS TABLE (
  total_files BIGINT,
  total_size BIGINT,
  total_uploads BIGINT,
  total_downloads BIGINT,
  total_processes BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(DISTINCT fm.id)::BIGINT as total_files,
    COALESCE(SUM(fm.file_size), 0)::BIGINT as total_size,
    COUNT(CASE WHEN fo.operation_type = 'upload' THEN 1 END)::BIGINT as total_uploads,
    COUNT(CASE WHEN fo.operation_type = 'download' THEN 1 END)::BIGINT as total_downloads,
    COUNT(CASE WHEN fo.operation_type = 'process' THEN 1 END)::BIGINT as total_processes
  FROM public.file_metadata fm
  LEFT JOIN public.file_operations fo ON fm.file_id = fo.file_id
  WHERE fm.user_id = p_user_id;
END;
$$ language 'plpgsql';

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

CREATE OR REPLACE VIEW public.recent_file_operations AS
SELECT 
  fo.id,
  fo.user_id,
  fo.operation_type,
  fo.status,
  fm.filename,
  fm.file_size,
  fm.bucket_id,
  fo.created_at,
  fo.completed_at,
  EXTRACT(EPOCH FROM (fo.completed_at - fo.created_at)) as duration_seconds
FROM public.file_operations fo
LEFT JOIN public.file_metadata fm ON fo.file_id = fm.file_id
ORDER BY fo.created_at DESC
LIMIT 100;

CREATE OR REPLACE VIEW public.file_access_patterns AS
SELECT 
  fm.id,
  fm.filename,
  fm.bucket_id,
  fm.access_count,
  fm.last_accessed,
  fm.created_at,
  EXTRACT(EPOCH FROM (NOW() - fm.last_accessed)) / 3600 as hours_since_last_access
FROM public.file_metadata fm
WHERE fm.access_count > 0
ORDER BY fm.access_count DESC, fm.last_accessed DESC;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE 'Supabase Universal File Hub schema (DEV) created successfully!';
  RAISE NOTICE 'Tables created: users, file_operations, file_metadata';
  RAISE NOTICE 'Indexes created: 13 indexes for performance';
  RAISE NOTICE 'Functions created: 4 utility functions';
  RAISE NOTICE 'Views created: 2 analytics views';
  RAISE NOTICE 'Development user: dev@localhost';
  RAISE NOTICE 'Next step: Create storage buckets';
END $$;

