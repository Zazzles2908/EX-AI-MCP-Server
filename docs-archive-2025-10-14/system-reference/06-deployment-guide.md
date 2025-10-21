# Deployment Guide

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Related:** `01-system-overview.md`, `05-api-endpoints-reference.md`

---

## Prerequisites

### System Requirements

**Operating System:**
- Windows 10/11 (PowerShell 5.1+)
- Linux (Ubuntu 20.04+, Debian 11+)
- macOS 11+

**Python:**
- Python 3.8 or higher
- pip package manager
- virtualenv (recommended)

**Network:**
- Internet connection for API access
- Firewall allowing outbound HTTPS (port 443)
- WebSocket support (port 8765 for local server)

### API Access

**Required:**
- Z.ai API key from https://z.ai/manage-apikey/apikey-list
- Active Z.ai account with billing enabled

**Optional:**
- Moonshot (Kimi) API key for Kimi provider
- GitHub account for repository access

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/EX-AI-MCP-Server.git
cd EX-AI-MCP-Server
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies Installed:**
```
zai-sdk>=0.0.4          # International SDK for api.z.ai
zhipuai>=2.1.0          # Mainland China SDK (dual approach)
websockets>=12.0        # WebSocket server
httpx>=0.27.0           # HTTP client with streaming
pydantic>=2.0           # Data validation
python-dotenv>=1.0.0    # Environment configuration
openai>=1.55.2          # OpenAI-compatible SDK
```

### Step 4: Verify Installation

```bash
python -c "import zai; print(zai.__version__)"
```

Expected output: `0.0.4` or higher

---

## Configuration

### Step 1: Create Environment File

```bash
cp .env.example .env
```

### Step 2: Edit .env File

**Minimum Configuration (GLM Only):**
```env
# GLM Provider (Required)
GLM_API_KEY=your_api_key_here
GLM_BASE_URL=https://api.z.ai/v1

# Server Configuration
MCP_SERVER_PORT=8765
MCP_SERVER_HOST=127.0.0.1

# Streaming (Optional)
GLM_STREAM_ENABLED=true
```

**Full Configuration (GLM + Kimi):**
```env
# GLM Provider (Required)
GLM_API_KEY=your_glm_api_key
GLM_BASE_URL=https://api.z.ai/v1
GLM_DEFAULT_MODEL=glm-4.6
GLM_TEMPERATURE=0.6
GLM_MAX_TOKENS=65536
GLM_STREAM_ENABLED=true

# Kimi Provider (Optional)
KIMI_API_KEY=your_kimi_api_key
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
KIMI_TEMPERATURE=0.5
KIMI_STREAM_ENABLED=true

# Server Configuration
MCP_SERVER_PORT=8765
MCP_SERVER_HOST=127.0.0.1
LOG_LEVEL=INFO

# Manager Configuration
DEFAULT_MANAGER_MODEL=glm-4.5-flash  # Fast manager for routing
ENABLE_AGENTIC_ROUTING=true

# Web Search (Optional)
GLM_ENABLE_WEB_BROWSING=true
DEFAULT_SEARCH_ENGINE=search_pro_jina
```

### Step 3: Validate Configuration

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('GLM_API_KEY:', 'SET' if os.getenv('GLM_API_KEY') else 'NOT SET')"
```

Expected output: `GLM_API_KEY: SET`

---

## Starting the Server

### Windows

**Using PowerShell Script:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1
```

**Manual Start:**
```powershell
python server.py
```

### Linux/macOS

**Using Shell Script:**
```bash
chmod +x scripts/ws_start.sh
./scripts/ws_start.sh
```

**Manual Start:**
```bash
python3 server.py
```

### Server Output

```
[2025-10-02 10:00:00] INFO: Starting EX-AI-MCP-Server
[2025-10-02 10:00:00] INFO: Loading configuration from .env
[2025-10-02 10:00:00] INFO: GLM provider initialized (base_url=https://api.z.ai/v1)
[2025-10-02 10:00:00] INFO: Kimi provider initialized (base_url=https://api.moonshot.ai/v1)
[2025-10-02 10:00:00] INFO: WebSocket server starting on ws://127.0.0.1:8765
[2025-10-02 10:00:01] INFO: Server ready - accepting connections
```

---

## Verification

### Step 1: Check Server Status

**Check Logs:**
```bash
tail -f .logs/mcp_server.log
```

**Expected Output:**
```
[INFO] Server started successfully
[INFO] Listening on ws://127.0.0.1:8765
[INFO] GLM provider: READY
[INFO] Kimi provider: READY
```

### Step 2: Test WebSocket Connection

**Using wscat (Node.js):**
```bash
npm install -g wscat
wscat -c ws://127.0.0.1:8765
```

**Expected Response:**
```json
{
  "type": "connection_established",
  "server": "EX-AI-MCP-Server",
  "version": "1.0"
}
```

### Step 3: Test Chat Endpoint

**Send Test Message:**
```json
{
  "tool": "chat",
  "params": {
    "prompt": "Hello, are you working?",
    "model": "glm-4.6"
  }
}
```

