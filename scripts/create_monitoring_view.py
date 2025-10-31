#!/usr/bin/env python3
"""
Create monitoring events view in Supabase
This view provides access to monitoring.monitoring_events via public schema
"""

import os
from supabase import create_client

SUPABASE_URL = 'https://mxaazuhlqewmkweewyaz.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE5MDUyNSwiZXhwIjoyMDczNzY2NTI1fQ.HpPi30g4NjpDRGYtc406X_TjIj70OoOYCzQYUltxfgw'

def create_view():
    """Create the monitoring events view"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("Creating monitoring events view...")
        
        # Step 1: Create the view
        print("\n[1/3] Creating view...")
        try:
            # Try to create view via direct table operations
            # First, check if view already exists
            result = client.table('monitoring_events_view').select('count', count='exact').limit(1).execute()
            print("✓ View already exists")
        except Exception as e:
            if 'does not exist' in str(e).lower() or 'not found' in str(e).lower():
                print("⚠ View doesn't exist yet - needs to be created via SQL")
                print("  Please run the migration manually:")
                print("  supabase db push")
                print("  Or execute the SQL from: supabase/migrations/20251101_create_monitoring_view.sql")
            else:
                print(f"✗ Error: {str(e)[:200]}")
        
        # Step 2: Test insert via view
        print("\n[2/3] Testing insert via view...")
        try:
            from datetime import datetime
            test_event = {
                'event_type': 'test_event',
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'test_source',
                'data': {'test': 'data'},
                'metadata': {'test': 'metadata'},
            }
            
            result = client.table('monitoring_events_view').insert(test_event).execute()
            print(f"✓ Insert successful: {result.data}")
            
            # Step 3: Verify data
            print("\n[3/3] Verifying data...")
            result = client.table('monitoring_events_view').select('count', count='exact').execute()
            print(f"✓ View contains {result.count} rows")
            
            print("\n✅ Monitoring view is operational!")
            return True
            
        except Exception as e:
            print(f"✗ Error: {str(e)[:200]}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    create_view()

