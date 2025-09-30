# Phase 5 – Chat context continuation (evidence)

- Components: src/conversation/history_store.py, src/conversation/memory_policy.py, tools/chat.py
- Behavior: When continuation_id is provided, previous turns are prefixed into the prepared prompt; user/assistant turns are persisted.
- Test: tests/phase5/test_chat_context_continuation.py (passing)

Assertion highlights:
- Prepared prompt contains previous user and assistant content and the marker "Current request:".

