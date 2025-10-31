"""
File Management Migration Facade

Provides backward-compatible routing between legacy file handlers and the new
UnifiedFileManager. Enables gradual migration with feature flags and rollout control.

Architecture: Facade Pattern with Feature Flag Routing
Date: 2025-10-22
Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)
"""

import logging
import asyncio
import random
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from time import time

from src.file_management.manager import UnifiedFileManager
from src.file_management.models import FileReference, FileUploadMetadata, FileOperationResult
from src.file_management.exceptions import FileManagementError
from src.file_management.rollout_manager import RolloutManager

logger = logging.getLogger(__name__)


class ShadowModeMetrics:
    """
    In-memory metrics for shadow mode operations.

    Tracks comparison counts, errors, and discrepancies for monitoring
    shadow mode health and triggering circuit breakers if needed.
    """

    def __init__(self):
        self.comparison_count = 0
        self.error_count = 0
        self.discrepancy_count = 0
        self.last_reset = datetime.now()

    def record_comparison(self, status: str):
        """Record a shadow mode comparison result."""
        self.comparison_count += 1
        if status == "error":
            self.error_count += 1
        elif status == "discrepancy":
            self.discrepancy_count += 1

    def get_error_rate(self) -> float:
        """Calculate current error rate."""
        if self.comparison_count == 0:
            return 0.0
        return self.error_count / self.comparison_count

    def reset(self):
        """Reset all metrics."""
        self.comparison_count = 0
        self.error_count = 0
        self.discrepancy_count = 0
        self.last_reset = datetime.now()


