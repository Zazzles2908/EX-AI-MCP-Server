# Router/Provider/MCP JSONL Samples (2025-09-27)

This file contains small, redacted samples to verify log flow per 20250926 review docs.

## Summary
- Router JSONL: currently empty for these runs (router.jsonl had no decision entries). We exercised provider file ingestion directly and captured provider breadcrumbs.
- Provider JSONL: toolcalls.jsonl shows multiple `provider=kimi` file extractions with timings and error envelopes when type unsupported.
- Next step: trigger a router-managed flow (decision envelope) by invoking a tool path that routes based on task type (e.g., large-file summarization). Capture `route_start`, `decision`, `attempt_*`, and `result_meta`.

## toolcalls.jsonl (excerpts)
```
{"provider": "kimi", "tool_name": "file_upload_extract", "args": {"path": "C:\\Project\\EX-AI-MCP-Server\\server.py", "purpose": "file-extract"}, "latency_ms": 2238.56, "ok": true}
{"provider": "kimi", "tool_name": "file_upload_extract", "args": {"path": "providers/openai_compatible.py", "purpose": "file-extract"}, "latency_ms": 1040.96, "ok": true}
{"provider": "kimi", "tool_name": "file_upload_extract", "args": {"path": ".env", "purpose": "file-extract"}, "latency_ms": 240.57, "ok": false, "error": "text extract error: 不支持的文件类型"}
```

## router.jsonl (excerpts)
```
<empty>
```

## Validation call results (human summary)
- EXAI-WS smoke test: success.
- File ingestion validation: returned CSV and bullets; RAW markers included.

## Recommendations
- Add/verify router decision emission in intelligent_router for non-chat file tasks.
- Add correlation of `request_id` across router and provider events.
- Keep provider breadcrumbs (already in place) and add sampled JSONL upload to this folder.


## Post-Restart Addendum (2025-09-27)

Evidence from latest WS daemon session:

- Raw tool-call results (.logs/toolcalls_raw.jsonl)
```
{"tool":"version","raw_len":962,"truncated":false,"raw":"[TextContent(type='text', text='{...}')]"}
{"tool":"listmodels","raw_len":1890,"truncated":false,"raw":"[TextContent(type='text', text='{...}')]"}
{"tool":"chat","raw_len":1979,"truncated":false,"raw":"[TextContent(type='text', text='{...}')]"}
```

- Adaptive summaries (.logs/toolcalls.jsonl)
```
{"provider":"kimi","tool_name":"file_upload_extract","args":{"path":"C:\\Project\\EX-AI-MCP-Server\\server.py","purpose":"file-extract"},"latency_ms":1987.89,"ok":true}
```

- Router decisions (.logs/router.jsonl)
```
<empty>
```

Next: Trigger explicit router-managed flows to populate router.jsonl and append 4–6 correlated samples here.
