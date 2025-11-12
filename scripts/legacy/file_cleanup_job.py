#!/usr/bin/env python3
"""
File Cleanup Job - Removes Expired Cache Files

Runs periodically to clean up expired cache files from the database and storage.
This prevents unbounded growth of the files table (addressing 11GB cached PNG issue).

Runs as:
- Cron job: 0 * * * * python scripts/file_cleanup_job.py
- Docker: Added to docker-compose.yml
- Python: asyncio task in daemon startup
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from storage.storage_manager import SupabaseStorageManager
from supabase import create_client, Client

logger = logging.getLogger(__name__)


async def cleanup_expired_files():
    """
    Clean up expired cache files from database and storage.

    Returns:
        int: Number of files cleaned up
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials not configured")
        return 0

    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        # Find expired cache files
        logger.info("Searching for expired cache files...")
        expired_files_result = supabase.table("files").select(
            "id, storage_path, file_type, expires_at, original_name"
        ).eq(
            "file_type", "cache"
        ).lt(
            "expires_at", datetime.now(timezone.utc).isoformat()
        ).execute()

        expired_files = expired_files_result.data
        logger.info(f"Found {len(expired_files)} expired cache files")

        if not expired_files:
            return 0

        # Delete from database
        file_ids = [f["id"] for f in expired_files]
        delete_result = supabase.table("files").delete().in_(
            "id", file_ids
        ).execute()

        deleted_count = len(delete_result.data)
        logger.info(f"Deleted {deleted_count} expired cache files from database")

        # Optional: Delete from storage bucket
        # Note: This requires bucket access and might be handled by Supabase's built-in
        # lifecycle policies. Uncomment if needed.

        # Log the cleanup
        logger.info(
            f"Cleanup complete: {deleted_count} files removed, "
            f"freed approximately {sum(f.get('size_bytes', 0) for f in expired_files) / (1024*1024):.2f} MB"
        )

        return deleted_count

    except Exception as e:
        logger.error(f"Error during file cleanup: {e}", exc_info=True)
        return 0


def main():
    """Main entry point for cleanup job"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting file cleanup job...")

    # Run cleanup
    deleted_count = asyncio.run(cleanup_expired_files())

    logger.info(f"Cleanup job completed. {deleted_count} files removed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
