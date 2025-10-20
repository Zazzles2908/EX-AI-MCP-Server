"""
Test Supabase connection with current credentials.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client

# Load from environment variables (same as supabase_client.py)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def test_supabase_connection():
    """Test Supabase connection with current credentials."""
    print("=" * 80)
    print("Testing Supabase Connection")
    print("=" * 80)
    
    print(f"\nURL: {SUPABASE_URL}")
    print(f"Key format: {SUPABASE_SERVICE_ROLE_KEY[:15]}... (length: {len(SUPABASE_SERVICE_ROLE_KEY)})")
    
    try:
        # Create client
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Client created successfully")
        
        # Test 1: Basic read
        print("\n--- Test 1: Basic Read ---")
        response = client.table("conversations").select("id").limit(1).execute()
        print(f"✅ Read successful: {len(response.data)} rows")
        
        # Test 2: Write permissions
        print("\n--- Test 2: Write Permissions ---")
        test_data = {
            "id": "test-connection-12345",
            "user_id": "test-user",
            "title": "Connection Test",
            "created_at": "2025-10-19T00:00:00Z",
            "updated_at": "2025-10-19T00:00:00Z"
        }
        
        try:
            response = client.table("conversations").insert(test_data).execute()
            print(f"✅ Write successful: {len(response.data)} rows inserted")
            
            # Test 3: Cleanup
            print("\n--- Test 3: Cleanup ---")
            client.table("conversations").delete().eq("id", "test-connection-12345").execute()
            print("✅ Cleanup successful")
            
        except Exception as e:
            print(f"⚠️  Write failed (might be schema mismatch): {e}")
            print("This is okay - we just need to verify the key works for reads")
        
        print("\n" + "=" * 80)
        print("✅ SUPABASE CONNECTION SUCCESSFUL!")
        print("=" * 80)
        print("\nThe service role key is VALID and working.")
        print("The errors in Docker logs are likely due to schema/table issues, not auth.")
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ SUPABASE CONNECTION FAILED!")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        if "Invalid API key" in str(e) or "JWT" in str(e):
            print("\n⚠️  This appears to be an authentication error.")
            print("The service role key is likely invalid or expired.")
        else:
            print("\n⚠️  This might be a different issue (network, permissions, etc.)")
        
        return False


if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)

