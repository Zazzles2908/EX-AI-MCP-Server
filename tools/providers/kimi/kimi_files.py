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

# PHASE A2 CLEANUP (2025-10-30):
# Removed KimiUploadFilesTool class (~282 lines)
# Removed KimiChatWithFilesTool class (~202 lines)
# These tool wrappers are redundant - smart_file_query now uses:
# - upload_file_with_provider() from tools/supabase_upload.py for uploads
# - ModelProviderRegistry.get_provider_for_model() for chat operations
# This eliminates triple wrapping: smart_file_query → tool wrappers → Supabase hub → providers
# New architecture: smart_file_query → Supabase hub → providers (direct)

# Only KimiManageFilesTool remains (file management operations)

# [DELETED: KimiUploadFilesTool methods - lines 60-253]
# [DELETED: KimiChatWithFilesTool class definition starts at line 255]

# [DELETED: KimiUploadFilesTool class - ~282 lines total]
# [DELETED: Remaining methods and execute() - lines 63-99]

# [DELETED: KimiChatWithFilesTool class - ~202 lines]
# This class is redundant - smart_file_query now uses ModelProviderRegistry directly

# [DELETED: Rest of KimiChatWithFilesTool._run_async() and execute() methods]
# Total deletion: ~202 lines for KimiChatWithFilesTool class

# [DELETED: Complete KimiChatWithFilesTool class - ~202 lines total]
# Deletion complete!

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

