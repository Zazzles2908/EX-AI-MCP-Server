"""
Token estimation and size validation utilities.

This module handles token counting, file size checking, and MCP boundary validation
to ensure files fit within model context windows.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def estimate_file_tokens(file_path: str) -> int:
    """
    Estimate tokens for a file using file-type aware ratios.

    Args:
        file_path: Path to the file

    Returns:
        Estimated token count for the file
    """
    try:
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return 0

        file_size = os.path.getsize(file_path)

        # Get the appropriate ratio for this file type
        from .types import get_token_estimation_ratio

        ratio = get_token_estimation_ratio(file_path)

        return int(file_size / ratio)
    except Exception:
        return 0


def check_files_size_limit(files: list[str], max_tokens: int, threshold_percent: float = 1.0) -> tuple[bool, int, int]:
    """
    Check if a list of files would exceed token limits.

    Args:
        files: List of file paths to check
        max_tokens: Maximum allowed tokens
        threshold_percent: Percentage of max_tokens to use as threshold (0.0-1.0)

    Returns:
        Tuple of (within_limit, total_estimated_tokens, file_count)
    """
    if not files:
        return True, 0, 0

    total_estimated_tokens = 0
    file_count = 0
    threshold = int(max_tokens * threshold_percent)

    for file_path in files:
        try:
            estimated_tokens = estimate_file_tokens(file_path)
            total_estimated_tokens += estimated_tokens
            if estimated_tokens > 0:  # Only count accessible files
                file_count += 1
        except Exception:
            # Skip files that can't be accessed for size check
            continue

    within_limit = total_estimated_tokens <= threshold
    return within_limit, total_estimated_tokens, file_count


def check_total_file_size(files: list[str], model_name: str) -> Optional[dict]:
    """
    Check if total file sizes would exceed token threshold before embedding.

    IMPORTANT: This performs STRICT REJECTION at MCP boundary.
    No partial inclusion - either all files fit or request is rejected.
    This forces Claude to make better file selection decisions.

    This function MUST be called with the effective model name (after resolution).
    It should never receive 'auto' or None - model resolution happens earlier.

    Args:
        files: List of file paths to check
        model_name: The resolved model name for context-aware thresholds (required)

    Returns:
        Dict with `code_too_large` response if too large, None if acceptable
    """
    if not files:
        return None

    # Validate we have a proper model name (not auto or None)
    if not model_name or model_name.lower() == "auto":
        raise ValueError(
            f"check_total_file_size called with unresolved model: '{model_name}'. "
            "Model must be resolved before file size checking."
        )

    logger.info(f"File size check: Using model '{model_name}' for token limit calculation")

    from utils.model.context import ModelContext

    model_context = ModelContext(model_name)
    token_allocation = model_context.calculate_token_allocation()

    # Dynamic threshold based on model capacity
    context_window = token_allocation.total_tokens
    if context_window >= 1_000_000:  # Gemini-class models
        threshold_percent = 0.8  # Can be more generous
    elif context_window >= 500_000:  # Mid-range models
        threshold_percent = 0.7  # Moderate
    else:  # OpenAI-class models (200K)
        threshold_percent = 0.6  # Conservative

    max_file_tokens = int(token_allocation.file_tokens * threshold_percent)

    # Use centralized file size checking (threshold already applied to max_file_tokens)
    within_limit, total_estimated_tokens, file_count = check_files_size_limit(files, max_file_tokens)

    if not within_limit:
        return {
            "status": "code_too_large",
            "content": (
                f"The selected files are too large for analysis "
                f"(estimated {total_estimated_tokens:,} tokens, limit {max_file_tokens:,}). "
                f"Please select fewer, more specific files that are most relevant "
                f"to your question, then invoke the tool again."
            ),
            "content_type": "text",
            "metadata": {
                "total_estimated_tokens": total_estimated_tokens,
                "limit": max_file_tokens,
                "file_count": file_count,
                "threshold_percent": threshold_percent,
                "model_context_window": context_window,
                "model_name": model_name,
                "instructions": "Reduce file selection and try again - all files must fit within budget. If this persists, please use a model with a larger context window where available.",
            },
        }

    return None  # Proceed with ALL files

