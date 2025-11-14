# Troubleshooting Documentation

This directory contains troubleshooting guides and diagnostic tools for the EX-AI MCP Server project.

## Quick Links

### 🔧 Diagnostic & Fix Scripts
- **[MCP Troubleshooting Guide](MCP_TROUBLESHOOTING_GUIDE.md)** - Comprehensive troubleshooting guide for all MCP issues
- **[Automated Fix Script](../../scripts/fix_mcp_servers.py)** - Run this first to auto-fix common issues
- **[Diagnostic Tool](../../scripts/diagnose_mcp_servers.py)** - Comprehensive system diagnostic

### 📊 Reports
- **[MCP QA Report](../../MCP_QA_REPORT.md)** - Detailed QA analysis of all MCP servers and components
- **Issue Logs** - Check `../../logs/` directory for runtime logs

## Common Issues

| Issue | Quick Fix | Documentation |
|-------|-----------|---------------|
| WS Shim not running | `python scripts/fix_mcp_servers.py` | [MCP Troubleshooting Guide](MCP_TROUBLESHOOTING_GUIDE.md#1-ws-shim-not-running) |
| EXAI daemon down | `docker-compose restart` | [MCP Troubleshooting Guide](MCP_TROUBLESHOOTING_GUIDE.md#2-exai-daemon-not-running) |
| Filesystem MCP failing | `npm cache clean --force` | [MCP Troubleshooting Guide](MCP_TROUBLESHOOTING_GUIDE.md#3-filesystem-mcp-failing) |
| Mermaid MCP failing | `npm install -g @narasimhaponnada/mermaid-mcp-server` | [MCP Troubleshooting Guide](MCP_TROUBLESHOOTING_GUIDE.md#4-mermaid-mcp-failing) |
| Log file bloat | `find logs/ -name "ws_shim_*.log" -mtime +1 -delete` | [MCP Troubleshooting Guide](MCP_TROUBLESHOOTING_GUIDE.md#6-log-file-bloat) |

## Running Diagnostics

### Automated Fix
```bash
python scripts/fix_mcp_servers.py
```

### Full Diagnostic
```bash
python scripts/diagnose_mcp_servers.py
```

### Manual Checks
```bash
# Check daemon health
curl http://127.0.0.1:3002/health

# Check Docker services
docker-compose ps

# Check ports
netstat -tlnp | grep -E "3005|3010"
```

## MCP Server Status

**Working (3/6):**
- ✅ git-mcp
- ✅ sequential-thinking
- ✅ memory-mcp

**Failing (3/6):**
- ❌ exai-mcp (WS Shim not running)
- ❌ filesystem-mcp (npx package issue)
- ❌ mermaid-mcp (npx package issue)

See [MCP_QA_REPORT.md](../../MCP_QA_REPORT.md) for detailed analysis.

## Getting Help

1. **Try automated fix first**: `python scripts/fix_mcp_servers.py`
2. **Read troubleshooting guide**: [MCP_TROUBLESHOOTING_GUIDE.md](MCP_TROUBLESHOOTING_GUIDE.md)
3. **Check QA report**: [MCP_QA_REPORT.md](../../MCP_QA_REPORT.md)
4. **Review logs**: `logs/ws_daemon.log`, `logs/ws-shim.log`

---

**Last Updated**: 2025-11-13
