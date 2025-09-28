import json
import os
from types import SimpleNamespace

import pytest


def test_budget_filters_candidate_order(monkeypatch):
    # Arrange model costs and log dir
    monkeypatch.setenv("MODEL_COSTS_JSON", json.dumps({
        "glm-4.5-flash": 0.02,
        "kimi-k2-0711-preview": 0.50,
    }))
    from pathlib import Path
    outdir = Path("docs/System_layout/_raw/routeplan_budget_test_out")
    outdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ROUTEPLAN_LOG_DIR", str(outdir))

    # Fake providers for both models
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

    # Act
    from src.router.service import RouterService
    svc = RouterService()
    dec = svc.choose_model_with_hint("auto", hint={"budget": 0.03})

    # Assert: budget steers selection to cheaper GLM
    assert dec.chosen == "glm-4.5-flash"

    # And JSONL includes meta.budget
    files = sorted(outdir.glob("*.jsonl"))
    assert files, "routeplan JSONL not written"
    data = json.loads(files[0].read_text(encoding="utf-8").strip().splitlines()[-1])
    assert data["event"] == "route_plan"
    assert data["meta"].get("budget") == 0.03


import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_chat_stream_flag_toggles_env(monkeypatch):
    # Ensure baseline streaming disabled
    monkeypatch.setenv("GLM_STREAM_ENABLED", "false")

    from tools.chat import ChatTool, ChatRequest

    tool = ChatTool()
    req = ChatRequest(prompt="hi", stream=True)
    _ = pytest.raises(Exception)
    # Call prepare_prompt to toggle env
    _ = await tool.prepare_prompt(req)
    assert os.getenv("GLM_STREAM_ENABLED", "false").strip().lower() in ("true", "1", "yes")
    # Simulate provider response -> format_response should restore
    tool.format_response("ok", req)
    assert os.getenv("GLM_STREAM_ENABLED", "").strip().lower() not in ("true", "1", "yes")

