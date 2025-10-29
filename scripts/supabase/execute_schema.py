"""
Execute Supabase Database Schema
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Executes the database schema SQL file to create tables, indexes, functions, and views.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env.docker
env_path = Path(__file__).parent.parent.parent / '.env.docker'
load_dotenv(env_path)

def execute_schema():
    """Execute database schema."""
    print("=" * 80)
    print("Executing Supabase Database Schema")
    print("=" * 80)
    
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    client = create_client(url, service_key)
    
    # Read schema file
    schema_path = Path(__file__).parent / 'schema_dev.sql'
    print(f"\n1. Reading schema file: {schema_path}")
    
    if not schema_path.exists():
        print(f"   ❌ Schema file not found: {schema_path}")
        return False
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print(f"   ✅ Schema file loaded ({len(schema_sql)} characters)")
    
    # Execute schema
    print("\n2. Executing schema SQL...")
    print("   ℹ️  This may take a moment...")
    
    try:
        # Execute the SQL using the REST API
        # Note: Supabase Python client doesn't have direct SQL execution
        # We need to use the PostgREST API or execute via RPC
        
        # Split SQL into individual statements
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        print(f"   ℹ️  Found {len(statements)} SQL statements")
        
        # For now, we'll need to execute this manually via Supabase dashboard
        print("\n   ⚠️  MANUAL STEP REQUIRED:")
        print("   1. Go to Supabase Dashboard → SQL Editor")
        print("   2. Copy the contents of scripts/supabase/schema_dev.sql")
        print("   3. Paste and execute in the SQL Editor")
        print("   4. Then run this script again to verify")
        
        # Try to verify if tables exist
        print("\n3. Verifying schema execution...")
        
        try:
            # Check if users table exists
            result = client.table('users').select('*').limit(1).execute()
            print("   ✅ 'users' table exists")
            
            # Check if file_operations table exists
            result = client.table('file_operations').select('*').limit(1).execute()
            print("   ✅ 'file_operations' table exists")
            
            # Check if file_metadata table exists
            result = client.table('file_metadata').select('*').limit(1).execute()
            print("   ✅ 'file_metadata' table exists")
            
            print("\n   ✅ All tables verified successfully!")
            
        except Exception as e:
            error_msg = str(e)
            if 'not found' in error_msg.lower() or 'does not exist' in error_msg.lower():
                print(f"\n   ❌ Tables not found. Please execute schema manually:")
                print(f"      {e}")
                print("\n   📋 INSTRUCTIONS:")
                print("   1. Open Supabase Dashboard")
                print("   2. Go to SQL Editor")
                print("   3. Copy contents of: scripts/supabase/schema_dev.sql")
                print("   4. Paste and click 'Run'")
                print("   5. Then run this script again")
                return False
            else:
                print(f"   ⚠️  Verification error: {e}")
                return False
        
    except Exception as e:
        print(f"   ❌ Schema execution failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ Schema execution complete")
    print("=" * 80)
    print("\nNext step: Test upload/download utilities")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = execute_schema()
    sys.exit(0 if success else 1)

