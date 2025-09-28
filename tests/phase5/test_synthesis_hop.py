import json
import os


def test_synthesis_hop_logged(monkeypatch):
    # Enable synthesis and routeplan log dir
    monkeypatch.setenv("SYNTHESIS_ENABLED", "true")
    from pathlib import Path
    outdir = Path("docs/System_layout/_raw/synthesis_hop_test_out")
    outdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ROUTEPLAN_LOG_DIR", str(outdir))

    # Fake provider to allow selection
    from src.providers.registry import ModelProviderRegistry as R
    from src.providers.base import ProviderType

    class FakeProv:
        def __init__(self, p):
            self._p = p
        def get_provider_type(self):
            return ProviderType.GLM

    monkeypatch.setattr(R, "get_provider_for_model", staticmethod(lambda name: FakeProv("glm") if name == "glm-4.5-flash" else None))

    # Run choose_model_with_hint to trigger synthesis
    from src.router.service import RouterService
    svc = RouterService()
    dec = svc.choose_model_with_hint("auto", hint={})

    assert dec.meta is None or "synthesis" in dec.meta

    # Verify synthesis hop JSONL event present
    files = sorted(outdir.glob("*.jsonl"))
    assert files, "no routeplan JSONL written"
    all_lines = []
    for f in files:
        all_lines.extend(f.read_text(encoding="utf-8").splitlines())
    assert any(json.loads(l).get("event") == "synthesis_hop" for l in all_lines), "no synthesis_hop event found"

