-- Migration: Add monitoring event functions for schema-qualified access
-- Date: 2025-11-01
-- Purpose: Provide database functions to insert/query monitoring events in monitoring schema
-- Reason: Supabase Python client doesn't support schema-qualified table names directly
-- EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
-- Strategy: Create wrapper functions in public schema that call monitoring schema functions

-- ============================================================================
-- Core Function: monitoring.insert_monitoring_event
-- ============================================================================
-- Core implementation in monitoring schema
-- Inserts a single monitoring event into monitoring.monitoring_events

CREATE OR REPLACE FUNCTION monitoring.insert_monitoring_event(
    p_event_type VARCHAR,
    p_timestamp TIMESTAMP WITH TIME ZONE,
    p_source VARCHAR,
    p_data JSONB,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE(
    id UUID,
    event_type VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    source VARCHAR,
    data JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = monitoring, public
AS $$
BEGIN
    RETURN QUERY
    INSERT INTO monitoring.monitoring_events (
        event_type,
        timestamp,
        source,
        data,
        metadata
    )
    VALUES (
        p_event_type,
        p_timestamp,
        p_source,
        p_data,
        p_metadata
    )
    RETURNING
        monitoring_events.id,
        monitoring_events.event_type,
        monitoring_events.timestamp,
        monitoring_events.source,
        monitoring_events.data,
        monitoring_events.metadata,
        monitoring_events.created_at;
END;
$$;

-- ============================================================================
-- Wrapper Function: public.insert_monitoring_event
-- ============================================================================
-- Public wrapper for Supabase RPC compatibility
-- Calls the core function in monitoring schema

CREATE OR REPLACE FUNCTION public.insert_monitoring_event(
    p_event_type VARCHAR,
    p_timestamp TIMESTAMP WITH TIME ZONE,
    p_source VARCHAR,
    p_data JSONB,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE(
    id UUID,
    event_type VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    source VARCHAR,
    data JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM monitoring.insert_monitoring_event(
        p_event_type,
        p_timestamp,
        p_source,
        p_data,
        p_metadata
    );
END;
$$;

-- ============================================================================
-- Core Function: monitoring.insert_monitoring_events_batch
-- ============================================================================
-- Core implementation in monitoring schema
-- Inserts multiple monitoring events efficiently
-- Accepts JSON array of events

CREATE OR REPLACE FUNCTION monitoring.insert_monitoring_events_batch(
    p_events JSONB
)
RETURNS TABLE(
    id UUID,
    event_type VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    source VARCHAR,
    data JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = monitoring, public
AS $$
BEGIN
    RETURN QUERY
    INSERT INTO monitoring.monitoring_events (
        event_type,
        timestamp,
        source,
        data,
        metadata
    )
    SELECT
        (event->>'event_type')::VARCHAR,
        (event->>'timestamp')::TIMESTAMP WITH TIME ZONE,
        (event->>'source')::VARCHAR,
        (event->'data')::JSONB,
        COALESCE((event->'metadata')::JSONB, '{}'::jsonb)
    FROM jsonb_array_elements(p_events) AS event
    RETURNING
        monitoring_events.id,
        monitoring_events.event_type,
        monitoring_events.timestamp,
        monitoring_events.source,
        monitoring_events.data,
        monitoring_events.metadata,
        monitoring_events.created_at;
END;
$$;

-- ============================================================================
-- Wrapper Function: public.insert_monitoring_events_batch
-- ============================================================================
-- Public wrapper for Supabase RPC compatibility

CREATE OR REPLACE FUNCTION public.insert_monitoring_events_batch(
    p_events JSONB
)
RETURNS TABLE(
    id UUID,
    event_type VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    source VARCHAR,
    data JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM monitoring.insert_monitoring_events_batch(p_events);
END;
$$;

-- ============================================================================
-- Core Function: monitoring.get_monitoring_events
-- ============================================================================
-- Core implementation in monitoring schema
-- Retrieves monitoring events with optional filtering
-- Supports pagination and ordering

CREATE OR REPLACE FUNCTION monitoring.get_monitoring_events(
    p_limit INT DEFAULT 100,
    p_offset INT DEFAULT 0,
    p_event_type VARCHAR DEFAULT NULL,
    p_source VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    id UUID,
    event_type VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    source VARCHAR,
    data JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = monitoring, public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        monitoring_events.id,
        monitoring_events.event_type,
        monitoring_events.timestamp,
        monitoring_events.source,
        monitoring_events.data,
        monitoring_events.metadata,
        monitoring_events.created_at
    FROM monitoring.monitoring_events
    WHERE
        (p_event_type IS NULL OR monitoring_events.event_type = p_event_type)
        AND (p_source IS NULL OR monitoring_events.source = p_source)
    ORDER BY monitoring_events.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;

-- ============================================================================
-- Wrapper Function: public.get_monitoring_events
-- ============================================================================
-- Public wrapper for Supabase RPC compatibility

CREATE OR REPLACE FUNCTION public.get_monitoring_events(
    p_limit INT DEFAULT 100,
    p_offset INT DEFAULT 0,
    p_event_type VARCHAR DEFAULT NULL,
    p_source VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    id UUID,
    event_type VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    source VARCHAR,
    data JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM monitoring.get_monitoring_events(
        p_limit,
        p_offset,
        p_event_type,
        p_source
    );
END;
$$;

-- ============================================================================
-- Grant permissions
-- ============================================================================
-- Grant permissions on public wrapper functions (for Supabase RPC)
GRANT EXECUTE ON FUNCTION public.insert_monitoring_event TO service_role;
GRANT EXECUTE ON FUNCTION public.insert_monitoring_events_batch TO service_role;
GRANT EXECUTE ON FUNCTION public.get_monitoring_events TO service_role;

-- Grant permissions on core functions in monitoring schema
GRANT EXECUTE ON FUNCTION monitoring.insert_monitoring_event TO service_role;
GRANT EXECUTE ON FUNCTION monitoring.insert_monitoring_events_batch TO service_role;
GRANT EXECUTE ON FUNCTION monitoring.get_monitoring_events TO service_role;

-- Allow authenticated users to execute (for future multi-user support)
GRANT EXECUTE ON FUNCTION public.insert_monitoring_event TO authenticated;
GRANT EXECUTE ON FUNCTION public.insert_monitoring_events_batch TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_monitoring_events TO authenticated;

