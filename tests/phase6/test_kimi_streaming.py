import asyncio
import json
import os
import socket
import uuid
import pytest

WS_URI = f"ws://{os.getenv('EXAI_WS_HOST','127.0.0.1')}:{os.getenv('EXAI_WS_PORT','8765')}"


def _ws_available(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False

ws_host = os.getenv('EXAI_WS_HOST','127.0.0.1')
ws_port = int(os.getenv('EXAI_WS_PORT','8765'))
ws_up = _ws_available(ws_host, ws_port)

pytestmark = pytest.mark.skipif(not ws_up, reason="WS daemon not available")


async def _call_tool(name: str, arguments: dict) -> dict:
    import websockets
    rid = uuid.uuid4().hex
    payload = {"op": "call_tool", "request_id": rid, "name": name, "arguments": arguments}
    async with websockets.connect(WS_URI) as ws:
        await ws.send(json.dumps({"op": "hello"}))
        await ws.recv()
        await ws.send(json.dumps(payload))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                return msg


@pytest.mark.asyncio
async def test_normalization_rejects_empty_messages():
    res = await _call_tool("kimi_chat_with_tools", {"messages": [], "stream": False, "model": "kimi-k2-0711-preview"})
    txt = (res.get("text") or "") + " " + json.dumps(res.get("outputs", []), ensure_ascii=False)
    assert "invalid_request" in txt


@pytest.mark.asyncio
async def test_mixed_inputs_stream_ok():
    res = await _call_tool(
        "kimi_chat_with_tools",
        {"messages": ["", {"role": "user", "content": "Hello"}, "  "], "stream": True, "model": "kimi-k2-0711-preview"},
    )
    txt = (res.get("text") or "") + " " + json.dumps(res.get("outputs", []), ensure_ascii=False)
    assert "\"provider\": \"KIMI\"" in txt and "\"raw\": {\"stream\": true" in txt


def test_context_cache_lru_unit():
    # Pure unit test of provider cache mechanics (no network)
    from src.providers.kimi import KimiModelProvider
    p = KimiModelProvider(api_key=os.getenv("KIMI_API_KEY", "dummy"))
    # messages → prefix_hash
    msgs = [{"role": "user", "content": "abc"}, {"role": "assistant", "content": "xyz"}]
    pf = p._prefix_hash(msgs)
    assert isinstance(pf, str) and len(pf) >= 32
    sid = "sess-1"
    tool = "kimi_chat_with_tools"
    assert p.get_cache_token(sid, tool, pf) is None
    p.save_cache_token(sid, tool, pf, "tok-12345")
    assert p.get_cache_token(sid, tool, pf) == "tok-12345"


def test_stream_toggles_present():
    # Don’t enforce truthiness — just ensure variables exist/documented
    assert os.getenv("KIMI_STREAM_ENABLED") is not None
    assert os.getenv("GLM_STREAM_ENABLED") is not None


@pytest.mark.asyncio
async def test_error_malformed_inputs():
    res = await _call_tool("kimi_chat_with_tools", {"messages": [{"role": "user"}], "stream": False})
    txt = (res.get("text") or "") + " " + json.dumps(res.get("outputs", []), ensure_ascii=False)
    assert "invalid_request" in txt

