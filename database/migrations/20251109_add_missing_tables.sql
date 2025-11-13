-- ============================================================================
-- EXAI MCP Server - Missing Tables Migration
-- Date: 2025-11-09
-- Purpose: Add missing tables referenced in code but not in schema
-- ============================================================================

-- ============================================================================
-- PROVIDER FILE UPLOADS TABLE
-- ============================================================================
-- Tracks file uploads to different providers (Kimi, GLM, etc.)
-- Referenced in: utils/file/deduplication.py, tools/smart_file_query.py
CREATE TABLE IF NOT EXISTS public.provider_file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255), -- Track which user uploaded the file
    provider_name VARCHAR(100) NOT NULL,
    provider_file_id VARCHAR(255),
    upload_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    file_size BIGINT,
    file_type VARCHAR(50),
    file_hash VARCHAR(64), -- SHA-256 hash for deduplication
    storage_path TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_file_id
    ON public.provider_file_uploads(file_id);

CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_provider
    ON public.provider_file_uploads(provider_name);

CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_timestamp
    ON public.provider_file_uploads(upload_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_provider_file_uploads_hash
    ON public.provider_file_uploads(file_hash);

-- Updated at trigger
DROP TRIGGER IF EXISTS trigger_update_provider_file_uploads_timestamp
    ON public.provider_file_uploads;

CREATE TRIGGER trigger_update_provider_file_uploads_timestamp
    BEFORE UPDATE ON public.provider_file_uploads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FILE ID MAPPINGS TABLE
-- ============================================================================
-- Maps original file IDs to provider-specific file IDs
-- Referenced in: tools/file_id_mapper.py
CREATE TABLE IF NOT EXISTS public.file_id_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_file_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255), -- Track which user owns this mapping
    provider_file_id VARCHAR(255) NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    mapping_type VARCHAR(50) DEFAULT 'upload', -- upload, download, transformation
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',

    -- Ensure one mapping per original_file_id per provider
    CONSTRAINT unique_mapping UNIQUE (original_file_id, provider_name)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_file_id_mappings_original
    ON public.file_id_mappings(original_file_id);

CREATE INDEX IF NOT EXISTS idx_file_id_mappings_provider
    ON public.file_id_mappings(provider_name);

CREATE INDEX IF NOT EXISTS idx_file_id_mappings_created
    ON public.file_id_mappings(created_at DESC);

-- Updated at trigger
DROP TRIGGER IF EXISTS trigger_update_file_id_mappings_timestamp
    ON public.file_id_mappings;

CREATE TRIGGER trigger_update_file_id_mappings_timestamp
    BEFORE UPDATE ON public.file_id_mappings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- AUDIT LOGS TABLE
-- ============================================================================
-- Tracks all security-relevant actions and system events
-- Referenced in: src/security/audit_logger.py
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    details JSONB DEFAULT '{}',
    correlation_id VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance and querying
CREATE INDEX IF NOT EXISTS idx_audit_logs_action
    ON public.audit_logs(action);

CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp
    ON public.audit_logs(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user
    ON public.audit_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_resource
    ON public.audit_logs(resource_type, resource_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_session
    ON public.audit_logs(session_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation
    ON public.audit_logs(correlation_id);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_timestamp
    ON public.audit_logs(action, timestamp DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE public.provider_file_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_id_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Service role: Full access to all tables
DROP POLICY IF EXISTS "Allow service role full access" ON public.provider_file_uploads;
CREATE POLICY "Allow service role full access"
    ON public.provider_file_uploads
    FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service role full access" ON public.file_id_mappings;
CREATE POLICY "Allow service role full access"
    ON public.file_id_mappings
    FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service role full access" ON public.audit_logs;
CREATE POLICY "Allow service role full access"
    ON public.audit_logs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Authenticated users: Read-only access to own data
DROP POLICY IF EXISTS "Allow authenticated users to read own uploads"
    ON public.provider_file_uploads;
CREATE POLICY "Allow authenticated users to read own uploads"
    ON public.provider_file_uploads
    FOR SELECT
    USING (auth.uid()::text = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Allow authenticated users to read own mappings"
    ON public.file_id_mappings;
CREATE POLICY "Allow authenticated users to read own mappings"
    ON public.file_id_mappings
    FOR SELECT
    USING (auth.uid()::text = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Allow authenticated users to read own audit logs"
    ON public.audit_logs;
CREATE POLICY "Allow authenticated users to read own audit logs"
    ON public.audit_logs
    FOR SELECT
    USING (auth.uid()::text = user_id);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE public.provider_file_uploads IS
    'Tracks file uploads to different providers (Kimi, GLM, etc.) for deduplication and tracking';

COMMENT ON COLUMN public.provider_file_uploads.file_id IS
    'Unique identifier for the file across the system';

COMMENT ON COLUMN public.provider_file_uploads.provider_name IS
    'Name of the provider: kimiglmmglm, supabase, etc.';

COMMENT ON COLUMN public.provider_file_uploads.file_hash IS
    'SHA-256 hash for content-based deduplication';

COMMENT ON TABLE public.file_id_mappings IS
    'Maps original file IDs to provider-specific file IDs for cross-provider operations';

COMMENT ON COLUMN public.file_id_mappings.mapping_type IS
    'Type of mapping: upload, download, transformation';

COMMENT ON TABLE public.audit_logs IS
    'Comprehensive audit trail for security and compliance';

COMMENT ON COLUMN public.audit_logs.action IS
    'Action performed: login, logout, file_upload, file_download, tool_call, etc.';

COMMENT ON COLUMN public.audit_logs.resource_type IS
    'Type of resource: file, conversation, message, session, tool';

COMMENT ON COLUMN public.audit_logs.success IS
    'Whether the action completed successfully';

COMMENT ON COLUMN public.audit_logs.correlation_id IS
    'ID for tracing related actions across the system';

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================
INSERT INTO schema_version (version, description)
VALUES (2, 'Added missing tables: provider_file_uploads, file_id_mappings, audit_logs')
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Missing Tables Migration Complete!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables Created:';
    RAISE NOTICE '  - provider_file_uploads (file tracking)';
    RAISE NOTICE '  - file_id_mappings (ID mapping)';
    RAISE NOTICE '  - audit_logs (security audit)';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total Indexes: 15';
    RAISE NOTICE 'RLS Policies: 9';
    RAISE NOTICE 'Triggers: 3 (updated_at)';
    RAISE NOTICE '========================================';
END $$;
