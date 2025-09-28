def test_health_circuit_skips_blocked_model(monkeypatch):
    # Setup provider mapping for both models
    from src.providers.registry import ModelProviderRegistry as R
    from src.providers.base import ProviderType

    class FakeProv:
        def __init__(self, p):
            self._p = p
        def get_provider_type(self):
            return ProviderType.GLM if self._p == "glm" else ProviderType.KIMI

    def fake_get_provider_for_model(name: str):
        if name == "glm-4.5-flash":
            return FakeProv("glm")
        if name == "kimi-k2-0711-preview":
            return FakeProv("kimi")
        return None

    monkeypatch.setattr(R, "get_provider_for_model", staticmethod(fake_get_provider_for_model))

    # Block the fast model via health circuit -> should route to long model
    from utils.health import open_circuit
    open_circuit("glm-4.5-flash")

    from src.router.service import RouterService
    svc = RouterService()
    dec = svc.choose_model_with_hint("auto", hint={})
    assert dec.chosen == "kimi-k2-0711-preview"

