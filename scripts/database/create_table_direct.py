import os
import psycopg2
from urllib.parse import urlparse

# Get project ref from URL
supabase_url = os.environ['SUPABASE_URL']
project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

# Construct direct PostgreSQL connection string
# Format: postgresql://postgres.PROJECT_REF:PASSWORD@HOST:PORT/postgres
# Supabase uses pooler.supabase.com on port 6543 for direct connections
db_password = os.environ['SUPABASE_SERVICE_ROLE_KEY']

# Try different connection string formats
connection_strings = [
    f"postgresql://postgres:{db_password}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres",
    f"postgresql://postgres.{project_ref}:{db_password}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres",
    f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres",
]

# Read SQL
with open('create_file_operations_table.sql', 'r') as f:
    sql = f.read()

for conn_str in connection_strings:
    try:
        print(f"Trying connection string...")
        conn = psycopg2.connect(conn_str)
        print("Connected successfully!")
        
        cur = conn.cursor()
        
        # Execute SQL statements
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for stmt in statements:
            if stmt:
                print(f"Executing: {stmt[:80]}...")
                cur.execute(stmt)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\nSUCCESS: Table created!")
        print("Now restarting PostgREST to refresh schema cache...")
        
        # The table should now exist
        break
        
    except Exception as e:
        print(f"Failed: {e}")
        continue
else:
    print("\nAll connection attempts failed. The table may already exist or there's a connectivity issue.")
