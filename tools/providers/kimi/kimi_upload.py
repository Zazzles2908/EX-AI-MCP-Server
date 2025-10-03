from __future__ import annotations

import json
import os
import asyncio
from typing import Any, Dict, List
from pathlib import Path

from mcp.types import TextContent

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest
from src.providers.kimi import KimiModelProvider
from src.providers.registry import ModelProviderRegistry


class KimiUploadAndExtractTool(BaseTool):
    def get_name(self) -> str:
        return "kimi_upload_and_extract"

    def get_description(self) -> str:
        return (
            "Upload one or more files to Moonshot (Kimi) using the Files API, extract parsed text, "
            "and return messages you can inject into chat/completions (system-role)."
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths (absolute or relative to project root)",
                },
                "purpose": {
                    "type": "string",
                    "enum": ["file-extract", "assistants"],
                    "default": "file-extract",
                },
            },
            "required": ["files"],
            "additionalProperties": False,
        }

    def get_system_prompt(self) -> str:
        return (
            "You are a precise EX-AI MCP file-ingestion assistant for Moonshot (Kimi).\n"
            "Purpose: Upload one or more local files to Kimi Files API and return parsed text as system messages.\n\n"
            "Parameters:\n- files: list of file paths (absolute preferred; relative allowed).\n- purpose: 'file-extract' (default) or 'assistants'.\n\n"
            "Constraints & Safety:\n- Prefer FULL ABSOLUTE paths to avoid ambiguity.\n- Respect provider limits (e.g., ~100MB/file). If KIMI_FILES_MAX_SIZE_MB is set, skip larger files locally; provider still enforces hard limits.\n- Do not include secrets or private data unnecessarily.\n\n"
            "Output:\n- Return JSON array of messages preserving original file order: {role:'system', content:'<extracted text>', _file_id:'<id>'}.\n- Keep content as-is; do not summarize or transform.\n- The caller may prepend these messages to chat with a concise user prompt."
        )

    def get_request_model(self):
        return ToolRequest

    def requires_model(self) -> bool:
        return False

    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def format_response(self, response: str, request: ToolRequest, model_info: dict | None = None) -> str:
        return response

    def _run(self, **kwargs) -> List[Dict[str, Any]]:
        files = kwargs.get("files") or []
        purpose = (kwargs.get("purpose") or "file-extract").strip()
        if not files:
            raise ValueError("No files provided")

        # Resolve provider
        prov = ModelProviderRegistry.get_provider_for_model(os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview"))
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        # Limits
        from pathlib import Path as _P
        max_count = int(os.getenv("KIMI_FILES_MAX_COUNT", "0") or 0)  # 0=no cap
        max_mb_env = os.getenv("KIMI_FILES_MAX_SIZE_MB", "").strip()
        max_mb = float(max_mb_env) if max_mb_env else 0.0
        max_bytes = int(max_mb * 1024 * 1024) if max_mb > 0 else 0
        oversize_behavior = os.getenv("KIMI_FILES_BEHAVIOR_ON_OVERSIZE", "skip").strip().lower()  # skip|fail
        upload_timeout = float(os.getenv("KIMI_FILES_UPLOAD_TIMEOUT_SECS", "90"))
        fetch_timeout = float(os.getenv("KIMI_FILES_FETCH_TIMEOUT_SECS", "25"))

        # Apply count cap if set
        effective_files = list(files)
        if max_count and len(effective_files) > max_count:
            effective_files = effective_files[:max_count]

        messages: List[Dict[str, Any]] = []
        from utils.tool_events import ToolCallEvent, ToolEventSink
        sink = ToolEventSink()
        from utils.file_cache import FileCache
        import concurrent.futures as _fut

        skipped: List[str] = []

        for idx, fp in enumerate(effective_files, start=1):
            evt = ToolCallEvent(provider=prov.get_provider_type().value, tool_name="file_upload_extract", args={"path": str(fp), "purpose": purpose})
            try:
                pth = _P(str(fp))
                # Size gate if configured
                if max_bytes and pth.exists() and pth.is_file():
                    try:
                        sz = pth.stat().st_size
                    except Exception:
                        sz = -1
                    if sz >= 0 and sz > max_bytes:
                        if oversize_behavior == "fail":
                            raise RuntimeError(f"File exceeds max size: {pth.name} ({(sz + 1048575)//1048576} MB > {int(max_mb)} MB cap)")
                        skipped.append(str(pth))
                        evt.end(ok=False, error=f"skipped: oversize ({(sz + 1048575)//1048576} MB > {int(max_mb)} MB cap)")
                        try:
                            sink.record(evt)
                        except Exception:
                            pass
                        continue

                # FileCache: reuse existing file_id if enabled and present
                cache_enabled = os.getenv("FILECACHE_ENABLED", "true").strip().lower() == "true"
                file_id = None
                prov_name = prov.get_provider_type().value
                if cache_enabled:
                    try:
                        sha = FileCache.sha256_file(pth)
                        fc = FileCache()
                        cached = fc.get(sha, prov_name)
                        if cached:
                            # cache hit
                            try:
                                from utils.observability import record_cache_hit
                                record_cache_hit(prov_name, sha)
                            except Exception:
                                pass
                            file_id = cached
                        else:
                            try:
                                from utils.observability import record_cache_miss
                                record_cache_miss(prov_name, sha)
                            except Exception:
                                pass
                    except Exception:
                        file_id = None

                # Upload with timeout when not cached
                if not file_id:
                    def _upload():
                        return prov.upload_file(str(pth), purpose=purpose)
                    try:
                        with _fut.ThreadPoolExecutor(max_workers=1) as _pool:
                            _future = _pool.submit(_upload)
                            file_id = _future.result(timeout=upload_timeout)
                    except _fut.TimeoutError:
                        raise TimeoutError(f"Kimi files.upload() timed out after {int(upload_timeout)}s for path={pth}")
                    except Exception as upload_err:
                        # Handle upload failures gracefully (e.g., Moonshot "text extract error")
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"⚠️ File upload failed for {pth.name}: {upload_err}")
                        logger.warning(f"   Skipping file and continuing with batch...")
                        skipped.append(str(pth))
                        evt.end(ok=False, error=f"upload failed: {upload_err}")
                        try:
                            sink.record(evt)
                        except Exception:
                            pass
                        continue

                    # on new upload, cache it
                    try:
                        if cache_enabled:
                            sha = FileCache.sha256_file(pth)
                            fc = FileCache()
                            fc.set(sha, prov_name, file_id)
                    except Exception:
                        pass
                    # Observability: record file count +1 for fresh upload
                    try:
                        from utils.observability import record_file_count  # lazy import
                        record_file_count(prov_name, +1)
                    except Exception:
                        pass

                # Retrieve parsed content with retry/backoff (provider may throttle on multiple files)
                def _fetch():
                    attempts = int(os.getenv("KIMI_FILES_FETCH_RETRIES", "3"))
                    backoff = float(os.getenv("KIMI_FILES_FETCH_BACKOFF", "0.8"))
                    delay = float(os.getenv("KIMI_FILES_FETCH_INITIAL_DELAY", "0.5"))
                    last_err = None
                    for _ in range(attempts):
                        try:
                            return prov.client.files.content(file_id=file_id).text
                        except Exception as e:
                            last_err = e
                            # backoff before retry
                            try:
                                import time as _t
                                _t.sleep(delay)
                            except Exception:
                                pass
                            delay *= (1.0 + backoff)
                    if last_err:
                        raise last_err
                    raise RuntimeError("Failed to fetch file content (unknown error)")

                try:
                    with _fut.ThreadPoolExecutor(max_workers=1) as _pool:
                        _future = _pool.submit(_fetch)
                        content = _future.result(timeout=fetch_timeout)
                except _fut.TimeoutError:
                    raise TimeoutError(f"Kimi files.content() timed out after {int(fetch_timeout)}s for file_id={file_id}")

                messages.append({"role": "system", "content": content, "_file_id": file_id})
                evt.end(ok=True)
            except Exception as e:
                evt.end(ok=False, error=str(e))
                # Observability: record provider error
                try:
                    from utils.observability import record_error
                    record_error(prov.get_provider_type().value, getattr(prov, 'FRIENDLY_NAME', 'Kimi'), 'upload_error', str(e))
                except Exception:
                    pass
                raise
            finally:
                try:
                    sink.record(evt)
                except Exception:
                    pass

        # If we skipped everything, fail clearly
        if not messages:
            if skipped:
                raise RuntimeError(f"All files skipped by size gate (>{int(max_mb)} MB): {skipped}")
            raise RuntimeError("No messages produced (unknown reason)")

        return messages

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        # Offload blocking provider/file I/O to a background thread to avoid blocking event loop
        import asyncio as _aio
        from tools.shared.error_envelope import make_error_envelope
        try:
            msgs = await _aio.to_thread(self._run, **arguments)
            return [TextContent(type="text", text=json.dumps(msgs, ensure_ascii=False))]
        except Exception as e:
            env = make_error_envelope("KIMI", self.get_name(), e)
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]



