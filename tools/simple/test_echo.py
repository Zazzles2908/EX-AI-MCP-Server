"""
Test Echo Tool - For Load Testing and Infrastructure Validation
================================================================

Simple echo tool that returns the input message without calling external APIs.
Used for load testing WebSocket infrastructure, authentication, and sampling logic.

EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
Purpose: Enable high-volume load testing without AI API costs or rate limits
"""

import asyncio
import time
from typing import Any, Dict, List

from tools.simple.base import SimpleTool
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class TestEchoTool(SimpleTool):
    """
    Echo tool for load testing and infrastructure validation.

    Returns the input message without calling external APIs.
    Useful for testing WebSocket infrastructure, authentication, and sampling logic.
    """

    def get_name(self) -> str:
        return "test_echo"

    def get_description(self) -> str:
        return "Echo back the input message. Used for load testing and infrastructure validation. Does not call external APIs."

    def get_tool_fields(self) -> Dict[str, Dict[str, Any]]:
        return {
            "prompt": {
                "type": "string",
                "description": "The message to echo back"
            },
            "delay_ms": {
                "type": "integer",
                "description": "Optional delay in milliseconds to simulate processing time (default: 0)",
                "default": 0
            },
            "include_metadata": {
                "type": "boolean",
                "description": "Whether to include metadata in response (default: true)",
                "default": True
            }
        }

    def get_required_fields(self) -> List[str]:
        return ["prompt"]

    async def prepare_prompt(self, **kwargs) -> str:
        """
        Prepare the prompt for the echo tool.
        Since this tool doesn't call AI models, we just return the input.
        """
        return kwargs.get("prompt", "")

    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the echo tool.

        This overrides the default run() method since we don't need to call AI models.
        """
        start_time = time.time()

        prompt = kwargs.get("prompt", "")
        delay_ms = kwargs.get("delay_ms", 0)
        include_metadata = kwargs.get("include_metadata", True)

        # Simulate processing delay if requested
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)

        # Build response
        response = {
            "status": "success",
            "content": f"Echo: {prompt}",
            "content_type": "text"
        }

        # Add metadata if requested
        if include_metadata:
            processing_time_ms = (time.time() - start_time) * 1000
            response["metadata"] = {
                "tool_name": "test_echo",
                "prompt_length": len(prompt),
                "delay_ms": delay_ms,
                "processing_time_ms": round(processing_time_ms, 2),
                "timestamp": time.time()
            }

        logger.debug(f"test_echo processed: {len(prompt)} chars, {delay_ms}ms delay")

        return response

