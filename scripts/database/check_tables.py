import os
from supabase import create_client

url = os.environ['SUPABASE_URL']
service_key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
supabase = create_client(url, service_key)

# Get schema information
try:
    # Try to query information_schema
    result = supabase.rpc('exec', {'query': '''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    '''}).execute()
    print("Tables in public schema:")
    for row in result.data:
        print(f"  - {row['table_name']}")
except Exception as e:
    print(f"Error querying information_schema: {e}")
    print("\nTrying alternative approach...")
    
    # Try querying known tables
    known_tables = ['secrets', 'conversations', 'messages', 'storage.objects']
    for table in known_tables:
        try:
            result = supabase.table(table).select('id').limit(1).execute()
            print(f"  ✓ {table} exists")
        except:
            print(f"  ✗ {table} not found")
