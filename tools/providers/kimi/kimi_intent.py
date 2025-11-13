from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.types import TextContent

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest
from src.providers.registry import ModelProviderRegistry
from src.providers.registry_core import get_registry_instance
from src.providers.kimi import KimiModelProvider
from src.providers.registry_core import get_registry_instance


class KimiIntentAnalysisTool(BaseTool):
    name = "kimi_intent_analysis"
    description = (
        "Classify a user prompt and return routing hints using Kimi. "
        "Outputs strict JSON with fields like needs_websearch, complexity, domain, recommended_provider, recommended_model, streaming_preferred."
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
                "prompt": {"type": "string", "description": "User prompt to classify"},
                "context": {"type": "string", "description": "Optional context (hints)"},
                "use_websearch": {"type": "boolean", "default": True},
            },
            "required": ["prompt"],
            "additionalProperties": False,
        }

    def get_request_model(self):
        return ToolRequest

    def prepare_prompt(self, request: ToolRequest) -> str:
        # This tool does not use a unified prompt; provider uses system+user inputs
        return ""

    def get_system_prompt(self) -> str:
        return (
            "You are an intent classifier for an AI router. "
            "Given a user prompt, output a STRICT JSON object with keys: "
            "needs_websearch (boolean), complexity ('simple'|'moderate'|'deep'), domain (string), "
            "recommended_provider ('GLM'|'KIMI'), recommended_model (string), streaming_preferred (boolean). "
            "Rules: prefer GLM 'glm-4.5-flash' for simple, fast tasks; prefer Kimi 'kimi-k2-0905-preview' for deep reasoning/long context; "
            "set needs_websearch=true when the prompt likely requires current information or web browsing. "
            "Return ONLY the JSON."
        )

    def _coerce_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except Exception:
            # Try to extract first JSON object
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass
            # Fallback minimal
            return {
                "needs_websearch": False,
                "complexity": "simple",
                "domain": "general",
                "recommended_provider": "GLM",
                "recommended_model": os.getenv("GLM_FLASH_MODEL", "glm-4.5-flash"),
                "streaming_preferred": False,
            }

    def run(self, **kwargs) -> Dict[str, Any]:
        prompt = (kwargs.get("prompt") or "").strip()
        context = (kwargs.get("context") or "").strip()
        if not prompt:
            raise ValueError("prompt is required")

        # Resolve Kimi provider
        prov = get_registry_instance().get_provider_for_model(os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview"))
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY/MOONSHOT_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        # Model for intent analysis (fast+cheap but good reasoning)
        model = os.getenv("KIMI_INTENT_MODEL", os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview"))

        sys_prompt = self.get_system_prompt()
        user_prompt = prompt if not context else f"{prompt}\n\n[Context]\n{context}"

        mr = prov.generate_content(
            prompt=user_prompt,
            system_prompt=sys_prompt,
            model_name=model,
            temperature=0.1,
            max_output_tokens=int(os.getenv("KIMI_INTENT_MAX_TOKENS", "512")),
        )
        data = self._coerce_json(mr.content or "")
        # Normalize recommendations
        rp = str(data.get("recommended_provider") or "").strip().upper()
        if rp not in {"GLM", "KIMI"}:
            data["recommended_provider"] = "GLM"
        return data

    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list[TextContent]:
        import asyncio as _aio
        from mcp.types import TextContent
        result = await _aio.to_thread(self.run, **arguments)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

