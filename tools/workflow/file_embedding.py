"""
File Embedding Mixin for Workflow Tools

This module provides context-aware file selection, token budget allocation,
deduplication, and file content preparation for workflow tools.

Key Features:
- Context-aware file embedding (intermediate vs final steps)
- Token budget allocation and management
- File deduplication across conversation history
- Newest-first file selection strategy
- Expert analysis file preparation
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class FileEmbeddingMixin:
    """
    Mixin providing file embedding and context management for workflow tools.
    
    This class handles intelligent file embedding based on workflow phase,
    token budgeting, and conversation history awareness.
    """
    
    def _prepare_file_content_for_prompt(
        self, files: list[str], continuation_id: Optional[str], purpose: str,
        remaining_budget: Optional[int], arguments: dict, model_context
    ) -> tuple[str, list[str]]:
        """Prepare file content with token budgeting (from BaseTool)."""
        pass
    
    # ================================================================================
    # Expert Analysis File Preparation
    # ================================================================================
    
    def _prepare_files_for_expert_analysis(self) -> str:
        """
        Prepare file content for expert analysis.
        
        EXPERT ANALYSIS REQUIRES ACTUAL FILE CONTENT:
        Expert analysis needs actual file content of all unique files marked as relevant
        throughout the workflow, regardless of conversation history optimization.
        
        SIMPLIFIED LOGIC:
        Expert analysis gets all unique files from relevant_files across the entire workflow.
        This includes:
        - Current step's relevant_files (consolidated_findings.relevant_files)
        - Plus any additional relevant_files from conversation history (if continued workflow)
        
        This ensures expert analysis has complete context without including irrelevant files.
        """
        all_relevant_files = set()
        
        # 1. Get files from current consolidated relevant_files
        all_relevant_files.update(self.consolidated_findings.relevant_files)  # type: ignore
        
        # 2. Get additional relevant_files from conversation history (if continued workflow)
        try:
            current_arguments = self.get_current_arguments()
            if current_arguments:
                continuation_id = current_arguments.get("continuation_id")
                
                if continuation_id:
                    from utils.conversation_memory import get_conversation_file_list, get_thread
                    
                    thread_context = get_thread(continuation_id)
                    if thread_context:
                        # Get all files from conversation (these were relevant_files in previous steps)
                        conversation_files = get_conversation_file_list(thread_context)
                        all_relevant_files.update(conversation_files)
                        logger.debug(
                            f"[WORKFLOW_FILES] {self.get_name()}: Added {len(conversation_files)} files from conversation history"
                        )
        except Exception as e:
            logger.warning(f"[WORKFLOW_FILES] {self.get_name()}: Could not get conversation files: {e}")
        
        # Convert to list and remove any empty/None values
        files_for_expert = [f for f in all_relevant_files if f and f.strip()]
        
        if not files_for_expert:
            logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: No relevant files found for expert analysis")
            return ""
        
        # Expert analysis needs actual file content, bypassing conversation optimization
        try:
            file_content, processed_files = self._force_embed_files_for_expert_analysis(files_for_expert)
            
            logger.info(
                f"[WORKFLOW_FILES] {self.get_name()}: Prepared {len(processed_files)} unique relevant files for expert analysis "
                f"(from {len(self.consolidated_findings.relevant_files)} current relevant files)"  # type: ignore
            )
            
            return file_content
        
        except Exception as e:
            logger.error(f"[WORKFLOW_FILES] {self.get_name()}: Failed to prepare files for expert analysis: {e}")
            return ""
    
    def _force_embed_files_for_expert_analysis(self, files: list[str]) -> tuple[str, list[str]]:
        """
        Force embed files for expert analysis, bypassing conversation history filtering.
        
        Expert analysis has different requirements than normal workflow steps:
        - Normal steps: Optimize tokens by skipping files in conversation history
        - Expert analysis: Needs actual file content regardless of conversation history
        
        Args:
            files: List of file paths to embed
        
        Returns:
            tuple[str, list[str]]: (file_content, processed_files)
        """
        # Use read_files directly with token budgeting, bypassing filter_new_files
        from utils.file_utils import expand_paths, read_files
        
        # Get token budget for files
        current_model_context = self.get_current_model_context()
        if current_model_context:
            try:
                token_allocation = current_model_context.calculate_token_allocation()
                max_tokens = token_allocation.file_tokens
                logger.debug(
                    f"[WORKFLOW_FILES] {self.get_name()}: Using {max_tokens:,} tokens for expert analysis files"
                )
            except Exception as e:
                logger.warning(f"[WORKFLOW_FILES] {self.get_name()}: Failed to get token allocation: {e}")
                max_tokens = 100_000  # Fallback
        else:
            max_tokens = 100_000  # Fallback
        
        # Read files directly without conversation history filtering
        logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: Force embedding {len(files)} files for expert analysis")
        file_content = read_files(
            files,
            max_tokens=max_tokens,
            reserve_tokens=1000,
            include_line_numbers=self.wants_line_numbers_by_default(),
        )
        
        # Expand paths to get individual files for tracking
        processed_files = expand_paths(files)
        
        logger.debug(
            f"[WORKFLOW_FILES] {self.get_name()}: Expert analysis embedding: {len(processed_files)} files, "
            f"{len(file_content):,} characters"
        )
        
        return file_content, processed_files
    
    def wants_line_numbers_by_default(self) -> bool:
        """
        Whether this tool wants line numbers in file content by default.
        Override this to customize line number behavior.
        """
        return True  # Most workflow tools benefit from line numbers for analysis
    
    def _add_files_to_expert_context(self, expert_context: str, file_content: str) -> str:
        """
        Add file content to the expert context.
        Override this to customize how files are added to the context.
        """
        return f"{expert_context}\n\n=== ESSENTIAL FILES ===\n{file_content}\n=== END ESSENTIAL FILES ==="
    
    # ================================================================================
    # Context-Aware File Embedding - Core Implementation
    # ================================================================================
    
    def _handle_workflow_file_context(self, request: Any, arguments: dict[str, Any]) -> None:
        """
        Handle file context appropriately based on workflow phase.

        CONTEXT-AWARE FILE EMBEDDING STRATEGY:
        1. Intermediate steps + continuation: Only reference file names (save AI assistant's context)
        2. Final step: Embed full file content for expert analysis
        3. Expert analysis: Always embed relevant files with token budgeting

        This prevents wasting the AI assistant's limited context on intermediate steps while ensuring
        the final expert analysis has complete file context.
        """
        continuation_id = self.get_request_continuation_id(request)
        is_final_step = not self.get_request_next_step_required(request)
        step_number = self.get_request_step_number(request)
        
        # Extract model context for token budgeting
        model_context = arguments.get("_model_context")
        self._model_context = model_context  # type: ignore
        
        # Clear any previous file context to ensure clean state
        self._embedded_file_content = ""  # type: ignore
        self._file_reference_note = ""  # type: ignore
        self._actually_processed_files = []  # type: ignore
        
        # Determine if we should embed files or just reference them
        should_embed_files = self._should_embed_files_in_workflow_step(step_number, continuation_id, is_final_step)
        
        if should_embed_files:
            # Final step or expert analysis - embed full file content
            logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: Embedding files for final step/expert analysis")
            self._embed_workflow_files(request, arguments)
        else:
            # Intermediate step with continuation - only reference file names
            logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: Only referencing file names for intermediate step")
            self._reference_workflow_files(request)
    
    def _should_embed_files_in_workflow_step(
        self, step_number: int, continuation_id: Optional[str], is_final_step: bool
    ) -> bool:
        """
        Determine whether to embed file content based on workflow context.

        CORRECT LOGIC:
        - NEVER embed files when the AI assistant is getting the next step (next_step_required=True)
        - ONLY embed files when sending to external model (next_step_required=False)

        Args:
            step_number: Current step number
            continuation_id: Thread continuation ID (None for new conversations)
            is_final_step: Whether this is the final step (next_step_required == False)
        
        Returns:
            bool: True if files should be embedded, False if only referenced
        """
        # RULE 1: Final steps (no more steps needed) - embed files for expert analysis
        if is_final_step:
            logger.debug("[WORKFLOW_FILES] Final step - will embed files for expert analysis")
            return True
        
        # RULE 2: Any intermediate step (more steps needed) - NEVER embed files
        # This includes:
        # - New conversations with next_step_required=True
        # - Steps with continuation_id and next_step_required=True
        logger.debug("[WORKFLOW_FILES] Intermediate step (more work needed) - will only reference files")
        return False

    def _embed_workflow_files(self, request: Any, arguments: dict[str, Any]) -> None:
        """
        Embed full file content for final steps and expert analysis.
        Uses proper token budgeting like existing debug.py.
        """
        # Use relevant_files as the standard field for workflow tools
        request_files = self.get_request_relevant_files(request)
        if not request_files:
            logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: No relevant_files to embed")
            return

        try:
            # Model context should be available from early validation, but might be deferred for tests
            current_model_context = self.get_current_model_context()
            if not current_model_context:
                # Try to resolve model context now (deferred from early validation)
                try:
                    model_name, model_context = self._resolve_model_context(arguments, request)
                    self._model_context = model_context  # type: ignore
                    self._current_model_name = model_name  # type: ignore
                except Exception as e:
                    logger.error(f"[WORKFLOW_FILES] {self.get_name()}: Failed to resolve model context: {e}")
                    # Create fallback model context (preserves existing test behavior)
                    from utils.model_context import ModelContext

                    model_name = self.get_request_model_name(request)
                    self._model_context = ModelContext(model_name)  # type: ignore
                    self._current_model_name = model_name  # type: ignore

            # Use the same file preparation logic as BaseTool with token budgeting
            continuation_id = self.get_request_continuation_id(request)
            remaining_tokens = arguments.get("_remaining_tokens")

            file_content, processed_files = self._prepare_file_content_for_prompt(
                request_files,
                continuation_id,
                "Workflow files for analysis",
                remaining_budget=remaining_tokens,
                arguments=arguments,
                model_context=self._model_context,  # type: ignore
            )

            # Store for use in expert analysis
            self._embedded_file_content = file_content  # type: ignore
            self._actually_processed_files = processed_files  # type: ignore

            # Update consolidated findings with the actual files processed so files_examined is accurate
            try:
                self.consolidated_findings.files_checked.update(processed_files)  # type: ignore
            except Exception:
                pass

            logger.info(
                f"[WORKFLOW_FILES] {self.get_name()}: Embedded {len(processed_files)} relevant_files for final analysis"
            )
            # If token budget forced truncation, add a concise summary of remaining files
            try:
                from utils.file_utils import expand_paths
                requested = set(expand_paths(request_files))
                embedded = set(processed_files or [])
                remaining = [f for f in requested if f not in embedded]
                if remaining:
                    logger.info(
                        f"[WORKFLOW_FILES] {self.get_name()}: Token budget excluded {len(remaining)} files; appending summary note"
                    )
                    names = [os.path.basename(f) for f in list(remaining)[:20]]
                    note = "\n\n--- NOTE: Additional files not embedded due to token budget ---\n" \
                           + "\n".join(f"  - {n}" for n in names) \
                           + ("\n  - ... (more)" if len(remaining) > 20 else "") \
                           + "\n--- END NOTE ---\n"
                    self._embedded_file_content = (self._embedded_file_content or "") + note  # type: ignore
            except Exception:
                pass

        except Exception as e:
            logger.error(f"[WORKFLOW_FILES] {self.get_name()}: Failed to embed files: {e}")
            # Continue without file embedding rather than failing
            self._embedded_file_content = ""  # type: ignore
            self._actually_processed_files = []  # type: ignore

    def _reference_workflow_files(self, request: Any) -> None:
        """
        Reference file names without embedding content for intermediate steps.
        Saves the AI assistant's context while still providing file awareness.
        """
        # Workflow tools use relevant_files, not files
        request_files = self.get_request_relevant_files(request)
        logger.debug(
            f"[WORKFLOW_FILES] {self.get_name()}: _reference_workflow_files called with {len(request_files)} relevant_files"
        )

        if not request_files:
            logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: No files to reference, skipping")
            return

        # Store file references for conversation context
        self._referenced_files = request_files  # type: ignore

        # Create a simple reference note
        file_names = [os.path.basename(f) for f in request_files]
        reference_note = (
            f"Files referenced in this step: {', '.join(file_names)}\n"
            f"(File content available via conversation history or can be discovered by the AI assistant)"
        )

        self._file_reference_note = reference_note  # type: ignore
        logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: Set _file_reference_note: {self._file_reference_note}")  # type: ignore

        logger.info(
            f"[WORKFLOW_FILES] {self.get_name()}: Referenced {len(request_files)} files without embedding content"
        )

