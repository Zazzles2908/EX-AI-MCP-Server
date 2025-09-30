# EXAI-WS MCP Consultation – Schema Strictness (draft-07, additionalProperties:false)

- Tool: chat_EXAI-WS
- Model: glm-4.5-flash
- req_id: 3da8a385-017d-412f-8c34-d0bbd4d68f2e
- Time: 2025-09-29

## Prompt
Give a concise, implementation-focused explanation for MCP tool JSON Schemas: 1) What declaring "$schema": "http://json-schema.org/draft-07/schema#" accomplishes. 2) Why setting "additionalProperties": false matters for strict validation in editor clients (e.g., Augment VS Code) and how it avoids hidden typos/shape drift. 3) How strict schemas work with central SchemaBuilder/WorkflowSchemaBuilder to guarantee consistent tool definitions and override handling. 4) Trade-offs between strict (additionalProperties:false) vs permissive schemas for cross-client compatibility, and when to relax. Target audience: engineers integrating EXAI-WS MCP tools. Use bullet points and crisp sentences.

## Response
- Declares JSON Schema version (draft-07) to enable correct validation and autocompletion in editor clients.
- `additionalProperties:false` strictly enforces only defined fields, preventing silent typos and shape drift.
- Central builders (SchemaBuilder/WorkflowSchemaBuilder) plus strict schemas guarantee consistent tool definitions and predictable override handling.
- Trade-offs: strict = better safety and early errors; permissive = flexibility but risks runtime failures. Start strict for core tools; relax for experimental/back-compat scenarios.

## Notes
- Continuation ID offered by tool: e8edcd68-87dc-45be-8624-b96487d453ce
- See agent answer for synthesized guidance and implementation details.

