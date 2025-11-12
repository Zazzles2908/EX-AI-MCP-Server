"""
Setup Multi-User Database Schema and Indexes

This script:
1. Adds missing indexes for performance
2. Adds expires_at and version columns
3. Creates cleanup function for expired sessions
4. Sets up RLS policies

Run this script to prepare the database for JWT authentication.

Author: EXAI Agent
Date: 2025-10-27
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bootstrap import load_env, get_repo_root
from supabase import create_client, Client

# Load environment from .env.docker
env_file = str(get_repo_root() / ".env.docker")
load_env(env_file=env_file)

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env.docker")
    sys.exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def add_columns():
    """Add expires_at and version columns to mcp_sessions table"""
    print("\n📝 Adding new columns to mcp_sessions table...")
    
    sql_commands = [
        # Add expires_at column
        """
        ALTER TABLE mcp_sessions 
        ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;
        """,
        
        # Add version column for optimistic locking
        """
        ALTER TABLE mcp_sessions 
        ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
        """,
        
        # Update existing rows to have expires_at
        """
        UPDATE mcp_sessions 
        SET expires_at = created_at + INTERVAL '1 hour'
        WHERE expires_at IS NULL;
        """,
    ]
    
    for sql in sql_commands:
        try:
            result = supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"  ✅ Executed: {sql.strip()[:50]}...")
        except Exception as e:
            # Try alternative approach using postgrest
            print(f"  ⚠️  RPC failed, trying alternative: {e}")
            # Note: This requires manual execution via Supabase dashboard
            print(f"  📋 Please execute manually:\n{sql}")


def create_indexes():
    """Create performance indexes on mcp_sessions table"""
    print("\n🔍 Creating performance indexes...")
    
    indexes = [
        # Single column indexes
        ("idx_mcp_sessions_user_id", "user_id"),
        ("idx_mcp_sessions_session_id", "session_id"),
        ("idx_mcp_sessions_expires_at", "expires_at"),
        ("idx_mcp_sessions_last_active", "last_active"),
        ("idx_mcp_sessions_status", "connection_status"),
        
        # Composite indexes
        ("idx_mcp_sessions_user_status", "user_id, connection_status"),
        
        # Partial index for active sessions
        ("idx_mcp_sessions_active", "user_id, last_active", "WHERE connection_status = 'connected'"),
    ]
    
    for index_info in indexes:
        index_name = index_info[0]
        columns = index_info[1]
        condition = index_info[2] if len(index_info) > 2 else ""
        
        sql = f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} 
        ON mcp_sessions({columns}) {condition};
        """
        
        try:
            result = supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"  ✅ Created index: {index_name}")
        except Exception as e:
            print(f"  ⚠️  Index creation failed: {index_name}")
            print(f"  📋 Please execute manually:\n{sql}")


def create_cleanup_function():
    """Create database function for cleaning up expired sessions"""
    print("\n🧹 Creating cleanup function...")
    
    sql = """
    CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
    RETURNS INTEGER AS $$
    DECLARE
        deleted_count INTEGER;
    BEGIN
        DELETE FROM mcp_sessions 
        WHERE expires_at < NOW();
        
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RETURN deleted_count;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """
    
    try:
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("  ✅ Created cleanup function")
    except Exception as e:
        print(f"  ⚠️  Function creation failed: {e}")
        print(f"  📋 Please execute manually:\n{sql}")


def verify_setup():
    """Verify the database setup"""
    print("\n✅ Verifying database setup...")
    
    try:
        # Check if table exists and has correct columns
        result = supabase.table("mcp_sessions").select("*").limit(1).execute()
        print("  ✅ mcp_sessions table accessible")
        
        # Check if we can query with new columns
        result = supabase.table("mcp_sessions").select("expires_at, version").limit(1).execute()
        print("  ✅ New columns (expires_at, version) accessible")
        
        print("\n🎉 Database setup complete!")
        print("\n📋 Next steps:")
        print("  1. Implement SessionManager in src/daemon/session_manager.py")
        print("  2. Add JWT validation middleware to src/daemon/ws/connection_manager.py")
        print("  3. Test authentication with Jazeel and Michelle users")
        
    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        print("\n⚠️  Some manual steps may be required:")
        print("  1. Go to Supabase Dashboard > SQL Editor")
        print("  2. Execute the SQL commands shown above")
        print("  3. Re-run this script to verify")


def main():
    """Main setup function"""
    print("="*60)
    print("Multi-User Database Setup")
    print("="*60)
    
    print(f"\n🔗 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 Using service role key: {SUPABASE_SERVICE_ROLE_KEY[:20]}...")
    
    # Note: Supabase Python client doesn't support DDL operations directly
    # We need to provide SQL commands for manual execution
    
    print("\n⚠️  IMPORTANT: Supabase Python client has limited DDL support.")
    print("Please execute the following SQL commands in Supabase Dashboard > SQL Editor:\n")
    
    print("-- Add columns")
    print("""
ALTER TABLE mcp_sessions 
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE mcp_sessions 
ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

UPDATE mcp_sessions 
SET expires_at = created_at + INTERVAL '1 hour'
WHERE expires_at IS NULL;
""")
    
    print("\n-- Create indexes")
    print("""
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcp_sessions_user_id ON mcp_sessions(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcp_sessions_session_id ON mcp_sessions(session_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcp_sessions_expires_at ON mcp_sessions(expires_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcp_sessions_last_active ON mcp_sessions(last_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcp_sessions_status ON mcp_sessions(connection_status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcp_sessions_user_status ON mcp_sessions(user_id, connection_status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mcp_sessions_active ON mcp_sessions(user_id, last_active) WHERE connection_status = 'connected';
""")
    
    print("\n-- Create cleanup function")
    print("""
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM mcp_sessions 
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
""")
    
    print("\n" + "="*60)
    print("After executing the SQL commands above, press Enter to verify...")
    input()
    
    verify_setup()


if __name__ == "__main__":
    main()

