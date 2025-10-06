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
    Execute web search using configured backend.
    
    Supports: duckduckgo (default), tavily, bing
    
    Args:
        query: Search query string
        
    Returns:
        Dictionary with search results
    """
    backend = os.getenv("SEARCH_BACKEND", "duckduckgo").strip().lower()
    
    try:
        if backend == "tavily":
            api_key = os.getenv("TAVILY_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("TAVILY_API_KEY not set")
            payload = json.dumps({"api_key": api_key, "query": query, "max_results": 5}).encode("utf-8")
            req = urllib.request.Request("https://api.tavily.com/search", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                results = []
                for it in (data.get("results") or [])[:5]:
                    url = it.get("url") or it.get("link")
                    if url:
                        results.append({"title": it.get("title") or it.get("snippet"), "url": url})
                return {"engine": "tavily", "query": query, "results": results}
                
        if backend == "bing":
            key = os.getenv("BING_SEARCH_API_KEY", "").strip()
            if not key:
                raise RuntimeError("BING_SEARCH_API_KEY not set")
            q = urllib.parse.urlencode({"q": query})
            req = urllib.request.Request(f"https://api.bing.microsoft.com/v7.0/search?{q}", headers={"Ocp-Apim-Subscription-Key": key})
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                results = []
                for it in (data.get("webPages", {}).get("value") or [])[:5]:
                    results.append({"title": it.get("name"), "url": it.get("url")})
                return {"engine": "bing", "query": query, "results": results}
                
        # Default: DuckDuckGo
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=5):
                    results.append({"title": r.get("title"), "url": r.get("href") or r.get("link")})
                return {"engine": "duckduckgo", "query": query, "results": results}
        except ImportError:
            # Fallback to simple HTTP request if duckduckgo_search not installed
            q = urllib.parse.quote_plus(query)
            req = urllib.request.Request(f"https://html.duckduckgo.com/html/?q={q}", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                # Very basic parsing - just return query confirmation
                return {"engine": "duckduckgo_fallback", "query": query, "results": [{"title": f"Search: {query}", "url": f"https://duckduckgo.com/?q={q}"}]}
                
    except Exception as e:
        logger.error(f"Web search failed for query '{query}': {e}")
        return {"engine": backend, "query": query, "error": str(e), "results": []}


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
        logger.error(f"Tool execution failed: {e}")
        return {
            "role": "tool",
            "tool_call_id": str(tool_call.get("id", "tc-0")),
            "content": json.dumps({"error": str(e)}, ensure_ascii=False),
        }


__all__ = ["run_web_search_backend", "extract_tool_calls", "execute_tool_call"]

