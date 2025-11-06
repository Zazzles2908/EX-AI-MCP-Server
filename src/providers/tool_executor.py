"""
Tool execution handler for provider-native tools (web_search, etc.)

This module provides a centralized tool execution loop that handles:
1. Extracting tool_calls from provider responses
2. Executing supported tools (web_search)
3. Sending results back to the model
4. Continuing the conversation until completion
"""

import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def run_web_search_backend(query: str) -> dict:
    """
    Execute web search using GLM native web search API.

    Uses Z.ai /api/paas/v4/web_search endpoint (native GLM web search).
    Documentation: https://docs.z.ai/api-reference/tools/web-search

    Last Updated: 2025-10-09 (Removed DuckDuckGo fallback, using native GLM only)

    Args:
        query: Search query string

    Returns:
        Dictionary with search results from GLM web search
    """
    try:
        # CRITICAL FIX (P2.1): Enhanced API key validation and logging for Docker debugging
        api_key = os.getenv("GLM_API_KEY", "").strip()
        if not api_key:
            error_msg = (
                "GLM_API_KEY not found in environment variables. "
                "This is required for web search functionality. "
                "In Docker, verify .env.docker is properly mounted and contains GLM_API_KEY."
            )
            log_error(ErrorCode.INTERNAL_ERROR, error_msg, exc_info=True)
            log_error(ErrorCode.PROVIDER_ERROR, error_msg)
            raise ProviderError("Provider", Exception(error_msg))

        # Log API key presence (first 8 chars only for security)
        logger.debug(f"GLM_API_KEY found: {api_key[:8]}... (length: {len(api_key)})")

        base_url = os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4").strip()
        web_search_url = f"{base_url}/web_search"

        logger.info(f"Initiating GLM web search for query: '{query}' using endpoint: {web_search_url}")

        # Prepare request payload
        # Documentation: https://docs.z.ai/api-reference/tools/web-search
        payload = {
            "search_query": query,
            "count": int(os.getenv("GLM_WEBSEARCH_COUNT", "10")),
            "search_engine": os.getenv("GLM_WEBSEARCH_ENGINE", "search-prime"),  # search-prime or search-pro
            "search_recency_filter": os.getenv("GLM_WEBSEARCH_RECENCY", "all"),  # oneDay, oneWeek, oneMonth, oneYear, all
        }

        logger.debug(f"Web search payload: {json.dumps(payload, indent=2)}")

        # Optional parameters
        domain_filter = os.getenv("GLM_WEBSEARCH_DOMAIN_FILTER", "").strip()
        if domain_filter:
            payload["search_domain_filter"] = domain_filter

        # Make request to GLM web search API
        data = json.dumps(payload).encode("utf-8")
        accept_lang = os.getenv("GLM_ACCEPT_LANGUAGE", "en-US,en")
        req = urllib.request.Request(
            web_search_url,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": accept_lang,
            }
        )

        timeout_s = float(os.getenv("GLM_WEBSEARCH_TIMEOUT_SECS", "30"))

        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            result = json.loads(raw)

            # Add metadata
            result["engine"] = "glm_native"
            result["query"] = query

            # CRITICAL FIX (P2.1): Enhanced success logging
            result_count = len(result.get("results", []))
            logger.info(
                f"GLM native web search completed successfully for query: '{query}' "
                f"(returned {result_count} results)"
            )
            return result

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
        # CRITICAL FIX (P2.1): Enhanced error logging for Docker debugging
        error_msg = (
            f"GLM web search HTTP {e.code} error for query '{query}': {body}\n"
            f"Endpoint: {web_search_url}\n"
            f"This may indicate: API key invalid, rate limiting, or network restrictions in Docker."
        )
        log_error(ErrorCode.INTERNAL_ERROR, error_msg, exc_info=True, exc_info=True)
        return {"engine": "glm_native", "query": query, "error": error_msg, "results": []}

    except urllib.error.URLError as e:
        # CRITICAL FIX (P2.1): Enhanced network error logging
        error_msg = (
            f"GLM web search network error for query '{query}': {e}\n"
            f"Endpoint: {web_search_url}\n"
            f"This may indicate: Docker container lacks internet access, DNS resolution failure, "
            f"or firewall blocking outbound connections."
        )
        log_error(ErrorCode.INTERNAL_ERROR, error_msg, exc_info=True, exc_info=True)
        return {"engine": "glm_native", "query": query, "error": error_msg, "results": []}

    except Exception as e:
        error_msg = f"GLM web search failed: {e}"
        log_error(ErrorCode.INTERNAL_ERROR, error_msg, exc_info=True)
        return {"engine": "glm_native", "query": query, "error": error_msg, "results": []}


