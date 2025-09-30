# Kimi Message Normalization Tester — 2025-09-28

Summary: Verified that empty/whitespace messages are rejected early with a clear invalid_request error, and mixed inputs preserve only non-empty content.

Commands:
- .venv\Scripts\python.exe -X utf8 scripts/diagnostics/kimi/normalize_tester.py

Results (abridged):
- CASE: empty list → invalid_request (No non-empty messages provided...)
- CASE: list with empty string → invalid_request
- CASE: list with whitespace → invalid_request
- CASE: dict empty content → invalid_request
- CASE: dict whitespace content → invalid_request
- CASE: mixed valid+empty → OK (streamed content returned)
- CASE: single valid string → OK (streamed content returned)

Notes:
- Fix implemented in tools/providers/kimi/kimi_tools_chat.py ensures all messages are trimmed and empties dropped; request aborted if none remain.
- WS daemon restarted with scripts\ws_start.ps1 -Restart to apply changes.

