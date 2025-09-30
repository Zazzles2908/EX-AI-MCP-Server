from __future__ import annotations

import json
from typing import Any, Dict

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest

class GLMPayloadPreviewTool(BaseTool):
    name = "glm_payload_preview"
    description = (
        "Preview the GLM chat.completions payload that would be sent, including explicit tools/tool_choice. "
        "Does not perform any network calls."
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
                "prompt": {"type": "string"},
                "model": {"type": "string", "default": "glm-4.5-flash"},
                "temperature": {"type": "number", "default": 0.3},
                "system_prompt": {"type": ["string", "null"]},
                "use_websearch": {"type": "boolean", "default": False},
                "tools": {"type": "array", "items": {"type": "object"}},
                "tool_choice": {"type": ["string", "object", "null"]},
            },
            "required": ["prompt"],
            "additionalProperties": False,
        }

    def get_request_model(self):
        return ToolRequest

    def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def get_system_prompt(self) -> str:
        return "Preview GLM payload; no network I/O."

    async def execute(self, arguments: dict[str, Any]):
        from mcp.types import TextContent
        from src.providers.glm import GLMModelProvider

        prompt = (arguments.get("prompt") or "").strip()
        model = (arguments.get("model") or "glm-4.5-flash").strip()
        system_prompt = arguments.get("system_prompt")
        temperature = float(arguments.get("temperature", 0.3))
        use_web = bool(arguments.get("use_websearch", False))
        tools = arguments.get("tools") or []
        if use_web and not any(isinstance(t, dict) and t.get("type") == "web_search" for t in tools):
            tools = tools + [{"type": "web_search"}]
        tool_choice = arguments.get("tool_choice")

        # Build payload via provider without sending
        p = GLMModelProvider(api_key="dummy")  # api_key unused for _build_payload
        payload = p._build_payload(
            prompt=prompt,
            system_prompt=system_prompt,
            model_name=model,
            temperature=temperature,
            max_output_tokens=None,
            tools=tools or None,
            tool_choice=tool_choice,
        )
        return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]

