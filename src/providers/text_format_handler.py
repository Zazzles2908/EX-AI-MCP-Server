"""
Text Format Handler for GLM Web Search Responses

This module handles cases where GLM models return web_search tool calls as TEXT
instead of in the tool_calls array. This is particularly common with glm-4.5-flash.

Supported Formats:
- Format B: <tool_call>web_search...<arg_value>query</tool_call>
- Format C: <tool_code>{"name": "web_search", "parameters": {"query": "..."}}</tool_code>
- Format D: Acknowledgment only (gracefully skipped)
"""

import re
import json
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Compile regex patterns once for performance
# Format B: <tool_call>web_search...<arg_value>query</tool_call>
PATTERN_FORMAT_B = re.compile(
    r'<tool_call>\s*web_search\s*.*?<arg_value>\s*(.*?)\s*</tool_call>',
    re.DOTALL | re.IGNORECASE
)

# Format C: <tool_code>{"name": "web_search", "parameters": {"query": "..."}}
PATTERN_FORMAT_C = re.compile(
    r'<tool_code>\s*\{\s*[^}]*?\s*"name"\s*:\s*"web_search"[^}]*?\s*"query"\s*:\s*"([^"]+)"',
    re.DOTALL | re.IGNORECASE
)

# Alternative Format C: Extract full JSON object
PATTERN_FORMAT_C_JSON = re.compile(
    r'<tool_code>\s*(\{.*?\})\s*</tool_code>',
    re.DOTALL
)


def extract_query_from_text(text: str) -> Optional[str]:
    """
    Extract web search query from text format tool call.
    
    Args:
        text: Response text that may contain tool call in text format
        
    Returns:
        Extracted query string, or None if no query found
    """
    query = None
    
    # Try Format B: <tool_call>web_search...<arg_value>query</tool_call>
    match_b = PATTERN_FORMAT_B.search(text)
    if match_b:
        query = match_b.group(1).strip()
        logger.debug(f"Parsed Format B: query='{query}'")
        return query
    
    # Try Format C: Direct query extraction
    match_c = PATTERN_FORMAT_C.search(text)
    if match_c:
        query = match_c.group(1).strip()
        logger.debug(f"Parsed Format C: query='{query}'")
        return query
    
    # Try Format C: JSON object extraction
    match_c_json = PATTERN_FORMAT_C_JSON.search(text)
    if match_c_json:
        try:
            tool_data = json.loads(match_c_json.group(1))
            if tool_data.get("name") == "web_search":
                params = tool_data.get("parameters", {})
                query = params.get("query", "").strip()
                if query:
                    logger.debug(f"Parsed Format C (JSON): query='{query}'")
                    return query
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse Format C JSON: {e}")
    
    return None


def execute_web_search_fallback(query: str, max_results: int = 5) -> Optional[dict]:
    """
    Execute web search using DuckDuckGo fallback.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        Search results dict, or None if search fails
    """
    try:
        from src.utils.web_search_fallback import execute_duckduckgo_search
        
        logger.info(f"Executing web_search via text format handler: query='{query}'")
        search_results = execute_duckduckgo_search(query, max_results=max_results)
        
        if search_results:
            logger.info(f"GLM web_search executed successfully via text format handler")
            return search_results
        else:
            logger.warning(f"Web search returned no results for query: {query}")
            return None
            
    except ImportError:
        logger.error("Web search fallback function not found (execute_duckduckgo_search)")
        return None
    except Exception as e:
        logger.error(f"Error executing web search fallback: {e}", exc_info=True)
        return None


def parse_and_execute_web_search(text: str) -> Tuple[str, bool]:
    """
    Parse text format tool call and execute web search if found.
    
    This is the main entry point for handling text format web search responses.
    
    Args:
        text: Response text that may contain tool call in text format
        
    Returns:
        Tuple of (updated_text, success_flag)
        - updated_text: Original text with search results appended if successful
        - success_flag: True if search was executed successfully, False otherwise
    """
    try:
        # Extract query from text
        query = extract_query_from_text(text)
        
        if not query:
            logger.debug("No web search query found in text format response")
            return text, False
        
        # Execute web search
        search_results = execute_web_search_fallback(query, max_results=5)
        
        if not search_results:
            logger.warning(f"Web search failed for query: {query}")
            return text, False
        
        # Format results similar to tool_calls array format
        results_text = "\n\n[Web Search Results]\n" + json.dumps(
            search_results,
            indent=2,
            ensure_ascii=False
        )
        
        updated_text = text + results_text
        return updated_text, True
        
    except (re.error, json.JSONDecodeError) as e:
        logger.error(f"Parsing error in text format handler: {e}")
        return text, False
    except Exception as e:
        logger.error(f"Unexpected error in text format handler: {e}", exc_info=True)
        return text, False


def has_text_format_tool_call(text: str) -> bool:
    """
    Check if text contains a tool call in text format.
    
    Args:
        text: Response text to check
        
    Returns:
        True if text format tool call detected, False otherwise
    """
    if not text:
        return False
    
    # Check for common text format markers
    markers = ["<tool_call>", "<tool_code>", "<function="]
    return any(marker in text for marker in markers)

