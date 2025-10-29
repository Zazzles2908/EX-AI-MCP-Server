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

# Provider tools (MCP wrappers - NOT low-level providers)
from tools.providers.kimi.kimi_files import KimiUploadFilesTool, KimiChatWithFilesTool
from tools.providers.glm.glm_files import GLMUploadFileTool, GLMMultiFileChatTool

# Base tool
from tools.shared.base_tool import BaseTool
from tools.models import ToolOutput
from mcp.types import TextContent

# Phase 2: Async upload feature flags and monitoring
from tools.config.async_upload_config import get_config
from tools.monitoring.async_upload_metrics import get_metrics_collector, UploadMetrics

logger = logging.getLogger(__name__)


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

        # FIX (2025-10-29): Lazy initialization to avoid sync init of async tools
        # Tools will be initialized on first use via _ensure_tools_initialized()
        self.kimi_upload = None
        self.kimi_chat = None
        self.glm_upload = None
        self.glm_chat = None
        self._tools_initialized = False

        # FIX (2025-10-29): Add async lock for thread-safe initialization
        # EXAI QA: Prevents race condition when multiple concurrent calls initialize tools
        self._init_lock = asyncio.Lock()
    
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

    async def _ensure_tools_initialized(self):
        """
        Ensure provider tools are properly initialized asynchronously.

        FIX (2025-10-29): Added lazy async initialization to avoid sync init of async tools.
        FIX (2025-10-29): Added async lock for thread-safe initialization.
        EXAI Consultation: 01bc55a8-86e9-467b-a4e8-351ec6cea6ea
        EXAI QA: Added lock to prevent race condition with concurrent calls

        This method:
        1. Uses async lock to prevent race conditions
        2. Checks if tools are already initialized
        3. Initializes tools asynchronously if they have async init methods
        4. Falls back to sync init in thread pool if needed
        5. Marks tools as initialized to avoid re-initialization
        """
        # FIX: Use async lock to prevent race condition
        async with self._init_lock:
            if self._tools_initialized:
                return

            logger.info("[SMART_FILE_QUERY] Initializing provider tools asynchronously...")

            try:
                # Initialize Kimi tools
                self.kimi_upload = KimiUploadFilesTool()
                self.kimi_chat = KimiChatWithFilesTool()

                # Initialize GLM tools
                self.glm_upload = GLMUploadFileTool()
                self.glm_chat = GLMMultiFileChatTool()

                # Check if tools have async initialization methods
                for tool_name, tool in [
                    ("kimi_upload", self.kimi_upload),
                    ("kimi_chat", self.kimi_chat),
                    ("glm_upload", self.glm_upload),
                    ("glm_chat", self.glm_chat)
                ]:
                    if hasattr(tool, 'initialize_async'):
                        logger.info(f"[SMART_FILE_QUERY] Async initializing {tool_name}...")
                        await tool.initialize_async()
                    elif hasattr(tool, 'initialize'):
                        logger.info(f"[SMART_FILE_QUERY] Sync initializing {tool_name} in thread pool...")
                        await asyncio.to_thread(tool.initialize)

                self._tools_initialized = True
                logger.info("[SMART_FILE_QUERY] All provider tools initialized successfully")

            except Exception as e:
                logger.error(f"[SMART_FILE_QUERY] Failed to initialize provider tools: {e}")
                self._tools_initialized = False
                raise

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
        # FIX (2025-10-29): Ensure tools are initialized before use
        await self._ensure_tools_initialized()

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

        # Step 3: Select provider
        provider = self._select_provider(provider_pref, file_size_mb)
        logger.info(f"[SMART_FILE_QUERY] Selected provider: {provider}")

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

            logger.info(f"[SMART_FILE_QUERY] Query successful")
            return result
        except TimeoutError as e:
            logger.error(f"[SMART_FILE_QUERY] Query timed out: {e}")
            raise
        except Exception as e:
            logger.error(f"[SMART_FILE_QUERY] Query failed: {e}")
            raise
    
    def _select_provider(self, preference: str, file_size_mb: float) -> str:
        """
        Select provider based on user preference and file size.

        Logic:
        1. ALWAYS use Kimi for file operations (GLM cannot handle pre-uploaded files)
        2. User preference only applies to non-file operations
        3. File size validation:
           - >100MB: Error (exceeds Kimi limit)

        FIX (2025-10-29): Force Kimi for ALL file operations due to GLM's file persistence limitation.
        EXAI Consultation: 7fe98857-42ce-4195-a889-76106496e00f
        """
        # CRITICAL: Always use Kimi for file operations
        # GLM requires re-uploading files for each query (no file persistence)
        logger.info(f"[SMART_FILE_QUERY] Forcing Kimi provider for file operations (requested: {preference})")

        # File size validation
        if file_size_mb > 100:
            raise ValueError(f"File size {file_size_mb:.2f}MB exceeds maximum limit of 100MB")

        return "kimi"  # Always Kimi for file operations
    
    async def _upload_file(self, file_path: str, provider: str) -> str:
        """
        Upload file using provider-specific tool asynchronously.

        FIX (2025-10-29): Changed to async method to avoid blocking event loop.
        FIX (2025-10-29): Added file validation and comprehensive error handling.
        EXAI Consultation: 01bc55a8-86e9-467b-a4e8-351ec6cea6ea
        EXAI QA: Added file validation and error handling

        Phase 2: Integrated with async feature flags and metrics collection.

        Returns:
            Provider file ID

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file is not readable
            ValueError: If upload fails or returns no file ID
        """
        import time

        # FIX (2025-10-29): Ensure tools are initialized before upload
        await self._ensure_tools_initialized()

        # FIX (2025-10-29): Validate file exists and is readable
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
        execution_type = "async"  # FIX: Always async now
        error_type = None

        try:
            # Determine if this upload should use async (based on rollout percentage)
            should_use_async = config.enabled and config.should_use_async(file_path)
            if should_use_async:
                logger.info(f"[SMART_FILE_QUERY] Using async upload for {file_path} (rollout: {config.rollout_percentage}%)")

            # FIX (2025-10-29): Perform upload asynchronously with comprehensive error handling
            # Check if tools have async methods, otherwise run sync methods in thread pool
            try:
                if provider == "kimi":
                    # Check if kimi_upload has async method
                    if hasattr(self.kimi_upload, '_run_async'):
                        result = await self.kimi_upload._run_async(files=[file_path], purpose="file-extract")
                    else:
                        # Fallback to sync method in thread pool
                        result = await asyncio.to_thread(
                            self.kimi_upload._run, files=[file_path], purpose="file-extract"
                        )

                    if result and len(result) > 0:
                        file_id = result[0]['file_id']
                    else:
                        raise ValueError("Kimi upload returned no file ID")

                elif provider == "glm":
                    # Check if glm_upload has async method
                    if hasattr(self.glm_upload, 'run_async'):
                        result = await self.glm_upload.run_async(file=file_path, purpose="agent")
                    else:
                        # Fallback to sync method in thread pool
                        result = await asyncio.to_thread(
                            self.glm_upload.run, file=file_path, purpose="agent"
                        )

                    if result and 'file_id' in result:
                        file_id = result['file_id']
                    else:
                        raise ValueError("GLM upload returned no file ID")
                else:
                    raise ValueError(f"Unknown provider: {provider}")
            except Exception as upload_error:
                # FIX (2025-10-29): Wrap upload errors with context
                raise ValueError(f"Failed to upload {file_path} to {provider}: {str(upload_error)}") from upload_error

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
        Query file using provider-specific chat tool.

        FIX (2025-10-29): Changed to async and use _run_async() for KimiChatWithFilesTool.
        EXAI Consultation: 7fe98857-42ce-4195-a889-76106496e00f

        Returns:
            Query result content (string)
        """
        if provider == "kimi":
            # FIX: Use _run_async() instead of _run() - KimiChatWithFilesTool only has async method
            result = await self.kimi_chat._run_async(
                prompt=question,
                file_ids=[file_id],
                model=model if model != "auto" else "kimi-k2-0905-preview"
            )
            # Extract content from result dict
            if isinstance(result, dict):
                return result.get('content', str(result))
            return str(result)
        elif provider == "glm":
            # GLM multi-file chat doesn't support pre-uploaded files
            # This is a fundamental limitation of GLM's API design
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

