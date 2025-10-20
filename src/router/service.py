"""
RouterService: central model routing and availability preflight for EX MCP Server.

- Preflight on startup checks provider/model availability and performs trivial
  chat probes (env-gated) to validate connectivity.
- Decision logging outputs JSON lines via the 'router' logger.
- Simple choose_model() policy that honors explicit model requests and falls back
  to preferred fast model (GLM) or long-context model (Kimi) when 'auto'.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from typing import Optional, Dict, Any

from src.providers.registry import ModelProviderRegistry as R
from src.providers.base import ProviderType
from src.router.routing_cache import get_routing_cache

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
        # Routing cache for performance optimization
        self._routing_cache = get_routing_cache()

    def preflight(self) -> None:
        """Check provider readiness and log available models; optionally probe chat."""
        try:
            avail = R.get_available_models(respect_restrictions=True)
            by_provider: Dict[str, list[str]] = {}
            for name, ptype in avail.items():
                by_provider.setdefault(ptype.name, []).append(name)
                # Cache provider availability status (5min TTL)
                self._routing_cache.set_provider_status(
                    ptype.name,
                    {"available": True, "models": sorted(by_provider[ptype.name])}
                )
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

    def _filter_by_budget(self, models: list[str], budget_usd: Optional[float]) -> list[str]:
        """Filter model list by per-request budget using MODEL_COSTS_JSON when present."""
        if not budget_usd:
            return models
        try:
            import json as _json
            costs = _json.loads(os.getenv("MODEL_COSTS_JSON", "{}")) or {}
            allowed = []
            for m in models:
                c = costs.get(m)
                # If cost unknown, allow but move to end later
                if c is None or float(c) <= float(budget_usd):
                    allowed.append(m)
            # Preserve original order
            return [m for m in models if m in allowed]
        except Exception:
            return models

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

        # Try cache for auto routing (3min TTL)
        if req.lower() == "auto":
            cache_context = {"requested": req, "hint": hint or {}}
            cached_model = self._routing_cache.get_model_selection(cache_context)
            if cached_model:
                prov = R.get_provider_for_model(cached_model)
                if prov is not None:
                    dec = RouteDecision(
                        requested=req,
                        chosen=cached_model,
                        reason="auto_cached",
                        provider=prov.get_provider_type().name,
                        meta={"cached": True}
                    )
                    logger.debug(f"[ROUTING_CACHE] Model selection cache HIT: {cached_model}")
                    return dec

        # Build candidate order from hint + defaults, then apply budget filter if present
        hint_candidates = self.accept_agentic_hint(hint)
        default_order = [self._fast_default, self._long_default]
        order: list[str] = []
        for m in (*hint_candidates, *default_order):
            if isinstance(m, str) and m and m not in order:
                order.append(m)
        try:
            budget = None
            if hint and isinstance(hint.get("budget"), (int, float)):
                budget = float(hint.get("budget"))
            order = self._filter_by_budget(order, budget)
        except Exception:
            pass

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

        # Health circuit filter: skip candidates with open circuits
        try:
            from utils.infrastructure.health import is_blocked
        except Exception:
            is_blocked = None

        for candidate in order:
            if is_blocked and is_blocked(candidate):
                # skip blocked model
                continue
            prov = R.get_provider_for_model(candidate)
            if prov is not None:
                reason = "auto_hint_applied" if hint_candidates else "auto_preferred"
                budget_val = None
                try:
                    budget_val = float(hint.get("budget")) if hint and isinstance(hint.get("budget"), (int, float)) else None
                except (TypeError, ValueError, AttributeError) as e:
                    logger.debug(f"Failed to parse budget from hint: {e}")
                    budget_val = None
                meta = {"hint": bool(hint_candidates)}
                if budget_val is not None:
                    meta["budget"] = budget_val
                dec = RouteDecision(requested=req, chosen=candidate, reason=reason, provider=prov.get_provider_type().name, meta=meta)
                logger.info(dec.to_json())

                # Cache the model selection (3min TTL)
                if req.lower() == "auto":
                    cache_context = {"requested": req, "hint": hint or {}}
                    self._routing_cache.set_model_selection(cache_context, candidate)
                    logger.debug(f"[ROUTING_CACHE] Cached model selection: {candidate}")
                try:
                    # Optional synthesis hop (Phase 5 optional)
                    try:
                        from src.router.synthesis import synthesize_if_enabled
                        syn = synthesize_if_enabled(dec, None, hint or {})
                        if syn:
                            dec.meta = dec.meta or {}
                            dec.meta["synthesis"] = syn
                    except ImportError as e:
                        logger.debug(f"Synthesis module not available: {e}")
                    except Exception as e:
                        logger.warning(f"Synthesis hop failed: {e}")
                    from utils.observability import append_routeplan_jsonl, append_synthesis_hop_jsonl, emit_telemetry_jsonl
                    append_routeplan_jsonl({
                        "requested": dec.requested,
                        "chosen": dec.chosen,
                        "reason": dec.reason,
                        "provider": dec.provider,
                        "meta": dec.meta or {},
                    })
                    # Emit a telemetry event per decision
                    try:
                        emit_telemetry_jsonl({
                            "provider": dec.provider,
                            "model": dec.chosen,
                            "hint": bool(hint_candidates),
                            "budget": budget_val,
                            "synthesis": bool(dec.meta and dec.meta.get("synthesis")),
                        })
                    except (OSError, IOError, PermissionError) as e:
                        logger.debug(f"Failed to emit telemetry: {e}")
                    except Exception as e:
                        logger.warning(f"Unexpected error emitting telemetry: {e}")
                    # If synthesis metadata present, also log an explicit synthesis hop record
                    try:
                        if dec.meta and dec.meta.get("synthesis"):
                            append_synthesis_hop_jsonl({
                                "chosen": dec.meta["synthesis"].get("model"),
                                "primary": dec.chosen,
                                "reason": dec.meta["synthesis"].get("reason"),
                            })
                    except (OSError, IOError, PermissionError) as e:
                        logger.debug(f"Failed to append synthesis hop: {e}")
                    except Exception as e:
                        logger.warning(f"Unexpected error appending synthesis hop: {e}")
                except (ImportError, AttributeError) as e:
                    logger.debug(f"Observability module not fully available: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error in observability logging: {e}")
                return dec

        # Fallback to generic behavior
        return self.choose_model(req)
    def build_hint_from_request(self, prompt: str | None = None, files_count: int = 0, images_count: int = 0) -> Dict[str, Any]:
        """Produce an agentic hint dict using the classifier output.
        Does not make routing decisions directly; callers can pass this to choose_model_with_hint().
        """
        try:
            from .classifier import classify
            res = classify(prompt or "", files_count=files_count, images_count=images_count)
            platform = "moonshot" if res.task_type == "long_context_analysis" else "zai"
            return {
                "platform": platform,
                "task_type": res.task_type,
                "preferred_models": [],
                "classification": {
                    "complexity": res.complexity,
                    "est_tokens": res.est_tokens,
                },
            }
        except ImportError as e:
            logger.debug(f"Classifier module not available: {e}")
            return {}
        except (AttributeError, TypeError) as e:
            logger.debug(f"Failed to build hint from classifier: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Unexpected error building hint: {e}")
            return {}


    def choose_model(self, requested: Optional[str]) -> RouteDecision:
        """Resolve a model name. If 'auto' or empty, choose a sensible default based on availability."""
        req = (requested or "auto").strip()
        if req.lower() != "auto":
            # Honor explicit request if available
            prov = R.get_provider_for_model(req)
            if prov is not None:
                dec = RouteDecision(requested=req, chosen=req, reason="explicit", provider=prov.get_provider_type().name)
                logger.info(dec.to_json())
                try:
                    from utils.observability import append_routeplan_jsonl
                    append_routeplan_jsonl({
                        "requested": dec.requested,
                        "chosen": dec.chosen,
                        "reason": dec.reason,
                        "provider": dec.provider,
                        "meta": dec.meta or {},
                    })
                except (ImportError, AttributeError) as e:
                    logger.debug(f"Observability module not available: {e}")
                except (OSError, IOError, PermissionError) as e:
                    logger.debug(f"Failed to append routeplan: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error appending routeplan: {e}")
                return dec
            # Fallback if explicit is unknown
            logger.info(json.dumps({"event": "route_explicit_unavailable", "requested": req}))
        # Auto selection policy: prefer fast GLM, else Kimi long-context, else any available
        for candidate in [self._fast_default, self._long_default]:
            prov = R.get_provider_for_model(candidate)
            if prov is not None:
                dec = RouteDecision(requested=req, chosen=candidate, reason="auto_preferred", provider=prov.get_provider_type().name)
                logger.info(dec.to_json())
                try:
                    from utils.observability import append_routeplan_jsonl
                    append_routeplan_jsonl({
                        "requested": dec.requested,
                        "chosen": dec.chosen,
                        "reason": dec.reason,
                        "provider": dec.provider,
                        "meta": dec.meta or {},
                    })
                except (ImportError, AttributeError) as e:
                    logger.debug(f"Observability module not available: {e}")
                except (OSError, IOError, PermissionError) as e:
                    logger.debug(f"Failed to append routeplan: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error appending routeplan: {e}")
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
        except (AttributeError, KeyError, TypeError) as e:
            logger.debug(f"Failed to get first available model: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error getting available models: {e}")
        # No models available
        dec = RouteDecision(requested=req, chosen=req, reason="no_models_available", provider=None)
        logger.warning(dec.to_json())
        try:
            from utils.observability import append_routeplan_jsonl
            append_routeplan_jsonl({
                "requested": dec.requested,
                "chosen": dec.chosen,
                "reason": dec.reason,
                "provider": dec.provider,
                "meta": dec.meta or {},
            })
        except (ImportError, AttributeError) as e:
            logger.debug(f"Observability module not available: {e}")
        except (OSError, IOError, PermissionError) as e:
            logger.debug(f"Failed to append routeplan: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error appending routeplan: {e}")
        return dec

