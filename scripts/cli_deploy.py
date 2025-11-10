#!/usr/bin/env python3
"""
CLI-based Migration Deployment Script
Uses Supabase CLI or direct SQL execution
"""

import os
import sys
import subprocess
from pathlib import Path

def run_sql_file(filepath, description):
    """Run SQL file using supabase CLI"""
    print(f"\n▶️  {description}")
    print(f"   File: {filepath}")

    # Check if supabase CLI is available
    try:
        result = subprocess.run(
            ["supabase", "db", "query", "-f", filepath],
            env=os.environ,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Error:")
            print(f"   {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)[:200]}")
        return False

def main():
    print("=" * 80)
    print("EX-AI MCP Server - Database Migration Deployment")
    print("=" * 80)

    # Get environment
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    project_ref = os.getenv('SUPABASE_PROJECT_ID')

    if not all([url, key, project_ref]):
        print("\n❌ Missing required environment variables:")
        print(f"  SUPABASE_URL: {'✅' if url else '❌'}")
        print(f"  SUPABASE_SERVICE_ROLE_KEY: {'✅' if key else '❌'}")
        print(f"  SUPABASE_PROJECT_ID: {'✅' if project_ref else '❌'}")
        sys.exit(1)

    print(f"\n✅ Connected to: {project_ref}")
    print(f"   URL: {url}")

    # Migration files in order
    migrations = [
        ('src/database/migrations/001_user_quotas.sql', 'User Quotas'),
        ('database/migrations/20251109_add_missing_tables.sql', 'Missing Tables'),
        ('database/migrations/20251109_create_core_tables.sql', 'Core Tables'),
        ('database/migrations/20251109_add_performance_indexes.sql', 'Performance Indexes'),
        ('database/migrations/20251109_create_rls_and_storage.sql', 'RLS & Storage'),
    ]

    print("\n" + "=" * 80)
    print("APPLYING MIGRATIONS")
    print("=" * 80)

    success = 0
    failed = 0

    for filepath, description in migrations:
        path = Path(filepath)
        if not path.exists():
            print(f"\n⚠️  File not found: {filepath}")
            failed += 1
            continue

        if run_sql_file(filepath, description):
            success += 1
        else:
            failed += 1
            print(f"   ⚠️  Continuing with next migration...")

    print("\n" + "=" * 80)
    print("DEPLOYMENT SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {success}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(migrations)}")

    if failed == 0:
        print("\n🎉 All migrations applied successfully!")
        print("\n📋 Next steps:")
        print("   1. Run verification queries")
        print("   2. Test file upload functionality")
        print("   3. Check monitoring metrics")
    else:
        print(f"\n⚠️  {failed} migration(s) failed.")
        print("   Check errors above and retry manually.")

    print("=" * 80)

if __name__ == '__main__':
    main()
