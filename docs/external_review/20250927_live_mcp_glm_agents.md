# GLM Agent live run via WS daemon (2025-09-27)

- WS URI: ws://127.0.0.1:8765
- Tool: glm_agent_chat
- Agent: general_translation (built-in agent)

Output (truncated)
```
[probe] glm_agent_chat preview: [{'type': 'text', 'text': '{"id":"202509272227027d2d42fed37b4120","agent_id":"general_translation","status":"success","choices":[{"index":0,"finish_reason":"stop","messages":[{"role":"assistant","cont...'}]
```

Notes
- Endpoint used: POST https://api.z.ai/api/v1/agents
- Payload used (simplified):
  {
    "agent_id": "general_translation",
    "stream": false,
    "messages": [
      {"role": "user", "content": [{"type": "text", "text": "hello from ws_probe"}]}
    ]
  }
- Result: success with assistant message returned
- async-result was not exercised (no async_id provided by this run)

