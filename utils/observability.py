"""
Lightweight JSONL observability helpers for EX MCP Server.

- record_token_usage: append token usage records to EX_METRICS_LOG_PATH
- record_file_count: append file count delta events to EX_METRICS_LOG_PATH
- record_error: append error events to EX_METRICS_LOG_PATH

Designed to be best-effort and non-intrusive. Failures are swallowed.
"""
from __future__ import annotations

import json
import os
import time
from typing import Optional


def _log_path() -> str:
    p = os.getenv("EX_METRICS_LOG_PATH", ".logs/metrics.jsonl").strip()
    # allow env to disable by setting empty
    return p


def _write_jsonl(obj: dict) -> None:
    path = _log_path()
    if not path:
        return
    try:
        base = os.path.dirname(path)
        if base and not os.path.exists(base):
            os.makedirs(base, exist_ok=True)
        obj.setdefault("t", time.time())
        line = json.dumps(obj, ensure_ascii=False)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # observability must never break flows
        pass


def record_token_usage(provider: str, model: str, input_tokens: int = 0, output_tokens: int = 0) -> None:
    try:
        _write_jsonl({
            "event": "token_usage",
            "provider": provider,
            "model": model,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
        })
    except Exception:
        pass


def record_file_count(provider: str, delta: int) -> None:
    try:
        _write_jsonl({
            "event": "file_count_delta",
            "provider": provider,
            "delta": int(delta),
        })
    except Exception:
        pass


def record_error(provider: str, model: str, error_type: str, message: Optional[str] = None) -> None:
    try:
        _write_jsonl({
            "event": "provider_error",
            "provider": provider,
            "model": model,
            "error_type": str(error_type),
            "message": message or "",
        })
    except Exception:
        pass


def record_cache_hit(provider: str, sha: Optional[str] = None) -> None:
    try:
        obj = {"event": "file_cache", "action": "hit", "provider": provider}
        if sha:
            obj["sha"] = sha
        _write_jsonl(obj)
    except Exception:
        pass


def record_cache_miss(provider: str, sha: Optional[str] = None) -> None:
    try:
        obj = {"event": "file_cache", "action": "miss", "provider": provider}
        if sha:
            obj["sha"] = sha
        _write_jsonl(obj)
    except Exception:
        pass



# Route plan JSONL enrichment

def append_routeplan_jsonl(event: dict) -> None:
    """Append a single JSON line capturing route plan / decision details.
    Writes to logs/routeplan/<YYYY-MM-DD>.jsonl (configurable via ROUTEPLAN_LOG_DIR).
    """
    try:
        import datetime as _dt
        from pathlib import Path
        base = Path(os.getenv("ROUTEPLAN_LOG_DIR", "logs/routeplan"))
        base.mkdir(parents=True, exist_ok=True)
        fname = _dt.datetime.utcnow().strftime("%Y-%m-%d") + ".jsonl"
        fpath = base / fname
        payload = {"event": "route_plan", "ts": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", **(event or {})}
        with fpath.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Never break routing
        pass


# Synthesis hop JSONL logging

def append_synthesis_hop_jsonl(event: dict) -> None:
    """Append a synthesis hop record under logs/routeplan as well for timeline continuity."""
    try:
        import datetime as _dt
        from pathlib import Path
        base = Path(os.getenv("ROUTEPLAN_LOG_DIR", "logs/routeplan"))
        base.mkdir(parents=True, exist_ok=True)
        fname = _dt.datetime.utcnow().strftime("%Y-%m-%d") + ".jsonl"
        fpath = base / fname
        payload = {"event": "synthesis_hop", "ts": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", **(event or {})}
        with fpath.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


# Telemetry JSONL and aggregates (Phase 7)

def emit_telemetry_jsonl(event: dict) -> None:
    """Append a telemetry event under logs/telemetry/<YYYY-MM-DD>.jsonl (TELEMETRY_LOG_DIR).
    Best-effort; swallows errors.
    """
    try:
        import datetime as _dt
        from pathlib import Path
        base = Path(os.getenv("TELEMETRY_LOG_DIR", "logs/telemetry"))
        base.mkdir(parents=True, exist_ok=True)
        fname = _dt.datetime.utcnow().strftime("%Y-%m-%d") + ".jsonl"
        fpath = base / fname
        payload = {"event": "telemetry", "ts": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", **(event or {})}
        with fpath.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def rollup_aggregates(input_dir: str | None = None, output_dir: str | None = None) -> str | None:
    """Create a simple aggregate JSON with counts per provider/model for the current day.
    Returns the path to the aggregate file when successful.
    """
    try:
        import datetime as _dt
        from pathlib import Path
        base = Path(input_dir or os.getenv("TELEMETRY_LOG_DIR", "logs/telemetry"))
        out_base = Path(output_dir or (str(base / "aggregates")))
        out_base.mkdir(parents=True, exist_ok=True)
        today = _dt.datetime.utcnow().strftime("%Y-%m-%d")
        in_path = base / f"{today}.jsonl"
        if not in_path.exists():
            return None
        counts: dict[str, dict[str, int]] = {}
        with in_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get("event") != "telemetry":
                        continue
                    prov = str(obj.get("provider") or "unknown")
                    model = str(obj.get("model") or "unknown")
                    counts.setdefault(prov, {})
                    counts[prov][model] = counts[prov].get(model, 0) + 1
                except Exception:
                    continue
        out_path = out_base / f"{today}.json"
        with out_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"date": today, "counts": counts}, ensure_ascii=False, indent=2))
        return str(out_path)
    except Exception:
        return None
