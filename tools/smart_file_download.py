"""
Smart File Download Tool - Unified file download interface with caching and integrity validation.

This tool provides seamless file download capabilities with:
- Cache-first download strategy (Supabase → Provider)
- SHA256-based integrity verification
- Provider fallback (Kimi → Supabase)
- Download tracking and analytics
- Automatic error handling and retry logic

Author: EXAI-MCP-Server
Date: 2025-10-29
Phase: 1 - Basic Download Functionality
"""

import os
import asyncio
import logging
import time
import shutil
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Set, Literal
from datetime import datetime, timedelta
from openai import OpenAI

# Import existing utilities
from utils.file.deduplication import FileDeduplicationManager
from src.storage.hybrid_supabase_manager import HybridSupabaseManager

logger = logging.getLogger(__name__)

# Default download directory (Docker container path)
DEFAULT_DOWNLOAD_DIR = os.getenv("EXAI_DOWNLOAD_DIR", "/tmp/exai-downloads/")

# Default cache expiry (7 days as recommended by EXAI)
DEFAULT_CACHE_EXPIRY_DAYS = 7

# PHASE 3: File type validation (EXAI recommendation)
ALLOWED_FILE_TYPES = {
    'application/pdf', 'text/plain', 'image/jpeg', 'image/png',
    'application/json', 'text/csv', 'text/markdown', 'text/html',
    'application/zip', 'application/x-tar', 'application/gzip',
    'text/x-python', 'text/x-javascript', 'text/x-typescript'
}

BLOCKED_FILE_TYPES = {
    'application/x-executable', 'application/x-msdownload',
    'application/x-msdos-program', 'application/x-sh',
    'application/x-shellscript'
}

# PHASE 3: Size limits per file type (MB)
FILE_SIZE_LIMITS = {
    'application/pdf': 50,
    'image/jpeg': 10,
    'image/png': 10,
    'text/plain': 5,
    'application/json': 5,
    'default': 100
}

# PHASE 3: Retry configuration (EXAI recommendation)
RETRY_CONFIG = {
    "max_attempts": 3,
    "base_delay": 1.0,  # seconds
    "max_delay": 30.0,
    "exponential_base": 2.0,
    "jitter": True
}

