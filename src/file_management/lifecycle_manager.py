"""
File Lifecycle Manager
Handles periodic cleanup of expired and orphaned files

PHASE 2 HIGH - Task 3.1: Lifecycle Management
- Periodic cleanup task (retention policy: 30 days)
- Orphaned file detection
- Race condition prevention
- Integration with graceful shutdown

Author: EX-AI MCP Server
Date: 2025-11-02
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config.file_management import FileManagementConfig
from supabase import Client
from src.monitoring.file_metrics import record_file_deletion

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    """Result of a cleanup operation"""
    files_marked: int
    files_deleted: int
    bytes_freed: int
    errors: List[str]
    duration: float


class FileLifecycleManager:
    """
    Manages file lifecycle including periodic cleanup and deletion.
    
    Features:
    - Periodic cleanup based on retention policy
    - Orphaned file detection
    - Race condition prevention (excludes uploading files)
    - Graceful shutdown support
    - Metrics collection
    """
    
    def __init__(
        self,
        supabase_client: Client,
        retention_days: Optional[int] = None,
        cleanup_interval_hours: Optional[int] = None
    ):
        """
        Initialize lifecycle manager.

        Args:
            supabase_client: Supabase client instance
            retention_days: Days to retain files (default from config)
            cleanup_interval_hours: Hours between cleanup runs (default from config)
        """
        self.supabase = supabase_client
        self.retention_days = retention_days or FileManagementConfig.RETENTION_DAYS
        self.cleanup_interval_hours = cleanup_interval_hours or FileManagementConfig.CLEANUP_INTERVAL_HOURS
        self.running = False
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info(
            f"FileLifecycleManager initialized: "
            f"retention={self.retention_days}d, "
            f"interval={self.cleanup_interval_hours}h"
        )
    
    async def start(self) -> None:
        """Start the periodic cleanup task"""
        if self.running:
            logger.warning("Lifecycle manager already running")
            return
        
        self.running = True
        self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Lifecycle manager started")
    
    async def stop(self) -> None:
        """Stop the periodic cleanup task gracefully"""
        if not self.running:
            return
        
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Lifecycle manager stopped")
    
    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup task that runs at configured intervals"""
        while self.running:
            try:
                # Wait for the cleanup interval
                await asyncio.sleep(self.cleanup_interval_hours * 3600)
                
                # Run cleanup
                logger.info("Starting periodic cleanup")
                result = await self.cleanup_expired_files()
                
                logger.info(
                    f"Periodic cleanup complete: "
                    f"marked={result.files_marked}, "
                    f"deleted={result.files_deleted}, "
                    f"freed={result.bytes_freed} bytes, "
                    f"duration={result.duration:.2f}s"
                )
                
            except asyncio.CancelledError:
                logger.info("Periodic cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}", exc_info=True)
                # Continue running despite errors
    
    async def cleanup_expired_files(self, dry_run: bool = False) -> CleanupResult:
        """
        Clean up files that have exceeded the retention period.
        
        Args:
            dry_run: If True, only identify files without deleting
            
        Returns:
            CleanupResult with statistics
        """
        start_time = datetime.now()
        files_marked = 0
        files_deleted = 0
        bytes_freed = 0
        errors = []
        
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Query for expired files
            # CRITICAL: Exclude files with status='uploading' to prevent race conditions
            # Note: Supabase Python client is synchronous, so we run in thread pool
            response = await asyncio.to_thread(
                lambda: self.supabase.table("provider_file_uploads").select("*").filter(
                    "deleted_at", "is", None  # Not already deleted
                ).filter(
                    "upload_status", "neq", "uploading"  # Not currently uploading
                ).filter(
                    "upload_status", "neq", "pending"  # Not pending upload
                ).filter(
                    "last_used", "lt", cutoff_date.isoformat()  # Older than retention period
                ).execute()
            )
            expired_files = response.data if response.data else []
            
            logger.info(f"Found {len(expired_files)} expired files")
            
            if dry_run:
                logger.info("DRY RUN: Would mark/delete the following files:")
                for file in expired_files:
                    logger.info(
                        f"  - {file['filename']} ({file['file_size_bytes']} bytes, "
                        f"last_used={file['last_used']})"
                    )
                files_marked = len(expired_files)
            else:
                # Mark files as deleted (soft delete)
                for file in expired_files:
                    try:
                        await self._soft_delete_file(
                            file['id'],
                            file['provider'],
                            "expired"
                        )
                        files_marked += 1
                        bytes_freed += file.get('file_size_bytes', 0)
                        
                        # Record metrics
                        record_file_deletion(file['provider'], "expired")
                        
                    except Exception as e:
                        error_msg = f"Failed to delete file {file['id']}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
            
        except Exception as e:
            error_msg = f"Error during cleanup: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return CleanupResult(
            files_marked=files_marked,
            files_deleted=files_deleted,
            bytes_freed=bytes_freed,
            errors=errors,
            duration=duration
        )
    
    async def cleanup_orphaned_files(self, dry_run: bool = False) -> CleanupResult:
        """
        Clean up orphaned files (failed uploads older than 7 days).
        
        Args:
            dry_run: If True, only identify files without deleting
            
        Returns:
            CleanupResult with statistics
        """
        start_time = datetime.now()
        files_marked = 0
        files_deleted = 0
        bytes_freed = 0
        errors = []
        
        try:
            # Calculate cutoff date (7 days for orphaned files)
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # Query for orphaned files
            # Note: Supabase Python client is synchronous, so we run in thread pool
            response = await asyncio.to_thread(
                lambda: self.supabase.table("provider_file_uploads").select("*").filter(
                    "deleted_at", "is", None  # Not already deleted
                ).filter(
                    "upload_status", "eq", "failed"  # Failed uploads
                ).filter(
                    "created_at", "lt", cutoff_date.isoformat()  # Older than 7 days
                ).execute()
            )
            orphaned_files = response.data if response.data else []
            
            logger.info(f"Found {len(orphaned_files)} orphaned files")
            
            if dry_run:
                logger.info("DRY RUN: Would mark/delete the following orphaned files:")
                for file in orphaned_files:
                    logger.info(
                        f"  - {file['filename']} ({file['file_size_bytes']} bytes, "
                        f"created={file['created_at']}, error={file.get('error_message', 'N/A')})"
                    )
                files_marked = len(orphaned_files)
            else:
                # Mark files as deleted (soft delete)
                for file in orphaned_files:
                    try:
                        await self._soft_delete_file(
                            file['id'],
                            file['provider'],
                            "orphaned"
                        )
                        files_marked += 1
                        bytes_freed += file.get('file_size_bytes', 0)
                        
                        # Record metrics
                        record_file_deletion(file['provider'], "orphaned")
                        
                    except Exception as e:
                        error_msg = f"Failed to delete orphaned file {file['id']}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
            
        except Exception as e:
            error_msg = f"Error during orphaned cleanup: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return CleanupResult(
            files_marked=files_marked,
            files_deleted=files_deleted,
            bytes_freed=bytes_freed,
            errors=errors,
            duration=duration
        )
    
    async def _soft_delete_file(
        self,
        file_id: str,
        provider: str,
        deletion_reason: str
    ) -> None:
        """
        Soft delete a file by setting deleted_at and deletion_reason.

        Args:
            file_id: File ID to delete
            provider: Provider name
            deletion_reason: Reason for deletion
        """
        # Note: Supabase Python client is synchronous, so we run in thread pool
        await asyncio.to_thread(
            lambda: self.supabase.table("provider_file_uploads").update({
                "deleted_at": datetime.now().isoformat(),
                "deletion_reason": deletion_reason,
                "upload_status": "deleted",
                "updated_at": datetime.now().isoformat()
            }).eq("id", file_id).execute()
        )

        logger.debug(f"Soft deleted file {file_id}: reason={deletion_reason}")

