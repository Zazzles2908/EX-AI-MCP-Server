import os


def test_routing_hints_bias_fast_vs_long(monkeypatch):
    # Fix defaults for deterministic behavior
    monkeypatch.setenv("FAST_MODEL_DEFAULT", "glm-4.5-flash")
    monkeypatch.setenv("LONG_MODEL_DEFAULT", "kimi-k2-0711-preview")

    # Fake providers for these models
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

    from src.router.service import RouterService
    svc = RouterService()

    # Quick chat bias -> GLM fast
    hint_fast = svc.build_hint_from_request(prompt="short", files_count=0, images_count=0)
    dec_fast = svc.choose_model_with_hint("auto", hint=hint_fast)
    assert dec_fast.chosen == "glm-4.5-flash"
    assert dec_fast.reason.startswith("auto")

    # Long context bias -> Kimi long
    hint_long = svc.build_hint_from_request(prompt="x"*2000, files_count=3)
    dec_long = svc.choose_model_with_hint("auto", hint=hint_long)
    assert dec_long.chosen == "kimi-k2-0711-preview"
    assert dec_long.reason.startswith("auto")

