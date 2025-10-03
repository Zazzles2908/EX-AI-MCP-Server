# Kimi – File Processing (Upload/Extract)

## Purpose
Upload files to Moonshot (Kimi) and use provider features for extraction/analysis.

## Current Implementation (code paths)
- src/providers/kimi.py: upload_file(file_path, purpose) via self.client.files.create; CWD resolution and size guardrail.
- tools/providers/kimi/*: Kimi tools wrappers (e.g., kimi_upload) integrate uploads in workflows.

## Parameters
- KIMI_API_URL (default https://api.moonshot.ai/v1)
- KIMI_FILES_MAX_SIZE_MB

## Dependencies
- Moonshot Python client via OpenAI‑compatible implementation

## Integration Points
- Workflows store file_id and pass to chat calls when needed.

## Status Assessment
- ✅ Existing & Complete

## Implementation Notes
- Friendly errors include CWD; purpose supports "file-extract" or "assistants".

## Next Steps
- Add example in tools/workflows that chains upload → analysis.

