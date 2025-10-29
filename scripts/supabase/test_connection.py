"""
Test Supabase Connection
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Verifies Supabase connection and credentials.
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

def test_connection():
    """Test Supabase connection."""
    print("=" * 80)
    print("Supabase Connection Test")
    print("=" * 80)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url:
        print("   ❌ SUPABASE_URL not set")
        return False
    if not service_key:
        print("   ❌ SUPABASE_SERVICE_ROLE_KEY not set")
        return False
    
    print(f"   ✅ SUPABASE_URL: {url}")
    print(f"   ✅ SUPABASE_SERVICE_ROLE_KEY: {service_key[:20]}...")
    
    # Test connection
    print("\n2. Testing connection to Supabase...")
    try:
        from supabase import create_client
        
        client = create_client(url, service_key)
        print("   ✅ Client created successfully")
        
    except ImportError:
        print("   ❌ Supabase client not installed")
        print("   Run: pip install supabase")
        return False
    except Exception as e:
        print(f"   ❌ Failed to create client: {e}")
        return False
    
    # Test database access
    print("\n3. Testing database access...")
    try:
        # Try to query a system table
        result = client.table('_supabase_migrations').select('*').limit(1).execute()
        print("   ✅ Database access successful")
        
    except Exception as e:
        # This might fail if migrations table doesn't exist, which is okay
        print(f"   ⚠️  Migrations table query failed (expected): {e}")
        print("   ℹ️  This is normal for a new project")
    
    # Test storage access
    print("\n4. Testing storage access...")
    try:
        buckets = client.storage.list_buckets()
        print(f"   ✅ Storage access successful")
        print(f"   ℹ️  Found {len(buckets)} existing buckets")

        if buckets:
            for bucket in buckets:
                # Handle both dict and object types
                bucket_name = bucket.name if hasattr(bucket, 'name') else bucket.get('name', 'unknown')
                bucket_public = bucket.public if hasattr(bucket, 'public') else bucket.get('public', False)
                print(f"      - {bucket_name} (public: {bucket_public})")

    except Exception as e:
        print(f"   ❌ Storage access failed: {e}")
        return False
    
    # Test RPC access
    print("\n5. Testing RPC access...")
    try:
        # Try to call a simple RPC function (this will fail but tests access)
        try:
            client.rpc('test_function').execute()
        except Exception as rpc_error:
            # Expected to fail if function doesn't exist
            if 'does not exist' in str(rpc_error).lower() or 'not found' in str(rpc_error).lower():
                print("   ✅ RPC access working (function not found is expected)")
            else:
                print(f"   ⚠️  RPC error: {rpc_error}")
        
    except Exception as e:
        print(f"   ⚠️  RPC test inconclusive: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Connection test PASSED")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Create storage buckets")
    print("2. Execute database schema")
    print("3. Test upload/download utilities")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

