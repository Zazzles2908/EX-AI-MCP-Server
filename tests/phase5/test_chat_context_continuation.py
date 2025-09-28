import pytest

from tools.chat import ChatTool, ChatRequest
from src.conversation.history_store import get_history_store


@pytest.mark.asyncio
async def test_chat_context_included_in_prompt():
    # Use a unique continuation_id for isolation
    cid = "test-cont-123"
    store = get_history_store()
    store.record_turn(cid, "user", "Earlier question A")
    store.record_turn(cid, "assistant", "Earlier answer A1")

    tool = ChatTool()
    req = ChatRequest(prompt="Current question B", files=[], images=[], continuation_id=cid)

    prompt = await tool.prepare_prompt(req)

    # The prompt should contain previous turns
    assert "Earlier question A" in prompt
    assert "Earlier answer A1" in prompt
    assert "Current request:" in prompt

