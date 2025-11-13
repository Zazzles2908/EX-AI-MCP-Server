"""
Hybrid Router: Orchestrates RouterService + MiniMax M2 + Fallback

Combines the best of both worlds:
- RouterService: Infrastructure, preflight, caching, logging
- MiniMax M2: Intelligent routing decisions
- Fallback: Reliable hardcoded rules

Target: Replace 2,538 lines of complex routing with 600 lines of clean code.

Created: 2025-11-11
Phase: 3/5
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.router.service import RouterService, RouteDecision
from src.router.minimax_m2_router import get_router
from src.router.routing_cache import get_routing_cache
from src.providers.registry_core import get_registry_instance

logger = logging.getLogger(__name__)


class HybridRouter:
    """
    Hybrid routing system combining RouterService infrastructure
    with MiniMax M2 intelligence and automatic fallback.

    Architecture:
    ┌─────────────────────────────────────┐
    │  HybridRouter.route_request()       │
    │  ┌───────────────────────────────┐  │
    │  │ 1. Check routing cache        │  │
    │  │ 2. Try MiniMax M2 (async)     │  │
    │  │ 3. Validate decision          │  │
    │  │ 4. Fallback if needed         │  │
    │  │ 5. Log & cache result         │  │
    │  └───────────────────────────────┘  │
    └─────────────────────────────────────┘
    """

    def __init__(self):
        """Initialize hybrid router with all components."""
        # Core infrastructure
        self.router_service = RouterService()
        self.minimax_router = get_router()
        self.routing_cache = get_routing_cache()

        # Configuration from environment
        self.minimax_enabled = self._get_bool_env("MINIMAX_ENABLED", True)
        self.cache_ttl = int(self._get_env("HYBRID_CACHE_TTL", "300"))  # 5 min
        self.fallback_enabled = self._get_bool_env("HYBRID_FALLBACK_ENABLED", True)

        # Health tracking
        self._health = {
            "minimax_available": None,
            "last_check": None,
            "consecutive_failures": 0,
        }

        # Statistics
        self._stats = {
            "total_requests": 0,
            "minimax_success": 0,
            "minimax_fail": 0,
            "fallback_used": 0,
            "cache_hits": 0,
        }

        logger.info(
            f"[HYBRID_ROUTER] Initialized - "
            f"MiniMax={self.minimax_enabled}, "
            f"Fallback={self.fallback_enabled}, "
            f"Cache_TTL={self.cache_ttl}s"
        )

    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with default."""
        import os
        return os.getenv(key, default)

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable."""
        import os
        return os.getenv(key, str(default)).lower() in ("true", "1", "yes", "on")

    async def route_request(
        self,
        tool_name: str,
        request_context: Dict[str, Any],
        available_providers: Optional[Dict[str, Any]] = None,
    ) -> RouteDecision:
        """
        Route request using hybrid approach.

        Flow:
        1. Check routing cache
        2. Try MiniMax M2 if enabled
        3. Fallback to RouterService if needed
        4. Log decision and update cache

        Args:
            tool_name: Name of the tool being called
            request_context: Request details (images, files, web_search, etc.)
            available_providers: Available providers (auto-detected if None)

        Returns:
            RouteDecision with provider, model, reason, and metadata
        """
        self._stats["total_requests"] += 1
        start_time = datetime.now()

        try:
            # Step 1: Get available providers (auto-detect if not provided)
            if available_providers is None:
                available_providers = self._get_available_providers()

            # Step 2: Check routing cache
            cache_key = self._build_cache_key(tool_name, request_context)
            cached_decision = self._get_cached_decision(cache_key)

            if cached_decision:
                self._stats["cache_hits"] += 1
                logger.debug(f"[HYBRID_ROUTER] Cache HIT: {tool_name}")
                return cached_decision

            # Step 3: Try MiniMax M2 if enabled
            if self.minimax_enabled and self._is_minimax_healthy():
                try:
                    decision = await self._route_with_minimax(
                        tool_name, request_context, available_providers
                    )
                    if decision:
                        self._stats["minimax_success"] += 1
                        self._health["consecutive_failures"] = 0
                        self._cache_decision(cache_key, decision)
                        return decision
                except Exception as e:
                    logger.warning(f"[HYBRID_ROUTER] MiniMax routing failed: {e}")
                    self._stats["minimax_fail"] += 1
                    self._health["consecutive_failures"] += 1

                    # Mark as unhealthy if too many consecutive failures
                    if self._health["consecutive_failures"] >= 3:
                        self._health["minimax_available"] = False
                        logger.warning("[HYBRID_ROUTER] MiniMax marked as unhealthy (3 failures)")

            # Step 4: Fallback to RouterService
            if self.fallback_enabled:
                self._stats["fallback_used"] += 1
                decision = self.router_service.fallback_routing(tool_name, request_context)

                # Add metadata about fallback usage
                decision.meta = decision.meta or {}
                decision.meta["routing_method"] = "fallback"
                decision.meta["minimax_used"] = False

                logger.info(f"[HYBRID_ROUTER] Fallback used: {tool_name} → {decision.chosen}")
                return decision

            # Step 5: Last resort - use RouterService basic routing
            decision = self.router_service.choose_model("auto")
            decision.meta = decision.meta or {}
            decision.meta["routing_method"] = "last_resort"
            return decision

        except Exception as e:
            logger.error(f"[HYBRID_ROUTER] Unexpected error: {e}")
            # Emergency fallback
            return self.router_service.choose_model("auto")

        finally:
            # Log performance
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(
                f"[HYBRID_ROUTER] Routing completed in {elapsed:.3f}s "
                f"(cache_hits={self._stats['cache_hits']}, "
                f"minimax={self._stats['minimax_success']}, "
                f"fallback={self._stats['fallback_used']})"
            )

    async def _route_with_minimax(
        self,
        tool_name: str,
        request_context: Dict[str, Any],
        available_providers: Dict[str, Any],
    ) -> Optional[RouteDecision]:
        """Route request using MiniMax M2 intelligence."""
        try:
            # Get routing decision from MiniMax M2
            minimax_decision = await self.minimax_router.route_request(
                tool_name=tool_name,
                request_context=request_context,
                available_providers=available_providers,
            )

            if not minimax_decision:
                logger.debug("[HYBRID_ROUTER] MiniMax returned empty decision")
                return None

            # Convert MiniMax decision to RouteDecision
            provider_name = minimax_decision.get("provider")
            model_name = minimax_decision.get("model")

            if not provider_name or not model_name:
                logger.warning("[HYBRID_ROUTER] MiniMax decision missing provider/model")
                return None

            # Validate provider exists
            prov = get_registry_instance().get_provider_for_model(model_name)
            if prov is None:
                logger.warning(f"[HYBRID_ROUTER] Provider not found for {model_name}")
                return None

            # Build RouteDecision
            decision = RouteDecision(
                requested=request_context.get("requested_model", "auto"),
                chosen=model_name,
                reason=minimax_decision.get("reasoning", "minimax_intelligence"),
                provider=prov.get_provider_type().name,
                meta={
                    "routing_method": "minimax_m2",
                    "confidence": minimax_decision.get("confidence", 0.0),
                    "execution_path": minimax_decision.get("execution_path", "STANDARD"),
                    "minimax_used": True,
                },
            )

            logger.info(
                f"[HYBRID_ROUTER] MiniMax routed: {tool_name} → "
                f"{provider_name}/{model_name} "
                f"({minimax_decision.get('reasoning', 'N/A')})"
            )

            return decision

        except Exception as e:
            logger.error(f"[HYBRID_ROUTER] MiniMax routing error: {e}")
            return None

    def _get_available_providers(self) -> Dict[str, Any]:
        """Get available providers and their capabilities."""
        try:
            registry = get_registry_instance()
            avail = registry.get_available_models(respect_restrictions=True)

            providers = {}
            for model_name, provider_type in avail.items():
                prov_name = provider_type.name
                if prov_name not in providers:
                    providers[prov_name] = {
                        "name": prov_name,
                        "models": [],
                        "capabilities": [],
                    }
                providers[prov_name]["models"].append(model_name)

            return providers

        except Exception as e:
            logger.warning(f"[HYBRID_ROUTER] Failed to get available providers: {e}")
            return {}

    def _build_cache_key(self, tool_name: str, context: Dict[str, Any]) -> str:
        """Build cache key for routing decision."""
        # Simplify context for caching
        cache_context = {
            "tool": tool_name,
            "has_images": bool(context.get("images")),
            "has_files": bool(context.get("files")),
            "web_search": bool(context.get("use_websearch")),
            "streaming": bool(context.get("stream")),
            "thinking_mode": bool(context.get("thinking_mode")),
            "requested_model": context.get("requested_model", "auto"),
        }

        # Use json.dumps for stable serialization
        import hashlib
        context_str = json.dumps(cache_context, sort_keys=True)
        context_hash = hashlib.blake2b(context_str.encode(), digest_size=8).hexdigest()

        return f"hybrid:{tool_name}:{context_hash}"

    def _get_cached_decision(self, cache_key: str) -> Optional[RouteDecision]:
        """Get cached routing decision."""
        try:
            cached = self.routing_cache.get_minimax_decision(cache_key)
            if cached:
                # Convert cached dict back to RouteDecision
                return RouteDecision(
                    requested=cached["requested"],
                    chosen=cached["chosen"],
                    reason=cached["reason"],
                    provider=cached.get("provider"),
                    meta=cached.get("meta"),
                )
        except Exception as e:
            logger.warning(f"[HYBRID_ROUTER] Cache read error: {e}")

        return None

    def _cache_decision(self, cache_key: str, decision: RouteDecision) -> None:
        """Cache routing decision."""
        try:
            cache_data = {
                "requested": decision.requested,
                "chosen": decision.chosen,
                "reason": decision.reason,
                "provider": decision.provider,
                "meta": decision.meta or {},
                "timestamp": datetime.now().isoformat(),
            }
            self.routing_cache.set_minimax_decision(cache_key, cache_data)
        except Exception as e:
            logger.warning(f"[HYBRID_ROUTER] Cache write error: {e}")

    def _is_minimax_healthy(self) -> bool:
        """Check if MiniMax M2 is healthy."""
        # If explicitly disabled, return False
        if not self.minimax_enabled:
            return False

        # If never checked, assume healthy
        if self._health["minimax_available"] is None:
            return True

        # Return current health status
        return self._health["minimax_available"]

    def get_stats(self) -> Dict[str, Any]:
        """Get hybrid router statistics."""
        total = self._stats["total_requests"]

        return {
            **self._stats,
            "hit_ratios": {
                "cache": self._stats["cache_hits"] / total if total > 0 else 0.0,
                "minimax": self._stats["minimax_success"] / total if total > 0 else 0.0,
                "fallback": self._stats["fallback_used"] / total if total > 0 else 0.0,
            },
            "health": self._health,
        }

    def clear_cache(self) -> None:
        """Clear all routing caches."""
        self.routing_cache.clear_all()
        logger.info("[HYBRID_ROUTER] Cache cleared")

    def enable_minimax(self) -> None:
        """Enable MiniMax M2 routing."""
        self.minimax_enabled = True
        self._health["minimax_available"] = None
        logger.info("[HYBRID_ROUTER] MiniMax M2 enabled")

    def disable_minimax(self) -> None:
        """Disable MiniMax M2 routing (fallback only)."""
        self.minimax_enabled = False
        self._health["minimax_available"] = False
        logger.info("[HYBRID_ROUTER] MiniMax M2 disabled (fallback only)")

    def reset_health(self) -> None:
        """Reset MiniMax M2 health status."""
        self._health = {
            "minimax_available": None,
            "last_check": None,
            "consecutive_failures": 0,
        }
        logger.info("[HYBRID_ROUTER] Health status reset")


# Global hybrid router instance
_hybrid_router: Optional[HybridRouter] = None


def get_hybrid_router() -> HybridRouter:
    """
    Get the singleton hybrid router instance.

    Returns:
        HybridRouter instance
    """
    global _hybrid_router
    if _hybrid_router is None:
        _hybrid_router = HybridRouter()
    return _hybrid_router


__all__ = ["HybridRouter", "get_hybrid_router"]
