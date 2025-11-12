#!/usr/bin/env python3
"""
Quick Database Migration Script
Uses supabase-py client for direct SQL execution
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    from supabase import create_client

    # Get environment
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)

    print("Connecting to Supabase...")
    supabase = create_client(url, key)

    # Migration files in order
    migrations = [
        ('src/database/migrations/001_user_quotas.sql', 'User Quotas'),
        ('database/migrations/20251109_add_missing_tables.sql', 'Missing Tables'),
        ('database/migrations/20251109_create_core_tables.sql', 'Core Tables'),
        ('database/migrations/20251109_add_performance_indexes.sql', 'Performance Indexes'),
        ('database/migrations/20251109_create_rls_and_storage.sql', 'RLS & Storage'),
    ]

    for filepath, name in migrations:
        print(f"\nApplying {name}...")
        path = Path(filepath)
        if not path.exists():
            print(f"  ERROR: File not found: {filepath}")
            continue

        try:
            with open(path, 'r') as f:
                sql = f.read()

            # Execute via RPC (simple approach)
            # Note: This is a basic implementation
            result = supabase.rpc('exec_sql', {'query': sql}).execute()
            print(f"  ✅ Success: {name}")

        except Exception as e:
            print(f"  ❌ Error: {str(e)[:200]}")
            print(f"     Try applying manually: psql -f {filepath}")

    print("\n✅ Deployment script complete!")

if __name__ == '__main__':
    main()
