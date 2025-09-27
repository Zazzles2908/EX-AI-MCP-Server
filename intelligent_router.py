"""
Intelligent Router for EX-AI MCP Server

This module implements the intelligent routing system that uses GLM-4.5-Flash
as an AI manager to route requests between different providers based on task type.

Key Features:
- GLM provider for web browsing and search tasks
- Kimi provider for file processing and analysis
- Cost-aware routing strategies
- Fallback mechanisms with retry logic
- Production-ready error handling
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


import json
import uuid
from pathlib import Path

# Structured JSONL router logger (configured in server.setup_logging)
_router_logger = logging.getLogger("router")

def _router_emit(event: dict):
    """Emit a structured JSON line to router.jsonl; never raise."""
    try:
        # lightweight schema; server.py expects pre-serialized JSON on this logger
        event.setdefault("timestamp", time.time())
        _router_logger.info(json.dumps(event, ensure_ascii=False))
    except Exception:
        # Avoid breaking normal logging flow
        logger.debug("Router JSONL emit failed", exc_info=False)

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Enumeration of different task types for routing decisions"""
    WEB_SEARCH = "web_search"
    FILE_PROCESSING = "file_processing"
    CODE_ANALYSIS = "code_analysis"
    GENERAL_CHAT = "general_chat"
    REASONING = "reasoning"

class ProviderType(Enum):
    """Available AI providers"""
    GLM = "glm"
    KIMI = "kimi"
    AUTO = "auto"

@dataclass
class RoutingDecision:
    """Represents a routing decision made by the AI manager"""
    provider: ProviderType
    confidence: float
    reasoning: str
    fallback_provider: Optional[ProviderType] = None
    estimated_cost: float = 0.0
    estimated_time: float = 0.0