**Expected Response:**
```json
{
  "type": "response",
  "content": "Yes, I'm working! How can I help you today?",
  "model": "glm-4.6",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

---

## Restarting the Server

### After Code Changes

**Windows:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

**Linux/macOS:**
```bash
./scripts/ws_start.sh --restart
```

### Manual Restart

1. Stop server: `Ctrl+C`
2. Start server: `python server.py`

---

## Troubleshooting

### Issue: "Module not found" Error

**Cause:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Invalid API key" Error

**Cause:** API key not set or incorrect

**Solution:**
1. Check `.env` file: `GLM_API_KEY=your_key_here`
2. Verify key at https://z.ai/manage-apikey/apikey-list
3. Restart server after updating `.env`

### Issue: "Connection refused" Error

**Cause:** Server not running or wrong port

**Solution:**
1. Check server is running: `ps aux | grep server.py`
2. Check port in `.env`: `MCP_SERVER_PORT=8765`
3. Check firewall settings

### Issue: "Rate limit exceeded" Error

**Cause:** Too many requests

**Solution:**
1. Wait for rate limit reset (check headers)
2. Implement request throttling
3. Upgrade API plan if needed

### Issue: Streaming Not Working

**Cause:** Streaming not enabled

**Solution:**
1. Check `.env`: `GLM_STREAM_ENABLED=true`
2. Restart server
3. Verify client supports SSE

### Issue: Web Search Not Working

**Cause:** Web search not enabled or configured

**Solution:**
1. Check `.env`: `GLM_ENABLE_WEB_BROWSING=true`
2. Verify model supports web search (GLM-4.6)
3. Check search engine configuration

---

## Production Deployment

### Using systemd (Linux)

**Create Service File:**
```bash
sudo nano /etc/systemd/system/exai-mcp.service
```

**Service Configuration:**
```ini
[Unit]
Description=EX-AI-MCP-Server
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/EX-AI-MCP-Server
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable exai-mcp
sudo systemctl start exai-mcp
```

**Check Status:**
```bash
sudo systemctl status exai-mcp
```

### Using Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["python", "server.py"]
```

**Build and Run:**
```bash
docker build -t exai-mcp-server .
docker run -d -p 8765:8765 --env-file .env exai-mcp-server
```

### Using Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  exai-mcp:
    build: .
    ports:
      - "8765:8765"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/.logs
```

**Start:**
```bash
docker-compose up -d
```

---

## Monitoring

### Log Files

**Location:**
```
.logs/mcp_server.log
```

**Rotation:**
- Automatic rotation at 10MB
- Keep last 5 log files
- Compressed older logs

**View Logs:**
```bash
tail -f .logs/mcp_server.log
```

### Health Check Endpoint

**Endpoint:**
```
GET http://127.0.0.1:8765/health
```

**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600,
  "providers": {
    "glm": "ready",
    "kimi": "ready"
  }
}
```

### Metrics

**Available Metrics:**
- Request count
- Response time
- Error rate
- Token usage
- Provider availability

**Access Metrics:**
```
GET http://127.0.0.1:8765/metrics
```

---

## Security Best Practices

### API Key Management

**DO:**
- Store API keys in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables
- Rotate keys regularly

**DON'T:**
- Commit API keys to Git
- Share API keys publicly
- Hardcode API keys in code
- Use same key across environments

### Network Security

**Recommendations:**
- Run server on localhost only (127.0.0.1)
- Use reverse proxy for external access
- Enable HTTPS for production
- Implement rate limiting
- Use firewall rules

### Access Control

**Recommendations:**
- Implement authentication
- Use API key rotation
- Monitor access logs
- Set up alerts for suspicious activity

---

## Backup and Recovery

### Configuration Backup

**Backup `.env` file:**
```bash
cp .env .env.backup
```

**Backup logs:**
```bash
tar -czf logs-backup-$(date +%Y%m%d).tar.gz .logs/
```

### Disaster Recovery

**Steps:**
1. Restore `.env` from backup
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Restart server
4. Verify functionality

---

## Upgrading

### Minor Version Upgrade

```bash
git pull origin main
pip install -r requirements.txt --upgrade
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### Major Version Upgrade

1. Read upgrade guide in `docs/upgrades/`
2. Backup configuration and data
3. Follow migration steps
4. Test in staging environment
5. Deploy to production

---

## Support

### Documentation

- **System Reference:** `docs/system-reference/`
- **User Guides:** `docs/guides/`
- **Architecture:** `docs/architecture/`
- **Upgrades:** `docs/upgrades/`

### Community

- **GitHub Issues:** Report bugs and request features
- **Discussions:** Ask questions and share experiences

### Official Resources

- **Z.ai API Docs:** https://docs.z.ai/
- **GLM-4.6 Guide:** https://docs.z.ai/guides/llm/glm-4.6
- **zai-sdk GitHub:** https://github.com/zai-org/z-ai-sdk-python

---

**Next:** Read `07-upgrade-roadmap.md` for current upgrade project status

