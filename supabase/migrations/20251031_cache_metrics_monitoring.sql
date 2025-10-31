-- Cache Metrics Monitoring System
-- Date: 2025-10-31
-- Purpose: Week 2-3 Monitoring Phase - Baseline metrics collection and AI Auditor integration
-- EXAI Consultation ID: c78bd85e-470a-4abb-8d0e-aeed72fab0a0

-- ============================================================================
-- CACHE METRICS RAW EVENTS TABLE
-- ============================================================================
-- Stores individual cache events for detailed analysis
-- Retention: 7 days (raw data), then aggregated and archived

CREATE TABLE IF NOT EXISTS public.cache_metrics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- Cache operation details
  cache_key TEXT NOT NULL,
  operation_type TEXT NOT NULL CHECK (operation_type IN ('hit', 'miss', 'set', 'evict', 'error')),
  implementation_type TEXT NOT NULL CHECK (implementation_type IN ('legacy', 'new')),
  
  -- Performance metrics
  response_time_ms INTEGER,
  cache_size INTEGER,
  
  -- Error tracking
  error_type TEXT,
  error_message TEXT,
  
  -- Metadata
  metadata JSONB DEFAULT '{}'::jsonb,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  
  -- Indexes for fast queries
  CONSTRAINT valid_response_time CHECK (response_time_ms >= 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cache_metrics_timestamp 
  ON public.cache_metrics(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_cache_metrics_operation 
  ON public.cache_metrics(operation_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_cache_metrics_implementation 
  ON public.cache_metrics(implementation_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_cache_metrics_errors 
  ON public.cache_metrics(operation_type, timestamp DESC) 
  WHERE operation_type = 'error';

-- Add table comment
COMMENT ON TABLE public.cache_metrics IS 'Raw cache events for detailed performance analysis (7-day retention)';

-- ============================================================================
-- CACHE METRICS AGGREGATED (1-MINUTE WINDOWS)
-- ============================================================================
-- Pre-aggregated metrics for faster dashboard queries
-- Retention: 30 days

CREATE TABLE IF NOT EXISTS public.cache_metrics_1min (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- Time window
  minute_window TIMESTAMPTZ NOT NULL,
  implementation_type TEXT NOT NULL CHECK (implementation_type IN ('legacy', 'new')),
  
  -- Aggregated metrics
  total_operations INTEGER NOT NULL DEFAULT 0,
  hits INTEGER NOT NULL DEFAULT 0,
  misses INTEGER NOT NULL DEFAULT 0,
  sets INTEGER NOT NULL DEFAULT 0,
  evictions INTEGER NOT NULL DEFAULT 0,
  errors INTEGER NOT NULL DEFAULT 0,
  
  -- Performance metrics
  avg_response_time_ms NUMERIC(10, 2),
  p50_response_time_ms INTEGER,
  p95_response_time_ms INTEGER,
  p99_response_time_ms INTEGER,
  max_response_time_ms INTEGER,
  
  -- Cache size metrics
  avg_cache_size INTEGER,
  max_cache_size INTEGER,
  
  -- Calculated metrics
  hit_rate NUMERIC(5, 2), -- Percentage (0.00 to 100.00)
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Unique constraint to prevent duplicates
  CONSTRAINT unique_minute_window UNIQUE (minute_window, implementation_type)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cache_metrics_1min_window 
  ON public.cache_metrics_1min(minute_window DESC);

CREATE INDEX IF NOT EXISTS idx_cache_metrics_1min_impl 
  ON public.cache_metrics_1min(implementation_type, minute_window DESC);

-- Add table comment
COMMENT ON TABLE public.cache_metrics_1min IS 'Pre-aggregated cache metrics (1-minute windows, 30-day retention)';

-- ============================================================================
-- CACHE METRICS AGGREGATED (1-HOUR WINDOWS)
-- ============================================================================
-- Long-term trend analysis
-- Retention: 1 year

CREATE TABLE IF NOT EXISTS public.cache_metrics_1hour (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- Time window
  hour_window TIMESTAMPTZ NOT NULL,
  implementation_type TEXT NOT NULL CHECK (implementation_type IN ('legacy', 'new')),
  
  -- Aggregated metrics (same structure as 1min)
  total_operations INTEGER NOT NULL DEFAULT 0,
  hits INTEGER NOT NULL DEFAULT 0,
  misses INTEGER NOT NULL DEFAULT 0,
  sets INTEGER NOT NULL DEFAULT 0,
  evictions INTEGER NOT NULL DEFAULT 0,
  errors INTEGER NOT NULL DEFAULT 0,
  
  -- Performance metrics
  avg_response_time_ms NUMERIC(10, 2),
  p50_response_time_ms INTEGER,
  p95_response_time_ms INTEGER,
  p99_response_time_ms INTEGER,
  max_response_time_ms INTEGER,
  
  -- Cache size metrics
  avg_cache_size INTEGER,
  max_cache_size INTEGER,
  
  -- Calculated metrics
  hit_rate NUMERIC(5, 2),
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Unique constraint
  CONSTRAINT unique_hour_window UNIQUE (hour_window, implementation_type)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cache_metrics_1hour_window 
  ON public.cache_metrics_1hour(hour_window DESC);

CREATE INDEX IF NOT EXISTS idx_cache_metrics_1hour_impl 
  ON public.cache_metrics_1hour(implementation_type, hour_window DESC);

-- Add table comment
COMMENT ON TABLE public.cache_metrics_1hour IS 'Pre-aggregated cache metrics (1-hour windows, 1-year retention)';

-- ============================================================================
-- CACHE BASELINE METRICS
-- ============================================================================
-- Stores baseline performance metrics for comparison
-- Used by AI Auditor for anomaly detection

CREATE TABLE IF NOT EXISTS public.cache_baseline_metrics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- Baseline identification
  implementation_type TEXT NOT NULL CHECK (implementation_type IN ('legacy', 'new')),
  baseline_period_start TIMESTAMPTZ NOT NULL,
  baseline_period_end TIMESTAMPTZ NOT NULL,
  
  -- Baseline metrics
  baseline_hit_rate NUMERIC(5, 2) NOT NULL,
  baseline_avg_response_time_ms NUMERIC(10, 2) NOT NULL,
  baseline_p95_response_time_ms INTEGER NOT NULL,
  baseline_error_rate NUMERIC(5, 2) NOT NULL,
  
  -- Statistical metrics for anomaly detection
  hit_rate_stddev NUMERIC(5, 2),
  response_time_stddev NUMERIC(10, 2),
  
  -- Metadata
  sample_size INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Only one active baseline per implementation
  CONSTRAINT unique_active_baseline UNIQUE (implementation_type, is_active) 
    WHERE is_active = TRUE
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_cache_baseline_active 
  ON public.cache_baseline_metrics(implementation_type, is_active) 
  WHERE is_active = TRUE;

-- Add table comment
COMMENT ON TABLE public.cache_baseline_metrics IS 'Baseline performance metrics for AI Auditor anomaly detection';

-- ============================================================================
-- AI AUDITOR OBSERVATIONS
-- ============================================================================
-- Stores AI Auditor observations and alerts for cache monitoring

CREATE TABLE IF NOT EXISTS public.cache_auditor_observations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- Observation details
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
  category TEXT NOT NULL CHECK (category IN ('performance', 'reliability', 'capacity', 'anomaly')),
  
  -- Observation content
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  recommendation TEXT,
  
  -- Related metrics
  implementation_type TEXT CHECK (implementation_type IN ('legacy', 'new')),
  metric_name TEXT,
  metric_value NUMERIC,
  baseline_value NUMERIC,
  deviation_percentage NUMERIC(5, 2),
  
  -- Metadata
  metadata JSONB DEFAULT '{}'::jsonb,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_at TIMESTAMPTZ,
  acknowledged_by TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cache_auditor_timestamp 
  ON public.cache_auditor_observations(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_cache_auditor_severity 
  ON public.cache_auditor_observations(severity, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_cache_auditor_unacknowledged 
  ON public.cache_auditor_observations(acknowledged, timestamp DESC) 
  WHERE acknowledged = FALSE;

-- Add table comment
COMMENT ON TABLE public.cache_auditor_observations IS 'AI Auditor observations and alerts for cache monitoring';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate hit rate from aggregated metrics
CREATE OR REPLACE FUNCTION calculate_hit_rate(hits INTEGER, misses INTEGER)
RETURNS NUMERIC(5, 2) AS $$
BEGIN
  IF (hits + misses) = 0 THEN
    RETURN 0.00;
  END IF;
  RETURN ROUND((hits::NUMERIC / (hits + misses)::NUMERIC) * 100, 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get current cache performance summary
CREATE OR REPLACE FUNCTION get_cache_performance_summary(
  p_implementation_type TEXT DEFAULT NULL,
  p_time_window INTERVAL DEFAULT '1 hour'::INTERVAL
)
RETURNS TABLE (
  implementation_type TEXT,
  total_operations BIGINT,
  hit_rate NUMERIC,
  avg_response_time_ms NUMERIC,
  error_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    cm.implementation_type,
    COUNT(*)::BIGINT as total_operations,
    calculate_hit_rate(
      COUNT(*) FILTER (WHERE cm.operation_type = 'hit')::INTEGER,
      COUNT(*) FILTER (WHERE cm.operation_type = 'miss')::INTEGER
    ) as hit_rate,
    AVG(cm.response_time_ms) as avg_response_time_ms,
    COUNT(*) FILTER (WHERE cm.operation_type = 'error')::BIGINT as error_count
  FROM public.cache_metrics cm
  WHERE cm.timestamp >= NOW() - p_time_window
    AND (p_implementation_type IS NULL OR cm.implementation_type = p_implementation_type)
  GROUP BY cm.implementation_type;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- REALTIME PUBLICATION
-- ============================================================================
-- Enable Supabase Realtime for cache metrics broadcasting

-- Add tables to realtime publication
ALTER PUBLICATION supabase_realtime ADD TABLE public.cache_metrics_1min;
ALTER PUBLICATION supabase_realtime ADD TABLE public.cache_auditor_observations;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE 'Cache Metrics Monitoring System created successfully!';
  RAISE NOTICE 'Tables created: cache_metrics, cache_metrics_1min, cache_metrics_1hour, cache_baseline_metrics, cache_auditor_observations';
  RAISE NOTICE 'Indexes created: 12 indexes for performance';
  RAISE NOTICE 'Functions created: 2 helper functions';
  RAISE NOTICE 'Realtime enabled: cache_metrics_1min, cache_auditor_observations';
  RAISE NOTICE 'Next step: Deploy Supabase Edge Function for metrics aggregation';
END $$;

