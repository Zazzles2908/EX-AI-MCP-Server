"""
Kimi File Management Tools - Clean Single-Purpose Architecture

Three tools for Kimi file operations:
1. KimiUploadFilesTool - Upload files, return file IDs only
2. KimiChatWithFilesTool - Chat with previously uploaded file IDs
3. KimiManageFilesTool - List, delete, cleanup file operations
"""

from __future__ import annotations

import json
import logging
import os
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta

from mcp.types import TextContent

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest
from src.providers.kimi import KimiModelProvider
from src.providers.registry import ModelProviderRegistry
from utils.file.cross_platform import get_path_handler
from utils.file.cache import FileCache
from utils.file.deduplication import FileDeduplicationManager

logger = logging.getLogger(__name__)


# ============================================================================
# SUPABASE GATEWAY FUNCTIONS (Phase 2 - 2025-10-26)
# ============================================================================

# PHASE 5 CLEANUP (2025-10-30):
# Removed upload_via_supabase_gateway_kimi() function (~133 lines)
# This function is now redundant - replaced by upload_file_with_provider() in tools/supabase_upload.py
# The new implementation provides:
# - Better error handling
# - Retry logic
# - Bidirectional ID mapping via FileIdMapper
# - Consistent interface with GLM

class KimiUploadFilesTool(BaseTool):
    """Upload files to Moonshot/Kimi and return file IDs only (no content extraction)"""
    
    def get_name(self) -> str:
        return "kimi_upload_files"

    def get_description(self) -> str:
        return (
            "Upload files to Moonshot/Kimi platform (100MB limit, multiple files supported). "
            "\n\n🎯 USE CASES: Large documents (>5MB), multiple files, PDFs, long-term file reference"
            "\n📁 PATH REQUIREMENTS: Linux container paths ONLY - Format: /mnt/project/EX-AI-MCP-Server/filename.ext"
            "\n⚡ ALTERNATIVE: Use glm_upload_file for single files <20MB, quick analysis"
            "\n\nDoes NOT extract content - just uploads and returns file IDs. "
            "Use kimi_chat_with_files to analyze uploaded files."
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "pattern": "^/mnt/project/.*"
                    },
                    "description": (
                        "Linux container paths ONLY. Format: /mnt/project/EX-AI-MCP-Server/filename.ext\n"
                        "❌ Windows paths (c:\\Project\\...) will be REJECTED\n"
                        "❌ Relative paths (./file.txt) will be REJECTED\n"
                        "✅ Only files under c:\\Project\\ are accessible at /mnt/project/ in the container"
                    ),
                },
                "purpose": {
                    "type": "string",
                    "enum": ["file-extract", "assistants"],
                    "default": "file-extract",
                    "description": "File purpose: 'file-extract' (default) for content analysis, 'assistants' for assistant API"
                },
            },
            "required": ["files"],
            "additionalProperties": False,
        }

    def get_system_prompt(self) -> str:
        return (
            "You are uploading files to Moonshot/Kimi platform running in a Docker container.\n\n"
            "🐳 DOCKER CONTEXT:\n"
            "- This system runs in Docker with files mounted at /mnt/project/\n"
            "- Windows paths (c:\\Project\\...) are NOT accessible\n"
            "- Only Linux container paths work: /mnt/project/EX-AI-MCP-Server/filename.ext\n\n"
            "📁 PATH REQUIREMENTS:\n"
            "✅ VALID: /mnt/project/EX-AI-MCP-Server/large_file.py\n"
            "❌ INVALID: c:\\Project\\EX-AI-MCP-Server\\large_file.py\n"
            "❌ INVALID: ./large_file.py\n"
            "❌ INVALID: large_file.py\n\n"
            "📋 PARAMETERS:\n"
            "- files: Array of Linux container paths (must start with /mnt/project/)\n"
            "- purpose: 'file-extract' (default) or 'assistants'\n\n"
            "🔄 WORKFLOW:\n"
            "1. Upload files with kimi_upload_files → get file_ids\n"
            "2. Use file_ids with kimi_chat_with_files for analysis\n\n"
            "⚠️ TROUBLESHOOTING:\n"
            "- 'All files were skipped' → Check path format (must start with /mnt/project/)\n"
            "- Windows paths → Convert to Linux container paths\n"
            "- File not found → Verify file exists under c:\\Project\\\n\n"
            "📊 LIMITS:\n"
            "- Max file size: 100MB per file\n"
            "- Multiple files supported\n"
            "- Use for large documents, PDFs, codebases\n"
            "- Files are cached by SHA256 - re-uploading same file returns cached ID."
        )

    def get_request_model(self):
        return ToolRequest

    def requires_model(self) -> bool:
        return True  # Changed to True so model resolution happens

    def get_default_model(self) -> str:
        """Override default model to use Kimi instead of GLM"""
        return os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")

    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def format_response(self, response: str, request: ToolRequest, model_info: dict | None = None) -> str:
        return response

    # System user ID for tool uploads
    SYSTEM_USER_ID = "system"

    def _run(self, **kwargs) -> List[Dict[str, Any]]:
        # ⚠️ DEPRECATION WARNING
        logger.warning(
            "⚠️ DEPRECATION WARNING: kimi_upload_files is deprecated. "
            "Use smart_file_query instead for unified file operations. "
            "smart_file_query provides automatic deduplication, provider selection, "
            "and fallback - all in one tool. "
            "Example: smart_file_query(file_path='/mnt/project/file.py', question='Analyze this code')"
        )

        files = kwargs.get("files") or []
        purpose = (kwargs.get("purpose") or "file-extract").strip()
        if not files:
            raise ValueError("No files provided")

        # CRITICAL: Validate path format BEFORE normalization using centralized validation
        from utils.path_validation import validate_upload_path
        # FIX (2025-10-29): Removed local logger redefinition that caused UnboundLocalError
        # Module-level logger is already defined at top of file

        for fp in files:
            is_valid, error_message = validate_upload_path(fp)
            if not is_valid:
                raise ValueError(error_message)

        # Normalize paths (should be no-op now since we validated format)
        path_handler = get_path_handler()
        normalized_files = []

        for fp in files:
            try:
                normalized_path, was_converted, error_message = path_handler.normalize_path(fp)
                if error_message:
                    logger.error(f"Path normalization failed for {fp}: {error_message}")
                    continue
                if was_converted:
                    logger.debug(f"Path converted: {fp} -> {normalized_path}")
                normalized_files.append(normalized_path)
            except Exception as e:
                logger.error(f"Failed to process file path {fp}: {str(e)}")
                continue

        if not normalized_files:
            raise ValueError("No valid files to process after path normalization")

        files = normalized_files

        # Get provider
        prov = ModelProviderRegistry.get_provider_for_model(os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview"))
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        # Configuration
        max_count = int(os.getenv("KIMI_FILES_MAX_COUNT", "0") or 0)
        max_mb_env = os.getenv("KIMI_FILES_MAX_SIZE_MB", "").split('#')[0].strip()
        try:
            max_mb = float(max_mb_env) if max_mb_env else 0.0
        except ValueError:
            logger.warning(f"Invalid KIMI_FILES_MAX_SIZE_MB value: '{max_mb_env}'. Using 0.0 (no limit).")
            max_mb = 0.0
        max_bytes = int(max_mb * 1024 * 1024) if max_mb > 0 else 0
        oversize_behavior = os.getenv("KIMI_FILES_BEHAVIOR_ON_OVERSIZE", "skip").strip().lower()
        upload_timeout = float(os.getenv("KIMI_FILES_UPLOAD_TIMEOUT_SECS", "90"))

        # Apply count cap
        effective_files = list(files)
        if max_count and len(effective_files) > max_count:
            effective_files = effective_files[:max_count]

        results: List[Dict[str, Any]] = []
        skipped: List[str] = []

        # Parallel upload configuration
        parallel_uploads_enabled = os.getenv("KIMI_FILES_PARALLEL_UPLOADS", "true").strip().lower() == "true"
        max_parallel = int(os.getenv("KIMI_FILES_MAX_PARALLEL", "3"))

        def process_single_file(fp):
            """
            Process a single file upload using enhanced utilities.

            PHASE 2 UPDATE (2025-10-30):
            - Uses upload_file_with_provider() for unified upload workflow
            - Deduplication handled by SupabaseUploadManager (SHA256-based)
            - Bidirectional ID mapping via FileIdMapper
            - Backward compatible return format
            """
            try:
                pth = Path(str(fp))

                # Size check (still needed for early validation)
                if max_bytes and pth.exists() and pth.is_file():
                    try:
                        sz = pth.stat().st_size
                    except Exception:
                        sz = -1
                    if sz >= 0 and sz > max_bytes:
                        if oversize_behavior == "fail":
                            raise RuntimeError(f"File exceeds max size: {pth.name} ({(sz + 1048575)//1048576} MB > {int(max_mb)} MB cap)")
                        skipped.append(str(pth))
                        return None

                # Upload using enhanced utilities (handles deduplication internally)
                from tools.supabase_upload import upload_file_with_provider
                from src.storage.supabase_client import get_storage_manager

                storage = get_storage_manager()
                supabase_client = storage.get_client()

                # Upload with provider adapter
                result = upload_file_with_provider(
                    supabase_client=supabase_client,
                    file_path=str(pth),
                    provider="kimi",
                    user_id=self.SYSTEM_USER_ID,
                    filename=pth.name,
                    bucket="user-files",
                    tags=["kimi-upload", purpose]
                )

                # Map adapter response to tool format (backward compatible)
                return {
                    "filename": pth.name,
                    "file_id": result["provider_file_id"],  # Kimi file_id
                    "size_bytes": result["file_size"],
                    "upload_timestamp": result["upload_time"],
                    "deduplicated": result.get("deduplicated", False)
                }

                # NOTE: Supabase upload and deduplication now handled by upload_file_with_provider()
                # No need for separate Supabase upload or FileDeduplicationManager calls

            except Exception as e:
                logger.warning(f"⚠️ File upload failed for {fp}: {e}")
                skipped.append(str(fp))
                return None

        # Process files
        if parallel_uploads_enabled and len(effective_files) > 1:
            import concurrent.futures as _fut
            logger.info(f"Processing {len(effective_files)} files in parallel (max {max_parallel} concurrent)")
            
            with _fut.ThreadPoolExecutor(max_workers=max_parallel) as executor:
                future_to_file = {executor.submit(process_single_file, fp): fp for fp in effective_files}
                for future in _fut.as_completed(future_to_file):
                    result = future.result()
                    if result is not None:
                        results.append(result)
        else:
            for fp in effective_files:
                result = process_single_file(fp)
                if result is not None:
                    results.append(result)

        if not results:
            if skipped:
                raise RuntimeError(f"All files were skipped. Skipped files: {skipped}")
            raise RuntimeError("No files uploaded (unknown reason)")

        return results

    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list[TextContent]:
        import asyncio as _aio
        from tools.shared.error_envelope import make_error_envelope
        try:
            results = await _aio.to_thread(self._run, **arguments)
            return [TextContent(type="text", text=json.dumps(results, ensure_ascii=False))]
        except Exception as e:
            env = make_error_envelope("KIMI", self.get_name(), e)
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]


