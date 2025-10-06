# MCP Configuration Guide

**Version:** 1.0.0  
**Last Updated:** 2025-10-05  
**Status:** ✅ COMPLETE (Week 2, Day 7-8)

---

## Overview

This guide documents the standardized MCP (Model Context Protocol) configuration structure for the EX-AI MCP Server across all supported clients:
- **Auggie CLI** (`mcp-config.auggie.json`)
- **Augment Code** (`mcp-config.augmentcode.json`)
- **Claude Desktop** (`mcp-config.claude.json`)

All configurations follow a standardized template (`mcp-config.template.json`) to ensure consistency and maintainability.

---

## Configuration Files

### Location
All MCP configuration files are located in the `Daemon/` directory:

```
Daemon/
├── mcp-config.template.json      # Base template (reference only)
├── mcp-config.auggie.json         # Auggie CLI configuration
├── mcp-config.augmentcode.json    # Augment Code configuration
└── mcp-config.claude.json         # Claude Desktop configuration
```

### Template File

The `mcp-config.template.json` file serves as the authoritative reference for all client configurations. It defines:

1. **Standard Environment Variables** - Must be identical across all clients
2. **Client-Specific Variables** - May differ based on client capabilities
3. **Configuration Structure** - Standard structure for each client
4. **Validation Rules** - Rules for validating configurations

---

## Standard Environment Variables

These environment variables **MUST be identical** across all client configurations:

### Core Settings
```json
{
  "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
  "PYTHONUNBUFFERED": "1",
  "PYTHONIOENCODING": "utf-8",
  "LOG_LEVEL": "INFO"
}
```

### WebSocket Connection
```json
{
  "EXAI_WS_HOST": "127.0.0.1",
  "EXAI_WS_PORT": "8765"
}
```

### Session Management
```json
{
  "EX_SESSION_SCOPE_STRICT": "true",
  "EX_SESSION_SCOPE_ALLOW_CROSS_SESSION": "false"
}
```

### Coordinated Timeout Hierarchy
**Source:** Week 1, Day 1-2 (Timeout Hierarchy Coordination)

```json
{
  "SIMPLE_TOOL_TIMEOUT_SECS": "60",
  "WORKFLOW_TOOL_TIMEOUT_SECS": "120",
  "EXPERT_ANALYSIS_TIMEOUT_SECS": "90"
}
```

**Rationale:** These timeouts implement the coordinated timeout hierarchy where:
- Simple tools (chat, listmodels) timeout at 60s
- Workflow tools (analyze, thinkdeep, debug) timeout at 120s
- Expert analysis (external model validation) timeouts at 90s
- Daemon timeout = 180s (1.5x workflow timeout)
- Shim timeout = 240s (2.0x workflow timeout)
- Client timeout = 300s (2.5x workflow timeout)

### Provider Timeouts
```json
{
  "GLM_TIMEOUT_SECS": "90",
  "KIMI_TIMEOUT_SECS": "120",
  "KIMI_WEB_SEARCH_TIMEOUT_SECS": "150"
}
```

**Rationale:**
- GLM timeout (90s) matches expert analysis timeout
- Kimi timeout (120s) matches workflow tool timeout
- Kimi web search timeout (150s) allows extra time for web operations

---

## Client-Specific Variables

These variables **MAY differ** between clients based on client capabilities:

### Auggie CLI Only
```json
{
  "AUGGIE_CLI": "true",
  "ALLOW_AUGGIE": "true",
  "AUGGIE_CONFIG": "C:/Project/EX-AI-MCP-Server/auggie-config.json",
  "EXAI_WS_CONNECT_TIMEOUT": "30"
}
```

### Augment Code
No client-specific variables (uses defaults)

### Claude Desktop
No client-specific variables (uses defaults)

---

## Configuration Structure Differences

While environment variables are standardized, each client has slight structural differences:

### Auggie CLI
```json
{
  "mcpServers": {
    "exai": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": { /* standard + client-specific vars */ }
    }
  }
}
```

**Key Differences:**
- Root key: `mcpServers`
- Server name: `exai`
- Includes Auggie-specific env vars

