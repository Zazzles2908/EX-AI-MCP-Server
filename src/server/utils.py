"""
Server Utility Functions

This module contains utility functions used by the MCP server
for model parsing, follow-up instructions, and other helper functionality.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def parse_model_option(model_string: str) -> tuple[str, Optional[str]]:
    """
    Parse model:option format into model name and option.

    Handles different formats:
    - OpenRouter models: preserve :free, :beta, :preview suffixes as part of model name
    - Ollama/Custom models: split on : to extract tags like :latest
    - Consensus stance: extract options like :for, :against

    Args:
        model_string: String that may contain "model:option" format

    Returns:
        tuple: (model_name, option) where option may be None
    """
    if ":" in model_string and not model_string.startswith("http"):  # Avoid parsing URLs
        # Check if this looks like an OpenRouter model (contains /)
        if "/" in model_string and model_string.count(":") == 1:
            # Could be openai/gpt-4:something - check what comes after colon
            parts = model_string.split(":", 1)
            suffix = parts[1].strip().lower()

            # Known OpenRouter suffixes to preserve
            if suffix in ["free", "beta", "preview"]:
                return model_string.strip(), None

        # For other patterns (Ollama tags, consensus stances), split normally
        parts = model_string.split(":", 1)
        model_name = parts[0].strip()
        model_option = parts[1].strip() if len(parts) > 1 else None
        return model_name, model_option
    return model_string.strip(), None


def get_follow_up_instructions(current_turn_count: int, max_turns: int = None) -> str:
    """
    Generate dynamic follow-up instructions based on conversation turn count.

    Args:
        current_turn_count: Current number of turns in the conversation
        max_turns: Maximum allowed turns before conversation ends (defaults to MAX_CONVERSATION_TURNS)

    Returns:
        Follow-up instructions to append to the tool prompt
    """
    if max_turns is None:
        from utils.conversation.memory import MAX_CONVERSATION_TURNS

        max_turns = MAX_CONVERSATION_TURNS

    if current_turn_count >= max_turns - 1:
        # We're at or approaching the turn limit - no more follow-ups
        return """
IMPORTANT: This is approaching the final exchange in this conversation thread.
Do NOT include any follow-up questions in your response. Provide your complete
final analysis and recommendations."""
    else:
        # Normal follow-up instructions - use dynamic client name
        from utils.client_info import get_client_friendly_name

        client_name = get_client_friendly_name()
        remaining_turns = max_turns - current_turn_count - 1
        return f"""

CONVERSATION CONTINUATION: You can continue this discussion! ({remaining_turns} exchanges remaining)

Feel free to ask clarifying questions or suggest areas for deeper exploration naturally within your response.
If something needs clarification or you'd benefit from additional context, simply mention it conversationally.

IMPORTANT: When you suggest follow-ups or ask questions, you MUST explicitly instruct the user to use the continuation_id
to respond. Use clear, direct language based on urgency:

For optional follow-ups: "Please continue this conversation using the continuation_id from this response if you'd "
"like to explore this further."

For needed responses: "Please respond using the continuation_id from this response - your input is needed to proceed."

For essential/critical responses: "RESPONSE REQUIRED: Please immediately continue using the continuation_id from "
"this response. Cannot proceed without your clarification/input."

This ensures the conversation thread is maintained properly and whether a response is optional, needed, or essential.

The tool will automatically provide a continuation_id in the structured response that can be used in subsequent
tool calls to maintain full conversation context across multiple exchanges.

Remember: Only suggest follow-ups when they would genuinely add value to the discussion, and always instruct "
"the user to use the continuation_id when you do."""


