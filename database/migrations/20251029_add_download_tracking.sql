-- Migration: Add Download Tracking and Caching Layer
-- Date: 2025-10-29
-- Phase: Phase 2 MVP - Essential Features

-- ============================================================
-- STEP 1: Extend provider_file_uploads table
-- ============================================================

-- Add download tracking columns
ALTER TABLE provider_file_uploads 
ADD COLUMN IF NOT EXISTS download_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_downloaded_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS cache_path VARCHAR(500),
ADD COLUMN IF NOT EXISTS cache_expiry TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS cache_size_bytes BIGINT,
ADD COLUMN IF NOT EXISTS cache_hit_count INTEGER DEFAULT 0;

-- Add comments for documentation
COMMENT ON COLUMN provider_file_uploads.download_count IS 'Total number of times this file has been downloaded';
COMMENT ON COLUMN provider_file_uploads.last_downloaded_at IS 'Timestamp of most recent download';
COMMENT ON COLUMN provider_file_uploads.cache_path IS 'Local cache file path (if cached)';
COMMENT ON COLUMN provider_file_uploads.cache_expiry IS 'When the local cache expires';
COMMENT ON COLUMN provider_file_uploads.cache_size_bytes IS 'Size of cached file in bytes';
COMMENT ON COLUMN provider_file_uploads.cache_hit_count IS 'Number of cache hits (downloads served from cache)';

-- ============================================================
-- STEP 2: Create file_download_history table
-- ============================================================

CREATE TABLE IF NOT EXISTS file_download_history (
    id SERIAL PRIMARY KEY,
    provider_file_id VARCHAR(255) NOT NULL 
        REFERENCES provider_file_uploads(provider_file_id) ON DELETE CASCADE,
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    downloaded_by VARCHAR(100),
    downloaded_by_type VARCHAR(20),  -- 'agent', 'user', 'system'
    destination_path VARCHAR(500),
    download_duration_ms INTEGER,
    file_size_bytes BIGINT,
    cache_hit BOOLEAN DEFAULT FALSE,
    provider_used VARCHAR(50),  -- 'kimi', 'supabase', 'glm'
    cache_source VARCHAR(20),  -- 'local', 'supabase', 'origin'
    error_count INTEGER DEFAULT 0,
    download_speed_mbps DECIMAL(10,2)
);

-- Add comments
COMMENT ON TABLE file_download_history IS 'Tracks all file download events with performance metrics';
COMMENT ON COLUMN file_download_history.cache_hit IS 'Whether download was served from cache';
COMMENT ON COLUMN file_download_history.provider_used IS 'Which provider served the download';
COMMENT ON COLUMN file_download_history.cache_source IS 'Source of the file (local cache, supabase, or origin provider)';
COMMENT ON COLUMN file_download_history.error_count IS 'Number of retry attempts before success';

-- ============================================================
-- STEP 3: Create indexes for performance
-- ============================================================

-- Index for file_download_history queries
CREATE INDEX IF NOT EXISTS idx_download_history_file_id 
    ON file_download_history(provider_file_id);

CREATE INDEX IF NOT EXISTS idx_download_history_timestamp 
    ON file_download_history(downloaded_at DESC);

CREATE INDEX IF NOT EXISTS idx_download_history_cache_hit 
    ON file_download_history(cache_hit, downloaded_at DESC);

CREATE INDEX IF NOT EXISTS idx_download_history_provider 
    ON file_download_history(provider_used, downloaded_at DESC);

-- Index for provider_file_uploads cache queries
CREATE INDEX IF NOT EXISTS idx_provider_files_cache_expiry 
    ON provider_file_uploads(cache_expiry) 
    WHERE cache_expiry IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_provider_files_last_downloaded 
    ON provider_file_uploads(last_downloaded_at DESC) 
    WHERE last_downloaded_at IS NOT NULL;

-- ============================================================
-- STEP 4: Create cache_metadata table (Phase 2.1 - Important)
-- ============================================================

