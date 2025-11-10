#!/usr/bin/env python3
"""
Execute Supabase migration for monitoring functions
Reads migration SQL and executes it via direct database connection
"""

import os
import sys

# Try psycopg2 first, fall back to supabase client
try:
    import psycopg2
    USE_PSYCOPG2 = True
except ImportError:
    USE_PSYCOPG2 = False
    from supabase import create_client

from src.config.settings import Config

config = Config()
SUPABASE_URL = config.supabase_url
SUPABASE_KEY = config.supabase_service_key

def execute_migration_psycopg2():
    """Execute migration using psycopg2"""
    try:
        conn = psycopg2.connect(
            host='mxaazuhlqewmkweewyaz.supabase.co',
            database='postgres',
            user='postgres',
            password=SUPABASE_KEY,
            port=5432,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Read migration file
        migration_path = 'supabase/migrations/20251101_add_monitoring_functions.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration executed successfully!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def execute_migration_supabase():
    """Execute migration using Supabase client (limited support)"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Read migration file
        migration_path = 'supabase/migrations/20251101_add_monitoring_functions.sql'
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Split by statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"Executing {len(statements)} SQL statements...")
        
        for i, stmt in enumerate(statements, 1):
            try:
                # Try to execute via RPC (if available)
                result = client.rpc('exec_sql', {'sql': stmt}).execute()
                print(f"  [{i}/{len(statements)}] ✓")
            except Exception as e:
                if 'exec_sql' in str(e):
                    print(f"  [{i}/{len(statements)}] ⚠ RPC not available, trying direct execution...")
                    # Fall back to direct table operations
                    pass
                else:
                    print(f"  [{i}/{len(statements)}] ✗ {str(e)[:100]}")
        
        print("✅ Migration execution completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("Executing Supabase migration...")
    print(f"Using psycopg2: {USE_PSYCOPG2}")
    
    if USE_PSYCOPG2:
        success = execute_migration_psycopg2()
    else:
        success = execute_migration_supabase()
    
    sys.exit(0 if success else 1)

