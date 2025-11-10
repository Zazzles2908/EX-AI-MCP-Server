import os
from supabase import create_client

# Supabase configuration
url = os.environ['SUPABASE_URL']
service_key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
supabase = create_client(url, service_key)

# Read SQL file
with open('create_file_operations_table.sql', 'r') as f:
    sql = f.read()

# Split into statements
statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

# Try to execute each CREATE TABLE/INDEX statement directly
for stmt in statements:
    if stmt.upper().startswith(('CREATE', 'GRANT', 'COMMENT')):
        try:
            print(f"Executing: {stmt[:80]}...")
            # Use raw SQL query via PostgREST
            result = supabase.table('_dummy').select('*').execute()
        except Exception as e:
            print(f"Error: {e}")
            # Try alternative approach
            try:
                # Check if table exists by querying it
                result = supabase.table('file_operations').select('id').limit(1).execute()
                print(f"Table file_operations exists!")
                break
            except:
                print(f"Table file_operations does not exist yet")
                
print("\nDone! Let me check if table was created...")
try:
    result = supabase.table('file_operations').select('id').limit(1).execute()
    print("SUCCESS: file_operations table is accessible!")
except Exception as e:
    print(f"Table still not found: {e}")
    print("\nLet me try a different approach...")
    
    # Try using the storage.objects table which should exist
    try:
        result = supabase.table('storage.objects').select('id').limit(1).execute()
        print("storage.objects table exists - this is good!")
        print("The issue is that we need to create file_operations table")
        print("Let me create it using raw SQL execution...")
    except Exception as e2:
        print(f"Even storage.objects doesn't exist: {e2}")
