"""GLM file upload functionality - ZAI SDK ONLY (2025-11-16)

Uses zai-sdk==0.0.4 exclusively for all GLM file operations.

CRITICAL UPDATE (2025-11-16):
- Removed fallback chain dependencies
- Uses zai-sdk==0.0.4 exclusively
- All functionality provided by zai-sdk ZaiClient
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

from src.daemon.error_handling import ProviderError, ErrorCode, log_error

logger = logging.getLogger(__name__)


def upload_file(
    sdk_client: Any,
    http_client: Any,
    file_path: str,
    purpose: str = "file",
    use_sdk: bool = False,
    **kwargs
) -> str:
    """Upload a file to GLM Files API using zai-sdk and return its file id.

    CRITICAL FIX (2025-11-16): Uses zai-sdk==0.0.4 exclusively
    Valid purpose for GLM/Z.ai (zai-sdk): ONLY 'file' is supported

    Args:
        sdk_client: zai-sdk ZaiClient instance (if available)
        http_client: HTTP client instance for fallback
        file_path: Path to file to upload
        purpose: Purpose of the file - MUST be 'file' (only valid value for GLM)
        use_sdk: Whether zai-sdk should be used
        **kwargs: Additional parameters (ignored for compatibility)

    Returns:
        File ID from GLM API

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file exceeds size limit or invalid purpose
        RuntimeError: If upload fails or doesn't return an ID
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Validate purpose parameter
    if purpose != "file":
        raise ValueError(
            f"Invalid purpose: '{purpose}'. "
            f"GLM/Z.ai only supports purpose='file'"
        )

    # Use zai-sdk directly if available
    if use_sdk and sdk_client:
        try:
            # Use zai-sdk files API
            with open(file_path, 'rb') as f:
                response = sdk_client.files.create(
                    file=f,
                    purpose=purpose
                )
            
            # Extract file ID from response
            if hasattr(response, 'id'):
                file_id = response.id
            elif hasattr(response, 'model_dump'):
                data = response.model_dump()
                file_id = data.get("id")
            else:
                file_id = str(response)
            
            if file_id:
                logger.info(f"GLM upload succeeded via zai-sdk: {file_id}")
                return file_id
            else:
                raise RuntimeError("zai-sdk upload did not return file ID")
            
        except Exception as e:
            logger.warning(f"zai-sdk upload failed: {e}")
            # Fall through to HTTP client fallback
            if not http_client:
                raise ProviderError("GLM", Exception(f"zai-sdk upload failed and no HTTP fallback available: {e}"))
    
    # HTTP client fallback
    if http_client:
        try:
            # Implement HTTP upload logic here if needed
            # For now, raise an error since we expect zai-sdk to work
            raise RuntimeError("HTTP upload not implemented - zai-sdk should handle all uploads")
        except Exception as e:
            logger.error(f"HTTP upload failed: {e}")
            raise ProviderError("GLM", Exception(f"All upload methods failed: {e}"))
    
    raise ProviderError("GLM", Exception("No upload method available - neither zai-sdk nor HTTP client provided"))


def download_file(file_id: str, sdk_client: Any, **kwargs) -> bytes:
    """Download a file from GLM Files API.
    
    Args:
        file_id: File ID to download
        sdk_client: zai-sdk ZaiClient instance
        **kwargs: Additional parameters
        
    Returns:
        File content as bytes
        
    Raises:
        RuntimeError: If download fails
    """
    if not sdk_client:
        raise RuntimeError("zai-sdk client required for file download")
    
    try:
        response = sdk_client.files.retrieve(file_id)
        if hasattr(response, 'content'):
            return response.content
        else:
            # Handle different response formats
            raise RuntimeError("zai-sdk download response format not supported")
    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise RuntimeError(f"Download failed: {e}")


def delete_file(file_id: str, sdk_client: Any, **kwargs) -> bool:
    """Delete a file from GLM Files API.
    
    Args:
        file_id: File ID to delete
        sdk_client: zai-sdk ZaiClient instance
        **kwargs: Additional parameters
        
    Returns:
        True if successful
        
    Raises:
        RuntimeError: If deletion fails
    """
    if not sdk_client:
        raise RuntimeError("zai-sdk client required for file deletion")
    
    try:
        sdk_client.files.delete(file_id)
        logger.info(f"GLM file deleted: {file_id}")
        return True
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise RuntimeError(f"Deletion failed: {e}")
