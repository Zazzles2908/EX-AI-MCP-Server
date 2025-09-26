"""
RouterService: Intelligent model routing and availability preflight for EX MCP Server.

Enhanced with GLM-4.5 Flash intelligent routing capabilities:
- Request preprocessing and analysis without sending large content to GLM
- Capability-aware provider selection based on request characteristics
- Cost-aware token management and routing optimization
- Smart fallback strategies and caching

- Preflight on startup checks provider/model availability and performs trivial
  chat probes (env-gated) to validate connectivity.
- Decision logging outputs JSON lines via the 'router' logger.
- Intelligent choose_model() policy with GLM Flash AI manager integration.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from typing import Optional, Dict, Any

from src.providers.registry import ModelProviderRegistry as R
from src.providers.base import ProviderType
from src.core.agentic.request_analyzer import RequestAnalyzer, RequestAnalysis
from src.core.agentic.glm_flash_manager import GLMFlashManager, RoutingStrategy

logger = logging.getLogger("router")


@dataclass
class RouteDecision:
    requested: str
    chosen: str
    reason: str
    provider: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps({
            "event": "route_decision",
            "requested": self.requested,
            "chosen": self.chosen,
            "reason": self.reason,
            "provider": self.provider,
            "meta": self.meta or {},
        }, ensure_ascii=False)


class RouterService:
    def __init__(self) -> None:
        # Env-tunable preferred models
        self._fast_default = os.getenv("FAST_MODEL_DEFAULT", "glm-4.5-flash")
        self._long_default = os.getenv("LONG_MODEL_DEFAULT", "kimi-k2-0711-preview")
        # Verbose diagnostics flag (opt-in)
        self._diag_enabled = os.getenv("ROUTER_DIAGNOSTICS_ENABLED", "false").strip().lower() == "true"
        # Minimal JSON logging
        logger.setLevel(getattr(logging, os.getenv("ROUTER_LOG_LEVEL", "INFO").upper(), logging.INFO))
        
        # Initialize intelligent routing components
        self._enable_intelligent_routing = os.getenv("ENABLE_INTELLIGENT_ROUTING", "true").strip().lower() == "true"
        self._request_analyzer = RequestAnalyzer(
            max_summary_tokens=int(os.getenv("ROUTING_SUMMARY_MAX_TOKENS", "500"))
        )
        self._glm_flash_manager = GLMFlashManager(
            enable_intelligent_routing=self._enable_intelligent_routing,
            cost_threshold=float(os.getenv("ROUTING_COST_THRESHOLD", "0.10")),
            performance_threshold=float(os.getenv("ROUTING_PERFORMANCE_THRESHOLD", "5.0"))
        )
        
        # Routing strategy configuration
        strategy_name = os.getenv("ROUTING_STRATEGY", "hybrid_intelligent").lower()
        self._routing_strategy = {
            "capability_based": RoutingStrategy.CAPABILITY_BASED,
            "cost_optimized": RoutingStrategy.COST_OPTIMIZED,
            "performance_optimized": RoutingStrategy.PERFORMANCE_OPTIMIZED,
            "hybrid_intelligent": RoutingStrategy.HYBRID_INTELLIGENT
        }.get(strategy_name, RoutingStrategy.HYBRID_INTELLIGENT)
        
        logger.info(f"RouterService initialized with intelligent routing: {self._enable_intelligent_routing}, strategy: {self._routing_strategy.value}")

    def preflight(self) -> None:
        """Check provider readiness and log available models; optionally probe chat."""
        try:
            avail = R.get_available_models(respect_restrictions=True)
            by_provider: Dict[str, list[str]] = {}
            for name, ptype in avail.items():
                by_provider.setdefault(ptype.name, []).append(name)
            logger.info(json.dumps({
                "event": "preflight_models",
                "providers": {k: sorted(v) for k, v in by_provider.items()},
            }, ensure_ascii=False))
        except Exception as e:
            logger.warning(json.dumps({"event": "preflight_models_error", "error": str(e)}))

        # Optional trivial chat probe (env: ROUTER_PREFLIGHT_CHAT=true)
        if (os.getenv("ROUTER_PREFLIGHT_CHAT", "true").strip().lower() == "true"):
            self._probe_chat_safely()

    def _probe_chat_safely(self) -> None:
        prompt = "ping"
        for candidate in [self._fast_default, self._long_default]:
            prov = R.get_provider_for_model(candidate)
            if not prov:
                continue
            try:
                # Short, cheap call with small max_output_tokens when supported
                resp = prov.generate_content(prompt=prompt, model_name=candidate, max_output_tokens=8, temperature=0)
                logger.info(json.dumps({
                    "event": "preflight_chat_ok",
                    "model": candidate,
                    "provider": prov.get_provider_type().name,
                    "usage": getattr(resp, "usage", None) or {},
                }, ensure_ascii=False))
            except Exception as e:
                logger.warning(json.dumps({
                    "event": "preflight_chat_fail",
                    "model": candidate,
                    "provider": getattr(prov, "get_provider_type", lambda: type("X", (), {"name":"unknown"}))().name,
                    "error": str(e),
                }, ensure_ascii=False))

    def accept_agentic_hint(self, hint: Optional[Dict[str, Any]]) -> list[str]:
        """Translate an optional agentic hint into an ordered list of preferred candidates.

        Hint schema (best-effort):
        - platform: one of {"zai","moonshot","kimi"}
        - task_type: values used by agentic router (e.g., "long_context_analysis", "multimodal_reasoning")
        - preferred_models: optional explicit list of model names to try first
        """
        candidates: list[str] = []
        if not hint:
            return candidates

        # 1) Explicit models take top priority
        pref = hint.get("preferred_models")
        if isinstance(pref, list):
            for m in pref:
                if isinstance(m, str) and m:
                    candidates.append(m)

        # 2) Platform / task-type guidance
        platform = str(hint.get("platform") or "").lower()
        task_type = str(hint.get("task_type") or "").lower()
        # Long-context leaning
        if platform in ("moonshot", "kimi") or "long_context" in task_type:
            for m in (self._long_default, self._fast_default):
                if m and m not in candidates:
                    candidates.append(m)
        else:
            # Default lean fast
            for m in (self._fast_default, self._long_default):
                if m and m not in candidates:
                    candidates.append(m)
        return candidates

    def choose_model_with_hint(self, requested: Optional[str], hint: Optional[Dict[str, Any]] = None) -> RouteDecision:
        """Resolve a model name with optional agentic hint influence.

        Backward compatible: callers can continue using choose_model().
        """
        req = (requested or "auto").strip()
        if req.lower() != "auto":
            prov = R.get_provider_for_model(req)
            if prov is not None:
                dec = RouteDecision(requested=req, chosen=req, reason="explicit", provider=prov.get_provider_type().name)
                logger.info(dec.to_json())
                return dec
            logger.info(json.dumps({"event": "route_explicit_unavailable", "requested": req}))

        # Build candidate order from hint + defaults
        hint_candidates = self.accept_agentic_hint(hint)
        default_order = [self._fast_default, self._long_default]
        order: list[str] = []
        for m in (*hint_candidates, *default_order):
            if isinstance(m, str) and m and m not in order:
                order.append(m)

        # Optional detailed diagnostics
        if self._diag_enabled:
            try:
                avail = R.get_available_models(respect_restrictions=True)
                by_provider: Dict[str, int] = {}
                for _, ptype in avail.items():
                    by_provider[ptype.name] = by_provider.get(ptype.name, 0) + 1
                logger.info(json.dumps({
                    "event": "route_diagnostics",
                    "requested": req,
                    "hint_candidates": hint_candidates,
                    "default_order": default_order,
                    "order": order,
                    "available_providers_counts": by_provider,
                }, ensure_ascii=False))
            except Exception as e:
                logger.debug(json.dumps({"event": "route_diagnostics_error", "error": str(e)}))

        for candidate in order:
            prov = R.get_provider_for_model(candidate)
            if prov is not None:
                reason = "auto_hint_applied" if hint_candidates else "auto_preferred"
                dec = RouteDecision(requested=req, chosen=candidate, reason=reason, provider=prov.get_provider_type().name, meta={"hint": bool(hint_candidates)})
                logger.info(dec.to_json())
                return dec

        # Fallback to generic behavior
        return self.choose_model(req)

    def choose_model_intelligent(self, 
                               requested: Optional[str], 
                               request_data: Optional[Dict[str, Any]] = None,
                               hint: Optional[Dict[str, Any]] = None) -> RouteDecision:
        """
        Intelligent model selection using GLM-4.5 Flash AI manager.
        
        This method analyzes the request content and uses intelligent routing
        to select the optimal provider based on capabilities, cost, and performance.
        
        Args:
            requested: Explicitly requested model name or 'auto'
            request_data: Full request data for analysis
            hint: Optional agentic hint for routing
            
        Returns:
            RouteDecision with intelligent provider selection
        """
        req = (requested or "auto").strip()
        
        # Handle explicit model requests first
        if req.lower() != "auto":
            prov = R.get_provider_for_model(req)
            if prov is not None:
                dec = RouteDecision(
                    requested=req, 
                    chosen=req, 
                    reason="explicit_intelligent", 
                    provider=prov.get_provider_type().name
                )
                logger.info(dec.to_json())
                return dec
            logger.info(json.dumps({"event": "route_explicit_unavailable", "requested": req}))

        # Use intelligent routing if enabled and request data is available
        if self._enable_intelligent_routing and request_data:
            try:
                return self._intelligent_route_selection(request_data, hint)
            except Exception as e:
                logger.warning(f"Intelligent routing failed, falling back to hint-based: {e}")
                return self.choose_model_with_hint(req, hint)
        
        # Fallback to hint-based routing
        return self.choose_model_with_hint(req, hint)

    def _intelligent_route_selection(self, 
                                   request_data: Dict[str, Any], 
                                   hint: Optional[Dict[str, Any]] = None) -> RouteDecision:
        """
        Perform intelligent route selection using request analysis and GLM Flash manager.
        
        Args:
            request_data: Full request data for analysis
            hint: Optional agentic hint
            
        Returns:
            RouteDecision with intelligent routing
        """
        # Analyze the request
        request_analysis = self._request_analyzer.analyze_request(request_data)
        
        logger.info(json.dumps({
            "event": "intelligent_routing_analysis",
            "analysis": request_analysis.to_dict()
        }, ensure_ascii=False))
        
        # Get routing decision from GLM Flash manager
        routing_decision = self._glm_flash_manager.make_routing_decision(
            request_analysis, 
            self._routing_strategy
        )
        
        logger.info(json.dumps({
            "event": "intelligent_routing_decision",
            "decision": routing_decision.to_dict()
        }, ensure_ascii=False))
        
        # Convert routing decision to RouteDecision
        return self._convert_routing_decision(routing_decision, request_analysis, hint)

    def _convert_routing_decision(self, 
                                routing_decision, 
                                request_analysis: RequestAnalysis,
                                hint: Optional[Dict[str, Any]] = None) -> RouteDecision:
        """
        Convert GLM Flash routing decision to RouterService RouteDecision.
        
        Args:
            routing_decision: Decision from GLM Flash manager
            request_analysis: Original request analysis
            hint: Optional agentic hint
            
        Returns:
            RouteDecision compatible with existing router interface
        """
        # Map provider type to model name
        provider_to_model = {
            routing_decision.primary_provider: self._get_preferred_model_for_provider(
                routing_decision.primary_provider, request_analysis
            )
        }
        
        chosen_model = provider_to_model[routing_decision.primary_provider]
        
        # Verify model availability
        prov = R.get_provider_for_model(chosen_model)
        if prov is None:
            # Fallback to traditional routing
            logger.warning(f"Intelligent routing selected unavailable model {chosen_model}, falling back")
            return self.choose_model_with_hint("auto", hint)
        
        # Create enhanced RouteDecision with intelligent routing metadata
        reason = f"intelligent_{routing_decision.strategy_used.value}"
        meta = {
            "intelligent_routing": True,
            "request_analysis": request_analysis.to_dict(),
            "routing_decision": routing_decision.to_dict(),
            "estimated_cost": routing_decision.estimated_cost,
            "estimated_time": routing_decision.estimated_time,
            "confidence": routing_decision.confidence
        }
        
        dec = RouteDecision(
            requested="auto",
            chosen=chosen_model,
            reason=reason,
            provider=prov.get_provider_type().name,
            meta=meta
        )
        
        logger.info(dec.to_json())
        return dec

    def _get_preferred_model_for_provider(self, 
                                        provider_type: ProviderType, 
                                        request_analysis: RequestAnalysis) -> str:
        """
        Get the preferred model for a provider type based on request analysis.
        
        Args:
            provider_type: The provider type selected by intelligent routing
            request_analysis: Analysis of the request
            
        Returns:
            Preferred model name for the provider
        """
        if provider_type == ProviderType.GLM:
            # For GLM, prefer flash for general use, regular for complex tasks
            if request_analysis.complexity.value in ["very_complex", "complex"]:
                return os.getenv("GLM_COMPLEX_MODEL", "glm-4.5")
            return self._fast_default
        
        elif provider_type == ProviderType.KIMI:
            # For Kimi, prefer latest preview models for file operations
            if request_analysis.has_files:
                return os.getenv("KIMI_FILE_MODEL", "kimi-k2-0905-preview")
            return self._long_default
        
        # Fallback to fast default
        return self._fast_default

    def get_routing_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive routing statistics including intelligent routing metrics.
        
        Returns:
            Dictionary with routing statistics and performance metrics
        """
        stats = {
            "intelligent_routing_enabled": self._enable_intelligent_routing,
            "routing_strategy": self._routing_strategy.value,
            "fast_default_model": self._fast_default,
            "long_default_model": self._long_default,
            "diagnostics_enabled": self._diag_enabled
        }
        
        # Add GLM Flash manager statistics if available
        if hasattr(self, '_glm_flash_manager'):
            stats.update(self._glm_flash_manager.get_routing_statistics())
        
        return stats

    def update_routing_strategy(self, strategy: RoutingStrategy) -> None:
        """
        Update the routing strategy at runtime.
        
        Args:
            strategy: New routing strategy to use
        """
        self._routing_strategy = strategy
        logger.info(f"Routing strategy updated to: {strategy.value}")

    def analyze_request_preview(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview request analysis without making routing decisions.
        
        Useful for debugging and understanding how requests would be routed.
        
        Args:
            request_data: Request data to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not self._enable_intelligent_routing:
            return {"error": "Intelligent routing not enabled"}
        
        try:
            analysis = self._request_analyzer.analyze_request(request_data)
            routing_decision = self._glm_flash_manager.make_routing_decision(
                analysis, self._routing_strategy
            )
            
            return {
                "request_analysis": analysis.to_dict(),
                "routing_decision": routing_decision.to_dict(),
                "recommended_model": self._get_preferred_model_for_provider(
                    routing_decision.primary_provider, analysis
                )
            }
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}

    def choose_model(self, requested: Optional[str]) -> RouteDecision:
        """Resolve a model name. If 'auto' or empty, choose a sensible default based on availability."""
        req = (requested or "auto").strip()
        if req.lower() != "auto":
            # Honor explicit request if available
            prov = R.get_provider_for_model(req)
            if prov is not None:
                dec = RouteDecision(requested=req, chosen=req, reason="explicit", provider=prov.get_provider_type().name)
                logger.info(dec.to_json())
                return dec
            # Fallback if explicit is unknown
            logger.info(json.dumps({"event": "route_explicit_unavailable", "requested": req}))
        # Auto selection policy: prefer fast GLM, else Kimi long-context, else any available
        for candidate in [self._fast_default, self._long_default]:
            prov = R.get_provider_for_model(candidate)
            if prov is not None:
                dec = RouteDecision(requested=req, chosen=candidate, reason="auto_preferred", provider=prov.get_provider_type().name)
                logger.info(dec.to_json())
                return dec
        # Last resort: pick first available model
        try:
            avail = R.get_available_models(respect_restrictions=True)
            if avail:
                first = sorted(avail.keys())[0]
                prov = R.get_provider_for_model(first)
                dec = RouteDecision(requested=req, chosen=first, reason="auto_first_available", provider=(prov.get_provider_type().name if prov else None))
                logger.info(dec.to_json())
                return dec
        except Exception:
            pass
        # No models available
        dec = RouteDecision(requested=req, chosen=req, reason="no_models_available", provider=None)
        logger.warning(dec.to_json())
        return dec

