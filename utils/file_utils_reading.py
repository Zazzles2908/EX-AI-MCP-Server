"""
File reading and content formatting utilities.

This module handles reading file content, formatting it for AI consumption,
and managing line numbers and token budgets.
"""

import logging
from pathlib import Path
from typing import Optional

from .file_types import BINARY_EXTENSIONS, IMAGE_EXTENSIONS, TEXT_EXTENSIONS
from .file_utils_expansion import expand_paths
from .file_utils_security import resolve_and_validate_path
from .token_utils import DEFAULT_CONTEXT_WINDOW, estimate_tokens

logger = logging.getLogger(__name__)


def detect_file_type(file_path: str) -> str:
    """
    Detect file type for appropriate processing strategy.

    This function is intended for specific file type handling (e.g., image processing,
    binary file analysis, or enhanced file filtering).

    Args:
        file_path: Path to the file to analyze

    Returns:
        str: "text", "binary", or "image"
    """
    path = Path(file_path)

    # Check extension first (fast)
    extension = path.suffix.lower()
    if extension in TEXT_EXTENSIONS:
        return "text"
    elif extension in IMAGE_EXTENSIONS:
        return "image"
    elif extension in BINARY_EXTENSIONS:
        return "binary"

    # Fallback: check magic bytes for text vs binary
    # This is helpful for files without extensions or unknown extensions
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            # Simple heuristic: if we can decode as UTF-8, likely text
            chunk.decode("utf-8")
            return "text"
    except UnicodeDecodeError:
        return "binary"
    except (FileNotFoundError, PermissionError) as e:
        logger.warning(f"Could not access file {file_path} for type detection: {e}")
        return "unknown"


def should_add_line_numbers(file_path: str, include_line_numbers: Optional[bool] = None) -> bool:
    """
    Determine if line numbers should be added to a file.

    Args:
        file_path: Path to the file
        include_line_numbers: Explicit preference, or None for auto-detection

    Returns:
        bool: True if line numbers should be added
    """
    if include_line_numbers is not None:
        return include_line_numbers

    # Default: DO NOT add line numbers
    # Tools that want line numbers must explicitly request them
    return False


def _normalize_line_endings(content: str) -> str:
    """
    Normalize line endings for consistent line numbering.

    Args:
        content: File content with potentially mixed line endings

    Returns:
        str: Content with normalized LF line endings
    """
    # Normalize all line endings to LF for consistent counting
    return content.replace("\r\n", "\n").replace("\r", "\n")


def _add_line_numbers(content: str) -> str:
    """
    Add line numbers to text content for precise referencing.

    Args:
        content: Text content to number

    Returns:
        str: Content with line numbers in format "  45│ actual code line"
        Supports files up to 99,999 lines with dynamic width allocation
    """
    # Normalize line endings first
    normalized_content = _normalize_line_endings(content)
    lines = normalized_content.split("\n")

    # Dynamic width allocation based on total line count
    # This supports files of any size by computing required width
    total_lines = len(lines)
    width = len(str(total_lines))
    width = max(width, 4)  # Minimum padding for readability

    # Format with dynamic width and clear separator
    numbered_lines = [f"{i + 1:{width}d}│ {line}" for i, line in enumerate(lines)]

    return "\n".join(numbered_lines)


