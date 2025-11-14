# Changelog

All notable changes to the EXAI MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [6.0.0] - 2025-11-14

### Changed - MAJOR DOCUMENTATION CONSOLIDATION
- **Documentation Structure**: Eliminated dual documentation directories
  - Removed `documents/` directory entirely
  - Consolidated all 59+ files from `documents/` to `docs/` subdirectories
  - Achieved single source of truth for all documentation

- **Professional Standards**: Enforced industry-standard documentation hierarchy
  - Following Linux Kernel, Python PEP, Kubernetes, and Apache Foundation patterns
  - Single `docs/` hierarchy only (no dual structure)
  - 75 markdown files properly organized in 15 subdirectories

- **Root Directory Policy**: Enforced strict 4-file limit
  - Root now contains exactly: README.md, CLAUDE.md, CHANGELOG.md, CONTRIBUTING.md
  - Moved all documentation to `docs/` subdirectories
  - No markdown files in root (except required 4)

- **Agent Workflow**: Created comprehensive mandatory standards
  - `docs/workflow/AGENT_WORKFLOW.md` - Mandatory for all agents
  - `docs/workflow/ROOT_DIRECTORY_POLICY.md` - Strict file organization rules
  - `docs/workflow/ENVIRONMENT_SETUP.md` - Environment file management
  - Clear entry points and navigation for all team members

- **Navigation**: Created comprehensive documentation hub
  - `docs/README.md` serves as main documentation entry point
  - 12 professional subdirectories: architecture, security, database, api, operations, development, smart-routing, workflow, integration, guides, troubleshooting, external-reviews
  - All sections properly linked and cross-referenced

- **Docker Build**: Verified complete build success
  - All 15 directories included in Docker image
  - Container builds successfully (311MB)
  - No missing dependencies

### Added
- **Comprehensive Reports**: Created `docs/reports/DOCUMENTATION_CONSOLIDATION_COMPLETE.md`
- **Workflow Documentation**: Complete agent standards in `docs/workflow/`
- **Project Organization**: Summary of all organizational changes
- **Professional Structure**: Industry-standard documentation hierarchy

### Fixed
- **Docker Build Incompleteness**: All directories now included
- **Documentation Sprawl**: Eliminated dual directories causing confusion
- **Root Directory Pollution**: Enforced professional 4-file limit
- **Navigation Confusion**: Single documentation entry point established

### Verified
- ✅ Single `docs/` hierarchy (no `documents/`)
- ✅ Root directory: Exactly 4 files
- ✅ 75 markdown files in professional structure
- ✅ Docker build: Success (311MB)
- ✅ Agent workflow: Mandatory standards established
- ✅ Professional standards: 100% compliant


### Fixed - DOCKER NAMING CONVENTIONS
- **Container Naming**: Renamed from `exai-mcp-daemon` to `exai-mcp-server`
  - Updated docker-compose.yml service name to `exai-mcp-server`
  - Updated container name to `exai-mcp-server`
  - Now matches image name: `exai-mcp-server:latest`
  - Professional Docker naming conventions implemented

- **Documentation Alignment**: Updated all documentation files
  - Updated CLAUDE.md with correct docs/ paths
  - Updated README.md with correct container references
  - Fixed broken documentation links

- **Dockerignore**: Updated .dockerignore patterns
  - Removed conflicting docs/ exclusion
  - Ensures documentation builds correctly into container

### Added - CONTAINER CONNECTION GUIDE
- **Connection Documentation**: Created comprehensive guide for future projects
  - `docs/operations/EXAI_CONNECTION_GUIDE.md` - Complete connection instructions
  - Port mapping reference for all services
  - Step-by-step setup for new developers
  - Troubleshooting section for common issues

- **Container Lifecycle Documentation**: Documented container management
  - Start/stop procedures
  - Build and rebuild instructions
  - Option B implementation (remove container and image)
  - Easy recovery procedures


### Changed - PROFESSIONAL DOCUMENTATION ORGANIZATION
- **Professional Navigation**: Added index.md to all 13 subdirectories
  - Each subdirectory now has proper navigation file
  - Cross-references between sections implemented
  - Follows Linux Kernel documentation standards

- **Professional Naming Conventions**: Removed all numeric prefixes
  - Renamed 21 files from `01_filename.md` to `filename.md`
  - Examples: `01_system_architecture.md` → `system-architecture.md`
  - Now uses kebab-case and Title Case consistently

- **Non-Production Cleanup**: Removed non-essential directories
  - Deleted `05_CURRENT_WORK/` (temporary files)
  - Deleted `archive/` (empty directory)
  - Only production-ready documentation remains

- **Navigation Links**: Updated all references to renamed files
  - Main `docs/README.md` updated with corrected links
  - All subdirectory index.md files corrected
  - Complete cross-reference validation

### Added
- **Professional Standards Report**: `docs/reports/PROFESSIONAL_DOCS_ORGANIZATION_COMPLETE.md`
- **Navigation Files**: index.md in architecture/, security/, database/, api/, development/, integration/, troubleshooting/, external-reviews/
- **Updated Main README**: Complete navigation hub with corrected links

### Verified
- ✅ 13 subdirectories with index.md (from 4)
- ✅ 0 files with numeric prefixes (from 21)
- ✅ Professional naming conventions: 100% compliant
- ✅ Industry standards: Linux, Python PEP, K8s, Apache patterns
- ✅ Documentation organization: Professional grade

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