class IntelligentRouter:
    """
    Intelligent routing system using GLM-4.5-Flash as AI manager
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.routing_enabled = config.get("INTELLIGENT_ROUTING_ENABLED", True)
        self.cost_aware = config.get("COST_AWARE_ROUTING", True)
        self.max_retries = config.get("MAX_RETRIES", 3)
        self.request_timeout = config.get("REQUEST_TIMEOUT", 30)

        # Provider preferences
        self.web_search_provider = config.get("WEB_SEARCH_PROVIDER", "glm")
        self.file_processing_provider = config.get("FILE_PROCESSING_PROVIDER", "kimi")

        # Performance tracking
        self.provider_stats = {
            ProviderType.GLM: {"success_rate": 0.95, "avg_response_time": 2.5},
            ProviderType.KIMI: {"success_rate": 0.92, "avg_response_time": 3.2}
        }

    async def route_request(self, request: Dict[str, Any]) -> RoutingDecision:
        """
        Route a request to the appropriate provider using AI manager logic
        """
        if not self.routing_enabled:
            return RoutingDecision(
                provider=ProviderType.GLM,
                confidence=1.0,
                reasoning="Routing disabled, using default GLM provider"
            )

        try:
            # Correlate request for structured logs
            request_id = request.get("request_id") or str(uuid.uuid4())
            request["request_id"] = request_id
            _router_emit({
                "type": "route_start",
                "request_id": request_id,
                "method": request.get("method"),
                "task_hint": str(request.get("params", {}))[:200]
            })

            # Analyze request to determine task type
            task_type = await self._analyze_task_type(request)
            _router_emit({
                "type": "task_type",
                "request_id": request_id,
                "task_type": task_type.value
            })

            # Make routing decision based on task type and current conditions
            decision = await self._make_routing_decision(task_type, request)

            _router_emit({
                "type": "decision",
                "request_id": request_id,
                "provider": decision.provider.value,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "fallback": decision.fallback_provider.value if decision.fallback_provider else None,
                "est_cost": decision.estimated_cost,
                "est_time": decision.estimated_time
            })

            logger.info(f"Routing decision: {decision.provider.value} (confidence: {decision.confidence:.2f})")
            return decision

        except Exception as e:
            logger.error(f"Error in routing decision: {e}")
            _router_emit({
                "type": "routing_error",
                "request_id": request.get("request_id"),
                "error": str(e)
            })

            # Fallback to GLM provider
            return RoutingDecision(
                provider=ProviderType.GLM,
                confidence=0.5,
                reasoning=f"Fallback due to routing error: {str(e)}"
            )

    async def _analyze_task_type(self, request: Dict[str, Any]) -> TaskType:
        """
        Analyze the request to determine the task type
        """
        tool_name = request.get("method", "").lower()
        content = str(request.get("params", {})).lower()

        # Web search indicators
        web_indicators = ["search", "browse", "web", "url", "website", "internet", "google"]
        if any(indicator in tool_name or indicator in content for indicator in web_indicators):
            return TaskType.WEB_SEARCH

        # File processing indicators
        file_indicators = ["file", "document", "pdf", "analyze", "process", "read", "parse"]
        if any(indicator in tool_name or indicator in content for indicator in file_indicators):
            return TaskType.FILE_PROCESSING

        # Code analysis indicators
        code_indicators = ["code", "review", "debug", "programming", "function", "class"]
        if any(indicator in tool_name or indicator in content for indicator in code_indicators):
            return TaskType.CODE_ANALYSIS

        # Reasoning indicators
        reasoning_indicators = ["think", "reason", "analyze", "deep", "complex", "solve"]
        if any(indicator in tool_name or indicator in content for indicator in reasoning_indicators):
            return TaskType.REASONING

        return TaskType.GENERAL_CHAT

    async def _make_routing_decision(self, task_type: TaskType, request: Dict[str, Any]) -> RoutingDecision:
        """
        Make intelligent routing decision based on task type and current conditions
        """
        # Task-based routing rules
        if task_type == TaskType.WEB_SEARCH:
            return RoutingDecision(
                provider=ProviderType.GLM,
                confidence=0.9,
                reasoning="GLM provider optimized for web browsing and search tasks",
                fallback_provider=ProviderType.KIMI,
                estimated_cost=0.02,
                estimated_time=3.0
            )

        elif task_type == TaskType.FILE_PROCESSING:
            return RoutingDecision(
                provider=ProviderType.KIMI,
                confidence=0.95,
                reasoning="Kimi provider specialized for file processing and analysis",
                fallback_provider=ProviderType.GLM,
                estimated_cost=0.05,
                estimated_time=4.0
            )

        elif task_type == TaskType.CODE_ANALYSIS:
            # Choose based on current performance metrics
            if self.provider_stats[ProviderType.GLM]["success_rate"] > 0.9:
                return RoutingDecision(
                    provider=ProviderType.GLM,
                    confidence=0.85,
                    reasoning="GLM provider performing well for code analysis",
                    fallback_provider=ProviderType.KIMI,
                    estimated_cost=0.03,
                    estimated_time=2.5
                )
            else:
                return RoutingDecision(
                    provider=ProviderType.KIMI,
                    confidence=0.8,
                    reasoning="Kimi provider as fallback for code analysis",
                    fallback_provider=ProviderType.GLM,
                    estimated_cost=0.04,
                    estimated_time=3.5
                )

        elif task_type == TaskType.REASONING:
            return RoutingDecision(
                provider=ProviderType.GLM,
                confidence=0.88,
                reasoning="GLM-4.5-Flash optimized for reasoning tasks",
                fallback_provider=ProviderType.KIMI,
                estimated_cost=0.06,
                estimated_time=5.0
            )

        else:  # GENERAL_CHAT
            # Load balance between providers
            glm_load = self.provider_stats[ProviderType.GLM]["avg_response_time"]
            kimi_load = self.provider_stats[ProviderType.KIMI]["avg_response_time"]

            if glm_load < kimi_load:
                return RoutingDecision(
                    provider=ProviderType.GLM,
                    confidence=0.75,
                    reasoning="GLM provider has lower current load",
                    fallback_provider=ProviderType.KIMI,
                    estimated_cost=0.02,
                    estimated_time=glm_load
                )
            else:
                return RoutingDecision(
                    provider=ProviderType.KIMI,
                    confidence=0.75,
                    reasoning="Kimi provider has lower current load",
                    fallback_provider=ProviderType.GLM,
                    estimated_cost=0.03,
                    estimated_time=kimi_load
                )

    async def execute_with_fallback(self, decision: RoutingDecision, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request with fallback mechanism and retry logic
        """
        primary_provider = decision.provider
        fallback_provider = decision.fallback_provider

        # Ensure request correlation id is present
        request_id = request.get("request_id") or str(uuid.uuid4())
        request["request_id"] = request_id

        for attempt in range(self.max_retries):
            try:
                # Try primary provider
                if attempt == 0:
                    provider = primary_provider
                else:

                    # Use fallback provider for retries
                    provider = fallback_provider or primary_provider

                logger.info(f"Attempt {attempt + 1}: Using {provider.value} provider")

                # Execute request with timeout
                start_time = time.time()
                _router_emit({
                    "type": "attempt_start",
                    "request_id": request_id,
                    "attempt": attempt + 1,
                    "provider": provider.value
                })
                result = await asyncio.wait_for(
                    self._execute_provider_request(provider, request),
                    timeout=self.request_timeout
                )


                # Update success statistics
                duration = time.time() - start_time
                _router_emit({
                    "type": "attempt_success",
                    "request_id": request_id,
                    "attempt": attempt + 1,
                    "provider": provider.value,
                    "duration_s": round(duration, 3)
                })
                _router_emit({
                    "type": "result_meta",
                    "request_id": request_id,
                    "provider": provider.value,
                    "result_preview_len": len(str(result.get("result", "")))
                })

                self._update_provider_stats(provider, success=True, response_time=time.time())

                return result

            except asyncio.TimeoutError:
                logger.warning(f"Timeout with {provider.value} provider (attempt {attempt + 1})")
                _router_emit({
                    "type": "attempt_timeout",
                    "request_id": request_id,
                    "attempt": attempt + 1,
                    "provider": provider.value,
                    "timeout_s": self.request_timeout
                })

                self._update_provider_stats(provider, success=False, response_time=self.request_timeout)

            except Exception as e:
                logger.error(f"Error with {provider.value} provider: {e} (attempt {attempt + 1})")
                _router_emit({
                    "type": "attempt_error",
                    "request_id": request_id,
                    "attempt": attempt + 1,
                    "provider": provider.value,
                    "error": str(e)
                })

                self._update_provider_stats(provider, success=False, response_time=0)

                if attempt == self.max_retries - 1:
                    raise

        raise Exception(f"All retry attempts failed for request")

    async def _execute_provider_request(self, provider: ProviderType, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request using specified provider
        """
        if provider == ProviderType.GLM:
            return await self._execute_glm_request(request)
        elif provider == ProviderType.KIMI:
            return await self._execute_kimi_request(request)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _execute_glm_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request using GLM provider with native web browsing
        """
        # Implementation would integrate with actual GLM API
        # This is a placeholder for the actual implementation
        logger.info("Executing GLM request with web browsing capabilities")

        # Simulate GLM processing
        await asyncio.sleep(0.1)

        return {
            "provider": "glm",
            "result": "GLM response with web browsing capabilities",
            "capabilities": ["web_search", "browsing", "reasoning"]
        }

    async def _execute_kimi_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request using Kimi provider for file processing
        """
        # Implementation would integrate with actual Kimi API
        # This is a placeholder for the actual implementation
        logger.info("Executing Kimi request with file processing capabilities")

        # Simulate Kimi processing
        await asyncio.sleep(0.1)

        return {
            "provider": "kimi",
            "result": "Kimi response with file processing capabilities",
            "capabilities": ["file_processing", "document_analysis", "reasoning"]
        }

    def _update_provider_stats(self, provider: ProviderType, success: bool, response_time: float):
        """
        Update provider performance statistics
        """
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {"success_rate": 0.5, "avg_response_time": 5.0}

        stats = self.provider_stats[provider]

        # Update success rate (exponential moving average)
        alpha = 0.1
        if success:
            stats["success_rate"] = stats["success_rate"] * (1 - alpha) + alpha
        else:
            stats["success_rate"] = stats["success_rate"] * (1 - alpha)

        # Update average response time
        if response_time > 0:
            stats["avg_response_time"] = stats["avg_response_time"] * (1 - alpha) + response_time * alpha

        logger.debug(f"Updated {provider.value} stats: {stats}")

# Global router instance
_router_instance = None

def get_router(config: Dict[str, Any]) -> IntelligentRouter:
    """Get or create the global router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = IntelligentRouter(config)
    return _router_instance
