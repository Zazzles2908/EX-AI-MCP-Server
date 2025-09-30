# Kimi websearch smoke test 1 (EXAI-WS MCP)

Prompt:
- Use web search to find the official Moonshot tool-use documentation URL and list three relevant URLs.

Raw tool response:

<raw>
(Empty body returned by tool; indicates provider issued tool_calls without a final assistant message.)
</raw>

Notes:
- This response being empty suggests tool_call roundtrip is incomplete at the client layer and relies on our server’s restored minimal tool loop to complete the chain.
- Next step: cross-check with secondary prompt and then run a direct non-search prompt to confirm chat path is healthy.

