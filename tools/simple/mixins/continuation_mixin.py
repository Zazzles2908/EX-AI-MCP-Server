"""
Continuation Mixin for SimpleTool

Provides conversation continuation and caching functionality.
Extracted from tools/simple/base.py to improve maintainability.
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ContinuationMixin:
    """
    Mixin providing conversation continuation and caching.

    This mixin handles:
    - Conversation history management
    - Continuation offer creation
    - Thread management
    - Turn tracking

    Dependencies:
    - Requires _model_context attribute from BaseTool
    - Requires _current_model_name attribute from BaseTool
    - Requires TOOL_NAME attribute from BaseTool
    - Requires _generate_content() method from BaseTool
    """

    def _handle_conversation_history(self, request, continuation_id: Optional[str], prompt_field_value: str):
        """
        Handle conversation history for continuation.
        
        Args:
            request: The validated request object
            continuation_id: Optional continuation ID for existing conversation
            prompt_field_value: The prompt field value from request
            
        Returns:
            Tuple of (final_prompt, should_add_follow_up_instructions)
        """
        if not continuation_id:
            # New conversation - return prompt as-is, will add follow-up instructions later
            return prompt_field_value, True
            
        # Check if conversation history is already embedded
        if "=== CONVERSATION HISTORY ===" in prompt_field_value:
            # Use pre-embedded history
            logger.debug(f"{self.get_name()}: Using pre-embedded conversation history")
            return prompt_field_value, False
            
        # No embedded history - reconstruct it (for in-process calls)
        logger.debug(f"{self.get_name()}: No embedded history found, reconstructing conversation")
        
        try:
            from utils.conversation_memory import add_turn, build_conversation_history, get_thread
            
            thread_context = get_thread(continuation_id)
            
            if thread_context:
                # Add user's new input to conversation
                user_prompt = self.get_request_prompt(request)
                user_files = self.get_request_files(request)
                if user_prompt:
                    add_turn(continuation_id, "user", user_prompt, files=user_files)
                    
                    # Get updated thread context after adding the turn
                    thread_context = get_thread(continuation_id)
                    logger.debug(
                        f"{self.get_name()}: Retrieved updated thread with {len(thread_context.turns)} turns"
                    )
                
                # Build conversation history with updated thread context
                conversation_history, conversation_tokens = build_conversation_history(
                    thread_context, self._model_context
                )
                
                # Get the base prompt from the tool
                base_prompt = prompt_field_value
                
                # Combine with conversation history
                if conversation_history:
                    final_prompt = f"{conversation_history}\n\n=== NEW USER INPUT ===\n{base_prompt}"
                else:
                    final_prompt = base_prompt
                    
                return final_prompt, False
            else:
                # Thread not found, prepare normally
                logger.warning(f"Thread {continuation_id} not found, preparing prompt normally")
                return prompt_field_value, False
                
        except Exception as e:
            logger.error(f"Error handling conversation history: {e}")
            return prompt_field_value, False

    def _create_continuation_offer(self, request, model_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create continuation offer following old base.py pattern.
        
        Args:
            request: The validated request object
            model_info: Optional model information dictionary
            
        Returns:
            Dictionary with continuation offer data or None
        """
        continuation_id = self.get_request_continuation_id(request)

        try:
            from utils.conversation_memory import create_thread, get_thread
            from utils.client_info import get_current_session_fingerprint, get_cached_client_info, format_client_info

            if continuation_id:
                # Existing conversation
                thread_context = get_thread(continuation_id)
                if thread_context and thread_context.turns:
                    turn_count = len(thread_context.turns)
                    from utils.conversation_memory import MAX_CONVERSATION_TURNS

                    if turn_count >= MAX_CONVERSATION_TURNS - 1:
                        return None  # No more turns allowed

                    remaining_turns = MAX_CONVERSATION_TURNS - turn_count - 1
                    return {
                        "continuation_id": continuation_id,
                        "remaining_turns": remaining_turns,
                        "note": f"You can continue this conversation for {remaining_turns} more exchanges.",
                    }
            else:
                # New conversation - create thread and offer continuation
                # Convert request to dict for initial_context
                initial_request_dict = self.get_request_as_dict(request)

                # Compute session fingerprint and friendly client name (for scoping and UX)
                try:
                    current_args = getattr(self, "_current_arguments", {})
                    sess_fp = get_current_session_fingerprint(current_args)
                    ci = get_cached_client_info()
                    friendly = format_client_info(ci) if ci else None
                except Exception:
                    sess_fp, friendly = None, None

                new_thread_id = create_thread(
                    tool_name=self.get_name(),
                    initial_request=initial_request_dict,
                    session_fingerprint=sess_fp,
                    client_friendly_name=friendly,
                )

                # Add the initial user turn to the new thread
                from utils.conversation_memory import MAX_CONVERSATION_TURNS, add_turn

                user_prompt = self.get_request_prompt(request)
                user_files = self.get_request_files(request)
                user_images = self.get_request_images(request)

                # Add user's initial turn
                add_turn(
                    new_thread_id, "user", user_prompt, files=user_files, images=user_images, tool_name=self.get_name()
                )

                note_client = friendly or "You"
                return {
                    "continuation_id": new_thread_id,
                    "remaining_turns": MAX_CONVERSATION_TURNS - 1,
                    "note": f"{note_client} can continue this conversation for {MAX_CONVERSATION_TURNS - 1} more exchanges.",
                }
        except Exception as e:
            logger.error(f"Error creating continuation offer: {e}")
            return None

    def _create_continuation_offer_response(
        self, content: str, continuation_data: Dict[str, Any], request, model_info: Optional[Dict[str, Any]] = None
    ):
        """
        Create response with continuation offer following old base.py pattern.
        
        Args:
            content: The response content
            continuation_data: Continuation offer data
            request: The validated request object
            model_info: Optional model information dictionary
            
        Returns:
            ToolOutput with continuation offer
        """
        from tools.models import ContinuationOffer, ToolOutput

        try:
            continuation_offer = ContinuationOffer(
                continuation_id=continuation_data["continuation_id"],
                note=continuation_data["note"],
                remaining_turns=continuation_data["remaining_turns"],
            )

            # Build metadata with model and provider info
            metadata = {"tool_name": self.get_name(), "conversation_ready": True}
            if model_info:
                model_name = model_info.get("model_name")
                if model_name:
                    metadata["model_used"] = model_name
                provider = model_info.get("provider")
                if provider:
                    # Handle both provider objects and string values
                    if isinstance(provider, str):
                        metadata["provider_used"] = provider
                    else:
                        try:
                            metadata["provider_used"] = provider.get_provider_type().value
                        except AttributeError:
                            # Fallback if provider doesn't have get_provider_type method
                            metadata["provider_used"] = str(provider)

            return ToolOutput(
                status="continuation_available",
                content=content,
                content_type="text",
                continuation_offer=continuation_offer,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Error creating continuation offer response: {e}")
            # Fallback to simple success if continuation offer fails
            return ToolOutput(status="success", content=content, content_type="text")

    def _add_assistant_turn_to_conversation(self, continuation_id: str, raw_text: str, request, model_info: Optional[Dict[str, Any]] = None):
        """
        Add assistant's response to conversation memory.
        
        Args:
            continuation_id: The conversation thread ID
            raw_text: The assistant's response text
            request: The validated request object
            model_info: Optional model information dictionary
        """
        if not continuation_id:
            return
            
        try:
            from utils.conversation_memory import add_turn
            
            # Extract model metadata for conversation tracking
            model_provider = None
            model_name = None
            model_metadata = None

            if model_info:
                provider = model_info.get("provider")
                if provider:
                    # Handle both provider objects and string values
                    if isinstance(provider, str):
                        model_provider = provider
                    else:
                        try:
                            model_provider = provider.get_provider_type().value
                        except AttributeError:
                            # Fallback if provider doesn't have get_provider_type method
                            model_provider = str(provider)
                model_name = model_info.get("model_name")
                model_response = model_info.get("model_response")
                if model_response:
                    model_metadata = {"usage": model_response.usage, "metadata": model_response.metadata}

            # Only add the assistant's response to the conversation
            # The user's turn is handled elsewhere (when thread is created/continued)
            add_turn(
                continuation_id,  # thread_id as positional argument
                "assistant",  # role as positional argument
                raw_text,  # content as positional argument
                files=self.get_request_files(request),
                images=self.get_request_images(request),
                tool_name=self.get_name(),
                model_provider=model_provider,
                model_name=model_name,
                model_metadata=model_metadata,
            )
        except Exception as e:
            logger.error(f"Error adding assistant turn to conversation: {e}")

