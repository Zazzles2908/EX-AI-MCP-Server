# Provider Parameter Shapes (Validated)

Date: 2025-09-28

This document records minimal JSON payloads and key links for validated provider calls used by EXAI WS daemon + manager.

## GLM Agents

### 1) Agent Chat (glm_agent_chat)
- Endpoint: POST /api/v1/agents
- Minimal arguments (tool):
```json
{
  "agent_id": "general_translation",
  "messages": [{"role": "user", "content": "hello"}],
  "temperature": 0.2
}
```
- Response contains: `id` (often usable as `conversation_id`), `agent_id`, `status`, `choices`, `usage`.

### 2) Conversation History (glm_agent_conversation)
- Endpoint: POST /api/v1/agents/conversation
- Minimal arguments (tool):
```json
{
  "agent_id": "general_translation",
  "conversation_id": "<from agent_chat id or conversation_id>",
  "page": 1,
  "page_size": 10
}
```
- Notes: prefer `conversation_id` if present; some responses only include `id`. We treat `id` as fallback for `conversation_id`.

### 3) Async Result (glm_agent_get_result)
- Endpoint: POST /api/v1/agents/async-result
- Minimal arguments (tool):
```json
{
  "agent_id": "<agent>",
  "async_id": "<returned async id>"
}
```

## GLM Chat (manager path with web search)
- Endpoint: POST /api/paas/v4/chat/completions (provider HTTP)
- Manager tool: `chat` with `use_websearch=true` triggers provider web browsing.
- Minimal payload concept (effective fields; manager abstracts this):
```json
{
  "model": "glm-4.5-flash",
  "messages": [{"role":"user","content":"..."}],
  "tools": [{"type":"web_search", "params": {"search_query":"..."}}],
  "tool_choice": "auto"
}
```

## GLM Web Search (direct tool, optional)
- Endpoint: POST https://api.z.ai/api/paas/v4/web_search
- Minimal arguments (tool):
```json
{
  "search_engine": "search-prime",
  "search_query": "<query>",
  "count": 5
}
```
- Returns: JSON with search results array. (Manager path via `chat(use_websearch=true)` is preferred.)

## Kimi Files

### 1) Upload + Extract (kimi_upload_and_extract)
- Endpoints: POST /v1/files (upload), GET /v1/files/{id}/content (download/extract)
- Minimal arguments (tool):
```json
{
  "file_path": "<absolute or repo-relative>",
  "extract": true
}
```
- Response: array of assistant/system messages including extracted content.

## Manager-side Conversation Meta Envelope
- The GLM Agent Chat tool appends a second text output:
```json
{"hint":"conversation_meta","agent_id":"...","conversation_id":"..."}
```
- Manager may, when user intent indicates, lazily fetch a small window of prior messages with `glm_agent_conversation`.

## Links (add official references)
- ZhipuAI GLM Chat Completions: https://open.bigmodel.cn/api/paas/v4/chat/completions
- ZhipuAI Agents (platform): /api/v1/agents, /api/v1/agents/async-result, /api/v1/agents/conversation (see ZhipuAI docs)
- Moonshot Kimi Files: https://api.moonshot.ai/v1/files




## Implementation Locations (Functions & Scripts)

- server.py
  - register_provider_specific_tools: registers provider tools when GLM/Kimi available (glm_agent_chat, glm_agent_get_result, glm_agent_conversation, kimi_upload_and_extract, kimi_multi_file_chat)
- tools/providers/glm/glm_agents.py
  - GLMAgentChatTool: posts to /api/v1/agents and appends conversation_meta envelope
  - GLMAgentConversationTool: posts to /api/v1/agents/conversation
  - GLMAgentGetResultTool: posts to /api/v1/agents/async-result
- tools/providers/glm/glm_web_search.py (optional direct wrapper)
  - GLMWebSearchTool: POST https://api.z.ai/api/paas/v4/web_search (manager path via chat(use_websearch=true) preferred)
- scripts/diagnostics/ws_probe.py
  - Connects to WS daemon, enumerates tools, runs smoke calls; captures conversation_id organically and verifies glm_agent_conversation; saves artifacts
- docs/external_review/
  - 20250928_ws_probe_run.md: live probe outputs
  - 20250928_glm_agent_session.json: captured agent_id + conversation_id + raw response
  - 20250928_exai_websearch_raw.md: exact EXAI-WS websearch output snapshot
