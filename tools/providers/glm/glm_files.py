from __future__ import annotations

import os
from typing import Any, Dict
from pathlib import Path
import logging



import json
from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest
from src.providers.glm import GLMModelProvider

from src.providers.registry import ModelProviderRegistry
from utils.file.deduplication import FileDeduplicationManager

logger = logging.getLogger(__name__)


# ============================================================================
# PHASE 5 CLEANUP (2025-10-30)
# ============================================================================
# Removed upload_via_supabase_gateway_glm() function (~144 lines)
# This function is now redundant - replaced by upload_file_with_provider() in tools/supabase_upload.py
# The new implementation provides:
# - Better error handling
# - Retry logic
# - Bidirectional ID mapping via FileIdMapper
# - Session tracking with 24h expiry
# - Consistent interface with Kimi

class GLMUploadFileTool(BaseTool):
    name = "glm_upload_file"
    description = (
        "Upload single file to GLM platform (20MB limit). "
        "\n\n🎯 USE CASES: Quick code analysis, single small files (<20MB), immediate processing"
        "\n📁 PATH REQUIREMENTS: Linux container paths ONLY - Format: /mnt/project/EX-AI-MCP-Server/filename.ext"
        "\n⚡ ALTERNATIVE: Use kimi_upload_files for larger files, multiple files, documents"
    )

    # System user ID for tool uploads
    SYSTEM_USER_ID = "system"

    # BaseTool required interface
    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "pattern": "^/mnt/project/.*",
                    "description": (
                        "Linux container path ONLY. Format: /mnt/project/EX-AI-MCP-Server/filename.ext\n"
                        "❌ Windows paths (c:\\Project\\...) will be REJECTED\n"
                        "❌ Relative paths (./file.txt) will be REJECTED\n"
                        "✅ Only files under c:\\Project\\ are accessible at /mnt/project/ in the container"
                    )
                },
                "purpose": {
                    "type": "string",
                    "enum": ["agent"],
                    "default": "agent",
                    "description": "File purpose: 'agent' (default) for GLM agent API"
                },
            },
            "required": ["file"],
            "additionalProperties": False,
        }

    def get_request_model(self):
        return ToolRequest

    def prepare_prompt(self, request: ToolRequest) -> str:
        # No unified prompt; this tool performs provider upload directly
        return ""

    def get_system_prompt(self) -> str:
        return (
            "You handle GLM file upload to support downstream agent or chat tasks.\n"
            "Parameters:\n- file: Path to a single file (abs or relative).\n- purpose: 'agent' (default).\n\n"
            "Behavior:\n- POST {GLM_API_URL}/files with Bearer auth; returns an id.\n- This tool does not retrieve file content (API does not expose it).\n\n"
            "Safety:\n- Respect provider limits (~100MB/file). Treat returned file_id as opaque; do not rely on its format.\n- Avoid uploading sensitive content unnecessarily.\n\n"
            "Output: Raw JSON fields commonly include {file_id, filename, bytes?}; content retrieval is not supported by this tool."
        )


    def get_descriptor(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_input_schema(),
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        # ⚠️ DEPRECATION WARNING
        logger.warning(
            "⚠️ DEPRECATION WARNING: glm_upload_file is deprecated. "
            "Use smart_file_query instead for unified file operations. "
            "smart_file_query provides automatic deduplication, provider selection, "
            "and fallback - all in one tool. "
            "Example: smart_file_query(file_path='/mnt/project/file.py', question='Analyze this code')"
        )

        file_path = kwargs.get("file")
        purpose = (kwargs.get("purpose") or "agent").strip()
        if not file_path:
            raise ValueError("file is required")

        # CRITICAL: Validate path format BEFORE processing using centralized validation
        from utils.path_validation import validate_upload_path

        is_valid, error_message = validate_upload_path(file_path)
        if not is_valid:
            raise ValueError(error_message)

        # Resolve provider and use provider-level upload implementation
        prov = ModelProviderRegistry.get_provider_for_model(os.getenv("GLM_QUALITY_MODEL", "glm-4.5"))
        if not isinstance(prov, GLMModelProvider):
            api_key = os.getenv("GLM_API_KEY", "")
            if not api_key:
                raise RuntimeError("GLM_API_KEY is not configured")
            prov = GLMModelProvider(api_key=api_key)

        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # PHASE 3 UPDATE (2025-10-30):
            # Use upload_file_with_provider() for unified upload workflow
            # Deduplication handled by SupabaseUploadManager (SHA256-based)
            # Bidirectional ID mapping via FileIdMapper

            from tools.supabase_upload import upload_file_with_provider
            from src.storage.supabase_client import get_storage_manager

            storage = get_storage_manager()
            supabase_client = storage.get_client()

            # Upload with provider adapter
            result = upload_file_with_provider(
                supabase_client=supabase_client,
                file_path=str(p),
                provider="glm",
                user_id=self.SYSTEM_USER_ID,
                filename=p.name,
                bucket="user-files",
                tags=["glm-upload", purpose]
            )

            # Observability: record file count +1 (only if not deduplicated)
            if not result.get("deduplicated", False):
                try:
                    from utils.observability import record_file_count
                    record_file_count("GLM", +1)
                except Exception:
                    pass
            else:
                # Record cache hit for deduplicated files
                try:
                    from utils.observability import record_cache_hit
                    record_cache_hit("GLM", "sha256")
                except Exception:
                    pass

            # Map adapter response to tool format (backward compatible)
            return {
                "file_id": result["provider_file_id"],
                "filename": p.name,
                "deduplicated": result.get("deduplicated", False)
            }
        except Exception as e:
            try:
                from utils.observability import record_error
                record_error("GLM", os.getenv("GLM_QUALITY_MODEL", "glm-4.5"), "upload_error", str(e))
            except Exception:
                pass
            raise

    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list["TextContent"]:
        import asyncio as _aio
        from mcp.types import TextContent
        result = await _aio.to_thread(self.run, **arguments)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

class GLMMultiFileChatTool(BaseTool):
    name = "glm_multi_file_chat"
    description = (
        "Upload multiple files to GLM (purpose=agent), then call chat/completions with those files summarized as system content."
    )

    def get_name(self) -> str:
        """Return the tool name."""
        return self.name

    def get_description(self) -> str:
        """Return the tool description."""
        return self.description

    def get_input_schema(self) -> Dict[str, Any]:
        """Return the input schema for this tool."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "files": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to upload and analyze"},
                "prompt": {"type": "string", "description": "Question or instruction about the files"},
                "model": {"type": "string", "default": os.getenv("GLM_QUALITY_MODEL", "glm-4.5"), "description": "GLM model to use"},
                "temperature": {"type": "number", "default": 0.3, "description": "Response creativity (0-1)"},
            },
            "required": ["files", "prompt"],
            "additionalProperties": False,
        }

    def get_system_prompt(self) -> str:
        return (
            "You orchestrate GLM multi-file chat.\n"
            "Purpose: Upload files (purpose 'agent'), include a system preamble enumerating uploaded files, then ask user's prompt.\n\n"
            "Parameters: files, prompt, model, temperature.\n"
            "Notes:\n- GLM upload returns ids; content retrieval is not available here.\n- Include filenames as context to guide the model, but do not expose ids in final answer.\n"
            "Output: Concise answer informed by listed files and user prompt."
        )

    def get_descriptor(self) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "input_schema": self.get_input_schema(),
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        # ⚠️ DEPRECATION WARNING
        logger.warning(
            "⚠️ DEPRECATION WARNING: glm_multi_file_chat is deprecated. "
            "Use smart_file_query instead for unified file operations. "
            "smart_file_query handles upload + query in one step with automatic deduplication. "
            "Example: smart_file_query(file_path='/mnt/project/file.py', question='Analyze this code')"
        )

        files = kwargs.get("files") or []
        prompt = kwargs.get("prompt") or ""
        model = kwargs.get("model") or os.getenv("GLM_QUALITY_MODEL", "glm-4.5")
        temperature = float(kwargs.get("temperature") or 0.3)
        if not files or not prompt:
            raise ValueError("files and prompt are required")

        # Upload files to GLM (purpose=agent); GLM docs do not expose a direct retrieve content API akin to Kimi's file-extract
        uploaded = []
        for fp in files:
            up = GLMUploadFileTool().run(file=fp, purpose="agent")
            uploaded.append(up)

        # For parity with Kimi chat flow, we will include placeholders listing filenames.
        # If/when GLM exposes content retrieval for uploaded files, we can fetch and include their text like Kimi.
        sys_msg = "\n".join([f"[GLM Uploaded] {u['filename']} (id={u['file_id']})" for u in uploaded])

        # Resolve provider from registry; fallback to direct client if missing
        prov = ModelProviderRegistry.get_provider_for_model(model)
        if not isinstance(prov, GLMModelProvider):
            api_key = os.getenv("GLM_API_KEY", "")
            if not api_key:
                raise RuntimeError("GLM_API_KEY is not configured")
            prov = GLMModelProvider(api_key=api_key)

        # Call provider using normalized API with a hard timeout to avoid hangs
        import concurrent.futures as _fut
        def _call():
            return prov.generate_content(prompt=prompt, model_name=model, system_prompt=sys_msg, temperature=temperature)
        timeout_s = float(os.getenv("GLM_MF_CHAT_TIMEOUT_SECS", "60"))
        try:
            with _fut.ThreadPoolExecutor(max_workers=1) as _pool:
                _future = _pool.submit(_call)
                mr = _future.result(timeout=timeout_s)
        except _fut.TimeoutError:
            raise TimeoutError(f"GLM multi-file chat timed out after {int(timeout_s)}s")
        return {"model": model, "content": mr.content, "uploaded": uploaded}


    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list["TextContent"]:
        import asyncio as _aio
        from mcp.types import TextContent
        from tools.shared.error_envelope import make_error_envelope
        try:
            try:
                timeout_s = float(os.getenv("GLM_MF_CHAT_TIMEOUT_SECS", "60"))
            except Exception:
                timeout_s = 60.0
            result = await _aio.wait_for(_aio.to_thread(self.run, **arguments), timeout=timeout_s)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        except _aio.TimeoutError:
            env = make_error_envelope("GLM", self.name, "glm_multi_file_chat exceeded execute cap", detail=f"{int(timeout_s)}s")
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]
        except Exception as e:
            env = make_error_envelope("GLM", self.name, e)
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]

