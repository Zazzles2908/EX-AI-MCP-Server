# Kimi (Moonshot) API – File Content Retrieval

## Authentication
- HTTP Authorization: `Bearer ${MOONSHOT_API_KEY}`
- Base URL: `https://api.moonshot.ai/v1`

## Get File Content
- GET `/files/{file_id}`

## Response
- Binary content or JSON wrapper depending on SDK; save as bytes on client if needed.

## Notes
- Useful to fetch parsed content (when applicable) or verify stored assets.
