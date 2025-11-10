"""
Hybrid Supabase Manager - Phase C Implementation

Combines Claude MCP orchestration with Python autonomous operations.

Architecture (CORRECTED 2025-10-22):
- Claude Layer: Interactive operations via MCP tools (Claude calls MCP directly)
- Python Layer: Autonomous operations via Supabase Python client

Rationale:
MCP tools are designed for AI assistant interaction, not programmatic access.
Python code uses Supabase Python client for all autonomous operations.
The "hybrid" refers to the coordination between Claude and Python, not a technical bridge.

Date: 2025-10-22 (Phase C)
EXAI Validation: Continuation 9222d725-b6cd-44f1-8406-274e5a3b3389
Architecture Clarification: GLM-4.6 + Kimi K2-0905 consensus
"""

import json
import logging
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HybridOperationResult:
    """
    Standardized result type for hybrid operations.

    Tracks which layer (Claude MCP or Python autonomous) was used for the operation.
    Note: Python code always uses "python" layer. "mcp" layer is for Claude-initiated operations.
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    layer_used: str = "python"  # Always "python" for autonomous operations


class HybridSupabaseManager:
    """
    Hybrid Supabase manager for autonomous Python operations.

    Phase C Implementation (CORRECTED):
    - All operations use Supabase Python client
    - No direct MCP tool calls from Python code
    - MCP tools are called by Claude (AI assistant) for interactive operations
    - This class handles autonomous background operations

    Architecture Clarification:
    - Claude Layer: Interactive operations via MCP tools (Claude calls directly)
    - Python Layer: Autonomous operations via Supabase client (this class)

    Usage:
        manager = HybridSupabaseManager()

        # Database operation (uses Python Supabase client)
        result = manager.execute_sql("SELECT * FROM files LIMIT 10")

        # File operation (uses Python Supabase client)
        result = manager.upload_file(
            file_path="path/file.txt",
            file_data=file_data,
            original_name="file.txt",
            file_type="user_upload"
        )
    """
    
    def __init__(self):
        """Initialize hybrid manager with Supabase Python client."""
        self.project_id = os.getenv("SUPABASE_PROJECT_ID", "mxaazuhlqewmkweewyaz")
        self._enabled_override = None  # For testing purposes

        # Initialize Python client for all autonomous operations
        from src.storage.supabase_client import SupabaseStorageManager
        self.python_client = SupabaseStorageManager()

        logger.info(
            f"HybridSupabaseManager initialized for autonomous operations (project: {self.project_id})"
        )

    @property
    def enabled(self) -> bool:
        """
        Return whether the underlying Supabase client is enabled.

        FIX (2025-10-29): Added to support FileDeduplicationManager interface.
        CRITICAL: FileDeduplicationManager checks self.storage.enabled before database operations.
        """
        # Allow override for testing
        if self._enabled_override is not None:
            return self._enabled_override
        return self.python_client.enabled if self.python_client else False

    @enabled.setter
    def enabled(self, value: bool):
        """
        Set whether the storage manager is enabled.

        FIX (2025-10-29): Added setter to support testing scenarios.
        This allows tests to disable storage operations without mocking the entire manager.
        """
        self._enabled_override = value

    def get_client(self):
        """
        Return the underlying Supabase client for direct database operations.

        FIX (2025-10-29): Added to support FileDeduplicationManager interface.
        CRITICAL: FileDeduplicationManager needs direct client access for table operations.
        """
        return self.python_client.get_client() if self.python_client else None

    # ========================================================================
    # DATABASE OPERATIONS (Python Supabase Client)
    # ========================================================================

    def execute_rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> HybridOperationResult:
        """
        Execute RPC function using Python Supabase client.

        Phase C (CORRECTED): Uses Supabase Python client for autonomous RPC operations.
        For raw SQL queries, Claude should call execute_sql_supabase-mcp-full directly.

        Note: Python client (PostgREST) only supports RPC functions, not raw SQL.
        This method is renamed from execute_sql to clarify its purpose.

        Args:
            function_name: Name of the RPC function to execute
            params: Optional function parameters

        Returns:
            HybridOperationResult with function results
        """
        try:
            logger.info(f"Executing RPC function via Python client: {function_name}")

            client = self.python_client.get_client()

            # Execute RPC function
            result = client.rpc(function_name, params or {}).execute()
            data = result.data if hasattr(result, 'data') else result

            return HybridOperationResult(
                success=True,
                data=data,
                metadata={"function": function_name, "params": params},
                layer_used="python"
            )

        except Exception as e:
            logger.error(f"Python RPC execution error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"function": function_name, "params": params},
                layer_used="python"
            )
    

    
    # ========================================================================
    # BUCKET OPERATIONS (Python Supabase Client)
    # ========================================================================

    def list_buckets(self) -> HybridOperationResult:
        """
        List storage buckets using Python Supabase client.

        Phase C (CORRECTED): Uses Supabase Python client for autonomous operations.
        For interactive bucket management, Claude should call list_storage_buckets_supabase-mcp-full directly.

        Returns:
            HybridOperationResult with list of buckets
        """
        try:
            logger.info("Listing buckets via Python client")

            client = self.python_client.get_client()
            buckets = client.storage.list_buckets()

            return HybridOperationResult(
                success=True,
                data=buckets,
                metadata={"count": len(buckets) if buckets else 0, "operation": "list_buckets"},
                layer_used="python"
            )

        except Exception as e:
            logger.error(f"Python list_buckets error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"operation": "list_buckets"},
                layer_used="python"
            )

    def create_bucket(
        self,
        bucket_name: str,
        public: bool = False,
        file_size_limit: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None
    ) -> HybridOperationResult:
        """
        Create storage bucket using Python Supabase client.

        Phase C Step 3: Autonomous bucket creation for background tasks.
        For interactive bucket creation, Claude should call create_bucket_supabase-mcp-full directly.

        Args:
            bucket_name: Name of the bucket to create
            public: Whether the bucket should be publicly accessible
            file_size_limit: Optional maximum file size in bytes
            allowed_mime_types: Optional list of allowed MIME types

        Returns:
            HybridOperationResult with creation status
        """
        try:
            logger.info(f"Creating bucket via Python client: {bucket_name} (public={public})")

            client = self.python_client.get_client()

            # Build bucket options
            options = {"public": public}
            if file_size_limit:
                options["file_size_limit"] = file_size_limit
            if allowed_mime_types:
                options["allowed_mime_types"] = allowed_mime_types

            result = client.storage.create_bucket(bucket_name, options)

            return HybridOperationResult(
                success=True,
                data=result,
                metadata={
                    "bucket_name": bucket_name,
                    "public": public,
                    "operation": "create_bucket"
                },
                layer_used="python"
            )

        except Exception as e:
            logger.error(f"Python create_bucket error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"bucket_name": bucket_name, "operation": "create_bucket"},
                layer_used="python"
            )

    def delete_bucket(self, bucket_name: str) -> HybridOperationResult:
        """
        Delete storage bucket using Python Supabase client.

        Phase C Step 3: Autonomous bucket deletion for background tasks.
        For interactive bucket deletion, Claude should call appropriate MCP tool directly.

        Args:
            bucket_name: Name of the bucket to delete

        Returns:
            HybridOperationResult with deletion status
        """
        try:
            logger.info(f"Deleting bucket via Python client: {bucket_name}")

            client = self.python_client.get_client()
            result = client.storage.delete_bucket(bucket_name)

            return HybridOperationResult(
                success=True,
                data=result,
                metadata={"bucket_name": bucket_name, "operation": "delete_bucket"},
                layer_used="python"
            )

        except Exception as e:
            logger.error(f"Python delete_bucket error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"bucket_name": bucket_name, "operation": "delete_bucket"},
                layer_used="python"
            )

    def empty_bucket(self, bucket_name: str) -> HybridOperationResult:
        """
        Empty all files from a storage bucket using Python Supabase client.

        Phase C Step 3: Autonomous bucket cleanup for background tasks.

        Args:
            bucket_name: Name of the bucket to empty

        Returns:
            HybridOperationResult with operation status
        """
        try:
            logger.info(f"Emptying bucket via Python client: {bucket_name}")

            client = self.python_client.get_client()
            result = client.storage.empty_bucket(bucket_name)

            return HybridOperationResult(
                success=True,
                data=result,
                metadata={"bucket_name": bucket_name, "operation": "empty_bucket"},
                layer_used="python"
            )

        except Exception as e:
            logger.error(f"Python empty_bucket error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"bucket_name": bucket_name, "operation": "empty_bucket"},
                layer_used="python"
            )

    def get_bucket(self, bucket_name: str) -> HybridOperationResult:
        """
        Get bucket information using Python Supabase client.

        Phase C Step 3: Autonomous bucket info retrieval for background tasks.
        For interactive bucket info, Claude should call get_storage_config_supabase-mcp-full directly.

        Args:
            bucket_name: Name of the bucket to get info for

        Returns:
            HybridOperationResult with bucket information
        """
        try:
            logger.info(f"Getting bucket info via Python client: {bucket_name}")

            client = self.python_client.get_client()
            result = client.storage.get_bucket(bucket_name)

            return HybridOperationResult(
                success=True,
                data=result,
                metadata={"bucket_name": bucket_name, "operation": "get_bucket"},
                layer_used="python"
            )

        except Exception as e:
            logger.error(f"Python get_bucket error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"bucket_name": bucket_name, "operation": "get_bucket"},
                layer_used="python"
            )
    
    # ========================================================================
    # FILE OPERATIONS (Python Supabase Client)
    # ========================================================================
    # Note: File operations are NOT available in Supabase MCP tools.
    # These operations always use Python Supabase client for autonomous file management.
    
    def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        progress_callback: Optional[callable] = None,
        use_parallel: bool = False,  # Deprecated - kept for backward compatibility
        chunk_size: int = 5 * 1024 * 1024,  # Deprecated
        max_workers: int = 4  # Deprecated
    ) -> HybridOperationResult:
        """
        Upload file using optimized SupabaseStorageManager.

        Phase C Step 4 (REFACTORED 2025-10-22):
        Now delegates to SupabaseStorageManager.upload_file() which provides:
        - Retry logic with exponential backoff
        - Progress tracking with throttling
        - Better error handling and classification
        - Configurable timeouts

        Note: File operations are NOT available in Supabase MCP.
        Note: use_parallel, chunk_size, max_workers are deprecated (kept for backward compatibility)

        Args:
            bucket: Bucket name
            path: File path in bucket
            file_data: File content as bytes
            content_type: Optional MIME type
            progress_callback: Optional callback(bytes_transferred, total_bytes, percentage)
            use_parallel: DEPRECATED - ignored (kept for backward compatibility)
            chunk_size: DEPRECATED - ignored (kept for backward compatibility)
            max_workers: DEPRECATED - ignored (kept for backward compatibility)

        Returns:
            HybridOperationResult with upload status
        """
        try:
            file_size = len(file_data)
            logger.info(f"Uploading file via optimized manager: {bucket}/{path} ({file_size} bytes)")

            # Determine file type based on bucket
            file_type = "user_upload" if bucket == "user-files" else "generated"

            # Use optimized SupabaseStorageManager.upload_file()
            # This provides retry logic, progress tracking, and better error handling
            file_id = self.python_client.upload_file(
                file_path=path,
                file_data=file_data,
                original_name=path.split('/')[-1],  # Extract filename from path
                mime_type=content_type,
                file_type=file_type,
                progress_callback=progress_callback
            )

            if file_id:
                return HybridOperationResult(
                    success=True,
                    data={"file_id": file_id, "path": path},
                    metadata={
                        "bucket": bucket,
                        "path": path,
                        "size": file_size,
                        "operation": "upload_file",
                        "file_id": file_id
                    },
                    layer_used="python"
                )
            else:
                return HybridOperationResult(
                    success=False,
                    error="Upload failed - no file_id returned",
                    metadata={"bucket": bucket, "path": path, "operation": "upload_file"},
                    layer_used="python"
                )

        except Exception as e:
            logger.error(f"File upload error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"bucket": bucket, "path": path, "operation": "upload_file"},
                layer_used="python"
            )

    # DEPRECATED: _upload_file_parallel removed (2025-10-22)
    # Reason: Flawed implementation that uploaded chunks then re-uploaded entire file
    # Replacement: SupabaseStorageManager.upload_file() with retry logic and progress tracking
    # See: Phase C Step 4 refactoring

    def download_file(
        self,
        file_id: str,
        progress_callback: Optional[callable] = None
    ) -> HybridOperationResult:
        """
        Download file using Python Supabase client with optional progress tracking.

        Phase C Step 4: Enhanced with progress tracking.
        Note: File operations are NOT available in Supabase MCP.

        Args:
            file_id: File ID to download
            progress_callback: Optional callback(bytes_transferred, total_bytes, percentage)

        Returns:
            HybridOperationResult with file bytes
        """
        try:
            logger.info(f"Downloading file via Python client: {file_id}")

            # Report initial progress
            if progress_callback:
                progress_callback(0, 0, 0.0)

            file_bytes = self.python_client.download_file(file_id=file_id)

            if file_bytes is None:
                return HybridOperationResult(
                    success=False,
                    error="File not found or download failed",
                    metadata={"file_id": file_id, "operation": "download_file"},
                    layer_used="python"
                )

            file_size = len(file_bytes)

            # Report completion
            if progress_callback:
                progress_callback(file_size, file_size, 100.0)

            return HybridOperationResult(
                success=True,
                data=file_bytes,
                metadata={
                    "file_id": file_id,
                    "size": file_size,
                    "operation": "download_file"
                },
                layer_used="python"
            )

        except Exception as e:
            logger.error(f"File download error: {e}")
            return HybridOperationResult(
                success=False,
                error=str(e),
                metadata={"file_id": file_id, "operation": "download_file"},
                layer_used="python"
            )


# ============================================================================
# ARCHITECTURE NOTES (Phase C - CORRECTED 2025-10-22)
# ============================================================================
"""
HYBRID ARCHITECTURE SUMMARY:

This class implements the Python layer of a two-layer architecture:
- Claude Layer: Interactive operations via MCP tools (Claude calls directly)
- Python Layer: Autonomous operations via Supabase client (this class)

Key Points:
- Python code uses Supabase Python client DIRECTLY (no MCP tools)
- Claude calls MCP tools DIRECTLY (no Python code)
- Clean separation: Interactive (Claude) vs Autonomous (Python)
- Both layers work independently but coherently

For comprehensive architecture documentation, see:
docs/HYBRID_SUPABASE_ARCHITECTURE.md

EXAI Validation: Continuation 9222d725-b6cd-44f1-8406-274e5a3b3389
Consensus: GLM-4.6 + Kimi K2-0905 (Python should NOT call MCP tools)
"""