def extract_tool_calls(response_dict: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Extract tool_calls from provider response.
    
    Args:
        response_dict: Provider response dictionary
        
    Returns:
        List of tool_calls or None if not present
    """
    try:
        choices = response_dict.get("choices", [])
        if not choices:
            return None
            
        message = choices[0].get("message", {})
        tool_calls = message.get("tool_calls")
        
        if not tool_calls:
            return None
            
        # Normalize tool_calls to list of dicts
        normalized = []
        for tc in tool_calls:
            if isinstance(tc, dict):
                normalized.append(tc)
            elif hasattr(tc, "model_dump"):
                normalized.append(tc.model_dump())
            else:
                # Try to convert object to dict
                try:
                    normalized.append({
                        "id": getattr(tc, "id", None),
                        "type": getattr(tc, "type", "function"),
                        "function": {
                            "name": getattr(getattr(tc, "function", None), "name", None),
                            "arguments": getattr(getattr(tc, "function", None), "arguments", "{}"),
                        }
                    })
                except Exception:
                    continue
                    
        return normalized if normalized else None
        
    except Exception as e:
        logger.debug(f"Failed to extract tool_calls: {e}")
        return None


def execute_tool_call(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single tool call.

    NOTE: This function is for CLIENT-SIDE tool execution only.
    For Kimi builtin_function ($web_search) and GLM web_search tool,
    the provider API executes the search SERVER-SIDE and returns results
    directly in the response content. No client execution needed!

    This function is kept for potential future client-side tools.

    Args:
        tool_call: Tool call dictionary with id, type, function

    Returns:
        Tool message dictionary to send back to model
    """
    try:
        # Check tool type
        tool_type = tool_call.get("type", "function")

        # Server-side tools (handled by provider API)
        if tool_type == "builtin_function":
            # Kimi builtin functions are executed server-side
            # We should never reach here for $web_search
            logger.warning(f"Received builtin_function tool_call - this should be handled server-side!")
            return {
                "role": "tool",
                "tool_call_id": str(tool_call.get("id", "tc-0")),
                "content": json.dumps({"error": "Builtin functions are executed server-side"}, ensure_ascii=False),
            }

        # Client-side function tools
        func = tool_call.get("function", {})
        func_name = func.get("name", "").strip()
        func_args_raw = func.get("arguments", "{}")

        # Parse arguments
        if isinstance(func_args_raw, str):
            try:
                func_args = json.loads(func_args_raw)
            except Exception:
                func_args = {"query": func_args_raw}
        elif isinstance(func_args_raw, dict):
            func_args = func_args_raw
        else:
            func_args = {}

        # Execute supported client-side tools
        if func_name == "web_search":
            # This is for custom client-side web search (not used by default)
            query = func_args.get("query", "")
            if not query:
                result = {"error": "No query provided"}
            else:
                result = run_web_search_backend(query)

            return {
                "role": "tool",
                "tool_call_id": str(tool_call.get("id", "tc-0")),
                "content": json.dumps(result, ensure_ascii=False),
            }
        else:
            # Unsupported tool
            return {
                "role": "tool",
                "tool_call_id": str(tool_call.get("id", "tc-0")),
                "content": json.dumps({"error": f"Unsupported tool: {func_name}"}, ensure_ascii=False),
            }

    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Tool execution failed: {e}", exc_info=True)
        return {
            "role": "tool",
            "tool_call_id": str(tool_call.get("id", "tc-0")),
            "content": json.dumps({"error": str(e)}, ensure_ascii=False),
        }


__all__ = ["run_web_search_backend", "extract_tool_calls", "execute_tool_call"]

