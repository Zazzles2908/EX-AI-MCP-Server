"""
Consensus tool validation - Step 1 validation logic

This module contains validation logic for the consensus workflow tool,
specifically for validating models, steps, and files in step 1.
"""

import os
from src.providers.registry_core import get_registry_instance


def validate_consensus_step_one(request) -> None:
    """
    Validate models, steps, and files for consensus step 1.

    Args:
        request: ConsensusRequest object for step 1

    Raises:
        ValueError: If validation fails with user-friendly message
    """
    # Validate models list (be tolerant of legacy mocks)
    models = request.models if isinstance(getattr(request, "models", None), list) else []
    if not models:
        raise ValueError("Step 1 requires 'models' with at least one entry")
    total_steps = getattr(request, "total_steps", None)
    if isinstance(total_steps, int) and total_steps and total_steps != len(models):
        raise ValueError(f"total_steps ({total_steps}) must equal len(models) ({len(models)}) in step 1")

    # Validate each model availability
    from src.providers.registry import ModelProviderRegistry

    unavailable: list[str] = []
    for m in models:
        name = m.get("model")
        if not name:
            unavailable.append("<missing model name>")
            continue
        # Hidden-router resolution for 'auto' or sentinel models
        resolved = name
        try:
            hidden_enabled = os.getenv("HIDDEN_MODEL_ROUTER_ENABLED", "true").strip().lower() == "true"
            sentinels = {
                s.strip().lower()
                for s in os.getenv("ROUTER_SENTINEL_MODELS", "glm-4.5-flash,auto").split(",")
                if s.strip()
            }
            if hidden_enabled and name.strip().lower() in sentinels:
                from src.providers.registry import ModelProviderRegistry as _Reg

                routed = _Reg.get_preferred_fallback_model(None)
                if routed:
                    resolved = routed
                    try:
                        import logging as _logging

                        _logging.getLogger("consensus").info(
                            f"EVENT consensus_model_routed input_model={name} resolved_model={resolved}"
                        )
                    except Exception:
                        pass
        except Exception:
            pass
        provider = get_registry_instance().get_provider_for_model(resolved)
        if not provider:
            unavailable.append(name)
        else:
            # Persist resolved model for execution phase
            m["resolved_model"] = resolved
    if unavailable:
        available = ModelProviderRegistry.get_available_model_names()
        raise ValueError(
            "Some models are not available: "
            + ", ".join(unavailable)
            + ". Available models: "
            + ", ".join(available)
        )

    # Validate files are absolute and readable if provided
    files = request.relevant_files or []
    bad: list[str] = []
    for f in files:
        try:
            if not f or not os.path.isabs(f) or not os.path.isfile(f) or not os.access(f, os.R_OK):
                bad.append(f)
        except Exception:
            bad.append(f)
    if bad:
        raise ValueError("Some relevant_files are not absolute/readable: " + ", ".join(bad))


__all__ = ["validate_consensus_step_one"]

