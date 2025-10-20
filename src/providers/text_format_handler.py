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
# Format A: <tool_call>web_search\nquery: value\nnum_results: 10\n (NEW - actual GLM format)
PATTERN_FORMAT_A = re.compile(
    r'<tool_call>\s*web_search\s*\n\s*query:\s*([^\n]+)',
    re.DOTALL | re.IGNORECASE
)

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

# Format E: <function=use_websearch><parameter=keyword>query</parameter></function> (GLM-4.6 format)
PATTERN_FORMAT_E = re.compile(
    r'<function=use_websearch>\s*<parameter=keyword>\s*(.*?)\s*</parameter>',
    re.DOTALL | re.IGNORECASE
)

# Alternative Format E: <function=web_search><parameter=query>...</parameter></function>
PATTERN_FORMAT_E_ALT = re.compile(
    r'<function=web_search>\s*<parameter=(?:query|keyword)>\s*(.*?)\s*</parameter>',
    re.DOTALL | re.IGNORECASE
)

# Format F: <search>query: value</search> or <search>\n  query: value\n</search> (GLM-4.6 alternative format)
PATTERN_FORMAT_F = re.compile(
    r'<search>\s*query:\s*([^\n<]+)',
    re.DOTALL | re.IGNORECASE
)

# Format F Alt: <search>value</search> (simple format)
PATTERN_FORMAT_F_SIMPLE = re.compile(
    r'<search>\s*([^<]+?)\s*</search>',
    re.DOTALL | re.IGNORECASE
)

# Format G: <TOOL_CALL>{"name": "web_search", "arguments": "{\"query\": \"...\"}"}</TOOL_CALL> (GLM-4.6 uppercase JSON format)
PATTERN_FORMAT_G = re.compile(
    r'<TOOL_CALL>\s*\{\s*"name"\s*:\s*"web_search"\s*,\s*"arguments"\s*:\s*"([^"]+)"\s*\}\s*</TOOL_CALL>',
    re.DOTALL
)

# Format G Alt: Extract full JSON from <TOOL_CALL>
PATTERN_FORMAT_G_JSON = re.compile(
    r'<TOOL_CALL>\s*(\{.*?\})\s*</TOOL_CALL>',
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

    # Try Format G: <TOOL_CALL>{"name": "web_search", "arguments": "{\"query\": \"...\"}"}</TOOL_CALL> (HIGHEST PRIORITY - GLM-4.6 uppercase JSON)
    match_g_json = PATTERN_FORMAT_G_JSON.search(text)
    if match_g_json:
        try:
            tool_data = json.loads(match_g_json.group(1))
            if tool_data.get("name") == "web_search":
                # Arguments might be a JSON string or dict
                args = tool_data.get("arguments", "{}")
                if isinstance(args, str):
                    # Parse the escaped JSON string
                    args_data = json.loads(args)
                else:
                    args_data = args

                query = args_data.get("query", "").strip()
                if query:
                    logger.info(f"✅ Parsed Format G (GLM-4.6 <TOOL_CALL> uppercase JSON): query='{query}'")
                    return query
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.debug(f"Failed to parse Format G JSON: {e}")

    # Try Format F: <search>query: value</search> (GLM-4.6 format - HIGH PRIORITY)
    match_f = PATTERN_FORMAT_F.search(text)
    if match_f:
        query = match_f.group(1).strip()
        logger.info(f"✅ Parsed Format F (GLM-4.6 <search>query: value</search>): query='{query}'")
        return query

    # Try Format F Simple: <search>value</search>
    match_f_simple = PATTERN_FORMAT_F_SIMPLE.search(text)
    if match_f_simple:
        query = match_f_simple.group(1).strip()
        # Only accept if it looks like a reasonable query (not empty, not too long)
        if query and len(query) < 500 and not query.startswith('<'):
            logger.info(f"✅ Parsed Format F Simple (<search>value</search>): query='{query}'")
            return query

    # Try Format E: <function=use_websearch><parameter=keyword>query</parameter> (GLM-4.6 format)
    match_e = PATTERN_FORMAT_E.search(text)
    if match_e:
        query = match_e.group(1).strip()
        logger.info(f"✅ Parsed Format E (GLM-4.6 <function=use_websearch>): query='{query}'")
        return query

    # Try Format E Alt: <function=web_search><parameter=query>...</parameter>
    match_e_alt = PATTERN_FORMAT_E_ALT.search(text)
    if match_e_alt:
        query = match_e_alt.group(1).strip()
        logger.info(f"✅ Parsed Format E Alt (<function=web_search>): query='{query}'")
        return query

    # Try Format A: <tool_call>web_search\nquery: value (NEW - actual GLM format)
    match_a = PATTERN_FORMAT_A.search(text)
    if match_a:
        query = match_a.group(1).strip()
        logger.debug(f"Parsed Format A (key:value): query='{query}'")
        return query

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

    logger.warning(f"⚠️ No web search query pattern matched in text: {text[:200]}...")
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
        from src.providers.tool_executor import run_web_search_backend

        logger.info(f"Executing web_search via text format handler: query='{query}'")
        search_results = run_web_search_backend(query)

        if search_results and search_results.get("results"):
            logger.info(f"GLM web_search executed successfully via text format handler")
            return search_results
        else:
            logger.warning(f"Web search returned no results for query: {query}")
            return None

    except ImportError:
        logger.error("Web search backend function not found (run_web_search_backend)")
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

    # Check for common text format markers (including GLM-4.6 formats)
    markers = [
        "<TOOL_CALL>",                 # GLM-4.6 uppercase JSON format (MOST COMMON NOW)
        "<tool_call>",
        "<tool_code>",
        "<function=use_websearch>",  # GLM-4.6 format variant 1
        "<function=web_search>",      # GLM-4.6 format variant 2
        "<function=",                  # Generic function call
        "<search>"                     # GLM-4.6 format variant 3
    ]
    has_marker = any(marker in text for marker in markers)

    if has_marker:
        logger.info(f"✅ Text format tool call detected in response (length: {len(text)} chars)")
        logger.debug(f"Response preview: {text[:300]}...")

    return has_marker

