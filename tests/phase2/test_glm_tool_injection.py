import json
import os
import pytest


def test_build_payload_web_search_injection_unit():
    from src.providers.glm import GLMModelProvider
    p = GLMModelProvider(api_key="dummy")
    payload = p._build_payload(
        prompt="hello",
        system_prompt=None,
        model_name="glm-4.5-flash",
        temperature=0.3,
        max_output_tokens=None,
        tools=[{"type": "web_search"}],
        tool_choice=None,
    )
    assert isinstance(payload, dict)
    assert payload.get("tools") == [{"type": "web_search"}]


def test_glm_payload_preview_tool_injects_web_search():
    from tools.providers.glm.glm_payload_preview import GLMPayloadPreviewTool
    tool = GLMPayloadPreviewTool()
    outs = pytest.run(async_=False) if False else None  # placeholder to avoid lint errors
    # execute is async; run via event loop
    import asyncio
    async def run():
        res = await tool.execute({"prompt": "test", "use_websearch": True, "model": "glm-4.5-flash"})
        return res
    res = asyncio.get_event_loop().run_until_complete(run())
    text = res[0].text
    data = json.loads(text)
    assert data.get("tools") == [{"type": "web_search"}]

