# EX-AI MCP Server - Environment File Management
# Per CLAUDE.md requirements - env files in main directory only

## Environment File Structure

### Main Directory Files (Required per CLAUDE.md):
- `.env` - Local development environment variables
- `.env.docker` - Container environment variables (CURRENTLY ACTIVE)
- `.env.example` - Template for environment setup
- `.env.patched` - Development patches (temporary)

### Configuration Directory:
- `config/pyproject.toml` - Python dependencies and project metadata
- `config/redis.conf` - Redis configuration
- `config/Dockerfile` - Container build configuration
- `config/pytest.ini` - Test configuration
- `config/redis-commander.json` - Redis commander config

### ❌ VIOLATIONS FOUND AND FIXED:
- **FIXED**: `config/.env.docker` - Duplicate removed (CLAUDE.md violation)
- **ISSUE**: `config/pyproject.toml` - Should be root directory per standard Python practices

### Status:
✅ Environment files consolidated to main directory only
✅ No duplicates between root and config directories
✅ All configuration properly organized per requirements

### Next Steps:
1. Review `clean_later/` for important project documentation
2. Consolidate multiple TODO lists into single authoritative source
3. Clean up daemon folder over-engineering
4. Rationalize memory system implementations