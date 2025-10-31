"""
Smart File Query Tool - Unified file upload and query interface.

This tool consolidates 6+ file upload tools into ONE intelligent interface with:
- Automatic SHA256-based deduplication
- Intelligent provider selection (Kimi vs GLM)
- Automatic fallback on provider failure
- Centralized Supabase tracking
- Path validation and security checks

Created: 2025-10-29
Architecture: Orchestrator pattern (reuses existing infrastructure)
EXAI Consultation: ed0f9ee4-906a-4cd7-848e-4a49bb93de6b, 7fe98857-42ce-4195-a889-76106496e00f

PROVIDER CAPABILITIES:
=====================

Kimi (Moonshot):
- File operations: ✅ Full support with persistent file uploads
- File persistence: ✅ Files remain uploaded across multiple queries
- Max file size: ✅ 100MB per file
- Async operations: ✅ Full async support
- Best for: Document analysis, file queries, long conversations, ANY file operations

GLM (Z.ai):
- File operations: ⚠️ SEVERELY LIMITED (files must be re-uploaded for each query)
- File persistence: ❌ NO file persistence across queries
- Max file size: ⚠️ 20MB limit
- Async operations: ✅ Full async support
- Best for: Quick text queries WITHOUT files, coding assistance

Auto Selection:
- With files: ALWAYS selects Kimi (GLM cannot handle pre-uploaded files)
- Without files: Selects based on query complexity
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Path handling - use existing CrossPlatformPathHandler
from utils.file.cross_platform import get_path_handler

# Deduplication
from utils.file.deduplication import FileDeduplicationManager

# Storage
from src.storage.hybrid_supabase_manager import HybridSupabaseManager

# Direct Supabase hub and provider access (NO tool wrappers)
from tools.supabase_upload import upload_file_with_provider
from src.storage.supabase_client import get_storage_manager
from src.providers.registry import ModelProviderRegistry

# Base tool
from tools.shared.base_tool import BaseTool
from tools.models import ToolOutput
from mcp.types import TextContent

# Phase 2: Async upload feature flags and monitoring
from tools.config.async_upload_config import get_config
from tools.monitoring.async_upload_metrics import get_metrics_collector, UploadMetrics

# Phase A2 Week 2: Security infrastructure
from src.security.rate_limiter import RateLimiter
from src.security.audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class RateLimitExceededError(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class SmartFileQueryTool(BaseTool):
    """
    Unified file upload and query interface.
    
    Orchestrates file operations across multiple providers with automatic:
    - Deduplication (SHA256-based)
    - Provider selection (file size + user preference)
    - Fallback (GLM fails → Kimi, vice versa)
    - Supabase tracking
    """
    
    def __init__(self):
        super().__init__()
        self.storage_manager = HybridSupabaseManager()
        # FIX (2025-10-29): Pass storage_manager to dedup_manager so it can access database
        # CRITICAL BUG: Was initialized without storage, causing all dedup checks to fail
        self.dedup_manager = FileDeduplicationManager(storage_manager=self.storage_manager)

        # Phase A2 Cleanup: Removed tool wrapper instances
        # Now using Supabase hub (upload_file_with_provider) directly
        # No initialization needed - hub functions are stateless

        # Phase A2 Week 2: Security infrastructure (graceful degradation)
        try:
            self.rate_limiter = RateLimiter()
            logger.info("[SMART_FILE_QUERY] Rate limiter initialized")
        except Exception as e:
            logger.warning(f"[SMART_FILE_QUERY] Rate limiter initialization failed: {e}. Rate limiting disabled.")
            self.rate_limiter = None

        try:
            self.audit_logger = AuditLogger()
            logger.info("[SMART_FILE_QUERY] Audit logger initialized")
        except Exception as e:
            logger.warning(f"[SMART_FILE_QUERY] Audit logger initialization failed: {e}. Audit logging disabled.")
            self.audit_logger = None
    
    @staticmethod
    def get_name() -> str:
        return "smart_file_query"
    
    @staticmethod
    def get_description() -> str:
        return """
        Unified file upload and query interface with automatic deduplication and provider selection.

        USE THIS TOOL for ALL file operations instead of individual upload/chat tools.

        ⚠️ CRITICAL PATH REQUIREMENTS:
        - Files MUST exist within the mounted project directory
        - Accessible paths: /mnt/project/EX-AI-MCP-Server/*, /mnt/project/Personal_AI_Agent/*
        - Files outside these directories are NOT accessible
        - If you need to analyze external files, they must be copied into the project first

        🔧 PROVIDER CAPABILITIES:
        - Kimi: ✅ Full file support, persistent uploads, 100MB limit
        - GLM: ❌ NO file persistence (must re-upload each query), 20MB limit
        - Auto: ALWAYS uses Kimi for file operations (GLM cannot handle pre-uploaded files)

        Features:
        - Automatic SHA256-based deduplication (reuses existing uploads)
        - Intelligent provider selection (ALWAYS Kimi for files)
        - Automatic fallback (GLM fails → Kimi, vice versa)
        - Centralized Supabase tracking
        - Path validation and security checks

        Example: smart_file_query(file_path="/mnt/project/EX-AI-MCP-Server/src/file.py", question="Analyze this code")

        Note: When files are provided, Kimi will ALWAYS be used regardless of provider setting due to GLM's file handling limitations.
        """
    
    @staticmethod
    def get_input_schema() -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                    "file_path": {
                    "type": "string",
                    "description": "REQUIRED. Absolute Linux path to file within mounted directories. MUST start with /mnt/project/EX-AI-MCP-Server/ or /mnt/project/Personal_AI_Agent/. Files outside these directories are NOT accessible. Windows paths NOT supported.",
                    "pattern": "^/mnt/project/(EX-AI-MCP-Server|Personal_AI_Agent)/.*"
                },
                "question": {
                    "type": "string",
                    "description": "REQUIRED. Question or instruction about the file."
                },
                "provider": {
                    "type": "string",
                    "description": "Optional. Provider to use: 'kimi', 'glm', or 'auto' (default). Auto selects based on file size.",
                    "enum": ["auto", "kimi", "glm"],
                    "default": "auto"
                },
                "model": {
                    "type": "string",
                    "description": "Optional. Specific model to use or 'auto' (default).",
                    "default": "auto"
                }
            },
            "required": ["file_path", "question"]
        }
    
    @staticmethod
    def get_system_prompt() -> str:
        from configurations.file_handling_guidance import SMART_FILE_QUERY_GUIDANCE
        return SMART_FILE_QUERY_GUIDANCE

    # Phase A2 Cleanup: Removed _ensure_tools_initialized()
    # No longer needed - using Supabase hub directly (stateless functions)

    async def execute(
        self,
        arguments: Dict[str, Any],
        on_chunk: Optional[Any] = None
    ) -> List[TextContent]:
        """
        Execute smart file query asynchronously.

        FIX (2025-10-29): Changed to call async _run_async() instead of sync _run().
        EXAI Consultation: 7fe98857-42ce-4195-a889-76106496e00f

        Args:
            arguments: Tool arguments (file_path, question, provider, model)
            on_chunk: Optional streaming callback (not used for file operations)

        Returns:
            List[TextContent]: Formatted response
        """
        logger.info(f"[SMART_FILE_QUERY] execute() called with arguments: {list(arguments.keys())}")

        try:
            # FIX: Call async _run_async() directly (no thread pool needed)
            result = await self._run_async(**arguments)

            # Format result as ToolOutput
            output = ToolOutput(
                status="success",
                content=result,
                content_type="text"
            )

            logger.info(f"[SMART_FILE_QUERY] execute() completed successfully")
            return [TextContent(type="text", text=output.model_dump_json())]

        except TimeoutError as e:
            # FIX (2025-10-29): Specific handling for timeout errors with helpful suggestions
            logger.error(f"[SMART_FILE_QUERY] Timeout error: {e}", exc_info=True)
            error_output = ToolOutput(
                status="error",
                content=str(e),
                content_type="text",
                metadata={
                    "error_type": "timeout",
                    "file_path": arguments.get("file_path"),
                    "provider": "kimi",
                    "suggestion": (
                        "File analysis timed out. This can happen with large or complex files. "
                        "Try: 1) Using a smaller file, 2) Simplifying your question, "
                        "3) Breaking the file into smaller chunks."
                    )
                }
            )
            return [TextContent(type="text", text=error_output.model_dump_json())]

        except Exception as e:
            # FIX (2025-10-29): Distinguish between upload and chat failures
            logger.error(f"[SMART_FILE_QUERY] execute() failed: {e}", exc_info=True)
            error_type = "upload_failed" if "upload" in str(e).lower() else "query_failed"
            error_output = ToolOutput(
                status="error",
                content=str(e),
                content_type="text",
                metadata={
                    "error_type": error_type,
                    "file_path": arguments.get("file_path"),
                    "provider": arguments.get("provider", "auto")
                }
            )
            return [TextContent(type="text", text=error_output.model_dump_json())]

    async def _run_async(self, **kwargs) -> str:
        """
        Execute smart file query with automatic deduplication and provider selection.

        FIX (2025-10-29): Changed return type to str (content only) instead of Dict.
        FIX (2025-10-29): Added lazy tool initialization before use.
        EXAI Consultation: 7fe98857-42ce-4195-a889-76106496e00f, 01bc55a8-86e9-467b-a4e8-351ec6cea6ea

        Workflow:
        1. Ensure tools are initialized
        2. Validate path
        3. Check deduplication (reuse existing upload if found)
        4. Select provider (ALWAYS Kimi for file operations)
        5. Upload file (if not already uploaded)
        6. Query with file
        7. Fallback on failure

        Returns:
            Query result content as string
        """
        # Phase A2 Cleanup: No initialization needed (using Supabase hub directly)

        file_path = kwargs.get("file_path")
        question = kwargs.get("question")
        provider_pref = kwargs.get("provider", "auto")
        model = kwargs.get("model", "auto")

        if not file_path or not question:
            raise ValueError("Both file_path and question are required")

        # Step 1: Path normalization using existing CrossPlatformPathHandler
        # This handles Windows → Linux conversion (c:\Project\... → /mnt/project/...)
        path_handler = get_path_handler()
        normalized_path, was_converted, error_message = path_handler.normalize_path(file_path)

        if error_message:
            raise ValueError(f"Path validation failed: {error_message}")

        if was_converted:
            logger.info(f"[SMART_FILE_QUERY] Path converted: {file_path} → {normalized_path}")

        # Step 2: Check file exists and get size
        if not os.path.exists(normalized_path):
            raise FileNotFoundError(f"File not found: {normalized_path}")

        file_size = os.path.getsize(normalized_path)
        file_size_mb = file_size / (1024 * 1024)
        logger.info(f"[SMART_FILE_QUERY] File: {normalized_path}, Size: {file_size_mb:.2f}MB")

        # Phase A2 Week 2: Rate limiting check (before file operations)
        application_id = kwargs.get('application_id', 'system')
        user_id = kwargs.get('user_id', 'system')

        if self.rate_limiter:
            try:
                rate_check = self.rate_limiter.check_rate_limit(
                    application_id=application_id,
                    operation='file_upload',
                    size_mb=file_size_mb
                )

                if not rate_check['allowed']:
                    limits = rate_check['limits']
                    logger.warning(f"[SMART_FILE_QUERY] Rate limit exceeded for {application_id}: {limits}")
                    raise RateLimitExceededError(
                        f"Rate limit exceeded for application '{application_id}'. "
                        f"Limits: {limits['requests_per_minute']['remaining']} req/min remaining, "
                        f"{limits['files_per_hour']['remaining']} files/hour remaining, "
                        f"{limits['mb_per_day']['remaining']:.2f} MB/day remaining"
                    )

                logger.info(f"[SMART_FILE_QUERY] Rate limit check passed for {application_id}")
            except RateLimitExceededError:
                raise  # Re-raise rate limit errors
            except Exception as e:
                logger.warning(f"[SMART_FILE_QUERY] Rate limit check failed: {e}. Proceeding without rate limiting.")

        # Step 3: Select provider (always Kimi for file operations)
        provider = self._select_provider(file_size_mb)
        logger.debug(f"[SMART_FILE_QUERY] Selected provider: {provider}")

        # Step 4: Check deduplication (async to avoid blocking)
        # FIX (2025-10-29): Run deduplication check in thread pool to avoid blocking event loop
        existing_upload = await asyncio.to_thread(
            self.dedup_manager.check_duplicate, normalized_path, provider
        )

        if existing_upload:
            logger.info(f"[SMART_FILE_QUERY] Deduplication HIT - reusing existing upload: {existing_upload['provider_file_id']}")
            file_id = existing_upload['provider_file_id']
            # FIX (2025-10-29): Increment reference count with correct parameters (async)
            await asyncio.to_thread(
                self.dedup_manager.increment_reference, file_id, provider
            )
        else:
            logger.info(f"[SMART_FILE_QUERY] Deduplication MISS - uploading new file")
            # Step 5: Upload file (async to avoid blocking)
            try:
                file_id = await self._upload_file(normalized_path, provider)
                logger.info(f"[SMART_FILE_QUERY] Upload successful: {file_id}")

                # FIX (2025-10-29): Register new file in database for future deduplication (async)
                await asyncio.to_thread(
                    self.dedup_manager.register_new_file,
                    provider_file_id=file_id,
                    supabase_file_id=None,  # Not stored in Supabase storage
                    file_path=normalized_path,
                    provider=provider,
                    upload_method="direct"
                )
                logger.info(f"[SMART_FILE_QUERY] File registered for deduplication: {file_id}")
            except Exception as e:
                logger.error(f"[SMART_FILE_QUERY] Upload failed with {provider}: {e}")
                # Try fallback provider
                fallback_provider = "kimi" if provider == "glm" else "glm"
                logger.info(f"[SMART_FILE_QUERY] Attempting fallback to {fallback_provider}")
                try:
                    file_id = await self._upload_file(normalized_path, fallback_provider)
                    provider = fallback_provider  # Update provider for query
                    logger.info(f"[SMART_FILE_QUERY] Fallback upload successful: {file_id}")
                except Exception as fallback_error:
                    logger.error(f"[SMART_FILE_QUERY] Fallback upload also failed: {fallback_error}")
                    raise ValueError(f"Upload failed with both providers. Primary: {e}, Fallback: {fallback_error}")
        
        # Step 6: Query with file (with retry logic and progress indicators)
        try:
            from utils.progress import send_progress

            # Progress indicator: Starting analysis
            send_progress(f"Analyzing file with {model}...")

            # FIX (2025-10-29): Use retry wrapper instead of direct call
            result = await self._query_with_file_with_retry(file_id, question, provider, model, max_retries=2)

            # Progress indicator: Complete
            send_progress("Analysis complete!")

            # Phase A2 Week 2: Audit logging (after successful operation)
            if self.audit_logger:
                try:
                    self.audit_logger.log_file_access(
                        application_id=application_id,
                        user_id=user_id,
                        file_path=normalized_path,
                        operation='file_query',
                        provider=provider,
                        additional_data={
                            'file_size_mb': file_size_mb,
                            'model': model,
                            'file_id': file_id
                        }
                    )
                    logger.debug(f"[SMART_FILE_QUERY] Audit log recorded for {application_id}")
                except Exception as e:
                    logger.warning(f"[SMART_FILE_QUERY] Audit logging failed: {e}. Continuing without audit log.")

            logger.info(f"[SMART_FILE_QUERY] Query successful")
            return result
        except TimeoutError as e:
            logger.error(f"[SMART_FILE_QUERY] Query timed out: {e}")
            raise
        except Exception as e:
            logger.error(f"[SMART_FILE_QUERY] Query failed: {e}")
            raise
    
    def _select_provider(self, file_size_mb: float) -> str:
        """
        Select provider for file operations.

        CRITICAL: Always returns 'kimi' because:
        - GLM requires re-uploading files for each query (no file persistence)
        - Kimi supports persistent file references across queries
        - Kimi has 100MB limit vs GLM's 20MB limit

        Args:
            file_size_mb: File size in MB

        Returns:
            'kimi' - the only supported provider for file operations

        Raises:
            ValueError: If file size exceeds 100MB limit
        """
        if file_size_mb > 100:
            raise ValueError(f"File size {file_size_mb:.2f}MB exceeds maximum limit of 100MB")

        logger.debug(f"[SMART_FILE_QUERY] Using Kimi provider (size: {file_size_mb:.2f}MB)")
        return "kimi"
    
    async def _upload_file(self, file_path: str, provider: str, **kwargs) -> str:
        """
        Upload file using Supabase hub directly (no tool wrappers).

        Phase A2 Cleanup: Refactored to use upload_file_with_provider() directly.
        Removed dependency on tool wrapper classes.

        Returns:
            Provider file ID

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file is not readable
            ValueError: If upload fails or returns no file ID
        """
        import time

        # Validate file exists and is readable
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {file_path}")

        # Get file size for metrics
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # Get config and metrics collector
        config = get_config()
        metrics_collector = get_metrics_collector()

        start_time = time.time()
        execution_type = "async"
        error_type = None

        try:
            # Get Supabase client
            storage = get_storage_manager()
            supabase_client = storage.get_client()

            # Extract user_id from kwargs (for audit logging)
            user_id = kwargs.get('user_id', 'system')

            # Call Supabase hub directly (no tool wrappers)
            result = await asyncio.to_thread(
                upload_file_with_provider,
                supabase_client=supabase_client,
                file_path=file_path,
                provider=provider,
                user_id=user_id
            )

            # Extract file_id from result
            if provider == "kimi":
                file_id = result.get('kimi_file_id')
            elif provider == "glm":
                file_id = result.get('glm_file_id')
            else:
                raise ValueError(f"Unknown provider: {provider}")

            if not file_id:
                raise ValueError(f"{provider} upload returned no file ID")

            # Record successful upload metrics
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_upload(UploadMetrics(
                execution_type=execution_type,
                success=True,
                duration_ms=duration_ms,
                file_size_mb=file_size_mb,
                provider=provider,
                request_id=file_path
            ))

            logger.info(f"[SMART_FILE_QUERY] Upload successful: {file_id} ({duration_ms:.2f}ms)")
            return file_id

        except Exception as e:
            error_type = type(e).__name__
            duration_ms = (time.time() - start_time) * 1000

            # Record failed upload metrics
            metrics_collector.record_upload(UploadMetrics(
                execution_type=execution_type,
                success=False,
                duration_ms=duration_ms,
                error_type=error_type,
                file_size_mb=file_size_mb,
                provider=provider,
                request_id=file_path
            ))

            logger.error(f"[SMART_FILE_QUERY] Upload failed: {error_type} - {e}")
            raise
    
    async def _query_with_file(self, file_id: str, question: str, provider: str, model: str) -> str:
        """
        Query file using provider directly (no tool wrappers).

        Phase A2 Cleanup: Refactored to use ModelProviderRegistry directly.
        Removed dependency on tool wrapper classes.

        Returns:
            Query result content (string)
        """
        if provider == "kimi":
            # Get Kimi provider instance
            model_to_use = model if model != "auto" else "kimi-k2-0905-preview"
            provider_instance = ModelProviderRegistry.get_provider_for_model(model_to_use)

            if not provider_instance:
                raise ValueError(f"No provider found for model: {model_to_use}")

            # Build messages with file_ids
            messages = [
                {
                    "role": "user",
                    "content": question
                }
            ]

            # Call provider's chat_completion_async directly
            result = await provider_instance.chat_completion_async(
                messages=messages,
                model=model_to_use,
                file_ids=[file_id]  # Kimi supports file_ids parameter
            )

            # Extract content from result
            if isinstance(result, dict):
                return result.get('content', str(result))
            return str(result)

        elif provider == "glm":
            # GLM doesn't support pre-uploaded files
            raise NotImplementedError(
                "GLM does not support file operations efficiently. "
                "Files are automatically routed to Kimi provider. "
                "If you see this error, it's a bug - provider selection should have forced Kimi."
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _query_with_file_with_retry(
        self,
        file_id: str,
        question: str,
        provider: str,
        model: str,
        max_retries: int = 2
    ) -> str:
        """
        Query file with automatic retry on timeout.

        FIX (2025-10-29): Added retry logic to handle transient timeouts.

        Args:
            file_id: Provider file ID
            question: Query question
            provider: Provider name (kimi/glm)
            model: Model name
            max_retries: Maximum retry attempts (default: 2)

        Returns:
            Query result content

        Raises:
            TimeoutError: If all retries timeout
            Exception: Other errors
        """
        import time

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"[SMART_FILE_QUERY] Query attempt {attempt + 1}/{max_retries + 1}")
                result = await self._query_with_file(file_id, question, provider, model)
                logger.info(f"[SMART_FILE_QUERY] Query successful on attempt {attempt + 1}")
                return result
            except (TimeoutError, asyncio.TimeoutError) as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"[SMART_FILE_QUERY] Query timeout on attempt {attempt + 1}, "
                        f"retrying in {wait_time}s... ({e})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"[SMART_FILE_QUERY] Query failed after {max_retries + 1} attempts")
                    raise TimeoutError(
                        f"File query timed out after {max_retries + 1} attempts. "
                        f"The file may be too large or complex for analysis. "
                        f"Try with a smaller file or simpler query."
                    )
            except Exception as e:
                # Don't retry on non-timeout errors
                logger.error(f"[SMART_FILE_QUERY] Query failed with non-timeout error: {e}")
                raise


# Export
__all__ = ['SmartFileQueryTool']

