"""GLM file upload functionality."""

import logging
import mimetypes
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def upload_file(
    sdk_client: Any,
    http_client: Any,
    file_path: str,
    purpose: str = "agent",
    use_sdk: bool = False
) -> str:
    """Upload a file to GLM Files API and return its file id.
    
    Uses native SDK when available; falls back to HTTP client otherwise.
    
    Args:
        sdk_client: ZhipuAI SDK client instance (if available)
        http_client: HTTP client instance for fallback
        file_path: Path to file to upload
        purpose: Purpose of the file (default: "agent")
        use_sdk: Whether SDK is available and should be used
        
    Returns:
        File ID from GLM API
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file exceeds size limit
        RuntimeError: If upload fails or doesn't return an ID
    """
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
        raise RuntimeError(f"GLM upload did not return an id: {js}")
    return str(file_id)


__all__ = ["upload_file"]

