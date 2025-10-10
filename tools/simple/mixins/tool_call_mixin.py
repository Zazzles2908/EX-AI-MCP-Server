"""
Tool Call Mixin for SimpleTool

Provides tool call detection and execution functionality.
Extracted from tools/simple/base.py to improve maintainability.
"""

from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ToolCallMixin:
    """
    Mixin providing tool call detection and execution.

    This mixin handles:
    - Tool call detection from model responses
    - Tool call execution loop
    - Multi-turn tool call conversations
    - Server-side vs client-side tool execution

    Dependencies:
    - Requires _model_context attribute from BaseTool
    - Requires _current_model_name attribute from BaseTool
    - Requires _generate_content() method from BaseTool
    - Requires _build_tool_call_messages() method from BaseTool
    """

    def _check_for_tool_calls(self, model_response) -> Optional[List[Dict[str, Any]]]:
        """
        Check if model requested tool calls.
        
        Args:
            model_response: The model response object
            
        Returns:
            List of tool calls or None if no tool calls detected
        """
        try:
            from src.providers.tool_executor import extract_tool_calls

            # Get metadata from model response
            metadata = getattr(model_response, "metadata", {})
            if isinstance(metadata, dict):
                # Try to extract tool_calls from raw response
                raw_dict = metadata.get("raw", {})
                if isinstance(raw_dict, dict):
                    tool_calls_list = extract_tool_calls(raw_dict)
                    
                    if tool_calls_list:
                        logger.info(f"Detected {len(tool_calls_list)} tool call(s) from model response")
                        return tool_calls_list
                        
        except Exception as e:
            logger.debug(f"Failed to check for tool_calls: {e}")
            
        return None

    def _execute_tool_calls(
        self,
        tool_calls_list: List[Dict[str, Any]],
        model_response,
        system_prompt: str,
        prompt: str,
        temperature: float,
        provider,
        provider_kwargs: Dict[str, Any]
    ):
        """
        Execute tool calls in a loop until model is satisfied.
        
        This implements the Kimi-style tool call pattern where the model
        can request multiple rounds of tool execution.
        
        Args:
            tool_calls_list: Initial list of tool calls
            model_response: Initial model response
            system_prompt: System prompt for the conversation
            prompt: User prompt
            temperature: Temperature setting
            provider: Provider instance
            provider_kwargs: Provider-specific kwargs
            
        Returns:
            Final model response after tool execution completes
        """
        from utils.progress import send_progress
        from utils.progress_utils.messages import ProgressMessages
        
        try:
            max_iterations = 5  # Prevent infinite loops
            iteration = 0

            # Build messages list for multi-turn conversation
            conv_messages = []
            if system_prompt:
                conv_messages.append({"role": "system", "content": system_prompt})
            conv_messages.append({"role": "user", "content": prompt})

            # Tool call loop - continue until model is satisfied
            while tool_calls_list and iteration < max_iterations:
                iteration += 1
                logger.info(f"Tool call iteration {iteration}: {len(tool_calls_list)} tool(s) requested")

                # Add assistant message with tool_calls
                conv_messages.append({
                    "role": "assistant",
                    "content": getattr(model_response, "content", "") or "",
                    "tool_calls": tool_calls_list
                })

                # Execute each tool call and add results
                for tc in tool_calls_list:
                    tool_msg = self._execute_single_tool_call(tc)
                    conv_messages.append(tool_msg)

                # Continue conversation with tool results
                logger.info(f"Sending tool results back to model (iteration {iteration})...")

                # Don't send tools parameter in follow-up call
                follow_up_kwargs = {k: v for k, v in provider_kwargs.items() if k not in ("tools", "tool_choice")}

                if hasattr(provider, "chat_completions_create"):
                    result_dict = provider.chat_completions_create(
                        model=self._current_model_name,
                        messages=conv_messages,
                        temperature=temperature,
                        **follow_up_kwargs
                    )

                    # Convert dict response to ModelResponse
                    from src.providers.base import ModelResponse, ProviderType
                    model_response = ModelResponse(
                        content=result_dict.get("content", ""),
                        usage=result_dict.get("usage", {}),
                        model_name=result_dict.get("model", self._current_model_name),
                        friendly_name=result_dict.get("provider", ""),
                        provider=getattr(provider, "get_provider_type", lambda: ProviderType.KIMI)(),
                        metadata=result_dict.get("metadata", {})
                    )

                    # Check finish_reason to see if we should continue
                    finish_reason = result_dict.get("choices", [{}])[0].get("finish_reason")
                    logger.info(f"Iteration {iteration} finish_reason: {finish_reason}")

                    # Extract new tool_calls if any
                    from src.providers.tool_executor import extract_tool_calls
                    tool_calls_list = extract_tool_calls(result_dict)

                    if finish_reason != "tool_calls" or not tool_calls_list:
                        # Model is satisfied, exit loop
                        logger.info(f"Tool call loop complete after {iteration} iteration(s)")
                        break
                else:
                    # Fallback: provider doesn't support chat_completions_create
                    logger.warning("Provider doesn't support chat_completions_create, tool execution may fail")
                    from tools.models import ToolOutput
                    from mcp.types import TextContent
                    tool_output = ToolOutput(
                        status="error",
                        content="Provider doesn't support multi-turn tool execution",
                        content_type="text",
                    )
                    return [TextContent(type="text", text=tool_output.model_dump_json())]

            if iteration >= max_iterations:
                logger.warning(f"Tool call loop reached max iterations ({max_iterations})")

            return model_response

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _execute_single_tool_call(self, tc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool call.
        
        Args:
            tc: Tool call dictionary
            
        Returns:
            Tool message dictionary for conversation
        """
        from utils.progress import send_progress
        from utils.progress_utils.messages import ProgressMessages
        
        # Check if this is a builtin_function (server-side execution)
        if tc.get("type") == "builtin_function":
            # Server-side tool (e.g., Kimi $web_search)
            # According to Kimi documentation:
            # - The search was ALREADY executed by Kimi's API server
            # - Search results are embedded in the assistant message content
            # - We just need to acknowledge with empty content
            # - The model will use the search results from its own response
            func_name = tc.get("function", {}).get("name", "unknown")
            send_progress(ProgressMessages.tool_complete(func_name))

            logger.info(f"Acknowledging server-side tool: {func_name}")

            # Acknowledge with empty content as per Kimi docs
            # The search results are already in the assistant message content
            tool_msg = {
                "role": "tool",
                "tool_call_id": str(tc.get("id", "tc-0")),
                "name": func_name,
                "content": ""  # Empty as per Kimi documentation
            }
        else:
            # Client-side tool execution
            from src.providers.tool_executor import execute_tool_call
            
            func_name = tc.get("function", {}).get("name", "unknown")
            send_progress(ProgressMessages.executing_tool(func_name))
            tool_msg = execute_tool_call(tc)
            send_progress(ProgressMessages.tool_complete(func_name))

        return tool_msg

