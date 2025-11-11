"""
MiniMax M2 Smart Router - Minimal Implementation

Simplified routing using MiniMax M2 for intelligent decisions.
"""

import logging
from typing import Dict, Any, Optional

from src.providers.registry import get_registry

logger = logging.getLogger(__name__)


class MiniMaxM2Router:
    """Simplified intelligent router."""

    def __init__(self):
        self.registry = get_registry()
        self.routing_rules = {
            "web_search": "glm",
            "code_analysis": "kimi",
            "file_processing": "kimi",
            "chat": "glm",
            "analysis": "glm"
        }

    async def route_request(self, task_type: str, content: str, model_preference: str = "auto") -> str:
        """
        Route request to appropriate provider.

        Args:
            task_type: Type of task (web_search, code_analysis, etc.)
            content: Content to process
            model_preference: Preferred model

        Returns:
            Result from routed provider
        """
        try:
            # Determine provider
            provider_name = self.routing_rules.get(task_type, "glm")

            # Get provider instance
            if provider_name == "glm":
                provider = self.registry.get_provider("GLM")
            elif provider_name == "kimi":
                provider = self.registry.get_provider("KIMI")
            else:
                provider = self.registry.get_provider("GLM")

            if not provider:
                return f"Error: Provider {provider_name} not available"

            # Route to provider
            result = await provider.chat_completions_create(
                messages=[{"role": "user", "content": content}],
                model=model_preference if model_preference != "auto" else "glm-4.5-flash"
            )

            return result

        except Exception as e:
            logger.error(f"Routing error: {e}")
            return f"Error: {str(e)}"
