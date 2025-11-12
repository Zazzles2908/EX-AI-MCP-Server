#!/usr/bin/env python3
"""
Database Migration Validation Script
Verifies that the unified schema migration was executed successfully.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def check_environment():
    """Check if required environment variables are set."""
    print("=" * 60)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)

    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url:
        print("❌ SUPABASE_URL not set")
        return False
    print(f"✅ SUPABASE_URL: {supabase_url[:40]}...")

    if not service_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not set")
        return False
    print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {service_key[:20]}...")

    return True

def validate_database_schema():
    """Validate the unified schema was created."""
    print("\n" + "=" * 60)
    print("VALIDATING DATABASE SCHEMA")
    print("=" * 60)

    try:
        from infrastructure.supabase_client import get_storage_manager

        storage = get_storage_manager()

        if not storage.enabled:
            print("⚠️  Supabase storage not enabled")
            return False

        # Try to get database client
        client = storage.get_client()

        # Check if unified schema exists
        try:
            result = client.table('event_metric_events').select('id').limit(1).execute()
            print("✅ Table: unified.event_metric_events exists")
        except Exception as e:
            print(f"❌ Table: unified.event_metric_events - {str(e)}")
            return False

        # Check sessions table
        try:
            result = client.table('sessions').select('id').limit(1).execute()
            print("✅ Table: public.sessions exists")
        except Exception as e:
            print(f"❌ Table: public.sessions - {str(e)}")
            return False

        print("\n✅ All database tables created successfully!")
        return True

    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False

def check_session_persistence_code():
    """Check if session persistence code is present."""
    print("\n" + "=" * 60)
    print("CHECKING SESSION PERSISTENCE CODE")
    print("=" * 60)

    files_to_check = [
        'src/infrastructure/session_service.py',
        'src/infrastructure/session_manager_enhanced.py',
        'scripts/test_session_persistence.py'
    ]

    all_exist = True
    for file_path in files_to_check:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False

    return all_exist

def main():
    """Main validation function."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DATABASE MIGRATION VALIDATION".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Run all checks
    checks = [
        ("Environment Variables", check_environment),
        ("Session Persistence Code", check_session_persistence_code),
        ("Database Schema", validate_database_schema)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\nNext Steps:")
        print("  1. Run test suite: python scripts/test_session_persistence.py")
        print("  2. Verify 100% session persistence")
        print("  3. Update application code if needed")
        print()
        return 0
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("\nPlease review the failures above and:")
        print("  1. Execute migration via Supabase dashboard SQL Editor")
        print("  2. Set environment variables correctly")
        print("  3. Re-run this validation script")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
