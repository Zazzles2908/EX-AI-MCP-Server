"""
File Handling Mixin for Zen MCP Tools

This module provides conversation-aware file processing and management for tools.

Key Components:
- FileHandlingMixin: Handles file validation, deduplication, and embedding
- Conversation-aware file tracking
- Token-aware file content preparation
- File path validation and normalization

CONVERSATION-AWARE FILE PROCESSING:
This mixin implements the sophisticated dual prioritization strategy for
conversation-aware file handling across all tools:

1. FILE DEDUPLICATION WITH NEWEST-FIRST PRIORITY:
   - When same file appears in multiple conversation turns, newest reference wins
   - Prevents redundant file embedding while preserving most recent file state
   - Cross-tool file tracking ensures consistent behavior across analyze → codereview → debug

2. CONVERSATION CONTEXT INTEGRATION:
   - All tools receive enhanced prompts with conversation history
   - File references from previous turns are preserved and accessible
   - Cross-tool knowledge transfer maintains full context without manual file re-specification

3. TOKEN-AWARE FILE EMBEDDING:
   - Respects model-specific token allocation budgets from ModelContext
   - Prioritizes conversation history, then newest files, then remaining content
   - Graceful degradation when token limits are approached

4. STATELESS-TO-STATEFUL BRIDGING:
   - Tools operate on stateless MCP requests but access full conversation state
   - Conversation memory automatically injected via continuation_id parameter
   - Enables natural AI-to-AI collaboration across tool boundaries
"""

import logging
import os
from typing import Any, Optional

from config import MCP_PROMPT_SIZE_LIMIT
from utils import check_token_limit
from utils.conversation.memory import ConversationTurn, get_conversation_file_list  # Keep model and helper function
from utils.conversation.global_storage import get_thread
from utils.file.operations import read_file_content, read_files
from utils.file.size_validator import validate_and_warn  # PHASE 2.3 ENHANCEMENT (2025-10-25)

logger = logging.getLogger(__name__)


