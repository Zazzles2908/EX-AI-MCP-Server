import json


def test_explicit_available(monkeypatch):
    from src.providers.registry import ModelProviderRegistry as R
    from src.providers.base import ProviderType

    class FakeProv:
        def __init__(self, p):
            self._p = p
        def get_provider_type(self):
            return ProviderType.GLM if self._p == "glm" else ProviderType.KIMI

    monkeypatch.setattr(R, "get_provider_for_model", staticmethod(lambda name: FakeProv("glm") if name == "glm-4.5-flash" else None))

    from src.router.service import RouterService
    svc = RouterService()
    dec = svc.choose_model_with_hint("glm-4.5-flash", hint={})
    assert dec.requested == "glm-4.5-flash"
    assert dec.chosen == "glm-4.5-flash"
    assert dec.reason == "explicit"
    assert dec.provider == "GLM"


def test_explicit_unavailable_fallback(monkeypatch):
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
        return None

    monkeypatch.setattr(R, "get_provider_for_model", staticmethod(fake_get_provider_for_model))

    from src.router.service import RouterService
    svc = RouterService()
    dec = svc.choose_model_with_hint("nonexistent-model", hint={})
    # Fallback to auto selection; it should pick fast default since it's available
    assert dec.chosen == "glm-4.5-flash"
    assert dec.reason.startswith("auto")


def test_auto_then_long_then_first_available(monkeypatch):
    from src.providers.registry import ModelProviderRegistry as R
    from src.providers.base import ProviderType

    class FakeProv:
        def __init__(self, p):
            self._p = p
        def get_provider_type(self):
            return ProviderType.GLM if self._p == "glm" else ProviderType.KIMI

    # Case A: only long available
    monkeypatch.setattr(R, "get_provider_for_model", staticmethod(lambda name: FakeProv("kimi") if name == "kimi-k2-0711-preview" else None))
    from src.router.service import RouterService
    svc = RouterService()
    dec = svc.choose_model_with_hint("auto", hint={})
    assert dec.chosen == "kimi-k2-0711-preview"
    assert dec.reason.startswith("auto")

    # Case B: neither default available -> first available wins
    def fake_get_provider_for_model_none(name: str):
        return None
    monkeypatch.setattr(R, "get_provider_for_model", staticmethod(fake_get_provider_for_model_none))

    # Provide an available models map for fallback path
    monkeypatch.setattr(R, "get_available_models", staticmethod(lambda respect_restrictions=True: {"glm-4.5-flash": ProviderType.GLM}))
    dec2 = svc.choose_model("auto")
    assert dec2.chosen == "glm-4.5-flash"
    assert dec2.reason in ("auto_preferred", "auto_first_available", "explicit")

