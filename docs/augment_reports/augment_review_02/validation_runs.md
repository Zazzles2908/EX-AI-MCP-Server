EXAI-WS MCP Validations (Batch 1)

1) GLM web-browse validation
- Tool: EXAI-WS MCP chat (glm-4.5-flash)
- Prompt: What's the most recent stable release version of FastAPI and one breaking change announced for the next major?
- Output (raw summary):
  - FastAPI 0.104.1 is most recent stable; v1.0 will remove starlette.middleware.gzip in favor of fastapi.middleware.gzip
  - Sources: https://github.com/tiangolo/fastapi/releases , https://fastapi.tiangolo.com/blog/fastapi-v1-release/#breaking-changes
- Duration≈8.0s; ~402 tokens (reported by tool)

2) File ingestion validation
- Tool: EXAI-WS MCP chat (glm-4.5-flash)
- File: docs/_tmp_kimi_upload.txt
- Prompted tasks: summarize 2 bullets, extract CSV, return token estimate
- Output (raw summary):
  - Two bullets, CSV rows, token count reported
- Duration≈13.1s; ~281 tokens (reported by tool)

Notes
- This batch confirms daemon runs and both browse and file ingestion pathways function via MCP tool calls. Routing JSONL will be attached in a later batch after enhancing decision envelopes.

