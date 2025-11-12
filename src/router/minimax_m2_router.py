"""
MiniMax M2-Stable Smart Router - Full Implementation

A simplified, intelligent routing system using MiniMax M2-Stable for decisions.
Replaces 2,500 lines of complex routing logic with 150 lines of clean code.
"""

import json
import logging
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from src.router.routing_cache import get_routing_cache

# Optional import - anthropic package may not be installed
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    Anthropic = None
    ANTHROPIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("anthropic package not available - MiniMax M2-Stable routing will use fallback only")

logger = logging.getLogger(__name__)


class MiniMaxM2Router:
    """
    Smart router using MiniMax M2-Stable for intelligent routing decisions.

    Instead of hardcoded logic, we use MiniMax M2-Stable to make routing decisions
    based on tool requirements, provider capabilities, and current context.
    """

    def __init__(self):
        """Initialize the smart router with MiniMax M2-Stable."""
        # Check if anthropic package is available
        if not ANTHROPIC_AVAILABLE:
            logger.warning("anthropic package not installed - MiniMax M2-Stable routing disabled")
            self.client = None
            self.api_key = None
        else:
            # Get MiniMax API key from environment
            self.api_key = os.getenv("MINIMAX_M2_KEY")
            if not self.api_key:
                logger.warning("MINIMAX_M2_KEY not found in environment")
                self.client = None
            else:
                self.client = Anthropic(
                    api_key=self.api_key,
                    base_url="https://api.minimax.io/anthropic"
                )

        self.routing_cache = get_routing_cache()
        self.enabled = os.getenv("MINIMAX_ENABLED", "true").lower() == "true"
        self.timeout = float(os.getenv("MINIMAX_TIMEOUT", "5"))
        self.max_retries = int(os.getenv("MINIMAX_RETRY", "2"))

        logger.info(f"MiniMax M2-Stable Smart Router initialized (enabled={self.enabled}, anthropic={ANTHROPIC_AVAILABLE})")

    async def route_request(
        self,
        tool_name: str,
        request_context: Dict[str, Any],
        available_providers: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Route request using MiniMax M2-Stable intelligence.

        Args:
            tool_name: Name of the tool being called
            request_context: Request details (images, files, web_search, etc.)
            available_providers: Available providers and their capabilities

        Returns:
            Routing decision with provider, model, and execution path
        """
        # Check if enabled
        if not self.enabled or not self.client:
            return self._fallback_routing(tool_name, available_providers)

        # Check cache first (5-minute TTL)
        cache_key = self._get_cache_key(tool_name, request_context)
        cached = self.routing_cache.get_minimax_decision(cache_key)
        if cached:
            logger.debug(f"Cache hit for {tool_name}")
            return cached

        # Build routing prompt
        routing_prompt = self._build_routing_prompt(
            tool_name,
            request_context,
            available_providers
        )

        # Call MiniMax M2-Stable for routing decision with retry
        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.messages.create(
                        model="MiniMax-M2-Stable",
                        max_tokens=500,
                        messages=[
                            {
                                "role": "system",
                                "content": """You are an intelligent routing system for an AI model server.
Your job is to select the optimal provider and model for each request.
Respond with ONLY a JSON object, no other text."""
                            },
                            {
                                "role": "user",
                                "content": routing_prompt
                            }
                        ]
                    ),
                    timeout=self.timeout
                )

                # Parse routing decision
                try:
                    routing_decision = json.loads(response.content[0].text)
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    logger.warning(f"Failed to parse MiniMax M2-Stable response: {e}")
                    if attempt < self.max_retries:
                        continue
                    return self._fallback_routing(tool_name, available_providers)

                # Validate decision
                validated_decision = self._validate_routing_decision(
                    routing_decision,
                    available_providers
                )

                # Cache the decision
                self.routing_cache.set_minimax_decision(cache_key, validated_decision)

                logger.info(
                    f"MiniMax M2-Stable Routing: {tool_name} → {validated_decision['provider']}/"
                    f"{validated_decision['model']} "
                    f"({validated_decision.get('reasoning', 'N/A')})"
                )

                return validated_decision

            except asyncio.TimeoutError:
                logger.warning(f"MiniMax M2-Stable timeout (attempt {attempt + 1}/{self.max_retries + 1})")
                if attempt < self.max_retries:
                    await asyncio.sleep(1)  # Wait before retry
                    continue
            except Exception as e:
                logger.error(f"MiniMax M2-Stable routing error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
                    continue

        # All attempts failed, use fallback
        logger.warning(f"MiniMax M2-Stable failed after {self.max_retries + 1} attempts, using fallback")
        return self._fallback_routing(tool_name, available_providers)

    def _build_routing_prompt(
        self,
        tool_name: str,
        context: Dict[str, Any],
        providers: Dict[str, Dict[str, Any]]
    ) -> str:
        """Build routing prompt for MiniMax M2-Stable."""
        return f"""
Tool: {tool_name}
Request Context: {json.dumps(context, indent=2)}
Available Providers: {json.dumps(providers, indent=2)}

Routing Rules:
1. Web search requests MUST go to GLM (Kimi doesn't support it)
2. Vision requests can go to GLM or Kimi (both support it)
3. Thinking mode works best with Kimi K2 models
4. File uploads supported by both
5. Balance cost and performance
6. Default to GLM for general tasks

Respond with JSON:
{{
    "provider": "GLM|KIMI",
    "model": "specific-model-name",
    "execution_path": "STANDARD|STREAMING|THINKING|VISION|FILE_UPLOAD",
    "reasoning": "brief explanation",
    "confidence": 0.95
}}
"""

    def _validate_routing_decision(
        self,
        decision: Dict[str, Any],
        providers: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate routing decision against available providers."""
        provider = decision.get('provider', '').upper()
        model = decision.get('model')

        # Validate provider
        if provider not in ['GLM', 'KIMI']:
            logger.warning(f"Invalid provider {provider}, using fallback")
            return self._fallback_routing('unknown', providers)

        # Validate model (for now, just check if it's a string)
        if not model or not isinstance(model, str):
            logger.warning(f"Invalid model {model}, using fallback")
            return self._fallback_routing('unknown', providers)

        # Add timestamp and source
        decision['timestamp'] = datetime.now().isoformat()
        decision['source'] = 'minimax'

        return decision

    def _fallback_routing(
        self,
        tool_name: str,
        providers: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback routing when MiniMax M2-Stable fails."""
        # Simple fallback: GLM for web search, Kimi for others
        return {
            'provider': 'GLM',
            'model': 'glm-4.5-flash',
            'execution_path': 'STANDARD',
            'reasoning': 'MiniMax unavailable, using fallback',
            'confidence': 0.5,
            'source': 'fallback',
            'timestamp': datetime.now().isoformat()
        }

    def _get_cache_key(self, tool_name: str, context: Dict[str, Any]) -> str:
        """Generate cache key for routing decision."""
        # Simplify context for caching
        cache_context = {
            'tool': tool_name,
            'has_images': bool(context.get('images')),
            'has_files': bool(context.get('files')),
            'web_search': bool(context.get('use_websearch')),
            'streaming': bool(context.get('stream')),
            'thinking_mode': bool(context.get('thinking_mode')),
        }
        return f"{tool_name}:{hash(json.dumps(cache_context, sort_keys=True))}"


# Global router instance
_router = None


def get_router() -> MiniMaxM2Router:
    """Get global router instance."""
    global _router
    if _router is None:
        _router = MiniMaxM2Router()
    return _router
