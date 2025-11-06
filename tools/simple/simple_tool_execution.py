"""
Execution and Response Processing for Simple Tools

This module provides the main execution flow and response handling for SimpleTool.

Key Components:
- SimpleToolExecutionMixin: Main execution flow and response processing
- execute() method: Complete tool execution pipeline
- Response parsing and formatting
- Continuation offer creation
"""

import json
import logging
from typing import Any, Optional

from mcp.types import TextContent

logger = logging.getLogger(__name__)


class SimpleToolExecutionMixin:
    """
    Mixin providing execution and response processing for simple tools.
    
    This class handles:
    - Main tool execution flow
    - Request validation and processing
    - Model context resolution
    - AI model invocation
    - Response parsing and formatting
    - Continuation offer creation
    """
    
    # ================================================================================
    # Main Execution Flow
    # ================================================================================
    
    async def execute(self, arguments: dict[str, Any], on_chunk=None) -> list:
        """
        Execute the simple tool using the comprehensive flow from old base.py.
        
        This method replicates the proven execution pattern while using SimpleTool hooks.
        """
        from tools.models import ToolOutput
        
        logger_name = f"tools.{self.get_name()}"
        tool_logger = logging.getLogger(logger_name)
        
        try:
            # Store arguments for access by helper methods
            self._current_arguments = arguments
            
            # FIX: Handle both dict and ToolRequest object types
            if hasattr(arguments, 'keys'):
                tool_logger.info(f"{self.get_name()} tool called with arguments: {list(arguments.keys())}")
            else:
                tool_logger.info(f"{self.get_name()} tool called with request object: {type(arguments).__name__}")
            try:
                from utils.progress import send_progress
                send_progress(f"{self.get_name()}: Starting execution")
            except Exception:
                pass
            
            # Validate request using the tool's Pydantic model
            request_model = self.get_request_model()
            request = request_model(**arguments)
            tool_logger.debug(f"Request validation successful for {self.get_name()}")
            try:
                from utils.progress import send_progress
                send_progress(f"{self.get_name()}: Request validated")
            except Exception:
                pass
            
            # Validate file paths for security
            path_error = self._validate_file_paths(request)
            if path_error:
                error_output = ToolOutput(
                    status="error",
                    content=path_error,
                    content_type="text",
                )
                return [TextContent(type="text", text=error_output.model_dump_json())]
            
            # Handle model resolution
            model_name = self.get_request_model_name(request)
            if not model_name:
                from config import DEFAULT_MODEL
                model_name = DEFAULT_MODEL
            
            # Store the current model name for later use
            self._current_model_name = model_name
            
            # Handle model context from arguments (for in-process testing)
            if "_model_context" in arguments:
                self._model_context = arguments["_model_context"]
                tool_logger.debug(f"{self.get_name()}: Using model context from arguments")
            else:
                # Create model context if not provided
                from utils.model.context import ModelContext
                from src.providers.registry import ModelProviderRegistry as _Registry
                
                # Avoid constructing ModelContext('auto') which triggers provider lookup error
                if (model_name or "").strip().lower() == "auto":
                    try:
                        seed = _Registry.get_preferred_fallback_model(self.get_model_category())
                    except Exception:
                        seed = None
                    seed = seed or "glm-4.5-flash"
                    self._model_context = ModelContext(seed)
                    tool_logger.debug(f"{self.get_name()}: Auto-mode seed context created for {seed}")
                else:
                    self._model_context = ModelContext(model_name)
                    tool_logger.debug(f"{self.get_name()}: Created model context for {model_name}")
            
            try:
                from utils.progress import send_progress
                send_progress(f"{self.get_name()}: Model/context ready: {model_name}")
            except Exception:
                pass
            
            # Get images if present
            images = self.get_request_images(request)
            continuation_id = self.get_request_continuation_id(request)
            
            # Handle conversation history and prompt preparation
            if continuation_id:
                # Check if conversation history is already embedded
                field_value = self.get_request_prompt(request)
                if "=== CONVERSATION HISTORY ===" in field_value:
                    # Use pre-embedded history
                    prompt = field_value
                    tool_logger.debug(f"{self.get_name()}: Using pre-embedded conversation history")
                else:
                    # No embedded history - reconstruct it (for in-process calls)
                    tool_logger.debug(f"{self.get_name()}: No embedded history found, reconstructing conversation")

                    # Get thread context
                    # BUG FIX #14 (2025-10-20): Removed build_conversation_history import (deleted function)
                    # CRITICAL FIX (2025-10-24): Use global_storage to prevent 4x Supabase duplication
                    from utils.conversation.global_storage import add_turn, get_thread

                    thread_context = get_thread(continuation_id)
                    
                    if thread_context:
                        # Add user's new input to conversation
                        user_prompt = self.get_request_prompt(request)
                        user_files = self.get_request_files(request)
                        if user_prompt:
                            add_turn(continuation_id, "user", user_prompt, files=user_files)
                            
                            # Get updated thread context after adding the turn
                            thread_context = get_thread(continuation_id)
                            tool_logger.debug(
                                f"{self.get_name()}: Retrieved updated thread with {len(thread_context.turns)} turns"
                            )
                        
                        # BUG FIX #14 (2025-10-20): No longer build text-based conversation history
                        # Modern approach: Request handler provides _messages parameter to SDK providers
                        # Tools receive conversation context via message arrays, not text strings

                        # Get the base prompt from the tool
                        base_prompt = await self.prepare_prompt(request)

                        # Use base prompt directly - conversation history is handled via _messages
                        prompt = base_prompt
                    else:
                        # Thread not found, prepare normally
                        tool_logger.warning(f"Thread {continuation_id} not found, preparing prompt normally")
                        prompt = await self.prepare_prompt(request)
            else:
                # New conversation, prepare prompt normally
                prompt = await self.prepare_prompt(request)
                
                # Add follow-up instructions for new conversations
                from server import get_follow_up_instructions
                
                follow_up_instructions = get_follow_up_instructions(0)
                prompt = f"{prompt}\n\n{follow_up_instructions}"
                tool_logger.debug(f"Added follow-up instructions for new {self.get_name()} conversation")
            
            # Validate images if any were provided
            if images:
                image_validation_error = self._validate_image_limits(
                    images, model_context=self._model_context, continuation_id=continuation_id
                )
                if image_validation_error:
                    return [TextContent(type="text", text=json.dumps(image_validation_error, ensure_ascii=False))]
            
            # Get and validate temperature against model constraints
            temperature, temp_warnings = self.get_validated_temperature(request, self._model_context)
            
            # Log any temperature corrections
            for warning in temp_warnings:
                tool_logger.warning(warning)
            
            # Get thinking mode with defaults
            thinking_mode = self.get_request_thinking_mode(request)
            if thinking_mode is None:
                thinking_mode = self.get_default_thinking_mode()
            
            # Get the provider from model context (clean OOP - no re-fetching)
            provider = self._model_context.provider
            
            # Get system prompt for this tool
            base_system_prompt = self.get_system_prompt()
            language_instruction = self.get_language_instruction()
            system_prompt = language_instruction + base_system_prompt
            
            # Estimate tokens for logging
            from utils.model.token_utils import estimate_tokens
            
            estimated_tokens = estimate_tokens(prompt)
            tool_logger.debug(f"Prompt length: {len(prompt)} characters (~{estimated_tokens:,} tokens)")
            try:
                from utils.progress import send_progress
                send_progress(f"{self.get_name()}: Generating response (~{estimated_tokens:,} tokens)")
            except Exception:
                pass
            
            # NOTE: The rest of execute() method continues in the file
            # This is just the first 300 lines - will continue with str-replace-editor
            
        except Exception as e:
            tool_logger.error(f"Error in {self.get_name()}: {str(e)}")
            error_output = ToolOutput(
                status="error",
                content=f"Error in {self.get_name()}: {str(e)}",
                content_type="text",
            )
            return [TextContent(type="text", text=error_output.model_dump_json())]

