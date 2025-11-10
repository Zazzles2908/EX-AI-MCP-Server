-- PHASE 4 IMPLEMENTATION (2025-11-01): Unified Metrics RPC Functions
-- EXAI Consultation: 63c00b70-364b-4351-bf6c-5a105e553dce
--
-- This migration creates PostgreSQL RPC functions to replace Edge Functions
-- for metrics aggregation. Provides native database aggregation with better
-- performance and no timeout issues.
--
-- Architecture:
-- UnifiedMetricsCollector → aggregate_metrics() RPC → monitoring.metrics_raw
--                                                    → Materialized Views
-- Dashboard ← RPC functions ← Materialized Views

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
CREATE INDEX IF NOT EXISTS idx_metrics_raw_type ON monitoring.metrics_raw(type);
CREATE INDEX IF NOT EXISTS idx_metrics_raw_timestamp ON monitoring.metrics_raw(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_raw_created_at ON monitoring.metrics_raw(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE monitoring.metrics_raw ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role full access
CREATE POLICY IF NOT EXISTS "Service role has full access to metrics_raw"
ON monitoring.metrics_raw
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- ============================================================================
-- RPC FUNCTION: aggregate_metrics
-- ============================================================================
-- Receives metrics from UnifiedMetricsCollector and inserts into raw table
-- Replaces the Edge Function approach with native PostgreSQL
-- ============================================================================

CREATE OR REPLACE FUNCTION monitoring.aggregate_metrics(metrics JSONB)
RETURNS VOID AS $$
BEGIN
    -- Insert raw metrics
    INSERT INTO monitoring.metrics_raw (type, data, timestamp)
    SELECT 
        (value->>'type')::TEXT,
        (value->'data')::JSONB,
        (value->>'timestamp')::TIMESTAMPTZ
    FROM jsonb_array_elements(metrics);
    
    -- Refresh materialized views (if they exist)
    -- Using CONCURRENTLY to avoid locking
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY monitoring.metrics_1min;
    EXCEPTION
        WHEN undefined_table THEN
            -- View doesn't exist yet, skip
            NULL;
    END;
    
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY monitoring.metrics_1hour;
    EXCEPTION
        WHEN undefined_table THEN
            -- View doesn't exist yet, skip
            NULL;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to service role
GRANT EXECUTE ON FUNCTION monitoring.aggregate_metrics(JSONB) TO service_role;

-- ============================================================================
-- MATERIALIZED VIEW: metrics_1min
-- ============================================================================
-- Pre-aggregated metrics at 1-minute granularity
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS monitoring.metrics_1min AS
SELECT 
    date_trunc('minute', timestamp) as minute_window,
    type,
    COUNT(*) as count,
    AVG(COALESCE((data->>'response_time_ms')::int, 0)) as avg_response_time_ms,
    MIN(COALESCE((data->>'response_time_ms')::int, 0)) as min_response_time_ms,
    MAX(COALESCE((data->>'response_time_ms')::int, 0)) as max_response_time_ms,
    SUM(CASE WHEN data->>'success' = 'true' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN data->>'success' = 'false' THEN 1 ELSE 0 END) as error_count
FROM monitoring.metrics_raw
GROUP BY 1, 2;

-- Create unique index for CONCURRENTLY refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_metrics_1min_unique 
ON monitoring.metrics_1min(minute_window, type);

-- ============================================================================
-- MATERIALIZED VIEW: metrics_1hour
-- ============================================================================
-- Pre-aggregated metrics at 1-hour granularity
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS monitoring.metrics_1hour AS
SELECT 
    date_trunc('hour', timestamp) as hour_window,
    type,
    COUNT(*) as count,
    AVG(COALESCE((data->>'response_time_ms')::int, 0)) as avg_response_time_ms,
    MIN(COALESCE((data->>'response_time_ms')::int, 0)) as min_response_time_ms,
    MAX(COALESCE((data->>'response_time_ms')::int, 0)) as max_response_time_ms,
    SUM(CASE WHEN data->>'success' = 'true' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN data->>'success' = 'false' THEN 1 ELSE 0 END) as error_count
FROM monitoring.metrics_raw
GROUP BY 1, 2;

-- Create unique index for CONCURRENTLY refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_metrics_1hour_unique 
ON monitoring.metrics_1hour(hour_window, type);

-- ============================================================================
-- RPC FUNCTION: get_cache_metrics_summary
-- ============================================================================
-- Returns cache metrics summary for dashboard
-- ============================================================================

CREATE OR REPLACE FUNCTION monitoring.get_cache_metrics_summary(time_range TEXT DEFAULT '1hour')
RETURNS TABLE(
    implementation_type TEXT,
    hit_rate NUMERIC,
    total_operations BIGINT,
    avg_response_time_ms NUMERIC
) AS $$
DECLARE
    interval_value INTERVAL;
BEGIN
    -- Convert time_range to interval
    interval_value := CASE time_range
        WHEN '1hour' THEN INTERVAL '1 hour'
        WHEN '24hours' THEN INTERVAL '24 hours'
        WHEN '7days' THEN INTERVAL '7 days'
        ELSE INTERVAL '1 hour'
    END;
    
    RETURN QUERY
    SELECT 
        (data->>'implementation')::TEXT as implementation_type,
        ROUND(
            (SUM(CASE WHEN type = 'cache_hit' THEN 1 ELSE 0 END)::numeric / 
             NULLIF(SUM(CASE WHEN type IN ('cache_hit', 'cache_miss') THEN 1 ELSE 0 END), 0)) * 100,
            2
        ) as hit_rate,
        SUM(CASE WHEN type IN ('cache_hit', 'cache_miss') THEN 1 ELSE 0 END) as total_operations,
        AVG(COALESCE((data->>'response_time_ms')::int, 0)) as avg_response_time_ms
    FROM monitoring.metrics_raw
    WHERE timestamp >= NOW() - interval_value
      AND type IN ('cache_hit', 'cache_miss')
    GROUP BY (data->>'implementation')::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION monitoring.get_cache_metrics_summary(TEXT) TO service_role, anon, authenticated;

-- ============================================================================
-- RPC FUNCTION: get_websocket_metrics_summary
-- ============================================================================
-- Returns WebSocket health metrics summary for dashboard
-- ============================================================================

CREATE OR REPLACE FUNCTION monitoring.get_websocket_metrics_summary(time_range TEXT DEFAULT '1hour')
RETURNS TABLE(
    avg_active_connections NUMERIC,
    total_messages BIGINT,
    error_count BIGINT,
    error_rate NUMERIC
) AS $$
DECLARE
    interval_value INTERVAL;
BEGIN
    interval_value := CASE time_range
        WHEN '1hour' THEN INTERVAL '1 hour'
        WHEN '24hours' THEN INTERVAL '24 hours'
        WHEN '7days' THEN INTERVAL '7 days'
        ELSE INTERVAL '1 hour'
    END;
    
    RETURN QUERY
    SELECT 
        AVG(COALESCE((data->>'active_connections')::int, 0)) as avg_active_connections,
        SUM(COALESCE((data->>'total_messages')::bigint, 0)) as total_messages,
        SUM(COALESCE((data->>'error_count')::bigint, 0)) as error_count,
        ROUND(
            (SUM(COALESCE((data->>'error_count')::bigint, 0))::numeric / 
             NULLIF(SUM(COALESCE((data->>'total_messages')::bigint, 0)), 0)) * 100,
            2
        ) as error_rate
    FROM monitoring.metrics_raw
    WHERE timestamp >= NOW() - interval_value
      AND type = 'websocket_health';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION monitoring.get_websocket_metrics_summary(TEXT) TO service_role, anon, authenticated;

-- ============================================================================
-- RPC FUNCTION: get_connection_metrics_summary
-- ============================================================================
-- Returns connection health metrics summary for dashboard
-- ============================================================================

CREATE OR REPLACE FUNCTION monitoring.get_connection_metrics_summary(time_range TEXT DEFAULT '1hour')
RETURNS TABLE(
    service TEXT,
    total_events BIGINT,
    success_count BIGINT,
    error_count BIGINT,
    success_rate NUMERIC
) AS $$
DECLARE
    interval_value INTERVAL;
BEGIN
    interval_value := CASE time_range
        WHEN '1hour' THEN INTERVAL '1 hour'
        WHEN '24hours' THEN INTERVAL '24 hours'
        WHEN '7days' THEN INTERVAL '7 days'
        ELSE INTERVAL '1 hour'
    END;
    
    RETURN QUERY
    SELECT 
        (data->>'service')::TEXT as service,
        COUNT(*) as total_events,
        SUM(CASE WHEN data->>'success' = 'true' THEN 1 ELSE 0 END) as success_count,
        SUM(CASE WHEN data->>'success' = 'false' THEN 1 ELSE 0 END) as error_count,
        ROUND(
            (SUM(CASE WHEN data->>'success' = 'true' THEN 1 ELSE 0 END)::numeric / 
             NULLIF(COUNT(*), 0)) * 100,
            2
        ) as success_rate
    FROM monitoring.metrics_raw
    WHERE timestamp >= NOW() - interval_value
      AND type = 'connection_event'
    GROUP BY (data->>'service')::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION monitoring.get_connection_metrics_summary(TEXT) TO service_role, anon, authenticated;

-- ============================================================================
-- RPC FUNCTION: get_performance_metrics_summary
-- ============================================================================
-- Returns performance metrics summary for dashboard
-- ============================================================================

CREATE OR REPLACE FUNCTION monitoring.get_performance_metrics_summary(time_range TEXT DEFAULT '1hour')
RETURNS TABLE(
    operation TEXT,
    total_operations BIGINT,
    avg_duration_ms NUMERIC,
    p95_duration_ms NUMERIC,
    success_rate NUMERIC
) AS $$
DECLARE
    interval_value INTERVAL;
BEGIN
    interval_value := CASE time_range
        WHEN '1hour' THEN INTERVAL '1 hour'
        WHEN '24hours' THEN INTERVAL '24 hours'
        WHEN '7days' THEN INTERVAL '7 days'
        ELSE INTERVAL '1 hour'
    END;
    
    RETURN QUERY
    SELECT 
        (data->>'operation')::TEXT as operation,
        COUNT(*) as total_operations,
        AVG(COALESCE((data->>'duration_ms')::int, 0)) as avg_duration_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY COALESCE((data->>'duration_ms')::int, 0)) as p95_duration_ms,
        ROUND(
            (SUM(CASE WHEN data->>'success' = 'true' THEN 1 ELSE 0 END)::numeric / 
             NULLIF(COUNT(*), 0)) * 100,
            2
        ) as success_rate
    FROM monitoring.metrics_raw
    WHERE timestamp >= NOW() - interval_value
      AND type = 'performance'
    GROUP BY (data->>'operation')::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION monitoring.get_performance_metrics_summary(TEXT) TO service_role, anon, authenticated;

