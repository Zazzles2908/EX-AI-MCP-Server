"""
Backfill SHA256 hashes for existing files

This script calculates SHA256 hashes for files that don't have them yet.
It processes files in batches to avoid memory issues and provides progress tracking.

Usage:
    python -m src.file_management.migrations.backfill_file_hashes [--dry-run] [--batch-size 100]
"""

import argparse
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.storage.supabase_client import SupabaseStorageManager
from src.logging_infrastructure import get_logger

logger = get_logger(__name__)


logger = logging.getLogger(__name__)

class FileHashBackfill:
    """Backfill SHA256 hashes for existing files"""
    
    def __init__(self, storage: SupabaseStorageManager, dry_run: bool = False):
        """
        Initialize backfill processor
        
        Args:
            storage: Supabase storage manager
            dry_run: If True, don't actually update database
        """
        self.storage = storage
        self.dry_run = dry_run
        self.processed = 0
        self.updated = 0
        self.errors = 0
        self.skipped = 0
    
    async def validate_backfill_scope(self) -> Dict[str, Any]:
        """
        Validate backfill scope before execution

        Returns:
            Dictionary with scope information and warnings
        """
        try:
            # Get count of files without SHA256
            count_result = self.storage.client.table("files").select("id", count="exact").is_("sha256", "null").execute()
            total_files = count_result.count if hasattr(count_result, 'count') else 0

            # Get total size of files without SHA256
            size_result = self.storage.client.table("files").select("size_bytes").is_("sha256", "null").execute()
            total_size = sum(row.get("size_bytes", 0) for row in (size_result.data or []))

            # Generate warnings
            warnings = []
            if total_files > 10000:
                warnings.append("⚠️  Large dataset detected - consider smaller batches")
            if total_size > 1024 * 1024 * 1024:  # 1GB
                warnings.append("⚠️  Large total size - consider rate limiting")

            scope = {
                "total_files": total_files,
                "total_size_mb": total_size / (1024 * 1024),
                "warnings": warnings
            }

            logger.info(f"Backfill scope: {total_files} files, {scope['total_size_mb']:.2f} MB")
            for warning in warnings:
                logger.warning(warning)

            return scope

        except Exception as e:
            logger.error(f"Error validating backfill scope: {e}")
            return {"total_files": 0, "total_size_mb": 0, "warnings": ["Error validating scope"]}

    async def backfill_all(self, batch_size: int = 50, rate_limit: float = 1.0) -> Dict[str, int]:
        """
        Backfill SHA256 hashes for all files without them

        Args:
            batch_size: Number of files to process in each batch (default: 50)
            rate_limit: Seconds to wait between files (default: 1.0)

        Returns:
            Dictionary with statistics (processed, updated, errors, skipped)
        """
        logger.info(f"Starting file hash backfill (dry_run={self.dry_run}, batch_size={batch_size}, rate_limit={rate_limit}s)")

        # Validate scope first
        scope = await self.validate_backfill_scope()
        if scope["total_files"] == 0:
            logger.info("No files to process")
            return self._get_stats()
        
        # Get files without SHA256
        files_to_process = await self._get_files_without_hash()
        total_files = len(files_to_process)
        
        logger.info(f"Found {total_files} files without SHA256 hash")
        
        if total_files == 0:
            logger.info("No files to process")
            return self._get_stats()
        
        # Process in batches
        for i in range(0, total_files, batch_size):
            batch = files_to_process[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} files)")

            await self._process_batch(batch, rate_limit=rate_limit)
            
            # Progress update
            progress = (self.processed / total_files) * 100
            logger.info(
                f"Progress: {self.processed}/{total_files} ({progress:.1f}%) - "
                f"Updated: {self.updated}, Errors: {self.errors}, Skipped: {self.skipped}"
            )
        
        logger.info("Backfill complete")
        return self._get_stats()
    
    async def _get_files_without_hash(self) -> List[Dict[str, Any]]:
        """
        Get all files that don't have SHA256 hash
        
        Returns:
            List of file records from database
        """
        try:
            result = self.storage.client.table("files").select("*").is_("sha256", "null").execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching files without hash: {e}")
            return []
    
    async def _process_batch(self, batch: List[Dict[str, Any]], rate_limit: float = 1.0) -> None:
        """
        Process a batch of files with rate limiting

        Args:
            batch: List of file records to process
            rate_limit: Seconds to wait between files
        """
        import asyncio

        for file_record in batch:
            try:
                await self._process_file(file_record)
            except Exception as e:
                logger.error(f"Error processing file {file_record.get('id')}: {e}")
                self.errors += 1

            self.processed += 1

            # Rate limiting
            if rate_limit > 0:
                await asyncio.sleep(rate_limit)
    
    async def _process_file(self, file_record: Dict[str, Any]) -> None:
        """
        Process a single file - calculate hash and update database
        
        Args:
            file_record: File record from database
        """
        file_id = file_record.get("id")
        storage_path = file_record.get("storage_path")
        
        if not storage_path:
            logger.warning(f"File {file_id} has no storage_path, skipping")
            self.skipped += 1
            return
        
        # Try to download file from Supabase Storage
        try:
            # Download file content
            file_data = await self._download_file_from_storage(storage_path)
            
            if not file_data:
                logger.warning(f"Could not download file {file_id} from storage, skipping")
                self.skipped += 1
                return
            
            # Calculate SHA256
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            logger.debug(f"Calculated SHA256 for file {file_id}: {file_hash}")
            
            # Update database (unless dry run)
            if not self.dry_run:
                await self._update_file_hash(file_id, file_hash)
                self.updated += 1
            else:
                logger.info(f"[DRY RUN] Would update file {file_id} with hash {file_hash}")
                self.updated += 1
                
        except Exception as e:
            logger.error(f"Error processing file {file_id}: {e}")
            raise
    
    async def _download_file_from_storage(self, storage_path: str) -> Optional[bytes]:
        """
        Download file from Supabase Storage
        
        Args:
            storage_path: Path to file in storage
            
        Returns:
            File content as bytes, or None if download fails
        """
        try:
            # Determine bucket from path
            if storage_path.startswith("user-files/"):
                bucket = "user-files"
                path = storage_path[len("user-files/"):]
            elif storage_path.startswith("generated-files/"):
                bucket = "generated-files"
                path = storage_path[len("generated-files/"):]
            else:
                # Try user-files bucket by default
                bucket = "user-files"
                path = storage_path
            
            # Download file
            response = self.storage.client.storage.from_(bucket).download(path)
            return response
            
        except Exception as e:
            logger.error(f"Error downloading file from storage: {e}")
            return None
    
    async def _update_file_hash(self, file_id: str, file_hash: str) -> None:
        """
        Update file hash in database
        
        Args:
            file_id: File ID
            file_hash: SHA256 hash
        """
        try:
            self.storage.client.table("files").update({
                "sha256": file_hash
            }).eq("id", file_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating file hash: {e}")
            raise
    
    def _get_stats(self) -> Dict[str, int]:
        """
        Get processing statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            "processed": self.processed,
            "updated": self.updated,
            "errors": self.errors,
            "skipped": self.skipped
        }


async def main():
    """Main entry point for backfill script"""
    parser = argparse.ArgumentParser(description="Backfill SHA256 hashes for existing files")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually update database")
    parser.add_argument("--batch-size", type=int, default=50, help="Number of files to process per batch (default: 50)")
    parser.add_argument("--rate-limit", type=float, default=1.0, help="Seconds to wait between files (default: 1.0)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate scope, don't process files")

    args = parser.parse_args()

    # Initialize storage
    storage = SupabaseStorageManager()

    # Run backfill
    backfill = FileHashBackfill(storage, dry_run=args.dry_run)

    # Validate scope first
    if args.validate_only:
        scope = await backfill.validate_backfill_scope()
        logger.info("\n" + "=" * 60)
        logger.info("BACKFILL SCOPE VALIDATION")
        logger.info("=" * 60)
        logger.info(f"Files to process: {scope['total_files']}")
        logger.info(f"Total size: {scope['total_size_mb']:.2f} MB")
        if scope['warnings']:
            logger.info("\nWarnings:")
            for warning in scope['warnings']:
                logger.info(f"  {warning}")
        logger.info("=" * 60)
        return

    stats = await backfill.backfill_all(batch_size=args.batch_size, rate_limit=args.rate_limit)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("BACKFILL SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Processed: {stats['processed']}")
    logger.info(f"Updated:   {stats['updated']}")
    logger.info(f"Errors:    {stats['errors']}")
    logger.info(f"Skipped:   {stats['skipped']}")
    logger.info("=" * 60)
    
    if args.dry_run:
        logger.info("\n[DRY RUN] No changes were made to the database")
    else:
        logger.info("\nBackfill complete!")


if __name__ == "__main__":
    asyncio.run(main())

