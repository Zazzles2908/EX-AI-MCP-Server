import os
import uuid

import pytest


@pytest.mark.asyncio
async def test_chat_continuation_across_turns(monkeypatch):
    # Ensure clean history dir if any policy uses disk
    cont_id = f"test-{uuid.uuid4()}"

    # Use ChatTool across two turns; verify history store accumulates
    from tools.chat import ChatTool, ChatRequest
    tool = ChatTool()

    # Turn 1 (user)
    req1 = ChatRequest(prompt="Hello", continuation_id=cont_id)
    _ = await tool.prepare_prompt(req1)
    tool.format_response("Hi there", req1)

    # Turn 2
    req2 = ChatRequest(prompt="How are you?", continuation_id=cont_id)
    preface2 = await tool.prepare_prompt(req2)
    tool.format_response("I'm good", req2)

    # Validate history contains both user/assistant turns
    from src.conversation.history_store import get_history_store
    hist = get_history_store().load_recent(cont_id, 10)
    roles = [it.get("role") for it in hist]
    assert roles.count("user") >= 2
    assert roles.count("assistant") >= 2

    # Validate assembled context includes previous content
    from src.conversation.memory_policy import assemble_context_block
    ctx = assemble_context_block(cont_id, max_turns=6)
    assert "Hello" in ctx and "Hi there" in ctx and "How are you?" in ctx

