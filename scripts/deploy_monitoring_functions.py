#!/usr/bin/env python3
"""
Deploy monitoring functions to Supabase
Creates database functions for schema-qualified table access
"""

import os
from supabase import create_client
from datetime import datetime

SUPABASE_URL = 'https://mxaazuhlqewmkweewyaz.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE5MDUyNSwiZXhwIjoyMDczNzY2NTI1fQ.HpPi30g4NjpDRGYtc406X_TjIj70OoOYCzQYUltxfgw'

def deploy_functions():
    """Deploy monitoring functions to Supabase"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Function 1: insert_monitoring_event
        print("[1/3] Creating insert_monitoring_event function...")
        client.postgrest.session.post(
            f'{client.url}/rest/v1/rpc/exec_sql',
            json={'sql': """
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
        """}
        )
        print("✓ insert_monitoring_event created")
        
        # Function 2: insert_monitoring_events_batch
        print("[2/3] Creating insert_monitoring_events_batch function...")
        cursor.execute("""
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
        """)
        conn.commit()
        print("✓ insert_monitoring_events_batch created")
        
        # Function 3: get_monitoring_events
        print("[3/3] Creating get_monitoring_events function...")
        cursor.execute("""
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
        """)
        conn.commit()
        print("✓ get_monitoring_events created")
        
        # Grant permissions
        print("\nGranting permissions...")
        cursor.execute("GRANT EXECUTE ON FUNCTION monitoring.insert_monitoring_event TO service_role;")
        cursor.execute("GRANT EXECUTE ON FUNCTION monitoring.insert_monitoring_events_batch TO service_role;")
        cursor.execute("GRANT EXECUTE ON FUNCTION monitoring.get_monitoring_events TO service_role;")
        conn.commit()
        print("✓ Permissions granted to service_role")
        
        cursor.close()
        conn.close()
        
        print("\n✅ All functions deployed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    deploy_functions()

