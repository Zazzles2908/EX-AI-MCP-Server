# EX-AI MCP Server - Production Deployment Guide
**Date:** 2025-10-21  
**Version:** 1.0  
**Status:** Production-Ready ✅

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Steps](#deployment-steps)
4. [Configuration](#configuration)
5. [Health Checks](#health-checks)
6. [Monitoring](#monitoring)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)

---

## 🔧 PREREQUISITES

### **System Requirements**
- **OS:** Linux (Ubuntu 20.04+, Debian 11+) or Windows with WSL2
- **Docker:** 24.0+ with Docker Compose v2
- **RAM:** Minimum 4GB, Recommended 8GB
- **CPU:** Minimum 2 cores, Recommended 4 cores
- **Disk:** Minimum 10GB free space

### **Required Services**
- **Supabase:** Active project with database + storage
- **Redis:** Included in docker-compose.yml (or external)
- **AI Providers:**
  - GLM API key (z.ai)
  - Kimi API key (moonshot.ai)

### **Network Requirements**
- **Ports:** 8079 (WebSocket), 8080 (Monitoring), 8082 (Health), 8000 (Metrics)
- **Outbound:** HTTPS access to api.z.ai, api.moonshot.cn, Supabase

---

## ✅ PRE-DEPLOYMENT CHECKLIST

### **1. Environment Configuration**
- [ ] Copy `.env.example` to `.env.docker`
- [ ] Set all required API keys (GLM, Kimi, Supabase)
- [ ] Configure Redis password
- [ ] Set timezone to your location (default: Australia/Melbourne)
- [ ] Review timeout configurations

### **2. Security**
- [ ] Generate strong Redis password (min 32 characters)
- [ ] Set Redis Commander credentials
- [ ] Verify Supabase RLS policies are enabled
- [ ] Review file upload size limits
- [ ] Check API rate limits

### **3. Resource Limits**
- [ ] Review docker-compose.yml resource limits
- [ ] Adjust CPU/memory based on expected load
- [ ] Configure file descriptor limits (ulimits)
- [ ] Set log rotation (max-size, max-file)

### **4. Code Verification**
- [ ] Run all EXAI fixes validation (6 fixes complete)
- [ ] Verify no hardcoded secrets in code
- [ ] Check all dependencies in requirements.txt
- [ ] Review .dockerignore excludes test files

### **5. Testing**
- [ ] Test WebSocket connection locally
- [ ] Verify all 13 workflow tools work
- [ ] Test provider failover (GLM ↔ Kimi)
- [ ] Verify Supabase connectivity
- [ ] Test Redis persistence

---

## 🚀 DEPLOYMENT STEPS

### **Step 1: Clone Repository**
```bash
git clone https://github.com/your-org/EX-AI-MCP-Server.git
cd EX-AI-MCP-Server
git checkout main  # or specific release tag
```

### **Step 2: Configure Environment**
```bash
# Copy environment template
cp .env.example .env.docker

# Edit configuration
nano .env.docker  # or vim, code, etc.
```

**Required Variables:**
```bash
# AI Providers
GLM_API_KEY=your_glm_key_here
KIMI_API_KEY=your_kimi_key_here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Redis
REDIS_PASSWORD=your_strong_redis_password_here
REDIS_COMMANDER_USER=admin
REDIS_COMMANDER_PASSWORD=your_commander_password

# Timezone
TZ=Australia/Melbourne  # Change to your timezone
```

### **Step 3: Build Docker Image**
```bash
# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker-compose build

# Verify image created
docker images | grep exai-mcp-server
```

### **Step 4: Start Services**
```bash
# Start in detached mode
docker-compose up -d

# Verify all containers running
docker-compose ps
```

**Expected Output:**
```
NAME                  STATUS              PORTS
exai-mcp-daemon       Up (healthy)        0.0.0.0:8079->8079/tcp, ...
exai-redis            Up (healthy)        0.0.0.0:6379->6379/tcp
exai-redis-commander  Up                  0.0.0.0:8081->8081/tcp
```

### **Step 5: Verify Health**
```bash
# Check health status
docker-compose ps

# View logs
docker-compose logs -f exai-daemon

# Test WebSocket connection
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $(openssl rand -base64 16)" \
  http://localhost:8079
```

### **Step 6: Verify Endpoints**
```bash
# Health check endpoint
curl http://localhost:8082/health

# Prometheus metrics
curl http://localhost:8000/metrics

# Monitoring dashboard
# Open browser: http://localhost:8080

# Redis Commander
# Open browser: http://localhost:8081
```

---

## ⚙️ CONFIGURATION

### **Timeout Configuration**
Located in `config.py` - `TimeoutConfig` class:

```python
# Tool timeouts (coordinated hierarchy)
SIMPLE_TOOL_TIMEOUT_SECS = 30      # Simple tools
WORKFLOW_TOOL_TIMEOUT_SECS = 45    # Workflow tools
EXPERT_ANALYSIS_TIMEOUT_SECS = 60  # Expert validation

# Daemon timeout (1.5x workflow)
DAEMON_TIMEOUT_SECS = 67.5

# Shim timeout (1.5x daemon)
SHIM_TIMEOUT_SECS = 101.25
```

**Override via .env.docker:**
```bash
SIMPLE_TOOL_TIMEOUT_SECS=30
WORKFLOW_TOOL_TIMEOUT_SECS=45
EXPERT_ANALYSIS_TIMEOUT_SECS=60
```

### **Resource Limits**
Located in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Maximum CPU cores
      memory: 2G       # Maximum RAM
    reservations:
      cpus: '0.5'      # Guaranteed CPU
      memory: 512M     # Guaranteed RAM
```

**Adjust for Production:**
- **Light load:** Keep defaults (2 CPU, 2GB RAM)
- **Medium load:** Increase to 4 CPU, 4GB RAM
- **Heavy load:** Increase to 8 CPU, 8GB RAM

### **Cache Configuration**
Expert validation cache (automatic):
- **TTL:** 1 hour (3600 seconds)
- **Max Size:** 100 entries
- **Eviction:** LRU (Least Recently Used)

---

## 🏥 HEALTH CHECKS

### **Container Health Checks**

**EXAI Daemon:**
```yaml
healthcheck:
  test: ["CMD", "python", "scripts/health_check.py"]
  interval: 30s
  timeout: 5s
  start_period: 60s
  retries: 3
```

**Redis:**
```yaml
healthcheck:
  test: ["CMD", "sh", "-c", "redis-cli -a $$REDIS_PASSWORD ping"]
  interval: 10s
  timeout: 3s
  start_period: 10s
  retries: 3
```

### **Manual Health Checks**
```bash
# Check all container health
docker-compose ps

# Check daemon health endpoint
curl http://localhost:8082/health

# Check WebSocket connectivity
python -c "import socket; s = socket.socket(); s.connect(('localhost', 8079)); print('OK')"

# Check Redis connectivity
docker exec exai-redis redis-cli -a YOUR_PASSWORD ping
```

---

## 📊 MONITORING

### **Log Locations**
```bash
# Container logs
docker-compose logs -f exai-daemon
docker-compose logs -f redis

# Application logs (mounted volume)
tail -f logs/mcp_server.log
tail -f logs/mcp_activity.log
```

### **Monitoring Dashboard**
Access at: `http://localhost:8080`

**Features:**
- Real-time WebSocket connections
- Active tool executions
- Provider health status
- Cache statistics
- Performance metrics

### **Prometheus Metrics**
Access at: `http://localhost:8000/metrics`

**Key Metrics:**
- `exai_requests_total` - Total requests
- `exai_request_duration_seconds` - Request latency
- `exai_provider_errors_total` - Provider failures
- `exai_cache_hits_total` - Cache hit rate

### **Redis Monitoring**
Access Redis Commander at: `http://localhost:8081`

**Credentials:** Set in `.env.docker`
- Username: `REDIS_COMMANDER_USER`
- Password: `REDIS_COMMANDER_PASSWORD`

---

## 🔄 ROLLBACK PROCEDURES

### **Scenario 1: Bad Deployment**

**Symptoms:**
- Health checks failing
- WebSocket connections rejected
- Provider errors

**Rollback Steps:**
```bash
# 1. Stop current deployment
docker-compose down

# 2. Checkout previous version
git checkout <previous-tag>

# 3. Rebuild and restart
docker-compose build
docker-compose up -d

# 4. Verify health
docker-compose ps
curl http://localhost:8082/health
```

### **Scenario 2: Configuration Error**

**Symptoms:**
- Services start but fail to connect
- Authentication errors
- Timeout errors

**Rollback Steps:**
```bash
# 1. Restore previous .env.docker
cp .env.docker.backup .env.docker

# 2. Restart services (no rebuild needed)
docker-compose restart

# 3. Verify health
docker-compose logs -f exai-daemon
```

### **Scenario 3: Database Migration Failure**

**Symptoms:**
- Supabase connection errors
- Schema mismatch errors

**Rollback Steps:**
```bash
# 1. Restore Supabase schema from backup
# (Use Supabase dashboard or pg_restore)

# 2. Rollback code to previous version
git checkout <previous-tag>

# 3. Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🔍 TROUBLESHOOTING

### **Issue: Container Won't Start**

**Check:**
```bash
# View container logs
docker-compose logs exai-daemon

# Check for port conflicts
netstat -tulpn | grep -E '8079|8080|8082|8000'

# Verify .env.docker exists
ls -la .env.docker
```

**Common Causes:**
- Missing `.env.docker` file
- Port already in use
- Invalid API keys
- Insufficient resources

### **Issue: WebSocket Connection Refused**

**Check:**
```bash
# Verify daemon is listening
docker exec exai-mcp-daemon netstat -tulpn | grep 8079

# Check firewall rules
sudo ufw status | grep 8079

# Test from inside container
docker exec exai-mcp-daemon python -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', 8079)); print('OK')"
```

**Common Causes:**
- Daemon not started
- Firewall blocking port
- Wrong host binding (0.0.0.0 vs 127.0.0.1)

### **Issue: Provider Timeouts**

**Check:**
```bash
# View provider logs
docker-compose logs exai-daemon | grep -i "provider\|timeout"

# Check circuit breaker status
docker-compose logs exai-daemon | grep "CIRCUIT_BREAKER"

# Verify API keys
docker exec exai-mcp-daemon env | grep -E "GLM_API_KEY|KIMI_API_KEY"
```

**Common Causes:**
- Invalid API keys
- Network connectivity issues
- Provider API downtime
- Timeout too short

### **Issue: High Memory Usage**

**Check:**
```bash
# Monitor container resources
docker stats exai-mcp-daemon

# Check cache size
docker-compose logs exai-daemon | grep "EXPERT_CACHE"

# Review Redis memory
docker exec exai-redis redis-cli -a YOUR_PASSWORD INFO memory
```

**Solutions:**
- Increase memory limits in docker-compose.yml
- Reduce cache TTL or max size
- Configure Redis maxmemory policy

---

## 🔒 SECURITY CONSIDERATIONS

### **1. API Keys**
- ✅ Never commit API keys to git
- ✅ Use strong, unique keys for each environment
- ✅ Rotate keys regularly (every 90 days)
- ✅ Store keys in `.env.docker` (not in code)

### **2. Redis Security**
- ✅ Enable authentication (requirepass)
- ✅ Use strong password (min 32 characters)
- ✅ Bind to localhost or private network only
- ✅ Enable TLS for production

### **3. Network Security**
- ✅ Use firewall to restrict port access
- ✅ Enable HTTPS for monitoring dashboard
- ✅ Use VPN for remote access
- ✅ Implement rate limiting

### **4. Container Security**
- ✅ Run containers as non-root user
- ✅ Use read-only file systems where possible
- ✅ Limit container capabilities
- ✅ Scan images for vulnerabilities

### **5. Supabase Security**
- ✅ Enable Row Level Security (RLS)
- ✅ Use service role key only in backend
- ✅ Implement proper access policies
- ✅ Enable audit logging

---

## 📝 DEPLOYMENT CHECKLIST

### **Pre-Deployment**
- [ ] All EXAI fixes verified (6 of 6 complete)
- [ ] Environment variables configured
- [ ] Security review complete
- [ ] Resource limits set appropriately
- [ ] Backup procedures tested

### **Deployment**
- [ ] Code deployed from tagged release
- [ ] Docker images built successfully
- [ ] All containers started
- [ ] Health checks passing
- [ ] Endpoints responding

### **Post-Deployment**
- [ ] Monitoring dashboard accessible
- [ ] Logs being collected
- [ ] Metrics being exported
- [ ] Alerts configured
- [ ] Rollback procedure documented

### **Validation**
- [ ] WebSocket connection successful
- [ ] All 13 workflow tools tested
- [ ] Provider failover tested
- [ ] Cache working correctly
- [ ] Performance acceptable

---

## 🎯 PRODUCTION READINESS SUMMARY

**✅ READY FOR PRODUCTION:**
- All 6 EXAI unpredictability fixes complete
- Docker optimized (multi-stage build, .dockerignore)
- Health checks configured
- Monitoring and metrics enabled
- Security hardened (Redis auth, RLS, API keys)
- Rollback procedures documented
- Troubleshooting guide complete

**Next Steps:**
1. Deploy to staging environment
2. Run load testing
3. Collect baseline metrics (1-2 days)
4. Fine-tune resource limits
5. Deploy to production

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-21  
**Maintained By:** EX-AI MCP Server Team

