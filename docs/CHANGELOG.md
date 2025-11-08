# Changelog

All notable changes to the EXAI MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-05

### Fixed
- **Zod Validation Errors**: Resolved validation failures by adding required fields to all tools:
  - Added `id` field (number) to all 5 tools
  - Ensured `description` field is non-empty for all tools
  - Verified `name` field is properly set
  - Added comprehensive `inputSchema` for parameter validation

### Changed
- Simplified MCP server configuration to use direct stdio (like gh-mcp)
- Removed complex WebSocket shim setup
- Streamlined configuration in `.mcp.json`

### Verified
- ✅ Tools/list returns proper format with all required fields
- ✅ Compatible with Claude web application (claude.ai)
- ✅ Follows MCP protocol version 2024-11-05

## [1.0.0] - 2025-11-05

### Added
- Initial EXAI MCP Server implementation
- 5 EXAI tools: exai_chat, exai_search, exai_analyze, exai_status, exai_tools
- Simple stdio-based MCP server
- Configuration example for Claude web application
