import json
import os
import pytest

@pytest.mark.asyncio
async def test_kimi_capture_headers_metadata_keys_present():
    # Skip if no Kimi key configured
    if not (os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")):
        pytest.skip("Kimi key not present")

    from tools.providers.kimi.kimi_capture_headers import KimiCaptureHeadersTool
    tool = KimiCaptureHeadersTool()

    # Minimal user message
    messages = [{"role": "user", "content": "ping"}]
    args = {
        "messages": messages,
        "session_id": "sess-phase2",
        "call_key": "ck-phase2",
        "tool_name": "kimi_capture_headers_test",
        "model": os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview"),
        "temperature": 0.6,
    }

    res = await tool.execute(args)
    data = json.loads(res[0].text)

    # metadata.cache structure should exist even if not saved on first call
    md = data.get("metadata") or {}
    cache = md.get("cache") or {}
    assert "attached" in cache and "saved" in cache

