"""
Phase 5 optional: synthesis hop for secondary GLM summarization.

Currently best-effort: records an observability event and returns synthesis metadata.
Provider calls are intentionally not made here to keep unit tests offline.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import os


def synthesize_if_enabled(decision, primary_text: Optional[str], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return synthesis metadata when enabled; log a synthesis hop event via observability.

    Env: SYNTHESIS_ENABLED=true to enable.
    Model: SYNTHESIS_MODEL (default glm-4.5-flash)
    Reason: basic static reason for now; callers may enrich.
    """
    try:
        enabled = os.getenv("SYNTHESIS_ENABLED", "false").strip().lower() in ("1","true","yes")
        if not enabled:
            return None
        model = os.getenv("SYNTHESIS_MODEL", "glm-4.5-flash")
        reason = "secondary synthesis hop for improved finalization"
        # Write a synthesis hop line
        try:
            from utils.observability import append_synthesis_hop_jsonl
            append_synthesis_hop_jsonl({
                "primary": getattr(decision, "chosen", None),
                "chosen": model,
                "reason": reason,
                "hint": bool(hint),
            })
        except Exception:
            pass
        return {"enabled": True, "model": model, "reason": reason}
    except Exception:
        return None

