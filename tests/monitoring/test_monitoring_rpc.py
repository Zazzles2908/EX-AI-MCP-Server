#!/usr/bin/env python3
"""
Test monitoring RPC functions
"""

import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = 'https://mxaazuhlqewmkweewyaz.supabase.co'
from src.config.settings import Config
config = Config()
SUPABASE_KEY = config.supabase_service_key

def test_rpc():
    """Test RPC functions"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("Testing RPC functions...")
        
        # Test 1: Try to call insert_monitoring_event
        print("\n[1] Testing insert_monitoring_event RPC...")
        try:
            result = client.rpc(
                'insert_monitoring_event',
                {
                    'p_event_type': 'test_event',
                    'p_timestamp': datetime.utcnow().isoformat(),
                    'p_source': 'test_source',
                    'p_data': {'test': 'data'},
                    'p_metadata': {'test': 'metadata'},
                }
            ).execute()
            print(f"✓ RPC call successful: {result.data}")
        except Exception as e:
            print(f"✗ RPC call failed: {str(e)[:200]}")
            
            # If function doesn't exist, try to create it
            if 'does not exist' in str(e) or 'could not find' in str(e).lower():
                print("\n[2] Function doesn't exist, attempting to create...")
                print("Note: This requires manual SQL execution or Supabase dashboard")
                print("Please run the SQL from supabase/migrations/20251101_add_monitoring_functions.sql")
        
        # Test 2: Check if table exists
        print("\n[3] Checking if monitoring.monitoring_events table exists...")
        try:
            result = client.table('monitoring_events').select('count', count='exact').execute()
            print(f"✓ Table exists with {result.count} rows")
        except Exception as e:
            print(f"✗ Table check failed: {str(e)[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_rpc()

