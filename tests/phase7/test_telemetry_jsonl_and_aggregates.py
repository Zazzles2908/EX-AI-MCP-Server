import json
from pathlib import Path


def test_telemetry_and_aggregate(monkeypatch):
    outdir = Path("docs/System_layout/_raw/telemetry_test_out")
    outdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("TELEMETRY_LOG_DIR", str(outdir))

    # Fake providers
    from src.providers.registry import ModelProviderRegistry as R
    from src.providers.base import ProviderType

    class FakeProv:
        def __init__(self, p):
            self._p = p
        def get_provider_type(self):
            return ProviderType.GLM

    monkeypatch.setattr(R, "get_provider_for_model", staticmethod(lambda name: FakeProv("glm") if name == "glm-4.5-flash" else None))

    # Route once to produce telemetry
    from src.router.service import RouterService
    svc = RouterService()
    dec = svc.choose_model_with_hint("auto", hint={})
    assert dec.chosen

    # Now roll up aggregates
    from utils.observability import rollup_aggregates
    agg_path = rollup_aggregates(input_dir=str(outdir), output_dir=str(outdir / "aggregates"))
    assert agg_path
    data = json.loads(Path(agg_path).read_text(encoding="utf-8"))
    assert "glm-4.5-flash" in data["counts"].get("GLM", {})

