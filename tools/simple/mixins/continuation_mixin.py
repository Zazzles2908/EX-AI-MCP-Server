"""
Continuation Mixin for SimpleTool

Provides conversation continuation and caching functionality.
Extracted from tools/simple/base.py to improve maintainability.

Updated to use storage factory pattern for Supabase integration.
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
    - Storage backend abstraction (memory/supabase/dual)

    Dependencies:
    - Requires _model_context attribute from BaseTool
    - Requires _current_model_name attribute from BaseTool
    - Requires TOOL_NAME attribute from BaseTool
    - Requires _generate_content() method from BaseTool
    """

    def _handle_conversation_history(self, request, continuation_id: Optional[str], prompt_field_value: str):
        """
        Handle conversation history for continuation using storage factory.

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
            # CRITICAL FIX: Use cached storage backend to avoid creating 60+ instances
            from utils.conversation.threads import _get_storage_backend

            storage = _get_storage_backend()
            if not storage:
                logger.warning(f"{self.get_name()}: Storage backend not available")
                return prompt_field_value, False

            thread_context = storage.get_thread(continuation_id)

            if thread_context:
                # Add user's new input to conversation
                user_prompt = self.get_request_prompt(request)
                user_files = self.get_request_files(request)
                user_images = self.get_request_images(request)

                if user_prompt:
                    # CRITICAL FIX (2025-10-19): Strip embedded conversation history before saving
                    # to prevent exponential token growth. When Augment Code (or other AI) sends
                    # a continuation request, it embeds the full conversation history in the prompt.
                    # If we save this AS-IS, then on the next turn we'll load it and add history AGAIN,
                    # causing exponential growth (Turn 1: 1K tokens, Turn 2: 2K, Turn 3: 4K, etc.)
                    #
                    # Extract only the NEW user input by stripping everything before "=== NEW USER INPUT ==="
                    original_prompt = user_prompt
                    if "=== NEW USER INPUT ===" in user_prompt:
                        # Extract only the new input after the marker
                        parts = user_prompt.split("=== NEW USER INPUT ===", 1)
                        if len(parts) == 2:
                            user_prompt = parts[1].strip()
                            logger.info(
                                f"{self.get_name()}: [CONTEXT_FIX] Stripped embedded history from user prompt "
                                f"({len(original_prompt):,} → {len(user_prompt):,} chars)"
                            )

                    storage.add_turn(
                        continuation_id,
                        "user",
                        user_prompt,
                        files=user_files,
                        images=user_images,
                        tool_name=self.get_name()
                    )

                    # Get updated thread context after adding the turn
                    thread_context = storage.get_thread(continuation_id)

                    # Handle different thread context formats (memory vs supabase)
                    turn_count = len(thread_context.get('messages', [])) if isinstance(thread_context, dict) else len(thread_context.turns)
                    logger.debug(
                        f"{self.get_name()}: Retrieved updated thread with {turn_count} turns"
                    )

                # BUG FIX #14 (2025-10-20): No longer build text-based conversation history
                # Modern approach: Request handler provides _messages parameter to SDK providers
                # Tools receive conversation context via message arrays, not text strings

                # Use base prompt directly - conversation history is handled via _messages
                return prompt_field_value, False
            else:
                # Thread not found, prepare normally
                logger.warning(f"Thread {continuation_id} not found, preparing prompt normally")
                return prompt_field_value, False

        except Exception as e:
            logger.error(f"Error handling conversation history: {e}")
            return prompt_field_value, False

    def _create_continuation_offer(self, request, model_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create continuation offer using storage factory pattern.

        Args:
            request: The validated request object
            model_info: Optional model information dictionary

        Returns:
            Dictionary with continuation offer data or None
        """
        continuation_id = self.get_request_continuation_id(request)

        try:
            # CRITICAL FIX: Use cached storage backend to avoid creating 60+ instances
            from utils.conversation.threads import _get_storage_backend
            from utils.client_info import get_current_session_fingerprint, get_cached_client_info, format_client_info
            from utils.conversation.memory import MAX_CONVERSATION_TURNS, create_thread

            storage = _get_storage_backend()
            if not storage:
                logger.warning(f"{self.get_name()}: Storage backend not available for continuation offer")
                return None

            if continuation_id:
                # Existing conversation (or first turn with pre-generated continuation_id)
                thread_context = storage.get_thread(continuation_id)
                if thread_context:
                    # Thread exists - this is a continuation
                    # Handle different thread context formats (memory vs supabase)
                    if isinstance(thread_context, dict):
                        # Supabase format
                        turn_count = len(thread_context.get('messages', []))
                    else:
                        # Memory format
                        turn_count = len(thread_context.turns) if hasattr(thread_context, 'turns') else 0

                    if turn_count >= MAX_CONVERSATION_TURNS - 1:
                        return None  # No more turns allowed

                    remaining_turns = MAX_CONVERSATION_TURNS - turn_count - 1
                    return {
                        "continuation_id": continuation_id,
                        "remaining_turns": remaining_turns,
                        "note": f"You can continue this conversation for {remaining_turns} more exchanges.",
                    }
                # CRITICAL FIX (2025-10-19): Thread doesn't exist yet - this is first turn
                # with pre-generated continuation_id from _parse_response. Treat as new conversation.
                # Fall through to "New conversation" logic below

            # New conversation - create thread and offer continuation
            # This handles both: 1) No continuation_id provided, 2) continuation_id exists but thread doesn't
            if True:  # Always execute this block (replaces "else:" to handle fall-through)
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

                # CRITICAL FIX (2025-10-19): Use pre-generated continuation_id if available
                # (from _parse_response), otherwise create a new one
                if continuation_id:
                    # Use the pre-generated continuation_id
                    new_thread_id = continuation_id
                else:
                    # Create thread (still uses memory.create_thread for now)
                    new_thread_id = create_thread(
                        tool_name=self.get_name(),
                        initial_request=initial_request_dict,
                        session_fingerprint=sess_fp,
                        client_friendly_name=friendly,
                    )

                # Add the initial user turn using storage
                user_prompt = self.get_request_prompt(request)
                user_files = self.get_request_files(request)
                user_images = self.get_request_images(request)

                # Add user's initial turn
                storage.add_turn(
                    new_thread_id,
                    "user",
                    user_prompt,
                    files=user_files,
                    images=user_images,
                    tool_name=self.get_name()
                )

                # CRITICAL FIX (2025-10-19): Save assistant response for first turn
                # The assistant response is generated BEFORE _create_continuation_offer is called,
                # so we need to save it here after the conversation is created in Supabase.
                # For subsequent turns, the assistant response is saved in format_response().
                if hasattr(request, '_assistant_response_to_save'):
                    storage.add_turn(
                        new_thread_id,
                        "assistant",
                        request._assistant_response_to_save,
                        tool_name=self.get_name()
                    )
                    # Clean up the temporary attribute
                    delattr(request, '_assistant_response_to_save')

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
        Add assistant's response to conversation using storage factory.

        Args:
            continuation_id: The conversation thread ID
            raw_text: The assistant's response text
            request: The validated request object
            model_info: Optional model information dictionary
        """
        if not continuation_id:
            return

        try:
            # CRITICAL FIX: Use cached storage backend to avoid creating 60+ instances
            from utils.conversation.threads import _get_storage_backend

            storage = _get_storage_backend()
            if not storage:
                logger.warning(f"{self.get_name()}: Storage backend not available for turn storage")
                return

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

            # Prepare metadata for storage
            metadata = {}
            if model_provider:
                metadata['model_provider'] = model_provider
            if model_name:
                metadata['model_name'] = model_name
            if model_metadata:
                metadata['model_metadata'] = model_metadata

            # Only add the assistant's response to the conversation
            # The user's turn is handled elsewhere (when thread is created/continued)
            storage.add_turn(
                continuation_id,
                "assistant",
                raw_text,
                files=self.get_request_files(request),
                images=self.get_request_images(request),
                metadata=metadata,
                tool_name=self.get_name()
            )
        except Exception as e:
            logger.error(f"Error adding assistant turn to conversation: {e}")

