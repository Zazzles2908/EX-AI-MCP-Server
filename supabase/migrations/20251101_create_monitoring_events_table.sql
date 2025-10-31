-- Create monitoring_events table in monitoring schema
-- Date: 2025-11-01
-- Purpose: Phase 2 - Supabase Realtime Migration
-- EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745

-- ============================================================================
-- MONITORING SCHEMA SETUP
-- ============================================================================
-- Ensure the monitoring schema exists
CREATE SCHEMA IF NOT EXISTS monitoring;

-- ============================================================================
-- MONITORING_EVENTS TABLE
-- ============================================================================
-- Stores unified monitoring events for real-time dashboard broadcasting
-- This table is the central hub for all monitoring events from adapters

CREATE TABLE IF NOT EXISTS monitoring.monitoring_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event identification
    event_type VARCHAR(50) NOT NULL,
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Source identification
    source VARCHAR(100) NOT NULL,
    
    -- Event data (flexible JSONB for different event types)
    data JSONB NOT NULL,
    
    -- Additional metadata
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
-- Create indexes for common query patterns

CREATE INDEX IF NOT EXISTS idx_monitoring_events_timestamp 
    ON monitoring.monitoring_events(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_monitoring_events_event_type 
    ON monitoring.monitoring_events(event_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_monitoring_events_source 
    ON monitoring.monitoring_events(source, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_monitoring_events_created_at 
    ON monitoring.monitoring_events(created_at DESC);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_monitoring_events_type_source_time 
    ON monitoring.monitoring_events(event_type, source, timestamp DESC);

-- ============================================================================
-- REALTIME PUBLICATION
-- ============================================================================
-- Enable Supabase Realtime for real-time dashboard updates

ALTER PUBLICATION supabase_realtime ADD TABLE monitoring.monitoring_events;

-- ============================================================================
-- TABLE COMMENTS
-- ============================================================================
-- Document the table purpose

COMMENT ON TABLE monitoring.monitoring_events IS 
    'Unified monitoring events for real-time dashboard broadcasting. Stores events from WebSocket, Realtime, and other adapters.';

COMMENT ON COLUMN monitoring.monitoring_events.event_type IS 
    'Type of monitoring event (e.g., cache_metrics, session_metrics, health_check)';

COMMENT ON COLUMN monitoring.monitoring_events.source IS 
    'Source of the event (e.g., websocket, realtime, redis, monitoring_endpoint)';

COMMENT ON COLUMN monitoring.monitoring_events.data IS 
    'Event-specific data in JSONB format for flexibility';

COMMENT ON COLUMN monitoring.monitoring_events.metadata IS 
    'Additional metadata about the event (broadcast_mode, adapter_type, etc.)';

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'monitoring.monitoring_events table created successfully!';
    RAISE NOTICE 'Schema: monitoring';
    RAISE NOTICE 'Table: monitoring_events';
    RAISE NOTICE 'Indexes: 5 indexes for performance';
    RAISE NOTICE 'Realtime: Enabled for real-time dashboard updates';
    RAISE NOTICE 'Next step: Update Realtime adapter to use monitoring schema';
END $$;

