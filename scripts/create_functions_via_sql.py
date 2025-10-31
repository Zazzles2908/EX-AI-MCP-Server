#!/usr/bin/env python3
"""
Create monitoring functions by executing SQL directly
Uses HTTP requests to Supabase SQL endpoint
"""

import requests
import json

SUPABASE_URL = 'https://mxaazuhlqewmkweewyaz.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE5MDUyNSwiZXhwIjoyMDczNzY2NTI1fQ.HpPi30g4NjpDRGYtc406X_TjIj70OoOYCzQYUltxfgw'

# SQL statements to create the functions
SQL_STATEMENTS = [
    # Create core function in monitoring schema
    """
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
    """,
    
    # Create public wrapper function
    """
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
    """,
    
    # Grant permissions
    "GRANT EXECUTE ON FUNCTION public.insert_monitoring_event TO service_role;",
    "GRANT EXECUTE ON FUNCTION monitoring.insert_monitoring_event TO service_role;",
]

def execute_sql(sql):
    """Execute SQL via Supabase REST API"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # Try different endpoints
    endpoints = [
        f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
        f'{SUPABASE_URL}/rest/v1/rpc/sql',
        f'{SUPABASE_URL}/rest/v1/rpc/execute_sql',
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json={'sql': sql},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return True, response.text
            elif response.status_code == 404:
                continue  # Try next endpoint
            else:
                return False, response.text
        except Exception as e:
            continue
    
    return False, "No valid endpoint found"

def main():
    print("Creating monitoring functions...")
    
    for i, sql in enumerate(SQL_STATEMENTS, 1):
        print(f"\n[{i}/{len(SQL_STATEMENTS)}] Executing SQL...")
        success, response = execute_sql(sql)
        
        if success:
            print(f"✓ Success")
        else:
            print(f"✗ Failed: {response[:200]}")
    
    print("\n✅ Done!")

if __name__ == '__main__':
    main()

