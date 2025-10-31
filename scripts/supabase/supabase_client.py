"""
Supabase Client Initialization for EXAI Universal File Hub
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

# Validate required environment variables
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")
if not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_ANON_KEY environment variable is required")
if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required")

# ============================================================================
# CLIENT INSTANCES
# ============================================================================

# Client for user-authenticated operations (uses anon key)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Client for admin/server operations (uses service role key)
# WARNING: Never expose this client to client-side code!
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_supabase_client(use_admin: bool = False) -> Client:
    """
    Get Supabase client instance.
    
    Args:
        use_admin: If True, returns admin client with service role key.
                   If False, returns user client with anon key.
    
    Returns:
        Supabase client instance
    
    Example:
        # For user operations
        client = get_supabase_client()
        
        # For admin operations
        admin_client = get_supabase_client(use_admin=True)
    """
    return supabase_admin if use_admin else supabase


def get_db_connection_string() -> Optional[str]:
    """
    Get database connection string for direct PostgreSQL access.
    
    Returns:
        Database connection string or None if not configured
    
    Example:
        conn_string = get_db_connection_string()
        if conn_string:
            # Use with psycopg2 or SQLAlchemy
            pass
    """
    return SUPABASE_DB_URL


def test_connection() -> bool:
    """
    Test Supabase connection.
    
    Returns:
        True if connection successful, False otherwise
    
    Example:
        if test_connection():
            print("Supabase connection successful!")
        else:
            print("Supabase connection failed!")
    """
    try:
        # Try to list buckets (requires valid connection)
        response = supabase_admin.storage.list_buckets()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def get_bucket_list() -> list:
    """
    Get list of all storage buckets.
    
    Returns:
        List of bucket objects
    
    Example:
        buckets = get_bucket_list()
        for bucket in buckets:
            print(f"Bucket: {bucket['name']}")
    """
    try:
        return supabase_admin.storage.list_buckets()
    except Exception as e:
        print(f"Failed to list buckets: {e}")
        return []


def verify_buckets() -> dict:
    """
    Verify that all required buckets exist.
    
    Returns:
        Dictionary with bucket verification results
    
    Example:
        results = verify_buckets()
        if results['all_exist']:
            print("All buckets exist!")
        else:
            print(f"Missing buckets: {results['missing']}")
    """
    required_buckets = ['user-files', 'results', 'generated-files']
    existing_buckets = [b['name'] for b in get_bucket_list()]
    
    missing = [b for b in required_buckets if b not in existing_buckets]
    
    return {
        'all_exist': len(missing) == 0,
        'required': required_buckets,
        'existing': existing_buckets,
        'missing': missing
    }


def verify_tables() -> dict:
    """
    Verify that all required database tables exist.
    
    Returns:
        Dictionary with table verification results
    
    Example:
        results = verify_tables()
        if results['all_exist']:
            print("All tables exist!")
        else:
            print(f"Missing tables: {results['missing']}")
    """
    required_tables = ['file_operations', 'file_metadata']
    existing_tables = []
    
    try:
        # Try to query each table
        for table in required_tables:
            try:
                supabase_admin.table(table).select("id").limit(1).execute()
                existing_tables.append(table)
            except:
                pass
    except Exception as e:
        print(f"Failed to verify tables: {e}")
    
    missing = [t for t in required_tables if t not in existing_tables]
    
    return {
        'all_exist': len(missing) == 0,
        'required': required_tables,
        'existing': existing_tables,
        'missing': missing
    }


def get_configuration_status() -> dict:
    """
    Get comprehensive configuration status.
    
    Returns:
        Dictionary with configuration status
    
    Example:
        status = get_configuration_status()
        print(f"Connection: {status['connection']}")
        print(f"Buckets: {status['buckets']['all_exist']}")
        print(f"Tables: {status['tables']['all_exist']}")
    """
    return {
        'connection': test_connection(),
        'buckets': verify_buckets(),
        'tables': verify_tables(),
        'env_vars': {
            'SUPABASE_URL': bool(SUPABASE_URL),
            'SUPABASE_ANON_KEY': bool(SUPABASE_ANON_KEY),
            'SUPABASE_SERVICE_ROLE_KEY': bool(SUPABASE_SERVICE_ROLE_KEY),
            'SUPABASE_DB_URL': bool(SUPABASE_DB_URL)
        }
    }


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Supabase Configuration Status")
    print("=" * 80)
    
    status = get_configuration_status()
    
    print("\n📡 Connection:")
    print(f"  {'✅' if status['connection'] else '❌'} Supabase connection")
    
    print("\n🔑 Environment Variables:")
    for var, exists in status['env_vars'].items():
        print(f"  {'✅' if exists else '❌'} {var}")
    
    print("\n🗄️ Storage Buckets:")
    buckets = status['buckets']
    if buckets['all_exist']:
        print(f"  ✅ All required buckets exist")
        for bucket in buckets['existing']:
            print(f"     - {bucket}")
    else:
        print(f"  ❌ Missing buckets: {', '.join(buckets['missing'])}")
        print(f"     Existing: {', '.join(buckets['existing'])}")
    
    print("\n📊 Database Tables:")
    tables = status['tables']
    if tables['all_exist']:
        print(f"  ✅ All required tables exist")
        for table in tables['existing']:
            print(f"     - {table}")
    else:
        print(f"  ❌ Missing tables: {', '.join(tables['missing'])}")
        print(f"     Existing: {', '.join(tables['existing'])}")
    
    print("\n" + "=" * 80)
    
    if status['connection'] and buckets['all_exist'] and tables['all_exist']:
        print("✅ Supabase setup is complete and ready to use!")
    else:
        print("❌ Supabase setup is incomplete. Please check the errors above.")
    
    print("=" * 80)

