-- File Management Enhancements Migration
-- Date: 2025-11-02
-- Purpose: Add deduplication, registry, health checks, lifecycle sync, recovery, and audit trail

-- ============================================================================
-- 1. FILE DEDUPLICATION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_hashes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    original_file_id UUID REFERENCES file_uploads(id) ON DELETE CASCADE,
    file_size BIGINT NOT NULL,
    content_type VARCHAR(255),
    duplicate_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_file_hashes_hash ON file_hashes(file_hash);
CREATE INDEX idx_file_hashes_original_file_id ON file_hashes(original_file_id);

-- ============================================================================
-- 2. CROSS-PLATFORM FILE REGISTRY
-- ============================================================================

CREATE TABLE IF NOT EXISTS platform_file_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES file_uploads(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'kimi', 'glm'
    platform_file_id VARCHAR(255) NOT NULL,
    platform_url TEXT,
    platform_metadata JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'deleted', 'archived', 'error'
    last_verified TIMESTAMP WITH TIME ZONE,
    verification_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(platform, platform_file_id)
);

CREATE INDEX idx_platform_registry_file_id ON platform_file_registry(file_id);
CREATE INDEX idx_platform_registry_platform ON platform_file_registry(platform);
CREATE INDEX idx_platform_registry_status ON platform_file_registry(status);

-- ============================================================================
-- 3. FILE HEALTH CHECKS
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_health_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registry_id UUID REFERENCES platform_file_registry(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- 'healthy', 'unhealthy', 'error', 'timeout'
    error_message TEXT,
    error_code VARCHAR(50),
    response_time_ms INTEGER,
    http_status_code INTEGER,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_health_checks_registry_id ON file_health_checks(registry_id);
CREATE INDEX idx_health_checks_status ON file_health_checks(status);
CREATE INDEX idx_health_checks_checked_at ON file_health_checks(checked_at DESC);

-- ============================================================================
-- 4. FILE LIFECYCLE SYNC
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_lifecycle_sync (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES file_uploads(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    local_status VARCHAR(50) NOT NULL, -- 'active', 'archived', 'deleted'
    platform_status VARCHAR(50), -- 'active', 'archived', 'deleted', 'unknown'
    sync_status VARCHAR(50) DEFAULT 'pending', -- 'synced', 'pending', 'error', 'conflict'
    sync_error TEXT,
    last_sync_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    next_sync_at TIMESTAMP WITH TIME ZONE,
    sync_attempt_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_lifecycle_sync_file_id ON file_lifecycle_sync(file_id);
CREATE INDEX idx_lifecycle_sync_platform ON file_lifecycle_sync(platform);
CREATE INDEX idx_lifecycle_sync_status ON file_lifecycle_sync(sync_status);
CREATE INDEX idx_lifecycle_sync_next_sync ON file_lifecycle_sync(next_sync_at);

-- ============================================================================
-- 5. ERROR RECOVERY TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_recovery_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES file_uploads(id) ON DELETE CASCADE,
    operation VARCHAR(100) NOT NULL, -- 'upload', 'download', 'delete', 'verify'
    platform VARCHAR(50),
    attempt_number INTEGER NOT NULL DEFAULT 1,
    error_message TEXT,
    error_code VARCHAR(50),
    recovery_strategy VARCHAR(100), -- 'exponential_backoff', 'circuit_breaker', 'fallback'
    status VARCHAR(50) DEFAULT 'pending', -- 'success', 'failed', 'pending', 'abandoned'
    next_retry_at TIMESTAMP WITH TIME ZONE,
    retry_delay_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_recovery_file_id ON file_recovery_attempts(file_id);
CREATE INDEX idx_recovery_status ON file_recovery_attempts(status);
CREATE INDEX idx_recovery_next_retry ON file_recovery_attempts(next_retry_at);
CREATE INDEX idx_recovery_operation ON file_recovery_attempts(operation);

-- ============================================================================
-- 6. FILE ACCESS AUDIT TRAIL
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES file_uploads(id) ON DELETE CASCADE,
    operation VARCHAR(100) NOT NULL, -- 'upload', 'download', 'delete', 'access', 'verify', 'deduplicate'
    platform VARCHAR(50),
    user_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    operation_details JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL, -- 'success', 'failed', 'partial'
    error_message TEXT,
    error_code VARCHAR(50),
    duration_ms INTEGER,
    bytes_transferred BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_file_id ON file_audit_trail(file_id);
CREATE INDEX idx_audit_operation ON file_audit_trail(operation);
CREATE INDEX idx_audit_status ON file_audit_trail(status);
CREATE INDEX idx_audit_created_at ON file_audit_trail(created_at DESC);
CREATE INDEX idx_audit_user_id ON file_audit_trail(user_id);

-- ============================================================================
-- 7. MODIFICATIONS TO EXISTING file_uploads TABLE
-- ============================================================================

-- Add new columns to file_uploads table
ALTER TABLE file_uploads 
    ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64),
    ADD COLUMN IF NOT EXISTS is_duplicate BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS original_file_id UUID REFERENCES file_uploads(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS health_status VARCHAR(50) DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS last_health_check TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS deduplication_checked BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_file_uploads_hash ON file_uploads(file_hash);
CREATE INDEX IF NOT EXISTS idx_file_uploads_is_duplicate ON file_uploads(is_duplicate);
CREATE INDEX IF NOT EXISTS idx_file_uploads_health_status ON file_uploads(health_status);

-- ============================================================================
-- 8. HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_file_hashes_updated_at BEFORE UPDATE ON file_hashes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_registry_updated_at BEFORE UPDATE ON platform_file_registry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lifecycle_sync_updated_at BEFORE UPDATE ON file_lifecycle_sync
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 9. COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE file_hashes IS 'Tracks file content hashes for deduplication';
COMMENT ON TABLE platform_file_registry IS 'Cross-platform file metadata registry for Kimi and GLM';
COMMENT ON TABLE file_health_checks IS 'Periodic health check results for files on platforms';
COMMENT ON TABLE file_lifecycle_sync IS 'Synchronization status between local and platform lifecycles';
COMMENT ON TABLE file_recovery_attempts IS 'Error recovery tracking with retry strategies';
COMMENT ON TABLE file_audit_trail IS 'Comprehensive audit log for all file operations';

-- ============================================================================
-- 10. INITIAL DATA / CLEANUP
-- ============================================================================

-- Clean up any orphaned records (optional, for safety)
-- This can be uncommented if needed during migration
-- DELETE FROM file_hashes WHERE original_file_id NOT IN (SELECT id FROM file_uploads);