class KimiChatWithFilesTool(BaseTool):
    """Chat with previously uploaded Kimi files using file IDs"""

    def get_name(self) -> str:
        return "kimi_chat_with_files"

    def get_description(self) -> str:
        return (
            "Chat with previously uploaded Kimi files using their file IDs. "
            "Upload files first with kimi_upload_files, then use the returned file_ids here."
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Question or instruction about the files"
                },
                "file_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Moonshot file IDs from kimi_upload_files"
                },
                "model": {
                    "type": "string",
                    "default": "kimi-k2-0905-preview",
                    "description": "Kimi model to use"
                },
                "temperature": {
                    "type": "number",
                    "default": 0.3,
                    "minimum": 0.0,
                    "maximum": 1.0
                },
            },
            "required": ["prompt", "file_ids"],
            "additionalProperties": False,
        }

    def get_system_prompt(self) -> str:
        return (
            "You are chatting with Kimi about uploaded files.\n"
            "Purpose: Analyze files using their file IDs.\n\n"
            "Parameters:\n"
            "- prompt: Your question or instruction\n"
            "- file_ids: List of file IDs from kimi_upload_files\n"
            "- model: Kimi model (default: kimi-k2-0905-preview)\n"
            "- temperature: Sampling temperature (default: 0.3)\n\n"
            "Output: Kimi's response analyzing the files."
        )

    def get_request_model(self):
        return ToolRequest

    def requires_model(self) -> bool:
        return True  # Changed to True so model resolution happens

    def get_default_model(self) -> str:
        """Override default model to use Kimi instead of GLM"""
        return os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")

    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def format_response(self, response: str, request: ToolRequest, model_info: dict | None = None) -> str:
        return response

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        """Async implementation - uses official Moonshot file pattern"""
        from utils.progress import send_progress

        # ⚠️ DEPRECATION WARNING
        logger.warning(
            "⚠️ DEPRECATION WARNING: kimi_chat_with_files is deprecated. "
            "Use smart_file_query instead for unified file operations. "
            "smart_file_query handles upload + query in one step with automatic deduplication. "
            "Example: smart_file_query(file_path='/mnt/project/file.py', question='Analyze this code')"
        )

        prompt = kwargs.get("prompt") or ""
        file_ids = kwargs.get("file_ids") or []
        model = kwargs.get("model") or os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")
        temperature = float(kwargs.get("temperature") or 0.3)

        if not prompt or not file_ids:
            raise ValueError("Both prompt and file_ids are required")

        # Get provider
        prov = ModelProviderRegistry.get_provider_for_model(model)
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        # Update last_used in Supabase (non-blocking)
        try:
            from src.storage.supabase_client import get_storage_manager
            storage = get_storage_manager()
            if storage and storage.enabled:
                client = storage.get_client()
                for file_id in file_ids:
                    client.table("provider_file_uploads").update({
                        "last_used": datetime.utcnow().isoformat()
                    }).eq("provider_file_id", file_id).execute()
        except Exception:
            pass  # Non-critical

        # PROGRESS FRAME: Notify client we're fetching files
        send_progress(f"Fetching {len(file_ids)} file(s) from Moonshot...")

        # Official Moonshot pattern: retrieve file content and create system messages
        file_messages = []

        def retrieve_content(file_id: str) -> str:
            """Retrieve file content from Moonshot API.

            ENHANCED (2025-10-29): Now handles both text and binary content.
            Returns text content as string for chat completions.
            """
            # The OpenAI SDK's files.content() method returns a response object
            # We need to call it as a method, not access it as a property
            files_api = prov.client.files
            content_method = files_api.content

            # Call the content method with file_id parameter
            response = content_method(file_id=file_id)

            # Handle different response types (text and binary)
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'content'):
                # Binary content - decode if possible, otherwise return as string
                try:
                    return response.content.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    # If binary can't be decoded, return base64 or hex representation
                    logger.warning(f"File {file_id} contains binary data, converting to string")
                    return str(response.content)
            elif isinstance(response, str):
                return response
            elif isinstance(response, bytes):
                try:
                    return response.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"File {file_id} contains binary data, converting to string")
                    return str(response)
            else:
                return str(response)

        for file_id in file_ids:
            try:
                # Retrieve file content using the helper function
                content = await asyncio.to_thread(retrieve_content, file_id)
                file_messages.append({"role": "system", "content": content})
            except Exception as e:
                raise RuntimeError(f"Failed to retrieve content for file {file_id}: {e}")

        # Build messages: file messages first, then user prompt
        messages = [
            *file_messages,
            {"role": "user", "content": prompt}
        ]

        # PROGRESS FRAME: Notify client we're calling Kimi API
        send_progress(f"Analyzing {len(file_ids)} file(s) with Kimi ({model})...")

        # Chat completion with timeout wrapper
        # Use environment variable for timeout (default: 180s for multi-file operations)
        timeout_secs = float(os.getenv("KIMI_MF_CHAT_TIMEOUT_SECS", "180"))
        try:
            resp = await asyncio.wait_for(
                asyncio.to_thread(
                    prov.chat_completions_create,
                    model=model,
                    messages=messages,
                    temperature=temperature
                ),
                timeout=timeout_secs
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Kimi chat analysis timed out after {int(timeout_secs)}s")

        content = (resp or {}).get("content", "")
        return {"model": model, "content": content}

    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list[TextContent]:
        from tools.shared.error_envelope import make_error_envelope
        try:
            result = await self._run_async(**arguments)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        except Exception as e:
            env = make_error_envelope("KIMI", self.get_name(), e)
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]