def read_file_content(
    file_path: str, max_size: int = 1_000_000, *, include_line_numbers: Optional[bool] = None
) -> tuple[str, int]:
    """
    Read a single file and format it for inclusion in AI prompts.

    This function handles various error conditions gracefully and always
    returns formatted content, even for errors. This ensures the AI model
    gets context about what files were attempted but couldn't be read.

    Args:
        file_path: Path to file (must be absolute)
        max_size: Maximum file size to read (default 1MB to prevent memory issues)
        include_line_numbers: Whether to add line numbers. If None, auto-detects based on file type

    Returns:
        Tuple of (formatted_content, estimated_tokens)
        Content is wrapped with clear delimiters for AI parsing
    """
    logger.debug(f"[FILES] read_file_content called for: {file_path}")
    try:
        # Validate path security before any file operations
        path = resolve_and_validate_path(file_path)
        logger.debug(f"[FILES] Path validated and resolved: {path}")
    except (ValueError, PermissionError) as e:
        # Return error in a format that provides context to the AI
        logger.debug(f"[FILES] Path validation failed for {file_path}: {type(e).__name__}: {e}")
        error_msg = str(e)
        content = f"\n--- ERROR ACCESSING FILE: {file_path} ---\nError: {error_msg}\n--- END FILE ---\n"
        tokens = estimate_tokens(content)
        logger.debug(f"[FILES] Returning error content for {file_path}: {tokens} tokens")
        return content, tokens

    try:
        # Validate file existence and type
        if not path.exists():
            logger.debug(f"[FILES] File does not exist: {file_path}")
            content = f"\n--- FILE NOT FOUND: {file_path} ---\nError: File does not exist\n--- END FILE ---\n"
            return content, estimate_tokens(content)

        if not path.is_file():
            logger.debug(f"[FILES] Path is not a file: {file_path}")
            content = f"\n--- NOT A FILE: {file_path} ---\nError: Path is not a file\n--- END FILE ---\n"
            return content, estimate_tokens(content)

        # Check file size to prevent memory exhaustion
        file_size = path.stat().st_size
        logger.debug(f"[FILES] File size for {file_path}: {file_size:,} bytes")
        if file_size > max_size:
            logger.debug(f"[FILES] File too large: {file_path} ({file_size:,} > {max_size:,} bytes)")
            content = f"\n--- FILE TOO LARGE: {file_path} ---\nFile size: {file_size:,} bytes (max: {max_size:,})\n--- END FILE ---\n"
            return content, estimate_tokens(content)

        # Determine if we should add line numbers
        add_line_numbers = should_add_line_numbers(file_path, include_line_numbers)
        logger.debug(f"[FILES] Line numbers for {file_path}: {'enabled' if add_line_numbers else 'disabled'}")

        # Read the file with UTF-8 encoding, replacing invalid characters
        # This ensures we can handle files with mixed encodings
        logger.debug(f"[FILES] Reading file content for {file_path}")
        with open(path, encoding="utf-8", errors="replace") as f:
            file_content = f.read()

        logger.debug(f"[FILES] Successfully read {len(file_content)} characters from {file_path}")

        # Add line numbers if requested or auto-detected
        if add_line_numbers:
            file_content = _add_line_numbers(file_content)
            logger.debug(f"[FILES] Added line numbers to {file_path}")
        else:
            # Still normalize line endings for consistency
            file_content = _normalize_line_endings(file_content)

        # Format with clear delimiters that help the AI understand file boundaries
        # Using consistent markers makes it easier for the model to parse
        # NOTE: These markers ("--- BEGIN FILE: ... ---") are distinct from git diff markers
        # ("--- BEGIN DIFF: ... ---") to allow AI to distinguish between complete file content
        # vs. partial diff content when files appear in both sections
        formatted = f"\n--- BEGIN FILE: {file_path} ---\n{file_content}\n--- END FILE: {file_path} ---\n"
        tokens = estimate_tokens(formatted)
        logger.debug(f"[FILES] Formatted content for {file_path}: {len(formatted)} chars, {tokens} tokens")
        return formatted, tokens

    except Exception as e:
        logger.debug(f"[FILES] Exception reading file {file_path}: {type(e).__name__}: {e}")
        content = f"\n--- ERROR READING FILE: {file_path} ---\nError: {str(e)}\n--- END FILE ---\n"
        tokens = estimate_tokens(content)
        logger.debug(f"[FILES] Returning error content for {file_path}: {tokens} tokens")
        return content, tokens


