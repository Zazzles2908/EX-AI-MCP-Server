"""GLM SDK Fallback Implementation - Week 1 Critical Task 1 (2025-11-02)

This module implements a robust fallback chain for GLM file uploads:
1. Primary: ZhipuAI SDK (native SDK)
2. Fallback: OpenAI SDK (GLM has OpenAI compatibility)
3. Last Resort: HTTP (direct API calls)

Based on proof-of-concept testing in tests/sdk/test_glm_openai_sdk.py which
confirmed that GLM/Z.ai works with OpenAI SDK using base_url='https://api.z.ai/api/paas/v4/'.

Key Differences from Kimi:
- GLM uses different function calls even with OpenAI SDK
- GLM only supports purpose='file' (not 'assistants', 'vision', etc.)
- GLM has 512MB file size limit (same as Kimi)
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


class GLMSDKFallback:
    """
    Manages fallback chain for GLM file uploads with three tiers:
    1. ZhipuAI SDK (primary)
    2. OpenAI SDK (fallback)
    3. HTTP (last resort)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.z.ai/api/paas/v4",
        timeout: float = 120.0,
        max_retries: int = 3
    ):
        """
        Initialize GLM SDK fallback manager.
        
        Args:
            api_key: GLM API key
            base_url: GLM API base URL (default: z.ai proxy)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize clients
        self.zhipuai_client = None
        self.openai_client = None
        self.http_client = None
        
        self._init_clients()
    
    def _init_clients(self) -> None:
        """Initialize all available clients in priority order."""
        # Try ZhipuAI SDK (primary)
        try:
            from zhipuai import ZhipuAI
            self.zhipuai_client = ZhipuAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            logger.info(f"GLM fallback: ZhipuAI SDK initialized (primary)")
        except Exception as e:
            logger.warning(f"GLM fallback: ZhipuAI SDK unavailable: {e}")
        
        # Try OpenAI SDK (fallback)
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            logger.info(f"GLM fallback: OpenAI SDK initialized (fallback)")
        except Exception as e:
            logger.warning(f"GLM fallback: OpenAI SDK unavailable: {e}")
        
        # HTTP client (last resort) - always available
        try:
            from utils.http_client import HttpClient
            self.http_client = HttpClient(
                self.base_url,
                api_key=self.api_key,
                api_key_header="Authorization",
                api_key_prefix="Bearer "
            )
            logger.info(f"GLM fallback: HTTP client initialized (last resort)")
        except Exception as e:
            logger.error(f"GLM fallback: HTTP client initialization failed: {e}")
    
    def upload_file(
        self,
        file_path: str,
        purpose: str = "file"
    ) -> Tuple[Optional[str], str]:
        """
        Upload file using fallback chain.
        
        Args:
            file_path: Path to file to upload
            purpose: File purpose (must be 'file' for GLM)
        
        Returns:
            Tuple of (file_id, method_used)
            - file_id: File ID from API (None if all methods failed)
            - method_used: Which method succeeded ('zhipuai', 'openai', 'http', or 'failed')
        
        Raises:
            ValueError: If purpose is not 'file'
            FileNotFoundError: If file doesn't exist
        """
        # Validate purpose
        if purpose != "file":
            raise ValueError(
                f"Invalid purpose: '{purpose}'. "
                f"GLM only supports purpose='file'"
            )
        
        # Validate file exists
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try each method in order
        methods = [
            ("zhipuai", self._upload_via_zhipuai),
            ("openai", self._upload_via_openai),
            ("http", self._upload_via_http)
        ]
        
        for method_name, method_func in methods:
            try:
                file_id = method_func(p, purpose)
                if file_id:
                    logger.info(f"GLM upload succeeded via {method_name}: {file_id}")
                    return file_id, method_name
            except Exception as e:
                logger.warning(f"GLM upload via {method_name} failed: {e}")
                continue
        
        # All methods failed
        logger.error(f"GLM upload failed via all methods: {file_path}")
        return None, "failed"
    
    def _upload_via_zhipuai(self, file_path: Path, purpose: str) -> Optional[str]:
        """Upload using ZhipuAI SDK."""
        if not self.zhipuai_client:
            return None
        
        with file_path.open("rb") as f:
            # Try common method names
            if hasattr(self.zhipuai_client, "files") and hasattr(self.zhipuai_client.files, "upload"):
                res = self.zhipuai_client.files.upload(file=f, purpose=purpose)
            elif hasattr(self.zhipuai_client, "files") and hasattr(self.zhipuai_client.files, "create"):
                res = self.zhipuai_client.files.create(file=f, purpose=purpose)
            else:
                return None
        
        # Extract file ID
        file_id = getattr(res, "id", None)
        if not file_id and hasattr(res, "model_dump"):
            data = res.model_dump()
            file_id = data.get("id") or data.get("data", {}).get("id")
        
        return str(file_id) if file_id else None
    
    def _upload_via_openai(self, file_path: Path, purpose: str) -> Optional[str]:
        """
        Upload using OpenAI SDK.
        
        CRITICAL: GLM uses different function calls than Kimi even with OpenAI SDK.
        GLM requires purpose='file' (not 'assistants' like Kimi).
        """
        if not self.openai_client:
            return None
        
        with file_path.open("rb") as f:
            # OpenAI SDK file upload
            # NOTE: GLM accepts purpose='file' via OpenAI SDK
            res = self.openai_client.files.create(
                file=f,
                purpose=purpose
            )
        
        # Extract file ID from OpenAI SDK response
        file_id = getattr(res, "id", None)
        return str(file_id) if file_id else None
    
    def _upload_via_http(self, file_path: Path, purpose: str) -> Optional[str]:
        """Upload using direct HTTP calls."""
        if not self.http_client:
            return None
        
        import mimetypes
        
        mime, _ = mimetypes.guess_type(str(file_path))
        
        with file_path.open("rb") as fh:
            files = {"file": (file_path.name, fh, mime or "application/octet-stream")}
            
            # HTTP multipart upload
            js = self.http_client.post_multipart(
                "/files",
                files=files,
                data={"purpose": purpose},
                timeout=self.timeout
            )
        
        # Extract file ID from response
        file_id = js.get("id") or js.get("data", {}).get("id")
        return str(file_id) if file_id else None
    
    def get_available_methods(self) -> list[str]:
        """
        Get list of available upload methods.
        
        Returns:
            List of available methods ('zhipuai', 'openai', 'http')
        """
        methods = []
        if self.zhipuai_client:
            methods.append("zhipuai")
        if self.openai_client:
            methods.append("openai")
        if self.http_client:
            methods.append("http")
        return methods
    
    def health_check(self) -> dict[str, bool]:
        """
        Check health of all clients.
        
        Returns:
            Dictionary mapping method name to availability status
        """
        return {
            "zhipuai": self.zhipuai_client is not None,
            "openai": self.openai_client is not None,
            "http": self.http_client is not None
        }


# Convenience function for backward compatibility
def upload_file_with_fallback(
    api_key: str,
    file_path: str,
    purpose: str = "file",
    base_url: str = "https://api.z.ai/api/paas/v4",
    timeout: float = 120.0
) -> Tuple[Optional[str], str]:
    """
    Upload file to GLM with automatic fallback.
    
    Args:
        api_key: GLM API key
        file_path: Path to file to upload
        purpose: File purpose (must be 'file')
        base_url: GLM API base URL
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (file_id, method_used)
    """
    fallback = GLMSDKFallback(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout
    )
    return fallback.upload_file(file_path, purpose)

