# Validation  Phase 3: GLM Native Web Search via MCP

## Command
- Script: scripts/diagnostics/ws_probe.py
- Result: Exit 0

## Key Log Lines
```
[probe] tools (..): [... 'glm_web_search', ...]
[probe] has glm_web_search: True
[probe] glm_web_search preview: [{'type': 'text', 'text': '{"created": 1759046190, "id": "20250928155628b9772cb79ae94e1b", "request_id": "20250928155628b9772cb79ae94e1b", "search_intent": [...], ... }'}]
```

## Outcome
- Tool present and callable through MCP.
- Received JSON payload from Z.ai web_search endpoint (truncated in preview).

## Notes
- Also validated Chat(auto, use_websearch=true) injected provider-native web_search tools (see ws_probe "chat(web) preview").

