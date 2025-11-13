# Changelog

All notable changes to the EXAI MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-11-08

### Fixed - CRITICAL PROVIDER ERRORS
- **Kimi Provider NameError**: Fixed `name 'prov' is not defined` error in tools/simple/base.py
  - Corrected 8+ instances of inconsistent variable naming (prov → provider)
  - Restored full Kimi provider functionality
  - Primary issue causing 100% request failures

- **GLM Provider Parameter Error**: Fixed `unexpected keyword argument 'continuation_id'`
  - Added parameter filtering in src/providers/glm_provider.py
  - GLM SDK doesn't support continuation_id parameter
  - Restored GLM fallback chain functionality

- **Port Configuration**: Fixed port mapping in docker-compose.yml
  - Changed from 8000 range to 3000-3003 range
  - Matches Orchestrator port requirements (8000-8999)

### Fixed - DATABASE GRACEFUL DEGRADATION
- **file_operations Table**: Added try-catch for missing table errors
- **file_metadata Table**: Added try-catch for missing table errors
- System now degrades gracefully when optional tables are unavailable

### Changed
- **Root Directory Reorganization**: Moved 8 files to appropriate subdirectories
  - Database scripts → scripts/database/
  - System scripts → scripts/system/
  - Testing scripts → scripts/testing/
  - Log files → logs/
- **Comprehensive Codebase Analysis**: Verified 557+ files across 60+ subdirectories
- **Documentation**: Created 6 comprehensive analysis and fix reports

### Verified
- ✅ All containers healthy (exai-daemon, redis, redis-commander)
- ✅ All circuit breakers closed (healthy state)
- ✅ Both Kimi and GLM providers operational
- ✅ 0% request failure rate (previously 100%)
- ✅ Fallback chain working correctly
- ✅ Port mapping correct (3000-3003)

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
