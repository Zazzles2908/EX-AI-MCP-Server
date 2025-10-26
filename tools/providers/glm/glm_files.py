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
# SUPABASE GATEWAY FUNCTIONS (Phase 3 - 2025-10-26)
# ============================================================================

async def upload_via_supabase_gateway_glm(file_path: str, storage, purpose: str = "agent") -> dict:
    """
    Upload file to Supabase first, then upload to GLM using SDK.

    UPDATED APPROACH (EXAI-validated):
    GLM does NOT support URL-based file extraction. Instead:
    1. Upload file to Supabase Storage
    2. Upload file to GLM using SDK (client.files.create or HTTP fallback)
    3. Track both IDs in database

    This provides:
    - Supabase as centralized storage
    - GLM file_id for AI operations
    - Bidirectional tracking
    - SDK handles large files with chunked uploads and retries

    Args:
        file_path: Path to file (absolute or relative)
        storage: Supabase storage manager instance
        purpose: File purpose ('agent' for GLM)

    Returns:
        dict with:
        - glm_file_id: File ID from GLM
        - supabase_file_id: File ID from Supabase
        - filename: Original filename
        - size_bytes: File size
        - upload_method: 'supabase_gateway'

    Raises:
        RuntimeError: If upload fails
        ValueError: If file doesn't exist or is too large

    Source: EXAI Consultation c90cdeec-48bb-4d10-b075-925ebbf39c8a
    Note: Uses SDK instead of raw HTTP for reliability and large file support
    """
    import mimetypes
    from pathlib import Path
    from utils.file.cache import FileCache

    pth = Path(file_path)

    # Validate file exists
    if not pth.exists() or not pth.is_file():
        raise ValueError(f"File not found: {file_path}")

    # Check file size (GLM limit: 20MB)
    file_size = pth.stat().st_size
    max_size = 20 * 1024 * 1024  # 20MB
    if file_size > max_size:
        raise ValueError(f"File too large: {file_size} bytes (max 20MB for GLM)")

    logger.info(f"Starting Supabase gateway upload for {pth.name} ({file_size} bytes)")

    # 1. Upload to Supabase Storage
    try:
        with open(pth, 'rb') as f:
            file_data = f.read()

        mime_type, _ = mimetypes.guess_type(str(pth))

        supabase_file_id = storage.upload_file(
            file_path=f"glm-gateway/{pth.name}",
            file_data=file_data,
            original_name=pth.name,
            mime_type=mime_type,
            file_type="user_upload"
        )

        if not supabase_file_id:
            raise RuntimeError("Supabase upload returned None")

        logger.info(f"✅ Uploaded to Supabase: {pth.name} -> {supabase_file_id}")

    except Exception as e:
        logger.error(f"❌ Supabase upload failed: {e}")
        raise RuntimeError(f"Failed to upload to Supabase: {e}")



    # 3. Upload to GLM using SDK (EXAI-recommended approach)
    # Note: GLM SDK handles large files better than raw HTTP
    # Provides chunked uploads, retry logic, and connection pooling
    try:
        from src.providers.registry import ModelProviderRegistry
        from src.providers.glm import GLMModelProvider

        api_key = os.getenv("GLM_API_KEY")
        if not api_key:
            raise RuntimeError("GLM_API_KEY not configured")

        default_model = os.getenv("GLM_DEFAULT_MODEL", "glm-4.6")
        prov = ModelProviderRegistry.get_provider_for_model(default_model)

        if not isinstance(prov, GLMModelProvider):
            # Fallback: create provider directly
            base_url = os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4")
            prov = GLMModelProvider(api_key=api_key, base_url=base_url)

        # Upload using SDK (uses client.files.create or HTTP fallback internally)
        # This handles large files much better than raw HTTP (chunked uploads, retries)
        glm_file_id = prov.upload_file(str(pth), purpose=purpose)

        if not glm_file_id:
            raise RuntimeError("GLM upload returned None")

        logger.info(f"✅ Uploaded to GLM via SDK: {glm_file_id}")

    except Exception as e:
        logger.error(f"❌ GLM SDK upload failed: {e}")
        raise RuntimeError(f"Failed to upload to GLM via SDK: {e}")

    # 5. Track both IDs in database
    try:
        client = storage.get_client()
        client.table("provider_file_uploads").insert({
            "provider": "glm",
            "provider_file_id": glm_file_id,
            "supabase_file_id": supabase_file_id,
            "sha256": FileCache.sha256_file(pth),
            "filename": pth.name,
            "file_size_bytes": file_size,
            "upload_status": "completed",
            "upload_method": "supabase_gateway_presigned"
        }).execute()

        logger.info(f"✅ Tracked in database: glm={glm_file_id}, supabase={supabase_file_id}")

    except Exception as e:
        logger.warning(f"⚠️  Failed to track in database: {e}")
        # Don't fail - upload was successful

    return {
        "glm_file_id": glm_file_id,
        "supabase_file_id": supabase_file_id,
        "filename": pth.name,
        "size_bytes": file_size,
        "upload_method": "supabase_gateway_presigned"
    }


class GLMUploadFileTool(BaseTool):
    name = "glm_upload_file"
    description = (
        "Upload a file to ZhipuAI GLM Files API (purpose=agent by default) and return its file id."
    )

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
                "file": {"type": "string", "description": "Path to file (abs or relative)"},
                "purpose": {"type": "string", "enum": ["agent"], "default": "agent"},
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
        file_path = kwargs.get("file")
        purpose = (kwargs.get("purpose") or "agent").strip()
        if not file_path:
            raise ValueError("file is required")

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
            # DEDUPLICATION CHECK (Phase 2.4 - 2025-10-26)
            from pathlib import Path as _P
            from utils.file.cache import FileCache

            dedup_enabled = os.getenv("FILE_DEDUPLICATION_ENABLED", "true").strip().lower() == "true"
            file_id = None

            if dedup_enabled:
                try:
                    from src.storage.supabase_client import get_storage_manager
                    storage = get_storage_manager()
                    dedup_manager = FileDeduplicationManager(storage)

                    existing = dedup_manager.check_duplicate(p, "glm")
                    if existing:
                        # File already exists - reuse it
                        file_id = existing['provider_file_id']

                        # Increment reference count
                        dedup_manager.increment_reference(file_id, "glm")

                        logger.info(f"♻️  Reusing existing file: {p.name} -> {file_id} (ref_count incremented)")

                        try:
                            from utils.observability import record_cache_hit
                            record_cache_hit("GLM", existing['sha256'])
                        except Exception:
                            pass

                        return {"file_id": file_id, "filename": p.name, "deduplicated": True}
                except Exception as e:
                    logger.warning(f"Deduplication check failed, proceeding with upload: {e}")

            # Upload if not deduplicated
            if not file_id:
                file_id = prov.upload_file(str(p), purpose=purpose)

                # Register new file with deduplication manager
                if dedup_enabled:
                    try:
                        from src.storage.supabase_client import get_storage_manager
                        storage = get_storage_manager()
                        dedup_manager = FileDeduplicationManager(storage)
                        dedup_manager.register_new_file(
                            provider_file_id=file_id,
                            supabase_file_id=None,
                            file_path=p,
                            provider="glm",
                            upload_method="direct"
                        )
                    except Exception as reg_err:
                        logger.warning(f"Failed to register with deduplication manager: {reg_err}")

                # Observability: record file count +1
                try:
                    from utils.observability import record_file_count
                    record_file_count("GLM", +1)
                except Exception:
                    pass

            return {"file_id": file_id, "filename": p.name}
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

