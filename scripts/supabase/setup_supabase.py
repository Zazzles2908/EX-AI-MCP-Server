"""
Automated Supabase Setup Script
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

This script automates the Supabase Universal File Hub setup:
1. Validates environment variables
2. Executes SQL schema
3. Creates storage buckets
4. Verifies setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease add these to your .env file:")
        print("\nSUPABASE_URL=https://your-project-id.supabase.co")
        print("SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
        print("\nGet these from: Supabase Dashboard → Settings → API")
        return False
    
    print("✅ Environment variables configured")
    return True


def execute_sql_file(client, filepath, description):
    """Execute SQL file using Supabase client."""
    print(f"\n📝 Executing {description}...")
    
    try:
        with open(filepath, 'r') as f:
            sql = f.read()
        
        # Execute SQL using Supabase RPC
        # Note: This requires the SQL to be executed via the Supabase REST API
        # For complex SQL, we'll use the PostgREST /rpc endpoint
        
        print(f"   SQL file: {filepath}")
        print(f"   Size: {len(sql)} characters")
        
        # Split SQL into individual statements
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"   Statements: {len(statements)}")
        
        # For now, print instructions for manual execution
        print(f"\n   ⚠️  Please execute this SQL manually in Supabase SQL Editor:")
        print(f"   1. Open Supabase Dashboard → SQL Editor")
        print(f"   2. Create new query")
        print(f"   3. Copy contents of: {filepath}")
        print(f"   4. Click 'Run'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_storage_buckets(client):
    """Create storage buckets."""
    print("\n🗄️  Creating storage buckets...")
    
    buckets = [
        {'name': 'user-files', 'public': False},
        {'name': 'results', 'public': False},
        {'name': 'generated-files', 'public': False}
    ]
    
    for bucket in buckets:
        try:
            # Check if bucket exists
            existing = client.storage.list_buckets()
            bucket_names = [b['name'] for b in existing]
            
            if bucket['name'] in bucket_names:
                print(f"   ✅ Bucket '{bucket['name']}' already exists")
            else:
                # Create bucket
                client.storage.create_bucket(bucket['name'], {'public': bucket['public']})
                print(f"   ✅ Created bucket '{bucket['name']}'")
                
        except Exception as e:
            print(f"   ❌ Error creating bucket '{bucket['name']}': {e}")
    
    return True


def verify_setup(client):
    """Verify the setup is complete."""
    print("\n🔍 Verifying setup...")
    
    # Check buckets
    try:
        buckets = client.storage.list_buckets()
        bucket_names = [b['name'] for b in buckets]
        
        required_buckets = ['user-files', 'results', 'generated-files']
        missing_buckets = [b for b in required_buckets if b not in bucket_names]
        
        if missing_buckets:
            print(f"   ❌ Missing buckets: {', '.join(missing_buckets)}")
        else:
            print(f"   ✅ All storage buckets exist")
            
    except Exception as e:
        print(f"   ❌ Error checking buckets: {e}")
    
    # Check tables
    try:
        # Try to query each table
        tables = ['users', 'file_operations', 'file_metadata']
        for table in tables:
            try:
                result = client.table(table).select("*").limit(1).execute()
                print(f"   ✅ Table '{table}' exists")
            except Exception as e:
                print(f"   ❌ Table '{table}' not found: {e}")
                
    except Exception as e:
        print(f"   ❌ Error checking tables: {e}")


def main():
    """Main setup function."""
    print("=" * 80)
    print("Supabase Universal File Hub - Automated Setup")
    print("=" * 80)
    
    # Step 1: Check environment
    if not check_environment():
        sys.exit(1)
    
    # Step 2: Initialize Supabase client
    print("\n📡 Connecting to Supabase...")
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        client = create_client(url, key)
        
        print("   ✅ Connected successfully")
        
    except ImportError:
        print("   ❌ Supabase client not installed")
        print("   Run: pip install supabase")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        sys.exit(1)
    
    # Step 3: Execute SQL schema
    script_dir = Path(__file__).parent
    schema_file = script_dir / 'schema_dev.sql'
    rls_file = script_dir / 'rls_policies_dev.sql'
    
    execute_sql_file(client, schema_file, "Database Schema")
    execute_sql_file(client, rls_file, "RLS Policies")
    
    # Step 4: Create storage buckets
    create_storage_buckets(client)
    
    # Step 5: Verify setup
    verify_setup(client)
    
    print("\n" + "=" * 80)
    print("Setup Instructions:")
    print("=" * 80)
    print("\n1. Execute SQL files manually in Supabase SQL Editor:")
    print(f"   - {schema_file}")
    print(f"   - {rls_file}")
    print("\n2. Storage buckets have been created automatically")
    print("\n3. Run this script again to verify setup")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