class KimiMultiFileChatTool(BaseTool):
    name = "kimi_multi_file_chat"
    description = (
        "Upload multiple files to Kimi, extract content, prepend as system messages, then call chat/completions."
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
                "files": {"type": "array", "items": {"type": "string"}},
                "prompt": {"type": "string"},
                "model": {"type": "string", "default": os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")},
                "temperature": {"type": "number", "default": 0.3},
            },
            "required": ["files", "prompt"],
            "additionalProperties": False,
        }

    def get_request_model(self):
        return ToolRequest

    def prepare_prompt(self, request: ToolRequest) -> str:
        # This tool performs provider calls directly; no unified prompt needed
        return ""

    def get_system_prompt(self) -> str:
        return (
            "You orchestrate Kimi multi-file chat.\n"
            "Purpose: Upload N files, extract their text, prepend each as a system message, then ask the user prompt.\n\n"
            "Parameters:\n"
            "- files: List of paths (absolute or relative under project root).\n"
            "- model: Kimi model id (defaults via KIMI_DEFAULT_MODEL).\n"
            "- temperature: Sampling temperature.\n\n"
            "Notes:\n"
            "- Extraction uses Kimi Files API (purpose 'file-extract'); content is added verbatim as system-role context messages.\n"
            "- Do not echo large file content verbatim in the final answer; provide concise, synthesized results.\n"
            "- Provider limits apply (e.g., ~100MB/file).\n"
            "Output: A concise answer to the user prompt informed by the provided files."
        )

    def get_descriptor(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_input_schema(),
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        files = kwargs.get("files") or []
        prompt = kwargs.get("prompt") or ""
        model = kwargs.get("model") or os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")
        temperature = float(kwargs.get("temperature") or 0.3)
        cache_id = kwargs.get("cache_id")
        reset_cache_ttl = kwargs.get("reset_cache_ttl", False)

        if not files or not prompt:
            raise ValueError("files and prompt are required")

        # Upload & extract (call provider tool's internal synchronous _run)
        upload_tool = KimiUploadAndExtractTool()
        sys_msgs = upload_tool._run(files=files)

        # Prepare messages
        messages = [*sys_msgs, {"role": "user", "content": prompt}]

        prov = ModelProviderRegistry.get_provider_for_model(os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview"))
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        # Use OpenAI-compatible client to create completion with a hard timeout
        import concurrent.futures as _fut
        def _call():
            # Use Kimi provider wrapper to inject idempotency + context-cache headers
            return prov.chat_completions_create(
                model=model,
                messages=messages,
                temperature=temperature,
                cache_id=cache_id,
                reset_cache_ttl=reset_cache_ttl
            )
        timeout_s = float(os.getenv("KIMI_MF_CHAT_TIMEOUT_SECS", "180"))
        try:
            with _fut.ThreadPoolExecutor(max_workers=1) as _pool:
                _future = _pool.submit(_call)
                resp = _future.result(timeout=timeout_s)
        except _fut.TimeoutError:
            raise TimeoutError(f"Kimi multi-file chat timed out after {int(timeout_s)}s")
        content = (resp or {}).get("content", "")
        return {"model": model, "content": content}

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        import asyncio as _aio
        try:
            # Hard-cap total execution time to ensure progress and enable fallback
            try:
                timeout_s = float(os.getenv("KIMI_MF_CHAT_TIMEOUT_SECS", "60"))
            except Exception:
                timeout_s = 60.0
            result = await _aio.wait_for(_aio.to_thread(self.run, **arguments), timeout=timeout_s)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        except _aio.TimeoutError:
            err = {
                "status": "execution_error",
                "error": f"kimi_multi_file_chat exceeded {int(timeout_s)}s (execute cap)",
                "error_class": "timeouterror",
                "provider": "KIMI",
                "tool": self.get_name(),
            }
            return [TextContent(type="text", text=json.dumps(err, ensure_ascii=False))]
        except Exception as e:
            # Emit a structured error envelope so the dispatcher can show the real error and trigger fallback
            err = {
                "status": "execution_error",
                "error": str(e),
                "error_class": type(e).__name__.lower(),
                "provider": "KIMI",
                "tool": self.get_name(),
            }
            return [TextContent(type="text", text=json.dumps(err, ensure_ascii=False))]
