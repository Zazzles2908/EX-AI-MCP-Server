"""
Unified File Manager

Central orchestrator for all file operations across multiple providers.
Handles deduplication, logging, error handling, and provider coordination.
"""

import asyncio
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import uuid
from cachetools import LRUCache

from src.file_management.models import (
    FileReference,
    FileUploadMetadata,
    FileOperationResult
)
from src.file_management.exceptions import (
    FileManagementError,
    FileUploadError,
    FileDuplicateError,
    FileNotFoundError,
    ProviderNotFoundError,
    FileValidationError
)
from src.file_management.providers.base import FileProviderInterface
from src.logging.file_operations_logger import FileOperationsLogger
from src.storage.supabase_client import SupabaseStorageManager


class UnifiedFileManager:
    """
    Unified File Manager - Single entry point for all file operations
    
    This class orchestrates file operations across multiple providers,
    handles deduplication, integrates logging, and ensures consistency.
    
    Architecture:
        - Dependency injection for testability
        - Async-first with sync wrappers for compatibility
        - Provider-agnostic file references
        - Comprehensive logging and error handling
    
    Attributes:
        storage: Supabase storage manager for metadata
        logger: File operations logger
        providers: Dictionary of available file providers
    
    Usage:
        # Async usage
        file_ref = await manager.upload_file_async("/path/to/file.txt")
        
        # Sync usage (backward compatibility)
        file_ref = manager.upload_file("/path/to/file.txt")
    """
    
    def __init__(
        self,
        storage: SupabaseStorageManager,
        logger: FileOperationsLogger,
        providers: Dict[str, FileProviderInterface]
    ):
        """
        Initialize Unified File Manager
        
        Args:
            storage: Supabase storage manager for metadata persistence
            logger: File operations logger for comprehensive logging
            providers: Dictionary mapping provider names to provider instances
        """
        self.storage = storage
        self.logger = logger
        self.providers = providers
        self._hash_cache = LRUCache(maxsize=1000)  # Bounded cache for file hashes
        self._executor = ThreadPoolExecutor(max_workers=4)  # For sync wrappers
    
    # ========================================================================
    # PUBLIC API - ASYNC METHODS
    # ========================================================================
    
    async def upload_file_async(
        self,
        file_path: str,
        metadata: Optional[FileUploadMetadata] = None,
        provider: str = "kimi",
        allow_duplicates: bool = False
    ) -> FileReference:
        """
        Upload a file asynchronously with deduplication
        
        Args:
            file_path: Absolute path to the file to upload
            metadata: Upload metadata (purpose, context, etc.)
            provider: Provider to use for upload (default: "kimi")
            allow_duplicates: If True, skip deduplication check
            
        Returns:
            FileReference for the uploaded file
            
        Raises:
            FileUploadError: If upload fails
            FileDuplicateError: If file already exists and allow_duplicates=False
            ProviderNotFoundError: If requested provider not available
            FileNotFoundError: If file doesn't exist locally
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Log operation start
            self.logger.log_upload(
                file_path=file_path,
                file_size=0,  # Will update after validation
                user_id=metadata.user_id if metadata else None,
                success=False,
                provider=provider,
                operation_id=operation_id
            )
            
            # Validate file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(file_path=file_path)
            
            # Get file size
            file_size = file_path_obj.stat().st_size
            
            # Calculate file hash
            file_hash = await self._calculate_file_hash_async(file_path)
            
            # Check for duplicates (unless explicitly allowed)
            if not allow_duplicates:
                existing = await self._find_duplicate_async(file_hash)
                if existing:
                    self.logger.log_upload(
                        file_path=file_path,
                        file_size=file_size,
                        user_id=metadata.user_id if metadata else None,
                        success=True,
                        provider=provider,
                        file_id=existing.internal_id,
                        operation_id=operation_id,
                        duplicate=True
                    )
                    raise FileDuplicateError(
                        f"File already exists: {existing.internal_id}",
                        existing
                    )
            
            # Get provider instance
            provider_instance = self.providers.get(provider)
            if not provider_instance:
                available = list(self.providers.keys())
                raise ProviderNotFoundError(provider, available)
            
            # Check provider availability
            if not provider_instance.is_available:
                raise FileUploadError(
                    f"Provider {provider} is not available",
                    provider,
                    "PROVIDER_UNAVAILABLE",
                    retryable=True
                )
            
            # Prepare metadata
            if metadata is None:
                metadata = FileUploadMetadata()
            
            # Upload to provider
            file_ref = await provider_instance.upload_file(file_path, metadata)
            
            # Store in Supabase
            await self._store_file_reference_async(file_ref)
            
            # Calculate duration
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log success
            self.logger.log_upload(
                file_path=file_path,
                file_size=file_size,
                user_id=metadata.user_id if metadata else None,
                success=True,
                provider=provider,
                file_id=file_ref.internal_id,
                operation_id=operation_id,
                duration_ms=duration_ms
            )
            
            return file_ref
            
        except (FileDuplicateError, FileNotFoundError, ProviderNotFoundError):
            # Re-raise these exceptions as-is
            raise
            
        except Exception as e:
            # Log error
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_upload(
                file_path=file_path,
                file_size=0,
                user_id=metadata.user_id if metadata else None,
                success=False,
                provider=provider,
                error=str(e),
                operation_id=operation_id,
                duration_ms=duration_ms
            )
            
            # Wrap in FileUploadError if not already a file management error
            if isinstance(e, FileManagementError):
                raise
            else:
                raise FileUploadError(
                    f"Upload failed: {str(e)}",
                    provider,
                    "UPLOAD_FAILED",
                    retryable=True,
                    file_path=file_path
                ) from e
    
    async def download_file_async(
        self,
        file_ref: FileReference,
        destination: str
    ) -> bool:
        """
        Download a file asynchronously
        
        Args:
            file_ref: Reference to the file to download
            destination: Absolute path where file should be saved
            
        Returns:
            True if download successful
            
        Raises:
            FileDownloadError: If download fails
            ProviderNotFoundError: If provider not available
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Get provider instance
            provider_instance = self.providers.get(file_ref.provider)
            if not provider_instance:
                available = list(self.providers.keys())
                raise ProviderNotFoundError(file_ref.provider, available)
            
            # Download from provider
            success = await provider_instance.download_file(file_ref, destination)
            
            # Calculate duration
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log operation
            self.logger.log_download(
                file_path=destination,
                file_size=file_ref.size,
                user_id=None,
                success=success,
                provider=file_ref.provider,
                file_id=file_ref.internal_id,
                operation_id=operation_id,
                duration_ms=duration_ms
            )
            
            return success
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_download(
                file_path=destination,
                file_size=file_ref.size,
                user_id=None,
                success=False,
                provider=file_ref.provider,
                error=str(e),
                operation_id=operation_id,
                duration_ms=duration_ms
            )
            raise
    
    async def delete_file_async(
        self,
        file_ref: FileReference
    ) -> bool:
        """
        Delete a file asynchronously
        
        Args:
            file_ref: Reference to the file to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            FileDeleteError: If deletion fails
            ProviderNotFoundError: If provider not available
        """
        operation_id = str(uuid.uuid4())
        
        try:
            # Get provider instance
            provider_instance = self.providers.get(file_ref.provider)
            if not provider_instance:
                available = list(self.providers.keys())
                raise ProviderNotFoundError(file_ref.provider, available)
            
            # Delete from provider
            success = await provider_instance.delete_file(file_ref)
            
            # Log operation
            self.logger.log_delete(
                file_path=file_ref.original_name,
                file_size=file_ref.size,
                user_id=None,
                success=success,
                provider=file_ref.provider,
                file_id=file_ref.internal_id,
                operation_id=operation_id
            )
            
            return success
            
        except Exception as e:
            self.logger.log_delete(
                file_path=file_ref.original_name,
                file_size=file_ref.size,
                user_id=None,
                success=False,
                provider=file_ref.provider,
                error=str(e),
                operation_id=operation_id
            )
            raise

    # ========================================================================
    # PUBLIC API - SYNC WRAPPERS (Backward Compatibility)
    # ========================================================================

    def upload_file(
        self,
        file_path: str,
        metadata: Optional[FileUploadMetadata] = None,
        provider: str = "kimi",
        allow_duplicates: bool = False
    ) -> FileReference:
        """
        Upload a file synchronously (backward compatibility wrapper)

        Uses thread pool executor to safely run async code from sync context.
        This prevents issues with existing event loops.

        Args:
            file_path: Absolute path to the file to upload
            metadata: Upload metadata (purpose, context, etc.)
            provider: Provider to use for upload (default: "kimi")
            allow_duplicates: If True, skip deduplication check

        Returns:
            FileReference for the uploaded file

        Raises:
            RuntimeError: If called from within an async context
        """
        # Check if we're in an async context
        try:
            asyncio.get_running_loop()
            # We're in an async context - user should use async method
            raise RuntimeError(
                "Cannot call upload_file() from async context. "
                "Use upload_file_async() instead."
            )
        except RuntimeError as e:
            if "Cannot call upload_file()" in str(e):
                raise
            # No running loop - safe to proceed

        # Use thread pool executor for safe async execution
        future = self._executor.submit(
            asyncio.run,
            self.upload_file_async(file_path, metadata, provider, allow_duplicates)
        )
        return future.result()

    def download_file(
        self,
        file_ref: FileReference,
        destination: str
    ) -> bool:
        """
        Download a file synchronously (backward compatibility wrapper)

        Uses thread pool executor to safely run async code from sync context.

        Args:
            file_ref: Reference to the file to download
            destination: Absolute path where file should be saved

        Returns:
            True if download successful

        Raises:
            RuntimeError: If called from within an async context
        """
        # Check if we're in an async context
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot call download_file() from async context. "
                "Use download_file_async() instead."
            )
        except RuntimeError as e:
            if "Cannot call download_file()" in str(e):
                raise

        # Use thread pool executor
        future = self._executor.submit(
            asyncio.run,
            self.download_file_async(file_ref, destination)
        )
        return future.result()

    def delete_file(
        self,
        file_ref: FileReference
    ) -> bool:
        """
        Delete a file synchronously (backward compatibility wrapper)

        Uses thread pool executor to safely run async code from sync context.

        Args:
            file_ref: Reference to the file to delete

        Returns:
            True if deletion successful

        Raises:
            RuntimeError: If called from within an async context
        """
        # Check if we're in an async context
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot call delete_file() from async context. "
                "Use delete_file_async() instead."
            )
        except RuntimeError as e:
            if "Cannot call delete_file()" in str(e):
                raise

        # Use thread pool executor
        future = self._executor.submit(
            asyncio.run,
            self.delete_file_async(file_ref)
        )
        return future.result()

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    async def _calculate_file_hash_async(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file asynchronously

        Args:
            file_path: Path to the file

        Returns:
            SHA256 hash as hexadecimal string
        """
        # Check cache first
        if file_path in self._hash_cache:
            return self._hash_cache[file_path]

        # Calculate hash
        hash_sha256 = hashlib.sha256()

        # Read file in chunks to avoid memory issues with large files
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)

        result = hash_sha256.hexdigest()

        # Cache result
        self._hash_cache[file_path] = result

        return result

    async def _find_duplicate_async(self, file_hash: str) -> Optional[FileReference]:
        """
        Find existing file with same hash

        Args:
            file_hash: SHA256 hash to search for

        Returns:
            FileReference if duplicate found, None otherwise
        """
        # Check Supabase first
        try:
            result = self.storage.client.table("files").select("*").eq("sha256", file_hash).execute()

            if result.data and len(result.data) > 0:
                # Convert to FileReference
                file_data = result.data[0]
                return FileReference.from_supabase_dict(file_data)
        except Exception as e:
            # Log error but don't fail the operation
            self.logger.logger.error(f"Error checking for duplicates: {e}")

        return None

    async def _store_file_reference_async(self, file_ref: FileReference) -> None:
        """
        Store file reference in Supabase

        Args:
            file_ref: File reference to store
        """
        try:
            # Convert to Supabase format
            data = file_ref.to_supabase_dict()

            # Insert into database
            self.storage.client.table("files").insert(data).execute()

        except Exception as e:
            # Log error
            self.logger.logger.error(f"Error storing file reference: {e}")
            raise FileUploadError(
                f"Failed to store file metadata: {str(e)}",
                file_ref.provider,
                "METADATA_STORAGE_FAILED",
                retryable=True
            ) from e

    def get_provider_status(self) -> Dict[str, bool]:
        """
        Get availability status of all providers

        Returns:
            Dictionary mapping provider names to availability status
        """
        return {
            name: provider.is_available
            for name, provider in self.providers.items()
        }

    def list_available_providers(self) -> List[str]:
        """
        List all available providers

        Returns:
            List of provider names that are currently available
        """
        return [
            name
            for name, provider in self.providers.items()
            if provider.is_available
        ]

