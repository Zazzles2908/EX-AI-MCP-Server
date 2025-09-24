"""
GLM Flash Manager: Intelligent AI manager using GLM-4.5 Flash for routing decisions.

This module implements the intelligent AI manager that uses GLM-4.5 Flash to make
smart routing decisions based on request analysis. It provides cost-aware token
management and capability-based routing.
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .request_analyzer import RequestAnalysis, RequestType, ContentComplexity
from ...providers.base import ProviderType
from ...providers.registry import ModelProviderRegistry

logger = logging.getLogger("glm_flash_manager")


class RoutingStrategy(Enum):
    """Routing strategies for different scenarios."""
    CAPABILITY_BASED = "capability_based"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    HYBRID_INTELLIGENT = "hybrid_intelligent"


@dataclass
class RoutingDecision:
    """Detailed routing decision with reasoning."""
    primary_provider: ProviderType
    fallback_providers: List[ProviderType]
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_time: float
    strategy_used: RoutingStrategy
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "primary_provider": self.primary_provider.value if self.primary_provider else None,
            "fallback_providers": [p.value for p in self.fallback_providers],
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "estimated_cost": self.estimated_cost,
            "estimated_time": self.estimated_time,
            "strategy_used": self.strategy_used.value,
            "metadata": self.metadata
        }


class ProviderCapabilityRegistry:
    """Registry of provider capabilities for intelligent routing."""
    
    def __init__(self):
        self.capabilities = {
            ProviderType.KIMI: {
                "strengths": ["file_processing", "long_context", "document_analysis", "extraction"],
                "context_window": 128000,
                "cost_per_1k_tokens": 0.012,  # Estimated
                "avg_response_time": 3.5,
                "supports_files": True,
                "supports_web": False,
                "supports_images": True,
                "max_file_size_mb": 20.0,
                "optimal_for": [RequestType.FILE_OPERATION, RequestType.LONG_CONTEXT]
            },
            ProviderType.GLM: {
                "strengths": ["web_browsing", "real_time_search", "general_chat", "code_generation"],
                "context_window": 128000,
                "cost_per_1k_tokens": 0.001,  # Much cheaper
                "avg_response_time": 1.2,
                "supports_files": False,
                "supports_web": True,
                "supports_images": True,
                "max_file_size_mb": 0.0,
                "optimal_for": [RequestType.WEB_BROWSING, RequestType.GENERAL_CHAT, RequestType.CODE_GENERATION]
            }
        }

    def get_optimal_provider(self, request_type: RequestType) -> ProviderType:
        """Get the optimal provider for a request type."""
        for provider, caps in self.capabilities.items():
            if request_type in caps["optimal_for"]:
                return provider
        return ProviderType.GLM  # Default fallback

    def get_capability_score(self, provider: ProviderType, request_analysis: RequestAnalysis) -> float:
        """Calculate capability score for a provider given request analysis."""
        if provider not in self.capabilities:
            return 0.0
        
        caps = self.capabilities[provider]
        score = 0.0
        
        # Base capability match
        if request_analysis.request_type in caps["optimal_for"]:
            score += 0.4
        
        # File handling capability
        if request_analysis.has_files and caps["supports_files"]:
            score += 0.3
        elif request_analysis.has_files and not caps["supports_files"]:
            score -= 0.5  # Major penalty
        
        # Web capability
        if request_analysis.has_web_intent and caps["supports_web"]:
            score += 0.3
        elif request_analysis.has_web_intent and not caps["supports_web"]:
            score -= 0.3
        
        # Image capability
        if request_analysis.has_images and caps["supports_images"]:
            score += 0.2
        elif request_analysis.has_images and not caps["supports_images"]:
            score -= 0.4
        
        # Context window consideration
        if request_analysis.estimated_tokens > caps["context_window"] * 0.8:
            score -= 0.3  # Penalty for near-limit usage
        
        # Complexity consideration
        if request_analysis.complexity == ContentComplexity.VERY_COMPLEX:
            if "long_context" in caps["strengths"]:
                score += 0.1
        
        return max(0.0, min(1.0, score))


class GLMFlashManager:
    """
    Intelligent AI manager using GLM-4.5 Flash for routing decisions.
    
    This manager analyzes requests and makes intelligent routing decisions
    based on provider capabilities, cost considerations, and performance
    requirements.
    """

    def __init__(self, 
                 enable_intelligent_routing: bool = True,
                 cost_threshold: float = 0.10,
                 performance_threshold: float = 5.0):
        """
        Initialize the GLM Flash Manager.
        
        Args:
            enable_intelligent_routing: Whether to use GLM for routing decisions
            cost_threshold: Maximum cost per request for cost optimization
            performance_threshold: Maximum response time for performance optimization
        """
        self.enable_intelligent_routing = enable_intelligent_routing
        self.cost_threshold = cost_threshold
        self.performance_threshold = performance_threshold
        self.capability_registry = ProviderCapabilityRegistry()
        
        # GLM Flash configuration for routing decisions
        self.glm_flash_model = os.getenv("GLM_FLASH_ROUTING_MODEL", "glm-4.5-flash")
        self.routing_max_tokens = int(os.getenv("GLM_FLASH_ROUTING_MAX_TOKENS", "500"))
        
        # Caching for routing decisions
        self._routing_cache: Dict[str, Tuple[RoutingDecision, float]] = {}
        self._cache_ttl = float(os.getenv("ROUTING_CACHE_TTL", "300"))  # 5 minutes
        
        logger.info(f"GLM Flash Manager initialized with intelligent routing: {enable_intelligent_routing}")

    def make_routing_decision(self, 
                            request_analysis: RequestAnalysis,
                            strategy: RoutingStrategy = RoutingStrategy.HYBRID_INTELLIGENT) -> RoutingDecision:
        """
        Make an intelligent routing decision based on request analysis.
        
        Args:
            request_analysis: Analysis of the incoming request
            strategy: Routing strategy to use
            
        Returns:
            RoutingDecision with provider selection and reasoning
        """
        try:
            # Check cache first
            cache_key = self._create_cache_key(request_analysis, strategy)
            cached_decision = self._get_cached_decision(cache_key)
            if cached_decision:
                logger.debug(f"Using cached routing decision for {request_analysis.request_type}")
                return cached_decision

            # Make routing decision based on strategy
            if strategy == RoutingStrategy.CAPABILITY_BASED:
                decision = self._capability_based_routing(request_analysis)
            elif strategy == RoutingStrategy.COST_OPTIMIZED:
                decision = self._cost_optimized_routing(request_analysis)
            elif strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
                decision = self._performance_optimized_routing(request_analysis)
            else:  # HYBRID_INTELLIGENT
                decision = self._hybrid_intelligent_routing(request_analysis)

            # Cache the decision
            self._cache_decision(cache_key, decision)
            
            logger.info(f"Routing decision made: {decision.to_dict()}")
            return decision

        except Exception as e:
            logger.error(f"Error making routing decision: {e}")
            return self._create_fallback_decision(request_analysis)

    def _capability_based_routing(self, analysis: RequestAnalysis) -> RoutingDecision:
        """Route based purely on provider capabilities."""
        scores = {}
        for provider in [ProviderType.KIMI, ProviderType.GLM]:
            scores[provider] = self.capability_registry.get_capability_score(provider, analysis)
        
        # Select provider with highest capability score
        primary_provider = max(scores, key=scores.get)
        fallback_providers = [p for p in scores.keys() if p != primary_provider]
        
        confidence = scores[primary_provider]
        reasoning = f"Selected {primary_provider.value} based on capability score: {confidence:.2f}"
        
        caps = self.capability_registry.capabilities[primary_provider]
        estimated_cost = (analysis.estimated_tokens / 1000) * caps["cost_per_1k_tokens"]
        estimated_time = caps["avg_response_time"]
        
        return RoutingDecision(
            primary_provider=primary_provider,
            fallback_providers=fallback_providers,
            confidence=confidence,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            strategy_used=RoutingStrategy.CAPABILITY_BASED,
            metadata={"capability_scores": {p.value: s for p, s in scores.items()}}
        )

    def _cost_optimized_routing(self, analysis: RequestAnalysis) -> RoutingDecision:
        """Route to minimize cost while maintaining capability."""
        providers_by_cost = []
        
        for provider in [ProviderType.KIMI, ProviderType.GLM]:
            caps = self.capability_registry.capabilities[provider]
            capability_score = self.capability_registry.get_capability_score(provider, analysis)
            
            # Skip providers that can't handle the request
            if capability_score < 0.3:
                continue
                
            cost = (analysis.estimated_tokens / 1000) * caps["cost_per_1k_tokens"]
            providers_by_cost.append((provider, cost, capability_score))
        
        # Sort by cost, then by capability
        providers_by_cost.sort(key=lambda x: (x[1], -x[2]))
        
        if not providers_by_cost:
            return self._create_fallback_decision(analysis)
        
        primary_provider, estimated_cost, capability_score = providers_by_cost[0]
        fallback_providers = [p[0] for p in providers_by_cost[1:]]
        
        reasoning = f"Selected {primary_provider.value} for cost optimization: ${estimated_cost:.4f}"
        
        caps = self.capability_registry.capabilities[primary_provider]
        
        return RoutingDecision(
            primary_provider=primary_provider,
            fallback_providers=fallback_providers,
            confidence=capability_score,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_time=caps["avg_response_time"],
            strategy_used=RoutingStrategy.COST_OPTIMIZED,
            metadata={"cost_comparison": {p[0].value: p[1] for p in providers_by_cost}}
        )

    def _performance_optimized_routing(self, analysis: RequestAnalysis) -> RoutingDecision:
        """Route to minimize response time while maintaining capability."""
        providers_by_speed = []
        
        for provider in [ProviderType.KIMI, ProviderType.GLM]:
            caps = self.capability_registry.capabilities[provider]
            capability_score = self.capability_registry.get_capability_score(provider, analysis)
            
            # Skip providers that can't handle the request
            if capability_score < 0.3:
                continue
                
            response_time = caps["avg_response_time"]
            providers_by_speed.append((provider, response_time, capability_score))
        
        # Sort by response time, then by capability
        providers_by_speed.sort(key=lambda x: (x[1], -x[2]))
        
        if not providers_by_speed:
            return self._create_fallback_decision(analysis)
        
        primary_provider, estimated_time, capability_score = providers_by_speed[0]
        fallback_providers = [p[0] for p in providers_by_speed[1:]]
        
        reasoning = f"Selected {primary_provider.value} for performance: {estimated_time:.1f}s response time"
        
        caps = self.capability_registry.capabilities[primary_provider]
        estimated_cost = (analysis.estimated_tokens / 1000) * caps["cost_per_1k_tokens"]
        
        return RoutingDecision(
            primary_provider=primary_provider,
            fallback_providers=fallback_providers,
            confidence=capability_score,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            strategy_used=RoutingStrategy.PERFORMANCE_OPTIMIZED,
            metadata={"speed_comparison": {p[0].value: p[1] for p in providers_by_speed}}
        )

    def _hybrid_intelligent_routing(self, analysis: RequestAnalysis) -> RoutingDecision:
        """
        Intelligent hybrid routing that balances capability, cost, and performance.
        
        This is the most sophisticated routing strategy that considers multiple factors.
        """
        # Calculate composite scores for each provider
        provider_scores = {}
        
        for provider in [ProviderType.KIMI, ProviderType.GLM]:
            caps = self.capability_registry.capabilities[provider]
            
            # Capability score (40% weight)
            capability_score = self.capability_registry.get_capability_score(provider, analysis)
            
            # Cost score (30% weight) - lower cost = higher score
            cost = (analysis.estimated_tokens / 1000) * caps["cost_per_1k_tokens"]
            cost_score = max(0, 1 - (cost / self.cost_threshold))
            
            # Performance score (30% weight) - faster = higher score
            time_score = max(0, 1 - (caps["avg_response_time"] / self.performance_threshold))
            
            # Composite score
            composite_score = (
                capability_score * 0.4 +
                cost_score * 0.3 +
                time_score * 0.3
            )
            
            provider_scores[provider] = {
                "composite": composite_score,
                "capability": capability_score,
                "cost": cost_score,
                "performance": time_score,
                "estimated_cost": cost,
                "estimated_time": caps["avg_response_time"]
            }
        
        # Select provider with highest composite score
        best_provider = max(provider_scores, key=lambda p: provider_scores[p]["composite"])
        best_scores = provider_scores[best_provider]
        
        # Create fallback list
        fallback_providers = [
            p for p in provider_scores.keys() 
            if p != best_provider and provider_scores[p]["capability"] > 0.3
        ]
        fallback_providers.sort(key=lambda p: provider_scores[p]["composite"], reverse=True)
        
        reasoning = (
            f"Hybrid routing selected {best_provider.value}: "
            f"capability={best_scores['capability']:.2f}, "
            f"cost=${best_scores['estimated_cost']:.4f}, "
            f"time={best_scores['estimated_time']:.1f}s"
        )
        
        return RoutingDecision(
            primary_provider=best_provider,
            fallback_providers=fallback_providers,
            confidence=best_scores["composite"],
            reasoning=reasoning,
            estimated_cost=best_scores["estimated_cost"],
            estimated_time=best_scores["estimated_time"],
            strategy_used=RoutingStrategy.HYBRID_INTELLIGENT,
            metadata={
                "provider_scores": {
                    p.value: scores for p, scores in provider_scores.items()
                }
            }
        )

    def _create_cache_key(self, analysis: RequestAnalysis, strategy: RoutingStrategy) -> str:
        """Create a cache key for routing decisions."""
        key_data = {
            "request_type": analysis.request_type.value,
            "complexity": analysis.complexity.value,
            "has_files": analysis.has_files,
            "has_images": analysis.has_images,
            "has_web_intent": analysis.has_web_intent,
            "token_range": analysis.estimated_tokens // 1000,  # Group by 1K tokens
            "strategy": strategy.value
        }
        return json.dumps(key_data, sort_keys=True)

    def _get_cached_decision(self, cache_key: str) -> Optional[RoutingDecision]:
        """Get cached routing decision if still valid."""
        if cache_key in self._routing_cache:
            decision, timestamp = self._routing_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return decision
            else:
                del self._routing_cache[cache_key]
        return None

    def _cache_decision(self, cache_key: str, decision: RoutingDecision) -> None:
        """Cache a routing decision."""
        # Prevent cache from growing too large
        if len(self._routing_cache) > 100:
            # Remove oldest entries
            oldest_keys = sorted(
                self._routing_cache.keys(),
                key=lambda k: self._routing_cache[k][1]
            )[:20]
            for key in oldest_keys:
                del self._routing_cache[key]
        
        self._routing_cache[cache_key] = (decision, time.time())

    def _create_fallback_decision(self, analysis: RequestAnalysis) -> RoutingDecision:
        """Create a fallback decision when routing fails."""
        # Default to GLM for general cases, Kimi for file operations
        if analysis.has_files or analysis.request_type == RequestType.FILE_OPERATION:
            primary_provider = ProviderType.KIMI
            fallback_providers = [ProviderType.GLM]
        else:
            primary_provider = ProviderType.GLM
            fallback_providers = [ProviderType.KIMI]
        
        caps = self.capability_registry.capabilities[primary_provider]
        estimated_cost = (analysis.estimated_tokens / 1000) * caps["cost_per_1k_tokens"]
        
        return RoutingDecision(
            primary_provider=primary_provider,
            fallback_providers=fallback_providers,
            confidence=0.5,
            reasoning="Fallback routing due to analysis error",
            estimated_cost=estimated_cost,
            estimated_time=caps["avg_response_time"],
            strategy_used=RoutingStrategy.CAPABILITY_BASED,
            metadata={"fallback": True}
        )

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about routing decisions."""
        return {
            "cache_size": len(self._routing_cache),
            "cache_ttl": self._cache_ttl,
            "intelligent_routing_enabled": self.enable_intelligent_routing,
            "cost_threshold": self.cost_threshold,
            "performance_threshold": self.performance_threshold
        }
