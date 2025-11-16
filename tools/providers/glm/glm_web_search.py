from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.types import TextContent

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest


class GLMWebSearchTool(BaseTool):
    name = "glm_web_search"
    description = (
        "Perform a native GLM web search via Z.ai /api/paas/v4/web_search. "
        "Returns raw JSON results from the provider."
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
                "search_query": {"type": "string", "description": "Search query (required)"},
                "count": {"type": "integer", "default": 10},
                "search_engine": {"type": "string", "default": "search-prime"},
                "search_domain_filter": {"type": ["string", "null"]},
                "search_recency_filter": {
                    "type": "string",
                    "enum": ["oneDay", "oneWeek", "oneMonth", "oneYear", "all"],
                    "default": "all",
                },
                "request_id": {"type": ["string", "null"]},
                "user_id": {"type": ["string", "null"]},
            },
            "required": ["search_query"],
            "additionalProperties": False,
        }

    def get_request_model(self):
        return ToolRequest

    def prepare_prompt(self, request: ToolRequest) -> str:
        # No LLM-facing prompt
        return ""

    def get_system_prompt(self) -> str:
        return (
            "You are a direct wrapper around Z.ai GLM native web search.\n"
            "Call POST {GLM_API_URL}/web_search with Bearer auth and relay results as JSON.\n\n"
            "Parameters:\n- search_query (required)\n- count (default 10)\n"
            "- search_engine (default 'search-prime')\n- search_domain_filter (optional)\n- search_recency_filter (oneDay|oneWeek|oneMonth|oneYear|all)\n"
            "- request_id, user_id (optional)\n\nSafety:\n- Respect rate limits.\n"
        )

    def _get_base_url(self) -> str:
        # Prefer GLM_API_URL, fallback to ZAI_BASE_URL, default official base
        return (
            os.getenv("GLM_API_URL")
            or os.getenv("ZAI_BASE_URL")
            or "https://api.z.ai/api/paas/v4"
        ).rstrip("/")

    def _get_api_key(self) -> str:
        key = os.getenv("GLM_API_KEY") or os.getenv("ZAI_API_KEY")
        if not key:
            raise RuntimeError("GLM_API_KEY (or ZAI_API_KEY) is not configured")
        return key.strip()

    def run(self, **kwargs) -> Dict[str, Any]:
        query = (kwargs.get("search_query") or "").strip()
        if not query:
            raise ValueError("search_query is required")
        # Validate and clamp count to API-supported range [1, 50]
        count = int(kwargs.get("count", 10))
        if count < 1:
            count = 1
        if count > 50:
            count = 50

        payload = {
            "search_query": query,
            "count": count,
            "search_engine": (kwargs.get("search_engine") or "search-prime"),
            "search_recency_filter": (kwargs.get("search_recency_filter") or "all"),
        }
        if kwargs.get("search_domain_filter"):
            payload["search_domain_filter"] = kwargs["search_domain_filter"]
        if kwargs.get("request_id"):
            payload["request_id"] = kwargs["request_id"]
        if kwargs.get("user_id"):
            payload["user_id"] = kwargs["user_id"]

        base = self._get_base_url()
        url = f"{base}/web_search"
        api_key = self._get_api_key()

        data = json.dumps(payload).encode("utf-8")
        accept_lang = os.getenv("GLM_ACCEPT_LANGUAGE", "en-US,en")
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": accept_lang,
        })
        timeout_s = float(os.getenv("GLM_WEBSEARCH_TIMEOUT_SECS", "30"))
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                try:
                    return json.loads(raw)
                except Exception:
                    # If provider returns non-JSON, wrap as text
                    return {"raw_text": raw}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
            raise RuntimeError(f"GLM web_search HTTP {e.code}: {body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"GLM web_search network error: {e}")

    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list[TextContent]:
        import asyncio as _aio
        from mcp.types import TextContent
        result = await _aio.to_thread(self.run, **arguments)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

