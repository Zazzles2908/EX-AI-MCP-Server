#!/usr/bin/env python3
"""
Apply Idempotency Key Migration to Supabase
============================================

This script applies the idempotency key migration to prevent duplicate message insertion.

DEDUPLICATION FIX (2025-10-22): Implements EXAI-recommended solution for message deduplication

Usage:
    python scripts/apply_idempotency_migration.py [--dry-run]

Date: 2025-10-22
Reference: EXAI consultation on message deduplication
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.supabase_client import SupabaseStorageManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_migration_sql() -> str:
    """Read the migration SQL file"""
    migration_file = project_root / "supabase" / "migrations" / "20251022_add_idempotency_key.sql"
    
    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")
    
    with open(migration_file, 'r') as f:
        return f.read()


def apply_migration(dry_run: bool = False):
    """
    Apply the idempotency key migration
    
    Args:
        dry_run: If True, only show what would be done without executing
    """
    logger.info("=" * 80)
    logger.info("IDEMPOTENCY KEY MIGRATION")
    logger.info("=" * 80)
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    # Initialize Supabase client
    storage = SupabaseStorageManager()
    
    if not storage._enabled:
        logger.error("Supabase is not enabled. Check your configuration.")
        return False
    
    # Read migration SQL
    try:
        migration_sql = read_migration_sql()
        logger.info(f"Loaded migration SQL ({len(migration_sql)} characters)")
    except Exception as e:
        logger.error(f"Failed to read migration file: {e}")
        return False
    
    if dry_run:
        logger.info("\nMigration SQL Preview:")
        logger.info("-" * 80)
        # Show first 500 characters
        preview = migration_sql[:500]
        logger.info(preview)
        if len(migration_sql) > 500:
            logger.info(f"\n... ({len(migration_sql) - 500} more characters)")
        logger.info("-" * 80)
        logger.info("\nDRY RUN: Would execute migration but not actually applying changes")
        return True
    
    # Execute migration
    logger.info("Applying migration...")
    
    try:
        client = storage.get_client()
        
        # Split SQL into individual statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        
        logger.info(f"Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            # Skip comments and empty statements
            if statement.startswith('--') or not statement:
                continue
            
            logger.debug(f"Statement {i}/{len(statements)}: {statement[:50]}...")
            
            try:
                # Execute via RPC if available, otherwise use raw SQL
                result = client.rpc('exec_sql', {'sql': statement}).execute()
                logger.debug(f"✓ Statement {i} executed successfully")
            except Exception as stmt_error:
                # Some statements might fail if already applied (idempotent)
                if "already exists" in str(stmt_error).lower():
                    logger.warning(f"Statement {i} already applied (skipping): {stmt_error}")
                else:
                    logger.error(f"✗ Statement {i} failed: {stmt_error}")
                    raise
        
        logger.info("✅ Migration applied successfully!")
        
        # Verify migration
        logger.info("\nVerifying migration...")
        verify_migration(storage)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def verify_migration(storage: SupabaseStorageManager):
    """Verify that the migration was applied correctly"""
    try:
        client = storage.get_client()
        
        # Check if idempotency_key column exists
        result = client.rpc('exec_sql', {
            'sql': """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                    AND table_name = 'messages'
                    AND column_name = 'idempotency_key';
            """
        }).execute()
        
        if result.data:
            logger.info("✓ idempotency_key column exists")
            logger.info(f"  Type: {result.data[0]['data_type']}")
            logger.info(f"  Nullable: {result.data[0]['is_nullable']}")
        else:
            logger.warning("✗ idempotency_key column not found")
        
        # Check if unique index exists
        result = client.rpc('exec_sql', {
            'sql': """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'messages'
                    AND schemaname = 'public'
                    AND indexname = 'idx_messages_idempotency_key';
            """
        }).execute()
        
        if result.data:
            logger.info("✓ Unique index on idempotency_key exists")
        else:
            logger.warning("✗ Unique index not found")
        
        # Check if upsert function exists
        result = client.rpc('exec_sql', {
            'sql': """
                SELECT proname
                FROM pg_proc
                WHERE proname = 'upsert_message_with_idempotency';
            """
        }).execute()
        
        if result.data:
            logger.info("✓ upsert_message_with_idempotency function exists")
        else:
            logger.warning("✗ upsert function not found")
        
        logger.info("\n✅ Migration verification complete")
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Apply idempotency key migration to Supabase"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )
    
    args = parser.parse_args()
    
    success = apply_migration(dry_run=args.dry_run)
    
    if success:
        logger.info("\n" + "=" * 80)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 80)
        if not args.dry_run:
            logger.info("\nNext steps:")
            logger.info("1. Test message insertion to verify deduplication works")
            logger.info("2. Monitor logs for 'Duplicate message detected' messages")
            logger.info("3. Check Supabase dashboard to confirm no duplicate entries")
        sys.exit(0)
    else:
        logger.error("\n" + "=" * 80)
        logger.error("MIGRATION FAILED")
        logger.error("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()