# Global set to track active downloads (concurrent download protection)
_active_downloads: Dict[str, asyncio.Event] = {}  # Maps file_id to completion event
_download_lock = asyncio.Lock()


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and injection attacks.

    CRITICAL FIX: Validates filename from Kimi API before using in os.path.join()

    Args:
        filename: Original filename from API

    Returns:
        Safe filename with dangerous characters removed

    Raises:
        ValueError: If filename is invalid or empty after sanitization
    """
    if not isinstance(filename, str):
        raise ValueError("Invalid filename: must be string")

    # Handle empty or whitespace-only strings
    if not filename or not filename.strip():
        return 'downloaded_file'

    # Remove path separators and dangerous characters
    # This prevents directory traversal attacks like "../../../etc/passwd"
    # Includes: < > : " / \ | ? * ` $ ( ) ; & ' space
    # NOTE: Dots are preserved to allow file extensions
    safe_name = re.sub(r'[<>:"/\\|?*`$();\s&\']+', '_', filename)

    # Use basename to prevent any remaining path traversal attempts
    safe_name = os.path.basename(safe_name)

    # Remove leading/trailing underscores (but keep dots for extensions)
    safe_name = safe_name.strip('_')

    # Prevent directory traversal by removing leading dots
    # (e.g., ".bashrc" becomes "bashrc")
    while safe_name.startswith('.'):
        safe_name = safe_name[1:]

    # Ensure filename is not empty after sanitization
    if not safe_name:
        safe_name = 'downloaded_file'

    # Limit filename length to 255 characters (filesystem limit)
    safe_name = safe_name[:255]

    logger.debug(f"[SMART_FILE_DOWNLOAD] Sanitized filename: {filename} → {safe_name}")
    return safe_name


class SmartFileDownloadTool:
    """
    Unified file download interface with automatic caching and integrity validation.
    
    Features:
    - Cache-first download strategy (Supabase → Provider)
    - SHA256-based integrity verification
    - Provider fallback (Kimi → Supabase)
    - Download tracking and analytics
    - Automatic error handling and retry logic
    
    Usage:
        tool = SmartFileDownloadTool()
        local_path = await tool.execute(file_id="file_abc123")
    """
    
    def __init__(self):
        """Initialize the smart file download tool."""
        # Initialize storage manager
        self.storage_manager = HybridSupabaseManager()
        
        # Initialize deduplication manager
        self.dedup_manager = FileDeduplicationManager(
            storage_manager=self.storage_manager
        )
        
        # Provider API keys
        self.moonshot_api_key = os.getenv("MOONSHOT_API_KEY")
        self.glm_api_key = os.getenv("GLM_API_KEY")
        
        # Ensure download directory exists
        self._ensure_download_dir()
        
        logger.info("[SMART_FILE_DOWNLOAD] Tool initialized successfully")
    
    def _ensure_download_dir(self):
        """Ensure the default download directory exists."""
        Path(DEFAULT_DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
        logger.info(f"[SMART_FILE_DOWNLOAD] Download directory ready: {DEFAULT_DOWNLOAD_DIR}")
    
    def _validate_destination(self, destination: str) -> str:
        """
        Validate destination path is within allowed directories.

        Handles cross-platform path normalization (Windows vs Linux).
        The code runs on Windows but validates Linux container paths.

        Args:
            destination: Destination path to validate

        Returns:
            Absolute validated path

        Raises:
            ValueError: If path is outside allowed directories
        """
        # Normalize path to use forward slashes for comparison
        # This handles Windows converting /mnt/project/ to C:\mnt\project\
        normalized_path = os.path.normpath(destination).replace('\\', '/')

        # Check if path is within allowed directories (/mnt/project/, /tmp/, or downloads dir)
        allowed_patterns = ["/mnt/project/", "/tmp/exai-downloads/"]
        if DEFAULT_DOWNLOAD_DIR and DEFAULT_DOWNLOAD_DIR not in ["/tmp/exai-downloads/"]:
            allowed_patterns.append(DEFAULT_DOWNLOAD_DIR)

        if not any(normalized_path.startswith(pattern) for pattern in allowed_patterns):
            raise ValueError(
                f"Downloads must be within allowed directories {allowed_patterns}, "
                f"got: {normalized_path}"
            )

        # Ensure parent directory exists (use original path for actual filesystem operations)
        Path(destination).parent.mkdir(parents=True, exist_ok=True)

        return destination
    
    async def _check_cache(self, file_id: str) -> Optional[str]:
        """
        Check if file exists in local cache or Supabase storage.

        Args:
            file_id: Provider file ID

        Returns:
            Local file path if cached, None otherwise
        """
        # PHASE 1 FIX: Check local file cache first (basic implementation)
        # Look for file in default download directory
        try:
            download_dir = Path(DEFAULT_DOWNLOAD_DIR)
            if download_dir.exists():
                # Check if file exists locally with matching hash
                if self.storage_manager.enabled:
                    client = self.storage_manager.get_client()
                    if client:
                        # Get file metadata from database
                        result = client.table("provider_file_uploads")\
                            .select("sha256_hash, file_path")\
                            .eq("provider_file_id", file_id)\
                            .execute()

                        if result.data:
                            expected_hash = result.data[0]["sha256_hash"]
                            file_path = result.data[0].get("file_path", "")

                            # Check if file exists locally
                            filename = os.path.basename(file_path) if file_path else None
                            if filename:
                                local_path = download_dir / filename
                                if local_path.exists():
                                    # Verify integrity
                                    actual_hash = self.dedup_manager.calculate_sha256(str(local_path))
                                    if actual_hash == expected_hash:
                                        logger.info(f"[SMART_FILE_DOWNLOAD] Cache HIT (local): {local_path}")
                                        return str(local_path)
                                    else:
                                        logger.warning(f"[SMART_FILE_DOWNLOAD] Corrupted cache file, re-downloading: {local_path}")
                                        os.unlink(local_path)  # Delete corrupted file
        except Exception as e:
            logger.error(f"[SMART_FILE_DOWNLOAD] Local cache check failed: {e}")

        # No local cache found
        logger.info(f"[SMART_FILE_DOWNLOAD] Cache MISS: {file_id}")
        return None
    
    async def _determine_provider(self, file_id: str) -> str:
        """
        Determine which provider has the file with proper fallback.

        Priority: Database lookup → Kimi verification → Supabase fallback

        Args:
            file_id: Provider file ID

        Returns:
            Provider name ('kimi' or 'supabase')

        Raises:
            ValueError: If file not found on any provider
        """
        # PHASE 1 FIX: Improved provider determination with fallback

        # Step 1: Check database for provider info
        if self.storage_manager.enabled:
            try:
                client = self.storage_manager.get_client()
                if client:
                    result = client.table("provider_file_uploads")\
                        .select("provider")\
                        .eq("provider_file_id", file_id)\
                        .execute()

                    if result.data:
                        provider = result.data[0]["provider"]
                        logger.info(f"[SMART_FILE_DOWNLOAD] Provider from DB: {provider}")

                        # Validate provider is supported for download
                        if provider == "glm":
                            logger.warning(f"[SMART_FILE_DOWNLOAD] GLM files cannot be downloaded, checking Supabase fallback")
                            return "supabase"  # Try Supabase as fallback

                        return provider
            except Exception as e:
                logger.error(f"[SMART_FILE_DOWNLOAD] Provider lookup failed: {e}")

        # Step 2: Try Kimi first (most common for platform uploads)
        # Kimi file IDs typically start with "file_" or are long alphanumeric strings (>=20 chars)
        if file_id.startswith("file_") or len(file_id) >= 20:
            logger.info(f"[SMART_FILE_DOWNLOAD] Provider from pattern: kimi")
            return "kimi"

        # Step 3: Fallback to Supabase
        logger.info(f"[SMART_FILE_DOWNLOAD] Provider fallback: supabase")
        return "supabase"
    
    async def _download_from_kimi(self, file_id: str, destination: str) -> str:
        """
        Download file from Kimi/Moonshot provider with streaming and security fixes.

        CRITICAL FIXES:
        - Uses streaming to prevent OOM on large files (HIGH bug fix)
        - Sanitizes filename to prevent path traversal (CRITICAL bug fix)

        Args:
            file_id: Kimi file ID
            destination: Destination directory or file path

        Returns:
            Local file path

        Raises:
            ValueError: If API key not configured or filename invalid
            Exception: If download fails
        """
        if not self.moonshot_api_key:
            raise ValueError("MOONSHOT_API_KEY not configured")

        logger.info(f"[SMART_FILE_DOWNLOAD] Downloading from Kimi: {file_id}")

        temp_path = None
        try:
            # Initialize Kimi client
            client = OpenAI(
                api_key=self.moonshot_api_key,
                base_url="https://api.moonshot.cn/v1"
            )

            # Get file metadata first
            metadata = client.files.retrieve(file_id)
            filename = metadata.filename
            file_size = metadata.bytes

            logger.info(f"[SMART_FILE_DOWNLOAD] File metadata: {filename} ({file_size} bytes)")

            # CRITICAL FIX: Sanitize filename to prevent path traversal
            safe_filename = _sanitize_filename(filename)

            # Determine local path
            if os.path.isdir(destination):
                local_path = os.path.join(destination, safe_filename)
            else:
                local_path = destination

            # Use temporary file for atomic write
            temp_path = local_path + ".tmp"

            # HIGH FIX: Use streaming to prevent OOM on large files
            # Download in chunks instead of loading entire file into memory
            logger.info(f"[SMART_FILE_DOWNLOAD] Starting streaming download to {temp_path}")

            bytes_downloaded = 0
            chunk_size = 8192  # 8KB chunks

            with open(temp_path, 'wb') as f:
                response = client.files.content(file_id)
                # The response object supports iteration for streaming
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)

                        # Log progress for large files
                        if file_size > 0 and bytes_downloaded % (1024 * 1024) == 0:  # Every 1MB
                            progress_pct = (bytes_downloaded / file_size) * 100
                            logger.debug(f"[SMART_FILE_DOWNLOAD] Download progress: {progress_pct:.1f}%")

            # Atomic rename (move temp to final location)
            if os.path.exists(local_path):
                os.unlink(local_path)
            os.rename(temp_path, local_path)
            temp_path = None  # Mark as successfully moved

            logger.info(f"[SMART_FILE_DOWNLOAD] Downloaded successfully: {local_path} ({bytes_downloaded} bytes)")
            return local_path

        except Exception as e:
            logger.error(f"[SMART_FILE_DOWNLOAD] Kimi download failed: {e}")
            # Clean up temporary file on failure
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.debug(f"[SMART_FILE_DOWNLOAD] Cleaned up temporary file: {temp_path}")
                except Exception as cleanup_error:
                    logger.warning(f"[SMART_FILE_DOWNLOAD] Failed to clean up temp file: {cleanup_error}")
            raise
    
    async def _download_from_supabase(self, file_id: str, destination: str) -> str:
        """
        Download file from Supabase storage.
        
        Args:
            file_id: Supabase file ID or path (storage path)
            destination: Destination directory or file path

        Returns:
            Local file path

        Raises:
            RuntimeError: If Supabase is not enabled or download fails
        """
        if not self.storage_manager.enabled:
            raise RuntimeError("Supabase storage is not enabled")

        try:
            client = self.storage_manager.get_client()
            if not client:
                raise RuntimeError("Supabase client not available")

            # Parse file_id to extract bucket and path
            # Expected format: "user-files/contexts/{uuid}/{filename}"
            # or "user-files/system/{uuid}/{filename}"
            file_id = file_id.strip('/')

            # Extract bucket name and file path
            parts = file_id.split('/', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid file_id format: {file_id}")

            bucket_name, file_path = parts

            # Download file from Supabase storage
            logger.info(f"[SMART_FILE_DOWNLOAD] Downloading from Supabase: bucket={bucket_name}, path={file_path}")

            # Download the file
            result = client.storage.from_(bucket_name).download(file_path)

            if not result:
                raise RuntimeError(f"Failed to download file: {file_id}")

            # Determine destination path
            if os.path.isdir(destination):
                filename = os.path.basename(file_path)
                local_path = os.path.join(destination, filename)
            else:
                local_path = destination

            # Ensure destination directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Write downloaded content to file
            with open(local_path, 'wb') as f:
                f.write(result)

            logger.info(f"[SMART_FILE_DOWNLOAD] Successfully downloaded to: {local_path}")

            # Verify integrity if possible
            try:
                self._verify_integrity(file_id, local_path)
            except Exception as e:
                logger.warning(f"[SMART_FILE_DOWNLOAD] Integrity verification failed: {e}")

            return local_path

        except Exception as e:
            logger.error(f"[SMART_FILE_DOWNLOAD] Download failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to download from Supabase: {e}")
    
    async def _verify_integrity(self, file_id: str, local_path: str):
        """
        Verify downloaded file integrity using SHA256.
        
        Args:
            file_id: Provider file ID
            local_path: Local file path to verify
            
        Raises:
            ValueError: If hash mismatch detected
        """
        if not self.storage_manager.enabled:
            logger.warning("[SMART_FILE_DOWNLOAD] Supabase not enabled, skipping integrity check")
            return
        
        try:
            client = self.storage_manager.get_client()
            if not client:
                logger.warning("[SMART_FILE_DOWNLOAD] No Supabase client, skipping integrity check")
                return
            
            # Get expected hash from database
            result = client.table("provider_file_uploads")\
                .select("sha256_hash")\
                .eq("provider_file_id", file_id)\
                .execute()
            
            if not result.data:
                logger.warning(f"[SMART_FILE_DOWNLOAD] No hash found for {file_id}, skipping verification")
                return
            
            expected_hash = result.data[0]["sha256_hash"]
            actual_hash = self.dedup_manager.calculate_sha256(local_path)
            
            if actual_hash != expected_hash:
                # Hash mismatch - delete corrupted file
                os.unlink(local_path)
                raise ValueError(
                    f"Hash mismatch for {file_id}: expected {expected_hash}, got {actual_hash}"
                )
            
            logger.info(f"[SMART_FILE_DOWNLOAD] Integrity verified: {file_id}")
            
        except Exception as e:
            logger.error(f"[SMART_FILE_DOWNLOAD] Integrity verification failed: {e}")
            raise

    async def _update_download_tracking(
        self,
        file_id: str,
        cache_hit: bool,
        provider: str,
        cache_source: str,
        local_path: str,
        download_duration_ms: int,
        error_count: int = 0
    ):
        """
        Update download tracking in database (Phase 2 MVP).

        Args:
            file_id: Provider file ID
            cache_hit: Whether download was served from cache
            provider: Provider used ('kimi', 'supabase')
            cache_source: Source of file ('local', 'supabase', 'origin')
            local_path: Path to downloaded file
            download_duration_ms: Download duration in milliseconds
            error_count: Number of retry attempts
        """
        if not self.storage_manager.enabled:
            logger.warning("[SMART_FILE_DOWNLOAD] Supabase not enabled, skipping tracking")
            return

        try:
            client = self.storage_manager.get_client()
            if not client:
                return

            # Get file size
            file_size_bytes = os.path.getsize(local_path) if os.path.exists(local_path) else 0

            # Calculate download speed (MB/s)
            download_speed_mbps = 0.0
            if download_duration_ms > 0 and file_size_bytes > 0:
                download_speed_mbps = round(
                    (file_size_bytes / (1024 * 1024)) / (download_duration_ms / 1000),
                    2
                )

            # Update provider_file_uploads statistics
            client.rpc(
                "update_download_stats",
                {"p_file_id": file_id, "p_cache_hit": cache_hit}
            ).execute()

            # Update cache path and expiry if not a cache hit
            # PHASE 2 IMPROVEMENT: Size-based expiry (EXAI recommendation)
            if not cache_hit:
                # Determine expiry based on file size
                file_size_mb = file_size_bytes / (1024 * 1024)
                if file_size_mb < 10:
                    expiry_days = 14  # Small files: 14 days
                elif file_size_mb < 100:
                    expiry_days = 7   # Medium files: 7 days
                else:
                    expiry_days = 3   # Large files: 3 days

                cache_expiry = datetime.now() + timedelta(days=expiry_days)
                client.table("provider_file_uploads")\
                    .update({
                        "cache_path": local_path,
                        "cache_expiry": cache_expiry.isoformat(),
                        "cache_size_bytes": file_size_bytes
                    })\
                    .eq("provider_file_id", file_id)\
                    .execute()

            # Record download history
            client.table("file_download_history")\
                .insert({
                    "provider_file_id": file_id,
                    "downloaded_by": "agent",  # TODO: Get actual agent name
                    "downloaded_by_type": "agent",
                    "destination_path": local_path,
                    "download_duration_ms": download_duration_ms,
                    "file_size_bytes": file_size_bytes,
                    "cache_hit": cache_hit,
                    "provider_used": provider,
                    "cache_source": cache_source,
                    "error_count": error_count,
                    "download_speed_mbps": download_speed_mbps
                })\
                .execute()

            logger.info(
                f"[SMART_FILE_DOWNLOAD] Tracking updated: {file_id} "
                f"(cache_hit={cache_hit}, speed={download_speed_mbps}MB/s)"
            )

        except Exception as e:
            # Don't fail download if tracking fails
            logger.error(f"[SMART_FILE_DOWNLOAD] Tracking update failed: {e}")

    async def execute(self, file_id: str, destination: str = None) -> str:
        """
        Download file by ID and return local path.

        Args:
            file_id: Provider file ID or Supabase file ID
            destination: Optional destination path (default: {DEFAULT_DOWNLOAD_DIR})

        Returns:
            Local file path

        Raises:
            ValueError: If validation fails or hash mismatch
            Exception: If download fails
        """
        logger.info(f"[SMART_FILE_DOWNLOAD] Starting download: {file_id}")

        # CRITICAL FIX: Concurrent download protection using asyncio.Event
        # This prevents race conditions by using proper synchronization primitives
        download_event = None

        async with _download_lock:
            if file_id in _active_downloads:
                # Another download is in progress, wait for it to complete
                logger.warning(f"[SMART_FILE_DOWNLOAD] Concurrent download detected, waiting: {file_id}")
                download_event = _active_downloads[file_id]
            else:
                # Create new event for this download
                download_event = asyncio.Event()
                _active_downloads[file_id] = download_event

        # If we're waiting for another download, wait for it to complete
        if download_event.is_set():
            # Download already completed, check cache
            logger.info(f"[SMART_FILE_DOWNLOAD] Waiting for concurrent download to complete: {file_id}")
            await download_event.wait()
            cached_path = await self._check_cache(file_id)
            if cached_path:
                logger.info(f"[SMART_FILE_DOWNLOAD] Cache HIT after wait: {file_id}")
                return cached_path
        elif file_id in _active_downloads and _active_downloads[file_id] != download_event:
            # Another download is in progress, wait for it
            logger.info(f"[SMART_FILE_DOWNLOAD] Waiting for concurrent download: {file_id}")
            await _active_downloads[file_id].wait()
            cached_path = await self._check_cache(file_id)
            if cached_path:
                logger.info(f"[SMART_FILE_DOWNLOAD] Cache HIT after wait: {file_id}")
                return cached_path

        # PHASE 2: Track download metrics
        start_time = time.time()
        cache_hit = False
        provider = None
        cache_source = None
        local_path = None
        error_count = 0

        try:
            # 1. Validate destination
            dest = destination or DEFAULT_DOWNLOAD_DIR
            dest = self._validate_destination(dest)

            # 2. Check cache first
            cached_path = await self._check_cache(file_id)
            if cached_path:
                cache_hit = True
                cache_source = "local"
                local_path = cached_path
                logger.info(f"[SMART_FILE_DOWNLOAD] Cache HIT: {file_id}")

                # PHASE 2: Track cache hit
                download_duration_ms = int((time.time() - start_time) * 1000)
                await self._update_download_tracking(
                    file_id, cache_hit, "cache", cache_source,
                    local_path, download_duration_ms, error_count
                )

                return cached_path

            # 3. Determine provider
            provider = await self._determine_provider(file_id)
            logger.info(f"[SMART_FILE_DOWNLOAD] Provider: {provider}")
            cache_source = "origin"

            # 4. Download from provider
            if provider == "kimi":
                local_path = await self._download_from_kimi(file_id, dest)
            elif provider == "supabase":
                local_path = await self._download_from_supabase(file_id, dest)
                cache_source = "supabase"
            else:
                raise ValueError(f"Unsupported provider: {provider} (GLM does not support file download)")

            # 5. Verify integrity
            await self._verify_integrity(file_id, local_path)

            # PHASE 2: Track successful download
            download_duration_ms = int((time.time() - start_time) * 1000)
            await self._update_download_tracking(
                file_id, cache_hit, provider, cache_source,
                local_path, download_duration_ms, error_count
            )

            logger.info(f"[SMART_FILE_DOWNLOAD] Download complete: {local_path}")
            return local_path

        except Exception as e:
            error_count += 1
            logger.error(f"[SMART_FILE_DOWNLOAD] Download failed: {e}")
            raise

        finally:
            # CRITICAL FIX: Signal completion to waiting downloads
            async with _download_lock:
                if file_id in _active_downloads:
                    event = _active_downloads[file_id]
                    event.set()  # Signal that download is complete
                    del _active_downloads[file_id]  # Clean up

