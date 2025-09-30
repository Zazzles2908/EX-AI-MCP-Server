# Kimi (Moonshot) API – File Management

## Authentication
- HTTP Authorization: `Bearer ${MOONSHOT_API_KEY}`
- Base URL: `https://api.moonshot.ai/v1`

## List Files
- GET `/files`

## Delete File
- DELETE `/files/{file_id}`

## Notes
- Combine with `/files` upload and `/files/{file_id}` retrieval for full lifecycle.