def read_files(
    file_paths: list[str],
    code: Optional[str] = None,
    max_tokens: Optional[int] = None,
    reserve_tokens: int = 50_000,
    *,
    include_line_numbers: bool = False,
) -> str:
    """
    Read multiple files and optional direct code with smart token management.

    This function implements intelligent token budgeting to maximize the amount
    of relevant content that can be included in an AI prompt while staying
    within token limits. It prioritizes direct code and reads files until
    the token budget is exhausted.

    Args:
        file_paths: List of file or directory paths (absolute paths required)
        code: Optional direct code to include (prioritized over files)
        max_tokens: Maximum tokens to use (defaults to DEFAULT_CONTEXT_WINDOW)
        reserve_tokens: Tokens to reserve for prompt and response (default 50K)
        include_line_numbers: Whether to add line numbers to file content

    Returns:
        str: All file contents formatted for AI consumption
    """
    if max_tokens is None:
        max_tokens = DEFAULT_CONTEXT_WINDOW

    logger.debug(f"[FILES] read_files called with {len(file_paths)} paths")
    logger.debug(
        f"[FILES] Token budget: max={max_tokens:,}, reserve={reserve_tokens:,}, available={max_tokens - reserve_tokens:,}"
    )

    content_parts = []
    total_tokens = 0
    available_tokens = max_tokens - reserve_tokens

    files_skipped = []

    # Priority 1: Handle direct code if provided
    # Direct code is prioritized because it's explicitly provided by the user
    if code:
        formatted_code = f"\n--- BEGIN DIRECT CODE ---\n{code}\n--- END DIRECT CODE ---\n"
        code_tokens = estimate_tokens(formatted_code)

        if code_tokens <= available_tokens:
            content_parts.append(formatted_code)
            total_tokens += code_tokens
            available_tokens -= code_tokens

    # Priority 2: Process file paths
    if file_paths:
        # Expand directories to get all individual files
        logger.debug(f"[FILES] Expanding {len(file_paths)} file paths")
        all_files = expand_paths(file_paths)
        logger.debug(f"[FILES] After expansion: {len(all_files)} individual files")

        if not all_files and file_paths:
            # No files found but paths were provided
            logger.debug("[FILES] No files found from provided paths")
            content_parts.append(f"\n--- NO FILES FOUND ---\nProvided paths: {', '.join(file_paths)}\n--- END ---\n")
        else:
            # Read files sequentially until token limit is reached
            logger.debug(f"[FILES] Reading {len(all_files)} files with token budget {available_tokens:,}")
            for i, file_path in enumerate(all_files):
                if total_tokens >= available_tokens:
                    logger.debug(f"[FILES] Token budget exhausted, skipping remaining {len(all_files) - i} files")
                    files_skipped.extend(all_files[i:])
                    break

                file_content, file_tokens = read_file_content(file_path, include_line_numbers=include_line_numbers)
                logger.debug(f"[FILES] File {file_path}: {file_tokens:,} tokens")

                # Check if adding this file would exceed limit
                if total_tokens + file_tokens <= available_tokens:
                    content_parts.append(file_content)
                    total_tokens += file_tokens
                    logger.debug(f"[FILES] Added file {file_path}, total tokens: {total_tokens:,}")
                else:
                    # File too large for remaining budget
                    logger.debug(
                        f"[FILES] File {file_path} too large for remaining budget ({file_tokens:,} tokens, {available_tokens - total_tokens:,} remaining)"
                    )
                    files_skipped.append(file_path)

    # Add informative note about skipped files to help users understand
    # what was omitted and why
    if files_skipped:
        logger.debug(f"[FILES] {len(files_skipped)} files skipped due to token limits")
        skip_note = "\n\n--- SKIPPED FILES (TOKEN LIMIT) ---\n"
        skip_note += f"Total skipped: {len(files_skipped)}\n"
        # Show first 10 skipped files as examples
        for _i, file_path in enumerate(files_skipped[:10]):
            skip_note += f"  - {file_path}\n"
        if len(files_skipped) > 10:
            skip_note += f"  ... and {len(files_skipped) - 10} more\n"
        skip_note += "--- END SKIPPED FILES ---\n"
        content_parts.append(skip_note)

    result = "\n\n".join(content_parts) if content_parts else ""
    logger.debug(f"[FILES] read_files complete: {len(result)} chars, {total_tokens:,} tokens used")
    return result

