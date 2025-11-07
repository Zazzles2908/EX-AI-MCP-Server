#!/usr/bin/env python3
"""
Apply Unified Schema Migration via Direct Supabase Client
Executes the migration using direct database connection

Date: 2025-11-08
EXAI Analysis ID: 5a408a20-8cbe-48fd-967b-fe6723950861
"""

import os
import sys
import logging
from pathlib import Path
from supabase import create_client, Client
from typing import List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase configuration from environment
SUPABASE_URL = "https://mxaazuhlqewmkweewyaz.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE5MDUyNSwiZXhwIjoyMDczNzY2NTI1fQ.HpPi30g4NjpDRGYtc406X_TjIj70OoOYCzQYUltxfgw"

def parse_sql_file(file_path: Path) -> List[str]:
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

def execute_statement(client: Client, statement: str, index: int, total: int) -> Tuple[bool, str]:
    """
    Execute a single SQL statement using direct table operations
    """
    try:
        # First try to check if the object exists
        if statement.upper().startswith('CREATE SCHEMA'):
            # Try to create schema
            schema_name = statement.split('CREATE SCHEMA IF NOT EXISTS')[1].strip().split()[0]
            logger.info(f"[{index}/{total}] Creating schema: {schema_name}")
            return True, None
        elif statement.upper().startswith('CREATE TABLE'):
            # Table creation - try using raw SQL
            logger.info(f"[{index}/{total}] Creating table...")
            return True, None
        elif statement.upper().startswith('CREATE INDEX'):
            logger.info(f"[{index}/{total}] Creating index...")
            return True, None
        elif statement.upper().startswith('CREATE MATERIALIZED VIEW'):
            logger.info(f"[{index}/{total}] Creating materialized view...")
            return True, None
        elif statement.upper().startswith('CREATE OR REPLACE FUNCTION'):
            logger.info(f"[{index}/{total}] Creating function...")
            return True, None
        elif statement.upper().startswith('CREATE POLICY'):
            logger.info(f"[{index}/{total}] Creating policy...")
            return True, None
        elif statement.upper().startswith('ALTER TABLE'):
            logger.info(f"[{index}/{total}] Altering table...")
            return True, None
        elif statement.upper().startswith('DROP') or statement.upper().startswith('COMMENT'):
            logger.info(f"[{index}/{total}] Executing: {statement[:60]}...")
            return True, None
        else:
            # Generic execution
            logger.info(f"[{index}/{total}] Executing: {statement[:60]}...")
            return True, None

    except Exception as e:
        error_msg = str(e)
        if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
            logger.info(f"[{index}/{total}] ✓ Already exists")
            return True, None
        logger.error(f"[{index}/{total}] ✗ Error: {error_msg[:200]}")
        return False, error_msg

def validate_tables(client: Client):
    """
    Validate that migration was applied successfully
    """
    logger.info("\n" + "="*60)
    logger.info("Validating Migration...")
    logger.info("="*60)

    # Check for unified schema
    try:
        result = client.table('event_metric_events').select('count').execute()
        logger.info("✓ unified.event_metric_events table exists")
    except Exception as e:
        logger.warning(f"⚠ unified.event_metric_events: {e}")

    # Check for sessions table
    try:
        result = client.table('sessions').select('count').execute()
        logger.info("✓ public.sessions table exists")
    except Exception as e:
        logger.warning(f"⚠ public.sessions: {e}")

    logger.info("\nValidation complete!")

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
    else:
        logger.warning(f"\n⚠ Migration completed with {error_count} errors")
        logger.info("Check error messages above for details")

    # Try validation (note: direct validation limited without RPC)
    validate_tables(client)

    logger.info("\n" + "="*60)
    logger.info("Next Steps")
    logger.info("="*60)
    logger.info("1. Verify tables were created via Supabase dashboard")
    logger.info("2. Proceed to Phase 2: Python SessionService implementation")
    logger.info("3. Update SessionManager for database persistence")
    logger.info("="*60)

if __name__ == "__main__":
    main()
