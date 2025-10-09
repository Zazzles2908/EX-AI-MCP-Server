"""Provider capability adapters for provider-native web search.

This module abstracts provider-specific tool schema injection and request normalization
for web search capabilities. It lets tools (e.g., Chat) enable web search uniformly
without hard-coding provider conditionals in tool code.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os

from .base import ProviderType


@dataclass
class WebSearchSchema:
    tools: Optional[List[Dict[str, Any]]]
    tool_choice: Optional[Any]


class ProviderCapabilitiesBase:
    def __init__(self, provider_type: ProviderType):
        self.provider_type = provider_type

    def supports_websearch(self) -> bool:
        return False

    def get_websearch_tool_schema(self, config: Dict[str, Any]) -> WebSearchSchema:
        # Default: no tools
        return WebSearchSchema(tools=None, tool_choice=None)

    def normalize_request_options(self, config: Dict[str, Any]) -> Dict[str, Any]:
        # Default: no changes
        return {}


class KimiCapabilities(ProviderCapabilitiesBase):
    def __init__(self):
        super().__init__(ProviderType.KIMI)

    def supports_websearch(self) -> bool:
        return os.getenv("KIMI_ENABLE_INTERNET_SEARCH", "true").strip().lower() == "true"

    def get_websearch_tool_schema(self, config: Dict[str, Any]) -> WebSearchSchema:
        if not self.supports_websearch() or not config.get("use_websearch"):
            return WebSearchSchema(None, None)

        # Kimi supports builtin_function for SERVER-SIDE web search
        # This means Kimi's API performs the search and returns results directly
        # No client-side execution needed!
        tools: list[dict] = [{
            "type": "builtin_function",
            "function": {"name": "$web_search"}
        }]

        return WebSearchSchema(tools=tools, tool_choice="auto")


class GLMCapabilities(ProviderCapabilitiesBase):
    def __init__(self):
        super().__init__(ProviderType.GLM)

    def supports_websearch(self) -> bool:
        return os.getenv("GLM_ENABLE_WEB_BROWSING", "true").strip().lower() == "true"

    def get_websearch_tool_schema(self, config: Dict[str, Any]) -> WebSearchSchema:
        if not self.supports_websearch() or not config.get("use_websearch"):
            return WebSearchSchema(None, None)

        # ALL GLM models support native web search tool calling (verified 2025-10-09)
        # Source: https://api.z.ai/api/paas/v4/web_search documentation
        # Models: glm-4.6, glm-4.5, glm-4.5-flash, glm-4.5-air, glm-4.5v all support web search

        # GLM requires web_search object with configuration parameters
        # Default to Jina search with one week recency filter
        web_search_config = {
            "search_engine": "search_pro_jina",  # or "search_pro_bing"
            "search_recency_filter": "oneWeek",  # oneDay, oneWeek, oneMonth, oneYear, noLimit
            "content_size": "medium",  # medium: 400-600 chars, high: 2500 chars
            "result_sequence": "after",  # Show results after response
            "search_result": True,  # Return search results
        }
        tools = [{"type": "web_search", "web_search": web_search_config}]
        # Use "auto" to let GLM decide when to execute web_search
        return WebSearchSchema(tools=tools, tool_choice="auto")


def get_capabilities_for_provider(ptype: ProviderType) -> ProviderCapabilitiesBase:
    if ptype == ProviderType.KIMI:
        return KimiCapabilities()
    if ptype == ProviderType.GLM:
        return GLMCapabilities()
    # Default: no-op capabilities
    return ProviderCapabilitiesBase(ptype)
