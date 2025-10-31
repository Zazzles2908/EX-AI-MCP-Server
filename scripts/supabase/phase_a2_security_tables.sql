-- Phase A2 Security Tables
-- Created: 2025-10-30
-- Purpose: Add security infrastructure for rate limiting and audit logging

-- ============================================================================
-- AUDIT LOGS TABLE
-- ============================================================================
-- Tracks all file operations for security auditing and compliance

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    application_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    operation VARCHAR(50) NOT NULL,  -- upload, download, delete, query
    provider VARCHAR(50) NOT NULL,   -- kimi, glm, etc.
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    additional_data JSONB,           -- Flexible metadata storage
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_application_id ON audit_logs(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_operation ON audit_logs(operation);
CREATE INDEX IF NOT EXISTS idx_audit_logs_provider ON audit_logs(provider);

-- Add comment
COMMENT ON TABLE audit_logs IS 'Security audit trail for all file operations (Phase A2)';

-- ============================================================================
-- RATE LIMITS TABLE (Optional - Redis is primary, this is backup/config)
-- ============================================================================
-- Stores application-specific rate limit overrides
-- Redis handles the actual rate limiting, this table stores configuration

CREATE TABLE IF NOT EXISTS rate_limit_config (
    id BIGSERIAL PRIMARY KEY,
    application_id VARCHAR(255) NOT NULL UNIQUE,
    requests_per_minute INTEGER DEFAULT 60,
    files_per_hour INTEGER DEFAULT 100,
    mb_per_day INTEGER DEFAULT 1000,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_rate_limit_config_application_id ON rate_limit_config(application_id);

-- Add comment
COMMENT ON TABLE rate_limit_config IS 'Application-specific rate limit configuration (Phase A2)';

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
-- Grant necessary permissions for service role

-- Audit logs: service role can insert and select
GRANT SELECT, INSERT ON audit_logs TO service_role;
GRANT USAGE, SELECT ON SEQUENCE audit_logs_id_seq TO service_role;

-- Rate limit config: service role can read and update
GRANT SELECT, INSERT, UPDATE ON rate_limit_config TO service_role;
GRANT USAGE, SELECT ON SEQUENCE rate_limit_config_id_seq TO service_role;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Enable RLS for security

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rate_limit_config ENABLE ROW LEVEL SECURITY;

-- Policy: Service role can do everything
CREATE POLICY IF NOT EXISTS "Service role full access to audit_logs"
    ON audit_logs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY IF NOT EXISTS "Service role full access to rate_limit_config"
    ON rate_limit_config
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================
-- Insert default rate limit config for test applications

INSERT INTO rate_limit_config (application_id, requests_per_minute, files_per_hour, mb_per_day)
VALUES 
    ('EX-AI-MCP-Server', 120, 200, 2000),  -- Higher limits for main app
    ('Personal_AI_Agent', 60, 100, 1000),  -- Default limits
    ('test-app', 30, 50, 500)              -- Lower limits for test app
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify the tables were created successfully

-- Check audit_logs table
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'audit_logs'
ORDER BY ordinal_position;

-- Check rate_limit_config table
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'rate_limit_config'
ORDER BY ordinal_position;

-- Check indexes
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('audit_logs', 'rate_limit_config')
ORDER BY tablename, indexname;

-- ============================================================================
-- CLEANUP (if needed)
-- ============================================================================
-- Uncomment these lines to drop the tables (use with caution!)

-- DROP TABLE IF EXISTS audit_logs CASCADE;
-- DROP TABLE IF NOT EXISTS rate_limit_config CASCADE;