CREATE TABLE IF NOT EXISTS cache_metadata (
    id SERIAL PRIMARY KEY,
    provider_file_id VARCHAR(255) NOT NULL 
        REFERENCES provider_file_uploads(provider_file_id) ON DELETE CASCADE,
    cache_location VARCHAR(20) NOT NULL,  -- 'local', 'supabase'
    cache_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    file_size_bytes BIGINT,
    checksum VARCHAR(64),  -- SHA256 for integrity verification
    expiry_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Add comments
COMMENT ON TABLE cache_metadata IS 'Tracks cache entries across local and Supabase storage';
COMMENT ON COLUMN cache_metadata.cache_location IS 'Where the file is cached (local or supabase)';
COMMENT ON COLUMN cache_metadata.checksum IS 'SHA256 hash for integrity verification';
COMMENT ON COLUMN cache_metadata.is_active IS 'Whether cache entry is still valid';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cache_metadata_file_id 
    ON cache_metadata(provider_file_id);

CREATE INDEX IF NOT EXISTS idx_cache_metadata_expiry 
    ON cache_metadata(expiry_at) 
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_cache_metadata_active 
    ON cache_metadata(is_active, last_accessed_at DESC);

CREATE INDEX IF NOT EXISTS idx_cache_metadata_location 
    ON cache_metadata(cache_location, is_active);

-- ============================================================
-- STEP 5: Create helper functions
-- ============================================================

-- Function to update download statistics
CREATE OR REPLACE FUNCTION update_download_stats(
    p_file_id VARCHAR(255),
    p_cache_hit BOOLEAN DEFAULT FALSE
) RETURNS VOID AS $$
BEGIN
    UPDATE provider_file_uploads
    SET 
        download_count = download_count + 1,
        last_downloaded_at = NOW(),
        cache_hit_count = CASE 
            WHEN p_cache_hit THEN cache_hit_count + 1 
            ELSE cache_hit_count 
        END
    WHERE provider_file_id = p_file_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_download_stats IS 'Updates download statistics for a file';

-- Function to cleanup expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache() RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Mark expired cache entries as inactive
    UPDATE cache_metadata
    SET is_active = FALSE
    WHERE expiry_at < NOW() AND is_active = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Clear cache paths from provider_file_uploads
    UPDATE provider_file_uploads
    SET 
        cache_path = NULL,
        cache_expiry = NULL,
        cache_size_bytes = NULL
    WHERE cache_expiry < NOW();
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_cache IS 'Marks expired cache entries as inactive and clears cache paths';

-- ============================================================
-- STEP 6: Create views for analytics
-- ============================================================

-- View for download statistics
CREATE OR REPLACE VIEW download_statistics AS
SELECT 
    pfu.provider_file_id,
    pfu.file_path,
    pfu.provider,
    pfu.download_count,
    pfu.cache_hit_count,
    CASE 
        WHEN pfu.download_count > 0 
        THEN ROUND((pfu.cache_hit_count::DECIMAL / pfu.download_count) * 100, 2)
        ELSE 0 
    END AS cache_hit_rate_percent,
    pfu.last_downloaded_at,
    pfu.cache_expiry,
    COUNT(fdh.id) AS total_download_events,
    AVG(fdh.download_duration_ms) AS avg_download_duration_ms,
    AVG(fdh.download_speed_mbps) AS avg_download_speed_mbps
FROM provider_file_uploads pfu
LEFT JOIN file_download_history fdh ON pfu.provider_file_id = fdh.provider_file_id
GROUP BY 
    pfu.provider_file_id,
    pfu.file_path,
    pfu.provider,
    pfu.download_count,
    pfu.cache_hit_count,
    pfu.last_downloaded_at,
    pfu.cache_expiry;

COMMENT ON VIEW download_statistics IS 'Aggregated download statistics per file';

-- View for cache effectiveness
CREATE OR REPLACE VIEW cache_effectiveness AS
SELECT 
    DATE_TRUNC('day', downloaded_at) AS date,
    provider_used,
    COUNT(*) AS total_downloads,
    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) AS cache_hits,
    SUM(CASE WHEN NOT cache_hit THEN 1 ELSE 0 END) AS cache_misses,
    ROUND(
        (SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
        2
    ) AS cache_hit_rate_percent,
    AVG(download_duration_ms) AS avg_duration_ms,
    AVG(download_speed_mbps) AS avg_speed_mbps
FROM file_download_history
GROUP BY DATE_TRUNC('day', downloaded_at), provider_used
ORDER BY date DESC, provider_used;

COMMENT ON VIEW cache_effectiveness IS 'Daily cache effectiveness metrics by provider';

-- ============================================================
-- STEP 7: Grant permissions (if needed)
-- ============================================================

-- Grant permissions to service role
-- GRANT ALL ON file_download_history TO service_role;
-- GRANT ALL ON cache_metadata TO service_role;
-- GRANT EXECUTE ON FUNCTION update_download_stats TO service_role;
-- GRANT EXECUTE ON FUNCTION cleanup_expired_cache TO service_role;

-- ============================================================
-- Migration Complete
-- ============================================================

