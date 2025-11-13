-- Migration: Create public view for monitoring events
-- Date: 2025-11-01
-- Purpose: Provide Supabase Python client access to monitoring schema table
-- Reason: Supabase Python client doesn't support schema-qualified table names
-- EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
-- Strategy: Create public view as temporary bridge to monitoring.monitoring_events

-- ============================================================================
-- Create public view for monitoring events
-- ============================================================================
-- This view provides access to monitoring.monitoring_events via the public schema
-- allowing the Supabase Python client to access the table

CREATE OR REPLACE VIEW public.monitoring_events_view AS
SELECT
    id,
    event_type,
    timestamp,
    source,
    data,
    metadata,
    created_at
FROM monitoring.monitoring_events;

-- ============================================================================
-- Create INSTEAD OF INSERT trigger for the view
-- ============================================================================
-- This allows INSERT operations on the view to be redirected to the table

CREATE OR REPLACE FUNCTION public.monitoring_events_view_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO monitoring.monitoring_events (
        event_type,
        timestamp,
        source,
        data,
        metadata
    )
    VALUES (
        NEW.event_type,
        NEW.timestamp,
        NEW.source,
        NEW.data,
        NEW.metadata
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if it exists
DROP TRIGGER IF NOT EXISTS monitoring_events_view_insert_trigger ON public.monitoring_events_view;

-- Create trigger
CREATE TRIGGER monitoring_events_view_insert_trigger
INSTEAD OF INSERT ON public.monitoring_events_view
FOR EACH ROW
EXECUTE FUNCTION public.monitoring_events_view_insert();

-- ============================================================================
-- Grant permissions on view
-- ============================================================================
GRANT SELECT, INSERT ON public.monitoring_events_view TO service_role;
GRANT SELECT, INSERT ON public.monitoring_events_view TO authenticated;

-- ============================================================================
-- Grant permissions on trigger function
-- ============================================================================
GRANT EXECUTE ON FUNCTION public.monitoring_events_view_insert TO service_role;
GRANT EXECUTE ON FUNCTION public.monitoring_events_view_insert TO authenticated;

