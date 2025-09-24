from __future__ import annotations

import json
import os
from typing import Any, Dict, List
from mcp.types import TextContent

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest
from src.providers.glm import GLMModelProvider
from src.providers.registry import ModelProviderRegistry


class GLMWebSearchTool(BaseTool):
    def get_name(self) -> str:
        return "glm_web_search"

    def get_description(self) -> str:
        return (
            "Perform web search using GLM's native web browsing capabilities. "
            "Leverages GLM-4.5's built-in web search tool for real-time information retrieval."
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for web browsing"
                },
                "model": {
                    "type": "string",
                    "default": os.getenv("GLM_QUALITY_MODEL", "glm-4.5"),
                    "description": "GLM model to use for web search"
                },
                "temperature": {
                    "type": "number",
                    "default": 0.3,
                    "description": "Temperature for response generation"
                },
                "max_results": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum number of search results to process"
                }
            },
            "required": ["query"]
        }

    def get_system_prompt(self) -> str:
        return (
            "You are a GLM web search assistant with native browsing capabilities.\n"
            "Purpose: Use GLM's built-in web search tool to retrieve real-time information from the internet.\n\n"
            "Parameters:\n"
            "- query: Search query string for web browsing\n"
            "- model: GLM model to use (default: glm-4.5)\n"
            "- temperature: Response generation temperature\n"
            "- max_results: Maximum search results to process\n\n"
            "Features:\n"
            "- Real-time web information retrieval\n"
            "- Native GLM web browsing integration\n"
            "- Structured search result processing\n\n"
            "Output: Comprehensive search results with analysis and synthesis."
        )

    def get_request_model(self):
        return ToolRequest

    def requires_model(self) -> bool:
        return False

    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def format_response(self, response: str, request: ToolRequest, model_info: dict | None = None) -> str:
        return response

    def _run(self, **kwargs) -> Dict[str, Any]:
        query = kwargs.get("query")
        if not query:
            raise ValueError("Query is required for web search")

        model = kwargs.get("model") or os.getenv("GLM_QUALITY_MODEL", "glm-4.5")
        temperature = float(kwargs.get("temperature", 0.3))
        max_results = int(kwargs.get("max_results", 5))

        # Resolve provider
        prov = ModelProviderRegistry.get_provider_for_model(model)
        if not isinstance(prov, GLMModelProvider):
            api_key = os.getenv("GLM_API_KEY", "")
            if not api_key:
                raise RuntimeError("GLM_API_KEY is not configured")
            prov = GLMModelProvider(api_key=api_key)

        try:
            # Use the new web_search method from GLM provider
            search_result = prov.web_search(
                query=query,
                model=model,
                temperature=temperature,
                max_results=max_results
            )

            return {
                "provider": "GLM",
                "model": model,
                "query": query,
                "search_results": search_result,
                "status": search_result.get("status", "unknown")
            }

        except Exception as e:
            # Observability: record error
            try:
                from utils.observability import record_error
                record_error("GLM", model, "web_search_error", str(e))
            except Exception:
                pass
            raise

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        import asyncio as _aio
        from tools.shared.error_envelope import make_error_envelope
        
        try:
            # Apply timeout for web search operations
            timeout_s = float(os.getenv("GLM_WEB_SEARCH_TIMEOUT_SECS", "60"))
            result = await _aio.wait_for(_aio.to_thread(self._run, **arguments), timeout=timeout_s)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        except _aio.TimeoutError:
            env = make_error_envelope("GLM", self.get_name(), f"GLM web search timed out after {int(timeout_s)}s")
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]
        except Exception as e:
            env = make_error_envelope("GLM", self.get_name(), e)
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]


class GLMWebBrowseChatTool(BaseTool):
    def get_name(self) -> str:
        return "glm_web_browse_chat"

    def get_description(self) -> str:
        return (
            "Perform web browsing and chat with GLM using native web search capabilities. "
            "Combines web search with conversational AI for comprehensive responses."
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "User prompt that may require web information"
                },
                "enable_web_search": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to enable web search for this query"
                },
                "model": {
                    "type": "string",
                    "default": os.getenv("GLM_QUALITY_MODEL", "glm-4.5")
                },
                "temperature": {
                    "type": "number",
                    "default": 0.3
                }
            },
            "required": ["prompt"]
        }

    def get_system_prompt(self) -> str:
        return (
            "You are a GLM web-enabled chat assistant.\n"
            "Purpose: Provide comprehensive responses using web browsing when needed.\n\n"
            "Capabilities:\n"
            "- Native GLM web search integration\n"
            "- Real-time information retrieval\n"
            "- Conversational AI with web context\n\n"
            "Output: Informative responses enhanced with current web information when relevant."
        )

    def get_request_model(self):
        return ToolRequest

    def requires_model(self) -> bool:
        return False

    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def format_response(self, response: str, request: ToolRequest, model_info: dict | None = None) -> str:
        return response

    def _run(self, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt")
        if not prompt:
            raise ValueError("Prompt is required")

        model = kwargs.get("model") or os.getenv("GLM_QUALITY_MODEL", "glm-4.5")
        temperature = float(kwargs.get("temperature", 0.3))
        enable_web_search = bool(kwargs.get("enable_web_search", True))

        # Resolve provider
        prov = ModelProviderRegistry.get_provider_for_model(model)
        if not isinstance(prov, GLMModelProvider):
            api_key = os.getenv("GLM_API_KEY", "")
            if not api_key:
                raise RuntimeError("GLM_API_KEY is not configured")
            prov = GLMModelProvider(api_key=api_key)

        try:
            messages = [{"role": "user", "content": prompt}]
            tools = []
            
            if enable_web_search:
                # Add web search tool to the conversation
                tools = [
                    {
                        "type": "web_search",
                        "web_search": {
                            "search_query": prompt,
                            "search_result": True
                        }
                    }
                ]

            # Use GLM's chat completions with web search tools
            if getattr(prov, "_use_sdk", False):
                response = prov._sdk_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools if tools else None,
                    temperature=temperature,
                    stream=False
                )
                
                if hasattr(response, "choices") and response.choices:
                    content = response.choices[0].message.content
                else:
                    content = ""
            else:
                # HTTP fallback
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": False
                }
                if tools:
                    payload["tools"] = tools
                
                response = prov.client.post_json("/chat/completions", payload)
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            return {
                "provider": "GLM",
                "model": model,
                "content": content,
                "web_search_enabled": enable_web_search,
                "status": "success"
            }

        except Exception as e:
            try:
                from utils.observability import record_error
                record_error("GLM", model, "web_browse_chat_error", str(e))
            except Exception:
                pass
            raise

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        import asyncio as _aio
        from tools.shared.error_envelope import make_error_envelope
        
        try:
            timeout_s = float(os.getenv("GLM_WEB_BROWSE_CHAT_TIMEOUT_SECS", "120"))
            result = await _aio.wait_for(_aio.to_thread(self._run, **arguments), timeout=timeout_s)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        except _aio.TimeoutError:
            env = make_error_envelope("GLM", self.get_name(), f"GLM web browse chat timed out after {int(timeout_s)}s")
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]
        except Exception as e:
            env = make_error_envelope("GLM", self.get_name(), e)
            return [TextContent(type="text", text=json.dumps(env, ensure_ascii=False))]
