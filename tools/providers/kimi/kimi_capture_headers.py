from __future__ import annotations

import json
from src.providers.registry_core import get_registry_instance
import os
from src.providers.registry_core import get_registry_instance
from typing import Any, Dict

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest

class KimiCaptureHeadersTool(BaseTool):
    name = "kimi_capture_headers"
    description = (
        "Perform a non-stream Kimi chat call (with idempotency/cache headers) and return normalized output "
        "including metadata.cache {attached,saved}. Skips when KIMI_API_KEY is not set."
    )

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "messages": {"type": "array", "items": {"type": "object"}},
                "model": {"type": "string", "default": "kimi-k2-0711-preview"},
                "temperature": {"type": "number", "default": 0.6},
                "session_id": {"type": ["string", "null"]},
                "call_key": {"type": ["string", "null"]},
                "tool_name": {"type": "string", "default": "kimi_capture_headers"},
            },
            "required": ["messages"],
            "additionalProperties": False,
        }

    def get_request_model(self):
        return ToolRequest

    def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def get_system_prompt(self) -> str:
        return "Capture headers via Kimi raw response; return normalized dict."

    async def execute(self, arguments: dict[str, Any], on_chunk=None):
        from mcp.types import TextContent
        from src.providers.registry_core import ModelProviderRegistry
        from src.providers.kimi import KimiModelProvider

        if not (os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")):
            return [TextContent(type="text", text=json.dumps({"status":"skipped","reason":"Kimi key not present"}))]

        messages = arguments.get("messages") or []
        model = (arguments.get("model") or "kimi-k2-0711-preview").strip()
        temperature = float(arguments.get("temperature", 0.6))
        session_id = arguments.get("session_id")
        call_key = arguments.get("call_key")
        tool_name = arguments.get("tool_name") or "kimi_capture_headers"

        prov = get_registry_instance().get_provider_for_model(model)
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
            prov = KimiModelProvider(api_key=api_key or "")

        result = prov.chat_completions_create(
            model=model,
            messages=messages,
            temperature=temperature,
            tools=None,
            tool_choice=None,
            _session_id=session_id,
            _call_key=call_key,
            _tool_name=tool_name,
        )
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

