import uuid

import pytest


@pytest.mark.asyncio
async def test_context_caching_token_reuse():
    from tools.chat import ChatTool, ChatRequest
    from src.conversation.cache_store import get_cache_store

    cont_id = f"ctx-{uuid.uuid4()}"
    tool = ChatTool()

    # First turn: no cache yet
    req1 = ChatRequest(prompt="First turn", continuation_id=cont_id)
    prompt1 = await tool.prepare_prompt(req1)
    assert "Context cache:" not in prompt1

    # Simulate provider response with cache tokens
    tokens = {"session_id": "sess-123", "call_key": "call-abc", "token": "tok-xyz"}
    tool.format_response("ack1", req1, model_info={"cache": tokens})

    # Verify stored
    cached = get_cache_store().load(cont_id)
    assert cached.get("session_id") == "sess-123"
    assert cached.get("call_key") == "call-abc"
    assert cached.get("token") == "tok-xyz"

    # Second turn: preface should include cache header
    req2 = ChatRequest(prompt="Second turn", continuation_id=cont_id)
    prompt2 = await tool.prepare_prompt(req2)
    assert "Context cache:" in prompt2
    assert "sess-123" in prompt2 and "call-abc" in prompt2

