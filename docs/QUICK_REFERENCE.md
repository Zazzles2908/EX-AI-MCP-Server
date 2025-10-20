# EX-AI-MCP-Server Quick Reference

**Version:** 2.2  
**Last Updated:** 2025-10-13

---

## 🚀 Quick Start

### Start the Server

```powershell
# Windows PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1

# Or restart if already running
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### Check Health

```powershell
# Quick health check
Get-Content logs/ws_daemon.health.json | ConvertFrom-Json | Select-Object tool_count,uptime_human,sessions

# Full health snapshot
cat logs/ws_daemon.health.json | jq
```

### View Logs

```powershell
# Daemon logs
Get-Content logs/ws_daemon.log -Tail 50

# MCP server logs
Get-Content .logs/mcp_server.log -Tail 50
```

---

## 🔧 Common Commands

### Server Management

| Command | Purpose |
|---------|---------|
| `.\scripts\ws_start.ps1` | Start daemon |
| `.\scripts\ws_start.ps1 -Restart` | Restart daemon |
| `Get-Process | Where-Object {$_.Name -like "*python*"}` | Check if running |
| `Stop-Process -Name python -Force` | Stop all Python processes |

### Testing

| Command | Purpose |
|---------|---------|
| `python scripts/testing/test_integration_suite.py` | Run integration tests |
| `python scripts/testing/benchmark_performance.py` | Run performance benchmarks |
| `python scripts/testing/test_workflow_minimal.py` | Test single WorkflowTool |

### Environment

| Command | Purpose |
|---------|---------|
| `Get-Content .env` | View environment variables |
| `$env:EXAI_WS_URL` | Check WebSocket URL |
| `$env:EXAI_WS_TOKEN` | Check auth token |

---

## 📚 Key File Locations

### Configuration

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys, URLs, tokens) |
| `.env.example` | Example environment file |
| `requirements.txt` | Python dependencies |

### Code

| Directory | Contents |
|-----------|----------|
| `src/` | Main source code |
| `src/daemon/` | WebSocket daemon |
| `src/providers/` | Provider implementations (GLM, Kimi) |
| `tools/` | Tool implementations |
| `scripts/` | Utility scripts |

### Logs

| File | Contents |
|------|----------|
| `logs/ws_daemon.log` | Daemon logs |
| `logs/ws_daemon.health.json` | Health snapshot |
| `.logs/mcp_server.log` | MCP server logs |

### Documentation

| Directory | Contents |
|-----------|----------|
| `docs/` | All documentation |
| `docs/system-reference/` | System documentation |
| `docs/guides/` | User guides |
| `docs/consolidated_checklist/` | Project roadmap |

---

## 🛠️ Tool Quick Reference

### Simple Tools (Direct AI Calls)

| Tool | Purpose | Model |
|------|---------|-------|
| `chat` | General conversation | Any |
| `thinkdeep` | Deep reasoning | Thinking models |
| `planner` | Task planning | GLM-4.5-flash |
| `consensus` | Multi-model consensus | Multiple |
| `challenge` | Challenge assumptions | GLM-4.5-flash |
| `listmodels` | List available models | N/A |

### Workflow Tools (Multi-Step Analysis)

| Tool | Purpose | Expert Analysis |
|------|---------|-----------------|
| `analyze` | Code analysis | Yes |
| `debug` | Debugging assistance | Optional |
| `codereview` | Code review | Yes |
| `precommit` | Pre-commit checks | Yes |
| `refactor` | Refactoring suggestions | Yes |
| `testgen` | Test generation | Yes |
| `tracer` | Execution tracing | Yes |
| `secaudit` | Security audit | Yes |
| `docgen` | Documentation generation | Yes |

---

## 🔍 Troubleshooting Checklist

### Server Won't Start

- [ ] Check if Python is installed: `python --version`
- [ ] Check if dependencies are installed: `pip list`
- [ ] Check if port 8079 is available: `netstat -an | findstr 8079`
- [ ] Check `.env` file exists and has required variables
- [ ] Check logs: `Get-Content logs/ws_daemon.log -Tail 50`

### Auth Token Errors

- [ ] Check `EXAI_WS_TOKEN` in `.env`
- [ ] Verify token matches in client and server
- [ ] Restart daemon after changing `.env`
- [ ] Check logs for "invalid auth token" messages

### Tools Not Working

- [ ] Check daemon is running: `Get-Content logs/ws_daemon.health.json`
- [ ] Check tool count is 29: `tool_count: 29`
- [ ] Run integration tests: `python scripts/testing/test_integration_suite.py`
- [ ] Check provider API keys in `.env`

### Performance Issues

- [ ] Check memory usage: `Get-Process python | Select-Object WorkingSet`
- [ ] Check logs for errors or warnings
- [ ] Run performance benchmarks: `python scripts/testing/benchmark_performance.py`
- [ ] Verify provider API is responding

---

## 📖 Documentation Quick Links

### Getting Started
- [System Overview](system-reference/01-system-overview.md)
- [Deployment Guide](system-reference/06-deployment-guide.md)
- [Tool Ecosystem](system-reference/03-tool-ecosystem.md)

### Using Tools
- [Tool Selection Guide](guides/tool-selection-guide.md)
- [Parameter Reference](guides/parameter-reference.md)
- [Query Examples](guides/query-examples.md)

### Development
- [Provider Architecture](system-reference/02-provider-architecture.md)
- [API Reference](system-reference/05-api-endpoints-reference.md)
- [Architecture Docs](architecture/)

### Project Status
- [GOD Checklist](consolidated_checklist/GOD_CHECKLIST_CONSOLIDATED.md)
- [Phase B Summary](consolidated_checklist/PHASE_B_CLEANUP_SUMMARY.md)
- [Evidence Documents](consolidated_checklist/evidence/)

---

## 🔑 Environment Variables

### Required

| Variable | Purpose | Example |
|----------|---------|---------|
| `GLM_API_KEY` | ZhipuAI API key | `your-glm-api-key` |
| `KIMI_API_KEY` | Moonshot API key | `your-kimi-api-key` |
| `EXAI_WS_TOKEN` | WebSocket auth token | `your-secure-token` |

### Optional

| Variable | Purpose | Default |
|----------|---------|---------|
| `EXAI_WS_HOST` | WebSocket host | `127.0.0.1` |
| `EXAI_WS_PORT` | WebSocket port | `8079` |
| `EXAI_WS_URL` | Full WebSocket URL | `ws://127.0.0.1:8079` |
| `TEST_FILES_DIR` | Test files directory | Project root |

