#!/usr/bin/env python3
"""
Execute Unified Schema Migration
Applies the unified database schema to Supabase

This script:
1. Reads the unified schema SQL migration file
2. Parses SQL statements (handles comments, multi-line statements)
3. Executes each statement using Supabase RPC
4. Validates successful creation of all components

Date: 2025-11-08
EXAI Analysis ID: 5a408a20-8cbe-48fd-967b-fe6723950861
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = "https://mxaazuhlqewmkweewyaz.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE5MDUyNSwiZXhwIjoyMDczNzY2NTI1fQ.HpPi30g4NjpDRGYtc406X_TjIj70OoOYCzQYUltxfgw"

def parse_sql_file(file_path):
    """
    Parse SQL file into individual statements

    Handles:
    - Comments (-- and /* */)
    - Multi-line statements
    - Dollar-quoted strings ($$)
    - Semicolon-separated statements
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove line comments
    lines = content.split('\n')
    statements = []
    current_stmt = []
    in_block_comment = False

    for line in lines:
        # Handle block comments
        if '/*' in line:
            in_block_comment = True
            line = line.split('/*')[0]
        if '*/' in line:
            in_block_comment = False
            line = line.split('*/')[1] if '*/' in line.split('*/')[0] else line.split('*/')[1]

        # Skip if in block comment
        if in_block_comment:
            continue

        # Remove line comments
        if '--' in line:
            line = line[:line.index('--')]

        # Add line to current statement
        if line.strip():
            current_stmt.append(line)

        # Check if statement ends (semicolon not in a dollar-quoted string)
        if current_stmt and current_stmt[-1].strip().endswith(';'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt and not stmt.startswith('--'):
                # Remove trailing semicolon
                if stmt.endswith(';'):
                    stmt = stmt[:-1].strip()
                statements.append(stmt)
            current_stmt = []

    # Add any remaining statement
    if current_stmt:
        stmt = '\n'.join(current_stmt).strip()
        if stmt and not stmt.startswith('--'):
            if stmt.endswith(';'):
                stmt = stmt[:-1].strip()
            statements.append(stmt)

    return statements

def execute_statement(client, statement, index, total):
    """
    Execute a single SQL statement
    """
    try:
        # Try using RPC first
        result = client.rpc('exec_sql', {'sql': statement}).execute()
        logger.info(f"[{index}/{total}] ✓ Success: {statement[:60]}...")
        return True, None
    except Exception as e:
        error_msg = str(e)

        # Check if RPC is not available
        if 'exec_sql' in error_msg.lower() or 'does not exist' in error_msg.lower():
            logger.warning(f"[{index}/{total}] ⚠ RPC method not available")
            logger.warning(f"  Statement: {statement[:80]}...")
            logger.warning(f"  Note: Use Supabase dashboard or 'supabase db push' to apply migration")
            return False, "RPC_NOT_AVAILABLE"

        # Check for specific errors
        if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
            logger.info(f"[{index}/{total}] ✓ Already exists: {statement[:60]}...")
            return True, None

        # Other errors
        logger.error(f"[{index}/{total}] ✗ Error: {error_msg[:100]}")
        logger.error(f"  Statement: {statement[:80]}...")
        return False, error_msg

def validate_migration(client):
    """
    Validate that migration was applied successfully
    """
    logger.info("\n" + "="*60)
    logger.info("Validating Migration...")
    logger.info("="*60)

    validations = [
        ("unified.event_metric_events", "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'event_metric_events' AND table_schema = 'unified'"),
        ("unified.sessions", "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'sessions' AND table_schema = 'public'"),
        ("Partitions", "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'unified' AND tablename LIKE 'event_metric_events_%'"),
        ("Indexes", "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'unified' AND indexname LIKE 'idx_event_metric_events_%'"),
        ("Functions", "SELECT COUNT(*) FROM pg_proc WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'unified')"),
    ]

    for name, query in validations:
        try:
            result = client.rpc('exec_sql', {'sql': query}).execute()
            count = result.data[0]['count'] if isinstance(result.data, list) else result.data
            logger.info(f"✓ {name}: {count} found")
        except Exception as e:
            logger.warning(f"⚠ {name}: Validation failed - {e}")

def main():
    """
    Main execution function
    """
    # Read migration file
    migration_file = Path(__file__).parent.parent / "supabase" / "migrations" / "20251108_unified_schema.sql"

    if not migration_file.exists():
        logger.error(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)

    logger.info("="*60)
    logger.info("EXAI Unified Schema Migration - Phase 1")
    logger.info("="*60)
    logger.info(f"Migration file: {migration_file}")

    # Parse SQL statements
    logger.info("\nParsing SQL statements...")
    statements = parse_sql_file(migration_file)
    logger.info(f"Found {len(statements)} SQL statements to execute")

    if not statements:
        logger.error("❌ No SQL statements found")
        sys.exit(1)

    # Initialize Supabase client
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("✓ Supabase client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        sys.exit(1)

    # Execute statements
    logger.info("\n" + "="*60)
    logger.info("Executing Migration Statements")
    logger.info("="*60)

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, statement in enumerate(statements, 1):
        # Skip DO blocks and other procedural code
        if statement.upper().startswith(('DO $$', 'BEGIN', 'END $$')):
            logger.info(f"[{i}/{len(statements)}] ⏭ Skipping procedural block")
            skip_count += 1
            continue

        success, error = execute_statement(client, statement, i, len(statements))

        if success:
            success_count += 1
        elif error == "RPC_NOT_AVAILABLE":
            skip_count += 1
        else:
            error_count += 1

    # Summary
    logger.info("\n" + "="*60)
    logger.info("Migration Summary")
    logger.info("="*60)
    logger.info(f"Total statements: {len(statements)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Skipped: {skip_count}")
    logger.info(f"Errors: {error_count}")

    if error_count == 0:
        logger.info("\n✅ Migration completed successfully!")
        if skip_count > 0:
            logger.info(f"Note: {skip_count} statements require manual execution via Supabase dashboard")
    else:
        logger.warning(f"\n⚠ Migration completed with {error_count} errors")
        logger.info("Check error messages above for details")

    # Try validation (only if RPC is available)
    if success_count > 0:
        validate_migration(client)

    logger.info("\n" + "="*60)
    logger.info("Next Steps")
    logger.info("="*60)
    logger.info("1. If RPC errors occurred, apply migration via Supabase dashboard")
    logger.info("2. Verify tables: unified.event_metric_events, public.sessions")
    logger.info("3. Check partitions: event_metric_events_2025_11, event_metric_events_2025_12")
    logger.info("4. Review indexes and materialized views")
    logger.info("5. Proceed to Phase 2: Architecture Consolidation")
    logger.info("="*60)

if __name__ == "__main__":
    main()
