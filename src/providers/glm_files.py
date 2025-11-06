"""GLM file upload functionality - Batch 8.2 (2025-11-02)

Consolidated with BaseFileProvider to reduce code duplication.
Maintains backward compatibility with existing upload_file function.

WEEK 1 CRITICAL UPDATE (2025-11-02):
Integrated GLM SDK fallback chain (ZhipuAI → OpenAI SDK → HTTP)
for improved resilience and compatibility.
"""

import logging
import mimetypes
import os
from pathlib import Path
from typing import Any, Optional

# Import error handling framework
from src.daemon.error_handling import ProviderError, ErrorCode, log_error

logger = logging.getLogger(__name__)


# ============================================================================
# Legacy Upload Function (Backward Compatibility)
# ============================================================================

def upload_file(
    sdk_client: Any,
    http_client: Any,
    file_path: str,
    purpose: str = "file",
    use_sdk: bool = False,
    use_fallback_chain: bool = True
) -> str:
    """Upload a file to GLM Files API and return its file id.

    CRITICAL FIX (2025-11-02): Changed default purpose from 'agent' to 'file'
    Valid purpose for GLM/Z.ai (ZhipuAI SDK): ONLY 'file' is supported

    WEEK 1 UPDATE (2025-11-02): Added SDK fallback chain support
    - Primary: ZhipuAI SDK
    - Fallback: OpenAI SDK (GLM has OpenAI compatibility)
    - Last Resort: HTTP

    Args:
        sdk_client: ZhipuAI SDK client instance (if available)
        http_client: HTTP client instance for fallback
        file_path: Path to file to upload
        purpose: Purpose of the file - MUST be 'file' (only valid value for GLM)
        use_sdk: Whether SDK is available and should be used
        use_fallback_chain: Whether to use SDK fallback chain (default: True)

    Returns:
        File ID from GLM API

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file exceeds size limit or invalid purpose
        RuntimeError: If upload fails or doesn't return an ID
    """
    # Use SDK fallback chain if enabled
    if use_fallback_chain:
        try:
            from src.providers.glm_sdk_fallback import upload_file_with_fallback

            # Get API key and base URL from environment
            api_key = os.getenv("GLM_API_KEY")
            base_url = os.getenv("GLM_API_URL", "https://api.z.ai/api/paas/v4")

            if api_key:
                file_id, method_used = upload_file_with_fallback(
                    api_key=api_key,
                    file_path=file_path,
                    purpose=purpose,
                    base_url=base_url
                )
                if file_id:
                    logger.info(f"GLM upload succeeded via fallback chain ({method_used}): {file_id}")
                    return file_id
                else:
                    logger.warning("GLM fallback chain failed, using legacy path")
        except Exception as e:
            logger.warning(f"GLM fallback chain error, using legacy path: {e}")

    # Legacy upload path (backward compatibility)
    # Validate purpose parameter (CRITICAL SECURITY FIX)
    if purpose != "file":
        raise ValueError(
            f"Invalid purpose: '{purpose}'. "
            f"GLM/Z.ai only supports purpose='file'"
        )
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Optional client-side size guardrail
    try:
        max_mb_env = os.getenv("GLM_FILES_MAX_SIZE_MB", "")
        if max_mb_env:
            max_bytes = float(max_mb_env) * 1024 * 1024
            if p.stat().st_size > max_bytes:
                raise ValueError(f"GLM upload exceeds max size {max_mb_env} MB: {p.name}")
    except ValueError:
        # Re-raise ValueError (size exceeded)
        raise
    except Exception:
        # If env is missing/malformed, rely on provider-side limits
        pass

    # Try SDK path first
    if use_sdk and sdk_client:
        try:
            # zhipuai SDK method name may vary across versions; try common variants
            # Preferred: files.upload(file=..., purpose=...)
            if hasattr(sdk_client, "files") and hasattr(sdk_client.files, "upload"):
                with p.open("rb") as f:
                    res = sdk_client.files.upload(file=f, purpose=purpose)
            elif hasattr(sdk_client, "files") and hasattr(sdk_client.files, "create"):
                with p.open("rb") as f:
                    res = sdk_client.files.create(file=f, purpose=purpose)
            else:
                res = None

            # Extract id from SDK response (object or dict)
            file_id = None
            if res is not None:
                file_id = getattr(res, "id", None)
                if not file_id and hasattr(res, "model_dump"):
                    data = res.model_dump()
                    file_id = data.get("id") or data.get("data", {}).get("id")
            if file_id:
                return str(file_id)
        except Exception as e:
            # Log at warning level and fall back to HTTP path
            logger.warning("GLM SDK upload failed, falling back to HTTP: %s", e)
            # Fall through to HTTP

    # HTTP fallback (ensure file handle is closed via context manager)
    mime, _ = mimetypes.guess_type(str(p))
    with p.open("rb") as fh:
        files = {"file": (p.name, fh, mime or "application/octet-stream")}
        # Allow configurable timeout for large uploads
        try:
            t = float(os.getenv("GLM_FILE_UPLOAD_TIMEOUT_SECS", os.getenv("FILE_UPLOAD_TIMEOUT_SECS", "120")))
        except Exception:
            t = 120.0
        logger.info("GLM upload: file=%s size=%dB timeout=%.1fs purpose=%s", p.name, p.stat().st_size, t, purpose)
        js = http_client.post_multipart("/files", files=files, data={"purpose": purpose}, timeout=t)

    file_id = js.get("id") or js.get("data", {}).get("id")
    if not file_id:
        log_error(ErrorCode.PROVIDER_ERROR, "GLM upload did not return an id")
        raise ProviderError("GLM", Exception(f"GLM upload did not return an id: {js}"))
    return str(file_id)


