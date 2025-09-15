import os
import json
import asyncio
from unittest.mock import patch, MagicMock

import pytest

from tools.chat import ChatTool
from tools.analyze import AnalyzeTool
from src.providers.base import ModelProvider, ModelCapabilities, ModelResponse, ProviderType


class DummyProvider(ModelProvider):
    """Minimal in-memory provider for testing direct-first and fallback paths."""

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.raise_on_generate = False
        self._calls = []

    def get_provider_type(self) -> ProviderType:
        return ProviderType.CUSTOM

    def validate_model_name(self, model_name: str) -> bool:
        return True

    def list_models(self, respect_restrictions: bool = True) -> list[str]:
        return ["glm-4.5-flash", "flash", "auto"]

    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        return ModelCapabilities(
            provider=self.get_provider_type(),
            model_name=model_name,
            friendly_name="Dummy",
            context_window=200_000,
            max_output_tokens=4000,
            supports_temperature=True,
        )

    def supports_thinking_mode(self, model_name: str) -> bool:
        return False

    def count_tokens(self, text: str, model_name: str) -> int:
        return max(1, len(text) // 3)

    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_output_tokens: int | None = None,
        **kwargs,
    ) -> ModelResponse:
        self._calls.append((model_name, prompt))
        if self.raise_on_generate:
            raise RuntimeError("primary-fail")
        return ModelResponse(content="ok", usage={"input_tokens": 10, "output_tokens": 5}, model_name=model_name, provider=self.get_provider_type())


class TestDirectFirstFallbackBehavior:
    @pytest.mark.asyncio
    async def test_chat_direct_model_does_not_use_fallback(self, monkeypatch):
        tool = ChatTool()
        provider = DummyProvider()

        # Spy for fallback
        fallback_called = {"count": 0}

        def fake_get_provider_for_model(name):
            return provider

        def fake_call_with_fallback(category, call_fn, hints=None):
            fallback_called["count"] += 1
            # If somehow called, return success via call_fn on a valid model
            return call_fn("glm-4.5-flash")

        with patch("src.providers.registry.ModelProviderRegistry.get_provider_for_model", side_effect=fake_get_provider_for_model), \
             patch("src.providers.registry.ModelProviderRegistry.call_with_fallback", side_effect=fake_call_with_fallback):
            args = {"prompt": "hello", "model": "glm-4.5-flash"}
            out = await tool.execute(args)

        # Expect a two-part response: summary + JSON
        assert isinstance(out, list) and len(out) == 2
        # Fallback should NOT be used for explicit model when success
        assert fallback_called["count"] == 0
        # Provider should have been called directly exactly once
        assert len(provider._calls) == 1
        assert provider._calls[0][0] == "glm-4.5-flash"

    @pytest.mark.asyncio
    async def test_chat_auto_model_uses_fallback_chain(self, monkeypatch):
        tool = ChatTool()
        provider = DummyProvider()

        fallback_called = {"count": 0}

        def fake_get_provider_for_model(name):
            return provider

        def fake_call_with_fallback(category, call_fn, hints=None):
            fallback_called["count"] += 1
            # Registry will pass candidate names; simulate choosing flash
            return call_fn("glm-4.5-flash")

        with patch("src.providers.registry.ModelProviderRegistry.get_provider_for_model", side_effect=fake_get_provider_for_model), \
             patch("src.providers.registry.ModelProviderRegistry.call_with_fallback", side_effect=fake_call_with_fallback), \
             patch("utils.model_router.ModelRouter.is_enabled", return_value=False):
            args = {"prompt": "hello", "model": "auto"}
            out = await tool.execute(args)

        assert isinstance(out, list) and len(out) == 2
        assert fallback_called["count"] >= 1, "Fallback chain should be used when model=auto"
        # Provider should have been used by the fallback
        assert len(provider._calls) == 1

    @pytest.mark.asyncio
    async def test_chat_primary_error_triggers_fallback_when_enabled(self, monkeypatch):
        tool = ChatTool()
        provider = DummyProvider()
        provider.raise_on_generate = True  # Force primary call to fail

        # Ensure fallback on failure is enabled
        orig = os.environ.get("FALLBACK_ON_FAILURE")
        os.environ["FALLBACK_ON_FAILURE"] = "true"

        try:
            fallback_called = {"count": 0}

            def fake_get_provider_for_model(name):
                # Direct path will raise; fallback path will also use this provider but via call_with_fallback
                return provider

            def fake_call_with_fallback(category, call_fn, hints=None):
                fallback_called["count"] += 1
                # On fallback, simulate switching to another model where call succeeds
                provider.raise_on_generate = False
                return call_fn("glm-4.5-flash")

            with patch("src.providers.registry.ModelProviderRegistry.get_provider_for_model", side_effect=fake_get_provider_for_model), \
                 patch("src.providers.registry.ModelProviderRegistry.call_with_fallback", side_effect=fake_call_with_fallback):
                args = {"prompt": "hello", "model": "glm-4.5-flash"}
                out = await tool.execute(args)

            assert isinstance(out, list) and len(out) == 2
            assert fallback_called["count"] == 1, "Fallback chain should run after primary failure when enabled"
            # Provider was called at least twice: one failing direct, one successful fallback
            assert len(provider._calls) >= 2
        finally:
            if orig is None:
                os.environ.pop("FALLBACK_ON_FAILURE", None)
            else:
                os.environ["FALLBACK_ON_FAILURE"] = orig


class TestAnalyzeContinuationHints:
    @pytest.mark.asyncio
    async def test_analyze_next_call_includes_continuation_fields(self):
        tool = AnalyzeTool()
        args = {
            "step": "Kickoff",
            "step_number": 1,
            "total_steps": 3,
            "next_step_required": True,
            "findings": "Set goal and scope",
            "relevant_files": ["tools/simple/base.py"],
            "model": "flash",
            # No files_checked yet on step 1
        }
        out = await tool.execute_workflow(args)
        assert len(out) == 1
        data = json.loads(out[0].text)

        # Core continuation envelope
        assert data.get("next_step_required") is True
        assert data.get("status") in {"pause_for_analysis", "analysis_in_progress", "analysis_required"}

        # next_call skeleton must exist with required flags
        next_call = data.get("next_call")
        assert isinstance(next_call, dict) and "arguments" in next_call
        next_args = next_call["arguments"]
        assert next_args["next_step_required"] is True

        # Carried-forward fields present
        # Normalize: tool may expand to absolute paths internally
        rf = next_args.get("relevant_files")
        assert isinstance(rf, list) and len(rf) == 1
        assert rf[0].replace("\\", "/").endswith("tools/simple/base.py")
        # Optional carried fields exist (empty OK)
        assert "files_checked" in next_args
        assert "relevant_context" in next_args
        assert "issues_found" in next_args

    @pytest.mark.asyncio
    async def test_analyze_next_call_preserves_continuation_id(self):
        tool = AnalyzeTool()
        args = {
            "step": "Kickoff",
            "step_number": 1,
            "total_steps": 2,
            "next_step_required": True,
            "findings": "Plan",
            "relevant_files": ["tools/workflow/workflow_mixin.py"],
            "model": "flash",
            "continuation_id": "thread-12345",
        }
        out = await tool.execute_workflow(args)
        data = json.loads(out[0].text)
        next_args = data["next_call"]["arguments"]
        assert next_args.get("continuation_id") == "thread-12345"