---

## 📊 System Status

### Current Phase: C (Optimize) - 33% Complete

**Phase A (Stabilize)** - ✅ COMPLETE
- Auth token error fixed
- Critical issues resolved
- System stable

**Phase B (Cleanup)** - ✅ COMPLETE
- WorkflowTools validated
- Integration tests passing
- Multi-provider support verified

**Phase C (Optimize)** - 🟡 IN PROGRESS
- ✅ Performance benchmarking
- 🟡 Documentation consolidation
- ⏳ Testing coverage

**Phase D (Refactor)** - ⏳ NOT STARTED
- Optional full modularization
- Awaiting Phase C completion

---

## 🆘 Getting Help

### Documentation
- **Master Index:** [docs/README.md](README.md)
- **Troubleshooting:** [docs/guides/troubleshooting.md](guides/troubleshooting.md)
- **Known Issues:** [docs/known_issues/](known_issues/)

### Support
- **GitHub Issues:** Report bugs or request features
- **Discussions:** Ask questions
- **Pull Requests:** Contribute improvements

---

## 📈 Performance Metrics

### Expected Performance

| Operation | Expected Time |
|-----------|---------------|
| SimpleTool (with AI) | 8-10s |
| SimpleTool (no AI) | < 0.1s |
| WorkflowTool | 2-10s |
| File embedding | < 1s per file |
| WebSocket connection | < 0.1s |

### Health Indicators

| Metric | Healthy Value |
|--------|---------------|
| Tool count | 29 |
| Sessions | 0-10 |
| Global capacity | 24 |
| Memory usage | < 500 MB |

---

## 🔄 Common Workflows

### Running Tests

```powershell
# 1. Start daemon
.\scripts\ws_start.ps1

# 2. Run integration tests
python scripts/testing/test_integration_suite.py

# 3. Check results
# All tests should pass (5/5)
```

### Making Code Changes

```powershell
# 1. Make your changes
# 2. Restart daemon to load changes
.\scripts\ws_start.ps1 -Restart

# 3. Test your changes
python scripts/testing/test_integration_suite.py

# 4. Check logs for errors
Get-Content logs/ws_daemon.log -Tail 50
```

### Debugging Issues

```powershell
# 1. Check daemon status
Get-Content logs/ws_daemon.health.json | ConvertFrom-Json

# 2. Check recent logs
Get-Content logs/ws_daemon.log -Tail 100

# 3. Run minimal test
python scripts/testing/test_workflow_minimal.py

# 4. Check for errors
# Look for ERROR or WARNING in logs
```

---

**Last Updated:** 2025-10-13  
**Version:** 2.2  
**For More Details:** See [docs/README.md](README.md)

