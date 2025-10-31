#!/usr/bin/env python3
"""
Apply migration directly by reading SQL file and executing statements
"""

import os
import sys

# Read the migration file
migration_file = '/app/migration.sql'

if not os.path.exists(migration_file):
    print(f"❌ Migration file not found: {migration_file}")
    sys.exit(1)

with open(migration_file, 'r') as f:
    migration_sql = f.read()

# Parse SQL statements (split by semicolon, ignore comments)
lines = migration_sql.split('\n')
statements = []
current_stmt = []

for line in lines:
    # Skip comments and empty lines
    if line.strip().startswith('--') or not line.strip():
        continue
    
    current_stmt.append(line)
    
    if line.strip().endswith(';'):
        stmt = '\n'.join(current_stmt).strip()
        if stmt:
            statements.append(stmt)
        current_stmt = []

print(f"Found {len(statements)} SQL statements")

# Now try to execute them
try:
    from supabase import create_client
    
    SUPABASE_URL = 'https://mxaazuhlqewmkweewyaz.supabase.co'
    SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE5MDUyNSwiZXhwIjoyMDczNzY2NTI1fQ.HpPi30g4NjpDRGYtc406X_TjIj70OoOYCzQYUltxfgw'
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Try to execute each statement
    for i, stmt in enumerate(statements, 1):
        try:
            # Try using rpc if available
            result = client.rpc('exec_sql', {'sql': stmt}).execute()
            print(f"[{i}/{len(statements)}] ✓ Executed")
        except Exception as e:
            error_msg = str(e)
            if 'exec_sql' in error_msg or 'does not exist' in error_msg:
                print(f"[{i}/{len(statements)}] ⚠ RPC method not available")
                print(f"  Note: Functions must be created manually via Supabase dashboard")
                print(f"  Or use: supabase db push")
            else:
                print(f"[{i}/{len(statements)}] ✗ {error_msg[:100]}")
    
    print("\n✅ Migration processing completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