### Augment Code
```json
{
  "mcpServers": {
    "EXAI-WS": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": { /* standard vars only */ }
    }
  }
}
```

**Key Differences:**
- Root key: `mcpServers`
- Server name: `EXAI-WS`
- Standard env vars only

### Claude Desktop
```json
{
  "servers": {
    "exai-mcp": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": { /* standard vars only */ }
    }
  }
}
```

**Key Differences:**
- Root key: `servers` (not `mcpServers`)
- Server name: `exai-mcp`
- Standard env vars only

---

## Validation

### Automated Validation Script

Run the validation script to ensure all configurations are consistent:

```bash
python scripts/validate_mcp_configs.py
```

**Output:**
```
============================================================
MCP Configuration Validator
============================================================

Loading template...
✓ Template loaded

Validating auggie configuration...
✓ Configuration valid

Validating augmentcode configuration...
✓ Configuration valid

Validating claude configuration...
✓ Configuration valid

Checking timeout consistency across all configs...
✓ All timeout values consistent across configs

============================================================
✓ All configurations valid and consistent!
============================================================
```

### Automated Tests

Run the test suite to validate configurations:

```bash
python -m pytest tests/week2/test_config_validation.py -v
```

**Test Coverage:**
- Template structure validation (4 tests)
- Configuration file existence (4 tests)
- Timeout value validation (3 tests)
- Required environment variables (3 tests)
- Structure validation (3 tests)
- Consistency across configs (2 tests)

**Total:** 19 tests, all passing

---

## Maintenance Guidelines

### When to Update Configurations

1. **Timeout Changes** - Update all three configs + template
2. **New Environment Variables** - Add to template, then all configs
3. **Client-Specific Features** - Update only relevant client config
4. **Infrastructure Changes** - Update all configs consistently

### Update Procedure

1. **Update Template First**
   ```bash
   # Edit Daemon/mcp-config.template.json
   # Update _standard_env_vars or _client_specific_vars
   ```

2. **Update All Client Configs**
   ```bash
   # Edit Daemon/mcp-config.auggie.json
   # Edit Daemon/mcp-config.augmentcode.json
   # Edit Daemon/mcp-config.claude.json
   ```

3. **Validate Changes**
   ```bash
   python scripts/validate_mcp_configs.py
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/week2/test_config_validation.py -v
   ```

5. **Test with Clients**
   - Test with Auggie CLI
   - Test with Augment Code
   - Test with Claude Desktop

### Version Control

When updating configurations:

1. Update `_version` in template
2. Add entry to `_change_log` in template
3. Commit all changes together
4. Tag release if significant changes

---

## Troubleshooting

### Configuration Not Loading

**Symptom:** Client doesn't recognize the MCP server

**Solutions:**
1. Check file path in client settings
2. Verify JSON syntax (use `python -m json.tool < config.json`)
3. Check Python path in `command` field
4. Verify `cwd` points to project root

### Timeout Issues

**Symptom:** Tools timing out unexpectedly

**Solutions:**
1. Run validation script to check timeout values
2. Verify timeout hierarchy: tool < daemon < shim < client
3. Check logs for actual timeout values being used
4. Ensure .env file has matching timeout values

### Inconsistent Behavior Across Clients

**Symptom:** Same tool behaves differently in different clients

**Solutions:**
1. Run validation script to check consistency
2. Compare environment variables across configs
3. Check for client-specific overrides
4. Verify all configs use same template version

---

## References

- **Template:** `Daemon/mcp-config.template.json`
- **Validation Script:** `scripts/validate_mcp_configs.py`
- **Tests:** `tests/week2/test_config_validation.py`
- **Timeout Hierarchy:** `docs/reviews/augment_code_review/02_architecture/TIMEOUT_HIERARCHY.md`
- **Week 1, Day 1-2:** Timeout Hierarchy Coordination
- **Week 2, Day 7-8:** Configuration Standardization

---

## Change Log

### Version 1.0.0 (2025-10-05)
- Initial configuration guide created
- Standardized timeout hierarchy from Week 1, Day 1-2
- Documented client-specific differences
- Added validation script and tests
- All configurations validated and consistent

