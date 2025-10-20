#!/usr/bin/env python3
"""
Test Supabase Connection and Storage Manager
Tests the Supabase storage manager implementation and verifies database connectivity.

Usage:
    python scripts/testing/test_supabase_connection.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.storage.supabase_client import get_storage_manager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_environment_variables():
    """Test that all required environment variables are set."""
    print("=" * 80)
    print("TEST 1: Environment Variables")
    print("=" * 80)
    
    required_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        status = "✅ SET" if var_value else "❌ MISSING"
        print(f"{var_name}: {status}")
        if not var_value:
            all_set = False
            if var_name == "SUPABASE_SERVICE_ROLE_KEY":
                print(f"  → Get from: https://supabase.com/dashboard/project/{os.getenv('SUPABASE_PROJECT_ID')}/settings/api")
    
    print()
    if all_set:
        print("✅ All environment variables are set!")
        return True
    else:
        print("❌ Some environment variables are missing. Please configure them in .env file.")
        return False


def test_storage_manager_initialization():
    """Test that the storage manager initializes correctly."""
    print("=" * 80)
    print("TEST 2: Storage Manager Initialization")
    print("=" * 80)
    
    try:
        manager = get_storage_manager()

        if not manager.enabled:
            print("❌ Storage manager is disabled (missing credentials)")
            print("   Please add SUPABASE_SERVICE_ROLE_KEY to .env file")
            return False

        print("✅ Storage manager initialized successfully!")
        print(f"   URL: {manager.url}")
        print(f"   Enabled: {manager.enabled}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize storage manager: {e}")
        return False


def test_database_connection():
    """Test database connectivity by querying schema_version table."""
    print("=" * 80)
    print("TEST 3: Database Connection")
    print("=" * 80)
    
    try:
        manager = get_storage_manager()

        if not manager.enabled:
            print("⏭️  Skipping (storage manager disabled)")
            return False

        client = manager.get_client()

        # Query schema_version table
        response = client.table("schema_version").select("*").execute()
        
        if response.data:
            print("✅ Database connection successful!")
            print(f"   Schema version: {response.data[0]['version']}")
            print(f"   Description: {response.data[0]['description']}")
            print(f"   Applied at: {response.data[0]['applied_at']}")
            return True
        else:
            print("❌ No schema version found (database might be empty)")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_table_structure():
    """Test that all required tables exist."""
    print("=" * 80)
    print("TEST 4: Table Structure")
    print("=" * 80)
    
    try:
        manager = get_storage_manager()

        if not manager.enabled:
            print("⏭️  Skipping (storage manager disabled)")
            return False

        client = manager.get_client()

        required_tables = ["conversations", "messages", "files", "conversation_files"]
        
        all_exist = True
        for table_name in required_tables:
            try:
                # Try to query the table (will fail if it doesn't exist)
                response = client.table(table_name).select("*").limit(1).execute()
                print(f"✅ Table '{table_name}' exists (rows: {len(response.data)})")
            except Exception as e:
                print(f"❌ Table '{table_name}' missing or inaccessible: {e}")
                all_exist = False
        
        print()
        if all_exist:
            print("✅ All required tables exist!")
            return True
        else:
            print("❌ Some tables are missing. Please run supabase/schema.sql")
            return False
            
    except Exception as e:
        print(f"❌ Table structure test failed: {e}")
        return False


def test_storage_buckets():
    """Test that storage buckets exist."""
    print("=" * 80)
    print("TEST 5: Storage Buckets")
    print("=" * 80)
    
    try:
        manager = get_storage_manager()

        if not manager.enabled:
            print("⏭️  Skipping (storage manager disabled)")
            return False

        client = manager.get_client()

        # List all buckets
        buckets = client.storage.list_buckets()
        
        required_buckets = ["user-files", "generated-files"]
        existing_buckets = [b.name for b in buckets]
        
        all_exist = True
        for bucket_name in required_buckets:
            if bucket_name in existing_buckets:
                bucket = next(b for b in buckets if b.name == bucket_name)
                print(f"✅ Bucket '{bucket_name}' exists")
                print(f"   Public: {bucket.public}")
                print(f"   File size limit: {bucket.file_size_limit / 1024 / 1024:.1f} MB")
            else:
                print(f"❌ Bucket '{bucket_name}' missing")
                all_exist = False
        
        print()
        if all_exist:
            print("✅ All required storage buckets exist!")
            return True
        else:
            print("❌ Some storage buckets are missing.")
            return False
            
    except Exception as e:
        print(f"❌ Storage bucket test failed: {e}")
        return False


def test_conversation_operations():
    """Test basic conversation operations."""
    print("=" * 80)
    print("TEST 6: Conversation Operations")
    print("=" * 80)
    
    try:
        manager = get_storage_manager()

        if not manager.enabled:
            print("⏭️  Skipping (storage manager disabled)")
            return False

        # Test save conversation
        test_continuation_id = "test-connection-" + str(os.getpid())
        conversation_id = manager.save_conversation(
            continuation_id=test_continuation_id,
            title="Test Connection",
            metadata={"test": True, "purpose": "connection_test"}
        )
        
        if conversation_id:
            print(f"✅ Created test conversation: {conversation_id}")
            
            # Test save message
            message_id = manager.save_message(
                conversation_id=conversation_id,
                role="user",
                content="Test message for connection verification",
                metadata={"test": True}
            )
            
            if message_id:
                print(f"✅ Created test message: {message_id}")
                
                # Test retrieve conversation
                messages = manager.get_conversation_messages(conversation_id)
                if messages and len(messages) > 0:
                    print(f"✅ Retrieved conversation history: {len(messages)} messages")
                    
                    # Cleanup test data
                    client = manager.get_client()
                    client.table("conversations").delete().eq("id", conversation_id).execute()
                    print("✅ Cleaned up test data")
                    
                    return True
                else:
                    print("❌ Failed to retrieve conversation history")
                    return False
            else:
                print("❌ Failed to create test message")
                return False
        else:
            print("❌ Failed to create test conversation")
            return False
            
    except Exception as e:
        print(f"❌ Conversation operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("SUPABASE CONNECTION TEST SUITE")
    print("=" * 80)
    print()
    
    results = {
        "Environment Variables": test_environment_variables(),
        "Storage Manager Init": test_storage_manager_initialization(),
        "Database Connection": test_database_connection(),
        "Table Structure": test_table_structure(),
        "Storage Buckets": test_storage_buckets(),
        "Conversation Operations": test_conversation_operations(),
    }
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    print()
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Supabase integration is ready!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

