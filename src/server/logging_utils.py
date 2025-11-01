"""
Logging Utilities for EXAI MCP Server

This module provides utility functions for logging tool calls and generating
adaptive previews and summaries of tool execution results.

Extracted from server.py to improve testability and reusability.
"""

import json
import math
import os
import re
from typing import Any, Dict, List, Optional


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: The value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        The clamped value
    """
    return max(min_value, min(max_value, value))


def derive_bullets(text: str, max_bullets: int = 5) -> List[str]:
    """
    Extract bullet points from text by splitting on common delimiters.
    
    Args:
        text: The text to extract bullets from
        max_bullets: Maximum number of bullets to return
        
    Returns:
        List of bullet point strings
    """
    try:
        if not text:
            return []
        parts = [p.strip() for p in re.split(r'[\n\.;]+', str(text)) if p.strip()]
        return parts[:max_bullets]
    except Exception:
        return []


def compute_preview_and_summary(
    args: Optional[Dict[str, Any]],
    result: Any,
    duration_s: float
) -> Dict[str, Any]:
    """
    Compute adaptive preview and summary for tool execution results.
    
    This function generates:
    - A preview of the result (truncated based on adaptive sizing)
    - A summary with adaptive word count
    - Bullet points extracted from the prompt
    
    The preview and summary sizes are calculated based on:
    - Output character count (logarithmic scaling)
    - Number of retries (increases size)
    - Error flag (increases size)
    - Execution duration (slight increase)
    
    Args:
        args: Tool execution arguments (may contain prompt, retries, error)
        result: Tool execution result (dict or string)
        duration_s: Execution duration in seconds
        
    Returns:
        Dictionary containing:
        - result_preview: Truncated preview of result
        - result_preview_len: Length of preview
        - result_truncated: Whether result was truncated
        - prompt_bullets: Bullet points from prompt
        - summary_words: Target word count for summary
        - summary_text: Summary text
    """
    # Extract result text
    if isinstance(result, dict):
        result_text = str(result.get("result", "")) or str(result)
    else:
        result_text = str(result)
    
    out_chars = len(result_text or "")
    retries = int((args or {}).get("retries", 0) or 0)
    error_flag = 1 if (args or {}).get("error") else 0
    
    # Adaptive sizing formula
    base = (
        math.log10(max(1, out_chars)) +
        0.4 * retries +
        0.3 * error_flag +
        0.002 * (duration_s * 1000.0)
    )
    
    # Preview sizing
    env_max = int(os.getenv("EXAI_TOOLCALL_PREVIEW_MAX_CHARS", "2000") or "2000")
    preview_len = int(clamp(round(120 * base), 280, env_max))
    preview = (result_text or "")[:preview_len] + ("..." if out_chars > preview_len else "")
    
    # Summary sizing
    sum_max_words = int(os.getenv("EXAI_TOOLCALL_SUMMARY_MAX_WORDS", "600") or "600")
    target_words = int(clamp(round(180 * base), 150, sum_max_words))
    words = re.split(r'\s+', (result_text or "").strip())
    summary_text = " ".join(words[:target_words])
    
    # Extract bullets from prompt
    prompt_text = (args or {}).get("prompt")
    bullets = derive_bullets(prompt_text, max_bullets=5)
    
    return {
        "result_preview": preview,
        "result_preview_len": preview_len,
        "result_truncated": out_chars > preview_len,
        "prompt_bullets": bullets,
        "summary_words": target_words,
        "summary_text": summary_text
    }


def redact_sensitive_data(text: str) -> str:
    """
    Redact potentially sensitive data from text.
    
    Redacts:
    - API keys (sk-...)
    - Hex strings (32+ characters)
    - Long tokens (40+ alphanumeric characters)
    
    Args:
        text: Text to redact
        
    Returns:
        Redacted text
    """
    try:
        # Redact API keys
        text = re.sub(r"sk-[A-Za-z0-9]{16,}", "sk-***REDACTED***", text)
        # Redact long hex strings
        text = re.sub(r"[A-Fa-f0-9]{32,}", "***REDACTED_HEX***", text)
        # Redact long tokens
        text = re.sub(r"[A-Za-z0-9]{40,}", "***REDACTED_TOKEN***", text)
        return text
    except Exception:
        return text


def truncate_large_text(text: str, max_bytes: int = 10 * 1024 * 1024) -> tuple[str, bool]:
    """
    Truncate text if it exceeds maximum byte size.
    
    Args:
        text: Text to truncate
        max_bytes: Maximum size in bytes (default: 10MB)
        
    Returns:
        Tuple of (truncated_text, was_truncated)
    """
    try:
        text_bytes = text.encode("utf-8")
        if len(text_bytes) > max_bytes:
            # Keep 95% of max size to leave room for truncation marker
            truncated = text_bytes[:int(max_bytes * 0.95)].decode("utf-8", errors="ignore")
            return truncated + "... [TRUNCATED]", True
        return text, False
    except Exception:
        return text, False

