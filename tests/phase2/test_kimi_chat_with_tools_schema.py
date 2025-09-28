import json
import types
import pytest

from tools.providers.kimi.kimi_tools_chat import KimiChatWithToolsTool
from src.providers.base import ProviderType
from src.providers.registry import ModelProviderRegistry


class FakeKimiProvider:
    def __init__(self):
        self._ptype = ProviderType.KIMI
        self.client = types.SimpleNamespace()

    def get_provider_type(self):
        return self._ptype

    def chat_completions_create(self, model, messages, tools=None, tool_choice=None, temperature=0.6, **kwargs):
        # Return a minimal OpenAI-style payload
        return {
            "provider": "KIMI",
            "model": model,
            "content": "ok",
            "raw": {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "ok",
                        }
                    }
                ]
            },
        }


@pytest.fixture(autouse=True)
def patch_registry(monkeypatch):
    fake = FakeKimiProvider()
    monkeypatch.setattr(ModelProviderRegistry, "get_provider", lambda p: fake)
    yield


def _decode_textcontent(items):
    assert isinstance(items, list) and items, "tool returned empty"
    txt = items[0].text
    return json.loads(txt)


@pytest.mark.asyncio
async def test_accepts_string_messages():
    tool = KimiChatWithToolsTool()
    out = await tool.execute({"messages": "ping", "model": "kimi-k2-0711-preview"})
    data = _decode_textcontent(out)
    assert data.get("provider") == "KIMI"


@pytest.mark.asyncio
async def test_accepts_array_messages():
    tool = KimiChatWithToolsTool()
    out = await tool.execute({"messages": ["ping"], "model": "kimi-k2-0711-preview"})
    data = _decode_textcontent(out)
    assert data.get("provider") == "KIMI"

