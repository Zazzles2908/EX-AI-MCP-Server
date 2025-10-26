"""
File Deduplication Utility

Provides SHA256-based file deduplication with database tracking and reference counting.
Prevents duplicate storage in Supabase and AI providers by checking for existing files
before upload.

Features:
- SHA256-based duplicate detection
- Reference counting for cleanup decisions
- Async SHA256 calculation for large files
- Cleanup job for unreferenced files
- Cache hit rate monitoring

EXAI Consultation: c90cdeec-48bb-4d10-b075-925ebbf39c8a
Phase: 2.4 Final 2% - File Deduplication
Date: 2025-10-26
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from utils.file.cache import FileCache

logger = logging.getLogger(__name__)

# Monitoring metrics
_dedup_metrics = {
    'cache_hits': 0,
    'cache_misses': 0,
    'db_hits': 0,
    'db_misses': 0,
    'total_checks': 0,
    'storage_saved_bytes': 0
}


def get_dedup_metrics() -> Dict[str, Any]:
    """
    Get current deduplication metrics.

    Returns:
        Dict with metrics: {
            'cache_hits': int,
            'cache_misses': int,
            'cache_hit_rate': float,
            'db_hits': int,
            'db_misses': int,
            'total_checks': int,
            'storage_saved_bytes': int
        }
    """
    total = _dedup_metrics['total_checks']
    cache_hit_rate = (_dedup_metrics['cache_hits'] / total * 100) if total > 0 else 0.0

    return {
        **_dedup_metrics,
        'cache_hit_rate': round(cache_hit_rate, 2)
    }


def reset_dedup_metrics():
    """Reset deduplication metrics to zero"""
    global _dedup_metrics
    _dedup_metrics = {
        'cache_hits': 0,
        'cache_misses': 0,
        'db_hits': 0,
        'db_misses': 0,
        'total_checks': 0,
        'storage_saved_bytes': 0
    }


async def sha256_file_async(file_path: Path, chunk_size: int = 8192) -> str:
    """
    Calculate SHA256 hash asynchronously for large files.

    Uses chunked reading to avoid loading entire file into memory.
    Recommended for files >100MB.

    Args:
        file_path: Path to file
        chunk_size: Size of chunks to read (default 8KB)

    Returns:
        SHA256 hash as hex string
    """
    sha256_hash = hashlib.sha256()

    def _read_chunks():
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    # Run blocking I/O in thread pool
    return await asyncio.to_thread(_read_chunks)


class FileDeduplicationManager:
    """
    Manages file deduplication using SHA256 hashing and database tracking.

    Features:
    - SHA256-based duplicate detection
    - Reference counting for cleanup decisions
    - Database-backed persistence
    - In-memory cache integration
    - Atomic operations for race condition safety
    - Async SHA256 for large files
    - Cleanup jobs for unreferenced files
    - Monitoring metrics
    """

    def __init__(self, storage_manager=None):
        """
        Initialize deduplication manager.

        Args:
            storage_manager: Supabase storage manager instance (optional)
        """
        self.storage = storage_manager
        self.file_cache = FileCache()
        self.large_file_threshold = 100 * 1024 * 1024  # 100MB

    async def check_duplicate_async(
        self,
        file_path: str | Path,
        provider: str
    ) -> Optional[Dict[str, Any]]:
        """
        Async version of check_duplicate for large files.

        Uses async SHA256 calculation for files >100MB.

        Args:
            file_path: Path to file to check
            provider: Provider name ('kimi' or 'glm')

        Returns:
            Dict with existing file info if duplicate found, None otherwise
        """
        pth = Path(file_path)

        if not pth.exists() or not pth.is_file():
            raise ValueError(f"File not found: {file_path}")

        if provider not in ['kimi', 'glm']:
            raise ValueError(f"Invalid provider: {provider}. Must be 'kimi' or 'glm'")

        # Use async SHA256 for large files
        file_size = pth.stat().st_size
        try:
            if file_size > self.large_file_threshold:
                logger.info(f"Using async SHA256 for large file: {pth.name} ({file_size / 1024 / 1024:.2f} MB)")
                sha256 = await sha256_file_async(pth)
            else:
                sha256 = await asyncio.to_thread(FileCache.sha256_file, pth)
        except Exception as e:
            logger.error(f"Failed to calculate SHA256 for {file_path}: {e}")
            return None

        return await self._check_duplicate_by_hash(sha256, provider, pth)

    def check_duplicate(
        self,
        file_path: str | Path,
        provider: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if file already exists in database by SHA256 hash.

        This is the core deduplication check that prevents duplicate uploads.
        It checks both in-memory cache and database for existing files.

        Args:
            file_path: Path to file to check
            provider: Provider name ('kimi' or 'glm')

        Returns:
            Dict with existing file info if duplicate found, None otherwise.
            Dict contains: {
                'provider_file_id': str,
                'supabase_file_id': str,
                'reference_count': int,
                'filename': str,
                'file_size_bytes': int,
                'created_at': str,
                'last_used': str
            }

        Raises:
            ValueError: If file doesn't exist or provider invalid
        """
        pth = Path(file_path)

        if not pth.exists() or not pth.is_file():
            raise ValueError(f"File not found: {file_path}")

        if provider not in ['kimi', 'glm']:
            raise ValueError(f"Invalid provider: {provider}. Must be 'kimi' or 'glm'")

        # Calculate SHA256 hash (sync version)
        try:
            sha256 = FileCache.sha256_file(pth)
        except Exception as e:
            logger.error(f"Failed to calculate SHA256 for {file_path}: {e}")
            return None

        # Check in-memory cache first (fast path)
        global _dedup_metrics
        _dedup_metrics['total_checks'] += 1

        cached_id = self.file_cache.get(sha256, provider.upper())
        if cached_id:
            logger.debug(f"Cache hit for {pth.name} (sha256={sha256[:16]}...)")
            _dedup_metrics['cache_hits'] += 1

            # Verify cache is still valid in database
            if self.storage and self.storage.enabled:
                try:
                    client = self.storage.get_client()
                    result = client.table("provider_file_uploads").select("*").eq(
                        "provider_file_id", cached_id
                    ).eq("provider", provider).execute()

                    if result.data and len(result.data) > 0:
                        logger.info(f"✅ Duplicate found in cache: {pth.name} -> {cached_id}")
                        file_size = result.data[0].get('file_size_bytes', 0)
                        _dedup_metrics['storage_saved_bytes'] += file_size
                        return result.data[0]
                    else:
                        # Cache stale - remove it
                        logger.warning(f"Cache stale for {cached_id}, removing")
                        self.file_cache.remove(sha256, provider.upper())
                        _dedup_metrics['cache_hits'] -= 1
                        _dedup_metrics['cache_misses'] += 1
                except Exception as e:
                    logger.warning(f"Failed to verify cached file: {e}")
        else:
            _dedup_metrics['cache_misses'] += 1

        # Database lookup (medium path)
        if self.storage and self.storage.enabled:
            try:
                client = self.storage.get_client()
                result = client.table("provider_file_uploads").select("*").eq(
                    "sha256", sha256
                ).eq("provider", provider).execute()

                if result.data and len(result.data) > 0:
                    existing = result.data[0]
                    _dedup_metrics['db_hits'] += 1
                    logger.info(f"✅ Duplicate found in database: {pth.name} -> {existing['provider_file_id']}")

                    # Update cache for future fast lookups
                    self.file_cache.set(sha256, provider.upper(), existing['provider_file_id'])

                    file_size = existing.get('file_size_bytes', 0)
                    _dedup_metrics['storage_saved_bytes'] += file_size

                    return existing
                else:
                    _dedup_metrics['db_misses'] += 1

            except Exception as e:
                logger.error(f"Database lookup failed: {e}")
                _dedup_metrics['db_misses'] += 1
                return None
        else:
            _dedup_metrics['db_misses'] += 1

        # No duplicate found
        logger.debug(f"No duplicate found for {pth.name} (sha256={sha256[:16]}...)")
        return None

    async def _check_duplicate_by_hash(
        self,
        sha256: str,
        provider: str,
        pth: Path
    ) -> Optional[Dict[str, Any]]:
        """Internal async method for duplicate checking by hash"""
        global _dedup_metrics
        _dedup_metrics['total_checks'] += 1

        # Check in-memory cache first (fast path)
        cached_id = self.file_cache.get(sha256, provider.upper())
        if cached_id:
            logger.debug(f"Cache hit for {pth.name} (sha256={sha256[:16]}...)")
            # Verify cache is still valid in database
            if self.storage and self.storage.enabled:
                try:
                    client = self.storage.get_client()
                    result = client.table("provider_file_uploads").select("*").eq(
                        "provider_file_id", cached_id
                    ).eq("provider", provider).execute()

                    if result.data and len(result.data) > 0:
                        logger.info(f"✅ Duplicate found in cache: {pth.name} -> {cached_id}")
                        return result.data[0]
                    else:
                        # Cache stale - remove it
                        logger.warning(f"Cache stale for {cached_id}, removing")
                        self.file_cache.remove(sha256, provider.upper())
                except Exception as e:
                    logger.warning(f"Failed to verify cached file: {e}")

        # Database lookup (medium path)
        if self.storage and self.storage.enabled:
            try:
                client = self.storage.get_client()
                result = client.table("provider_file_uploads").select("*").eq(
                    "sha256", sha256
                ).eq("provider", provider).execute()

                if result.data and len(result.data) > 0:
                    existing = result.data[0]
                    logger.info(f"✅ Duplicate found in database: {pth.name} -> {existing['provider_file_id']}")

                    # Update cache for future fast lookups
                    self.file_cache.set(sha256, provider.upper(), existing['provider_file_id'])

                    return existing

            except Exception as e:
                logger.error(f"Database lookup failed: {e}")
                return None

        # No duplicate found
        logger.debug(f"No duplicate found for {pth.name} (sha256={sha256[:16]}...)")
        return None

    def increment_reference(
        self,
        provider_file_id: str,
        provider: str
    ) -> bool:
        """
        Atomically increment reference count and update last_used timestamp.

        This is called when a duplicate file is detected to track reuse.

        Args:
            provider_file_id: Provider's file ID
            provider: Provider name ('kimi' or 'glm')

        Returns:
            True if successful, False otherwise
        """
        if not self.storage or not self.storage.enabled:
            logger.warning("Storage not available, cannot increment reference count")
            return False

        try:
            client = self.storage.get_client()

            # Atomic update: increment reference_count and update last_used
            result = client.rpc(
                'increment_file_reference',
                {
                    'file_id': provider_file_id,
                    'prov': provider
                }
            ).execute()

            # Fallback if RPC doesn't exist - use PostgreSQL function via raw SQL
            if not result or not result.data:
                # Use raw SQL for atomic increment
                from postgrest import APIError
                try:
                    # Execute raw SQL through Supabase
                    client.rpc('exec_sql', {
                        'query': f"""
                            UPDATE provider_file_uploads
                            SET reference_count = reference_count + 1,
                                last_used = NOW()
                            WHERE provider_file_id = '{provider_file_id}'
                            AND provider = '{provider}'
                        """
                    }).execute()
                except Exception:
                    # Final fallback - fetch, increment, update (not atomic but works)
                    current = client.table("provider_file_uploads").select("reference_count").eq(
                        "provider_file_id", provider_file_id
                    ).eq("provider", provider).execute()

                    if current.data and len(current.data) > 0:
                        new_count = current.data[0]['reference_count'] + 1
                        client.table("provider_file_uploads").update({
                            "reference_count": new_count,
                            "last_used": datetime.utcnow().isoformat()
                        }).eq("provider_file_id", provider_file_id).eq("provider", provider).execute()

            logger.info(f"✅ Incremented reference count for {provider_file_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to increment reference count: {e}")
            return False

    def register_new_file(
        self,
        provider_file_id: str,
        supabase_file_id: Optional[str],
        file_path: str | Path,
        provider: str,
        upload_method: str = "direct"
    ) -> bool:
        """
        Register a newly uploaded file in the database.

        This is called after successful upload to track the file.

        Args:
            provider_file_id: Provider's file ID
            supabase_file_id: Supabase storage file ID (optional)
            file_path: Path to uploaded file
            provider: Provider name ('kimi' or 'glm')
            upload_method: Upload method used ('direct', 'supabase_gateway', etc.)

        Returns:
            True if successful, False otherwise
        """
        if not self.storage or not self.storage.enabled:
            logger.warning("Storage not available, cannot register file")
            return False

        pth = Path(file_path)

        try:
            sha256 = FileCache.sha256_file(pth)

            client = self.storage.get_client()

            # RACE CONDITION FIX: Try insert, handle duplicate gracefully
            try:
                client.table("provider_file_uploads").insert({
                    "provider": provider,
                    "provider_file_id": provider_file_id,
                    "supabase_file_id": supabase_file_id,
                    "sha256": sha256,
                    "filename": pth.name,
                    "file_size_bytes": pth.stat().st_size,
                    "upload_status": "completed",
                    "upload_method": upload_method,
                    "reference_count": 1,
                    "last_used": datetime.utcnow().isoformat()
                }).execute()

                logger.info(f"✅ Registered new file: {pth.name} -> {provider_file_id}")

            except Exception as insert_err:
                # Check if this is a duplicate key error (race condition)
                error_msg = str(insert_err).lower()
                if "duplicate" in error_msg or "unique" in error_msg or "constraint" in error_msg:
                    logger.warning(f"⚠️  Race condition detected for {pth.name}, file already exists")

                    # Find the existing file by SHA256
                    result = client.table("provider_file_uploads").select("*").eq(
                        "provider", provider
                    ).eq("sha256", sha256).execute()

                    if result.data and len(result.data) > 0:
                        existing_file_id = result.data[0]['provider_file_id']
                        # Increment reference count on existing file
                        self.increment_reference(existing_file_id, provider)
                        logger.info(f"✅ Incremented reference for existing file: {existing_file_id}")
                    else:
                        # Unexpected - re-raise
                        logger.error(f"Race condition but no existing file found for SHA256: {sha256[:16]}...")
                        raise insert_err
                else:
                    # Not a duplicate error - re-raise
                    raise insert_err

            # Update in-memory cache
            self.file_cache.set(sha256, provider.upper(), provider_file_id)

            return True

        except Exception as e:
            logger.error(f"Failed to register file: {e}")
            return False

    def get_deduplication_stats(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get deduplication statistics from database.

        Args:
            provider: Optional provider filter ('kimi' or 'glm')

        Returns:
            Dict with statistics: {
                'total_files': int,
                'total_references': int,
                'deduplicated_files': int,
                'storage_saved_bytes': int
            }
        """
        if not self.storage or not self.storage.enabled:
            return {
                'total_files': 0,
                'total_references': 0,
                'deduplicated_files': 0,
                'storage_saved_bytes': 0
            }

        try:
            client = self.storage.get_client()

            # Build query
            query = client.table("provider_file_uploads").select("reference_count, file_size_bytes")
            if provider:
                query = query.eq("provider", provider)

            result = query.execute()

            if not result.data:
                return {
                    'total_files': 0,
                    'total_references': 0,
                    'deduplicated_files': 0,
                    'storage_saved_bytes': 0
                }

            total_files = len(result.data)
            total_references = sum(r.get('reference_count', 1) for r in result.data)
            deduplicated_files = sum(1 for r in result.data if r.get('reference_count', 1) > 1)

            # Calculate storage saved (files with ref_count > 1 saved (ref_count - 1) * size)
            storage_saved = sum(
                (r.get('reference_count', 1) - 1) * r.get('file_size_bytes', 0)
                for r in result.data
                if r.get('reference_count', 1) > 1
            )

            return {
                'total_files': total_files,
                'total_references': total_references,
                'deduplicated_files': deduplicated_files,
                'storage_saved_bytes': storage_saved
            }

        except Exception as e:
            logger.error(f"Failed to get deduplication stats: {e}")
            return {
                'total_files': 0,
                'total_references': 0,
                'deduplicated_files': 0,
                'storage_saved_bytes': 0
            }



    def cleanup_unreferenced_files(
        self,
        provider: Optional[str] = None,
        grace_period_hours: int = 24,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Clean up files with reference_count=0 after grace period.

        This removes files that are no longer referenced by any uploads.
        Uses a grace period to handle temporary reference count drops.

        Args:
            provider: Provider to clean up ('kimi', 'glm', or None for all)
            grace_period_hours: Hours to wait before deleting (default 24)
            dry_run: If True, only report what would be deleted (default True)

        Returns:
            Dict with cleanup results: {
                'files_found': int,
                'files_deleted': int,
                'storage_freed_bytes': int,
                'errors': List[str]
            }
        """
        if not self.storage or not self.storage.enabled:
            logger.warning("Cleanup skipped: Supabase not available")
            return {
                'files_found': 0,
                'files_deleted': 0,
                'storage_freed_bytes': 0,
                'errors': ['Supabase not available']
            }

        cutoff_time = (datetime.utcnow() - timedelta(hours=grace_period_hours)).isoformat()

        try:
            client = self.storage.get_client()

            # Build query
            query = client.table("provider_file_uploads").select("*").eq("reference_count", 0).lt("last_used", cutoff_time)

            if provider:
                query = query.eq("provider", provider)

            result = query.execute()

            files_to_delete = result.data if result.data else []
            files_found = len(files_to_delete)
            storage_freed = sum(f.get('file_size_bytes', 0) for f in files_to_delete)

            logger.info(f"Found {files_found} unreferenced files (grace period: {grace_period_hours}h)")

            if dry_run:
                logger.info(f"DRY RUN: Would delete {files_found} files, freeing {storage_freed:,} bytes")
                return {
                    'files_found': files_found,
                    'files_deleted': 0,
                    'storage_freed_bytes': storage_freed,
                    'errors': [],
                    'dry_run': True
                }

            # Actually delete files
            deleted_count = 0
            errors = []

            for file_record in files_to_delete:
                try:
                    # Delete from Supabase Storage if exists
                    if file_record.get('supabase_file_id'):
                        try:
                            self.storage.delete_file(file_record['supabase_file_id'])
                        except Exception as storage_err:
                            logger.warning(f"Failed to delete from storage: {storage_err}")

                    # Delete database record
                    client.table("provider_file_uploads").delete().eq(
                        "provider_file_id", file_record['provider_file_id']
                    ).execute()

                    # Remove from cache
                    if file_record.get('sha256'):
                        self.file_cache.remove(file_record['sha256'], file_record['provider'].upper())

                    deleted_count += 1
                    logger.info(f"Deleted unreferenced file: {file_record['filename']}")

                except Exception as e:
                    error_msg = f"Failed to delete {file_record['filename']}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            logger.info(f"Cleanup complete: {deleted_count}/{files_found} files deleted, {storage_freed:,} bytes freed")

            return {
                'files_found': files_found,
                'files_deleted': deleted_count,
                'storage_freed_bytes': storage_freed,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                'files_found': 0,
                'files_deleted': 0,
                'storage_freed_bytes': 0,
                'errors': [str(e)]
            }
