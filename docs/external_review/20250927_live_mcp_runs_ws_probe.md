# Live MCP runs via WS daemon (2025-09-27)

Environment
- WS URI: ws://127.0.0.1:8765
- Script: scripts/diagnostics/ws_probe.py

Output
```
[probe] connecting to ws://127.0.0.1:8765
[probe] hello ok
[probe] tools (23): ['analyze', 'challenge', 'chat', 'codereview', 'consensus', 'debug', 'docgen', 'glm_agent_chat', 'glm_agent_conversation', 'glm_agent_get_result', 'glm_upload_file', 'kimi_multi_file_chat', 'kimi_upload_and_extract', 'listmodels', 'planner', 'precommit', 'refactor', 'secaudit', 'self-check', 'testgen']...
[probe] version preview: [{'type': 'text', 'text': '{"status":"success","content":"# EX MCP Server Version\\n\\n## Server Information\\n**Current Version**: 2.0.0\\n**Last Updated**: 20'}]
[probe] listmodels preview: [{'type': 'text', 'text': '{"status":"success","content":"# Available AI Models\\n\\n## Moonshot Kimi ✅\\n**Status**: Configured and available\\n\\n**Models**:\\n-  `kimi-k2-0905-preview` - 128K contex'}]
[probe] chat(web) preview: [{'type': 'text', 'text': '{"status": "continuation_available", "content": "=== PROGRESS ===\\n[PROGRESS] chat: Starting execution\\n[PROGRESS] chat: Request validated\\n[PROGRESS] chat: Model/context'}]
[probe] kimi_upload_and_extract preview: [{'type': 'text', 'text': '[{"role": "system", "content": "{\\"content\\":\\"# EXAI-WS MCP Raw Output: Implementation Validation Queries (2025-09-27)\\n\\nRequest Model: glm-4.5-flash (manager)\\n"'}]
[probe] GLM agent tests skipped (GLM_TEST_AGENT_ID not set)
```

Notes
- Provider-specific tools are now visible and callable via WS daemon.
- Kimi Files upload+content retrieved successfully for the test document.
- GLM Agent tests await GLM_TEST_AGENT_ID (or we can auto-create a temporary test agent via zai-sdk).