__all__ = ["upload_file", "GLMFileProvider"]


# ============================================================================
# Consolidated Provider Class (Batch 8.2 - 2025-11-02)
# ============================================================================

class GLMFileProvider:
    """
    Consolidated GLM file provider with common upload logic.

    This class consolidates the common file upload patterns and reduces
    code duplication across the codebase. It provides:
    - Standardized path resolution and validation
    - Size validation with configurable limits
    - SDK and HTTP client support with automatic fallback
    - Error handling with informative messages
    """

    def __init__(self, sdk_client: Any = None, http_client: Any = None, use_sdk: bool = False):
        """
        Initialize GLM file provider.

        Args:
            sdk_client: ZhipuAI SDK client instance (optional)
            http_client: HTTP client instance (optional)
            use_sdk: Whether SDK is available and should be used
        """
        self.sdk_client = sdk_client
        self.http_client = http_client
        self.use_sdk = use_sdk
        self.provider_name = "glm"

    def _resolve_path(self, file_path: str) -> Path:
        """
        Resolve and validate file path.

        Args:
            file_path: Path to resolve

        Returns:
            Resolved Path object

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return p

    def _validate_file_size(self, file_path: Path) -> None:
        """
        Validate file size against configured limits.

        Args:
            file_path: Path to validate

        Raises:
            ValueError: If file exceeds size limit
        """
        try:
            max_mb_env = os.getenv("GLM_FILES_MAX_SIZE_MB", "")
            if max_mb_env:
                max_bytes = float(max_mb_env) * 1024 * 1024
                if file_path.stat().st_size > max_bytes:
                    raise ValueError(
                        f"GLM upload exceeds max size {max_mb_env} MB: {file_path.name}"
                    )
        except ValueError:
            # Re-raise ValueError (size exceeded)
            raise
        except Exception:
            # If env is missing/malformed, rely on provider-side limits
            pass

    def _upload_via_sdk(self, file_path: Path, purpose: str) -> Optional[str]:
        """
        Attempt upload via SDK.

        Args:
            file_path: Path to upload
            purpose: Purpose of the file

        Returns:
            File ID if successful, None if SDK upload fails
        """
        if not (self.use_sdk and self.sdk_client):
            return None

        try:
            # Try SDK upload with common method names
            if hasattr(self.sdk_client, "files") and hasattr(self.sdk_client.files, "upload"):
                with file_path.open("rb") as f:
                    res = self.sdk_client.files.upload(file=f, purpose=purpose)
            elif hasattr(self.sdk_client, "files") and hasattr(self.sdk_client.files, "create"):
                with file_path.open("rb") as f:
                    res = self.sdk_client.files.create(file=f, purpose=purpose)
            else:
                return None

            # Extract ID from SDK response
            file_id = None
            if res is not None:
                file_id = getattr(res, "id", None)
                if not file_id and hasattr(res, "model_dump"):
                    data = res.model_dump()
                    file_id = data.get("id") or data.get("data", {}).get("id")

            return str(file_id) if file_id else None

        except Exception as e:
            logger.warning("GLM SDK upload failed, falling back to HTTP: %s", e)
            return None

    def _upload_via_http(self, file_path: Path, purpose: str) -> str:
        """
        Upload via HTTP client.

        Args:
            file_path: Path to upload
            purpose: Purpose of the file

        Returns:
            File ID

        Raises:
            RuntimeError: If upload fails
        """
        if not self.http_client:
            raise ValueError("No HTTP client provided for GLM upload")

        mime, _ = mimetypes.guess_type(str(file_path))

        with file_path.open("rb") as fh:
            files = {"file": (file_path.name, fh, mime or "application/octet-stream")}

            # Configurable timeout for large uploads
            try:
                t = float(os.getenv(
                    "GLM_FILE_UPLOAD_TIMEOUT_SECS",
                    os.getenv("FILE_UPLOAD_TIMEOUT_SECS", "120")
                ))
            except Exception:
                t = 120.0

            logger.info(
                "GLM upload: file=%s size=%dB timeout=%.1fs purpose=%s",
                file_path.name, file_path.stat().st_size, t, purpose
            )

            js = self.http_client.post_multipart(
                "/files",
                files=files,
                data={"purpose": purpose},
                timeout=t
            )

        file_id = js.get("id") or js.get("data", {}).get("id")
        if not file_id:
            log_error(ErrorCode.PROVIDER_ERROR, "GLM upload did not return an id")
            raise ProviderError("GLM", Exception(f"GLM upload did not return an id: {js}"))

        return str(file_id)

    def upload(
        self,
        file_path: str,
        purpose: str = "agent",
        sdk_client: Any = None,
        http_client: Any = None,
        use_sdk: bool = None
    ) -> str:
        """
        Upload a file to GLM platform.

        Args:
            file_path: Path to the file to upload
            purpose: Purpose of the file (default: "agent")
            sdk_client: SDK client (uses self.sdk_client if not provided)
            http_client: HTTP client (uses self.http_client if not provided)
            use_sdk: Whether to use SDK (uses self.use_sdk if not provided)

        Returns:
            Provider-assigned file ID

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file exceeds size limit or no client provided
            RuntimeError: If upload fails
        """
        # Use provided clients or instance clients
        upload_sdk_client = sdk_client or self.sdk_client
        upload_http_client = http_client or self.http_client
        upload_use_sdk = use_sdk if use_sdk is not None else self.use_sdk

        # Resolve and validate path
        p = self._resolve_path(file_path)
        self._validate_file_size(p)

        # Try SDK upload first
        if upload_use_sdk and upload_sdk_client:
            file_id = self._upload_via_sdk(p, purpose)
            if file_id:
                return file_id

        # Fallback to HTTP upload
        return self._upload_via_http(p, purpose)

