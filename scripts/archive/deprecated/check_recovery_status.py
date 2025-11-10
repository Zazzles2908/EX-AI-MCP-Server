#!/usr/bin/env python3
"""
Emergency Database Recovery Status Check
Verifies if the database has been restored after the wipe.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def check_tables():
    """Check if required tables exist."""
    print("=" * 70)
    print("CHECKING DATABASE TABLES")
    print("=" * 70)

    try:
        from infrastructure.supabase_client import get_storage_manager

        storage = get_storage_manager()

        if not storage.enabled:
            print("⚠️  Supabase storage not enabled")
            return False

        client = storage.get_client()

        # Check base tables
        base_tables = ['conversations', 'messages', 'files', 'conversation_files']
        missing_tables = []

        for table in base_tables:
            try:
                result = client.table(table).select('count').limit(1).execute()
                print(f"✅ {table}")
            except Exception as e:
                print(f"❌ {table} - {str(e)}")
                missing_tables.append(table)

        # Check unified schema
        try:
            result = client.table('event_metric_events').select('count').limit(1).execute()
            print("✅ unified.event_metric_events")
        except Exception as e:
            print(f"❌ unified.event_metric_events - {str(e)}")
            missing_tables.append('unified.event_metric_events')

        # Check sessions table
        try:
            result = client.table('sessions').select('count').limit(1).execute()
            print("✅ sessions")
        except Exception as e:
            print(f"❌ sessions - {str(e)}")
            missing_tables.append('sessions')

        if missing_tables:
            print(f"\n❌ Missing {len(missing_tables)} tables")
            return False
        else:
            print("\n✅ All required tables exist!")
            return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_daemon_status():
    """Check if daemon is running and functional."""
    print("\n" + "=" * 70)
    print("CHECKING DAEMON STATUS")
    print("=" * 70)

    import subprocess

    # Check if container is running
    result = subprocess.run(
        ['docker', 'ps', '--filter', 'name=exai-mcp-daemon', '--format', '{{.Status}}'],
        capture_output=True,
        text=True
    )

    if 'Up' in result.stdout:
        print("✅ Daemon container is running")

        # Check logs for errors
        log_result = subprocess.run(
            ['docker', 'logs', 'exai-mcp-daemon', '--tail', '20'],
            capture_output=True,
            text=True
        )

        if 'PGRST205' in log_result.stderr or 'Could not find the table' in log_result.stderr:
            print("❌ Daemon has table not found errors (database not restored)")
            return False
        elif 'Created session' in log_result.stderr or 'session' in log_result.stderr.lower():
            print("✅ Daemon is creating sessions (functional)")
            return True
        else:
            print("⚠️  Daemon running but status unclear (check logs)")
            return False
    else:
        print("❌ Daemon container is not running")
        return False

def main():
    """Main check function."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  DATABASE RECOVERY STATUS CHECK".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    # Run checks
    checks = [
        ("Database Tables", check_tables),
        ("Daemon Status", check_daemon_status)
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
    print("\n" + "=" * 70)
    print("RECOVERY STATUS")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "✅ RECOVERED" if passed else "❌ NOT READY"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n🎉 DATABASE RECOVERY COMPLETE!")
        print("\nNext Steps:")
        print("  1. Run full test suite: python scripts/test_session_persistence.py")
        print("  2. Verify 100% session persistence")
        print("  3. Test MCP functionality")
        print()
        return 0
    else:
        print("\n⚠️  DATABASE NOT FULLY RECOVERED")
        print("\nTo Recover:")
        print("  1. Open Supabase Dashboard SQL Editor")
        print("  2. Execute supabase/schema.sql (154 lines)")
        print("  3. Execute supabase/migrations/20251108_unified_schema.sql (427 lines)")
        print("  4. Re-run this script: python scripts/check_recovery_status.py")
        print("\nSee: scripts/EMERGENCY_DATABASE_RECOVERY.md for detailed instructions")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
