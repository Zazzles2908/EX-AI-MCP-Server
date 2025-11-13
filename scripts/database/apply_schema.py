import os
from supabase import create_client

# Supabase configuration from environment
url = os.environ['SUPABASE_URL']
service_key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
supabase = create_client(url, service_key)

# Read and execute schema
with open('scripts/supabase/schema.sql', 'r') as f:
    schema_sql = f.read()

# Split by statements and execute
statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
for stmt in statements:
    if stmt and not stmt.startswith('--'):
        try:
            result = supabase.rpc('exec_sql', {'sql': stmt}).execute()
            print(f"Executed: {stmt[:50]}...")
        except Exception as e:
            print(f"Error executing: {stmt[:50]}... - {e}")

print("Schema application complete!")