class FileHandlingMixin:
    """
    Mixin providing file handling functionality for tools.
    
    This class handles:
    - File path validation and normalization
    - Conversation-aware file deduplication
    - Token-aware file content preparation
    - File embedding with budget management
    """
    
    # ================================================================================
    # File Path Validation
    # ================================================================================
    
    def validate_file_paths(self, request) -> Optional[str]:
        """
        Validate that all file paths in the request are absolute.
        
        If EX_ALLOW_RELATIVE_PATHS=true, resolve relative paths against the project root
        (current working directory) and ensure they do not escape that root. This preserves
        security while improving UX for MCP clients.
        
        Args:
            request: The validated request object
        
        Returns:
            Optional[str]: Error message if validation fails, None if all paths are valid
        """
        # Only validate files/paths if they exist in the request
        file_fields = [
            "files",
            "file",
            "path",
            "directory",
            "notebooks",
            "test_examples",
            "style_guide_examples",
            "files_checked",
            "relevant_files",
        ]
        
        # Default to true for better UX - relative paths are auto-resolved with security checks
        allow_relative = os.getenv("EX_ALLOW_RELATIVE_PATHS", "true").strip().lower() == "true"
        project_root = os.path.abspath(os.getcwd())
        
        for field_name in file_fields:
            if hasattr(request, field_name):
                field_value = getattr(request, field_name)
                if field_value is None:
                    continue
                
                # Handle both single paths and lists of paths
                is_list = isinstance(field_value, list)
                paths_to_check = field_value if is_list else [field_value]
                normalized: list[str] = []
                
                for path in paths_to_check:
                    if not path:
                        normalized.append(path)
                        continue
                    if os.path.isabs(path):
                        # Already absolute - keep as is
                        normalized.append(path)
                    else:
                        if not allow_relative:
                            return f"All file paths must be FULL absolute paths. Invalid path: '{path}'"
                        # Resolve relative path against project root and ensure containment
                        abs_p = os.path.abspath(os.path.join(project_root, path))
                        if not abs_p.startswith(project_root):
                            return f"Relative path escapes project root: '{path}'"
                        normalized.append(abs_p)
                
                # Write back normalized values to the request model for downstream consumers
                try:
                    setattr(request, field_name, normalized if is_list else (normalized[0] if normalized else field_value))
                except Exception:
                    # If we cannot set, we still validated; but prefer not to fail here
                    pass
        
        return None
    
    def _validate_token_limit(self, content: str, content_type: str = "Content") -> None:
        """
        Validate that content doesn't exceed the MCP prompt size limit.
        
        Args:
            content: The content to validate
            content_type: Description of the content type for error messages
        
        Raises:
            ValueError: If content exceeds size limit
        """
        is_valid, token_count = check_token_limit(content, MCP_PROMPT_SIZE_LIMIT)
        if not is_valid:
            error_msg = f"~{token_count:,} tokens. Maximum is {MCP_PROMPT_SIZE_LIMIT:,} tokens."
            logger.error(f"{self.name} tool {content_type.lower()} validation failed: {error_msg}")
            raise ValueError(f"{content_type} too large: {error_msg}")
        
        logger.debug(f"{self.name} tool {content_type.lower()} token validation passed: {token_count:,} tokens")
    
    # ================================================================================
    # Conversation-Aware File Tracking
    # ================================================================================
    
    def get_conversation_embedded_files(self, continuation_id: Optional[str]) -> list[str]:
        """
        Get list of files already embedded in conversation history.
        
        This method returns the list of files that have already been embedded
        in the conversation history for a given continuation thread. Tools can
        use this to avoid re-embedding files that are already available in the
        conversation context.
        
        Args:
            continuation_id: Thread continuation ID, or None for new conversations
        
        Returns:
            list[str]: List of file paths already embedded in conversation history
        """
        if not continuation_id:
            # New conversation, no files embedded yet
            return []
        
        thread_context = get_thread(continuation_id)
        if not thread_context:
            # Thread not found, no files embedded
            return []
        
        embedded_files = get_conversation_file_list(thread_context)
        logger.debug(f"[FILES] {self.name}: Found {len(embedded_files)} embedded files")
        return embedded_files
    
    def filter_new_files(self, requested_files: list[str], continuation_id: Optional[str]) -> list[str]:
        """
        Filter out files that are already embedded in conversation history.
        
        This method prevents duplicate file embeddings by filtering out files that have
        already been embedded in the conversation history. This optimizes token usage
        while ensuring tools still have logical access to all requested files through
        conversation history references.
        
        Args:
            requested_files: List of files requested for current tool execution
            continuation_id: Thread continuation ID, or None for new conversations
        
        Returns:
            list[str]: List of files that need to be embedded (not already in history)
        """
        logger.debug(f"[FILES] {self.name}: Filtering {len(requested_files)} requested files")
        
        if not continuation_id:
            # New conversation, all files are new
            logger.debug(f"[FILES] {self.name}: New conversation, all {len(requested_files)} files are new")
            return requested_files
        
        try:
            embedded_files = set(self.get_conversation_embedded_files(continuation_id))
            logger.debug(f"[FILES] {self.name}: Found {len(embedded_files)} embedded files in conversation")
            
            # Safety check: If no files are marked as embedded but we have a continuation_id,
            # this might indicate an issue with conversation history. Be conservative.
            if not embedded_files:
                logger.debug(f"{self.name} tool: No files found in conversation history for thread {continuation_id}")
                logger.debug(
                    f"[FILES] {self.name}: No embedded files found, returning all {len(requested_files)} requested files"
                )
                return requested_files
            
            # Return only files that haven't been embedded yet
            new_files = [f for f in requested_files if f not in embedded_files]
            logger.debug(
                f"[FILES] {self.name}: After filtering: {len(new_files)} new files, {len(requested_files) - len(new_files)} already embedded"
            )
            logger.debug(f"[FILES] {self.name}: New files to embed: {new_files}")
            
            # Log filtering results for debugging
            if len(new_files) < len(requested_files):
                skipped = [f for f in requested_files if f in embedded_files]
                logger.debug(
                    f"{self.name} tool: Filtering {len(skipped)} files already in conversation history: {', '.join(skipped)}"
                )
                logger.debug(f"[FILES] {self.name}: Skipped (already embedded): {skipped}")
            
            return new_files
        
        except Exception as e:
            # If there's any issue with conversation history lookup, be conservative
            # and include all files rather than risk losing access to needed files
            logger.warning(f"{self.name} tool: Error checking conversation history for {continuation_id}: {e}")
            logger.warning(f"{self.name} tool: Including all requested files as fallback")
            logger.debug(
                f"[FILES] {self.name}: Exception in filter_new_files, returning all {len(requested_files)} files as fallback"
            )
            return requested_files
    
    def format_conversation_turn(self, turn: ConversationTurn) -> list[str]:
        """
        Format a conversation turn for display in conversation history.
        
        Tools can override this to provide custom formatting for their responses
        while maintaining the standard structure for cross-tool compatibility.
        
        This method is called by build_conversation_history when reconstructing
        conversation context, allowing each tool to control how its responses
        appear in subsequent conversation turns.
        
        Args:
            turn: The conversation turn to format (from utils.conversation_memory)
        
        Returns:
            list[str]: Lines of formatted content for this turn
        
        Example:
            Default implementation returns:
            ["Files used in this turn: file1.py, file2.py", "", "Response content..."]
            
            Tools can override to add custom sections, formatting, or metadata display.
        """
        parts = []
        
        # Add files context if present
        if turn.files:
            parts.append(f"Files used in this turn: {', '.join(turn.files)}")
            parts.append("")  # Empty line for readability
        
        # Add the actual content
        parts.append(turn.content)

        return parts

    # ================================================================================
    # Prompt File Handling
    # ================================================================================

    def handle_prompt_file(self, files: Optional[list[str]]) -> tuple[Optional[str], Optional[list[str]]]:
        """
        Check for and handle prompt.txt in the files list.

        If prompt.txt is found, reads its content and removes it from the files list.
        This file is treated specially as the main prompt, not as an embedded file.

        This mechanism allows us to work around MCP's ~25K token limit by having
        the MCP client save large prompts to a file, effectively using the file transfer
        mechanism to bypass token constraints while preserving response capacity.

        Args:
            files: List of file paths (will be translated for current environment)

        Returns:
            tuple: (prompt_content, updated_files_list)
        """
        if not files:
            return None, files

        prompt_content = None
        updated_files = []

        for file_path in files:

            # Check if the filename is exactly "prompt.txt"
            # This ensures we don't match files like "myprompt.txt" or "prompt.txt.bak"
            if os.path.basename(file_path) == "prompt.txt":
                try:
                    # Read prompt.txt content and extract just the text
                    content, _ = read_file_content(file_path)
                    # Extract the content between the file markers
                    if "--- BEGIN FILE:" in content and "--- END FILE:" in content:
                        lines = content.split("\n")
                        in_content = False
                        content_lines = []
                        for line in lines:
                            if line.startswith("--- BEGIN FILE:"):
                                in_content = True
                                continue
                            elif line.startswith("--- END FILE:"):
                                break
                            elif in_content:
                                content_lines.append(line)
                        prompt_content = "\n".join(content_lines)
                    else:
                        # Fallback: if it's already raw content (from tests or direct input)
                        # and doesn't have error markers, use it directly
                        if not content.startswith("\n--- ERROR"):
                            prompt_content = content
                        else:
                            prompt_content = None
                except Exception:
                    # If we can't read the file, we'll just skip it
                    # The error will be handled elsewhere
                    pass
            else:
                # Keep the original path in the files list (will be translated later by read_files)
                updated_files.append(file_path)

        return prompt_content, updated_files if updated_files else None

    def get_prompt_content_for_size_validation(self, user_content: str) -> str:
        """
        Get the content that should be validated for MCP prompt size limits.

        This hook method allows tools to specify what content should be checked
        against the MCP transport size limit. By default, it returns the user content,
        but can be overridden to exclude conversation history when needed.

        Args:
            user_content: The user content that would normally be validated

        Returns:
            The content that should actually be validated for size limits
        """
        # Default implementation: validate the full user content
        return user_content

    def check_prompt_size(self, text: str) -> Optional[dict[str, Any]]:
        """
        Check if USER INPUT text is too large for MCP transport boundary.

        IMPORTANT: This method should ONLY be used to validate user input that crosses
        the client ↔ MCP Server transport boundary. It should NOT be used to limit
        internal MCP Server operations.

        Args:
            text: The user input text to check (NOT internal prompt content)

        Returns:
            Optional[dict[str, Any]]: Response asking for file handling if too large, None otherwise
        """
        if text and len(text) > MCP_PROMPT_SIZE_LIMIT:
            return {
                "status": "resend_prompt",
                "content": (
                    f"MANDATORY ACTION REQUIRED: The prompt is too large for MCP's token limits (>{MCP_PROMPT_SIZE_LIMIT:,} characters). "
                    "YOU MUST IMMEDIATELY save the prompt text to a temporary file named 'prompt.txt' in the working directory. "
                    "DO NOT attempt to shorten or modify the prompt. SAVE IT AS-IS to 'prompt.txt'. "
                    "Then resend the request with the absolute file path to 'prompt.txt' in the files parameter (must be FULL absolute path - DO NOT SHORTEN), "
                    "along with any other files you wish to share as context. Leave the prompt text itself empty or very brief in the new request. "
                    "This is the ONLY way to handle large prompts - you MUST follow these exact steps."
                ),
                "content_type": "text",
                "metadata": {
                    "prompt_size": len(text),
                    "limit": MCP_PROMPT_SIZE_LIMIT,
                    "instructions": "MANDATORY: Save prompt to 'prompt.txt' in current folder and include absolute path in files parameter. DO NOT modify or shorten the prompt.",
                },
            }
        return None

    # ================================================================================
    # File Content Preparation
    # ================================================================================

    def _prepare_file_content_for_prompt(
        self,
        request_files: list[str],
        continuation_id: Optional[str],
        context_description: str = "New files",
        max_tokens: Optional[int] = None,
        reserve_tokens: int = 1_000,
        remaining_budget: Optional[int] = None,
        arguments: Optional[dict] = None,
        model_context: Optional[Any] = None,
    ) -> tuple[str, list[str]]:
        """
        Centralized file processing implementing dual prioritization strategy.

        This method is the heart of conversation-aware file processing across all tools.

        Args:
            request_files: List of files requested for current tool execution
            continuation_id: Thread continuation ID, or None for new conversations
            context_description: Description for token limit validation (e.g. "Code", "New files")
            max_tokens: Maximum tokens to use (defaults to remaining budget or model-specific content allocation)
            reserve_tokens: Tokens to reserve for additional prompt content (default 1K)
            remaining_budget: Remaining token budget after conversation history (from server.py)
            arguments: Original tool arguments (used to extract _remaining_tokens if available)
            model_context: Model context object with all model information including token allocation

        Returns:
            tuple[str, list[str]]: (formatted_file_content, actually_processed_files)
                - formatted_file_content: Formatted file content string ready for prompt inclusion
                - actually_processed_files: List of individual file paths that were actually read and embedded
                  (directories are expanded to individual files)
        """
        if not request_files:
            return "", []

        # PHASE 2.3 ENHANCEMENT (2025-10-25): Validate file sizes and warn if >5KB
        # This helps agents discover kimi_upload_files workflow for token savings
        size_warning = validate_and_warn(request_files, tool_name=self.name)
        if size_warning:
            logger.info(f"[FILE_SIZE] {self.name}: {size_warning}")
            # Note: Warning is logged but not returned to avoid breaking existing behavior
            # Future enhancement: Include warning in tool response metadata

        # Extract remaining budget from arguments if available
        if remaining_budget is None:
            # Use provided arguments or fall back to stored arguments from execute()
            args_to_use = arguments or getattr(self, "_current_arguments", {})
            remaining_budget = args_to_use.get("_remaining_tokens")

        # Use remaining budget if provided, otherwise fall back to max_tokens or model-specific default
        if remaining_budget is not None:
            effective_max_tokens = remaining_budget - reserve_tokens
        elif max_tokens is not None:
            effective_max_tokens = max_tokens - reserve_tokens
        else:
            # Use model_context for token allocation
            if not model_context:
                # Try to get from stored attributes as fallback
                model_context = getattr(self, "_model_context", None)
                if not model_context:
                    logger.error(
                        f"[FILES] {self.name}: _prepare_file_content_for_prompt called without model_context. "
                        "This indicates an incorrect call sequence in the tool's implementation."
                    )
                    raise RuntimeError("Model context not provided for file preparation.")

            # This is now the single source of truth for token allocation.
            try:
                token_allocation = model_context.calculate_token_allocation()
                # Standardize on `file_tokens` for consistency and correctness.
                effective_max_tokens = token_allocation.file_tokens - reserve_tokens
                logger.debug(
                    f"[FILES] {self.name}: Using model context for {model_context.model_name}: "
                    f"{token_allocation.file_tokens:,} file tokens from {token_allocation.total_tokens:,} total"
                )
            except Exception as e:
                logger.error(
                    f"[FILES] {self.name}: Failed to calculate token allocation from model context: {e}", exc_info=True
                )
                # If the context exists but calculation fails, we still need to prevent a crash.
                # A loud error is logged, and we fall back to a safe default.
                effective_max_tokens = 100_000 - reserve_tokens

        # Ensure we have a reasonable minimum budget
        effective_max_tokens = max(1000, effective_max_tokens)

        files_to_embed = self.filter_new_files(request_files, continuation_id)
        logger.debug(f"[FILES] {self.name}: Will embed {len(files_to_embed)} files after filtering")

        # Log the specific files for debugging/testing
        if files_to_embed:
            logger.info(
                f"[FILE_PROCESSING] {self.name} tool will embed new files: {', '.join([os.path.basename(f) for f in files_to_embed])}"
            )
        else:
            logger.info(
                f"[FILE_PROCESSING] {self.name} tool: No new files to embed (all files already in conversation history)"
            )

        content_parts = []
        actually_processed_files = []

        # Read content of new files only
        if files_to_embed:
            logger.debug(f"{self.name} tool embedding {len(files_to_embed)} new files: {', '.join(files_to_embed)}")
            logger.debug(
                f"[FILES] {self.name}: Starting file embedding with token budget {effective_max_tokens + reserve_tokens:,}"
            )
            try:
                # Before calling read_files, expand directories to get individual file paths
                from utils.file.operations import expand_paths

                expanded_files = expand_paths(files_to_embed)
                logger.debug(
                    f"[FILES] {self.name}: Expanded {len(files_to_embed)} paths to {len(expanded_files)} individual files"
                )

                file_content = read_files(
                    files_to_embed,
                    max_tokens=effective_max_tokens + reserve_tokens,
                    reserve_tokens=reserve_tokens,
                    include_line_numbers=self.wants_line_numbers_by_default(),
                )
                self._validate_token_limit(file_content, context_description)
                content_parts.append(file_content)

                # Track the expanded files as actually processed
                actually_processed_files.extend(expanded_files)

                # Estimate tokens for debug logging
                from utils.model.token_utils import estimate_tokens

                content_tokens = estimate_tokens(file_content)
                logger.debug(
                    f"{self.name} tool successfully embedded {len(files_to_embed)} files ({content_tokens:,} tokens)"
                )
                logger.debug(f"[FILES] {self.name}: Successfully embedded files - {content_tokens:,} tokens used")
                logger.debug(
                    f"[FILES] {self.name}: Actually processed {len(actually_processed_files)} individual files"
                )
            except Exception as e:
                logger.error(f"{self.name} tool failed to embed files {files_to_embed}: {type(e).__name__}: {e}")
                logger.debug(f"[FILES] {self.name}: File embedding failed - {type(e).__name__}: {e}")
                raise
        else:
            logger.debug(f"[FILES] {self.name}: No files to embed after filtering")

        # Generate note about files already in conversation history
        if continuation_id and len(files_to_embed) < len(request_files):
            embedded_files = self.get_conversation_embedded_files(continuation_id)
            skipped_files = [f for f in request_files if f in embedded_files]
            if skipped_files:
                logger.debug(
                    f"{self.name} tool skipping {len(skipped_files)} files already in conversation history: {', '.join(skipped_files)}"
                )
                logger.debug(f"[FILES] {self.name}: Adding note about {len(skipped_files)} skipped files")
                if content_parts:
                    content_parts.append("\n\n")
                note_lines = [
                    "--- NOTE: Additional files referenced in conversation history ---",
                    "The following files are already available in our conversation context:",
                    "\n".join(f"  - {f}" for f in skipped_files),
                    "--- END NOTE ---",
                ]
                content_parts.append("\n".join(note_lines))
            else:
                logger.debug(f"[FILES] {self.name}: No skipped files to note")

        result = "".join(content_parts) if content_parts else ""
        logger.debug(
            f"[FILES] {self.name}: _prepare_file_content_for_prompt returning {len(result)} chars, {len(actually_processed_files)} processed files"
        )
        return result, actually_processed_files

