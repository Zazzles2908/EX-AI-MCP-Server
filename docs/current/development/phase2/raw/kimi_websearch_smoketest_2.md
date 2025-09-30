# Kimi websearch smoke test 2 (EXAI-WS MCP)

Prompt:
- Find the section in Moonshot docs describing the native web_search tool schema and summarize its required/optional fields, then provide the direct section URL.

Raw tool response:

<raw>
(Empty body returned by tool; indicates provider issued tool_calls without a final assistant message.)
</raw>

Notes:
- Also empty, consistent with a provider tool_call that needs the server-side minimal loop to execute the web_search and return a final assistant message.
- This aligns with the code change we just enabled and restarted for.

