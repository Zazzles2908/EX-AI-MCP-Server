# EX-AI MCP Server - Quick Reference

## 🚀 Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 📊 Current Status

**Containers**: ✅ 4/4 Operational  
**Tools**: ✅ 20 Available  
**Configuration**: ✅ Complete  
**Documentation**: ✅ 4 Guides  

---

## 🛠️ Essential Commands

### Container Management
```bash
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose restart            # Restart all
docker-compose ps                 # Status check
```

### Logs & Debugging
```bash
docker logs exai-mcp-stdio        # STDIO server logs
docker logs exai-mcp-server       # WebSocket logs
docker logs exai-redis            # Database logs
```

### Health Checks
```bash
curl http://localhost:3002/health                    # WebSocket health
docker exec exai-redis redis-cli PING               # Redis health
docker-compose ps                                    # All containers
```

### Validation
```bash
bash validate_deployment.sh       # Full validation
python diagnose_system_prompt.py  # System prompt check
```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Container orchestration |
| `config.yaml` | Mini-Agent project config |
| `.mcp.json` | MCP server connection |
| `system_prompt.md` | Primary system prompt |
| `validate_deployment.sh` | Deployment validation |

---

## 🔧 Tool Categories

**Core Analysis**: analyze, codereview, debug, tracer  
**Communication**: chat, consensus, planner, thinkdeep  
**Documentation**: docgen, testgen, secaudit, precommit, refactor  
**File Ops**: smart_file_download, smart_file_query  
**Utility**: listmodels, status, version, glm_payload_preview, kimi_chat_with_tools  

---

## 🌐 Ports

| Port | Service |
|------|---------|
| 3010 | WebSocket MCP |
| 3002 | Health endpoint |
| 6379 | Redis |
| 8081 | Redis Commander |

---

## 📚 Documentation

1. **EXAI_MCP_STREAMLINING_COMPLETE.md** - Complete implementation guide
2. **DEPLOYMENT_VERIFICATION.md** - Deployment verification report
3. **SYSTEM_PROMPT_FIX_GUIDE.md** - System prompt troubleshooting
4. **CRITICAL_ISSUES_RESOLVED.md** - Issue resolution log

---

## 🔍 Troubleshooting

**Container won't start?**  
→ `docker logs CONTAINER_NAME --tail=50`

**System prompt not found?**  
→ `python diagnose_system_prompt.py`

**Tools not loading?**  
→ `docker-compose build --no-cache && docker-compose up -d`

**Redis connection error?**  
→ `docker exec exai-redis redis-cli PING`

---

## 📞 Quick Links

**Project**: `C:\Project\EX-AI-MCP-Server`  
**Config**: `C:\Users\Jazeel-Home\.mini-agent\config`  
**Outputs**: `C:\Project\EX-AI-MCP-Server\outputs`  

---

**Status**: ✅ FULLY OPERATIONAL  
**Last Updated**: 2025-11-16