class KimiManageFilesTool(BaseTool):
    """Manage Kimi files: list, delete, cleanup operations"""

    def get_name(self) -> str:
        return "kimi_manage_files"

    def get_description(self) -> str:
        return (
            "Manage Kimi files with operations: list (show all files), "
            "delete (remove specific file), cleanup_all (delete all files), "
            "cleanup_orphaned (remove files not in Supabase), "
            "cleanup_expired (remove files unused for 30+ days)"
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["list", "delete", "cleanup_all", "cleanup_orphaned", "cleanup_expired"],
                    "description": "Operation to perform"
                },
                "file_id": {
                    "type": "string",
                    "description": "File ID (required for delete operation)"
                },
                "limit": {
                    "type": "integer",
                    "default": 100,
                    "description": "Max files to list (for list operation)"
                },
                "dry_run": {
                    "type": "boolean",
                    "default": False,
                    "description": "Preview changes without executing (for cleanup operations)"
                },
            },
            "required": ["operation"],
            "additionalProperties": False,
        }

    def get_system_prompt(self) -> str:
        return (
            "You are managing Kimi files.\n"
            "Operations:\n"
            "- list: Show all uploaded files\n"
            "- delete: Remove specific file by ID\n"
            "- cleanup_all: Delete ALL files (use with caution!)\n"
            "- cleanup_orphaned: Remove files not tracked in Supabase\n"
            "- cleanup_expired: Remove files unused for 30+ days\n\n"
            "Use dry_run=true to preview cleanup operations before executing."
        )

    def get_request_model(self):
        return ToolRequest

    def requires_model(self) -> bool:
        return True  # Changed to True so model resolution happens

    def get_default_model(self) -> str:
        """Override default model to use Kimi instead of GLM"""
        return os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")

    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def format_response(self, response: str, request: ToolRequest, model_info: dict | None = None) -> str:
        return response

    def _run(self, **kwargs) -> Dict[str, Any]:
        operation = kwargs.get("operation")
        file_id = kwargs.get("file_id")
        limit = kwargs.get("limit", 100)
        dry_run = kwargs.get("dry_run", False)

        # Get provider
        prov = ModelProviderRegistry.get_provider_for_model(os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview"))
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        client = prov.client

        if operation == "list":
            try:
                res = client.files.list(limit=limit)
                data = getattr(res, "data", None) or getattr(res, "files", None) or res
                files = []
                for f in data:
                    files.append({
                        "id": getattr(f, "id", None),
                        "filename": getattr(f, "filename", None),
                        "bytes": getattr(f, "bytes", None),
                        "created_at": getattr(f, "created_at", None),
                        "purpose": getattr(f, "purpose", None),
                    })
                return {"operation": "list", "count": len(files), "files": files}
            except Exception as e:
                raise RuntimeError(f"Failed to list files: {e}")

        elif operation == "delete":
            if not file_id:
                raise ValueError("file_id is required for delete operation")
            try:
                res = client.files.delete(file_id=file_id)
                deleted = getattr(res, "deleted", None)
                if deleted is None and isinstance(res, dict):
                    deleted = res.get("deleted")

                # Remove from Supabase
                try:
                    from src.storage.supabase_client import get_storage_manager
                    storage = get_storage_manager()
                    if storage and storage.enabled:
                        client = storage.get_client()
                        client.table("provider_file_uploads").delete().eq("provider_file_id", file_id).execute()
                except Exception:
                    pass

                return {"operation": "delete", "file_id": file_id, "deleted": bool(deleted)}
            except Exception as e:
                raise RuntimeError(f"Failed to delete file {file_id}: {e}")

        elif operation == "cleanup_all":
            try:
                # List all files
                res = client.files.list(limit=1000)
                data = getattr(res, "data", None) or getattr(res, "files", None) or res

                deleted_count = 0
                failed = []

                for f in data:
                    fid = getattr(f, "id", None)
                    if not fid:
                        continue

                    if dry_run:
                        deleted_count += 1
                    else:
                        try:
                            client.files.delete(file_id=fid)
                            deleted_count += 1
                        except Exception as e:
                            failed.append({"file_id": fid, "error": str(e)})

                # Clear Supabase if not dry run
                if not dry_run:
                    try:
                        from src.storage.supabase_client import get_storage_manager
                        storage = get_storage_manager()
                        if storage and storage.enabled:
                            client = storage.get_client()
                            client.table("provider_file_uploads").delete().eq("provider", "kimi").execute()
                    except Exception:
                        pass

                return {
                    "operation": "cleanup_all",
                    "dry_run": dry_run,
                    "deleted_count": deleted_count,
                    "failed": failed
                }
            except Exception as e:
                raise RuntimeError(f"Failed to cleanup all files: {e}")

        elif operation == "cleanup_orphaned":
            try:
                # Get all Moonshot files
                res = client.files.list(limit=1000)
                data = getattr(res, "data", None) or getattr(res, "files", None) or res
                moonshot_ids = {getattr(f, "id", None) for f in data if getattr(f, "id", None)}

                # Get all Supabase tracked files
                from src.storage.supabase_client import get_storage_manager
                storage = get_storage_manager()
                supabase_ids = set()
                if storage and storage.enabled:
                    client = storage.get_client()
                    result = client.table("provider_file_uploads").select("provider_file_id").eq("provider", "kimi").execute()
                    supabase_ids = {r["provider_file_id"] for r in result.data}

                # Find orphans (in Moonshot but not in Supabase)
                orphaned = moonshot_ids - supabase_ids

                deleted_count = 0
                failed = []

                for fid in orphaned:
                    if dry_run:
                        deleted_count += 1
                    else:
                        try:
                            client.files.delete(file_id=fid)
                            deleted_count += 1
                        except Exception as e:
                            failed.append({"file_id": fid, "error": str(e)})

                return {
                    "operation": "cleanup_orphaned",
                    "dry_run": dry_run,
                    "orphaned_count": len(orphaned),
                    "deleted_count": deleted_count,
                    "failed": failed
                }
            except Exception as e:
                raise RuntimeError(f"Failed to cleanup orphaned files: {e}")

        elif operation == "cleanup_expired":
            try:
                # Get files unused for 30+ days from Supabase
                from src.storage.supabase_client import get_storage_manager
                storage = get_storage_manager()
                if not storage or not storage.enabled:
                    return {"operation": "cleanup_expired", "error": "Supabase not available"}

                supabase_client = storage.get_client()
                cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
                result = supabase_client.table("provider_file_uploads").select("provider_file_id").eq("provider", "kimi").lt("last_used", cutoff).execute()

                expired_ids = [r["provider_file_id"] for r in result.data]

                deleted_count = 0
                failed = []

                for fid in expired_ids:
                    if dry_run:
                        deleted_count += 1
                    else:
                        try:
                            client.files.delete(file_id=fid)
                            supabase_client.table("provider_file_uploads").delete().eq("provider_file_id", fid).execute()
                            deleted_count += 1
                        except Exception as e:
                            failed.append({"file_id": fid, "error": str(e)})

                return {
                    "operation": "cleanup_expired",
                    "dry_run": dry_run,
                    "expired_count": len(expired_ids),
                    "deleted_count": deleted_count,
                    "failed": failed
                }
            except Exception as e:
                raise RuntimeError(f"Failed to cleanup expired files: {e}")

        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list[TextContent]:
        import asyncio as _aio
        from tools.shared.error_envelope import make_error_envelope
        try:
            result = await _aio.to_thread(self._run, **arguments)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        except Exception as e:
            env = make_error_envelope("KIMI", self.get_name(), e)
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]

