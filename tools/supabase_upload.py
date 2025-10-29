"""
Supabase Upload Utility for Universal File Hub
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Provides file upload functionality with:
- SHA256-based deduplication
- Progress tracking
- Metadata management
- Error handling and retry logic
- Provider adapters for Kimi and GLM integration

PHASE 1 ENHANCEMENT: Added provider adapters for unified upload workflow
"""

import os
import hashlib
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Provider constants
PROVIDER_KIMI = "kimi"
PROVIDER_GLM = "glm"
PROVIDER_SUPABASE_ONLY = "supabase_only"
PROVIDER_AUTO = "auto"


class SupabaseUploadManager:
    """Manages file uploads to Supabase Storage with deduplication and tracking."""
    
    def __init__(self, supabase_client, default_bucket: str = "user-files"):
        """
        Initialize upload manager.
        
        Args:
            supabase_client: Supabase client instance
            default_bucket: Default storage bucket name
        """
        self.client = supabase_client
        self.default_bucket = default_bucket
        self.chunk_size = 5 * 1024 * 1024  # 5MB chunks for large files
        self.large_file_threshold = 50 * 1024 * 1024  # 50MB threshold
    
    def upload_file(
        self,
        file_path: str,
        user_id: str,
        filename: Optional[str] = None,
        bucket: Optional[str] = None,
        progress_callback: Optional[Callable[[int, float], None]] = None,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Supabase Storage with deduplication and progress tracking.
        
        Args:
            file_path: Path to file to upload
            user_id: User ID for ownership tracking
            filename: Optional custom filename (defaults to original filename)
            bucket: Optional bucket name (defaults to default_bucket)
            progress_callback: Optional callback for progress updates (bytes_uploaded, percent)
            tags: Optional list of tags for categorization
        
        Returns:
            Dictionary with upload result:
            {
                'file_id': str,
                'storage_path': str,
                'sha256_hash': str,
                'file_size': int,
                'deduplicated': bool,
                'metadata_id': str
            }
        
        Raises:
            FileNotFoundError: If file_path doesn't exist
            UploadError: If upload fails
        """
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        filename = filename or os.path.basename(file_path)
        bucket = bucket or self.default_bucket
        
        # Calculate SHA256 hash
        logger.info(f"Calculating SHA256 for {filename} ({file_size} bytes)")
        file_hash = self.calculate_sha256(file_path)
        
        # Check for existing file with same hash
        existing_file = self.check_existing_file(file_hash, user_id)
        if existing_file:
            logger.info(f"File with hash {file_hash} already exists, creating reference")
            metadata_id = self.create_metadata_reference(
                existing_file, user_id, filename, tags
            )
            return {
                'file_id': existing_file['file_id'],
                'storage_path': existing_file['path'],
                'sha256_hash': file_hash,
                'file_size': file_size,
                'deduplicated': True,
                'metadata_id': metadata_id
            }
        
        # Start operation tracking
        operation_id = self.track_operation(
            user_id=user_id,
            operation_type='upload',
            status='processing',
            metadata={'filename': filename, 'file_size': file_size}
        )
        
        try:
            # Generate storage path
            storage_path = self.get_storage_path(user_id, file_hash, filename)
            
            # Upload to storage
            logger.info(f"Uploading {filename} to {storage_path}")
            upload_result = self.upload_to_storage(
                file_path, bucket, storage_path, progress_callback
            )

            # Extract file ID from upload result
            # Supabase returns UploadResponse object with 'path' attribute
            file_id = storage_path  # Use storage path as file ID

            # Create metadata record
            metadata_id = self.create_metadata_record(
                file_id=file_id,
                user_id=user_id,
                filename=filename,
                file_size=file_size,
                content_type=self._get_content_type(filename),
                bucket_id=bucket,
                path=storage_path,
                sha256_hash=file_hash,
                tags=tags or []
            )
            
            # Update operation status
            self.update_operation(operation_id, 'completed', metadata={'metadata_id': metadata_id})
            
            logger.info(f"Upload completed: {filename} -> {storage_path}")

            return {
                'file_id': file_id,
                'storage_path': storage_path,
                'sha256_hash': file_hash,
                'file_size': file_size,
                'deduplicated': False,
                'metadata_id': metadata_id,
                'operation_id': operation_id
            }
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            self.update_operation(operation_id, 'failed', error_message=str(e))
            # Cleanup partial upload if needed
            self.cleanup_on_failure(bucket, storage_path if 'storage_path' in locals() else None)
            raise UploadError(f"Upload failed: {str(e)}") from e
    
    def calculate_sha256(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_storage_path(self, user_id: str, file_hash: str, filename: str) -> str:
        """
        Generate storage path using hybrid approach: {user_id}/{hash_prefix}/{hash}/{filename}
        
        Args:
            user_id: User ID
            file_hash: SHA256 hash
            filename: Original filename
        
        Returns:
            Storage path string
        """
        hash_prefix = file_hash[:2]
        return f"{user_id}/{hash_prefix}/{file_hash}/{filename}"
    
    def check_existing_file(self, file_hash: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if file with given hash already exists for this user.
        
        Args:
            file_hash: SHA256 hash to check
            user_id: User ID
        
        Returns:
            Existing file metadata or None
        """
        try:
            result = self.client.table('file_metadata').select('*').eq(
                'sha256_hash', file_hash
            ).eq('user_id', user_id).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.warning(f"Error checking existing file: {e}")
            return None
    
    def upload_to_storage(
        self,
        file_path: str,
        bucket: str,
        storage_path: str,
        progress_callback: Optional[Callable[[int, float], None]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Supabase Storage.
        
        Args:
            file_path: Path to file
            bucket: Bucket name
            storage_path: Destination path in storage
            progress_callback: Optional progress callback
        
        Returns:
            Upload result from Supabase
        """
        file_size = os.path.getsize(file_path)
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Upload to Supabase Storage
        result = self.client.storage.from_(bucket).upload(
            storage_path,
            file_data,
            file_options={"content-type": self._get_content_type(file_path)}
        )
        
        # Call progress callback with 100%
        if progress_callback:
            progress_callback(file_size, 100.0)
        
        return result
    
    def create_metadata_record(
        self,
        file_id: Optional[str],
        user_id: str,
        filename: str,
        file_size: int,
        content_type: str,
        bucket_id: str,
        path: str,
        sha256_hash: str,
        tags: list
    ) -> str:
        """Create metadata record in database."""
        data = {
            'file_id': file_id,
            'user_id': user_id,
            'filename': filename,
            'file_size': file_size,
            'content_type': content_type,
            'bucket_id': bucket_id,
            'path': path,
            'sha256_hash': sha256_hash,
            'tags': tags,
            'access_count': 0
        }
        
        result = self.client.table('file_metadata').insert(data).execute()
        return result.data[0]['id']
    
    def create_metadata_reference(
        self,
        existing_file: Dict[str, Any],
        user_id: str,
        filename: str,
        tags: Optional[list]
    ) -> str:
        """Create new metadata record referencing existing file."""
        data = {
            'file_id': existing_file['file_id'],
            'user_id': user_id,
            'filename': filename,
            'file_size': existing_file['file_size'],
            'content_type': existing_file['content_type'],
            'bucket_id': existing_file['bucket_id'],
            'path': existing_file['path'],
            'sha256_hash': existing_file['sha256_hash'],
            'tags': tags or [],
            'access_count': 0
        }
        
        result = self.client.table('file_metadata').insert(data).execute()
        return result.data[0]['id']
    
    def track_operation(
        self,
        user_id: str,
        operation_type: str,
        status: str,
        metadata: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> str:
        """Track file operation in database."""
        data = {
            'user_id': user_id,
            'operation_type': operation_type,
            'status': status,
            'metadata': metadata or {},
            'error_message': error_message
        }
        
        result = self.client.table('file_operations').insert(data).execute()
        return result.data[0]['id']
    
    def update_operation(
        self,
        operation_id: str,
        status: str,
        metadata: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """Update operation status."""
        data = {'status': status}
        if metadata:
            data['metadata'] = metadata
        if error_message:
            data['error_message'] = error_message
        if status in ['completed', 'failed']:
            data['completed_at'] = datetime.utcnow().isoformat()
        
        self.client.table('file_operations').update(data).eq('id', operation_id).execute()
    
    def cleanup_on_failure(self, bucket: str, storage_path: Optional[str]):
        """Clean up partial uploads on failure."""
        if storage_path:
            try:
                self.client.storage.from_(bucket).remove([storage_path])
                logger.info(f"Cleaned up partial upload: {storage_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {storage_path}: {e}")
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename extension."""
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'


class UploadError(Exception):
    """Custom exception for upload errors."""
    pass


# ============================================================================
# PROVIDER ADAPTERS (Phase 1 Enhancement)
# ============================================================================

def _kimi_upload_adapter(
    supabase_client,
    file_path: str,
    user_id: str,
    filename: str,
    bucket: str,
    tags: List[str]
) -> Dict[str, Any]:
    """
    Kimi-specific upload adapter.

    Workflow:
    1. Upload to Supabase (persistent storage)
    2. Upload to Kimi SDK (100MB limit, persistent files)
    3. Store mapping in file_id_mappings table
    4. Return unified response with both IDs

    Args:
        supabase_client: Supabase client instance
        file_path: Path to file
        user_id: User ID
        filename: Filename
        bucket: Storage bucket
        tags: List of tags

    Returns:
        Unified response with both Supabase and Kimi file IDs

    Raises:
        ValueError: If file exceeds size limit
        UploadError: If upload fails
    """
    from tools.provider_config import validate_file_size
    from tools.file_id_mapper import FileIdMapper

    # Validate file size
    file_size = os.path.getsize(file_path)
    is_valid, error_msg = validate_file_size(file_size, "kimi")
    if not is_valid:
        raise ValueError(error_msg)

    logger.info(f"Starting Kimi upload adapter for {filename} ({file_size} bytes)")

    # 1. Upload to Supabase
    upload_manager = SupabaseUploadManager(supabase_client, bucket)
    supabase_result = upload_manager.upload_file(
        file_path=file_path,
        user_id=user_id,
        filename=filename,
        bucket=bucket,
        tags=tags
    )

    supabase_file_id = supabase_result['file_id']

    try:
        # 2. Upload to Kimi SDK
        from src.providers.registry import ModelProviderRegistry

        # Get Kimi provider
        kimi_model = os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")
        provider = ModelProviderRegistry.get_provider_for_model(kimi_model)

        # Upload to Kimi
        kimi_file_id = provider.upload_file(file_path, purpose="file-extract")

        logger.info(f"✅ Uploaded to Kimi: {kimi_file_id}")

        # 3. Store mapping
        mapper = FileIdMapper(supabase_client)
        mapper.store_mapping(
            supabase_id=supabase_file_id,
            provider_id=kimi_file_id,
            provider="kimi",
            user_id=user_id,
            status="completed"
        )

        # 4. Return unified response
        return {
            "success": True,
            "supabase_file_id": supabase_file_id,
            "provider_file_id": kimi_file_id,
            "provider": "kimi",
            "file_size": file_size,
            "filename": filename,
            "upload_time": datetime.utcnow().isoformat(),
            "deduplicated": supabase_result.get('deduplicated', False),
            "metadata_id": supabase_result.get('metadata_id')
        }

    except Exception as e:
        logger.error(f"❌ Kimi upload failed: {e}")

        # Store failed mapping for retry
        mapper = FileIdMapper(supabase_client)
        mapper.store_mapping(
            supabase_id=supabase_file_id,
            provider_id=None,
            provider="kimi",
            user_id=user_id,
            status="failed"
        )

        # Don't fail the whole operation - Supabase upload succeeded
        logger.warning(
            f"Provider upload failed but Supabase upload succeeded. "
            f"User: {user_id}, File: {filename}, Provider: kimi, "
            f"Supabase ID: {supabase_file_id}, Error: {str(e)}"
        )

        return {
            "success": True,
            "supabase_file_id": supabase_file_id,
            "provider_file_id": None,
            "provider": "kimi",
            "file_size": file_size,
            "filename": filename,
            "upload_time": datetime.utcnow().isoformat(),
            "deduplicated": supabase_result.get('deduplicated', False),
            "metadata_id": supabase_result.get('metadata_id'),
            "provider_upload_failed": True,
            "error": str(e)
        }


def _glm_upload_adapter(
    supabase_client,
    file_path: str,
    user_id: str,
    filename: str,
    bucket: str,
    tags: List[str]
) -> Dict[str, Any]:
    """
    GLM-specific upload adapter.

    Workflow:
    1. Upload to Supabase (persistent storage)
    2. Upload to GLM SDK (20MB limit, session-bound files)
    3. Store mapping + session info in file_id_mappings table
    4. Return unified response with both IDs

    Args:
        supabase_client: Supabase client instance
        file_path: Path to file
        user_id: User ID
        filename: Filename
        bucket: Storage bucket
        tags: List of tags

    Returns:
        Unified response with both Supabase and GLM file IDs

    Raises:
        ValueError: If file exceeds size limit
        UploadError: If upload fails
    """
    from tools.provider_config import validate_file_size
    from tools.file_id_mapper import FileIdMapper

    # Validate file size
    file_size = os.path.getsize(file_path)
    is_valid, error_msg = validate_file_size(file_size, "glm")
    if not is_valid:
        raise ValueError(error_msg)

    logger.info(f"Starting GLM upload adapter for {filename} ({file_size} bytes)")

    # 1. Upload to Supabase
    upload_manager = SupabaseUploadManager(supabase_client, bucket)
    supabase_result = upload_manager.upload_file(
        file_path=file_path,
        user_id=user_id,
        filename=filename,
        bucket=bucket,
        tags=tags
    )

    supabase_file_id = supabase_result['file_id']

    try:
        # 2. Upload to GLM SDK
        from src.providers.registry import ModelProviderRegistry

        # Get GLM provider
        glm_model = os.getenv("GLM_DEFAULT_MODEL", "glm-4.6")
        provider = ModelProviderRegistry.get_provider_for_model(glm_model)

        # Upload to GLM
        glm_file_id = provider.upload_file(file_path, purpose="agent")

        logger.info(f"✅ Uploaded to GLM: {glm_file_id}")

        # 3. Store mapping with session info
        now = datetime.utcnow()
        session_info = {
            "model": glm_model,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=24)).isoformat(),
            "session_id": f"glm_session_{user_id}_{int(now.timestamp())}"
        }

        mapper = FileIdMapper(supabase_client)
        mapper.store_mapping(
            supabase_id=supabase_file_id,
            provider_id=glm_file_id,
            provider="glm",
            user_id=user_id,
            session_info=session_info,
            status="completed"
        )

        # 4. Return unified response
        return {
            "success": True,
            "supabase_file_id": supabase_file_id,
            "provider_file_id": glm_file_id,
            "provider": "glm",
            "file_size": file_size,
            "filename": filename,
            "upload_time": datetime.utcnow().isoformat(),
            "deduplicated": supabase_result.get('deduplicated', False),
            "metadata_id": supabase_result.get('metadata_id'),
            "session_info": session_info
        }

    except Exception as e:
        logger.error(f"❌ GLM upload failed: {e}")

        # Store failed mapping for retry
        mapper = FileIdMapper(supabase_client)
        mapper.store_mapping(
            supabase_id=supabase_file_id,
            provider_id=None,
            provider="glm",
            user_id=user_id,
            status="failed"
        )

        # Don't fail the whole operation - Supabase upload succeeded
        logger.warning(
            f"Provider upload failed but Supabase upload succeeded. "
            f"User: {user_id}, File: {filename}, Provider: glm, "
            f"Supabase ID: {supabase_file_id}, Error: {str(e)}"
        )

        return {
            "success": True,
            "supabase_file_id": supabase_file_id,
            "provider_file_id": None,
            "provider": "glm",
            "file_size": file_size,
            "filename": filename,
            "upload_time": datetime.utcnow().isoformat(),
            "deduplicated": supabase_result.get('deduplicated', False),
            "metadata_id": supabase_result.get('metadata_id'),
            "provider_upload_failed": True,
            "error": str(e)
        }


def upload_file_with_provider(
    supabase_client,
    file_path: str,
    provider: str = "auto",
    user_id: str = None,
    filename: str = None,
    bucket: str = "user-files",
    tags: List[str] = None
) -> Dict[str, Any]:
    """
    Universal upload function with provider routing.

    This is the main entry point for file uploads with provider integration.

    Args:
        supabase_client: Supabase client instance
        file_path: Path to file to upload
        provider: Provider name ('kimi', 'glm', 'auto', 'supabase_only')
        user_id: User ID (required)
        filename: Optional custom filename
        bucket: Storage bucket (default: 'user-files')
        tags: Optional list of tags

    Returns:
        Unified response dictionary with upload results

    Raises:
        ValueError: If parameters are invalid or file exceeds limits
        UploadError: If upload fails
    """
    from tools.provider_config import auto_select_provider

    # Validate required parameters
    if not user_id:
        raise ValueError("user_id is required")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get filename
    filename = filename or os.path.basename(file_path)
    tags = tags or []

    # Auto-detect provider if needed
    if provider == PROVIDER_AUTO:
        file_size = os.path.getsize(file_path)
        provider = auto_select_provider(file_size)
        logger.info(f"Auto-selected provider: {provider} for {filename} ({file_size} bytes)")

    # Route to appropriate adapter
    if provider == PROVIDER_KIMI:
        return _kimi_upload_adapter(
            supabase_client, file_path, user_id, filename, bucket, tags
        )
    elif provider == PROVIDER_GLM:
        return _glm_upload_adapter(
            supabase_client, file_path, user_id, filename, bucket, tags
        )
    elif provider == PROVIDER_SUPABASE_ONLY:
        # Upload only to Supabase (for large files)
        upload_manager = SupabaseUploadManager(supabase_client, bucket)
        result = upload_manager.upload_file(
            file_path=file_path,
            user_id=user_id,
            filename=filename,
            bucket=bucket,
            tags=tags
        )

        return {
            "success": True,
            "supabase_file_id": result['file_id'],
            "provider_file_id": None,
            "provider": "supabase_only",
            "file_size": result['file_size'],
            "filename": filename,
            "upload_time": datetime.utcnow().isoformat(),
            "deduplicated": result.get('deduplicated', False),
            "metadata_id": result.get('metadata_id')
        }
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ============================================================================
# APPLICATION-AWARE FILE UPLOAD (Phase A1)
# ============================================================================

def upload_file_with_app_context(
    file_path: str,
    bucket: str,
    application_id: Optional[str] = None,
    user_id: Optional[str] = None,
    provider: str = PROVIDER_AUTO,
    **kwargs
) -> Dict[str, Any]:
    """
    Upload file with application context and validation.

    Supports external applications by:
    - Validating application permissions
    - Copying files to temp location if needed
    - Processing through Supabase integration
    - Cleaning up temporary files

    Args:
        file_path: Path to file to upload
        bucket: Supabase storage bucket name
        application_id: Optional application identifier
        user_id: Optional user identifier
        provider: Provider to use (kimi, glm, auto)
        **kwargs: Additional arguments passed to upload_file_with_provider

    Returns:
        Dict with upload results including success status, file_id, etc.
    """
    from tools.temp_file_handler import temp_handler
    from utils.path_validation import validate_file_path
    from src.storage.supabase_client import get_storage_manager

    temp_path = None

    try:
        # Get Supabase client
        storage = get_storage_manager()
        supabase_client = storage.get_client()

        # Check if file is in accessible location
        is_accessible, error_msg = validate_file_path(file_path, application_id)

        if not is_accessible and application_id:
            # Copy to temp location for external applications
            logger.info(f"[APP_UPLOAD] File not accessible, copying to temp: {file_path}")
            temp_path, success, error_msg = temp_handler.copy_to_temp(file_path, application_id)

            if not success:
                return {
                    "success": False,
                    "error": f"Failed to copy file to temp: {error_msg}"
                }

            file_path = temp_path
            logger.info(f"[APP_UPLOAD] Using temp file: {temp_path}")

        # Proceed with upload using existing infrastructure (NOT async)
        result = upload_file_with_provider(
            supabase_client=supabase_client,
            file_path=file_path,
            user_id=user_id or "system",
            provider=provider,
            bucket=bucket,
            **kwargs
        )

        # Log application access if needed (run in background thread)
        if application_id and user_id:
            import threading
            import asyncio

            def run_async_logging():
                asyncio.run(log_application_access(
                    application_id,
                    user_id,
                    file_path,
                    result.get("success", False)
                ))

            thread = threading.Thread(target=run_async_logging, daemon=True)
            thread.start()

        # Cleanup temp file if used
        if temp_path:
            temp_handler.cleanup_temp_file(temp_path)
            logger.debug(f"[APP_UPLOAD] Cleaned up temp file: {temp_path}")

        return result

    except Exception as e:
        logger.error(f"[APP_UPLOAD] Upload failed: {str(e)}")

        # Cleanup temp file on error
        if temp_path:
            temp_handler.cleanup_temp_file(temp_path)

        return {
            "success": False,
            "error": str(e)
        }


async def log_application_access(
    application_id: str,
    user_id: str,
    file_path: str,
    success: bool
) -> None:
    """
    Log file access for application auditing.

    Args:
        application_id: Application identifier
        user_id: User identifier
        file_path: File path accessed
        success: Whether the access was successful
    """
    try:
        logger.info(
            f"[APP_ACCESS] app={application_id}, user={user_id}, "
            f"file={file_path}, success={success}"
        )

        # TODO: Store in database for auditing
        # This could be enhanced to write to a dedicated audit table

    except Exception as e:
        logger.error(f"[APP_ACCESS] Failed to log access: {str(e)}")