class FileManagementFacade:
    """
    Facade that routes file operations between legacy and unified implementations.
    
    This class provides a single entry point for all file operations while allowing
    gradual migration from legacy handlers to the UnifiedFileManager. It uses feature
    flags and rollout percentages to control which implementation handles each request.
    
    Key Features:
    - Zero-downtime migration
    - Per-tool feature flags
    - Percentage-based rollout
    - Automatic fallback to legacy on errors
    - Comprehensive logging and metrics
    """
    
    def __init__(
        self,
        unified_manager: UnifiedFileManager,
        rollout_manager: RolloutManager,
        config: Any,
        legacy_handlers: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the migration facade.
        
        Args:
            unified_manager: The new UnifiedFileManager instance
            rollout_manager: Manager for rollout percentage decisions
            config: Configuration object with feature flags
            legacy_handlers: Dictionary of legacy handler instances (optional)
        """
        self.unified_manager = unified_manager
        self.rollout_manager = rollout_manager
        self.config = config
        self.legacy_handlers = legacy_handlers or {}
        self.shadow_metrics = ShadowModeMetrics()

        logger.info(
            "FileManagementFacade initialized",
            extra={
                "unified_enabled": config.ENABLE_UNIFIED_MANAGER,
                "shadow_mode_enabled": config.ENABLE_SHADOW_MODE,
                "legacy_handlers": list(self.legacy_handlers.keys())
            }
        )
    
    async def upload_file(
        self,
        file_path: str,
        metadata: Optional[FileUploadMetadata] = None,
        provider: str = "kimi",
        context_id: Optional[str] = None,
        user_id: Optional[str] = None,
        allow_duplicates: bool = False
    ) -> FileOperationResult:
        """
        Upload a file using either unified or legacy implementation.

        Triggers shadow mode comparison in background if enabled and sampled.

        Args:
            file_path: Path to the file to upload
            metadata: Optional metadata for the file
            provider: Provider to use ('kimi' or 'glm')
            context_id: Optional context ID for the upload
            user_id: Optional user ID for rollout decisions
            allow_duplicates: Whether to allow duplicate uploads

        Returns:
            FileOperationResult with upload details

        Raises:
            FileManagementError: If upload fails in both unified and legacy
        """
        tool_name = f"{provider}_upload"
        use_unified = self._should_use_unified(tool_name, user_id)

        logger.info(
            f"Upload request routing decision",
            extra={
                "file_path": file_path,
                "provider": provider,
                "use_unified": use_unified,
                "user_id": user_id
            }
        )

        # Execute primary operation
        if use_unified:
            try:
                result = await self.unified_manager.upload_file_async(
                    file_path=file_path,
                    metadata=metadata,
                    provider=provider,
                    allow_duplicates=allow_duplicates
                )

                logger.info(
                    "Unified upload successful",
                    extra={
                        "file_path": file_path,
                        "provider": provider,
                        "file_id": result.file_reference.internal_id if result.success else None
                    }
                )

            except Exception as e:
                logger.error(
                    f"Unified upload failed, attempting fallback",
                    extra={
                        "file_path": file_path,
                        "provider": provider,
                        "error": str(e)
                    },
                    exc_info=True
                )

                # Fallback to legacy if enabled
                if self.config.ENABLE_FALLBACK_TO_LEGACY:
                    result = await self._legacy_upload(
                        file_path=file_path,
                        metadata=metadata,
                        provider=provider,
                        context_id=context_id
                    )
                else:
                    raise
        else:
            # Use legacy implementation
            result = await self._legacy_upload(
                file_path=file_path,
                metadata=metadata,
                provider=provider,
                context_id=context_id
            )

        # Trigger shadow mode comparison in background (fire-and-forget)
        if self._should_run_shadow_mode():
            asyncio.create_task(
                self._run_shadow_mode_comparison(
                    file_path=file_path,
                    metadata=metadata,
                    provider=provider,
                    context_id=context_id,
                    allow_duplicates=allow_duplicates,
                    primary_result=result,
                    primary_used_unified=use_unified
                )
            )

        return result
    
    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> FileOperationResult:
        """
        Download a file using either unified or legacy implementation.
        
        Args:
            file_id: ID of the file to download
            destination: Optional destination path
            user_id: Optional user ID for rollout decisions
            
        Returns:
            FileOperationResult with download details
        """
        use_unified = self._should_use_unified("download", user_id)
        
        if use_unified:
            try:
                result = await self.unified_manager.download_file_async(
                    file_id=file_id,
                    destination=destination
                )
                return result
            except Exception as e:
                logger.error(f"Unified download failed: {e}", exc_info=True)
                if self.config.ENABLE_FALLBACK_TO_LEGACY:
                    return await self._legacy_download(file_id, destination)
                else:
                    raise
        else:
            return await self._legacy_download(file_id, destination)
    
    async def delete_file(
        self,
        file_id: str,
        user_id: Optional[str] = None
    ) -> FileOperationResult:
        """
        Delete a file using either unified or legacy implementation.
        
        Args:
            file_id: ID of the file to delete
            user_id: Optional user ID for rollout decisions
            
        Returns:
            FileOperationResult with deletion details
        """
        use_unified = self._should_use_unified("delete", user_id)
        
        if use_unified:
            try:
                result = await self.unified_manager.delete_file_async(file_id)
                return result
            except Exception as e:
                logger.error(f"Unified delete failed: {e}", exc_info=True)
                if self.config.ENABLE_FALLBACK_TO_LEGACY:
                    return await self._legacy_delete(file_id)
                else:
                    raise
        else:
            return await self._legacy_delete(file_id)
    
    def _should_use_unified(self, tool_name: str, user_id: Optional[str] = None) -> bool:
        """
        Determine if request should use unified implementation.
        
        Args:
            tool_name: Name of the tool/operation
            user_id: Optional user ID for consistent routing
            
        Returns:
            True if should use unified, False for legacy
        """
        if not self.config.ENABLE_UNIFIED_MANAGER:
            return False
        
        return self.rollout_manager.should_use_unified(tool_name, user_id)
    
    async def _legacy_upload(
        self,
        file_path: str,
        metadata: Optional[FileUploadMetadata],
        provider: str,
        context_id: Optional[str]
    ) -> FileOperationResult:
        """
        Upload using legacy handler.

        Routes to the appropriate legacy upload handler based on provider.
        Currently supports:
        - kimi: KimiUploadFilesTool
        - glm: GLM file upload (future)
        """
        logger.info(
            f"Using legacy upload handler",
            extra={"file_path": file_path, "provider": provider}
        )

        try:
            if provider == "kimi":
                return await self._legacy_kimi_upload(file_path, metadata)
            elif provider == "glm":
                return await self._legacy_glm_upload(file_path, metadata)
            else:
                return FileOperationResult(
                    success=False,
                    error=f"Unsupported provider for legacy upload: {provider}"
                )
        except Exception as e:
            logger.error(
                f"Legacy upload failed",
                extra={"file_path": file_path, "provider": provider, "error": str(e)},
                exc_info=True
            )
            return FileOperationResult(
                success=False,
                error=f"Legacy upload error: {str(e)}"
            )

    async def _legacy_kimi_upload(
        self,
        file_path: str,
        metadata: Optional[FileUploadMetadata]
    ) -> FileOperationResult:
        """
        Upload using Supabase hub directly.

        Phase A2 Cleanup: Replaced KimiUploadFilesTool with direct upload_file_with_provider() call.
        This eliminates the redundant tool wrapper layer.
        """
        try:
            # Import Supabase hub function
            from tools.supabase_upload import upload_file_with_provider
            from src.storage.supabase_client import get_storage_manager

            # Prepare arguments
            purpose = metadata.purpose if metadata else "file-extract"
            user_id = metadata.user_id if metadata and hasattr(metadata, 'user_id') else "system"

            # Get Supabase client
            storage = get_storage_manager()
            supabase_client = storage.get_client()

            # Call Supabase hub directly (sync method, so run in thread)
            import asyncio
            result = await asyncio.to_thread(
                upload_file_with_provider,
                supabase_client=supabase_client,
                file_path=file_path,
                provider="kimi",
                user_id=user_id
            )

            # Convert result to FileOperationResult
            if result:
                # Create FileReference from Supabase hub result
                from src.file_management.models import FileReference
                file_ref = FileReference(
                    internal_id=result.get("supabase_file_id"),
                    provider_id=result.get("kimi_file_id"),  # Kimi file ID
                    provider="kimi",
                    file_hash=result.get("sha256"),
                    size=result.get("size_bytes"),
                    mime_type=result.get("mime_type"),
                    original_name=result.get("filename"),
                    created_at=result.get("created_at"),
                    metadata={"supabase_hub_upload": True}
                )

                return FileOperationResult(
                    success=True,
                    file_reference=file_ref
                )
            else:
                return FileOperationResult(
                    success=False,
                    error="Kimi upload via Supabase hub returned no results"
                )

        except Exception as e:
            logger.error(f"Kimi upload via Supabase hub failed: {e}", exc_info=True)
            return FileOperationResult(
                success=False,
                error=f"Kimi upload error: {str(e)}"
            )

    async def _legacy_glm_upload(
        self,
        file_path: str,
        metadata: Optional[FileUploadMetadata]
    ) -> FileOperationResult:
        """
        Upload using legacy GLM file upload.

        Placeholder for future GLM legacy handler integration.
        """
        logger.warning("GLM legacy upload not yet implemented")
        return FileOperationResult(
            success=False,
            error="GLM legacy upload not yet implemented"
        )
    
    async def _legacy_download(
        self,
        file_id: str,
        destination: Optional[str]
    ) -> FileOperationResult:
        """
        Download using MCP storage adapter (Phase B implementation).

        Phase B: Uses MCPStorageAdapter (Python wrapper)
        Phase C: Will use pure MCP storage tools
        """
        logger.info(f"Using MCP download handler", extra={"file_id": file_id})

        try:
            # Import MCP adapter
            from src.file_management.mcp_storage_adapter import MCPStorageAdapter

            # Get file metadata from database
            from src.storage.supabase_client import SupabaseStorageManager
            storage = SupabaseStorageManager()
            client = storage.get_client()

            file_result = client.table("files").select(
                "id, storage_path, original_name, size_bytes"
            ).eq("id", file_id).execute()

            if not file_result.data or len(file_result.data) == 0:
                return FileOperationResult(
                    success=False,
                    error=f"File {file_id} not found in database"
                )

            file_info = file_result.data[0]
            storage_path = file_info.get("storage_path")

            # Download using MCP adapter
            mcp_adapter = MCPStorageAdapter()
            download_result = mcp_adapter.download_file(
                file_id=file_id,
                storage_path=storage_path
            )

            if not download_result.success:
                return FileOperationResult(
                    success=False,
                    error=download_result.error
                )

            # Save to destination if provided
            if destination:
                with open(destination, 'wb') as f:
                    f.write(download_result.data)
                logger.info(f"File saved to {destination}")

            return FileOperationResult(
                success=True,
                file_reference=None,  # Download doesn't return file reference
                metadata={
                    "file_id": file_id,
                    "size_bytes": len(download_result.data),
                    "destination": destination
                }
            )

        except Exception as e:
            logger.error(f"MCP download failed: {e}")
            return FileOperationResult(
                success=False,
                error=str(e)
            )
    
    async def _legacy_delete(self, file_id: str) -> FileOperationResult:
        """
        Delete using MCP storage adapter (Phase B implementation).

        Phase B: Uses MCPStorageAdapter (Python wrapper)
        Phase C: Will use pure MCP storage tools
        """
        logger.info(f"Using MCP delete handler", extra={"file_id": file_id})

        try:
            # Import MCP adapter
            from src.file_management.mcp_storage_adapter import MCPStorageAdapter

            # Get file metadata from database
            from src.storage.supabase_client import SupabaseStorageManager
            storage = SupabaseStorageManager()
            client = storage.get_client()

            file_result = client.table("files").select(
                "id, storage_path"
            ).eq("id", file_id).execute()

            if not file_result.data or len(file_result.data) == 0:
                return FileOperationResult(
                    success=False,
                    error=f"File {file_id} not found in database"
                )

            file_info = file_result.data[0]
            storage_path = file_info.get("storage_path")

            # Delete using MCP adapter
            mcp_adapter = MCPStorageAdapter()
            delete_result = mcp_adapter.delete_file(
                file_id=file_id,
                storage_path=storage_path
            )

            if not delete_result.success:
                return FileOperationResult(
                    success=False,
                    error=delete_result.error
                )

            logger.info(f"File {file_id} deleted successfully")

            return FileOperationResult(
                success=True,
                metadata={
                    "file_id": file_id,
                    "storage_path": storage_path
                }
            )

        except Exception as e:
            logger.error(f"MCP delete failed: {e}")
            return FileOperationResult(
                success=False,
                error=str(e)
            )

    # ========================================================================
    # SHADOW MODE IMPLEMENTATION
    # ========================================================================
    # Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)
    # Date: 2025-10-22

    def _should_run_shadow_mode(self) -> bool:
        """
        Determine if shadow mode should run for this operation.

        Checks:
        1. Shadow mode is enabled in config
        2. Random sampling based on SHADOW_MODE_SAMPLE_RATE

        Returns:
            bool: True if shadow mode should run
        """
        if not self.config.ENABLE_SHADOW_MODE:
            return False

        # Random sampling based on sample rate
        return random.random() < self.config.SHADOW_MODE_SAMPLE_RATE

    async def _run_shadow_mode_comparison(
        self,
        file_path: str,
        metadata: Optional[FileUploadMetadata],
        provider: str,
        context_id: Optional[str],
        allow_duplicates: bool,
        primary_result: FileOperationResult,
        primary_used_unified: bool
    ):
        """
        Execute shadow mode comparison in background.

        Runs the alternate implementation (unified if primary was legacy,
        legacy if primary was unified) and compares results.

        This method is fire-and-forget and should never affect the primary operation.

        Args:
            file_path: Path to the file
            metadata: File metadata
            provider: Provider name
            context_id: Context ID
            allow_duplicates: Allow duplicates flag
            primary_result: Result from primary operation
            primary_used_unified: Whether primary used unified implementation
        """
        start_time = time()

        try:
            # Execute shadow operation (opposite of primary)
            if primary_used_unified:
                # Primary was unified, run legacy as shadow
                shadow_result = await self._legacy_upload(
                    file_path=file_path,
                    metadata=metadata,
                    provider=provider,
                    context_id=context_id
                )
                shadow_impl = "legacy"
            else:
                # Primary was legacy, run unified as shadow
                shadow_result = await self.unified_manager.upload_file_async(
                    file_path=file_path,
                    metadata=metadata,
                    provider=provider,
                    allow_duplicates=allow_duplicates
                )
                shadow_impl = "unified"

            # Calculate timing
            duration = time() - start_time

            # Compare results
            comparison = self._compare_results(primary_result, shadow_result)

            # Log comparison
            await self._log_shadow_mode_comparison(
                file_path=file_path,
                provider=provider,
                primary_impl="unified" if primary_used_unified else "legacy",
                shadow_impl=shadow_impl,
                comparison=comparison,
                duration=duration
            )

            # Update metrics
            if comparison["has_errors"]:
                self.shadow_metrics.record_comparison("error")
            elif not comparison["results_match"]:
                self.shadow_metrics.record_comparison("discrepancy")
            else:
                self.shadow_metrics.record_comparison("success")

        except asyncio.TimeoutError:
            logger.warning(
                "Shadow mode comparison timed out",
                extra={"file_path": file_path, "provider": provider}
            )
            self.shadow_metrics.record_comparison("error")

        except Exception as e:
            logger.error(
                f"Shadow mode comparison failed: {e}",
                extra={"file_path": file_path, "provider": provider},
                exc_info=True
            )
            self.shadow_metrics.record_comparison("error")

    def _compare_results(
        self,
        primary_result: FileOperationResult,
        shadow_result: FileOperationResult
    ) -> Dict[str, Any]:
        """
        Compare results from primary and shadow implementations.

        Args:
            primary_result: Result from primary implementation
            shadow_result: Result from shadow implementation

        Returns:
            Dictionary with comparison details:
            - results_match: bool - Whether results match
            - has_errors: bool - Whether either result has errors
            - discrepancies: List[str] - List of specific discrepancies
            - primary_success: bool - Primary operation success
            - shadow_success: bool - Shadow operation success
        """
        discrepancies = []
        has_errors = False

        # Check for errors in either result
        if not primary_result.success:
            has_errors = True
            discrepancies.append(f"Primary failed: {primary_result.error}")

        if not shadow_result.success:
            has_errors = True
            discrepancies.append(f"Shadow failed: {shadow_result.error}")

        # If both failed, they "match" in failure
        if not primary_result.success and not shadow_result.success:
            return {
                "results_match": True,
                "has_errors": True,
                "discrepancies": discrepancies,
                "primary_success": False,
                "shadow_success": False,
                "match_reason": "Both implementations failed"
            }

        # If one succeeded and one failed, they don't match
        if primary_result.success != shadow_result.success:
            discrepancies.append(
                f"Success mismatch: primary={primary_result.success}, shadow={shadow_result.success}"
            )
            return {
                "results_match": False,
                "has_errors": has_errors,
                "discrepancies": discrepancies,
                "primary_success": primary_result.success,
                "shadow_success": shadow_result.success
            }

        # Both succeeded - compare file references
        if primary_result.file_reference and shadow_result.file_reference:
            primary_ref = primary_result.file_reference
            shadow_ref = shadow_result.file_reference

            # Compare provider IDs (if both have them)
            if primary_ref.provider_id and shadow_ref.provider_id:
                if primary_ref.provider_id != shadow_ref.provider_id:
                    discrepancies.append(
                        f"Provider ID mismatch: primary={primary_ref.provider_id}, "
                        f"shadow={shadow_ref.provider_id}"
                    )

            # Compare file sizes (if both have them)
            if primary_ref.size and shadow_ref.size:
                if primary_ref.size != shadow_ref.size:
                    discrepancies.append(
                        f"Size mismatch: primary={primary_ref.size}, shadow={shadow_ref.size}"
                    )

            # Compare file hashes (if both have them)
            if primary_ref.file_hash and shadow_ref.file_hash:
                if primary_ref.file_hash != shadow_ref.file_hash:
                    discrepancies.append(
                        f"Hash mismatch: primary={primary_ref.file_hash}, "
                        f"shadow={shadow_ref.file_hash}"
                    )

        results_match = len(discrepancies) == 0

        return {
            "results_match": results_match,
            "has_errors": has_errors,
            "discrepancies": discrepancies,
            "primary_success": primary_result.success,
            "shadow_success": shadow_result.success
        }

    async def _log_shadow_mode_comparison(
        self,
        file_path: str,
        provider: str,
        primary_impl: str,
        shadow_impl: str,
        comparison: Dict[str, Any],
        duration: float
    ):
        """
        Log shadow mode comparison results with structured logging.

        Args:
            file_path: Path to the file
            provider: Provider name
            primary_impl: Primary implementation used ('unified' or 'legacy')
            shadow_impl: Shadow implementation used ('unified' or 'legacy')
            comparison: Comparison results from _compare_results
            duration: Shadow operation duration in seconds
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "shadow_mode_upload",
            "file_path": file_path,
            "provider": provider,
            "primary_impl": primary_impl,
            "shadow_impl": shadow_impl,
            "results_match": comparison["results_match"],
            "has_errors": comparison["has_errors"],
            "primary_success": comparison["primary_success"],
            "shadow_success": comparison["shadow_success"],
            "duration_seconds": round(duration, 3),
            "metrics": {
                "total_comparisons": self.shadow_metrics.comparison_count,
                "error_count": self.shadow_metrics.error_count,
                "discrepancy_count": self.shadow_metrics.discrepancy_count,
                "error_rate": round(self.shadow_metrics.get_error_rate(), 4)
            }
        }

        # Add discrepancies if any
        if comparison["discrepancies"]:
            log_entry["discrepancies"] = comparison["discrepancies"]

        # Log at appropriate level
        if comparison["has_errors"]:
            logger.warning(
                f"Shadow mode comparison had errors",
                extra=log_entry
            )
        elif not comparison["results_match"]:
            logger.warning(
                f"Shadow mode comparison found discrepancies",
                extra=log_entry
            )
        else:
            # Only log successful matches at INFO level with sampling
            # to avoid overwhelming logs
            if random.random() < 0.1:  # 10% sampling for success logs
                logger.info(
                    f"Shadow mode comparison successful",
                    extra=log_entry
                )

