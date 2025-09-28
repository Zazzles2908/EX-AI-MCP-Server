# GLM – File Operations (Upload)

## Purpose
Upload local files to GLM Files API for later use (analysis/assistants).

## Current Implementation (code paths)
- src/providers/glm.py: GLMModelProvider.upload_file(file_path, purpose="agent") with SDK and HTTP fallback; size guardrail and timeout support.

## Parameters
- GLM_FILES_MAX_SIZE_MB, FILE_UPLOAD_TIMEOUT_SECS or GLM_FILE_UPLOAD_TIMEOUT_SECS

## Dependencies
- zhipuai SDK (preferred), or HttpClient multipart /files endpoint

## Integration Points
- Downstream tools needing GLM files should store returned file_id in workflow metadata.

## Status Assessment
- ✅ Existing & Complete

## Implementation Notes
- Uses mimetypes.guess_type; logs size/timeout; normalizes id from SDK/HTTP responses.

## Next Steps
- None critical; add small smoke test for upload if desired.

